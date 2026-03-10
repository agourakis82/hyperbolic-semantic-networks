"""
UNIFIED SEMANTIC NETWORK ORC — Exact LP Computation

Computes exact Ollivier-Ricci curvature for real semantic networks using the
same methodology as the phase transition paper (JuMP + HiGHS, α=0.5).

Loads edge CSVs from data/processed/, builds undirected SimpleGraph, extracts
largest connected component, and computes exact LP ORC for all edges.

Usage:
    julia unified_semantic_orc.jl                    # Run all networks
    julia unified_semantic_orc.jl --network swow_es  # Run single network
    julia unified_semantic_orc.jl --list              # List available networks
    julia unified_semantic_orc.jl --quick             # Run smallest network (BabelNet AR) as test
"""

import Pkg
let deps = Pkg.project().dependencies
    for pkg in ["JuMP", "HiGHS", "Graphs", "JSON", "CSV", "DataFrames"]
        if !haskey(deps, pkg)
            Pkg.add(pkg)
        end
    end
end

using JuMP
using HiGHS
using Graphs
using Statistics
using Random
using JSON
using Printf
using CSV
using DataFrames

# ─────────────────────────────────────────────────────────────────
# Network registry: all semantic networks with metadata
# ─────────────────────────────────────────────────────────────────

const DATA_DIR = joinpath(@__DIR__, "..", "..", "data", "processed")
const RESULTS_DIR = joinpath(@__DIR__, "..", "..", "results", "unified")

struct NetworkSpec
    id::String
    filename::String
    category::String     # "association", "knowledge", "taxonomy", "clinical"
    language::String
    has_relation::Bool   # CSV has a 'relation' column
end

const NETWORKS = [
    # SWOW association networks (source,target,weight — no relation column)
    NetworkSpec("swow_es", "spanish_edges_FINAL.csv", "association", "Spanish", false),
    NetworkSpec("swow_en", "english_edges_FINAL.csv", "association", "English", false),
    NetworkSpec("swow_zh", "chinese_edges_FINAL.csv", "association", "Chinese", false),
    NetworkSpec("swow_nl", "dutch_edges.csv", "association", "Dutch", false),

    # ConceptNet knowledge graphs (source,target,weight,relation)
    NetworkSpec("conceptnet_en", "conceptnet_en_edges.csv", "knowledge", "English", true),
    NetworkSpec("conceptnet_pt", "conceptnet_pt_edges.csv", "knowledge", "Portuguese", true),

    # Taxonomy networks (source,target,weight,relation)
    NetworkSpec("wordnet_en", "wordnet_edges.csv", "taxonomy", "English", true),
    NetworkSpec("wordnet_en_2k", "wordnet_N2000_edges.csv", "taxonomy", "English", true),
    NetworkSpec("babelnet_ru", "babelnet_ru_edges.csv", "taxonomy", "Russian", true),
    NetworkSpec("babelnet_ar", "babelnet_ar_edges.csv", "taxonomy", "Arabic", true),

    # --- EXTENDED NETWORKS (out-of-sample validation set) ---

    # EAT: Edinburgh Associative Thesaurus (British English, ~1970, N=500)
    # Alternative collection protocol: validates methodology generalization
    # Predicted: Hyperbolic (eta=1.85 < eta_c(500)=3.10, C>0.05 expected)
    NetworkSpec("eat_en", "eat_en_edges.csv", "association", "British English", false),

    # FrameNet 1.7: semantic frame relations (English, N~1200)
    # Domain-extension test: taxonomy-like, predicted Euclidean (eta~0.009, low C)
    NetworkSpec("framenet_en", "framenet_en_edges.csv", "frames", "English", false),

    # SWOW-RP22: Rioplatense Spanish word associations (Argentine/Uruguayan Spanish)
    # Same methodology as SWOW-ES/EN/ZH; predicted Hyperbolic (eta<<eta_c, low density)
    NetworkSpec("swow_rp", "swow_rp_edges.csv", "association", "Arg. Spanish", false),

    # OdeNet (German WordNet): hypernymy taxonomy, similar structure to WordNet-EN
    # Predicted: Euclidean (low C, low eta, taxonomy structure like WordNet-EN)
    NetworkSpec("wordnet_de", "wordnet_de_edges.csv", "taxonomy", "German", false),

    # USF Free Association Norms (Nelson, McEvoy & Schreiber 1998): American English
    # Alternative collection protocol: validates EAT finding with different culture/era
    # Predicted: Hyperbolic (association network, expected low eta, C~0.1)
    NetworkSpec("usf_en", "usf_en_edges.csv", "association", "American English", false),

    # Depression severity networks (source,target,weight — no relation column)
    NetworkSpec("depression_minimum", "depression_networks_optimal/depression_minimum_edges.csv", "clinical", "English", false),
    NetworkSpec("depression_mild", "depression_networks_optimal/depression_mild_edges.csv", "clinical", "English", false),
    NetworkSpec("depression_moderate", "depression_networks_optimal/depression_moderate_edges.csv", "clinical", "English", false),
    NetworkSpec("depression_severe", "depression_networks_optimal/depression_severe_edges.csv", "clinical", "English", false),
]

# ─────────────────────────────────────────────────────────────────
# CSV loader → undirected SimpleGraph (largest connected component)
# ─────────────────────────────────────────────────────────────────

"""
    load_network(spec::NetworkSpec) -> (g, node_names, edge_weights)

Load an edge CSV and build an undirected SimpleGraph.
Returns the largest connected component with node name mapping.
"""
function load_network(spec::NetworkSpec)
    filepath = joinpath(DATA_DIR, spec.filename)
    if !isfile(filepath)
        error("File not found: $filepath")
    end

    df = CSV.read(filepath, DataFrame; stringtype=String)

    # Collect unique nodes
    all_nodes = sort(unique(vcat(df.source, df.target)))
    node_to_id = Dict(name => i for (i, name) in enumerate(all_nodes))
    N = length(all_nodes)

    # Build undirected graph
    g = SimpleGraph(N)
    edge_weights = Dict{Tuple{Int,Int}, Float64}()

    for row in eachrow(df)
        u = node_to_id[row.source]
        v = node_to_id[row.target]
        if u != v  # skip self-loops
            add_edge!(g, u, v)
            # Store weight (take max if edge appears in both directions)
            key = minmax(u, v)
            w = Float64(row.weight)
            edge_weights[key] = max(get(edge_weights, key, 0.0), w)
        end
    end

    # Extract largest connected component
    ccs = connected_components(g)
    if length(ccs) > 1
        largest_cc = ccs[argmax(length.(ccs))]
        g_lcc, vmap = induced_subgraph(g, sort(largest_cc))

        # Remap node names
        id_to_name = Dict(i => name for (name, i) in node_to_id)
        lcc_names = [id_to_name[vmap[i]] for i in 1:nv(g_lcc)]

        # Remap edge weights
        lcc_weights = Dict{Tuple{Int,Int}, Float64}()
        for e in edges(g_lcc)
            old_u, old_v = vmap[src(e)], vmap[dst(e)]
            key_old = minmax(old_u, old_v)
            key_new = minmax(src(e), dst(e))
            if haskey(edge_weights, key_old)
                lcc_weights[key_new] = edge_weights[key_old]
            end
        end

        return g_lcc, lcc_names, lcc_weights
    end

    id_to_name = Dict(i => name for (name, i) in node_to_id)
    names = [id_to_name[i] for i in 1:N]
    return g, names, edge_weights
end

# ─────────────────────────────────────────────────────────────────
# Graph metrics
# ─────────────────────────────────────────────────────────────────

"""
    compute_graph_metrics(g) -> NamedTuple

Compute standard graph metrics: N, E, mean degree, clustering, degree std, eta.
"""
function compute_graph_metrics(g::SimpleGraph)
    N = nv(g)
    E = ne(g)
    degrees = degree(g)
    mean_k = 2.0 * E / N
    sigma_k = std(degrees)
    eta = mean_k^2 / N

    # Global clustering coefficient (fraction of closed triplets)
    triangles_total = 0
    triplets_total = 0
    for v in vertices(g)
        nbrs = neighbors(g, v)
        d = length(nbrs)
        if d >= 2
            triplets_total += d * (d - 1) ÷ 2
            for i in 1:length(nbrs)
                for j in (i+1):length(nbrs)
                    if has_edge(g, nbrs[i], nbrs[j])
                        triangles_total += 1
                    end
                end
            end
        end
    end
    clustering = triplets_total > 0 ? triangles_total / triplets_total : 0.0

    return (N=N, E=E, mean_k=mean_k, sigma_k=sigma_k, eta=eta,
            clustering=clustering, degrees=degrees,
            min_degree=minimum(degrees), max_degree=maximum(degrees),
            median_degree=median(degrees))
end

# ─────────────────────────────────────────────────────────────────
# Exact Wasserstein-1 via LP (reused from exact_curvature_lp.jl)
# ─────────────────────────────────────────────────────────────────

function exact_wasserstein1(mu::Vector{Float64}, nu::Vector{Float64},
                            C::Matrix{Float64})::Float64
    n = length(mu)
    @assert length(nu) == n
    @assert size(C) == (n, n)

    model = Model(HiGHS.Optimizer)
    set_silent(model)

    @variable(model, gamma[1:n, 1:n] >= 0)
    @constraint(model, source[i=1:n], sum(gamma[i, j] for j in 1:n) == mu[i])
    @constraint(model, target[j=1:n], sum(gamma[i, j] for i in 1:n) == nu[j])
    @objective(model, Min, sum(C[i, j] * gamma[i, j] for i in 1:n, j in 1:n))

    optimize!(model)

    if termination_status(model) != OPTIMAL
        @warn "LP not optimal, status=$(termination_status(model))"
        return NaN
    end

    return objective_value(model)
end

# ─────────────────────────────────────────────────────────────────
# ORC with precomputed APSP (optimized for real networks)
# ─────────────────────────────────────────────────────────────────

"""
    precompute_apsp(g) -> Matrix{Int}

All-pairs shortest paths via BFS. Returns N×N distance matrix.
"""
function precompute_apsp(g::SimpleGraph)
    N = nv(g)
    D = Matrix{Int}(undef, N, N)
    Threads.@threads for v in 1:N
        D[v, :] = gdistances(g, v)
    end
    return D
end

"""
    compute_edge_curvature_apsp(g, u, v, D; alpha=0.5) -> Float64

Compute exact ORC for edge (u,v) using precomputed distance matrix D.
"""
function compute_edge_curvature_apsp(g::SimpleGraph, u::Int, v::Int,
                                      D::Matrix{Int}; alpha::Float64=0.5)::Float64
    # Build probability measures
    mu_u = Dict{Int, Float64}()
    mu_v = Dict{Int, Float64}()

    mu_u[u] = alpha
    mu_v[v] = alpha

    nbrs_u = neighbors(g, u)
    nbrs_v = neighbors(g, v)

    if length(nbrs_u) > 0
        w = (1.0 - alpha) / length(nbrs_u)
        for z in nbrs_u
            mu_u[z] = get(mu_u, z, 0.0) + w
        end
    end

    if length(nbrs_v) > 0
        w = (1.0 - alpha) / length(nbrs_v)
        for z in nbrs_v
            mu_v[z] = get(mu_v, z, 0.0) + w
        end
    end

    # Support = union of both measures
    all_nodes = sort(unique(vcat(collect(keys(mu_u)), collect(keys(mu_v)))))
    n = length(all_nodes)
    node_to_idx = Dict(node => i for (i, node) in enumerate(all_nodes))

    # Build probability vectors
    mu_vec = zeros(n)
    nu_vec = zeros(n)
    for (node, prob) in mu_u
        mu_vec[node_to_idx[node]] = prob
    end
    for (node, prob) in mu_v
        nu_vec[node_to_idx[node]] = prob
    end

    # Cost matrix from precomputed APSP
    C = zeros(n, n)
    for i in 1:n
        for j in 1:n
            C[i, j] = Float64(D[all_nodes[i], all_nodes[j]])
        end
    end

    W1 = exact_wasserstein1(mu_vec, nu_vec, C)

    d_uv = Float64(D[u, v])
    if d_uv == 0.0
        return 0.0
    end
    return 1.0 - W1 / d_uv
end

"""
    compute_all_curvatures(g, D; alpha=0.5) -> Vector{Float64}

Compute exact ORC for all edges using precomputed APSP.
Multi-threaded for performance.
"""
function compute_all_curvatures(g::SimpleGraph, D::Matrix{Int};
                                 alpha::Float64=0.5)::Vector{Float64}
    edges_list = collect(edges(g))
    n_edges = length(edges_list)
    kappas = Vector{Float64}(undef, n_edges)

    Threads.@threads for i in 1:n_edges
        e = edges_list[i]
        kappas[i] = compute_edge_curvature_apsp(g, src(e), dst(e), D; alpha=alpha)
    end

    return kappas
end

# ─────────────────────────────────────────────────────────────────
# LLY curvature (for comparison)
# ─────────────────────────────────────────────────────────────────

function compute_edge_lly(g::SimpleGraph, u::Int, v::Int)::Float64
    nbrs_u = Set(neighbors(g, u))
    nbrs_v = Set(neighbors(g, v))
    triangles = length(intersect(nbrs_u, nbrs_v))
    d_u = degree(g, u)
    d_v = degree(g, v)
    if d_u == 0 || d_v == 0
        return 0.0
    end
    return (2 * triangles + 2 - max(d_u, d_v)) / max(d_u, d_v)
end

# ─────────────────────────────────────────────────────────────────
# Main: process a single network
# ─────────────────────────────────────────────────────────────────

function process_network(spec::NetworkSpec; alpha::Float64=0.5, save::Bool=true)
    println("\n", "="^70)
    println("NETWORK: $(spec.id) ($(spec.category) / $(spec.language))")
    println("File: $(spec.filename)")
    println("="^70)

    # Load
    t0 = time()
    g, node_names, edge_weights = load_network(spec)
    t_load = time() - t0

    # Metrics
    metrics = compute_graph_metrics(g)
    @printf("  Loaded: N=%d  E=%d  <k>=%.2f  C=%.4f  σ_k=%.2f  η=%.4f  (%.1fs)\n",
            metrics.N, metrics.E, metrics.mean_k, metrics.clustering,
            metrics.sigma_k, metrics.eta, t_load)

    # Precompute APSP
    t0 = time()
    println("  Computing all-pairs shortest paths...")
    D = precompute_apsp(g)
    t_apsp = time() - t0
    @printf("  APSP done (%.1fs)\n", t_apsp)

    # Check connectivity: max distance
    max_dist = maximum(D)
    mean_dist = mean(D[D .> 0])
    @printf("  Diameter=%d  Mean path length=%.2f\n", max_dist, mean_dist)

    # Compute exact ORC
    t0 = time()
    println("  Computing exact LP ORC ($(metrics.E) edges, $(Threads.nthreads()) threads)...")
    kappas = compute_all_curvatures(g, D; alpha=alpha)
    t_orc = time() - t0
    @printf("  ORC done (%.1fs)\n", t_orc)

    # LLY curvature
    lly_kappas = [compute_edge_lly(g, src(e), dst(e)) for e in edges(g)]

    # Summary statistics
    kappa_mean = mean(kappas)
    kappa_std = std(kappas)
    kappa_median = median(kappas)
    lly_mean = mean(lly_kappas)

    if kappa_mean < -0.05
        geometry = "HYPERBOLIC"
    elseif kappa_mean > 0.05
        geometry = "SPHERICAL"
    else
        geometry = "EUCLIDEAN/TRANSITION"
    end

    @printf("\n  RESULT: κ̄ = %+.6f ± %.4f  (median=%+.4f)  [%s]\n",
            kappa_mean, kappa_std, kappa_median, geometry)
    @printf("          κ_LLY = %+.6f\n", lly_mean)
    @printf("          κ_min = %+.4f  κ_max = %+.4f\n", minimum(kappas), maximum(kappas))
    @printf("          Total time: %.1fs (APSP: %.1fs, ORC: %.1fs)\n",
            t_apsp + t_orc, t_apsp, t_orc)

    # Fraction of hyperbolic/spherical/flat edges
    n_hyp = count(k -> k < -0.01, kappas)
    n_sph = count(k -> k > 0.01, kappas)
    n_flat = metrics.E - n_hyp - n_sph
    @printf("          Edges: %d hyperbolic (%.1f%%), %d spherical (%.1f%%), %d flat (%.1f%%)\n",
            n_hyp, 100*n_hyp/metrics.E, n_sph, 100*n_sph/metrics.E, n_flat, 100*n_flat/metrics.E)

    # Save results
    if save
        mkpath(RESULTS_DIR)
        output_file = joinpath(RESULTS_DIR, "$(spec.id)_exact_lp.json")

        result = Dict(
            "experiment" => "unified_semantic_orc",
            "network_id" => spec.id,
            "filename" => spec.filename,
            "category" => spec.category,
            "language" => spec.language,
            "method" => "exact_LP",
            "solver" => "HiGHS",
            "alpha" => alpha,
            "graph_type" => "undirected_unweighted",

            # Graph metrics
            "N" => metrics.N,
            "E" => metrics.E,
            "mean_degree" => round(metrics.mean_k, digits=4),
            "degree_std" => round(metrics.sigma_k, digits=4),
            "min_degree" => metrics.min_degree,
            "max_degree" => metrics.max_degree,
            "median_degree" => metrics.median_degree,
            "clustering" => round(metrics.clustering, digits=6),
            "eta" => round(metrics.eta, digits=6),
            "diameter" => max_dist,
            "mean_path_length" => round(mean_dist, digits=4),

            # ORC results
            "kappa_mean" => round(kappa_mean, digits=6),
            "kappa_std" => round(kappa_std, digits=6),
            "kappa_median" => round(kappa_median, digits=6),
            "kappa_min" => round(minimum(kappas), digits=6),
            "kappa_max" => round(maximum(kappas), digits=6),
            "geometry" => geometry,
            "frac_hyperbolic" => round(n_hyp / metrics.E, digits=4),
            "frac_spherical" => round(n_sph / metrics.E, digits=4),

            # LLY comparison
            "lly_kappa_mean" => round(lly_mean, digits=6),
            "lly_kappa_std" => round(std(lly_kappas), digits=6),

            # Per-edge curvatures (for downstream analysis)
            "per_edge_curvatures" => round.(kappas, digits=6),
            "per_edge_lly" => round.(lly_kappas, digits=6),

            # Timing
            "elapsed_apsp_seconds" => round(t_apsp, digits=1),
            "elapsed_orc_seconds" => round(t_orc, digits=1),
            "elapsed_total_seconds" => round(t_apsp + t_orc, digits=1),
            "n_threads" => Threads.nthreads()
        )

        open(output_file, "w") do f
            JSON.print(f, result, 2)
        end
        println("  SAVED: $output_file")
    end

    return (spec=spec, metrics=metrics, kappa_mean=kappa_mean, kappa_std=kappa_std,
            kappa_median=kappa_median, geometry=geometry, kappas=kappas,
            lly_mean=lly_mean)
end

# ─────────────────────────────────────────────────────────────────
# Run all networks
# ─────────────────────────────────────────────────────────────────

function run_all(; alpha::Float64=0.5)
    println("="^70)
    println("UNIFIED SEMANTIC NETWORK ORC — Exact LP Computation")
    println("Method: JuMP + HiGHS, α=$alpha, undirected unweighted")
    println("Threads: $(Threads.nthreads())")
    println("Networks: $(length(NETWORKS))")
    println("="^70)

    results = []
    for spec in NETWORKS
        try
            r = process_network(spec; alpha=alpha)
            push!(results, r)
        catch e
            @warn "FAILED: $(spec.id)" exception=e
        end
    end

    # Summary table
    println("\n\n", "="^70)
    println("SUMMARY TABLE")
    println("="^70)
    @printf("%-22s %5s %6s %6s %8s %8s %10s  %s\n",
            "Network", "N", "E", "<k>", "C", "η", "κ̄", "Geometry")
    println("-"^80)

    for r in results
        @printf("%-22s %5d %6d %6.2f %8.4f %8.4f %+10.6f  %s\n",
                r.spec.id, r.metrics.N, r.metrics.E, r.metrics.mean_k,
                r.metrics.clustering, r.metrics.eta, r.kappa_mean, r.geometry)
    end

    # Save summary
    mkpath(RESULTS_DIR)
    summary_file = joinpath(RESULTS_DIR, "summary_all_networks.json")
    summary_data = Dict(
        "experiment" => "unified_semantic_orc_summary",
        "method" => "exact_LP",
        "solver" => "HiGHS",
        "alpha" => alpha,
        "n_threads" => Threads.nthreads(),
        "networks" => [Dict(
            "id" => r.spec.id,
            "category" => r.spec.category,
            "language" => r.spec.language,
            "N" => r.metrics.N,
            "E" => r.metrics.E,
            "mean_k" => round(r.metrics.mean_k, digits=4),
            "clustering" => round(r.metrics.clustering, digits=6),
            "eta" => round(r.metrics.eta, digits=6),
            "kappa_mean" => round(r.kappa_mean, digits=6),
            "kappa_std" => round(r.kappa_std, digits=6),
            "kappa_median" => round(r.kappa_median, digits=6),
            "lly_kappa_mean" => round(r.lly_mean, digits=6),
            "geometry" => r.geometry
        ) for r in results]
    )
    open(summary_file, "w") do f
        JSON.print(f, summary_data, 2)
    end
    println("\nSummary saved: $summary_file")

    return results
end

# ─────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────

if abspath(PROGRAM_FILE) == @__FILE__
    if "--list" in ARGS
        println("Available networks:")
        for spec in NETWORKS
            println("  $(spec.id)  ($(spec.category)/$(spec.language))  $(spec.filename)")
        end
    elseif "--quick" in ARGS
        # Quick test: smallest network (BabelNet AR)
        spec = NETWORKS[findfirst(s -> s.id == "babelnet_ar", NETWORKS)]
        process_network(spec)
    elseif any(startswith(a, "--network") for a in ARGS)
        idx = findfirst(startswith("--network"), ARGS)
        if idx !== nothing
            # Handle --network=name or --network name
            parts = split(ARGS[idx], "=")
            net_id = length(parts) > 1 ? parts[2] : (idx < length(ARGS) ? ARGS[idx+1] : "")
            spec_idx = findfirst(s -> s.id == net_id, NETWORKS)
            if spec_idx !== nothing
                process_network(NETWORKS[spec_idx])
            else
                println("Unknown network: $net_id")
                println("Available: $(join([s.id for s in NETWORKS], ", "))")
            end
        end
    else
        run_all()
    end
end
