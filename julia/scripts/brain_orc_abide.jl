"""
B1: EXACT LP ORC ON ABIDE-I BRAIN GRAPHS

Loads thresholded binary brain graphs (CC200, N=200) exported by
code/fmri/abide_threshold_graphs.py and computes exact Ollivier-Ricci
curvature via JuMP + HiGHS linear programming.

Uses all-pairs shortest paths (APSP) precomputation for efficiency.

Usage:
    julia --project=julia -t8 julia/scripts/brain_orc_abide.jl
    julia --project=julia -t8 julia/scripts/brain_orc_abide.jl --threshold 0.50
    julia --project=julia -t8 julia/scripts/brain_orc_abide.jl --subject Pitt_0050003
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
using JSON
using Printf
using CSV
using DataFrames

# ─────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────

const GRAPH_DIR = joinpath(@__DIR__, "..", "..", "data", "processed", "abide_graphs")
const PHENO_CSV = joinpath(@__DIR__, "..", "..", "data", "processed", "abide_phenotypic_matched.csv")
const RESULTS_DIR = joinpath(@__DIR__, "..", "..", "results", "fmri", "abide_orc")
mkpath(RESULTS_DIR)

const ALPHA = 0.5
const ETA_C_200 = 3.75 - 14.62 / sqrt(200)  # ≈ 2.72

# ─────────────────────────────────────────────────────────────────
# Exact Wasserstein-1 via LP (from exact_curvature_lp.jl)
# ─────────────────────────────────────────────────────────────────

function exact_wasserstein1(mu::Vector{Float64}, nu::Vector{Float64},
                            C::Matrix{Float64})::Float64
    n = length(mu)
    model = Model(HiGHS.Optimizer)
    set_silent(model)
    @variable(model, gamma[1:n, 1:n] >= 0)
    @constraint(model, [i=1:n], sum(gamma[i, j] for j in 1:n) == mu[i])
    @constraint(model, [j=1:n], sum(gamma[i, j] for i in 1:n) == nu[j])
    @objective(model, Min, sum(C[i, j] * gamma[i, j] for i in 1:n, j in 1:n))
    optimize!(model)
    termination_status(model) != OPTIMAL && return NaN
    return objective_value(model)
end

# ─────────────────────────────────────────────────────────────────
# ORC with precomputed APSP
# ─────────────────────────────────────────────────────────────────

function compute_edge_orc_apsp(g::SimpleGraph, u::Int, v::Int,
                                D::Matrix{Int}; alpha::Float64=0.5)::Float64
    # Build probability measures
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

    # Support
    all_nodes = sort(unique(vcat(collect(keys(mu_u)), collect(keys(mu_v)))))
    n = length(all_nodes)
    node_to_idx = Dict(node => i for (i, node) in enumerate(all_nodes))

    mu_vec = zeros(n)
    nu_vec = zeros(n)
    for (node, prob) in mu_u; mu_vec[node_to_idx[node]] = prob; end
    for (node, prob) in mu_v; nu_vec[node_to_idx[node]] = prob; end

    # Cost matrix from precomputed APSP
    C = zeros(n, n)
    for i in 1:n, j in 1:n
        C[i, j] = Float64(D[all_nodes[i], all_nodes[j]])
    end

    W1 = exact_wasserstein1(mu_vec, nu_vec, C)
    d_uv = Float64(D[u, v])
    d_uv == 0.0 && return 0.0
    return 1.0 - W1 / d_uv
end

# ─────────────────────────────────────────────────────────────────
# Graph loader
# ─────────────────────────────────────────────────────────────────

function load_brain_graph(filepath::String)
    df = CSV.read(filepath, DataFrame)
    all_nodes = sort(unique(vcat(df.source, df.target)))
    # Remap to 1-indexed contiguous IDs
    node_to_id = Dict(n => i for (i, n) in enumerate(all_nodes))
    N = length(all_nodes)
    g = SimpleGraph(N)
    for row in eachrow(df)
        u = node_to_id[row.source]
        v = node_to_id[row.target]
        u != v && add_edge!(g, u, v)
    end
    return g
end

# ─────────────────────────────────────────────────────────────────
# APSP via threaded BFS
# ─────────────────────────────────────────────────────────────────

function compute_apsp(g::SimpleGraph)
    N = nv(g)
    D = Matrix{Int}(undef, N, N)
    Threads.@threads for u in 1:N
        D[u, :] = gdistances(g, u)
    end
    return D
end

# ─────────────────────────────────────────────────────────────────
# Process a single subject
# ─────────────────────────────────────────────────────────────────

function process_subject(file_id, threshold::Float64, pheno_row)
    file_id_str = string(file_id)
    edge_file = joinpath(GRAPH_DIR, "$(file_id_str)_t$(Printf.@sprintf("%.2f", threshold))_edges.csv")
    if !isfile(edge_file)
        @warn "Missing edge file: $edge_file"
        return nothing
    end

    t_start = time()

    # Load graph
    g = load_brain_graph(edge_file)

    # Extract LCC
    ccs = connected_components(g)
    lcc_idx = argmax(length.(ccs))
    if length(ccs[lcc_idx]) < nv(g)
        g_lcc, vmap = induced_subgraph(g, ccs[lcc_idx])
        g = g_lcc
    end

    N = nv(g)
    E = ne(g)
    mean_k = 2.0 * E / N
    eta = mean_k^2 / N

    @printf("  %s: N=%d, E=%d, k=%.1f, η=%.2f ", file_id_str, N, E, mean_k, eta)

    # Precompute APSP
    D = compute_apsp(g)

    # Compute ORC for all edges (threaded)
    edges_list = collect(edges(g))
    n_edges = length(edges_list)
    kappas = Vector{Float64}(undef, n_edges)

    Threads.@threads for i in 1:n_edges
        e = edges_list[i]
        kappas[i] = compute_edge_orc_apsp(g, src(e), dst(e), D; alpha=ALPHA)
    end

    # Filter NaN
    valid_kappas = filter(!isnan, kappas)
    kappa_mean = mean(valid_kappas)
    kappa_std = std(valid_kappas)
    frac_positive = count(k -> k > 0, valid_kappas) / length(valid_kappas)

    elapsed = time() - t_start
    geometry = eta > ETA_C_200 ? (kappa_mean > 0 ? "SPHERICAL" : "ANOMALOUS_HYP") :
                                 (kappa_mean < 0 ? "HYPERBOLIC" : "ANOMALOUS_SPH")

    @printf("→ κ̄=%.4f (%s) [%.1fs]\n", kappa_mean, geometry, elapsed)

    return Dict(
        "file_id" => file_id_str,
        "dx_group" => pheno_row.dx_group,
        "site_id" => pheno_row.site_id,
        "age" => pheno_row.age,
        "sex" => pheno_row.sex,
        "threshold" => threshold,
        "N" => N,
        "n_edges" => E,
        "mean_k" => round(mean_k; digits=2),
        "eta" => round(eta; digits=4),
        "eta_c" => round(ETA_C_200; digits=4),
        "kappa_mean" => round(kappa_mean; digits=6),
        "kappa_std" => round(kappa_std; digits=6),
        "kappa_min" => round(minimum(valid_kappas); digits=6),
        "kappa_max" => round(maximum(valid_kappas); digits=6),
        "frac_positive" => round(frac_positive; digits=4),
        "geometry" => geometry,
        "n_valid_edges" => length(valid_kappas),
        "elapsed_s" => round(elapsed; digits=1),
        "per_edge_curvatures" => round.(valid_kappas; digits=6),
    )
end

# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────

function main()
    # Parse arguments
    threshold = 0.40  # default
    target_subject = nothing
    for arg in ARGS
        if startswith(arg, "--threshold")
            threshold = parse(Float64, split(arg, "=")[end])
        elseif startswith(arg, "--subject")
            target_subject = split(arg, "=")[end]
        end
    end

    pheno = CSV.read(PHENO_CSV, DataFrame)
    println("ABIDE-I Brain ORC — Exact LP (α=$ALPHA, threshold=$threshold)")
    println("η_c(N=200) = $(round(ETA_C_200; digits=3))")
    println("Threads: $(Threads.nthreads())")
    println("Subjects: $(nrow(pheno))")
    println("="^60)

    results = []
    for row in eachrow(pheno)
        fid = string(row.file_id)
        if target_subject !== nothing && fid != target_subject
            continue
        end
        result = process_subject(fid, threshold, row)
        if result !== nothing
            push!(results, result)
            # Save incrementally
            out_path = joinpath(RESULTS_DIR, "$(fid)_t$(Printf.@sprintf("%.2f", threshold))_orc.json")
            open(out_path, "w") do f
                JSON.print(f, result, 2)
            end
        end
    end

    # Summary
    println("\n" * "="^60)
    println("SUMMARY (threshold=$threshold)")

    for (dx, label) in [(1, "ASD"), (2, "Control")]
        group = filter(r -> r["dx_group"] == dx, results)
        if !isempty(group)
            etas = [r["eta"] for r in group]
            kappas = [r["kappa_mean"] for r in group]
            println("  $label (n=$(length(group))): η=$(round(mean(etas); digits=2)) ± $(round(std(etas); digits=2)), " *
                    "κ̄=$(round(mean(kappas); digits=4)) ± $(round(std(kappas); digits=4))")
        end
    end

    # Save combined results
    combined_path = joinpath(RESULTS_DIR, "abide_orc_combined_t$(Printf.@sprintf("%.2f", threshold)).json")
    open(combined_path, "w") do f
        JSON.print(f, results, 2)
    end
    println("\nResults saved to: $combined_path")
end

main()
