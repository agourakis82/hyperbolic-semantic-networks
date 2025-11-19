# Architecture Design Document

**Date**: 2025-11-08  
**Version**: 1.0  
**Status**: Design Phase

## Executive Summary

This document defines the complete architecture for the Julia/Rust implementation of the hyperbolic semantic networks analysis pipeline. The design prioritizes performance, modularity, testability, and reproducibility at Nature-tier standards.

## System Overview

### Architecture Principles

1. **Modularity**: Clear separation of concerns, reusable components
2. **Performance**: Julia for high-level logic, Rust for critical computations
3. **Type Safety**: Strong typing in both Julia and Rust
4. **Testability**: Comprehensive test coverage (90%+ target)
5. **Reproducibility**: Deterministic, version-locked, containerized
6. **Extensibility**: Support for multiple papers and future research

### Technology Stack

- **Primary Language**: Julia 1.9+
- **Performance-Critical**: Rust (via FFI)
- **Graph Library**: LightGraphs.jl (Julia), petgraph (Rust)
- **Data**: DataFrames.jl, CSV.jl
- **Visualization**: Plots.jl, PlotlyJS.jl
- **Testing**: Test.jl, Criterion (Rust)

## Module Structure

```
src/
├── HyperbolicSemanticNetworks.jl    # Main module, exports public API
│
├── Preprocessing/
│   ├── SWOW.jl                       # SWOW data loader
│   ├── ConceptNet.jl                 # ConceptNet loader
│   └── Taxonomies.jl                 # WordNet/BabelNet loaders
│
├── Curvature/
│   ├── OllivierRicci.jl              # High-level API (Julia)
│   ├── Forman.jl                     # Forman curvature (optional)
│   └── Wasserstein.jl                # Wasserstein distance utilities
│
├── Analysis/
│   ├── NullModels.jl                 # Configuration, triadic-rewire
│   ├── Bootstrap.jl                  # Bootstrap resampling
│   ├── Robustness.jl                  # Sensitivity analysis
│   └── RicciFlow.jl                  # Discrete Ricci flow
│
├── Visualization/
│   ├── Figures.jl                    # Publication-quality figures
│   ├── PhaseDiagram.jl               # Phase diagram generation
│   └── Trajectories.jl               # Ricci flow trajectories
│
└── Utils/
    ├── Metrics.jl                    # Network metrics (C, σ_k, etc.)
    ├── IO.jl                         # File I/O utilities
    └── Validation.jl                 # Data validation
```

## Rust Components

### Performance-Critical Rust Crates

```
rust/
├── curvature/
│   ├── Cargo.toml
│   └── src/
│       ├── lib.rs                   # FFI interface
│       ├── wasserstein.rs           # Wasserstein-1 distance
│       └── sinkhorn.rs              # Sinkhorn algorithm (parallel)
│
└── null_models/
    ├── Cargo.toml
    └── src/
        ├── lib.rs                   # FFI interface
        ├── configuration.rs         # Configuration model
        └── triadic_rewire.rs       # Triadic-rewire (parallel)
```

## API Design

### High-Level API (Julia)

```julia
# Main module
using HyperbolicSemanticNetworks

# Load data
swow_graph = load_swow("data/raw/swow_en.csv")

# Compute curvature
curvatures = compute_curvature(swow_graph, alpha=0.5)

# Null models
nulls = generate_null_models(swow_graph, method=:configuration, n=1000)

# Analysis
results = analyze_geometry(swow_graph, nulls)

# Visualization
plot_phase_diagram(results)
```

### Low-Level API (Rust FFI)

```rust
// Wasserstein-1 distance
pub fn wasserstein1_distance(
    mu: &[f64],
    nu: &[f64],
    cost_matrix: &[f64],
    epsilon: f64,
) -> f64;

// Configuration model
pub fn configuration_model(
    degrees: &[usize],
    n_samples: usize,
) -> Vec<Graph>;
```

## Data Flow

### Curvature Computation Pipeline

```
Input Data (CSV/JSON)
    ↓
Preprocessing (Julia)
    ↓
Graph Construction (LightGraphs.jl)
    ↓
Curvature Computation
    ├── Probability Measures (Julia)
    ├── Wasserstein-1 (Rust) ← Performance critical
    └── Edge Curvature (Julia)
    ↓
Results (DataFrame/JSON)
```

### Null Model Pipeline

```
Real Network
    ↓
Null Model Generation
    ├── Configuration (Rust) ← Parallel
    └── Triadic-rewire (Rust) ← Parallel
    ↓
Statistical Comparison (Julia)
    ↓
Results (DataFrame/JSON)
```

## Performance Design

### Optimization Strategies

1. **Parallelization**
   - Edge curvature: Parallel processing
   - Null models: Parallel replicate generation
   - Bootstrap: Parallel resampling

2. **Memory Efficiency**
   - Sparse matrices for large graphs
   - Streaming for large datasets
   - Efficient graph representations

3. **Caching**
   - Probability measures
   - Shortest paths
   - Computed metrics

4. **Algorithm Optimization**
   - Optimized Sinkhorn (Rust)
   - Early stopping in Ricci flow
   - Incremental updates

### Performance Targets

| Operation | Python (baseline) | Julia/Rust (target) | Speedup |
|-----------|------------------|---------------------|---------|
| Curvature (500 nodes) | 50-100s | 5-10s | 10x |
| Curvature (1000 nodes) | 400-800s | 30-60s | 10-20x |
| Null models (M=1000) | 600s | 60s | 10x |
| Memory (1000 nodes) | 8-16 GB | 2-4 GB | 4x |

## Error Handling

### Error Types

```julia
abstract type HSNError <: Exception end

struct DataLoadError <: HSNError
    message::String
    file::String
end

struct ComputationError <: HSNError
    message::String
    operation::String
end

struct ValidationError <: HSNError
    message::String
    field::String
end
```

### Error Handling Strategy

- **Fail Fast**: Validate inputs early
- **Clear Messages**: Descriptive error messages
- **Recovery**: Graceful degradation where possible
- **Logging**: Comprehensive logging for debugging

## Testing Strategy

### Test Structure

```
test/
├── test_preprocessing.jl
├── test_curvature.jl
├── test_null_models.jl
├── test_analysis.jl
├── test_visualization.jl
├── test_integration.jl
└── test_performance.jl
```

### Test Types

1. **Unit Tests**: Individual functions
2. **Integration Tests**: Full pipelines
3. **Regression Tests**: Compare with Python
4. **Performance Tests**: Benchmarks
5. **Property Tests**: Invariants

### Coverage Target

- **Overall**: 90%+
- **Critical paths**: 100%
- **Public API**: 100%

## Reproducibility

### Version Control

- `Project.toml`: Dependency specifications
- `Manifest.toml`: Exact versions (locked)
- `Cargo.lock`: Rust dependency versions

### Environment

- Docker container with all dependencies
- `RUNME.md`: Step-by-step reproduction guide
- Checksums for all data files

### Documentation

- API documentation (auto-generated)
- Tutorial notebooks
- Code examples
- Architecture diagrams

## Migration Strategy

### Incremental Migration

1. **Phase 1**: Core infrastructure (Julia setup, Rust setup)
2. **Phase 2**: Preprocessing (data loaders)
3. **Phase 3**: Curvature computation (critical path)
4. **Phase 4**: Analysis modules
5. **Phase 5**: Visualization
6. **Phase 6**: Integration and testing

### Parallel Development

- Keep Python codebase working
- Migrate module by module
- Validate each module against Python
- Incremental performance testing

## Next Steps

1. Set up Julia project structure
2. Set up Rust workspace
3. Implement FFI bindings
4. Begin with preprocessing modules
5. Migrate curvature computation (critical path)

---

**Status**: Design complete, ready for implementation

