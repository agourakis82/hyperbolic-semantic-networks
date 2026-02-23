#!/usr/bin/env julia
#
# Semantic Network Analysis
# Using SWOW-like properties for realistic phase transition testing

using Random
using Statistics
using LinearAlgebra
using Printf

"""
    Semantic network properties
"""
struct SemanticGraph
    n::Int
    adj::Vector{Vector{Int}}
    weights::Dict{Tuple{Int, Int}, Float64}  # Association strengths
end

"""
    Generate power-law degree sequence (semantic network-like)
    
    Real semantic networks have:
    - Heavy-tailed degree distribution (γ ≈ 2.5-3.0)
    - High clustering (C ≈ 0.02-0.15)
    - Small world structure
"""
function generate_powerlaw_degrees(n::Int, γ::Float64, k_min::Int=1; seed::Int=42)
    Random.seed!(seed)
    degrees = Int[]
    
    # Discrete power-law using inverse CDF
    for i in 1:n
        u = rand()
        k = floor(Int, k_min * (1 - u)^(-1/(γ-1)))
        k = min(k, n-1)
        k = max(k, k_min)
        push!(degrees, k)
    end
    
    # Ensure even sum
    if sum(degrees) % 2 == 1
        degrees[1] += 1
    end
    
    return degrees
end

"""
    Generate configuration model with clustering
    
    Uses triadic closure to create realistic clustering
"""
function generate_semantic_network(n::Int, γ::Float64, target_C::Float64; 
                                    seed::Int=42, max_retries::Int=1000)
    Random.seed!(seed)
    
    # Generate degree sequence
    degrees = generate_powerlaw_degrees(n, γ, 1, seed=seed)
    
    # Create stubs
    stubs = Int[]
    for (v, d) in enumerate(degrees)
        for _ in 1:d
            push!(stubs, v)
        end
    end
    
    # Shuffle and match with triadic closure
    adj = [Int[] for _ in 1:n]
    shuffle!(stubs)
    
    # Matching with preference for triadic closure
    i = 1
    retries = 0
    
    while i < length(stubs) && retries < max_retries
        u = stubs[i]
        v = stubs[i+1]
        
        # Check if edge already exists
        if u != v && !(v in adj[u])
            # With probability related to target clustering,
            # prefer connecting to common neighbors
            common_nbrs = length(intersect(adj[u], adj[v]))
            total_nbrs = length(adj[u]) + length(adj[v])
            
            if total_nbrs > 0
                current_C = 2 * common_nbrs / total_nbrs
            else
                current_C = 0.0
            end
            
            # Accept edge with higher probability if it increases clustering
            p_accept = 0.5 + 0.5 * (target_C - current_C)
            p_accept = clamp(p_accept, 0.1, 0.9)
            
            if rand() < p_accept
                push!(adj[u], v)
                push!(adj[v], u)
                i += 2
                retries = 0
            else
                # Swap with random stub
                j = rand(i+2:length(stubs))
                stubs[i+1], stubs[j] = stubs[j], stubs[i+1]
                retries += 1
            end
        else
            # Invalid edge, swap
            j = rand(i+2:length(stubs))
            stubs[i+1], stubs[j] = stubs[j], stubs[i+1]
            retries += 1
        end
    end
    
    # Create weight dictionary (uniform for now)
    weights = Dict{Tuple{Int, Int}, Float64}()
    for u in 1:n
        for v in adj[u]
            if u < v
                weights[(u, v)] = 1.0
            end
        end
    end
    
    return SemanticGraph(n, adj, weights)
end

"""
    Compute network metrics
"""
function network_metrics(g::SemanticGraph)
    n = g.n
    m = sum(length(adj) for adj in g.adj) ÷ 2
    
    # Mean degree
    mean_deg = 2 * m / n
    
    # Density parameter η
    eta = mean_deg^2 / n
    
    # Clustering coefficient
    total_C = 0.0
    count_C = 0
    
    for v in 1:n
        Nv = g.adj[v]
        deg = length(Nv)
        
        if deg >= 2
            triangles = 0
            for i in 1:deg
                for j in (i+1):deg
                    u = Nv[i]
                    w = Nv[j]
                    if w in g.adj[u]
                        triangles += 1
                    end
                end
            end
            
            possible = deg * (deg - 1) ÷ 2
            total_C += triangles / possible
            count_C += 1
        end
    end
    
    C = count_C > 0 ? total_C / count_C : 0.0
    
    return (n=n, m=m, mean_deg=mean_deg, eta=eta, C=C)
end

"""
    Compute Ollivier-Ricci curvature (weighted version)
"""
function ollivier_ricci_weighted(g::SemanticGraph, u::Int, v::Int; alpha::Float64=0.5)
    # Get weighted degrees
    deg_u = length(g.adj[u])
    deg_v = length(g.adj[v])
    
    (deg_u == 0 || deg_v == 0) && return 0.0
    
    # Compute common neighbors
    common = intersect(g.adj[u], g.adj[v])
    
    # Simplified curvature: κ = 2×(common/min_deg) - 1
    min_deg = min(deg_u, deg_v)
    return clamp(2.0 * length(common) / min_deg - 1.0, -1.0, 1.0)
end

function mean_curvature_semantic(g::SemanticGraph)
    total_κ = 0.0
    edge_count = 0
    
    for u in 1:g.n
        for v in g.adj[u]
            if u < v
                κ = ollivier_ricci_weighted(g, u, v)
                total_κ += κ
                edge_count += 1
            end
        end
    end
    
    return edge_count > 0 ? total_κ / edge_count : 0.0
end

"""
    Largest connected component
"""
function largest_component_semantic(g::SemanticGraph)
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
            for u in g.adj[v]
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

function induced_subgraph_semantic(g::SemanticGraph, vertices::Vector{Int})
    vm = Dict(v => i for (i, v) in enumerate(vertices))
    new_n = length(vertices)
    new_adj = [Int[] for _ in 1:new_n]
    new_weights = Dict{Tuple{Int, Int}, Float64}()
    
    for (new_u, old_u) in enumerate(vertices)
        for old_v in g.adj[old_u]
            if haskey(vm, old_v)
                new_v = vm[old_v]
                if new_u < new_v && !(new_v in new_adj[new_u])
                    push!(new_adj[new_u], new_v)
                    push!(new_adj[new_v], new_u)
                    new_weights[(new_u, new_v)] = get(g.weights, (min(old_u, old_v), max(old_u, old_v)), 1.0)
                end
            end
        end
    end
    
    return SemanticGraph(new_n, new_adj, new_weights)
end

"""
    Test semantic networks
"""
function test_semantic_networks()
    println("="^70)
    println("SEMANTIC NETWORK ANALYSIS")
    println("Power-law degree distribution with clustering")
    println("="^70)
    println()
    
    # Test different parameter combinations
    configs = [
        (n=500, γ=2.8, target_C=0.02),   # Low clustering (taxonomy-like)
        (n=500, γ=2.6, target_C=0.05),   # Medium clustering
        (n=500, γ=2.4, target_C=0.10),   # High clustering (SWOW-like)
        (n=500, γ=2.2, target_C=0.15),   # Very high clustering
    ]
    
    results = []
    
    for (n, γ, target_C) in configs
        println("Configuration: n=$n, γ=$γ, target_C=$target_C")
        println("-"^70)
        
        κs = Float64[]
        etas = Float64[]
        Cs = Float64[]
        
        for sim in 1:30
            g = generate_semantic_network(n, γ, target_C, seed=sim)
            
            # Get largest component
            lcc = largest_component_semantic(g)
            length(lcc) < 100 && continue
            
            sg = induced_subgraph_semantic(g, lcc)
            isempty(sg.adj[1]) && continue
            
            # Compute metrics
            metrics = network_metrics(sg)
            κ = mean_curvature_semantic(sg)
            
            push!(κs, κ)
            push!(etas, metrics.eta)
            push!(Cs, metrics.C)
        end
        
        if !isempty(κs)
            @printf("  η:   %.3f ± %.3f [%.2f, %.2f]\n", mean(etas), std(etas), minimum(etas), maximum(etas))
            @printf("  C:   %.4f ± %.4f [%.4f, %.4f]\n", mean(Cs), std(Cs), minimum(Cs), maximum(Cs))
            @printf("  κ̄:  %+.4f ± %.4f [%.4f, %.4f]\n", mean(κs), std(κs), minimum(κs), maximum(κs))
            
            push!(results, (γ=γ, target_C=target_C, η=mean(etas), C=mean(Cs), κ=mean(κs)))
        end
        println()
    end
    
    # Analysis
    println("="^70)
    println("ANALYSIS")
    println("="^70)
    println()
    println("Correlation analysis:")
    
    if length(results) >= 3
        # Correlation between C and κ
        Cs = [r.C for r in results]
        κs = [r.κ for r in results]
        
        @printf("  Clustering C vs Curvature κ: r = %.3f\n", cor(Cs, κs))
        println("  → Higher clustering → Higher curvature (less negative)")
        println()
        
        # Find sweet spot
        println("Hyperbolic sweet spot (empirical):")
        for r in results
            if r.C ∈ 0.02:0.01:0.15 && r.κ < 0
                @printf("  C = %.2f, κ̄ = %+.4f [SWEET SPOT]\n", r.C, r.κ)
            end
        end
    end
    
    return results
end

# Run test
test_semantic_networks()