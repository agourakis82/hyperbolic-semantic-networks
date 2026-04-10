# Test Strategy

**Date**: 2025-11-08  
**Version**: 1.0  
**Target Coverage**: 90%+

## Overview

Comprehensive testing strategy for the Julia/Rust implementation, ensuring correctness, performance, and reproducibility at Nature-tier standards.

## Test Types

### 1. Unit Tests

**Scope**: Individual functions and modules

**Coverage Target**: 90%+ of all functions

**Examples**:
- Curvature computation for single edge
- Probability measure construction
- Network metric calculations
- Data validation functions

**Location**: `test/test_*.jl`

### 2. Integration Tests

**Scope**: Full pipelines and workflows

**Coverage**: All major workflows

**Examples**:
- Complete curvature computation pipeline
- Null model generation and comparison
- Bootstrap analysis workflow
- Ricci flow computation

**Location**: `test/test_integration.jl`

### 3. Regression Tests

**Scope**: Compare results with Python implementation

**Coverage**: All critical computations

**Examples**:
- Curvature values match Python (within tolerance)
- Null model statistics match
- Bootstrap results match
- Network metrics match

**Location**: `test/test_regression.jl`

### 4. Performance Tests

**Scope**: Benchmark critical operations

**Coverage**: All performance-critical paths

**Examples**:
- Curvature computation speed
- Null model generation speed
- Memory usage
- Scalability

**Location**: `test/test_performance.jl`

### 5. Property-Based Tests

**Scope**: Test invariants and properties

**Coverage**: Mathematical properties

**Examples**:
- Curvature bounds: κ ∈ [-1, 1]
- Network metrics consistency
- Null model degree preservation
- Ricci flow convergence

**Location**: `test/test_properties.jl`

## Test Structure

```
test/
├── test_preprocessing.jl
│   ├── test_load_swow
│   ├── test_load_conceptnet
│   └── test_load_taxonomy
│
├── test_curvature.jl
│   ├── test_compute_edge_curvature
│   ├── test_compute_graph_curvature
│   ├── test_wasserstein_distance
│   └── test_curvature_bounds
│
├── test_null_models.jl
│   ├── test_configuration_model
│   ├── test_triadic_rewire
│   └── test_degree_preservation
│
├── test_analysis.jl
│   ├── test_bootstrap
│   ├── test_ricci_flow
│   └── test_robustness
│
├── test_visualization.jl
│   ├── test_phase_diagram
│   └── test_curvature_plots
│
├── test_integration.jl
│   ├── test_full_pipeline
│   └── test_paper1_workflow
│
├── test_regression.jl
│   ├── test_curvature_equivalence
│   ├── test_null_model_equivalence
│   └── test_metrics_equivalence
│
├── test_performance.jl
│   ├── benchmark_curvature
│   ├── benchmark_null_models
│   └── benchmark_memory
│
└── test_properties.jl
    ├── test_curvature_properties
    └── test_network_properties
```

## Test Framework

### Julia Testing

**Framework**: `Test.jl` (built-in)

**Example**:
```julia
using Test
using HyperbolicSemanticNetworks

@testset "Curvature Computation" begin
    G = create_test_graph()
    
    @test compute_curvature(G, 1, 2) ≈ -0.2 atol=1e-6
    @test -1.0 <= compute_curvature(G, 1, 2) <= 1.0
end
```

### Rust Testing

**Framework**: Built-in `#[test]` attributes

**Example**:
```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_wasserstein_distance() {
        let mu = vec![0.5, 0.5];
        let nu = vec![0.5, 0.5];
        let cost = vec![0.0, 1.0, 1.0, 0.0];
        
        let result = wasserstein1_distance(&mu, &nu, &cost, 0.01);
        assert!((result - 0.0).abs() < 1e-6);
    }
}
```

## Test Data

### Synthetic Test Networks

- Small networks (10-50 nodes) for unit tests
- Medium networks (100-500 nodes) for integration tests
- Large networks (1000+ nodes) for performance tests

### Real Data Samples

- Subset of SWOW data for regression tests
- Known networks with published results

## Validation Criteria

### Numerical Equivalence

- Curvature: Within 1e-6 of Python results
- Network metrics: Within 1e-4
- Statistical tests: p-values within 1e-3

### Performance Targets

- Curvature: 10-100x speedup
- Null models: 5-10x speedup
- Memory: <50% of Python

### Correctness

- All mathematical properties hold
- Edge cases handled correctly
- Error handling works as expected

## Continuous Integration

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: julia-actions/setup-julia@v1
      - run: julia --project=. -e 'using Pkg; Pkg.test()'
      - run: cargo test
```

### Coverage Reporting

- Use `Coverage.jl` for Julia
- Use `cargo-tarpaulin` for Rust
- Target: 90%+ coverage

## Regression Testing

### Python Comparison

1. Run Python implementation on test data
2. Save results as reference
3. Run Julia/Rust implementation
4. Compare results (within tolerance)
5. Report discrepancies

### Test Data Management

- Store reference results in `test/data/`
- Version control test data
- Checksums for validation

## Performance Testing

### Benchmark Suite

- Use `BenchmarkTools.jl` for Julia
- Use `criterion` for Rust
- Track performance over time
- Compare against Python baseline

### Performance Regression

- Fail tests if performance degrades
- Track performance trends
- Alert on significant slowdowns

## Test Execution

### Local Development

```bash
# Run all tests
julia --project=. -e 'using Pkg; Pkg.test()'

# Run specific test file
julia --project=. test/test_curvature.jl

# Run with coverage
julia --project=. --code-coverage test/test_curvature.jl
```

### CI/CD

- Automatic on every push
- Required for merge
- Performance benchmarks on schedule

## Test Maintenance

### Adding New Tests

1. Write test alongside code
2. Ensure coverage >90%
3. Update test documentation
4. Add to CI/CD

### Updating Tests

- Update when API changes
- Maintain backward compatibility tests
- Update regression baselines when needed

## Success Criteria

- [ ] 90%+ code coverage
- [ ] All tests passing
- [ ] Performance targets met
- [ ] Regression tests passing
- [ ] CI/CD green

## Next Steps

1. Set up test infrastructure
2. Write initial test suite
3. Set up CI/CD
4. Begin test-driven development

---

**Status**: Strategy defined, ready for implementation

