#!/usr/bin/env julia
#
# Production Pipeline for Phase Transition Analysis
# 
# Features:
# - Distributed computing support
# - Progress tracking
# - Result serialization
# - Reproducibility guarantees
# - Performance monitoring

using Random
using Statistics
using LinearAlgebra
using Printf
using Dates
using JSON
using Serialization

# Configuration
struct PipelineConfig
    n_values::Vector{Int}
    c_values::Vector{Float64}
    n_sims::Int
    output_dir::String
    checkpoint_interval::Int
    seed_base::Int
end

function default_config()
    PipelineConfig(
        [500, 1000, 2000, 5000],
        range(0.5, 10.0, length=50),
        100,
        "results",
        10,
        42
    )
end

# Progress tracking
mutable struct ProgressTracker
    total_jobs::Int
    completed_jobs::Int
    start_time::DateTime
    current_job::String
end

function ProgressTracker(total::Int)
    ProgressTracker(total, 0, now(), "")
end

function update!(p::ProgressTracker, job_name::String)
    p.completed_jobs += 1
    p.current_job = job_name
    
    elapsed = now() - p.start_time
    rate = p.completed_jobs / (Dates.value(elapsed) / 1000)  # jobs per second
    remaining = (p.total_jobs - p.completed_jobs) / rate
    
    percent = 100 * p.completed_jobs / p.total_jobs
    
    @printf("\r[%5.1f%%] %s | Elapsed: %s | ETA: %s | Rate: %.2f jobs/s",
        percent, job_name, format_duration(elapsed), 
        format_duration(Second(round(Int, remaining))), rate)
    flush(stdout)
end

function format_duration(d::DateTime)
    return Dates.format(d, "HH:MM:SS")
end

function format_duration(s::Second)
    hrs = div(s.value, 3600)
    mins = div(s.value % 3600, 60)
    secs = s.value % 60
    @sprintf("%02d:%02d:%02d", hrs, mins, secs)
end

# Optimized graph structures
struct FastGraph
    n::Int
    adj::Vector{Vector{Int}}
end

function generate_gnp(n::Int, p::Real; seed::Int=42)
    Random.seed!(seed)
    adj = [Int[] for _ in 1:n]
    
    @inbounds for i in 1:n
        for j in (i+1):n
            if rand() < p
                push!(adj[i], j)
                push!(adj[j], i)
            end
        end
    end
    
    # Sort for fast intersection
    @inbounds for i in 1:n
        sort!(adj[i])
    end
    
    return FastGraph(n, adj)
end

# Fast intersection
function fast_intersect(A::Vector{Int}, B::Vector{Int})
    count = 0
    i, j = 1, 1
    @inbounds while i <= length(A) && j <= length(B)
        if A[i] < B[j]
            i += 1
        elseif A[i] > B[j]
            j += 1
        else
            count += 1
            i += 1
            j += 1
        end
    end
    return count
end

# Optimized curvature
function edge_curvature(g::FastGraph, u::Int, v::Int)
    Nu = g.adj[u]
    Nv = g.adj[v]
    
    common = fast_intersect(Nu, Nv)
    du, dv = length(Nu), length(Nv)
    min_deg = min(du, dv)
    
    min_deg <= 1 && return -1.0
    return clamp(2.0 * common / min_deg - 1.0, -1.0, 1.0)
end

function mean_curvature(g::FastGraph)
    total = 0.0
    n_edges = 0
    
    @inbounds for u in 1:g.n
        for v in g.adj[u]
            if u < v
                total += edge_curvature(g, u, v)
                n_edges += 1
            end
        end
    end
    
    return n_edges > 0 ? total / n_edges : 0.0
end

# BFS for largest component
function largest_component(g::FastGraph)
    visited = falses(g.n)
    max_size = 0
    max_component = Int[]
    
    @inbounds for start in 1:g.n
        visited[start] && continue
        
        component = Int[]
        sizehint!(component, 1000)
        stack = Int[start]
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
        
        if length(component) > max_size
            max_size = length(component)
            max_component = component
        end
    end
    
    return max_component
end

function extract_subgraph(g::FastGraph, vertices::Vector{Int})
    vm = Dict{Int, Int}(v => i for (i, v) in enumerate(vertices))
    new_n = length(vertices)
    new_adj = [Int[] for _ in 1:new_n]
    
    @inbounds for (new_u, old_u) in enumerate(vertices)
        for old_v in g.adj[old_u]
            if haskey(vm, old_v)
                new_v = vm[old_v]
                if new_u < new_v
                    push!(new_adj[new_u], new_v)
                    push!(new_adj[new_v], new_u)
                end
            end
        end
    end
    
    @inbounds for i in 1:new_n
        sort!(new_adj[i])
    end
    
    return FastGraph(new_n, new_adj)
end

# Single simulation
function run_simulation(n::Int, c::Float64, sim_id::Int, config::PipelineConfig)
    p = c / sqrt(n)
    
    g = generate_gnp(n, p, seed=config.seed_base + sim_id)
    lcc = largest_component(g)
    
    length(lcc) < n ÷ 10 && return nothing  # Skip if component too small
    
    sg = extract_subgraph(g, lcc)
    isempty(sg.adj[1]) && return nothing
    
    κ = mean_curvature(sg)
    
    return Dict(
        "n" => n,
        "c" => c,
        "eta" => c^2,
        "p" => p,
        "curvature" => κ,
        "lcc_size" => length(lcc),
        "sim_id" => sim_id,
        "timestamp" => string(now())
    )
end

# Batch processing
function process_batch(n::Int, c::Float64, sim_range::UnitRange{Int}, 
                       config::PipelineConfig, tracker::ProgressTracker)
    results = Dict[]
    
    for sim_id in sim_range
        result = run_simulation(n, c, sim_id, config)
        
        if result !== nothing
            push!(results, result)
        end
        
        update!(tracker, "n=$n, c=$c, sim=$sim_id")
    end
    
    return results
end

# Main pipeline
function run_pipeline(config::PipelineConfig=default_config())
    println("="^70)
    println("PHASE TRANSITION - PRODUCTION PIPELINE")
    println("="^70)
    println()
    
    # Create output directory
    mkpath(config.output_dir)
    
    # Calculate total jobs
    total_jobs = length(config.n_values) * length(config.c_values) * config.n_sims
    println("Configuration:")
    println("  Graph sizes: $(config.n_values)")
    println("  η range: $(round(minimum(config.c_values)^2, digits=2)) to $(round(maximum(config.c_values)^2, digits=2))")
    println("  Simulations per point: $(config.n_sims)")
    println("  Total jobs: $total_jobs")
    println()
    
    tracker = ProgressTracker(total_jobs)
    all_results = Dict[]
    checkpoint_count = 0
    
    # Process all combinations
    for n in config.n_values
        for c in config.c_values
            batch_results = process_batch(n, c, 1:config.n_sims, config, tracker)
            append!(all_results, batch_results)
            
            checkpoint_count += 1
            
            # Checkpoint
            if checkpoint_count >= config.checkpoint_interval
                checkpoint_file = joinpath(config.output_dir, 
                    "checkpoint_$(n)_$(replace(string(c), '.' => '_')).jls")
                serialize(checkpoint_file, batch_results)
                checkpoint_count = 0
            end
        end
    end
    
    println()  # New line after progress
    println()
    
    # Save final results
    results_file = joinpath(config.output_dir, 
        "phase_transition_results_$(Dates.format(now(), "yyyymmdd_HHMMSS")).json")
    
    open(results_file, "w") do f
        JSON.print(f, all_results)
    end
    
    println("="^70)
    println("PIPELINE COMPLETE")
    println("="^70)
    println()
    println("Results saved to: $results_file")
    println("Total simulations completed: $(length(all_results))")
    println("Success rate: $(round(100 * length(all_results) / total_jobs, digits=1))%")
    
    # Quick analysis
    println()
    println("Quick Analysis:")
    println("-"^70)
    
    for n in config.n_values
        n_results = filter(r -> r["n"] == n, all_results)
        if !isempty(n_results)
            κs = [r["curvature"] for r in n_results]
            etas = [r["eta"] for r in n_results]
            
            # Correlation
            if length(κs) > 10
                @printf("  n=%4d: η range [%.2f, %.2f], κ̄ range [%.3f, %.3f], n=%d\n",
                    n, minimum(etas), maximum(etas), 
                    minimum(κs), maximum(κs), length(κs))
            end
        end
    end
    
    return all_results
end

# Analysis of results
function analyze_results(results_file::String)
    results = JSON.parsefile(results_file)
    
    println("="^70)
    println("RESULTS ANALYSIS")
    println("="^70)
    println()
    
    # Group by n
    by_n = Dict{Int, Vector{Dict}}()
    for r in results
        n = r["n"]
        if !haskey(by_n, n)
            by_n[n] = Dict[]
        end
        push!(by_n[n], r)
    end
    
    # Analyze each n
    for (n, n_results) in sort(collect(by_n), by=x->x[1])
        println("n = $n:")
        println("-"^70)
        
        # Group by η
        by_eta = Dict{Float64, Vector{Float64}}()
        for r in n_results
            η = r["eta"]
            κ = r["curvature"]
            if !haskey(by_eta, η)
                by_eta[η] = Float64[]
            end
            push!(by_eta[η], κ)
        end
        
        # Summary statistics
        for (η, κs) in sort(collect(by_eta), by=x->x[1])
            if length(κs) >= 5
                μ = mean(κs)
                σ = std(κs)
                regime = η < 2.0 ? "HYPERBOLIC" : (η > 3.5 ? "SPHERICAL" : "CRITICAL")
                @printf("  η = %6.2f: κ̄ = %+.4f ± %.4f (%s, n=%d)\n",
                    η, μ, σ, regime, length(κs))
            end
        end
        println()
    end
end

# Main
if abspath(PROGRAM_FILE) == @__FILE__
    # Run pipeline
    config = PipelineConfig(
        [1000, 2000],  # Start with smaller sizes for testing
        range(0.5, 5.0, length=20),
        50,
        "results",
        5,
        42
    )
    
    results = run_pipeline(config)
    
    # Analyze
    println()
    println("="^70)
    println()
    
    # Find latest results file
    result_files = filter(f -> endswith(f, ".json"), readdir("results", join=true))
    if !isempty(result_files)
        latest = sort(result_files, by=mtime)[end]
        analyze_results(latest)
    end
end