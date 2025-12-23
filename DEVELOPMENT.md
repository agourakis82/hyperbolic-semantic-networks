# Development Guide

## Overview

This repository implements a high-performance analysis pipeline for hyperbolic geometry in semantic networks using a multi-language stack:

- **Rust**: Performance-critical curvature computation and null model generation
- **Julia**: Scientific computing layer with FFI bindings to Rust
- **Python**: Analysis scripts and data processing

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Python Layer                         │
│         (Analysis Scripts, Visualization)               │
│                                                         │
│  • SWOW data processing                                │
│  • Figure generation                                   │
│  • Statistical analysis                                │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                    Julia Layer                          │
│       (Scientific Computing & Orchestration)            │
│                                                         │
│  • Graph preprocessing                                 │
│  • High-level curvature API                           │
│  • Null model generation                              │
│  • Statistical validation                             │
└──────────────────┬──────────────────────────────────────┘
                   │ FFI
                   ▼
┌─────────────────────────────────────────────────────────┐
│                    Rust Layer                           │
│            (Performance-Critical Kernels)               │
│                                                         │
│  • Wasserstein-1 distance (Sinkhorn algorithm)        │
│  • Configuration model sampling                        │
│  • Triadic-rewire null models                         │
└─────────────────────────────────────────────────────────┘
```

---

## Development Setup

### Prerequisites

1. **Rust** (1.70+):
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

2. **Julia** (1.9+):
   ```bash
   # Download from https://julialang.org/downloads/
   ```

3. **Python** (3.9+):
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r code/analysis/requirements.txt
   ```

### Building Rust Components

```bash
cd rust

# Build all workspace members
cargo build --release

# Run tests
cargo test --workspace

# Run benchmarks
cargo bench --workspace

# Generate documentation
cargo doc --workspace --no-deps --open
```

### Setting up Julia

```bash
cd julia

# Start Julia REPL
julia

# Install dependencies
] add Graphs DataFrames CSV JSON Statistics LinearAlgebra Random ProgressMeter Logging

# Run tests
] test

# Or from command line
julia --project=. test/runtests.jl
```

### Running Python Tests

```bash
cd code/analysis

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_curvature.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

---

## Code Quality Standards

### Rust

**Style**: Use `rustfmt` for formatting
```bash
cargo fmt --all
```

**Linting**: Use `clippy` for linting
```bash
cargo clippy --workspace -- -D warnings
```

**Safety**:
- All FFI functions must validate inputs
- Use `#[cfg(test)]` for unit tests
- Benchmark performance-critical code

### Julia

**Style**: Follow Julia style guide
- Use 4 spaces for indentation
- CamelCase for types, snake_case for functions
- Comprehensive docstrings

**Testing**:
- Add tests to `julia/test/`
- Use `@testset` for grouping
- Test edge cases and error conditions

### Python

**Style**: Follow PEP 8
```bash
black code/analysis/*.py
```

**Type Hints**: Add type hints where possible
```python
def compute_curvature(graph: nx.Graph, alpha: float = 0.5) -> Dict[Tuple[int, int], float]:
    ...
```

**Testing**:
- Use `pytest` for all tests
- Aim for >80% code coverage
- Use fixtures for common setup

---

## Performance Optimization

### Profiling Rust Code

```bash
# CPU profiling with flamegraph
cargo install flamegraph
sudo cargo flamegraph --bench wasserstein_bench

# Memory profiling with valgrind
cargo build --release
valgrind --tool=massif target/release/hyperbolic-curvature
```

### Profiling Julia Code

```julia
using Profile, ProfileView

# Profile curvature computation
@profile compute_graph_curvature(graph; parallel=true)
ProfileView.view()
```

### Profiling Python Code

```python
import cProfile
import pstats

cProfile.run('compute_curvature_FINAL.main()', 'profile.stats')
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(20)
```

---

## Testing Strategy

### Unit Tests
- **Rust**: Test individual functions with edge cases
- **Julia**: Test mathematical correctness
- **Python**: Test data processing and I/O

### Integration Tests
- Test Rust ↔ Julia FFI
- Test end-to-end pipelines
- Validate against known results

### Performance Tests
- Benchmark critical paths
- Ensure O(n²) or better scaling
- Monitor memory usage

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: CI

on: [push, pull_request]

jobs:
  rust:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
      - run: cargo test --workspace
      - run: cargo clippy --workspace -- -D warnings

  julia:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: julia-actions/setup-julia@v1
        with:
          version: '1.9'
      - run: julia --project=julia -e 'using Pkg; Pkg.test()'

  python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r code/analysis/requirements.txt
      - run: pytest code/analysis/tests/ -v
```

---

## Debugging

### Rust

```bash
# Run with debug symbols
cargo build
rust-gdb target/debug/hyperbolic-curvature

# Enable logging
RUST_LOG=debug cargo test
```

### Julia

```julia
# Use Debugger.jl
using Debugger

@enter compute_curvature(graph, 1, 2)
```

### Python

```python
# Use pdb
import pdb; pdb.set_trace()

# Or ipdb for better interface
import ipdb; ipdb.set_trace()
```

---

## Contributing

1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Write tests** for your changes
4. **Ensure all tests pass**: Run Rust, Julia, and Python tests
5. **Format code**: `cargo fmt`, `black`, Julia conventions
6. **Commit**: `git commit -m "feat: add amazing feature"`
7. **Push**: `git push origin feature/amazing-feature`
8. **Open a Pull Request**

### Commit Message Convention

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/changes
- `perf:` Performance improvements
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

---

## Release Process

1. Update `CHANGELOG.md`
2. Bump version in:
   - `rust/Cargo.toml`
   - `julia/Project.toml`
   - `CITATION.cff`
3. Tag release: `git tag -a v0.2.0 -m "Release v0.2.0"`
4. Push tags: `git push origin v0.2.0`
5. Create GitHub release
6. Publish to Zenodo

---

## Troubleshooting

### Common Issues

**Issue**: Rust FFI not found by Julia
**Solution**: Ensure Rust library is compiled with `cdylib` crate-type

**Issue**: Julia parallel processing not working
**Solution**: Start Julia with multiple threads: `julia -t 8`

**Issue**: Python tests fail with import errors
**Solution**: Install package in editable mode: `pip install -e .`

---

## Resources

- [Rust Book](https://doc.rust-lang.org/book/)
- [Julia Documentation](https://docs.julialang.org/)
- [NetworkX Documentation](https://networkx.org/)
- [Ollivier-Ricci Curvature Paper](https://arxiv.org/abs/0712.3711)

---

## Contact

Dr. Demetrios Agourakis
Email: demetrios@agourakis.med.br
ORCID: 0000-0002-8596-5097
