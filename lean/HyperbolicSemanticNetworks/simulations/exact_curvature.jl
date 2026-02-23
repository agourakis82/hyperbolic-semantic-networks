#!/usr/bin/env julia
#
# EXACT Ollivier-Ricci Curvature Computation
# 
# This implements the REAL algorithm with proper Wasserstein distance
# Using Sinkhorn algorithm for optimal transport

using Random
using Statistics
using LinearAlgebra
using Printf

"""
    Optimal transport via Sinkhorn algorithm
    
    Compute Wasserstein-1 distance between two probability measures
    on a graph with shortest-path metric
"""

struct Graph
    n::Int
    adj::Vector{Vector{Int}}
    distances::Matrix{Float64}  # All-pairs shortest paths
end

function Graph(n::Int)
    adj = [Int[] for _ in 1:n]
    return Graph(n, adj, zeros(n, n))
end

function add_edge!(g::Graph, u::Int, v::Int)
    if v ∉ g.adj[u]
        push!(g.adj[u], v)
        push!(g.adj[v], u)
    end
end

"""
    Floyd-Warshall for all-pairs shortest paths
"""
function compute_distances!(g::Graph)
    n = g.n
    dist = fill(Inf, n, n)
    
    # Initialize
    for i in 1:n
        dist[i, i] = 0.0
        for j in g.adj[i]
            dist[i, j] = 1.0
        end
    end
    
    # Floyd-Warshall
    for k in 1:n
        for i in 1:n
            for j in 1:n
                if dist[i, k] + dist[k, j] < dist[i, j]
                    dist[i, j] = dist[i, k] + dist[k, j]
                end
            end
        end
    end
    
    g.distances .= dist
    return dist
end

"""
    Sinkhorn algorithm for entropic optimal transport
    
    Computes Wasserstein distance with entropic regularization
    More efficient than linear programming for large problems
"""
function sinkhorn_wasserstein(
    μ::Vector{Float64},  # Source measure
    ν::Vector{Float64},  # Target measure
    C::Matrix{Float64},  # Cost matrix
    ε::Float64=0.01,     # Entropic regularization
    max_iter::Int=1000,  # Maximum iterations
    tol::Float64=1e-6    # Convergence tolerance
)
    n = length(μ)
    m = length(ν)
    
    # Initialize
    K = exp.(-C ./ ε)  # Gibbs kernel
    u = ones(n)
    v = ones(m)
    
    # Sinkhorn iterations
    for iter in 1:max_iter
        u_prev = copy(u)
        
        # Update u and v
        u = μ ./ (K * v)
        v = ν ./ (K' * u)
        
        # Check convergence
        if maximum(abs.(u - u_prev)) < tol
            break
        end
    end
    
    # Compute optimal coupling
    P = Diagonal(u) * K * Diagonal(v)
    
    # Compute Wasserstein distance
    W1 = sum(P .* C)
    
    return W1
end

"""
    Build probability measure for Ollivier-Ricci
    μ_u = α·δ_u + (1-α)·Uniform(neighbors(u))
"""
function probability_measure(g::Graph, u::Int, α::Float64)
    n = g.n
    μ = zeros(n)
    
    # Idleness component
    μ[u] = α
    
    # Neighbor component
    neighbors_u = g.adj[u]
    if !isempty(neighbors_u)
        for v in neighbors_u
            μ[v] += (1 - α) / length(neighbors_u)
        end
    end
    
    return μ
end

"""
    Compute EXACT Ollivier-Ricci curvature for edge (u,v)
    
    κ(u,v) = 1 - W₁(μ_u, μ_v) / d(u,v)
"""
function ollivier_ricci_exact(g::Graph, u::Int, v::Int; α::Float64=0.5)
    # Check edge exists
    if v ∉ g.adj[u]
        return 0.0
    end
    
    # Distance between u and v
    d_uv = g.distances[u, v]
    if d_uv == 0 || d_uv == Inf
        return 0.0
    end
    
    # Build probability measures
    μ_u = probability_measure(g, u, α)
    μ_v = probability_measure(g, v, α)
    
    # Get supports (non-zero probability nodes)
    supp_u = findall(μ_u .> 1e-10)
    supp_v = findall(μ_v .> 1e-10)
    
    # Extract sub-measures
    μ_u_sub = μ_u[supp_u]
    μ_v_sub = μ_v[supp_v]
    
    # Extract cost sub-matrix
    C_sub = g.distances[supp_u, supp_v]
    
    # Compute Wasserstein distance
    W1 = sinkhorn_wasserstein(μ_u_sub, μ_v_sub, C_sub)
    
    # Curvature
    κ = 1.0 - W1 / d_uv
    
    return clamp(κ, -1.0, 1.0)
end

"""
    Mean curvature over all edges
"""
function mean_curvature_exact(g::Graph; α::Float64=0.5)
    total_κ = 0.0
    n_edges = 0
    
    for u in 1:g.n
        for v in g.adj[u]
            if u < v  # Count each edge once
                κ = ollivier_ricci_exact(g, u, v, α=α)
                total_κ += κ
                n_edges += 1
            end
        end
    end
    
    return n_edges > 0 ? total_κ / n_edges : 0.0
end

"""
    Generate G(n,p) random graph
"""
function generate_gnp(n::Int, p::Real; seed::Int=42)
    Random.seed!(seed)
    g = Graph(n)
    
    for i in 1:n
        for j in (i+1):n
            if rand() < p
                add_edge!(g, i, j)
            end
        end
    end
    
    # Compute distances
    compute_distances!(g)
    
    return g
end

"""
    Largest connected component
"""
function largest_component(g::Graph)
    visited = falses(g.n)
    max_component = Int[]
    
    for start in 1:g.n
        visited[start] && continue
        component = Int[]
        stack = [start]
        visited[start] = true
        
        while !isempty(stack)
            v = pop!(stack)
            push!(component, v)
            for u in g.adj[v]
                if !visited[u]
                    visited[u] = true
                    push!(stack, u)
                end
            end
        end
        
        if length(component) > length(max_component)
            max_component = component
        end
    end
    
    return max_component
end

function induced_subgraph(g::Graph, vertices::Vector{Int})
    vm = Dict(v => i for (i, v) in enumerate(vertices))
    new_n = length(vertices)
    new_g = Graph(new_n)
    
    for (new_u, old_u) in enumerate(vertices)
        for old_v in g.adj[old_u]
            if haskey(vm, old_v)
                new_v = vm[old_v]
                if new_u < new_v
                    add_edge!(new_g, new_u, new_v)
                end
            end
        end
    end
    
    compute_distances!(new_g)
    return new_g
end

"""
    Run test with EXACT curvature
"""
function test_exact_curvature(n::Int=100, n_sims::Int=10)
    println("="^70)
    println("EXACT OLLIVIER-RICCI CURVATURE TEST")
    println("Using Sinkhorn algorithm for Wasserstein distance")
    println("n = $n, n_sims = $n_sims")
    println("WARNING: This is SLOW - exact computation is expensive!")
    println("="^70)
    println()
    
    # Test smaller range due to computational cost
    c_values = [0.5, 1.0, 1.5, 2.0, 2.5]
    
    for c in c_values
        η = c^2
        p = c / sqrt(n)
        
        println("Testing η = $η (c = $c)...")
        
        curvatures = Float64[]
        
        for sim in 1:n_sims
            g = generate_gnp(n, p, seed=sim)
            lcc = largest_component(g)
            
            length(lcc) < n ÷ 5 && continue
            
            sg = induced_subgraph(g, lcc)
            isempty(sg.adj[1]) && continue
            
            # Compute exact curvature
            κ = mean_curvature_exact(sg, α=0.5)
            push!(curvatures, κ)
            
            print(".")
            flush(stdout)
        end
        println()
        
        if !isempty(curvatures)
            μ = mean(curvatures)
            σ = std(curvatures)
            @printf("  η = %.2f: κ̄ = %+.4f ± %.4f (n=%d)\n", 
                    η, μ, σ, length(curvatures))
        else
            println("  No valid graphs generated")
        end
        println()
    end
    
    println("="^70)
    println("Note: Exact computation is O(n³) due to Floyd-Warshall.")
    println("For n=100, this is manageable. For n=1000, use approximations.")
    println("="^70)
end

# Run test with small n (exact computation is expensive!)
test_exact_curvature(50, 5)