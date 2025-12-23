"""
OllivierRicci.jl - Ollivier-Ricci curvature computation

High-level Julia API for computing Ollivier-Ricci curvature.
Uses Rust backend for performance-critical Wasserstein-1 computation.
"""

using Graphs  # Replaces deprecated LightGraphs
using LinearAlgebra
using Statistics
using SparseArrays

# Import FFI functions - FFI is a submodule included in main module
# We'll access it via the parent module

"""
    compute_curvature(graph::SimpleGraph, u::Int, v::Int; alpha::Float64=0.5, weights::Union{Dict{Tuple{Int, Int}, Float64}, Nothing}=nothing)

Compute Ollivier-Ricci curvature for a single edge.

# Arguments
- `graph`: Input graph
- `u`, `v`: Edge endpoints
- `alpha`: Idleness parameter (default: 0.5)
- `weights`: Edge weights dictionary (optional)

# Returns
- Curvature value κ(u,v) ∈ [-1, 1]
"""
function compute_curvature(
    graph::SimpleGraph,
    u::Int,
    v::Int;
    alpha::Float64 = 0.5,
    weights::Union{Dict{Tuple{Int, Int}, Float64}, Nothing} = nothing
)::Float64
    # Check edge exists
    if !has_edge(graph, u, v)
        throw(ErrorException("Edge ($u, $v) does not exist"))
    end
    
    # Build probability measures
    mu_u = build_probability_measure(graph, u, alpha, weights)
    mu_v = build_probability_measure(graph, v, alpha, weights)
    
    # Compute Wasserstein-1 distance using Rust backend
    W1 = compute_wasserstein1_optimized(graph, mu_u, mu_v, weights)
    
    # Get edge distance
    d_uv = get_edge_weight(graph, u, v, weights)
    
    if d_uv > 0
        kappa = 1.0 - W1 / d_uv
    else
        kappa = 0.0
    end
    
    return kappa
end

"""
    compute_graph_curvature(graph::SimpleGraph; alpha::Float64=0.5, weights::Union{Dict{Tuple{Int, Int}, Float64}, Nothing}=nothing, parallel::Bool=true)

Compute curvature for all edges in graph.

# Arguments
- `graph`: Input graph
- `alpha`: Idleness parameter
- `weights`: Edge weights
- `parallel`: Use parallel processing (default: true)

# Returns
- Dictionary mapping (u, v) → κ(u, v)
"""
function compute_graph_curvature(
    graph::SimpleGraph;
    alpha::Float64 = 0.5,
    weights::Union{Dict{Tuple{Int, Int}, Float64}, Nothing} = nothing,
    parallel::Bool = true
)::Dict{Tuple{Int, Int}, Float64}
    edges_list = collect(edges(graph))

    if parallel && Threads.nthreads() > 1
        # Use multi-threading for parallel processing
        # Pre-allocate result arrays
        n_edges = length(edges_list)
        edge_pairs = Vector{Tuple{Int, Int}}(undef, n_edges)
        kappa_values = Vector{Float64}(undef, n_edges)

        Threads.@threads for i in 1:n_edges
            edge = edges_list[i]
            u, v = src(edge), dst(edge)
            edge_pairs[i] = (u, v)
            kappa_values[i] = compute_curvature(graph, u, v; alpha=alpha, weights=weights)
        end

        # Combine into dictionary
        curvatures = Dict{Tuple{Int, Int}, Float64}()
        for i in 1:n_edges
            curvatures[edge_pairs[i]] = kappa_values[i]
        end

        return curvatures
    else
        # Serial processing
        curvatures = Dict{Tuple{Int, Int}, Float64}()
        for edge in edges_list
            u, v = src(edge), dst(edge)
            curvatures[(u, v)] = compute_curvature(graph, u, v; alpha=alpha, weights=weights)
        end
        return curvatures
    end
end

"""
Build probability measure for node u.

μ_u = α·δ_u + (1-α)·Σ(w_uz / Σw_uz')·δ_z
"""
function build_probability_measure(
    graph::SimpleGraph,
    u::Int,
    alpha::Float64,
    weights::Union{Dict{Tuple{Int, Int}, Float64}, Nothing}
)::Dict{Int, Float64}
    mu = Dict{Int, Float64}()
    
    # Idleness component
    mu[u] = alpha
    
    # Neighbor component
    neighbors_u = neighbors(graph, u)
    if length(neighbors_u) > 0
        total_weight = 0.0
        neighbor_weights = Dict{Int, Float64}()
        
        for z in neighbors_u
            w_uz = get_edge_weight(graph, u, z, weights)
            neighbor_weights[z] = w_uz
            total_weight += w_uz
        end
        
        if total_weight > 0
            for (z, w_uz) in neighbor_weights
                mu[z] = get(mu, z, 0.0) + (1 - alpha) * w_uz / total_weight
            end
        end
    end
    
    return mu
end

"""
Get edge weight, defaulting to 1.0 if not specified.
"""
function get_edge_weight(
    graph::SimpleGraph,
    u::Int,
    v::Int,
    weights::Union{Dict{Tuple{Int, Int}, Float64}, Nothing}
)::Float64
    if has_edge(graph, u, v)
        if weights !== nothing && haskey(weights, (u, v))
            return weights[(u, v)]
        else
            return 1.0
        end
    else
        return 0.0
    end
end

"""
Optimized Wasserstein-1 computation using Rust backend.
"""
function compute_wasserstein1_optimized(
    graph::SimpleGraph,
    mu::Dict{Int, Float64},
    nu::Dict{Int, Float64},
    weights::Union{Dict{Tuple{Int, Int}, Float64}, Nothing}
)::Float64
    support_mu = collect(keys(mu))
    support_nu = collect(keys(nu))
    
    if length(support_mu) == 0 || length(support_nu) == 0
        return 0.0
    end
    
    # Get union of supports
    all_nodes = unique(vcat(support_mu, support_nu))
    n = length(all_nodes)
    
    if n == 0
        return 0.0
    end
    
    # Create node index mapping
    node_to_idx = Dict(node => i for (i, node) in enumerate(all_nodes))
    
    # Build probability vectors
    mu_vec = zeros(Float64, n)
    nu_vec = zeros(Float64, n)
    
    for (node, prob) in mu
        if haskey(node_to_idx, node)
            mu_vec[node_to_idx[node]] = prob
        end
    end
    
    for (node, prob) in nu
        if haskey(node_to_idx, node)
            nu_vec[node_to_idx[node]] = prob
        end
    end
    
    # Build cost matrix (shortest path distances)
    cost_matrix = zeros(Float64, n * n)
    for i in 1:n
        for j in 1:n
            u = all_nodes[i]
            v = all_nodes[j]
            cost_matrix[(i-1)*n + j] = shortest_path_distance(graph, u, v, weights)
        end
    end
    
    # Call Rust backend (or Julia fallback)
    # FFI functions are available in parent scope after include
    # Use fully qualified name or direct call
    return FFI.wasserstein1_rust(mu_vec, nu_vec, cost_matrix, 0.01, 100)
end

"""
Compute shortest path distance between nodes.
"""
function shortest_path_distance(
    graph::SimpleGraph,
    u::Int,
    v::Int,
    weights::Union{Dict{Tuple{Int, Int}, Float64}, Nothing}
)::Float64
    if u == v
        return 0.0
    end

    if weights === nothing
        # BFS for unweighted graphs
        try
            path = a_star(graph, u, v)
            return Float64(length(path) - 1)
        catch
            return Inf
        end
    else
        # Dijkstra for weighted graphs
        return dijkstra_distance(graph, u, v, weights)
    end
end

"""
Dijkstra's algorithm for weighted shortest path.

# Arguments
- `graph`: Input graph
- `source`: Source node
- `target`: Target node
- `weights`: Edge weights dictionary

# Returns
- Shortest path distance from source to target
"""
function dijkstra_distance(
    graph::SimpleGraph,
    source::Int,
    target::Int,
    weights::Dict{Tuple{Int, Int}, Float64}
)::Float64
    n = nv(graph)
    dist = fill(Inf, n)
    visited = falses(n)
    dist[source] = 0.0

    # Priority queue: (distance, node)
    pq = [(0.0, source)]

    while !isempty(pq)
        # Get node with minimum distance
        sort!(pq, by=x->x[1])
        (d, u) = popfirst!(pq)

        if visited[u]
            continue
        end

        visited[u] = true

        # Early termination if target reached
        if u == target
            return d
        end

        # Relax edges
        for v in neighbors(graph, u)
            if !visited[v]
                # Get edge weight
                w = get(weights, (u, v), get(weights, (v, u), 1.0))
                alt = dist[u] + w

                if alt < dist[v]
                    dist[v] = alt
                    push!(pq, (alt, v))
                end
            end
        end
    end

    return dist[target]
end
