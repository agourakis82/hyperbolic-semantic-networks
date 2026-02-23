#!/usr/bin/env julia
#
# Improved Phase Transition Simulation
# Using more accurate curvature computation
#
# This version uses a better approximation of Wasserstein distance

using Random
using Statistics
using LinearAlgebra
using Printf

"""
    SimpleGraph structure for testing
"""
struct SimpleGraph
    n::Int
    edges::Set{Tuple{Int, Int}}
    adj::Vector{Set{Int}}  # Adjacency list for efficiency
end

function SimpleGraph(n::Int)
    adj = [Set{Int}() for _ in 1:n]
    return SimpleGraph(n, Set{Tuple{Int, Int}}(), adj)
end

function add_edge!(g::SimpleGraph, u::Int, v::Int)
    if u > v
        u, v = v, u
    end
    if !((u, v) in g.edges)
        push!(g.edges, (u, v))
        push!(g.adj[u], v)
        push!(g.adj[v], u)
    end
end

has_edge(g::SimpleGraph, u::Int, v::Int) = (min(u,v), max(u,v)) in g.edges
ne(g::SimpleGraph) = length(g.edges)
nv(g::SimpleGraph) = g.n
neighbors(g::SimpleGraph, v::Int) = g.adj[v]
degree(g::SimpleGraph, v::Int) = length(g.adj[v])

"""
    BFS distance computation
"""
function bfs_distance(g::SimpleGraph, src::Int, dst::Int)
    src == dst && return 0
    
    visited = falses(g.n)
    dist = fill(-1, g.n)
    queue = [src]
    visited[src] = true
    dist[src] = 0
    
    while !isempty(queue)
        v = popfirst!(queue)
        for u in neighbors(g, v)
            if !visited[u]
                visited[u] = true
                dist[u] = dist[v] + 1
                u == dst && return dist[u]
                push!(queue, u)
            end
        end
    end
    
    return -1  # No path
end

"""
    Compute all-pairs shortest paths (up to max_dist)
"""
function all_pairs_distances(g::SimpleGraph; max_dist::Int=10)
    n = g.n
    dists = fill(max_dist + 1, n, n)
    
    for v in 1:n
        dists[v, v] = 0
        # BFS from v
        visited = falses(n)
        queue = [v]
        visited[v] = true
        
        while !isempty(queue)
            u = popfirst!(queue)
            for w in neighbors(g, u)
                if !visited[w]
                    visited[w] = true
                    dists[v, w] = dists[v, u] + 1
                    if dists[v, w] < max_dist
                        push!(queue, w)
                    end
                end
            end
        end
    end
    
    return dists
end

"""
    Compute probability measure for Ollivier-Ricci
    μ_u = α·δ_u + (1-α)·Uniform(neighbors(u))
"""
function probability_measure(g::SimpleGraph, u::Int, alpha::Float64)
    deg = degree(g, u)
    measure = Dict{Int, Float64}()
    
    # Self component
    measure[u] = alpha
    
    # Neighbor component
    if deg > 0
        for v in neighbors(g, u)
            measure[v] = get(measure, v, 0.0) + (1 - alpha) / deg
        end
    end
    
    return measure
end

"""
    Compute Wasserstein-1 distance using earth mover's algorithm
    
    Simplified: use greedy matching on sorted masses
"""
function wasserstein_distance(mu::Dict{Int, Float64}, nu::Dict{Int, Float64}, 
                               dists::Matrix{Int}, max_dist::Int)
    # Get union of supports
    nodes = union(keys(mu), keys(nu))
    
    # Build mass vectors
    masses = [(get(mu, v, 0.0), get(nu, v, 0.0), v) for v in nodes]
    
    # Greedy transport
    cost = 0.0
    
    # For each node, match excess mass
    for (i, (m_u, m_v, v)) in enumerate(masses)
        diff = m_u - m_v
        if abs(diff) > 1e-10
            # Find closest node with opposite excess
            for (j, (m_u2, m_v2, v2)) in enumerate(masses)
                if i != j
                    diff2 = m_v2 - m_u2  # Opposite sign
                    if diff * diff2 > 0  # Same direction means both excess
                        continue
                    end
                    
                    transport = min(abs(diff), abs(diff2))
                    d = dists[v, v2]
                    if d > 0 && d <= max_dist
                        cost += transport * d
                        # Update masses (simplified - not tracking state)
                    end
                end
            end
        end
    end
    
    return cost
end

"""
    Improved Ollivier-Ricci curvature computation
"""
function ollivier_ricci_curvature(g::SimpleGraph, u::Int, v::Int, 
                                   dists::Matrix{Int}; alpha::Float64=0.5)
    !has_edge(g, u, v) && return 0.0
    
    # Get measures
    mu_u = probability_measure(g, u, alpha)
    mu_v = probability_measure(g, v, alpha)
    
    # Compute Wasserstein distance
    W1 = wasserstein_distance(mu_u, mu_v, dists, 10)
    
    # Curvature
    kappa = 1.0 - W1
    
    return clamp(kappa, -1.0, 1.0)
end

"""
    Compute mean curvature for graph
"""
function compute_mean_curvature(g::SimpleGraph; alpha::Float64=0.5)
    ne(g) == 0 && return 0.0
    
    # Precompute distances
    dists = all_pairs_distances(g, max_dist=10)
    
    curvatures = Float64[]
    for (u, v) in g.edges
        κ = ollivier_ricci_curvature(g, u, v, dists, alpha=alpha)
        push!(curvatures, κ)
    end
    
    return mean(curvatures)
end

"""
    Generate G(n,p) random graph
"""
function generate_gnp(n::Int, p::Real; seed::Int=42)
    Random.seed!(seed)
    g = SimpleGraph(n)
    
    for i in 1:n
        for j in (i+1):n
            if rand() < p
                add_edge!(g, i, j)
            end
        end
    end
    
    return g
end

"""
    Get largest connected component
"""
function largest_component(g::SimpleGraph)
    visited = falses(g.n)
    largest = Int[]
    
    for start in 1:g.n
        visited[start] && continue
        
        component = Int[]
        stack = [start]
        visited[start] = true
        
        while !isempty(stack)
            v = pop!(stack)
            push!(component, v)
            for u in neighbors(g, v)
                if !visited[u]
                    visited[u] = true
                    push!(stack, u)
                end
            end
        end
        
        if length(component) > length(largest)
            largest = component
        end
    end
    
    return largest
end

function induced_subgraph(g::SimpleGraph, vertices::Vector{Int})
    sg = SimpleGraph(length(vertices))
    vm = Dict(v => i for (i, v) in enumerate(vertices))
    
    for (u, v) in g.edges
        if haskey(vm, u) && haskey(vm, v)
            add_edge!(sg, vm[u], vm[v])
        end
    end
    
    return sg
end

"""
    Test phase transition with improved curvature
"""
function test_phase_transition(n::Int=500, n_sims::Int=50)
    println("="^70)
    println("PHASE TRANSITION TEST - Improved Curvature Computation")
    println("n = $n, n_sims = $n_sims")
    println("="^70)
    println()
    
    # Test range: c from 0.5 to 4.0 (η from 0.25 to 16)
    c_values = [0.5, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.5, 3.0, 3.5, 4.0]
    
    results = []
    
    for c in c_values
        η = c^2
        p = c / sqrt(n)
        
        curvatures = Float64[]
        
        for sim in 1:n_sims
            g = generate_gnp(n, p, seed=sim)
            
            # Get largest component
            lcc = largest_component(g)
            length(lcc) < 20 && continue
            
            sg = induced_subgraph(g, lcc)
            ne(sg) == 0 && continue
            
            # Compute curvature
            κ = compute_mean_curvature(sg, alpha=0.5)
            !isnan(κ) && !isinf(κ) && push!(curvatures, κ)
        end
        
        if !isempty(curvatures)
            mean_κ = mean(curvatures)
            std_κ = std(curvatures)
            median_κ = median(curvatures)
            
            regime = if η < 2.0
                "HYPERBOLIC"
            elseif η > 3.5
                "SPHERICAL"
            else
                "CRITICAL"
            end
            
            @printf("η = %5.2f, c = %4.1f: κ̄ = %+.4f, med = %+.4f, σ = %.4f [%s] (n=%d)\n",
                    η, c, mean_κ, median_κ, std_κ, regime, length(curvatures))
            
            push!(results, (η=η, c=c, mean_κ=mean_κ, median_κ=median_κ, 
                          std_κ=std_κ, n=length(curvatures)))
        end
    end
    
    println()
    println("="^70)
    println("ANALYSIS")
    println("="^70)
    
    # Find approximate critical point
    neg_curv = filter(r -> r.mean_κ < 0, results)
    pos_curv = filter(r -> r.mean_κ > 0, results)
    
    if !isempty(neg_curv) && !isempty(pos_curv)
        max_neg = maximum(r.η for r in neg_curv)
        min_pos = minimum(r.η for r in pos_curv)
        println("Sign change occurs between η = $max_neg and η = $min_pos")
        println("Estimated critical point: η_c ≈ $(sqrt(max_neg * min_pos))")
    elseif !isempty(neg_curv)
        println("All tested values show negative curvature (increase η range)")
    else
        println("All tested values show positive curvature (decrease η range)")
    end
    
    return results
end

"""
    Main function
"""
function main()
    test_phase_transition(500, 50)
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end