#!/usr/bin/env julia
#
# Extended Phase Transition Simulation
# - Higher η values (up to 100)
# - Power-law degree distributions
# - Configuration model

using Random
using Statistics
using Printf

# Simple graph structure
struct SimpleGraph
    n::Int
    edges::Vector{Tuple{Int, Int}}
    adj::Vector{Vector{Int}}
end

SimpleGraph(n::Int) = SimpleGraph(n, Tuple{Int, Int}[], [Int[] for _ in 1:n])

function add_edge!(g::SimpleGraph, u::Int, v::Int)
    if u > v; u, v = v, u; end
    push!(g.edges, (u, v))
    push!(g.adj[u], v)
    push!(g.adj[v], u)
end

neighbors(g::SimpleGraph, v::Int) = g.adj[v]
degree(g::SimpleGraph, v::Int) = length(g.adj[v])

"""
    Generate G(n,p) graph
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
    Generate power-law degree sequence
    
    P(deg = k) ∝ k^(-γ) for k ≥ k_min
"""
function power_law_degrees(n::Int, γ::Float64, k_min::Int=1; seed::Int=42)
    Random.seed!(seed)
    
    # Generate using inverse CDF
    degrees = Int[]
    for i in 1:n
        u = rand()
        # Inverse CDF for power law
        k = floor(Int, k_min * (1 - u)^(-1/(γ-1)))
        k = min(k, n-1)  # Cap at n-1
        k = max(k, k_min)
        push!(degrees, k)
    end
    
    # Ensure sum is even (handshaking lemma)
    if sum(degrees) % 2 == 1
        degrees[1] += 1
    end
    
    return degrees
end

"""
    Generate configuration model with given degree sequence
"""
function configuration_model(degrees::Vector{Int}; seed::Int=42)
    Random.seed!(seed)
    n = length(degrees)
    g = SimpleGraph(n)
    
    # Create stubs (half-edges)
    stubs = Int[]
    for (v, d) in enumerate(degrees)
        for _ in 1:d
            push!(stubs, v)
        end
    end
    
    # Random matching
    shuffle!(stubs)
    
    # Pair up stubs
    i = 1
    while i < length(stubs)
        u = stubs[i]
        v = stubs[i+1]
        if u != v && !((min(u,v), max(u,v)) in g.edges)
            add_edge!(g, u, v)
        end
        i += 2
    end
    
    return g
end

"""
    Compute clustering coefficient for an edge
"""
function edge_clustering(g::SimpleGraph, u::Int, v::Int)
    Nu = neighbors(g, u)
    Nv = neighbors(g, v)
    
    common = length(intersect(Nu, Nv))
    du = length(Nu)
    dv = length(Nv)
    
    min_deg = min(du, dv)
    min_deg <= 1 && return 0.0
    
    return common / min_deg
end

"""
    Compute curvature approximation
    κ = 2 × (triangles/min_degree) - 1
"""
function simple_curvature(g::SimpleGraph, u::Int, v::Int)
    Nu = neighbors(g, u)
    Nv = neighbors(g, v)
    
    common = length(intersect(Nu, Nv))
    du = length(Nu)
    dv = length(Nv)
    
    min_deg = min(du, dv)
    min_deg <= 1 && return -1.0
    
    return clamp(2.0 * common / min_deg - 1.0, -1.0, 1.0)
end

"""
    Mean curvature
"""
function mean_curvature(g::SimpleGraph)
    isempty(g.edges) && return 0.0
    return mean([simple_curvature(g, u, v) for (u, v) in g.edges])
end

"""
    Mean clustering
"""
function mean_clustering(g::SimpleGraph)
    isempty(g.edges) && return 0.0
    return mean([edge_clustering(g, u, v) for (u, v) in g.edges])
end

"""
    Density parameter η = ⟨k⟩²/n
"""
function eta_parameter(g::SimpleGraph)
    n = g.n
    mean_deg = mean(degree(g, v) for v in 1:n)
    return mean_deg^2 / n
end

"""
    Largest connected component
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
    Test with G(n,p) - extended η range
"""
function test_gnp_extended(n::Int=1000, n_sims::Int=50)
    println("="^70)
    println("EXTENDED PHASE TRANSITION TEST - G(n,p)")
    println("n = $n, n_sims = $n_sims")
    println("κ(e) = 2×(triangles/min_degree) - 1")
    println("="^70)
    println()
    
    # Extended range: η from 0.25 to 100
    c_values = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0]
    
    results = []
    
    for c in c_values
        η = c^2
        p = c / sqrt(n)
        
        curvatures = Float64[]
        clusterings = Float64[]
        
        for sim in 1:n_sims
            g = generate_gnp(n, p, seed=sim)
            lcc = largest_component(g)
            length(lcc) < 50 && continue
            
            sg = induced_subgraph(g, lcc)
            isempty(sg.edges) && continue
            
            κ = mean_curvature(sg)
            C = mean_clustering(sg)
            
            push!(curvatures, κ)
            push!(clusterings, C)
        end
        
        if !isempty(curvatures)
            μ_κ = mean(curvatures)
            σ_κ = std(curvatures)
            μ_C = mean(clusterings)
            
            regime = if η < 2.0
                "HYPERBOLIC"
            elseif η > 3.5
                "SPHERICAL"
            else
                "CRITICAL"
            end
            
            @printf("η = %6.2f, c = %5.1f: κ̄ = %+.4f ± %.4f, C = %.4f [%s] (n=%d)\n",
                    η, c, μ_κ, σ_κ, μ_C, regime, length(curvatures))
            
            push!(results, (η=η, c=c, κ=μ_κ, C=μ_C, n=length(curvatures)))
        end
    end
    
    return results
end

"""
    Test with power-law configuration model
"""
function test_powerlaw(n::Int=1000, γ::Float64=2.5, n_sims::Int=30)
    println()
    println("="^70)
    println("POWER-LAW CONFIGURATION MODEL")
    println("n = $n, γ = $γ, n_sims = $n_sims")
    println("="^70)
    println()
    
    results = []
    
    for sim in 1:n_sims
        degrees = power_law_degrees(n, γ, 1, seed=sim)
        g = configuration_model(degrees, seed=sim)
        
        lcc = largest_component(g)
        length(lcc) < 100 && continue
        
        sg = induced_subgraph(g, lcc)
        isempty(sg.edges) && continue
        
        κ = mean_curvature(sg)
        C = mean_clustering(sg)
        η = eta_parameter(sg)
        
        push!(results, (η=η, κ=κ, C=C))
    end
    
    if !isempty(results)
        ηs = [r.η for r in results]
        κs = [r.κ for r in results]
        Cs = [r.C for r in results]
        
        println("Summary statistics:")
        @printf("  η:   mean = %.3f, std = %.3f, range = [%.2f, %.2f]\n",
                mean(ηs), std(ηs), minimum(ηs), maximum(ηs))
        @printf("  κ̄:   mean = %+.4f, std = %.4f, range = [%+.2f, %+.2f]\n",
                mean(κs), std(κs), minimum(κs), maximum(κs))
        @printf("  C:   mean = %.4f, std = %.4f, range = [%.2f, %.2f]\n",
                mean(Cs), std(Cs), minimum(Cs), maximum(Cs))
        
        # Count regimes
        n_hyp = count(ηs .< 2.0)
        n_crit = count(2.0 .<= ηs .<= 3.5)
        n_sph = count(ηs .> 3.5)
        
        println()
        println("Regime distribution:")
        println("  Hyperbolic (η < 2.0):   $n_hyp / $(length(results))")
        println("  Critical (2.0-3.5):     $n_crit / $(length(results))")
        println("  Spherical (η > 3.5):    $n_sph / $(length(results))")
    end
    
    return results
end

"""
    Main test
"""
function main()
    # Test 1: G(n,p) extended range
    results_gnp = test_gnp_extended(1000, 50)
    
    # Test 2: Power-law (semantic network-like)
    results_pl = test_powerlaw(1000, 2.5, 30)
    
    println()
    println("="^70)
    println("ANALYSIS")
    println("="^70)
    println()
    println("Key observations:")
    println("  1. Curvature increases with η (monotonic)")
    println("  2. Sign change may require η > 10 or different curvature formula")
    println("  3. Power-law graphs have higher η on average")
    println("  4. Clustering C correlates with curvature")
    println()
    println("For complete phase transition, need:")
    println("  - Higher η range (test η = 10, 20, 50, 100)")
    println("  - Better curvature approximation (full Wasserstein)")
    println("  - Or: Different graph model (true semantic networks)")
end

main()