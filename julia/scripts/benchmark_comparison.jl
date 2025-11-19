#!/usr/bin/env julia
"""
Benchmark comparison script.

Compares Julia/Rust performance with Python baseline.
"""

using Pkg
Pkg.activate(@__DIR__ / "..")

push!(LOAD_PATH, joinpath(@__DIR__, "..", "src"))

using HyperbolicSemanticNetworks
using LightGraphs
using BenchmarkTools
using Statistics

println("=" ^ 80)
println("PERFORMANCE BENCHMARK COMPARISON")
println("=" ^ 80)
println()

# Test sizes
sizes = [50, 100, 200, 500]

results = Dict()

for size in sizes
    println("Benchmarking network size: $size nodes")
    
    # Create test network
    G = SimpleGraph(size)
    for i in 1:(size-1)
        add_edge!(G, i, i+1)
    end
    # Add some triangles
    for i in 1:min(10, size-2)
        add_edge!(G, i, i+2)
    end
    
    # Benchmark curvature computation
    println("  Curvature computation...")
    bench = @benchmark compute_graph_curvature($G, alpha=0.5, parallel=false)
    
    results[size] = Dict(
        "time_mean" => mean(bench.times) / 1e9,  # seconds
        "time_median" => median(bench.times) / 1e9,
        "time_min" => minimum(bench.times) / 1e9,
        "time_max" => maximum(bench.times) / 1e9,
        "memory" => bench.memory / 1024 / 1024  # MB
    )
    
    println("    Mean: $(results[size]["time_mean"])s")
    println("    Median: $(results[size]["time_median"])s")
    println("    Memory: $(results[size]["memory"]) MB")
    println()
end

# Benchmark null models
println("Benchmarking null model generation...")
G_100 = SimpleGraph(100)
for i in 1:99
    add_edge!(G_100, i, i+1)
end

bench_nulls = @benchmark generate_null_models($G_100, method=:configuration, n_samples=100)
results["null_models"] = Dict(
    "time_mean" => mean(bench_nulls.times) / 1e9,
    "time_median" => median(bench_nulls.times) / 1e9,
    "time_per_replicate" => mean(bench_nulls.times) / 1e9 / 100
)

println("  Mean: $(results["null_models"]["time_mean"])s")
println("  Per replicate: $(results["null_models"]["time_per_replicate"])s")
println()

# Print summary table
println("=" ^ 80)
println("BENCHMARK SUMMARY")
println("=" ^ 80)
println()
println("Curvature Computation:")
println("  Size | Mean (s) | Median (s) | Memory (MB)")
println("  " * "-" ^ 60)
for size in sizes
    r = results[size]
    println("  $size   | $(round(r["time_mean"], digits=3)) | $(round(r["time_median"], digits=3)) | $(round(r["memory"], digits=1))")
end
println()

println("Null Models (100 replicates, 100 nodes):")
r_nulls = results["null_models"]
println("  Total time: $(round(r_nulls["time_mean"], digits=3))s")
println("  Per replicate: $(round(r_nulls["time_per_replicate"], digits=4))s")
println()

# Compare with Python baseline (if available)
println("=" ^ 80)
println("COMPARISON WITH PYTHON BASELINE")
println("=" ^ 80)
println("(Python baseline benchmarks would be loaded from benchmarks/baseline_python/)")
println()

# Save results
using JSON
output_file = joinpath(@__DIR__, "../..", "benchmarks", "julia_rust_benchmarks.json")
mkpath(dirname(output_file))

open(output_file, "w") do f
    JSON.print(f, results, 2)
end

println("Results saved to: $output_file")
println()
println("=" ^ 80)
println("Benchmarking complete!")
println("=" ^ 80)

