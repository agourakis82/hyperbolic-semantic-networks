# FFI Integration Guide

**Date**: 2025-11-08  
**Status**: Implementation Guide

## Overview

This guide explains how to set up and use the Foreign Function Interface (FFI) between Julia and Rust for high-performance curvature computation.

## Building Rust Libraries

### Step 1: Build Rust Libraries

```bash
cd rust
cargo build --release
```

Or use the provided script:

```bash
./scripts/build_rust_libs.sh
```

This will create:
- `rust/target/release/libhyperbolic_curvature.so` (Linux)
- `rust/target/release/libhyperbolic_curvature.dylib` (macOS)
- `rust/target/release/hyperbolic_curvature.dll` (Windows)

### Step 2: Verify Library Location

The Julia FFI code (`julia/src/Curvature/FFI.jl`) will automatically search for the library in:
1. `rust/target/release/libhyperbolic_curvature.so` (Linux)
2. `rust/target/release/libhyperbolic_curvature.dylib` (macOS)
3. `rust/target/release/hyperbolic_curvature.dll` (Windows)

## Using FFI in Julia

### Automatic Fallback

The FFI implementation automatically falls back to a Julia implementation if the Rust library is not found:

```julia
using HyperbolicSemanticNetworks

# This will use Rust if available, Julia fallback otherwise
curvatures = compute_graph_curvature(graph, alpha=0.5)
```

### Manual Initialization

To explicitly initialize the Rust library:

```julia
using HyperbolicSemanticNetworks.Curvature: init_rust_library

if init_rust_library()
    println("Rust library loaded successfully")
else
    println("Using Julia fallback")
end
```

## FFI Function Signatures

### Rust Side

```rust
#[no_mangle]
pub extern "C" fn compute_wasserstein1(
    mu: *const f64,
    nu: *const f64,
    cost_matrix: *const f64,
    n: usize,
    epsilon: f64,
    max_iterations: usize,
) -> f64
```

### Julia Side

```julia
function wasserstein1_rust(
    mu::Vector{Float64},
    nu::Vector{Float64},
    cost_matrix::Vector{Float64},
    epsilon::Float64 = 0.01,
    max_iterations::Int = 100
)::Float64
```

## Testing FFI

### Unit Tests

```bash
cd rust
cargo test
```

### Integration Tests

```bash
julia --project=julia test/test_curvature.jl
```

### Validation

```bash
julia --project=julia scripts/validate_implementation.jl
```

## Troubleshooting

### Library Not Found

**Problem**: Julia can't find the Rust library

**Solutions**:
1. Build the library: `cargo build --release`
2. Check library path in `FFI.jl`
3. Verify library extension (.so, .dylib, .dll)
4. Check file permissions

### FFI Call Fails

**Problem**: `ccall` fails with error

**Solutions**:
1. Verify function signature matches
2. Check data types (must be C-compatible)
3. Ensure arrays are contiguous in memory
4. Check for null pointers

### Performance Issues

**Problem**: No performance improvement

**Solutions**:
1. Verify Rust library is actually being used (check logs)
2. Ensure release build (`--release` flag)
3. Profile to identify bottlenecks
4. Check if fallback to Julia is being used

## Next Steps

1. Complete FFI for null models
2. Add more Rust functions
3. Optimize data passing
4. Add comprehensive error handling

---

**Status**: Basic FFI structure complete, ready for testing

