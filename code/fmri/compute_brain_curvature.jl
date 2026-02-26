"""
BRAIN FUNCTIONAL CONNECTIVITY — Ollivier-Ricci Curvature

Computes exact Ollivier-Ricci curvature on functional connectivity graphs
derived from fMRI data, and tests the orc_hypercomplex_correspondence axiom:

    κ̄ < 0  ↔  ‖snd‖² > ‖fst‖²   (hyperbolic ↔ distributed networks)
    κ̄ > 0  ↔  ‖fst‖² > ‖snd‖²   (spherical  ↔ global signal)

where x = brainState(global, dmn, smn, vn, dan, van, fpn, lim) ∈ 𝕆 (octonion),
fst = x[1:4], snd = x[5:8] (Cayley-Dickson decomposition).

Usage:
    julia compute_brain_curvature.jl                            # synthetic demo
    julia compute_brain_curvature.jl --edges path/to/edges.csv  # custom edge list

Input edge CSV format (from extract_hcp_data.py or example_synthetic_analysis.py):
    source,target,weight
    roi_0,roi_1,0.61
    ...

Output:
    results/fmri/curvature/synthetic_orc_results.json

NOTE: The module→octonion mapping used here assigns the 8 synthetic network
modules to octonion coordinates as a proof-of-concept. Real fMRI requires
a principled RSN assignment:
    fst = [global, DMN, SMN, VN]
    snd = [DAN, VAN, FPN, Limbic]
matching the Lean brainState definition in Hypercomplex.lean.
"""

import Pkg
let deps = Pkg.project().dependencies
    for pkg in ["JuMP", "HiGHS", "Graphs", "JSON", "CSV", "DataFrames", "Statistics"]
        if !haskey(deps, pkg)
            Pkg.add(pkg)
        end
    end
end

using JuMP, HiGHS, Graphs, Statistics, JSON, CSV, DataFrames, Printf, LinearAlgebra

# ──────────────────────────────────────────────────────────────────────────────
# Core LP (same pattern as exact_curvature_lp.jl)
# ──────────────────────────────────────────────────────────────────────────────

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

# ──────────────────────────────────────────────────────────────────────────────
# Load FC edge list → unweighted SimpleGraph + weight dictionary
# ──────────────────────────────────────────────────────────────────────────────

"""
    load_fc_graph(edges_csv) -> (g, node_list, edge_weights)

Load a functional connectivity edge list into a SimpleGraph.
Returns:
- g: SimpleGraph (for BFS/topology)
- node_list: sorted list of node name strings
- edge_weights: Dict{Tuple{Int,Int}, Float64} by integer index pairs
"""
function load_fc_graph(edges_csv::String)
    df = CSV.read(edges_csv, DataFrame)

    # Collect unique nodes, assign integer indices
    all_nodes = unique(vcat(df.source, df.target))
    sort!(all_nodes)
    node_idx = Dict(n => i for (i, n) in enumerate(all_nodes))
    N = length(all_nodes)

    g = SimpleGraph(N)
    edge_weights = Dict{Tuple{Int,Int}, Float64}()

    for row in eachrow(df)
        u = node_idx[row.source]
        v = node_idx[row.target]
        add_edge!(g, u, v)
        key = (min(u, v), max(u, v))
        edge_weights[key] = row.weight
    end

    return g, all_nodes, edge_weights
end

# ──────────────────────────────────────────────────────────────────────────────
# Graph-based probability measure (idleness α=0.5)
# ──────────────────────────────────────────────────────────────────────────────

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

# ──────────────────────────────────────────────────────────────────────────────
# ORC via exact LP (hop-count transport cost)
# ──────────────────────────────────────────────────────────────────────────────

function compute_edge_orc(g::SimpleGraph, u::Int, v::Int; alpha::Float64=0.5)::Float64
    mu_u = build_prob_measure(g, u, alpha)
    mu_v = build_prob_measure(g, v, alpha)

    all_nodes = sort(unique(vcat(collect(keys(mu_u)), collect(keys(mu_v)))))
    n = length(all_nodes)

    mu_vec = [get(mu_u, all_nodes[i], 0.0) for i in 1:n]
    nu_vec = [get(mu_v, all_nodes[i], 0.0) for i in 1:n]

    # Hop-count cost matrix (local BFS)
    C = zeros(Float64, n, n)
    for i in 1:n
        dists = gdistances(g, all_nodes[i])
        for j in 1:n
            C[i, j] = Float64(dists[all_nodes[j]])
        end
    end

    d_uv = Float64(gdistances(g, u)[v])
    d_uv < 1e-10 && return 0.0

    W1 = exact_wasserstein1(mu_vec, nu_vec, C)
    return 1.0 - W1 / d_uv
end

"""
    compute_orc(g; alpha, verbose) -> (mean_κ, per_edge_κ)

Compute ORC for all edges in g using exact LP and hop-count distances.
"""
function compute_orc(g::SimpleGraph; alpha::Float64=0.5, verbose::Bool=true)
    edges_list = collect(edges(g))
    n_edges = length(edges_list)
    verbose && println("Computing ORC for $n_edges edges (hop-count, α=$alpha)...")

    kappas = Vector{Float64}(undef, n_edges)
    Threads.@threads for i in 1:n_edges
        e = edges_list[i]
        kappas[i] = compute_edge_orc(g, src(e), dst(e); alpha=alpha)
    end

    valid = filter(!isnan, kappas)
    return mean(valid), kappas
end

# ──────────────────────────────────────────────────────────────────────────────
# Module assignment and octonionic norm test
# ──────────────────────────────────────────────────────────────────────────────

"""
    assign_modules(N, n_modules=8) -> Vector{Int}

Divide N nodes into n_modules equal-ish groups (0-indexed module IDs).
Module i contains nodes: floor(i*N/n_modules) .. floor((i+1)*N/n_modules)-1
"""
function assign_modules(N::Int, n_modules::Int=8)::Vector{Int}
    modules = Vector{Int}(undef, N)
    for i in 0:N-1
        modules[i+1] = floor(Int, i * n_modules / N)
    end
    return modules
end

"""
    compute_module_signals(g, edge_weights, modules) -> Vector{Float64}

For each module, compute mean edge weight among within-module edges.
Used as a proxy for the "octonion coordinate" in the absence of BOLD signals.
Returns a vector of length n_modules.

NOTE: For real fMRI, replace with mean BOLD signal per RSN parcellation.
"""
function compute_module_signals(g::SimpleGraph, edge_weights::Dict{Tuple{Int,Int},Float64},
                                 modules::Vector{Int})::Vector{Float64}
    n_modules = maximum(modules) + 1
    module_weights = [Float64[] for _ in 1:n_modules]

    for (key, w) in edge_weights
        u, v = key
        if modules[u] == modules[v]
            push!(module_weights[modules[u]+1], w)
        end
    end

    signals = Float64[]
    for m in 1:n_modules
        push!(signals, isempty(module_weights[m]) ? 0.0 : mean(module_weights[m]))
    end
    return signals
end

"""
    octonionic_norm_test(mean_kappa, module_signals) -> NamedTuple

Test the orc_hypercomplex_correspondence axiom:
    κ̄ < 0  ↔  ‖snd‖² > ‖fst‖²

Maps 8 module signals to octonion coordinates (Cayley-Dickson decomposition):
    fst = module_signals[1:4]  (global + DMN-like networks)
    snd = module_signals[5:8]  (task-positive networks)

Returns: (predicted, actual, match, norm_fst, norm_snd, details)

CAVEAT: For synthetic data, module→coordinate mapping is arbitrary.
Real fMRI requires the principled mapping from Hypercomplex.lean.
"""
function octonionic_norm_test(mean_kappa::Float64, module_signals::Vector{Float64})
    @assert length(module_signals) == 8 "Need exactly 8 module signals for octonion"
    fst = module_signals[1:4]
    snd = module_signals[5:8]
    norm_fst_sq = sum(x^2 for x in fst)
    norm_snd_sq = sum(x^2 for x in snd)

    predicted_hyp = norm_snd_sq > norm_fst_sq   # axiom: κ̄ < 0 ↔ snd dominates
    actual_hyp    = mean_kappa < 0

    return (
        predicted_hyperbolic = predicted_hyp,
        actual_hyperbolic    = actual_hyp,
        axiom_match          = predicted_hyp == actual_hyp,
        norm_fst_sq          = round(norm_fst_sq, digits=6),
        norm_snd_sq          = round(norm_snd_sq, digits=6),
        module_signals       = round.(module_signals, digits=4),
    )
end

# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

function main()
    args = ARGS
    default_edges = joinpath(@__DIR__, "../../results/fmri/synthetic_demo/synthetic_edges.csv")
    edges_csv = default_edges

    for i in 1:length(args)-1
        args[i] == "--edges" && (edges_csv = args[i+1])
    end

    isfile(edges_csv) || error("Edge list not found: $edges_csv")
    println("Loading graph from: $edges_csv")

    g, node_list, edge_weights = load_fc_graph(edges_csv)
    N = nv(g)
    E = ne(g)
    println("Graph: $N nodes, $E edges, mean degree = $(round(2E/N, digits=2))")

    # ORC computation
    mean_kappa, per_edge_kappas = compute_orc(g; verbose=true)
    @printf("Mean κ̄ = %.4f\n", mean_kappa)
    geometry = mean_kappa < -0.05 ? "hyperbolic" : mean_kappa > 0.05 ? "spherical" : "flat"
    println("Geometry: $geometry")

    # Module assignment (synthetic: 8 equal groups)
    modules = assign_modules(N, 8)
    module_signals = compute_module_signals(g, edge_weights, modules)
    println("\nModule mean connectivity signals (proxy for octonion coordinates):")
    for m in 1:8
        coord = m <= 4 ? "fst[$(m)]" : "snd[$(m-4)]"
        @printf("  Module %d (%s): %.4f\n", m, coord, module_signals[m])
    end

    # Octonionic norm test
    oct_result = octonionic_norm_test(mean_kappa, module_signals)
    println("\n── Octonionic norm test (orc_hypercomplex_correspondence) ──")
    @printf("  ‖fst‖² = %.4f  |  ‖snd‖² = %.4f\n", oct_result.norm_fst_sq, oct_result.norm_snd_sq)
    @printf("  Axiom predicts: %s  |  Actual: %s  |  Match: %s\n",
            oct_result.predicted_hyperbolic ? "hyperbolic" : "spherical",
            oct_result.actual_hyperbolic    ? "hyperbolic" : "spherical",
            oct_result.axiom_match ? "✓ YES" : "✗ NO")

    println("\nNOTE: Module→octonion mapping is arbitrary for synthetic data.")
    println("Real fMRI requires: fst=[global,DMN,SMN,VN], snd=[DAN,VAN,FPN,Limbic]")

    # Save results
    outdir = joinpath(@__DIR__, "../../results/fmri/curvature")
    mkpath(outdir)
    outfile = joinpath(outdir, "synthetic_orc_results.json")

    results = Dict(
        "input_file"   => edges_csv,
        "n_nodes"      => N,
        "n_edges"      => E,
        "mean_degree"  => round(2E/N, digits=4),
        "alpha"        => 0.5,
        "mean_kappa"   => round(mean_kappa, digits=6),
        "geometry"     => geometry,
        "kappa_std"    => round(std(filter(!isnan, per_edge_kappas)), digits=6),
        "octonionic"   => Dict(
            "norm_fst_sq"          => oct_result.norm_fst_sq,
            "norm_snd_sq"          => oct_result.norm_snd_sq,
            "predicted_hyperbolic" => oct_result.predicted_hyperbolic,
            "actual_hyperbolic"    => oct_result.actual_hyperbolic,
            "axiom_match"          => oct_result.axiom_match,
            "module_signals"       => oct_result.module_signals,
            "mapping_note"         => "Synthetic: modules 1-4→fst, 5-8→snd (arbitrary). Real fMRI: global,DMN,SMN,VN→fst; DAN,VAN,FPN,Limbic→snd."
        ),
    )

    open(outfile, "w") do f
        JSON.print(f, results, 2)
    end
    println("\nSaved → $outfile")
end

main()
