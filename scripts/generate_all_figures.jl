#!/usr/bin/env julia
"""
Generate all figures for Paper 1.

Creates publication-quality figures for the manuscript.
"""

using Pkg
Pkg.activate(@__DIR__ / "../..")

push!(LOAD_PATH, joinpath(@__DIR__, "../..", "src"))

using HyperbolicSemanticNetworks
using LightGraphs
using Statistics
using Plots

println("=" ^ 80)
println("GENERATING ALL FIGURES FOR PAPER 1")
println("=" ^ 80)
println()

output_dir = joinpath(@__DIR__, "../..", "figures", "paper1")
mkpath(output_dir)

# Figure 1: Clustering-Curvature Map
println("Generating Figure 1: Clustering-Curvature Map...")

# Create synthetic networks with different clustering
networks = []
for c_target in [0.01, 0.05, 0.10, 0.15, 0.20, 0.30]
    # Create network with target clustering (simplified)
    G = SimpleGraph(100)
    # Add structure to approximate target clustering
    for i in 1:99
        add_edge!(G, i, i+1)
    end
    # Add triangles to increase clustering
    triangles_to_add = Int(round(c_target * 100))
    for _ in 1:triangles_to_add
        u = rand(1:100)
        v = rand(1:100)
        w = rand(1:100)
        if u != v != w && u != w
            add_edge!(G, u, v)
            add_edge!(G, v, w)
            add_edge!(G, w, u)
        end
    end
    
    metrics = network_metrics(G)
    curvatures = compute_graph_curvature(G, alpha=0.5, parallel=false)
    kappa_mean = mean(collect(values(curvatures)))
    
    push!(networks, Dict(
        "clustering" => metrics.clustering,
        "degree_std" => metrics.degree_std,
        "curvature_mean" => kappa_mean
    ))
end

clustering_vals = [n["clustering"] for n in networks]
curvature_vals = [n["curvature_mean"] for n in networks]

p1 = plot_clustering_curvature_relationship(clustering_vals, curvature_vals)
savefig(p1, joinpath(output_dir, "figure1_clustering_curvature.png"))
println("  ✅ Saved: figure1_clustering_curvature.png")
println()

# Figure 2: Null Model Comparisons
println("Generating Figure 2: Null Model Comparisons...")

G = SimpleGraph(100)
for i in 1:99
    add_edge!(G, i, i+1)
end

real_curvatures = compute_graph_curvature(G, alpha=0.5, parallel=false)
real_kappa = mean(collect(values(real_curvatures)))

nulls = generate_null_models(G, method=:configuration, n_samples=100)
null_kappas = Float64[]
for null in nulls
    null_c = compute_graph_curvature(null, alpha=0.5, parallel=false)
    push!(null_kappas, mean(collect(values(null_c))))
end

p2 = plot_null_model_comparison(real_kappa, null_kappas)
savefig(p2, joinpath(output_dir, "figure2_null_comparison.png"))
println("  ✅ Saved: figure2_null_comparison.png")
println()

# Figure 3: Ricci Flow Trajectories
println("Generating Figure 3: Ricci Flow Trajectories...")

G = SimpleGraph(50)
for i in 1:49
    add_edge!(G, i, i+1)
end

flow_result = ricci_flow(G, max_iterations=20, alpha=0.5)
p3 = plot_ricci_flow_trajectory(flow_result.trajectory)
savefig(p3, joinpath(output_dir, "figure3_ricci_flow.png"))
println("  ✅ Saved: figure3_ricci_flow.png")
println()

# Figure 4: Phase Diagram
println("Generating Figure 4: Phase Diagram...")

p4 = create_phase_diagram(networks)
savefig(p4, joinpath(output_dir, "figure4_phase_diagram.png"))
println("  ✅ Saved: figure4_phase_diagram.png")
println()

println("=" ^ 80)
println("All figures generated!")
println("Output directory: $output_dir")
println("=" ^ 80)

