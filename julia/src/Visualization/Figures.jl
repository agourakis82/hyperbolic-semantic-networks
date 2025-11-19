"""
Figures.jl - Publication-quality figure generation

Generate figures for papers using Plots.jl.
"""

using Plots
using Statistics
using LightGraphs

"""
    plot_phase_diagram(results::Vector; output_file::Union{String, Nothing}=nothing)

Generate phase diagram (C vs σ_k).

# Arguments
- `results`: Vector of network results with clustering and degree_std
- `output_file`: Optional file path to save figure

# Returns
- Plot object
"""
function plot_phase_diagram(
    results::Vector;
    output_file::Union{String, Nothing} = nothing
)
    # Extract data
    clustering = [r.clustering for r in results]
    degree_std = [r.degree_std for r in results]
    curvature = [r.curvature_mean for r in results]
    
    # Create scatter plot with color coding by curvature
    p = scatter(
        clustering,
        degree_std,
        zcolor = curvature,
        color = :viridis,
        xlabel = "Clustering Coefficient (C)",
        ylabel = "Degree Std (σ_k)",
        title = "Phase Diagram: Network Geometry",
        colorbar_title = "Mean Curvature (κ)",
        markersize = 8,
        alpha = 0.7
    )
    
    # Add region boundaries (placeholder - would need actual boundaries)
    # vline!([0.02, 0.15], linestyle=:dash, color=:gray, alpha=0.5, label="Hyperbolic sweet spot")
    
    if output_file !== nothing
        savefig(p, output_file)
    end
    
    return p
end

"""
    plot_curvature_distribution(curvatures::Dict{Tuple{Int, Int}, Float64}; output_file::Union{String, Nothing}=nothing)

Plot curvature distribution.

# Arguments
- `curvatures`: Dictionary mapping edges to curvature values
- `output_file`: Optional file path to save figure

# Returns
- Plot object
"""
function plot_curvature_distribution(
    curvatures::Dict{Tuple{Int, Int}, Float64};
    output_file::Union{String, Nothing} = nothing
)
    values = collect(values(curvatures))
    
    p = histogram(
        values,
        bins = 50,
        xlabel = "Ollivier-Ricci Curvature (κ)",
        ylabel = "Frequency",
        title = "Curvature Distribution",
        alpha = 0.7,
        color = :steelblue
    )
    
    # Add vertical line at mean
    vline!([mean(values)], linestyle=:dash, color=:red, linewidth=2, label="Mean")
    
    if output_file !== nothing
        savefig(p, output_file)
    end
    
    return p
end

"""
    plot_clustering_curvature_relationship(clustering::Vector{Float64}, curvature::Vector{Float64}; output_file::Union{String, Nothing}=nothing)

Plot relationship between clustering and curvature.

# Arguments
- `clustering`: Clustering coefficient values
- `curvature`: Mean curvature values
- `output_file`: Optional file path to save figure

# Returns
- Plot object
"""
function plot_clustering_curvature_relationship(
    clustering::Vector{Float64},
    curvature::Vector{Float64};
    output_file::Union{String, Nothing} = nothing
)
    p = scatter(
        clustering,
        curvature,
        xlabel = "Clustering Coefficient (C)",
        ylabel = "Mean Curvature (κ)",
        title = "Clustering-Curvature Relationship",
        markersize = 6,
        alpha = 0.6,
        color = :steelblue
    )
    
    # Add trend line (simple linear fit)
    if length(clustering) > 1
        # Simple linear regression
        coeffs = [ones(length(clustering)) clustering] \ curvature
        x_fit = range(minimum(clustering), maximum(clustering), length=100)
        y_fit = coeffs[1] .+ coeffs[2] .* x_fit
        plot!(x_fit, y_fit, linestyle=:dash, color=:red, linewidth=2, label="Trend")
    end
    
    # Highlight "sweet spot" region
    vspan!([0.02, 0.15], alpha=0.2, color=:yellow, label="Hyperbolic sweet spot")
    
    if output_file !== nothing
        savefig(p, output_file)
    end
    
    return p
end

"""
    plot_ricci_flow_trajectory(trajectory::Vector{Dict{String, Float64}}; output_file::Union{String, Nothing}=nothing)

Plot Ricci flow trajectory.

# Arguments
- `trajectory`: Vector of state dictionaries from ricci_flow
- `output_file`: Optional file path to save figure

# Returns
- Plot object
"""
function plot_ricci_flow_trajectory(
    trajectory::Vector{Dict{String, Float64}};
    output_file::Union{String, Nothing} = nothing
)
    iterations = [t["iteration"] for t in trajectory]
    clustering = [t["clustering"] for t in trajectory]
    curvature = [t["curvature_mean"] for t in trajectory]
    
    p = plot(
        iterations,
        [clustering, curvature],
        label = ["Clustering (C)" "Curvature (κ)"],
        xlabel = "Iteration",
        ylabel = "Value",
        title = "Ricci Flow Trajectory",
        linewidth = 2,
        alpha = 0.8
    )
    
    if output_file !== nothing
        savefig(p, output_file)
    end
    
    return p
end

"""
    plot_null_model_comparison(real_value::Float64, null_values::Vector{Float64}; output_file::Union{String, Nothing}=nothing)

Plot comparison of real value vs null model distribution.

# Arguments
- `real_value`: Real network value
- `null_values`: Null model values
- `output_file`: Optional file path to save figure

# Returns
- Plot object
"""
function plot_null_model_comparison(
    real_value::Float64,
    null_values::Vector{Float64};
    output_file::Union{String, Nothing} = nothing
)
    p = histogram(
        null_values,
        bins = 30,
        xlabel = "Value",
        ylabel = "Frequency",
        title = "Real vs Null Models",
        alpha = 0.6,
        color = :lightblue,
        label = "Null Models"
    )
    
    # Add vertical line for real value
    vline!([real_value], linestyle=:solid, color=:red, linewidth=3, label="Real")
    
    # Add mean of nulls
    vline!([mean(null_values)], linestyle=:dash, color=:blue, linewidth=2, label="Null Mean")
    
    if output_file !== nothing
        savefig(p, output_file)
    end
    
    return p
end
