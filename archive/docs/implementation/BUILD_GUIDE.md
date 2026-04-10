# Build and Development Guide

**Date**: 2025-11-08

## Prerequisites

### Required

- **Julia 1.9+**: Download from https://julialang.org/downloads/
- **Rust stable**: Install via https://rustup.rs/
- **Python 3.10+**: For baseline comparison (optional)

### Optional

- **Docker**: For containerized environment
- **Make**: For build automation

## Quick Start

```bash
# Clone repository
git clone <repository-url>
cd hyperbolic-semantic-networks

# Install Julia dependencies
cd julia
julia --project=. -e 'using Pkg; Pkg.instantiate()'
cd ..

# Build Rust libraries
cd rust
cargo build --release
cd ..

# Run tests
make test-all
```

## Detailed Setup

### Step 1: Install Julia

```bash
# Linux
wget https://julialang-s3.julialang.org/bin/linux/x64/1.9/julia-1.9.x-linux-x86_64.tar.gz
tar -xzf julia-1.9.x-linux-x86_64.tar.gz
sudo mv julia-1.9.x /opt/julia
sudo ln -s /opt/julia/bin/julia /usr/local/bin/julia

# Verify
julia --version
```

### Step 2: Install Rust

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# Verify
rustc --version
cargo --version
```

### Step 3: Build Rust Libraries

```bash
cd rust

# Build curvature library
cd curvature
cargo build --release
cd ..

# Build null_models library
cd null_models
cargo build --release
cd ..

cd ..
```

Or use the build script:
```bash
./scripts/build_rust_libs.sh
```

### Step 4: Install Julia Dependencies

```bash
cd julia
julia --project=. -e 'using Pkg; Pkg.instantiate()'
```

This will install all dependencies listed in `Project.toml`.

## Building

### Manual Build

```bash
# Rust libraries
cd rust && cargo build --release && cd ..

# Julia package (no separate build step, but test loading)
julia --project=julia -e 'using HyperbolicSemanticNetworks'
```

### Using Makefile

```bash
# Build everything
make build-rust

# Run tests
make test-all

# Validate
make validate
```

## Development Workflow

### Running Tests

```bash
# All tests
make test-all

# Julia tests only
make test-julia

# Rust tests only
make test-rust

# Specific test file
julia --project=julia test/test_curvature.jl
```

### Running Scripts

```bash
# Example usage
julia --project=julia julia/scripts/example_usage.jl

# Full pipeline
julia --project=julia julia/scripts/paper1/full_pipeline.jl

# Generate figures
julia --project=julia scripts/generate_all_figures.jl

# Generate tables
julia --project=julia julia/scripts/paper1/generate_tables.jl
```

### Benchmarking

```bash
# Julia/Rust benchmarks
julia --project=julia julia/scripts/benchmark_comparison.jl

# Compare with Python
python scripts/compare_with_python.py
```

## Docker Development

```bash
# Build image
docker build -t hyperbolic-semantic-networks .

# Run container
docker run -it -v $(pwd):/workspace hyperbolic-semantic-networks

# Inside container
julia --project=julia
```

## Troubleshooting

### Julia Package Errors

```bash
# Clear and reinstall
cd julia
rm Manifest.toml
julia --project=. -e 'using Pkg; Pkg.instantiate()'
```

### Rust Build Errors

```bash
# Clean and rebuild
cd rust
cargo clean
cargo build --release
```

### FFI Library Not Found

1. Verify library exists: `ls rust/target/release/libhyperbolic_curvature.*`
2. Check permissions: `chmod +r rust/target/release/libhyperbolic_curvature.*`
3. Julia will fall back to Julia implementation if not found

### Import Errors

```bash
# Make sure you're in the right directory
cd julia
julia --project=. 

# Then in Julia REPL:
using Pkg
Pkg.activate(".")
using HyperbolicSemanticNetworks
```

## Continuous Integration

The CI pipeline (`.github/workflows/ci.yml`) automatically:
1. Tests Julia code
2. Tests Rust code
3. Runs benchmarks (if configured)

To run locally:
```bash
# Simulate CI
make test-all
```

## Performance Profiling

### Julia Profiling

```julia
using Profile

@profile compute_graph_curvature(G, alpha=0.5)
Profile.print()
```

### Rust Profiling

```bash
# Install cargo-flamegraph
cargo install flamegraph

# Profile
cd rust/curvature
cargo flamegraph --bench wasserstein_bench
```

## Next Steps

1. Build and test everything
2. Run benchmarks
3. Compare with Python
4. Optimize hot paths
5. Expand test coverage

---

**For more details, see `docs/REPRODUCIBILITY.md`**

