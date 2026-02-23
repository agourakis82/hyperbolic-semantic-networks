#!/usr/bin/env julia
#
# Fast Curvature Computation
# Optimized for large graphs and many simulations

using Random
using Statistics
using LinearAlgebra
using Printf

"""
    CompactGraph - memory-efficient representation
"""
struct CompactGraph
    n::Int
    adj::Vector{Vector{Int}}  # Adjacency lists
end

function generate_gnp_fast(n::Int, p::Real; seed::Int=42)
    Random.seed!(seed)
    adj = [Int[] for _ in 1:n]
    
    # Use vectorized operations where possible
    for i in 1:n
        # Generate all potential neighbors at once
        candidates = (i+1):n
        for j in candidates
            if rand() < p
                push!(adj[i], j)
                push!(adj[j], i)
            end
        end
    end
    
    # Sort adjacency lists for faster intersection
    for i in 1:n
        sort!(adj[i])
    end
    
    return CompactGraph(n, adj)
end

"""
    Fast intersection of sorted vectors
    Complexity: O(|A| + |B|)
"""
function fast_intersection(A::Vector{Int}, B::Vector{Int})
    result = Int[]
    sizehint!(result, min(length(A), length(B)))
    
    i, j = 1, 1
    while i <= length(A) && j <= length(B)
        if A[i] < B[j]
            i += 1
        elseif A[i] > B[j]
            j += 1
        else
            push!(result, A[i])
            i += 1
            j += 1
        end
    end
    
    return result
end

"""
    Fast curvature computation
    Uses optimized intersection and preallocated buffers
"""
function fast_curvature(g::CompactGraph, u::Int, v::Int)
    Nu = g.adj[u]
    Nv = g.adj[v]
    
    # Fast intersection
    common = fast_intersection(Nu, Nv)
    
    du = length(Nu)
    dv = length(Nv)
    min_deg = min(du, dv)
    
    min_deg <= 1 && return -1.0
    
    return clamp(2.0 * length(common) / min_deg - 1.0, -1.0, 1.0)
end

"""
    Mean curvature with batch processing
"""
function fast_mean_curvature(g::CompactGraph)
    # Generate edge list on the fly
    total_curv = 0.0
    edge_count = 0
    
    for u in 1:g.n
        for v in g.adj[u]
            if u < v  # Process each edge once
                κ = fast_curvature(g, u, v)
                total_curv += κ
                edge_count += 1
            end
        end
    end
    
    return edge_count > 0 ? total_curv / edge_count : 0.0
end

"""
    BFS for largest component (optimized)
"""
function largest_component_fast(g::CompactGraph)
    visited = falses(g.n)
    max_component = Int[]
    
    # Preallocate stack
    stack = Int[]
    sizehint!(stack, g.n)
    
    for start in 1:g.n
        visited[start] && continue
        
        empty!(stack)
        push!(stack, start)
        visited[start] = true
        component_size = 0
        
        while !isempty(stack)
            v = pop!(stack)
            component_size += 1
            
            for u in g.adj[v]
                if !visited[u]
                    visited[u] = true
                    push!(stack, u)
                end
            end
        end
        
        if component_size > length(max_component)
            max_component = findall(visited)
            # Reset visited for new search
            fill!(visited, false)
            for v in max_component
                visited[v] = true
            end
        end
    end
    
    return max_component
end

"""
    Extract subgraph (optimized)
"""
function extract_subgraph(g::CompactGraph, vertices::Vector{Int})
    vm = Dict(v => i for (i, v) in enumerate(vertices))
    new_n = length(vertices)
    new_adj = [Int[] for _ in 1:new_n]
    
    for (new_u, old_u) in enumerate(vertices)
        for old_v in g.adj[old_u]
            if haskey(vm, old_v)
                new_v = vm[old_v]
                if new_u < new_v && !(new_v in new_adj[new_u])
                    push!(new_adj[new_u], new_v)
                    push!(new_adj[new_v], new_u)
                end
            end
        end
    end
    
    # Sort adjacency lists
    for i in 1:new_n
        sort!(new_adj[i])
    end
    
    return CompactGraph(new_n, new_adj)
end

"""
    Parallel simulation runner
"""
function run_simulations_parallel(n::Int, p::Real, n_sims::Int; n_workers::Int=4)
    results = Float64[]
    
    # Simple parallelization via batching
    batch_size = ceil(Int, n_sims / n_workers)
    
    for worker_id in 1:n_workers
        start_idx = (worker_id - 1) * batch_size + 1
        end_idx = min(worker_id * batch_size, n_sims)
        
        for sim in start_idx:end_idx
            g = generate_gnp_fast(n, p, seed=sim)
            lcc = largest_component_fast(g)
            length(lcc) < 50 && continue
            
            sg = extract_subgraph(g, lcc)
            isempty(sg.adj[1]) && continue
            
            κ = fast_mean_curvature(sg)
            push!(results, κ)
        end
    end
    
    return results
end

"""
    Benchmark and test
"""
function benchmark_and_test()
    println("="^70)
    println("FAST CURVATURE COMPUTATION - BENCHMARK")
    println("="^70)
    println()
    
    # Test different graph sizes
    sizes = [500, 1000, 2000]
    
    for n in sizes
        p = 1.6 / sqrt(n)  # η = 2.56
        
        println("n = $n, p = $(round(p, digits=4))")
        
        # Time graph generation
        t_gen = @elapsed g = generate_gnp_fast(n, p, seed=1)
        println("  Graph generation: $(round(t_gen, digits=3))s")
        
        # Time component extraction
        t_comp = @elapsed lcc = largest_component_fast(g)
        println("  Component extraction: $(round(t_comp, digits=3))s")
        println("  Largest component: $(length(lcc)) / $n nodes")
        
        # Time curvature computation
        if length(lcc) > 50
            sg = extract_subgraph(g, lcc)
            t_curv = @elapsed κ = fast_mean_curvature(sg)
            println("  Curvature computation: $(round(t_curv, digits=3))s")
            println("  Mean curvature: $(round(κ, digits=4))")
        end
        
        println()
    end
end

"""
    Run extended test with fast implementation
"""
function run_extended_test()
    println("="^70)
    println("EXTENDED PHASE TEST - FAST IMPLEMENTATION")
    println("="^70)
    println()
    
    n = 2000  # Larger graphs
    c_values = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]
    n_sims = 100
    
    println("n = $n, n_sims = $n_sims per point")
    println("-"^70)
    
    for c in c_values
        η = c^2
        p = c / sqrt(n)
        
        println("Testing η = $(round(η, digits=2)) (c = $c)...")
        
        results = Float64[]
        
        for sim in 1:n_sims
            g = generate_gnp_fast(n, p, seed=sim)
            lcc = largest_component_fast(g)
            length(lcc) < 100 && continue
            
            sg = extract_subgraph(g, lcc)
            isempty(sg.adj[1]) && continue
            
            κ = fast_mean_curvature(sg)
            push!(results, κ)
            
            # Progress indicator
            if sim % 20 == 0
                print(".")
            end
        end
        println()
        
        if !isempty(results)
            μ = mean(results)
            σ = std(results)
            @printf("  η = %.2f: κ̄ = %+.4f ± %.4f (n=%d)\n", 
                    η, μ, σ, length(results))
        end
    end
end

"""
    Main
"""
function main()
    # Run benchmark
    benchmark_and_test()
    
    println()
    println("="^70)
    println()
    
    # Run extended test
    run_extended_test()
end

main()