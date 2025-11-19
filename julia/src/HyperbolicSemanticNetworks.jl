"""
HyperbolicSemanticNetworks.jl

Main module for hyperbolic geometry analysis of semantic networks.

Author: Dr. Demetrios Agourakis
Date: 2025-11-08
Version: 0.1.0
"""

module HyperbolicSemanticNetworks

# Export public API
export
    # Preprocessing
    load_swow, load_conceptnet, load_taxonomy,
    
    # Curvature
    compute_curvature, compute_graph_curvature,
    
    # Analysis
    generate_null_models, bootstrap_analysis, ricci_flow,
    
    # Visualization
    plot_phase_diagram, plot_curvature_distribution,
    plot_clustering_curvature_relationship, plot_ricci_flow_trajectory,
    plot_null_model_comparison, create_phase_diagram,
    
    # Utilities
    network_metrics, validate_graph

# Import dependencies
using LightGraphs
using DataFrames
using CSV
using JSON
using Statistics
using LinearAlgebra
using Random
using ProgressMeter
using Logging

# Include submodules
include("Preprocessing/SWOW.jl")
include("Preprocessing/ConceptNet.jl")
include("Preprocessing/Taxonomies.jl")

# Curvature module - FFI must be included first, then OllivierRicci can use it
include("Curvature/FFI.jl")
include("Curvature/OllivierRicci.jl")

include("Analysis/NullModels.jl")
include("Analysis/Bootstrap.jl")
include("Analysis/RicciFlow.jl")
include("Visualization/Figures.jl")
include("Visualization/PhaseDiagram.jl")
include("Utils/Metrics.jl")
include("Utils/IO.jl")
include("Utils/Validation.jl")

end # module
