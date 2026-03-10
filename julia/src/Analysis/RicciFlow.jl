"""
RicciFlow.jl - Normalized Discrete Ollivier-Ricci Flow

Implements the discrete Ricci flow from Ni, Lin, Luo, Gao (2019):
    w_e(t+1) = w_e(t) * (1 - dt * kappa_e(t))

with total weight normalization (Bai, Lin, Lu 2021) to prevent collapse.

Positive curvature edges shrink (contract), negative edges stretch.
The flow drives all curvatures toward uniformity.
"""

using Graphs
using Statistics
using Printf

"""
    weighted_orc_edge(g, u, v, weights, dist_cache; alpha=0.5)

Compute Ollivier-Ricci curvature for edge (u,v) using edge weights as distances.
Uses the Sinkhorn-like approach with the given weight dictionary.

The measure at u is: mu_u = alpha * delta_u + (1-alpha) * Uniform(N(u))
Distance d(u,v) = weights[(min(u,v), max(u,v))].
"""
function weighted_orc_edge(g::SimpleGraph, u::Int, v::Int,
                           weights::Dict{Tuple{Int,Int}, Float64},
                           all_dists::Matrix{Float64};
                           alpha::Float64=0.5)::Float64
    # Build measures
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

    # Support nodes
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

    # Cost matrix from precomputed weighted shortest paths
    C = zeros(n, n)
    for i in 1:n
        for j in 1:n
            C[i, j] = all_dists[support[i], support[j]]
        end
    end

    # Sinkhorn W1 approximation (fast, epsilon=0.1)
    W1 = sinkhorn_w1(mu_vec, nu_vec, C; epsilon=0.1, max_iter=200)

    d_uv = all_dists[u, v]
    if d_uv < 1e-10
        return 0.0
    end
    return 1.0 - W1 / d_uv
end

"""
    sinkhorn_w1(mu, nu, C; epsilon=0.1, max_iter=200)

Compute Wasserstein-1 distance via entropy-regularized Sinkhorn.
"""
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

    # Transport plan
    gamma = diagm(u) * K * diagm(v)
    return sum(C .* gamma)
end

"""
    weighted_shortest_paths(g, weights)

Compute all-pairs shortest paths using Dijkstra with edge weights.
Returns N x N distance matrix.
"""
function weighted_shortest_paths(g::SimpleGraph,
                                  weights::Dict{Tuple{Int,Int}, Float64})::Matrix{Float64}
    N = nv(g)
    dists = fill(Inf, N, N)

    for v in 1:N
        dists[v, v] = 0.0
    end

    # Dijkstra from each vertex
    for src_node in 1:N
        # Simple Dijkstra
        visited = falses(N)
        dists[src_node, src_node] = 0.0
        pq = [(0.0, src_node)]  # (distance, node)

        while !isempty(pq)
            sort!(pq, by=first)
            d_curr, u = popfirst!(pq)

            if visited[u]
                continue
            end
            visited[u] = true

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

using LinearAlgebra: diagm

"""
    RicciFlowResult

Result of running discrete Ricci flow.
"""
struct RicciFlowResult
    trajectory::Vector{Dict{String, Any}}
    converged::Bool
    iterations::Int
    final_weights::Dict{Tuple{Int,Int}, Float64}
    final_kappas::Dict{Tuple{Int,Int}, Float64}
end

"""
    ricci_flow(g; dt=0.5, alpha=0.5, max_iterations=100, delta=1e-4)

Run normalized discrete Ollivier-Ricci flow on graph g.

The flow evolves edge weights according to:
    w_e(t+1) = w_e(t) * (1 - dt * kappa_e(t))
with total weight normalization after each step.

Returns RicciFlowResult with full trajectory.
"""
function ricci_flow(
    g::SimpleGraph;
    dt::Float64 = 0.5,
    alpha::Float64 = 0.5,
    max_iterations::Int = 100,
    delta::Float64 = 1e-4,
    verbose::Bool = true
)
    N = nv(g)
    E = ne(g)
    edges_list = collect(edges(g))

    # Initialize all edge weights to 1.0
    weights = Dict{Tuple{Int,Int}, Float64}()
    for e in edges_list
        weights[minmax(src(e), dst(e))] = 1.0
    end

    trajectory = Vector{Dict{String, Any}}()
    converged = false

    for t in 0:max_iterations
        # Compute weighted shortest paths
        all_dists = weighted_shortest_paths(g, weights)

        # Compute ORC for all edges (Sinkhorn)
        kappas = Dict{Tuple{Int,Int}, Float64}()
        kappa_values = Float64[]

        for e in edges_list
            u, v = src(e), dst(e)
            k = weighted_orc_edge(g, u, v, weights, all_dists; alpha=alpha)
            kappas[minmax(u, v)] = k
            push!(kappa_values, k)
        end

        # Compute observables
        kappa_mean = mean(kappa_values)
        kappa_std = std(kappa_values)
        kappa_range = maximum(kappa_values) - minimum(kappa_values)

        # Clustering coefficient
        C = Graphs.global_clustering_coefficient(g)

        # Edge weight statistics
        w_values = collect(values(weights))
        w_sorted = sort(w_values)
        w_gini = gini_coefficient(w_sorted)
        w_spread = maximum(w_values) / max(minimum(w_values), 1e-30)

        record = Dict{String, Any}(
            "t" => t,
            "kappa_mean" => kappa_mean,
            "kappa_std" => kappa_std,
            "kappa_range" => kappa_range,
            "kappa_min" => minimum(kappa_values),
            "kappa_max" => maximum(kappa_values),
            "clustering" => C,
            "w_gini" => w_gini,
            "w_spread" => w_spread,
            "w_mean" => mean(w_values),
            "w_std" => std(w_values),
        )
        push!(trajectory, record)

        if verbose
            @printf("  t=%3d: κ̄=%+.6f  σ_κ=%.4f  range=%.4f  C=%.4f  Gini=%.4f  w_spread=%.1f\n",
                    t, kappa_mean, kappa_std, kappa_range, C, w_gini, w_spread)
        end

        # Check convergence (skip iteration 0)
        if t > 0 && kappa_range < delta
            converged = true
            if verbose
                println("  CONVERGED at t=$t (range=$kappa_range < delta=$delta)")
            end
            break
        end

        # Don't update on last iteration
        if t == max_iterations
            break
        end

        # Update edge weights: w_e *= (1 - dt * kappa_e)
        for (key, kappa) in kappas
            weights[key] *= (1.0 - dt * kappa)
            weights[key] = max(weights[key], 1e-10)  # prevent zero/negative weights
        end

        # Normalize: preserve total weight = E (original total)
        total = sum(values(weights))
        scale = Float64(E) / total
        for key in keys(weights)
            weights[key] *= scale
        end
    end

    return RicciFlowResult(trajectory, converged, length(trajectory) - 1,
                           weights, Dict{Tuple{Int,Int}, Float64}())
end

"""
    gini_coefficient(sorted_values)

Compute Gini coefficient from a sorted array of non-negative values.
0 = perfect equality, 1 = perfect inequality.
"""
function gini_coefficient(sorted_values::Vector{Float64})::Float64
    n = length(sorted_values)
    if n == 0 || sum(sorted_values) == 0
        return 0.0
    end
    numerator = sum((2i - n - 1) * sorted_values[i] for i in 1:n)
    denominator = n * sum(sorted_values)
    return numerator / denominator
end
