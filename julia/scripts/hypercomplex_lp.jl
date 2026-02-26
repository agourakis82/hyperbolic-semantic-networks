"""
HYPERCOMPLEX LANDMARK EMBEDDING — Exact ORC via LP

Computes Ollivier-Ricci curvature on k-regular random graphs where the
transport cost is the geodesic distance on a hypercomplex unit sphere
S^(d-1), obtained by landmark embedding of graph nodes.

The probability measures µ_u, µ_v are GRAPH-BASED (idleness α=0.5 on
original graph edges). Only the transport cost matrix changes.

Key question: Does η_c depend on the ambient embedding dimension d?

Usage:
    julia hypercomplex_lp.jl                 # N=100, d=4 (quick test)
    julia hypercomplex_lp.jl --full          # N∈{50,100,200}, d∈{4,8}
    julia hypercomplex_lp.jl --N 50 --d 4   # Single (N,d) pair

Scientific background:
    Experiment 05 (Sounio, ε=0.5) found sign changes in mean κ̄ for
    hop/Q4/Oct/Sed embeddings, but the Sinkhorn bias (ε=0.5) prevents
    quantitative η_c comparison. This script uses exact LP (ε→0).
"""

import Pkg
let deps = Pkg.project().dependencies
    for pkg in ["JuMP", "HiGHS", "Graphs", "JSON", "LinearAlgebra"]
        if !haskey(deps, pkg)
            Pkg.add(pkg)
        end
    end
end

using JuMP, HiGHS, Graphs, Statistics, Random, JSON, Printf, LinearAlgebra

# ──────────────────────────────────────────────────────────────────────────────
# Core LP: Exact Wasserstein-1 (same as exact_curvature_lp.jl)
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
# BFS all-pairs distance matrix
# ──────────────────────────────────────────────────────────────────────────────

function bfs_all_pairs(g::SimpleGraph)::Matrix{Int}
    N = nv(g)
    D = zeros(Int, N, N)
    for u in 1:N
        dists = gdistances(g, u)
        D[u, :] = dists
    end
    return D
end

# ──────────────────────────────────────────────────────────────────────────────
# Landmark embedding: nodes → S^(d-1)
# ──────────────────────────────────────────────────────────────────────────────

"""
    select_landmarks(D_hop, n_lm; rng) -> Vector{Int}

Greedy farthest-first landmark selection.
Starts from a random node and iteratively picks the node farthest from the
current landmark set (by minimum distance to any landmark).
"""
function select_landmarks(D_hop::Matrix{Int}, n_lm::Int;
                          rng::AbstractRNG=Random.default_rng())::Vector{Int}
    N = size(D_hop, 1)
    n_lm = min(n_lm, N)
    landmarks = [rand(rng, 1:N)]
    min_dists = vec(D_hop[landmarks[1], :])

    for _ in 2:n_lm
        next = argmax(min_dists)
        push!(landmarks, next)
        new_dists = vec(D_hop[next, :])
        min_dists = min.(min_dists, new_dists)
    end
    return landmarks
end

"""
    landmark_embed(D_hop, landmarks) -> Matrix{Float64}

Embed all N nodes onto S^(d-1) where d = length(landmarks).

x[i, :] = dist_to_landmarks[i, :] / norm(dist_to_landmarks[i, :])

If a node has zero distance to all landmarks (isolated), use uniform vector.
"""
function landmark_embed(D_hop::Matrix{Int}, landmarks::Vector{Int})::Matrix{Float64}
    N = size(D_hop, 1)
    d = length(landmarks)
    X = Matrix{Float64}(undef, N, d)
    for i in 1:N
        v = Float64[D_hop[i, l] for l in landmarks]
        n = norm(v)
        if n < 1e-10
            @warn "Node $i has zero distance to all landmarks; using uniform embedding"
            X[i, :] = fill(1.0 / sqrt(d), d)
        else
            X[i, :] = v / n
        end
    end
    return X
end

"""
    geodesic_cost(X) -> Matrix{Float64}

Pairwise geodesic distances on S^(d-1):
    dist(i,j) = acos(clamp(X[i,:]⋅X[j,:], -1, 1))

Values are in [0, π].
"""
function geodesic_cost(X::Matrix{Float64})::Matrix{Float64}
    N = size(X, 1)
    C = Matrix{Float64}(undef, N, N)
    for i in 1:N, j in 1:N
        C[i, j] = acos(clamp(dot(X[i, :], X[j, :]), -1.0, 1.0))
    end
    return C
end

# ──────────────────────────────────────────────────────────────────────────────
# Graph-based probability measure (idleness α on original graph)
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
# Edge curvature with hypercomplex cost matrix
# ──────────────────────────────────────────────────────────────────────────────

"""
    hypercomplex_edge_curvature(g, u, v, X, C_geo; alpha) -> Float64

Compute ORC for edge (u,v) where:
- µ_u, µ_v are graph-based random walk measures (idleness α)
- C_geo is the geodesic cost matrix on S^(d-1)
- The edge "distance" d(u,v) is the geodesic distance C_geo[u,v]

Returns NaN if d(u,v) ≈ 0 (nodes mapped to same point on sphere).
"""
function hypercomplex_edge_curvature(g::SimpleGraph, u::Int, v::Int,
                                     X::Matrix{Float64}, C_geo::Matrix{Float64};
                                     alpha::Float64=0.5)::Float64
    d_uv = C_geo[u, v]
    if d_uv < 1e-6
        return NaN  # degenerate (identical embeddings up to FP error); skip
    end

    mu_u = build_prob_measure(g, u, alpha)
    mu_v = build_prob_measure(g, v, alpha)

    all_nodes = sort(unique(vcat(collect(keys(mu_u)), collect(keys(mu_v)))))
    n = length(all_nodes)
    idx = Dict(node => i for (i, node) in enumerate(all_nodes))

    mu_vec = [get(mu_u, all_nodes[i], 0.0) for i in 1:n]
    nu_vec = [get(mu_v, all_nodes[i], 0.0) for i in 1:n]

    # Local cost submatrix using geodesic distances
    C_local = [C_geo[all_nodes[i], all_nodes[j]] for i in 1:n, j in 1:n]

    W1 = exact_wasserstein1(mu_vec, nu_vec, C_local)
    return 1.0 - W1 / d_uv
end

# ──────────────────────────────────────────────────────────────────────────────
# Full sweep for one (N, d, k, seed)
# ──────────────────────────────────────────────────────────────────────────────

function sweep_single(N::Int, d::Int, k::Int, seed::Int; alpha::Float64=0.5)
    rng = MersenneTwister(seed)
    g = random_regular_graph(N, k; rng=rng)

    D_hop = bfs_all_pairs(g)
    landmarks = select_landmarks(D_hop, d; rng=rng)
    X = landmark_embed(D_hop, landmarks)
    C_geo = geodesic_cost(X)

    kappas = Float64[]
    for e in edges(g)
        κ = hypercomplex_edge_curvature(g, src(e), dst(e), X, C_geo; alpha=alpha)
        isnan(κ) || push!(kappas, κ)
    end

    isempty(kappas) && return NaN
    return mean(kappas)
end

# ──────────────────────────────────────────────────────────────────────────────
# Multi-seed sweep for one (N, d, k)
# ──────────────────────────────────────────────────────────────────────────────

function sweep_k(N::Int, d::Int, k::Int, seeds::Vector{Int}; alpha::Float64=0.5)
    kappa_means = Float64[]
    for s in seeds
        κ̄ = sweep_single(N, d, k, s; alpha=alpha)
        isnan(κ̄) || push!(kappa_means, κ̄)
    end
    isempty(kappa_means) && return (kappa_mean=NaN, kappa_std=NaN, n_seeds=0)
    return (kappa_mean=mean(kappa_means), kappa_std=std(kappa_means), n_seeds=length(kappa_means))
end

# ──────────────────────────────────────────────────────────────────────────────
# Main sweep for (N, d)
# ──────────────────────────────────────────────────────────────────────────────

# k values matching Table 5 for each N
const K_VALUES = Dict(
    50  => [2, 4, 6, 8, 10, 12, 14, 16],
    100 => [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 25, 30],
    200 => [4, 8, 12, 16, 20, 25, 30, 35, 40],
)

function run_sweep(N::Int, d::Int; seeds::Vector{Int}=[42,137,271,314,577],
                   alpha::Float64=0.5, verbose::Bool=true)
    k_values = get(K_VALUES, N, [4, 6, 8, 10, 12, 14, 16, 18, 20])
    embedding_name = d == 4 ? "Q4 (S³)" : d == 8 ? "Oct (S⁷)" : d == 16 ? "Sed (S¹⁵)" : "d=$d"
    verbose && println("\n── N=$N, d=$d ($embedding_name), $(length(seeds)) seeds ──")

    results = []
    for k in k_values
        # Skip invalid (k,N) combinations
        k >= N && continue
        isodd(k) && isodd(N) && continue

        eta = k^2 / N
        t0 = time()
        r = sweep_k(N, d, k, seeds; alpha=alpha)
        elapsed = time() - t0

        push!(results, Dict(
            "k" => k,
            "eta" => round(eta, digits=4),
            "kappa_mean" => isnan(r.kappa_mean) ? nothing : round(r.kappa_mean, digits=6),
            "kappa_std"  => isnan(r.kappa_std)  ? nothing : round(r.kappa_std,  digits=6),
            "n_seeds"    => r.n_seeds,
        ))
        verbose && @printf("  k=%2d  η=%.2f  κ̄=%+.4f  σ=%.4f  (%.1fs)\n",
                           k, eta, r.kappa_mean, r.kappa_std, elapsed)
    end

    return Dict(
        "N" => N, "d" => d, "alpha" => alpha,
        "embedding" => embedding_name,
        "seeds" => seeds,
        "results" => results,
    )
end

# ──────────────────────────────────────────────────────────────────────────────
# Interpolate η_c from results (first sign change)
# ──────────────────────────────────────────────────────────────────────────────

function interpolate_eta_c(results::Vector)
    for i in 2:length(results)
        prev, curr = results[i-1], results[i]
        κ_prev = prev["kappa_mean"]
        κ_curr = curr["kappa_mean"]
        (isnothing(κ_prev) || isnothing(κ_curr)) && continue
        if κ_prev < 0 && κ_curr >= 0
            # Linear interpolation
            η_prev, η_curr = prev["eta"], curr["eta"]
            frac = abs(κ_prev) / (abs(κ_prev) + abs(κ_curr))
            return η_prev + frac * (η_curr - η_prev)
        end
    end
    return NaN  # no sign change found
end

# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

function main()
    args = ARGS
    full_sweep = "--full" in args

    if full_sweep
        N_values = [50, 100, 200]
        d_values = [4, 8]
        seeds = [42, 137, 271, 314, 577]
    else
        # Parse --N and --d flags, with defaults
        N = 100
        d = 4
        for i in 1:length(args)-1
            args[i] == "--N" && (N = parse(Int, args[i+1]))
            args[i] == "--d" && (d = parse(Int, args[i+1]))
        end
        N_values = [N]
        d_values = [d]
        seeds = [42, 137, 271]  # 3 seeds for quick test
    end

    mkpath("results/experiments")
    all_data = Dict[]

    for N in N_values, d in d_values
        data = run_sweep(N, d; seeds=seeds, verbose=true)
        push!(all_data, data)

        # Save per-(N,d) file
        outfile = "results/experiments/hypercomplex_lp_n$(N)_d$(d).json"
        open(outfile, "w") do f
            JSON.print(f, data, 2)
        end
        println("Saved → $outfile")

        # Print η_c estimate
        η_c = interpolate_eta_c(data["results"])
        @printf("  → η_c ≈ %.3f (N=%d, d=%d)\n", η_c, N, d)
    end

    # Summary table
    println("\n── Dimensional phase boundary summary ──")
    println("  N     d   embedding    η_c")
    for data in all_data
        η_c = interpolate_eta_c(data["results"])
        @printf("  %-4d  %-3d  %-11s  %.3f\n",
                data["N"], data["d"], data["embedding"], η_c)
    end

    # Hop-count reference values from manuscript Table 5
    println("\n  Hop-count reference (exact LP, Table 5):")
    println("  N= 50: η_c ≈ 1.73  |  N=100: η_c ≈ 2.22  |  N=200: η_c ≈ 2.71")
end

main()
