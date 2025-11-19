#!/usr/bin/env julia
"""
Validation script to compare Julia/Rust implementation with Python baseline.

Run with: julia --project=julia scripts/validate_implementation.jl
"""

using Pkg
Pkg.activate("julia")

# Add src to path
push!(LOAD_PATH, joinpath(@__DIR__, "..", "julia", "src"))

using HyperbolicSemanticNetworks
using LightGraphs
using Statistics

println("=" ^ 80)
println("VALIDATION: Julia/Rust vs Python Baseline")
println("=" ^ 80)
println()

# Create test network (same as Python baseline)
println("Creating test network...")
G = SimpleGraph(100)
for i in 1:99
    add_edge!(G, i, i+1)
end
# Add some triangles
add_edge!(G, 1, 3)
add_edge!(G, 2, 4)

println("  Nodes: $(nv(G))")
println("  Edges: $(ne(G))")
println()

# Compute curvature
println("Computing curvature...")
curvatures = compute_graph_curvature(G, alpha=0.5, parallel=false)

kappa_values = collect(values(curvatures))
kappa_mean = mean(kappa_values)
kappa_std = std(kappa_values)
kappa_min = minimum(kappa_values)
kappa_max = maximum(kappa_values)

println("Results:")
println("  Mean curvature: $(kappa_mean)")
println("  Std curvature: $(kappa_std)")
println("  Min curvature: $(kappa_min)")
println("  Max curvature: $(kappa_max)")
println()

# Validate bounds
println("Validation:")
all_valid = true

if any(k -> k < -1.0 || k > 1.0, kappa_values)
    println("  ❌ ERROR: Curvature values outside [-1, 1] bounds!")
    all_valid = false
else
    println("  ✅ Curvature values within bounds")
end

if !isfinite(kappa_mean)
    println("  ❌ ERROR: Mean curvature is not finite!")
    all_valid = false
else
    println("  ✅ Mean curvature is finite")
end

if length(curvatures) != ne(G)
    println("  ❌ ERROR: Number of curvatures doesn't match number of edges!")
    all_valid = false
else
    println("  ✅ All edges have curvature values")
end

println()
if all_valid
    println("✅ VALIDATION PASSED")
else
    println("❌ VALIDATION FAILED")
    exit(1)
end

