"""
PhaseDiagram.jl - Phase diagram generation

Generate phase diagrams showing geometry regimes.
"""

using Plots
using Statistics

"""
    create_phase_diagram(
        networks::Vector;
        output_file::Union{String, Nothing} = nothing
    )

Create phase diagram from multiple networks.

# Arguments
- `networks`: Vector of network results (with clustering, degree_std, curvature_mean)
- `output_file`: Optional file path to save figure

# Returns
- Plot object
"""
function create_phase_diagram(
    networks::Vector;
    output_file::Union{String, Nothing} = nothing
)
    # Extract data
    C = [n.clustering for n in networks]
    sigma_k = [n.degree_std for n in networks]
    kappa = [n.curvature_mean for n in networks]
    
    # Create phase diagram
    p = scatter(
        C,
        sigma_k,
        zcolor = kappa,
        color = :RdYlBu,
        xlabel = "Clustering Coefficient (C)",
        ylabel = "Degree Heterogeneity (σ_k)",
        title = "Phase Diagram: Network Geometry",
        colorbar_title = "Mean Curvature (κ)",
        markersize = 10,
        alpha = 0.8,
        legend = false
    )
    
    # Add region boundaries (approximate)
    # Hyperbolic region: C ≈ 0.02-0.15
    vspan!([0.02, 0.15], alpha=0.1, color=:yellow, label="Hyperbolic sweet spot")
    
    # Add annotations for regions
    annotate!(0.08, maximum(sigma_k) * 0.9, text("Hyperbolic", :center, :bottom, 10))
    annotate!(0.001, maximum(sigma_k) * 0.5, text("Euclidean", :center, :bottom, 10))
    annotate!(0.3, maximum(sigma_k) * 0.5, text("Spherical", :center, :bottom, 10))
    
    if output_file !== nothing
        savefig(p, output_file)
    end
    
    return p
end

