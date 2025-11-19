# Performance Benchmarks

**Date**: 2025-11-08  
**Status**: Benchmark Framework Ready

## Overview

This document tracks performance benchmarks comparing the Julia/Rust implementation with the Python baseline.

## Benchmark Framework

### Python Baseline

Run to establish baseline:
```bash
python tools/audit/baseline_benchmarks.py
```

Results saved to: `benchmarks/baseline_python/baseline_benchmarks.json`

### Julia/Rust Benchmarks

Run to benchmark Julia/Rust implementation:
```bash
julia --project=julia julia/scripts/benchmark_comparison.jl
```

Results saved to: `benchmarks/julia_rust_benchmarks.json`

### Comparison

Compare results:
```bash
python scripts/compare_with_python.py
```

## Expected Performance Gains

### Curvature Computation

| Network Size | Python (baseline) | Julia/Rust (target) | Speedup Target |
|--------------|-------------------|---------------------|----------------|
| 100 nodes    | ~2-5s             | ~0.2-0.5s           | 10x            |
| 500 nodes    | ~50-100s          | ~5-10s              | 10x            |
| 1000 nodes   | ~400-800s         | ~30-60s             | 10-20x         |

### Null Model Generation

| Method           | Python (baseline) | Julia/Rust (target) | Speedup Target |
|------------------|-------------------|---------------------|----------------|
| Configuration    | ~600s (M=1000)    | ~60s (M=1000)       | 10x            |
| Triadic-rewire   | ~3000s (M=1000)   | ~300s (M=1000)      | 10x            |

### Memory Usage

| Network Size | Python (baseline) | Julia/Rust (target) | Reduction Target |
|--------------|-------------------|---------------------|------------------|
| 100 nodes    | ~200-500 MB       | ~50-100 MB          | 4x               |
| 500 nodes    | ~2-4 GB           | ~500 MB-1 GB        | 4x               |
| 1000 nodes   | ~8-16 GB          | ~2-4 GB             | 4x               |

## Benchmark Results

(To be populated after running benchmarks)

## Performance Analysis

### Bottlenecks Identified

1. **Curvature Computation**: O(n³) complexity (Sinkhorn algorithm)
   - Target: Parallel edge processing
   - Target: Optimized Rust backend

2. **Null Models**: Sequential generation
   - Target: Parallel replicate generation (Rust)

3. **Cost Matrix Construction**: O(n²) shortest paths
   - Target: Caching, incremental updates

### Optimization Opportunities

1. **Parallelization**: ThreadsX.jl for Julia, rayon for Rust
2. **Memory**: Sparse matrices, streaming
3. **Algorithms**: Early stopping, convergence detection
4. **Caching**: Probability measures, shortest paths

## Validation

After benchmarks, validate:
1. Numerical equivalence (within tolerance)
2. Correctness (same results)
3. Performance gains (meet targets)
4. Memory reduction (meet targets)

---

**Status**: Framework ready, awaiting benchmark execution  
**Next Step**: Run benchmarks and populate results

