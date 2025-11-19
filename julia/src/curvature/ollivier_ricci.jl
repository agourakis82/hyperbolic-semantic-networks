"""
Ollivier-Ricci Curvature Computation

Implementation of Ollivier-Ricci curvature for semantic networks.
This is a Julia port of the Python GraphRicciCurvature library.

Author: Dr. Demetrios Agourakis
Date: 2025-11-08
"""

module OllivierRicci

using LightGraphs
using LinearAlgebra
using SparseArrays
using Statistics
using Random

export compute_edge_curvature, compute_graph_curvature, build_probability_measure

"""
Compute Ollivier-Ricci curvature for an edge (u, v).

κ(u,v) = 1 - W₁(μ_u, μ_v) / d(u,v)

where:
- μ_u = α·δ_u + (1-α)·Σ(w_uz / Σw_uz')·δ_z
- W₁ is Wasserstein-1 distance (optimal transport)
- α is idleness parameter (default 0.5)
- d(u,v) is the edge distance/weight

# Arguments
- `G`: Graph (LightGraphs.AbstractGraph)
- `u`: Source node
- `v`: Target node
- `α`: Idleness parameter (default 0.5)
- `weights`: Edge weights dictionary (default: uniform weights)

# Returns
- Curvature value κ(u,v)
"""
function compute_edge_curvature(
    G::AbstractGraph,
    u::Int,
    v::Int;
    α::Float64 = 0.5,
    weights::Dict{Tuple{Int,Int},Float64} = Dict()
)::Float64
    # 1. Build probability measures μ_u, μ_v
    μ_u = build_probability_measure(G, u, α, weights)
    μ_v = build_probability_measure(G, v, α, weights)
    
    # 2. Compute Wasserstein-1 distance
    W1 = wasserstein1_distance(G, μ_u, μ_v, weights)
    
    # 3. Edge distance
    d_uv = get_edge_weight(G, u, v, weights)
    
    # 4. Curvature
    if d_uv > 0
        κ = 1.0 - W1 / d_uv
    else
        κ = 0.0  # Edge doesn't exist or zero weight
    end
    
    return κ
end

"""
Build probability measure for node u.

μ_u = α·δ_u + (1-α)·Σ(w_uz / Σw_uz')·δ_z

where:
- δ_u is Dirac delta at u
- w_uz is weight of edge (u, z)
- α is idleness parameter
"""
function build_probability_measure(
    G::AbstractGraph,
    u::Int,
    α::Float64,
    weights::Dict{Tuple{Int,Int},Float64}
)::Dict{Int,Float64}
    μ = Dict{Int,Float64}()
    
    # Idleness component
    μ[u] = α
    
    # Neighbor component
    neighbors_u = neighbors(G, u)
    if length(neighbors_u) > 0
        # Compute total weight
        total_weight = 0.0
        for z in neighbors_u
            total_weight += get_edge_weight(G, u, z, weights)
        end
        
        if total_weight > 0
            for z in neighbors_u
                w_uz = get_edge_weight(G, u, z, weights)
                μ[z] = get(μ, z, 0.0) + (1 - α) * w_uz / total_weight
            end
        end
    end
    
    return μ
end

"""
Get edge weight, defaulting to 1.0 if not specified.
"""
function get_edge_weight(
    G::AbstractGraph,
    u::Int,
    v::Int,
    weights::Dict{Tuple{Int,Int},Float64}
)::Float64
    if has_edge(G, u, v)
        return get(weights, (u, v), 1.0)
    else
        return 0.0
    end
end

"""
Compute Wasserstein-1 distance using Sinkhorn algorithm.

This is a simplified implementation. For production, consider:
- More efficient Sinkhorn iterations
- Entropy regularization tuning
- Convergence criteria
"""
function wasserstein1_distance(
    G::AbstractGraph,
    μ::Dict{Int,Float64},
    ν::Dict{Int,Float64},
    weights::Dict{Tuple{Int,Int},Float64};
    ε::Float64 = 0.01,
    max_iter::Int = 100
)::Float64
    # Get support of measures
    support_μ = collect(keys(μ))
    support_ν = collect(keys(ν))
    
    # Build cost matrix (shortest path distances)
    n = length(support_μ)
    m = length(support_ν)
    
    if n == 0 || m == 0
        return 0.0
    end
    
    # Cost matrix: shortest path distances
    C = zeros(n, m)
    for i in 1:n
        for j in 1:m
            u = support_μ[i]
            v = support_ν[j]
            C[i, j] = shortest_path_distance(G, u, v, weights)
        end
    end
    
    # Sinkhorn algorithm (simplified)
    # For full implementation, see: https://github.com/jeanfeydy/geomloss
    # Here we use a simple approximation
    μ_vec = [get(μ, u, 0.0) for u in support_μ]
    ν_vec = [get(ν, v, 0.0) for v in support_ν]
    
    # Normalize
    μ_vec = μ_vec / sum(μ_vec)
    ν_vec = ν_vec / sum(ν_vec)
    
    # Simple transport: greedy assignment
    # TODO: Implement proper Sinkhorn
    W1 = 0.0
    μ_remaining = copy(μ_vec)
    ν_remaining = copy(ν_vec)
    
    # Greedy matching (simplified - should use proper OT)
    for _ in 1:min(n, m)
        # Find minimum cost
        min_cost = Inf
        min_i, min_j = 0, 0
        for i in 1:n
            for j in 1:m
                if μ_remaining[i] > 0 && ν_remaining[j] > 0
                    cost = C[i, j]
                    if cost < min_cost
                        min_cost = cost
                        min_i, min_j = i, j
                    end
                end
            end
        end
        
        if min_i > 0 && min_j > 0
            transport = min(μ_remaining[min_i], ν_remaining[min_j])
            W1 += transport * C[min_i, min_j]
            μ_remaining[min_i] -= transport
            ν_remaining[min_j] -= transport
        else
            break
        end
    end
    
    return W1
end

"""
Compute shortest path distance between nodes u and v.
"""
function shortest_path_distance(
    G::AbstractGraph,
    u::Int,
    v::Int,
    weights::Dict{Tuple{Int,Int},Float64}
)::Float64
    if u == v
        return 0.0
    end
    
    # Use Dijkstra's algorithm (LightGraphs)
    try
        dist = dijkstra_shortest_paths(G, u, weights)
        return dist.dists[v]
    catch
        # Fallback: BFS if no weights
        return length(a_star(G, u, v)) - 1
    end
end

"""
Compute curvature for all edges in graph.

# Returns
- Dictionary mapping (u, v) → κ(u, v)
"""
function compute_graph_curvature(
    G::AbstractGraph;
    α::Float64 = 0.5,
    weights::Dict{Tuple{Int,Int},Float64} = Dict()
)::Dict{Tuple{Int,Int},Float64}
    curvatures = Dict{Tuple{Int,Int},Float64}()
    
    for edge in edges(G)
        u, v = src(edge), dst(edge)
        κ = compute_edge_curvature(G, u, v; α=α, weights=weights)
        curvatures[(u, v)] = κ
    end
    
    return curvatures
end

"""
Compute mean curvature for graph.
"""
function mean_curvature(
    curvatures::Dict{Tuple{Int,Int},Float64}
)::Float64
    if length(curvatures) == 0
        return 0.0
    end
    return mean(collect(values(curvatures)))
end

"""
Compute curvature statistics.
"""
function curvature_stats(
    curvatures::Dict{Tuple{Int,Int},Float64}
)::Dict{String,Float64}
    κ_values = collect(values(curvatures))
    
    return Dict(
        "mean" => mean(κ_values),
        "median" => median(κ_values),
        "std" => std(κ_values),
        "min" => minimum(κ_values),
        "max" => maximum(κ_values)
    )
end

end # module OllivierRicci

