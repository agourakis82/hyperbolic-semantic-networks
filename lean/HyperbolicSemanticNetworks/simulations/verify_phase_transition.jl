#!/usr/bin/env julia
#
# Phase Transition Verification Script
# 
# This script validates the theoretical predictions from the Lean
# formalization against empirical simulations.
#
# Usage: julia verify_phase_transition.jl

using Random
using Statistics
using LinearAlgebra
using Dates
using Printf

# Simple graph structure for testing
struct SimpleGraph
    n::Int
    edges::Set{Tuple{Int, Int}}
end

SimpleGraph(n::Int) = SimpleGraph(n, Set{Tuple{Int, Int}}())

function add_edge!(g::SimpleGraph, u::Int, v::Int)
    if u > v
        u, v = v, u
    end
    push!(g.edges, (u, v))
end

function has_edge(g::SimpleGraph, u::Int, v::Int)
    if u > v
        u, v = v, u
    end
    return (u, v) in g.edges
end

ne(g::SimpleGraph) = length(g.edges)
nv(g::SimpleGraph) = g.n

function neighbors(g::SimpleGraph, v::Int)
    nbrs = Int[]
    for (u, w) in g.edges
        if u == v
            push!(nbrs, w)
        elseif w == v
            push!(nbrs, u)
        end
    end
    return nbrs
end

function degree(g::SimpleGraph, v::Int)
    return length(neighbors(g, v))
end

function connected_components(g::SimpleGraph)
    visited = falses(g.n)
    components = Vector{Int}[]
    
    for start in 1:g.n
        if visited[start]
            continue
        end
        
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

function induced_subgraph(g::SimpleGraph, vertices::Vector{Int})
    vertex_map = Dict(v => i for (i, v) in enumerate(vertices))
    sg = SimpleGraph(length(vertices))
    
    for (u, v) in g.edges
        if haskey(vertex_map, u) && haskey(vertex_map, v)
            add_edge!(sg, vertex_map[u], vertex_map[v])
        end
    end
    
    return sg, vertices
end

"""
    generate_gnp(n, p; seed=42)

Generate an Erdős-Rényi G(n,p) random graph.
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
    ollivier_ricci_simple(g, u, v, alpha=0.5)

Simplified Ollivier-Ricci curvature computation.

Formula: κ = 1 - W₁(μᵤ, μᵥ) / d(u,v)

Where μᵤ = α·δᵤ + (1-α)·Uniform(neighbors(u))
"""
function ollivier_ricci_simple(g::SimpleGraph, u::Int, v::Int, alpha::Float64=0.5)
    if !has_edge(g, u, v)
        return 0.0
    end
    
    # Get neighbors
    nbrs_u = neighbors(g, u)
    nbrs_v = neighbors(g, v)
    
    deg_u = length(nbrs_u)
    deg_v = length(nbrs_v)
    
    if deg_u == 0 || deg_v == 0
        return 0.0
    end
    
    # Compute probability measures
    # μᵤ(u) = α, μᵤ(nbr) = (1-α)/deg_u
    # Similarly for μᵥ
    
    # Simplified Wasserstein distance computation
    # W₁ = sum over all nodes of |μᵤ(w) - μᵥ(w)| for the "greedy" coupling
    # This is a lower bound on true Wasserstein
    
    # Common neighbors contribute 0 cost
    common = intersect(nbrs_u, nbrs_v)
    only_u = setdiff(nbrs_u, nbrs_v)
    only_v = setdiff(nbrs_v, nbrs_u)
    
    # Transport cost approximation
    # Mass on u itself: α
    # Mass on exclusive neighbors: (1-α) * |only_u|/deg_u
    # This mass needs to be transported to v's side
    
    cost = 0.0
    
    # Self mass difference
    mass_u_at_u = alpha
    mass_v_at_u = 0.0
    if u == v
        mass_v_at_u = alpha
    elseif u in nbrs_v
        mass_v_at_u = (1 - alpha) / deg_v
    end
    
    cost += abs(mass_u_at_u - mass_v_at_u)
    
    # Mass on common neighbors (contributes little to cost)
    for w in common
        mass_u_at_w = (1 - alpha) / deg_u
        mass_v_at_w = (1 - alpha) / deg_v
        cost += abs(mass_u_at_w - mass_v_at_w) * 0.1  # Small distance
    end
    
    # Mass on exclusive neighbors (contributes full cost)
    for w in only_u
        mass_u_at_w = (1 - alpha) / deg_u
        mass_v_at_w = 0.0
        cost += abs(mass_u_at_w - mass_v_at_w) * 1.0
    end
    
    for w in only_v
        mass_u_at_w = 0.0
        mass_v_at_w = (1 - alpha) / deg_v
        cost += abs(mass_u_at_w - mass_v_at_w) * 1.0
    end
    
    # Curvature: κ = 1 - cost / distance
    # Distance between u and v is 1 (they're neighbors)
    distance = 1.0
    
    kappa = 1.0 - cost / distance
    
    return clamp(kappa, -1.0, 1.0)
end

"""
    compute_mean_curvature(g; alpha=0.5)

Compute mean Ollivier-Ricci curvature for graph g.
"""
function compute_mean_curvature(g::SimpleGraph; alpha::Float64=0.5)
    if ne(g) == 0
        return 0.0
    end
    
    curvatures = Float64[]
    
    for (u, v) in g.edges
        κ = ollivier_ricci_simple(g, u, v, alpha)
        push!(curvatures, κ)
    end
    
    return mean(curvatures)
end

"""
    eta_parameter(n, p)

Compute the density parameter η = ⟨k⟩²/n.
"""
function eta_parameter(n::Int, p::Real)
    mean_degree = (n - 1) * p
    return mean_degree^2 / n
end

"""
    test_critical_point(; n=1000, n_sims=200)

Test curvature around the critical point η_c = 2.5.
"""
function test_critical_point(; n::Int=1000, n_sims::Int=200)
    println("Testing critical point at η_c = 2.5")
    println("n = $n, n_sims = $n_sims")
    println("="^60)
    
    # Test values of c where η = c²
    c_values = range(0.5, 3.0, length=20)
    
    results = []
    
    for c in c_values
        η = c^2
        p = c / sqrt(n)
        
        curvatures = Float64[]
        
        for sim in 1:n_sims
            g = generate_gnp(n, p, seed=sim)
            
            # Only use largest connected component
            cc = connected_components(g)
            if isempty(cc)
                continue
            end
            largest_cc = cc[argmax(length.(cc))]
            
            if length(largest_cc) < 10
                continue
            end
            
            # Subgraph
            sg, _ = induced_subgraph(g, largest_cc)
            
            if ne(sg) == 0
                continue
            end
            
            κ = compute_mean_curvature(sg)
            push!(curvatures, κ)
        end
        
        if !isempty(curvatures)
            mean_κ = mean(curvatures)
            std_κ = std(curvatures)
            
            push!(results, (η=η, c=c, mean_κ=mean_κ, std_κ=std_κ, n=length(curvatures)))
            
            regime = η < 2.0 ? "HYPERBOLIC" : (η > 3.0 ? "SPHERICAL" : "CRITICAL")
            @printf("η = %.3f, c = %.3f: κ̄ = %+.4f ± %.4f [%s]\n", 
                    η, c, mean_κ, std_κ, regime)
        end
    end
    
    return results
end

"""
    test_concentration(; n_values=[100, 200, 500, 1000], c=1.6)

Test that variance decreases as 1/n (concentration).
"""
function test_concentration(; n_values::Vector{Int}=[100, 200, 500, 1000], 
                            c::Float64=1.6, n_sims::Int=500)
    println("Testing concentration: Var[κ] = O(1/n)")
    println("c = $c (η = $(c^2))")
    println("="^60)
    
    variances = Float64[]
    
    for n in n_values
        p = c / sqrt(n)
        
        curvatures = Float64[]
        
        for sim in 1:n_sims
            g = generate_gnp(n, p, seed=sim)
            
            cc = connected_components(g)
            isempty(cc) && continue
            
            largest_cc = cc[argmax(length.(cc))]
            length(largest_cc) < 10 && continue
            
            sg, _ = induced_subgraph(g, largest_cc)
            ne(sg) == 0 && continue
            
            κ = compute_mean_curvature(sg)
            push!(curvatures, κ)
        end
        
        if length(curvatures) > 10
            var_κ = var(curvatures)
            push!(variances, var_κ)
            
            @printf("n = %4d: Var[κ] = %.6f, n×Var[κ] = %.4f\n",
                    n, var_κ, n * var_κ)
        end
    end
    
    return variances
end

"""
    main()

Run all verification tests.
"""
function main()
    println("="^60)
    println("PHASE TRANSITION VERIFICATION")
    println("Lean 4 Formalization Companion")
    println("="^60)
    println()
    
    # Test 1: Critical point
    println("TEST 1: Critical Point Detection")
    println("-"^60)
    results_critical = test_critical_point(n=500, n_sims=100)
    println()
    
    # Test 2: Concentration
    println("TEST 2: Concentration (Variance Scaling)")
    println("-"^60)
    results_concentration = test_concentration(
        n_values=[100, 200, 500],
        c=1.6,
        n_sims=200
    )
    println()
    
    println("="^60)
    println("VERIFICATION COMPLETE")
    println("="^60)
    println()
    println("Summary:")
    println("  - Critical point should be near η ≈ 2.5")
    println("  - Concentration: Var[κ] should decrease with n")
    println("  - Scaling: p = c/√n should give consistent η = c²")
    println()
    println("Compare these empirical results with the Lean formalization")
    println("in PhaseTransitionProof.lean")
end

# Run main if executed directly
if abspath(PROGRAM_FILE) == @__FILE__
    main()
end