#!/usr/bin/env julia
#
# Simple Phase Transition Test
# Using a very simple curvature approximation

using Random
using Statistics
using Printf

struct SimpleGraph
    n::Int
    edges::Vector{Tuple{Int, Int}}
    adj::Vector{Vector{Int}}
end

function SimpleGraph(n::Int)
    return SimpleGraph(n, Tuple{Int, Int}[], [Int[] for _ in 1:n])
end

function add_edge!(g::SimpleGraph, u::Int, v::Int)
    if u > v; u, v = v, u; end
    push!(g.edges, (u, v))
    push!(g.adj[u], v)
    push!(g.adj[v], u)
end

neighbors(g::SimpleGraph, v::Int) = g.adj[v]
degree(g::SimpleGraph, v::Int) = length(g.adj[v])

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

function connected_components(g::SimpleGraph)
    visited = falses(g.n)
    components = Vector{Int}[]
    
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
        
        push!(components, component)
    end
    
    return components
end

function largest_component(g::SimpleGraph)
    cc = connected_components(g)
    isempty(cc) && return Int[]
    return cc[argmax(length.(cc))]
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
    Very simple curvature approximation:
    κ(e) ≈ 2 × (triangles through e) / (min degree) - 1
    
    This gives:
    - Tree edge: κ ≈ -1
    - Balanced edge: κ ≈ 0  
    - Clique edge: κ ≈ +1
"""
function simple_curvature(g::SimpleGraph, u::Int, v::Int)
    Nu = neighbors(g, u)
    Nv = neighbors(g, v)
    
    common = length(intersect(Nu, Nv))
    deg_u = length(Nu)
    deg_v = length(Nv)
    
    min_deg = min(deg_u, deg_v)
    min_deg <= 1 && return -1.0
    
    # κ = 2*(common/min_deg) - 1
    # Range: [-1, 1]
    return clamp(2.0 * common / min_deg - 1.0, -1.0, 1.0)
end

function mean_curvature(g::SimpleGraph)
    isempty(g.edges) && return 0.0
    return mean([simple_curvature(g, u, v) for (u, v) in g.edges])
end

"""
    Run phase transition test
"""
function test_phase_transition(n::Int=1000, n_sims::Int=30)
    println("="^70)
    println("PHASE TRANSITION TEST - Simple Curvature")
    println("κ(e) = 2×(triangles/min_degree) - 1")
    println("n = $n, n_sims = $n_sims")
    println("="^70)
    println()
    
    # Extended range
    c_values = [0.5, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.5, 3.0, 3.5, 4.0, 5.0]
    
    for c in c_values
        η = c^2
        p = c / sqrt(n)
        
        curvatures = Float64[]
        
        for sim in 1:n_sims
            g = generate_gnp(n, p, seed=sim)
            lcc = largest_component(g)
            length(lcc) < 30 && continue
            
            sg = induced_subgraph(g, lcc)
            isempty(sg.edges) && continue
            
            κ = mean_curvature(sg)
            push!(curvatures, κ)
        end
        
        if !isempty(curvatures)
            μ = mean(curvatures)
            σ = std(curvatures)
            
            regime = if η < 2.0
                "HYPERBOLIC"
            elseif η > 3.5
                "SPHERICAL"
            else
                "CRITICAL"
            end
            
            @printf("η = %5.2f, c = %4.1f: κ̄ = %+.4f ± %.4f [%s] (n=%d)\n",
                    η, c, μ, σ, regime, length(curvatures))
        end
    end
end

test_phase_transition(1000, 30)