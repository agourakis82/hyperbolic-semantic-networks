"""
HYPERCOMPLEX ORC on SEMANTIC NETWORKS

Applies sphere-embedded (S^(d-1)) Ollivier-Ricci curvature to real semantic
networks, comparing hop-count vs. geodesic transport cost.

Key question: Is semantic network hyperbolicity intrinsic to the topology,
or an artifact of the hop-count metric? If networks flip to κ > 0 under
sphere embedding (as random graphs do), hyperbolicity is metric-dependent.

Usage:
    julia hypercomplex_semantic_orc.jl                          # All networks, d=4
    julia hypercomplex_semantic_orc.jl --network swow_en --d 8  # Single network
    julia hypercomplex_semantic_orc.jl --all-dims               # All networks, d∈{4,8,16}
"""

import Pkg
let deps = Pkg.project().dependencies
    for pkg in ["JuMP", "HiGHS", "Graphs", "JSON", "CSV", "DataFrames"]
        if !haskey(deps, pkg)
            Pkg.add(pkg)
        end
    end
end

using JuMP, HiGHS, Graphs, Statistics, Random, JSON, Printf, LinearAlgebra, CSV, DataFrames

# ─────────────────────────────────────────────────────────────────
# Import network loader from unified script
# ─────────────────────────────────────────────────────────────────

# We need the network loading infrastructure. Inline the key parts
# to avoid include() issues.

const DATA_DIR = joinpath(@__DIR__, "..", "..", "data", "processed")
const RESULTS_DIR = joinpath(@__DIR__, "..", "..", "results", "unified")

struct NetworkSpec
    id::String
    filename::String
    category::String
    language::String
    has_relation::Bool
end

# Only include networks with N < 2000 (BFS all-pairs memory constraint)
const NETWORKS = [
    NetworkSpec("swow_es", "spanish_edges_FINAL.csv", "association", "Spanish", false),
    NetworkSpec("swow_en", "english_edges_FINAL.csv", "association", "English", false),
    NetworkSpec("swow_zh", "chinese_edges_FINAL.csv", "association", "Chinese", false),
    NetworkSpec("swow_nl", "dutch_edges.csv", "association", "Dutch", false),
    NetworkSpec("conceptnet_en", "conceptnet_en_edges.csv", "knowledge", "English", true),
    NetworkSpec("conceptnet_pt", "conceptnet_pt_edges.csv", "knowledge", "Portuguese", true),
    NetworkSpec("wordnet_en", "wordnet_edges.csv", "taxonomy", "English", true),
    NetworkSpec("wordnet_en_2k", "wordnet_N2000_edges.csv", "taxonomy", "English", true),
    NetworkSpec("babelnet_ru", "babelnet_ru_edges.csv", "taxonomy", "Russian", true),
    NetworkSpec("babelnet_ar", "babelnet_ar_edges.csv", "taxonomy", "Arabic", true),
    NetworkSpec("depression_minimum", "depression_networks_optimal/depression_minimum_edges.csv", "clinical", "English", false),
]

function load_network(spec::NetworkSpec)
    filepath = joinpath(DATA_DIR, spec.filename)
    isfile(filepath) || error("File not found: $filepath")
    df = CSV.read(filepath, DataFrame; stringtype=String)
    all_nodes = sort(unique(vcat(df.source, df.target)))
    node_to_id = Dict(name => i for (i, name) in enumerate(all_nodes))
    N = length(all_nodes)
    g = SimpleGraph(N)
    for row in eachrow(df)
        u, v = node_to_id[row.source], node_to_id[row.target]
        u != v && add_edge!(g, u, v)
    end
    ccs = connected_components(g)
    if length(ccs) > 1
        largest_cc = ccs[argmax(length.(ccs))]
        g, vmap = induced_subgraph(g, sort(largest_cc))
        id_to_name = Dict(i => name for (name, i) in node_to_id)
        names = [id_to_name[vmap[i]] for i in 1:nv(g)]
        return g, names
    end
    id_to_name = Dict(i => name for (name, i) in node_to_id)
    return g, [id_to_name[i] for i in 1:N]
end

# ─────────────────────────────────────────────────────────────────
# Core functions (from hypercomplex_lp.jl)
# ─────────────────────────────────────────────────────────────────

function exact_wasserstein1(mu::Vector{Float64}, nu::Vector{Float64},
                            C::Matrix{Float64})::Float64
    n = length(mu)
    model = Model(HiGHS.Optimizer)
    set_silent(model)
    @variable(model, gamma[1:n, 1:n] >= 0)
    @constraint(model, [i=1:n], sum(gamma[i, :]) == mu[i])
    @constraint(model, [j=1:n], sum(gamma[:, j]) == nu[j])
    @objective(model, Min, sum(C[i, j] * gamma[i, j] for i in 1:n, j in 1:n))
    optimize!(model)
    termination_status(model) == OPTIMAL || return NaN
    return objective_value(model)
end

function bfs_all_pairs(g::SimpleGraph)::Matrix{Int}
    N = nv(g)
    D = zeros(Int, N, N)
    Threads.@threads for u in 1:N
        D[u, :] = gdistances(g, u)
    end
    return D
end

function select_landmarks(D_hop::Matrix{Int}, n_lm::Int;
                          rng::AbstractRNG=MersenneTwister(42))::Vector{Int}
    N = size(D_hop, 1)
    n_lm = min(n_lm, N)
    landmarks = [rand(rng, 1:N)]
    min_dists = vec(D_hop[landmarks[1], :])
    for _ in 2:n_lm
        next = argmax(min_dists)
        push!(landmarks, next)
        min_dists = min.(min_dists, vec(D_hop[next, :]))
    end
    return landmarks
end

function landmark_embed(D_hop::Matrix{Int}, landmarks::Vector{Int})::Matrix{Float64}
    N = size(D_hop, 1)
    d = length(landmarks)
    X = Matrix{Float64}(undef, N, d)
    for i in 1:N
        v = Float64[D_hop[i, l] for l in landmarks]
        n = norm(v)
        X[i, :] = n < 1e-10 ? fill(1.0 / sqrt(d), d) : v / n
    end
    return X
end

function geodesic_cost(X::Matrix{Float64})::Matrix{Float64}
    N = size(X, 1)
    C = Matrix{Float64}(undef, N, N)
    for i in 1:N, j in 1:N
        C[i, j] = acos(clamp(dot(X[i, :], X[j, :]), -1.0, 1.0))
    end
    return C
end

function build_prob_measure(g::SimpleGraph, u::Int, alpha::Float64=0.5)::Dict{Int,Float64}
    mu = Dict{Int,Float64}(u => alpha)
    nbrs = neighbors(g, u)
    if !isempty(nbrs)
        w = (1.0 - alpha) / length(nbrs)
        for z in nbrs
            mu[z] = get(mu, z, 0.0) + w
        end
    end
    return mu
end

function hypercomplex_edge_curvature(g::SimpleGraph, u::Int, v::Int,
                                     C_geo::Matrix{Float64};
                                     alpha::Float64=0.5)::Float64
    d_uv = C_geo[u, v]
    d_uv < 1e-6 && return NaN

    mu_u = build_prob_measure(g, u, alpha)
    mu_v = build_prob_measure(g, v, alpha)

    all_nodes = sort(unique(vcat(collect(keys(mu_u)), collect(keys(mu_v)))))
    n = length(all_nodes)
    idx = Dict(node => i for (i, node) in enumerate(all_nodes))

    mu_vec = [get(mu_u, all_nodes[i], 0.0) for i in 1:n]
    nu_vec = [get(mu_v, all_nodes[i], 0.0) for i in 1:n]
    C_local = [C_geo[all_nodes[i], all_nodes[j]] for i in 1:n, j in 1:n]

    W1 = exact_wasserstein1(mu_vec, nu_vec, C_local)
    return 1.0 - W1 / d_uv
end

# ─────────────────────────────────────────────────────────────────
# Process one network at one embedding dimension
# ─────────────────────────────────────────────────────────────────

function process_hypercomplex(spec::NetworkSpec, d::Int; alpha::Float64=0.5, seed::Int=42)
    embedding_name = d == 4 ? "Q4 (S³)" : d == 8 ? "Oct (S⁷)" : d == 16 ? "Sed (S¹⁵)" : "S^$(d-1)"

    println("\n", "-"^60)
    @printf("HYPERCOMPLEX: %s  d=%d (%s)\n", spec.id, d, embedding_name)

    # Load network
    t0 = time()
    g, names = load_network(spec)
    N = nv(g)
    E = ne(g)
    mean_k = 2.0 * E / N
    @printf("  N=%d  E=%d  <k>=%.2f\n", N, E, mean_k)

    # BFS all-pairs
    println("  Computing BFS all-pairs...")
    D_hop = bfs_all_pairs(g)

    # Landmark embedding
    rng = MersenneTwister(seed)
    landmarks = select_landmarks(D_hop, d; rng=rng)
    X = landmark_embed(D_hop, landmarks)
    C_geo = geodesic_cost(X)

    # Compute hypercomplex ORC for all edges
    println("  Computing hypercomplex ORC ($E edges)...")
    edges_list = collect(edges(g))
    kappas_hyper = Vector{Float64}(undef, length(edges_list))
    n_nan = 0

    Threads.@threads for i in 1:length(edges_list)
        e = edges_list[i]
        kappas_hyper[i] = hypercomplex_edge_curvature(g, src(e), dst(e), C_geo; alpha=alpha)
    end

    # Filter NaN edges (degenerate embeddings)
    valid_idx = findall(!isnan, kappas_hyper)
    kappas_valid = kappas_hyper[valid_idx]
    n_nan = length(edges_list) - length(valid_idx)

    elapsed = time() - t0

    if isempty(kappas_valid)
        @warn "All edges produced NaN for $(spec.id) d=$d"
        return nothing
    end

    kappa_mean = mean(kappas_valid)
    kappa_std = std(kappas_valid)

    @printf("  κ̄_hyper = %+.6f ± %.4f  (d=%d, %d/%d valid edges, %.1fs)\n",
            kappa_mean, kappa_std, d, length(kappas_valid), E, elapsed)

    if n_nan > 0
        @printf("  (%d edges with degenerate embedding, filtered)\n", n_nan)
    end

    return Dict(
        "network_id" => spec.id,
        "category" => spec.category,
        "language" => spec.language,
        "N" => N,
        "E" => E,
        "mean_degree" => round(mean_k, digits=4),
        "embedding_dim" => d,
        "embedding_name" => embedding_name,
        "alpha" => alpha,
        "seed" => seed,
        "kappa_hyper_mean" => round(kappa_mean, digits=6),
        "kappa_hyper_std" => round(kappa_std, digits=6),
        "kappa_hyper_median" => round(median(kappas_valid), digits=6),
        "kappa_hyper_min" => round(minimum(kappas_valid), digits=6),
        "kappa_hyper_max" => round(maximum(kappas_valid), digits=6),
        "n_valid_edges" => length(kappas_valid),
        "n_nan_edges" => n_nan,
        "elapsed_seconds" => round(elapsed, digits=1)
    )
end

# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────

function main()
    println("="^70)
    println("HYPERCOMPLEX ORC on SEMANTIC NETWORKS")
    println("="^70)

    # Parse args
    all_dims = "--all-dims" in ARGS
    d_values = all_dims ? [4, 8, 16] : [4]

    net_filter = nothing
    for i in 1:length(ARGS)-1
        ARGS[i] == "--network" && (net_filter = ARGS[i+1])
        ARGS[i] == "--d" && !all_dims && (d_values = [parse(Int, ARGS[i+1])])
    end

    specs = isnothing(net_filter) ? NETWORKS :
            filter(s -> s.id == net_filter, NETWORKS)

    all_results = []

    for spec in specs
        for d in d_values
            result = process_hypercomplex(spec, d)
            !isnothing(result) && push!(all_results, result)
        end
    end

    # Summary
    println("\n\n", "="^70)
    println("SUMMARY: Hypercomplex ORC on Semantic Networks")
    println("="^70)
    @printf("%-22s %3s %5s %6s %10s\n", "Network", "d", "N", "E", "κ̄_hyper")
    println("-"^55)
    for r in all_results
        @printf("%-22s %3d %5d %6d %+10.4f\n",
                r["network_id"], r["embedding_dim"], r["N"], r["E"],
                r["kappa_hyper_mean"])
    end

    # Also load hop-count results for comparison if available
    println("\n--- Hop-count vs Hypercomplex comparison ---")
    @printf("%-22s %3s %10s %10s %10s\n", "Network", "d", "κ̄_hop", "κ̄_hyper", "Δκ")
    println("-"^65)
    for r in all_results
        hop_file = joinpath(RESULTS_DIR, "$(r["network_id"])_exact_lp.json")
        if isfile(hop_file)
            hop_data = JSON.parsefile(hop_file)
            kappa_hop = hop_data["kappa_mean"]
            delta = r["kappa_hyper_mean"] - kappa_hop
            @printf("%-22s %3d %+10.4f %+10.4f %+10.4f\n",
                    r["network_id"], r["embedding_dim"], kappa_hop,
                    r["kappa_hyper_mean"], delta)
        end
    end

    # Save
    mkpath(RESULTS_DIR)
    output_file = joinpath(RESULTS_DIR, "hypercomplex_semantic_orc.json")
    output = Dict(
        "experiment" => "hypercomplex_semantic_orc",
        "description" => "Sphere-embedded ORC on real semantic networks",
        "d_values" => d_values,
        "results" => all_results
    )
    open(output_file, "w") do f
        JSON.print(f, output, 2)
    end
    println("\nSAVED: $output_file")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
