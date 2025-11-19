#!/usr/bin/env julia
"""
Full pipeline for Paper 1: Hyperbolic Geometry Boundaries

This script reproduces all analyses for the first paper.
"""

using Pkg
Pkg.activate(@__DIR__ / "../..")

push!(LOAD_PATH, joinpath(@__DIR__, "../..", "src"))

using HyperbolicSemanticNetworks
using LightGraphs
using Statistics
using ProgressMeter
using JSON

println("=" ^ 80)
println("PAPER 1: Full Analysis Pipeline")
println("=" ^ 80)
println()

# Step 1: Load data
println("Step 1: Loading data...")
# TODO: Load actual SWOW/ConceptNet data
# For now, create synthetic test data
println("  (Using synthetic data for demonstration)")
println()

# Step 2: Compute curvature
println("Step 2: Computing curvature...")
# Placeholder - would load real data
G = SimpleGraph(100)
for i in 1:99
    add_edge!(G, i, i+1)
end

curvatures = compute_graph_curvature(G, alpha=0.5, parallel=false)
kappa_mean = mean(collect(values(curvatures)))
println("  Mean curvature: $(kappa_mean)")
println()

# Step 3: Generate null models
println("Step 3: Generating null models...")
nulls = generate_null_models(G, method=:configuration, n_samples=100)
println("  Generated $(length(nulls)) null models")
println()

# Step 4: Statistical comparison
println("Step 4: Statistical comparison...")
null_kappas = Float64[]
for null in nulls
    null_c = compute_graph_curvature(null, alpha=0.5, parallel=false)
    push!(null_kappas, mean(collect(values(null_c))))
end

comparison = compare_with_nulls(kappa_mean, null_kappas)
println("  Real vs Null:")
println("    Real κ: $(comparison.real_value)")
println("    Null mean κ: $(comparison.null_mean)")
println("    Effect size: $(comparison.effect_size)")
println("    p-value: $(comparison.p_value)")
println()

# Step 5: Bootstrap analysis
println("Step 5: Bootstrap analysis...")
function curvature_stat(g::SimpleGraph)::Float64
    c = compute_graph_curvature(g, alpha=0.5, parallel=false)
    return mean(collect(values(c)))
end

bootstrap_result = bootstrap_analysis(G, curvature_stat, n_samples=100, sample_size=0.8)
println("  Bootstrap results:")
println("    Mean: $(bootstrap_result.mean)")
println("    95% CI: [$(bootstrap_result.ci_lower), $(bootstrap_result.ci_upper)]")
println()

# Step 6: Ricci flow
println("Step 6: Ricci flow analysis...")
flow_result = ricci_flow(G, max_iterations=10, alpha=0.5)
println("  Converged: $(flow_result.converged)")
println("  Iterations: $(flow_result.iterations)")
println("  Final curvature: $(flow_result.final_curvature)")
println()

# Step 7: Save results
println("Step 7: Saving results...")
results = Dict(
    "kappa_mean" => kappa_mean,
    "null_comparison" => Dict(
        "real_value" => comparison.real_value,
        "null_mean" => comparison.null_mean,
        "effect_size" => comparison.effect_size,
        "p_value" => comparison.p_value
    ),
    "bootstrap" => Dict(
        "mean" => bootstrap_result.mean,
        "ci_lower" => bootstrap_result.ci_lower,
        "ci_upper" => bootstrap_result.ci_upper
    ),
    "ricci_flow" => Dict(
        "converged" => flow_result.converged,
        "iterations" => flow_result.iterations,
        "final_curvature" => flow_result.final_curvature
    )
)

output_dir = joinpath(@__DIR__, "../..", "results", "paper1")
mkpath(output_dir)

output_file = joinpath(output_dir, "analysis_results.json")
open(output_file, "w") do f
    JSON.print(f, results, 2)
end

println("  Results saved to: $(output_file)")
println()

println("=" ^ 80)
println("Pipeline completed!")
println("=" ^ 80)

