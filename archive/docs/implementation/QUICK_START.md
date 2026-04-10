# Quick Start Guide

**Date**: 2025-11-08

## Installation

### Prerequisites

- Julia 1.9+
- Rust toolchain (stable)
- Python 3.10+ (for baseline comparison)

### Setup

```bash
# 1. Install Julia dependencies
cd julia
julia --project=. -e 'using Pkg; Pkg.instantiate()'
cd ..

# 2. Build Rust libraries
cd rust
cargo build --release
cd ..

# Or use the build script
./scripts/build_rust_libs.sh
```

## Basic Usage

### Example 1: Compute Curvature

```julia
using HyperbolicSemanticNetworks
using LightGraphs

# Create a graph
G = SimpleGraph(10)
add_edge!(G, 1, 2)
add_edge!(G, 2, 3)
# ... add more edges

# Compute curvature
curvatures = compute_graph_curvature(G, alpha=0.5)
kappa_mean = mean(collect(values(curvatures)))
println("Mean curvature: $kappa_mean")
```

### Example 2: Null Models

```julia
# Generate null models
nulls = generate_null_models(G, method=:configuration, n_samples=1000)

# Compare
real_kappa = mean(collect(values(compute_graph_curvature(G))))
null_kappas = [mean(collect(values(compute_graph_curvature(n)))) for n in nulls]

comparison = compare_with_nulls(real_kappa, null_kappas)
println("Effect size: $(comparison.effect_size)")
println("p-value: $(comparison.p_value)")
```

### Example 3: Bootstrap

```julia
# Bootstrap analysis
function curvature_stat(g::SimpleGraph)
    c = compute_graph_curvature(g)
    return mean(collect(values(c)))
end

result = bootstrap_analysis(G, curvature_stat, n_samples=1000)
println("Mean: $(result.mean)")
println("95% CI: [$(result.ci_lower), $(result.ci_upper)]")
```

## Running Examples

```bash
# Run example script
julia --project=julia julia/scripts/example_usage.jl

# Run full pipeline
julia --project=julia julia/scripts/paper1/full_pipeline.jl
```

## Testing

```bash
# Run all tests
make test-julia

# Or directly
julia --project=julia test/runtests.jl
```

## Troubleshooting

### Rust Library Not Found

If you see warnings about Rust library not found:
1. Build the library: `cargo build --release`
2. Check the library is in `rust/target/release/`
3. The Julia code will automatically fall back to a Julia implementation

### Module Not Found

Make sure you're in the correct directory and have activated the project:
```julia
using Pkg
Pkg.activate("julia")
```

---

**For more details, see `docs/REPRODUCIBILITY.md`**

