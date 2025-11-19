#!/usr/bin/env julia
"""
Example usage script for HyperbolicSemanticNetworks.jl

Demonstrates basic usage of the package.
"""

using Pkg
Pkg.activate(@__DIR__ / "..")

# Add src to path
push!(LOAD_PATH, joinpath(@__DIR__, "..", "src"))

using HyperbolicSemanticNetworks
using LightGraphs

println("=" ^ 80)
println("HyperbolicSemanticNetworks.jl - Example Usage")
println("=" ^ 80)
println()

# Example 1: Create a simple test graph
println("Example 1: Creating test graph...")
G = SimpleGraph(10)
for i in 1:9
    add_edge!(G, i, i+1)
end
add_edge!(G, 1, 10)  # Close the cycle
add_edge!(G, 1, 5)   # Add a chord

println("  Graph: $(nv(G)) nodes, $(ne(G)) edges")
println()

# Example 2: Compute network metrics
println("Example 2: Computing network metrics...")
metrics = network_metrics(G)
println("  Clustering: $(metrics.clustering)")
println("  Degree std: $(metrics.degree_std)")
println("  Path length: $(metrics.path_length)")
println()

# Example 3: Compute curvature
println("Example 3: Computing curvature...")
curvatures = compute_graph_curvature(G, alpha=0.5, parallel=false)
kappa_mean = mean(collect(values(curvatures)))
println("  Mean curvature: $(kappa_mean)")
println("  Number of edges: $(length(curvatures))")
println()

# Example 4: Generate null models
println("Example 4: Generating null models...")
nulls = generate_null_models(G, method=:configuration, n_samples=10)
println("  Generated $(length(nulls)) null models")
println()

# Example 5: Compare with nulls
println("Example 5: Comparing with null models...")
null_kappas = Float64[]
for null in nulls
    null_c = compute_graph_curvature(null, alpha=0.5, parallel=false)
    push!(null_kappas, mean(collect(values(null_c))))
end

comparison = compare_with_nulls(kappa_mean, null_kappas)
println("  Real κ: $(comparison.real_value)")
println("  Null mean κ: $(comparison.null_mean)")
println("  Effect size: $(comparison.effect_size)")
println("  p-value: $(comparison.p_value)")
println()

# Example 6: Bootstrap analysis
println("Example 6: Bootstrap analysis...")
function mean_degree_stat(g::SimpleGraph)::Float64
    degrees = [degree(g, v) for v in vertices(g)]
    return mean(degrees)
end

bootstrap_result = bootstrap_analysis(G, mean_degree_stat, n_samples=50, sample_size=0.8)
println("  Bootstrap mean: $(bootstrap_result.mean)")
println("  95% CI: [$(bootstrap_result.ci_lower), $(bootstrap_result.ci_upper)]")
println()

println("=" ^ 80)
println("Examples completed!")
println("=" ^ 80)

