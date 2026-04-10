# API Specification

**Date**: 2025-11-08  
**Version**: 1.0

## Overview

This document specifies the public API for the HyperbolicSemanticNetworks.jl package, including function signatures, types, and behavior.

## Main Module

### `HyperbolicSemanticNetworks`

Main module that exports all public APIs.

```julia
module HyperbolicSemanticNetworks

export
    # Preprocessing
    load_swow, load_conceptnet, load_taxonomy,
    
    # Curvature
    compute_curvature, compute_graph_curvature,
    
    # Analysis
    generate_null_models, bootstrap_analysis, ricci_flow,
    
    # Visualization
    plot_phase_diagram, plot_curvature_distribution,
    
    # Utilities
    network_metrics, validate_graph

end
```

## Preprocessing API

### `load_swow`

Load SWOW association data.

```julia
function load_swow(
    filepath::String;
    language::String = "english",
    max_nodes::Union{Int, Nothing} = nothing,
    min_weight::Float64 = 0.0
) -> LightGraphs.SimpleGraph
```

**Parameters**:
- `filepath`: Path to SWOW CSV file
- `language`: Language code (optional)
- `max_nodes`: Maximum nodes to load (optional)
- `min_weight`: Minimum edge weight threshold

**Returns**: `SimpleGraph` with edge weights

**Errors**: `DataLoadError` if file not found or invalid

### `load_conceptnet`

Load ConceptNet knowledge graph.

```julia
function load_conceptnet(
    filepath::String;
    language::String = "en",
    relation_types::Vector{String} = ["RelatedTo"]
) -> LightGraphs.SimpleGraph
```

### `load_taxonomy`

Load taxonomy (WordNet/BabelNet).

```julia
function load_taxonomy(
    filepath::String;
    taxonomy_type::String = "wordnet",
    language::String = "en"
) -> LightGraphs.SimpleGraph
```

## Curvature API

### `compute_curvature`

Compute Ollivier-Ricci curvature for a single edge.

```julia
function compute_curvature(
    graph::SimpleGraph,
    u::Int,
    v::Int;
    alpha::Float64 = 0.5,
    weights::Union{Dict{Tuple{Int, Int}, Float64}, Nothing} = nothing
) -> Float64
```

**Parameters**:
- `graph`: Input graph
- `u`, `v`: Edge endpoints
- `alpha`: Idleness parameter (default 0.5)
- `weights`: Edge weights dictionary (optional)

**Returns**: Curvature value κ(u,v) ∈ [-1, 1]

**Errors**: `ComputationError` if edge doesn't exist

### `compute_graph_curvature`

Compute curvature for all edges in graph.

```julia
function compute_graph_curvature(
    graph::SimpleGraph;
    alpha::Float64 = 0.5,
    weights::Union{Dict{Tuple{Int, Int}, Float64}, Nothing} = nothing,
    parallel::Bool = true
) -> Dict{Tuple{Int, Int}, Float64}
```

**Parameters**:
- `graph`: Input graph
- `alpha`: Idleness parameter
- `weights`: Edge weights
- `parallel`: Use parallel processing (default true)

**Returns**: Dictionary mapping (u, v) → κ(u, v)

**Performance**: Parallel processing recommended for large graphs

## Analysis API

### `generate_null_models`

Generate null model networks.

```julia
function generate_null_models(
    graph::SimpleGraph;
    method::Symbol = :configuration,
    n_samples::Int = 1000,
    parallel::Bool = true
) -> Vector{SimpleGraph}
```

**Parameters**:
- `graph`: Input graph
- `method`: `:configuration` or `:triadic_rewire`
- `n_samples`: Number of null model replicates
- `parallel`: Use parallel generation

**Returns**: Vector of null model graphs

**Performance**: Uses Rust backend for parallel generation

### `bootstrap_analysis`

Bootstrap resampling analysis.

```julia
function bootstrap_analysis(
    graph::SimpleGraph,
    statistic::Function;
    n_samples::Int = 1000,
    sample_size::Float64 = 0.8,
    parallel::Bool = true
) -> BootstrapResult
```

**Returns**: `BootstrapResult` with mean, std, confidence intervals

### `ricci_flow`

Compute discrete Ricci flow.

```julia
function ricci_flow(
    graph::SimpleGraph;
    alpha::Float64 = 0.5,
    eta::Float64 = 0.5,
    max_iterations::Int = 40,
    tolerance::Float64 = 1e-6
) -> RicciFlowResult
```

**Returns**: `RicciFlowResult` with trajectory and convergence info

## Visualization API

### `plot_phase_diagram`

Generate phase diagram (C vs σ_k).

```julia
function plot_phase_diagram(
    results::Vector{NetworkResult};
    output_file::Union{String, Nothing} = nothing
) -> Plots.Plot
```

### `plot_curvature_distribution`

Plot curvature distribution.

```julia
function plot_curvature_distribution(
    curvatures::Dict{Tuple{Int, Int}, Float64};
    output_file::Union{String, Nothing} = nothing
) -> Plots.Plot
```

## Utility API

### `network_metrics`

Compute network metrics.

```julia
function network_metrics(
    graph::SimpleGraph;
    weights::Union{Dict{Tuple{Int, Int}, Float64}, Nothing} = nothing
) -> NetworkMetrics
```

**Returns**: `NetworkMetrics` with C, σ_k, L, Q, etc.

### `validate_graph`

Validate graph structure.

```julia
function validate_graph(
    graph::SimpleGraph;
    check_connected::Bool = true,
    check_weights::Bool = true
) -> ValidationResult
```

**Returns**: `ValidationResult` with validation status and errors

## Type Definitions

```julia
struct NetworkMetrics
    n_nodes::Int
    n_edges::Int
    clustering::Float64
    degree_std::Float64
    path_length::Float64
    modularity::Float64
end

struct BootstrapResult
    mean::Float64
    std::Float64
    ci_lower::Float64
    ci_upper::Float64
    samples::Vector{Float64}
end

struct RicciFlowResult
    trajectory::Vector{Dict{String, Float64}}
    converged::Bool
    iterations::Int
    final_curvature::Float64
end
```

## Error Handling

All functions that can fail return results or throw specific error types:

- `DataLoadError`: File I/O issues
- `ComputationError`: Computational failures
- `ValidationError`: Input validation failures

## Performance Guarantees

- Curvature computation: O(n²) to O(n³) depending on graph structure
- Null models: O(M × n) where M is number of replicates
- Bootstrap: O(B × n) where B is number of bootstrap samples

## Next Steps

1. Implement API contracts
2. Write comprehensive tests
3. Generate API documentation
4. Create usage examples

---

**Status**: Specification complete, ready for implementation

