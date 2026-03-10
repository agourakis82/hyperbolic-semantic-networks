"""
DISCRETE RICCI FLOW ON SEMANTIC NETWORKS

Applies normalized discrete Ollivier-Ricci flow (Ni et al. 2019) to all 11
semantic networks. Tests whether the three geometric regimes (hyperbolic,
Euclidean, spherical) exhibit qualitatively different flow dynamics.

Key predictions:
  - Hyperbolic networks (SWOW ES/EN/ZH, ConceptNet, Depression):
    κ̄(t) rises from negative toward 0, clustering collapses
  - Euclidean networks (WordNet, BabelNet):
    κ̄(t) stays near 0, minimal structural change
  - Spherical network (SWOW Dutch):
    κ̄(t) falls from positive toward 0, moderate restructuring

Usage:
    julia --project=julia -t8 julia/scripts/ricci_flow_semantic.jl
    julia --project=julia -t8 julia/scripts/ricci_flow_semantic.jl --quick   # Small networks only
    julia --project=julia -t8 julia/scripts/ricci_flow_semantic.jl --network swow_es
"""

import Pkg
let deps = Pkg.project().dependencies
    for pkg in ["Graphs", "JSON", "CSV", "DataFrames"]
        if !haskey(deps, pkg)
            Pkg.add(pkg)
        end
    end
end

using Graphs
using Statistics
using Random
using JSON
using Printf
using CSV
using DataFrames
using LinearAlgebra

# ─────────────────────────────────────────────────────────────────
# Network registry (same as unified_semantic_orc.jl)
# ─────────────────────────────────────────────────────────────────

const DATA_DIR = joinpath(@__DIR__, "..", "..", "data", "processed")
const RESULTS_DIR = joinpath(@__DIR__, "..", "..", "results", "experiments")

struct NetworkSpec
    id::String
    filename::String
    category::String
    language::String
    has_relation::Bool
end

const NETWORKS = [
    NetworkSpec("swow_es", "spanish_edges_FINAL.csv", "association", "Spanish", false),
    NetworkSpec("swow_en", "english_edges_FINAL.csv", "association", "English", false),
    NetworkSpec("swow_zh", "chinese_edges_FINAL.csv", "association", "Chinese", false),
    NetworkSpec("swow_nl", "dutch_edges.csv", "association", "Dutch", false),
    NetworkSpec("conceptnet_en", "conceptnet_en_edges.csv", "knowledge", "English", true),
    NetworkSpec("conceptnet_pt", "conceptnet_pt_edges.csv", "knowledge", "Portuguese", true),
    NetworkSpec("wordnet_en", "wordnet_edges.csv", "taxonomy", "English", true),
    NetworkSpec("babelnet_ru", "babelnet_ru_edges.csv", "taxonomy", "Russian", true),
    NetworkSpec("babelnet_ar", "babelnet_ar_edges.csv", "taxonomy", "Arabic", true),
    NetworkSpec("depression_min", "depression_networks_optimal/depression_minimum_edges.csv", "clinical", "English", false),
]

# Skip wordnet_en_2k (too large for flow) and depression severity variants

# ─────────────────────────────────────────────────────────────────
# Network loader
# ─────────────────────────────────────────────────────────────────

function load_network(spec::NetworkSpec)
    filepath = joinpath(DATA_DIR, spec.filename)
    if !isfile(filepath)
        @warn "File not found: $filepath"
        return nothing, nothing
    end

    df = CSV.read(filepath, DataFrame; stringtype=String)

    all_nodes = sort(unique(vcat(df.source, df.target)))
    node_to_id = Dict(name => i for (i, name) in enumerate(all_nodes))
    N = length(all_nodes)

    g = SimpleGraph(N)
    for row in eachrow(df)
        u = node_to_id[row.source]
        v = node_to_id[row.target]
        if u != v
            add_edge!(g, u, v)
        end
    end

    # Largest connected component
    ccs = connected_components(g)
    if length(ccs) > 1
        largest_cc = ccs[argmax(length.(ccs))]
        g, _ = induced_subgraph(g, sort(largest_cc))
    end

    return g, spec.id
end

# ─────────────────────────────────────────────────────────────────
# Sinkhorn W1 (for flow iterations — fast approximate)
# ─────────────────────────────────────────────────────────────────

function sinkhorn_w1(mu::Vector{Float64}, nu::Vector{Float64},
                     C::Matrix{Float64}; epsilon::Float64=0.1,
                     max_iter::Int=200)::Float64
    n = length(mu)
    K = exp.(-C ./ epsilon)

    u = ones(n)
    v = ones(n)

    for _ in 1:max_iter
        u_new = mu ./ (K * v .+ 1e-30)
        v_new = nu ./ (K' * u_new .+ 1e-30)

        if maximum(abs.(u_new .- u)) < 1e-8 && maximum(abs.(v_new .- v)) < 1e-8
            u = u_new
            v = v_new
            break
        end
        u = u_new
        v = v_new
    end

    gamma = Diagonal(u) * K * Diagonal(v)
    return sum(C .* gamma)
end

# ─────────────────────────────────────────────────────────────────
# Weighted shortest paths (Dijkstra)
# ─────────────────────────────────────────────────────────────────

function weighted_shortest_paths(g::SimpleGraph,
                                  weights::Dict{Tuple{Int,Int}, Float64})::Matrix{Float64}
    N = nv(g)
    dists = fill(Inf, N, N)

    Threads.@threads for src_node in 1:N
        dists[src_node, src_node] = 0.0
        visited = falses(N)
        pq = [(0.0, src_node)]

        while !isempty(pq)
            sort!(pq, by=first)
            d_curr, u = popfirst!(pq)

            if visited[u]
                continue
            end
            visited[u] = true
            dists[src_node, u] = d_curr

            for v in neighbors(g, u)
                key = minmax(u, v)
                w = get(weights, key, 1.0)
                d_new = d_curr + w
                if d_new < dists[src_node, v]
                    dists[src_node, v] = d_new
                    push!(pq, (d_new, v))
                end
            end
        end
    end

    return dists
end

# ─────────────────────────────────────────────────────────────────
# Edge ORC with weighted distances (Sinkhorn)
# ─────────────────────────────────────────────────────────────────

function compute_weighted_orc(g::SimpleGraph, u::Int, v::Int,
                               all_dists::Matrix{Float64};
                               alpha::Float64=0.5)::Float64
    mu_u = Dict{Int, Float64}()
    mu_v = Dict{Int, Float64}()

    mu_u[u] = alpha
    mu_v[v] = alpha

    nbrs_u = neighbors(g, u)
    nbrs_v = neighbors(g, v)

    if !isempty(nbrs_u)
        w = (1.0 - alpha) / length(nbrs_u)
        for z in nbrs_u
            mu_u[z] = get(mu_u, z, 0.0) + w
        end
    end

    if !isempty(nbrs_v)
        w = (1.0 - alpha) / length(nbrs_v)
        for z in nbrs_v
            mu_v[z] = get(mu_v, z, 0.0) + w
        end
    end

    support = sort(unique(vcat(collect(keys(mu_u)), collect(keys(mu_v)))))
    n = length(support)
    node_idx = Dict(s => i for (i, s) in enumerate(support))

    mu_vec = zeros(n)
    nu_vec = zeros(n)
    for (node, p) in mu_u
        mu_vec[node_idx[node]] = p
    end
    for (node, p) in mu_v
        nu_vec[node_idx[node]] = p
    end

    C = zeros(n, n)
    for i in 1:n
        for j in 1:n
            C[i, j] = all_dists[support[i], support[j]]
        end
    end

    W1 = sinkhorn_w1(mu_vec, nu_vec, C; epsilon=0.1, max_iter=200)

    d_uv = all_dists[u, v]
    if d_uv < 1e-10
        return 0.0
    end
    return 1.0 - W1 / d_uv
end

# ─────────────────────────────────────────────────────────────────
# Gini coefficient
# ─────────────────────────────────────────────────────────────────

function gini_coefficient(values::Vector{Float64})::Float64
    sorted = sort(values)
    n = length(sorted)
    if n == 0 || sum(sorted) == 0
        return 0.0
    end
    numerator = sum((2i - n - 1) * sorted[i] for i in 1:n)
    denominator = n * sum(sorted)
    return numerator / denominator
end

# ─────────────────────────────────────────────────────────────────
# Main Ricci Flow
# ─────────────────────────────────────────────────────────────────

function run_ricci_flow(g::SimpleGraph, network_id::String;
                        dt::Float64=0.5, alpha::Float64=0.5,
                        max_iterations::Int=50)
    N = nv(g)
    E = ne(g)
    mean_k = 2.0 * E / N
    eta = mean_k^2 / N

    println("\n", "="^60)
    @printf("RICCI FLOW: %s (N=%d, E=%d, <k>=%.1f, η=%.3f)\n", network_id, N, E, mean_k, eta)
    println("Parameters: dt=$dt, alpha=$alpha, max_iter=$max_iterations")
    println("="^60)

    edges_list = collect(edges(g))

    # Initialize weights to 1.0
    weights = Dict{Tuple{Int,Int}, Float64}()
    for e in edges_list
        weights[minmax(src(e), dst(e))] = 1.0
    end

    trajectory = Vector{Dict{String, Any}}()

    for t in 0:max_iterations
        iter_start = time()

        # Compute weighted APSP
        all_dists = weighted_shortest_paths(g, weights)

        # Compute ORC for all edges
        kappa_values = Vector{Float64}(undef, length(edges_list))
        kappa_dict = Dict{Tuple{Int,Int}, Float64}()

        Threads.@threads for i in 1:length(edges_list)
            e = edges_list[i]
            kappa_values[i] = compute_weighted_orc(g, src(e), dst(e), all_dists; alpha=alpha)
        end

        for (i, e) in enumerate(edges_list)
            kappa_dict[minmax(src(e), dst(e))] = kappa_values[i]
        end

        # Observables
        kappa_mean = mean(kappa_values)
        kappa_std = std(kappa_values)
        kappa_range = maximum(kappa_values) - minimum(kappa_values)
        C = Graphs.global_clustering_coefficient(g)
        w_vals = collect(values(weights))
        w_gini = gini_coefficient(w_vals)
        w_spread = maximum(w_vals) / max(minimum(w_vals), 1e-30)

        elapsed = time() - iter_start

        record = Dict{String, Any}(
            "t" => t,
            "kappa_mean" => round(kappa_mean; digits=6),
            "kappa_std" => round(kappa_std; digits=6),
            "kappa_range" => round(kappa_range; digits=6),
            "kappa_min" => round(minimum(kappa_values); digits=6),
            "kappa_max" => round(maximum(kappa_values); digits=6),
            "clustering" => round(C; digits=6),
            "w_gini" => round(w_gini; digits=6),
            "w_spread" => round(w_spread; digits=2),
            "w_mean" => round(mean(w_vals); digits=6),
            "w_std" => round(std(w_vals); digits=6),
            "elapsed_s" => round(elapsed; digits=1),
        )
        push!(trajectory, record)

        @printf("  t=%3d: κ̄=%+.5f  σ_κ=%.4f  range=%.4f  C=%.4f  Gini=%.4f  spread=%.1f  (%.1fs)\n",
                t, kappa_mean, kappa_std, kappa_range, C, w_gini, w_spread, elapsed)

        # Check convergence
        if t > 0 && kappa_range < 1e-4
            println("  CONVERGED at t=$t")
            break
        end

        # Don't update on last iteration
        if t == max_iterations
            break
        end

        # Update weights
        for (key, kappa) in kappa_dict
            weights[key] *= (1.0 - dt * kappa)
            weights[key] = max(weights[key], 1e-10)
        end

        # Normalize: total weight = E
        total = sum(values(weights))
        scale = Float64(E) / total
        for key in keys(weights)
            weights[key] *= scale
        end
    end

    # Encode final edge weights as list of [u, v, w] triples
    final_weights_list = [[u, v, w] for ((u,v), w) in weights]

    return Dict(
        "network_id" => network_id,
        "N" => N,
        "E" => E,
        "mean_k" => mean_k,
        "eta" => eta,
        "clustering_initial" => trajectory[1]["clustering"],
        "kappa_initial" => trajectory[1]["kappa_mean"],
        "kappa_final" => trajectory[end]["kappa_mean"],
        "clustering_final" => trajectory[end]["clustering"],
        "iterations" => length(trajectory) - 1,
        "converged" => length(trajectory) > 1 && trajectory[end]["kappa_range"] < 1e-4,
        "dt" => dt,
        "alpha" => alpha,
        "trajectory" => trajectory,
        "final_weights" => final_weights_list,
    )
end

# ─────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────

function main()
    # Parse args
    quick_mode = "--quick" in ARGS
    single_network = nothing
    for (i, arg) in enumerate(ARGS)
        if arg == "--network" && i < length(ARGS)
            single_network = ARGS[i+1]
        end
    end

    # Select networks
    if single_network !== nothing
        specs = filter(s -> s.id == single_network, NETWORKS)
        if isempty(specs)
            error("Unknown network: $single_network. Available: $(join([s.id for s in NETWORKS], ", "))")
        end
    elseif quick_mode
        # Small networks only (N < 500, exclude Dutch SWOW which has 15k edges)
        specs = filter(s -> s.id in ["babelnet_ar", "swow_es", "wordnet_en", "babelnet_ru"], NETWORKS)
    else
        specs = NETWORKS
    end

    println("="^60)
    println("DISCRETE RICCI FLOW ON SEMANTIC NETWORKS")
    println("Networks: $(length(specs))")
    println("Threads: $(Threads.nthreads())")
    println("="^60)

    all_results = Dict{String, Any}[]

    for spec in specs
        g, id = load_network(spec)
        if g === nothing
            @warn "Skipping $(spec.id) — file not found"
            continue
        end

        N = nv(g)
        E = ne(g)

        # Adaptive iteration count based on network size
        max_iter = N > 1000 ? 30 : 50

        # Skip very large networks in quick mode
        if quick_mode && E > 5000
            @warn "Skipping $(spec.id) (E=$E > 5000) in quick mode"
            continue
        end

        result = run_ricci_flow(g, id; max_iterations=max_iter)
        push!(all_results, result)

        # Save per-network result immediately
        mkpath(RESULTS_DIR)
        per_file = joinpath(RESULTS_DIR, "ricci_flow_$(id).json")
        open(per_file, "w") do f
            JSON.print(f, result, 2)
        end
        println("  SAVED: $per_file")
    end

    # Save combined results
    mkpath(RESULTS_DIR)
    output_file = joinpath(RESULTS_DIR, "ricci_flow_semantic.json")
    output_data = Dict(
        "experiment" => "ricci_flow_semantic",
        "description" => "Normalized discrete ORC flow on semantic networks (Ni et al. 2019)",
        "method" => "Sinkhorn ORC (epsilon=0.1), normalized flow",
        "dt" => 0.5,
        "alpha" => 0.5,
        "n_networks" => length(all_results),
        "results" => all_results,
    )
    open(output_file, "w") do f
        JSON.print(f, output_data, 2)
    end
    println("\nSAVED: $output_file")

    # Summary table
    println("\n", "="^60)
    println("RICCI FLOW SUMMARY")
    println("="^60)
    @printf("%-18s  %5s  %5s  %7s  %8s → %8s  %6s → %6s  %s\n",
            "Network", "N", "E", "η", "κ₀", "κ_final", "C₀", "C_final", "Conv?")
    println("-"^100)
    for r in all_results
        @printf("%-18s  %5d  %5d  %7.3f  %+8.5f → %+8.5f  %6.4f → %6.4f  %s\n",
                r["network_id"], r["N"], r["E"], r["eta"],
                r["kappa_initial"], r["kappa_final"],
                r["clustering_initial"], r["clustering_final"],
                r["converged"] ? "YES" : "no")
    end
end

main()
