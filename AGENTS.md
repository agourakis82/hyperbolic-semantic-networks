# AGENTS.md - AI Coding Agent Guide

**Project**: Hyperbolic Geometry of Semantic Networks  
**Version**: v2.0 (Phase Transition Discovery)  
**Languages**: Julia, Rust, Python, Sounio  
**Primary Language (Documentation)**: English (with some Portuguese/Spanish code comments)

---

## Project Overview

This is a research codebase for analyzing hyperbolic geometry in semantic networks using Ollivier-Ricci curvature. The project implements a multi-language computational pipeline:

- **Julia** (v1.9+): Reference scientific computing implementation
- **Rust** (stable): Performance-critical curvature computation kernels  
- **Python** (3.10+): Data processing, analysis scripts, and baseline validation
- **Sounio**: Type-safe experiments with epistemic computing and effect tracking

**Key Discovery**: Universal phase transition at `⟨k⟩²/N ≈ 2.5` that determines network geometry:
- `⟨k⟩²/N < 2.0` → Hyperbolic (negative curvature, tree-like)
- `⟨k⟩²/N ≈ 2.5` → Euclidean (critical point/phase transition)
- `⟨k⟩²/N > 3.5` → Spherical (positive curvature, clique-like)

---

## Technology Stack

### Core Dependencies

**Julia** (`julia/Project.toml`):
```
- Graphs.jl (graph library, replaces LightGraphs)
- DataFrames.jl, CSV.jl, JSON.jl (data handling)
- Statistics.jl, LinearAlgebra.jl, Optim.jl (numerical computation)
- Plots.jl, StatsPlots.jl (visualization)
- ProgressMeter.jl, Logging.jl (utilities)
```

**Rust** (`rust/Cargo.toml`):
```
- ndarray 0.16 (numerical arrays)
- rayon 1.8 (parallel processing)
- petgraph 0.6 (graph library)
- libc 0.2 (FFI)
- criterion 0.5 (benchmarking)
```

**Python** (implicit dependencies):
```
- networkx, GraphRicciCurvature (curvature computation)
- numpy, scipy, pandas (numerical/data)
- matplotlib, seaborn (visualization)
- pytest (testing)
```

### External Tools
- **Sounio Compiler**: Effect-tracked programming language for experiments (`souc` command)
- **Docker**: Reproducible environment (Julia 1.9 base + Rust)
- **Kubernetes**: Distributed job execution (Ricci flow, null models)
- **Lean 4**: Mathematical formalization for proof verification

### Lean 4 Formalization
The `lean/` directory contains machine-checked proofs for key mathematical claims:

**Status**: 76% complete (~2,070 lines)

**Formalized Theorems**:
- ✅ Curvature bounds: κ ∈ [-1, 1]
- ✅ Clustering bounds: C ∈ [0, 1]  
- ✅ Probability measure normalization
- ✅ Cross-implementation equivalence (Julia/Rust/Sounio)
- ⚠️ Phase transition (empirical conjecture structure)

**Build**:
```bash
cd lean/HyperbolicSemanticNetworks
lake update
lake build
lake test
```

See `lean/HyperbolicSemanticNetworks/doc/FORMALIZATION_REPORT.md` for details.

---

## Repository Structure

```
hyperbolic-semantic-networks/
├── README.md                    # Main project documentation
├── CHANGELOG.md                 # Version history
├── DEVELOPMENT.md               # Comprehensive development guide
├── RUNME.md                     # Quick reproduction guide
├── CITATION.cff                 # Citation metadata
├── LICENSE                      # MIT license
├── .zenodo.json                 # Zenodo publication config
├── ZENODO_DOI.txt               # DOI reference
│
├── julia/                       # Julia implementation (reference)
│   ├── Project.toml             # Julia dependencies
│   ├── src/
│   │   ├── HyperbolicSemanticNetworks.jl  # Main module
│   │   ├── Preprocessing/       # SWOW, ConceptNet, Taxonomies
│   │   ├── Curvature/           # Ollivier-Ricci + FFI to Rust
│   │   ├── Analysis/            # Null models, bootstrap, Ricci flow
│   │   ├── Visualization/       # Figures, phase diagrams
│   │   └── Utils/               # Metrics, IO, validation
│   ├── test/                    # Test suite
│   └── scripts/                 # Pipeline scripts
│
├── lean/                        # Lean 4 mathematical formalization
│   ├── lakefile.lean            # Lean build configuration
│   ├── HyperbolicSemanticNetworks/
│   │   ├── src/                 # Formalization source
│   │   │   ├── Basic.lean       # Graph definitions
│   │   │   ├── Curvature.lean   # Ollivier-Ricci
│   │   │   ├── PhaseTransition.lean  # Critical point theory
│   │   │   └── ...
│   │   ├── test/                # Unit tests
│   │   └── doc/                 # Documentation
│
├── rust/                        # Rust implementation (performance)
│   ├── Cargo.toml               # Workspace config
│   ├── curvature/               # Wasserstein distance, Sinkhorn
│   └── null_models/             # Configuration model, triadic-rewire
│
├── code/                        # Python analysis scripts
│   ├── analysis/                # Full analysis pipeline (75+ scripts)
│   │   ├── tests/               # pytest test suite
│   │   ├── compute_curvature_FINAL.py
│   │   └── *_v6.4.py            # Versioned analysis scripts
│   └── fmri/                    # fMRI analysis extensions
│
├── experiments/                 # Sounio experiments
│   ├── 01_epistemic_uncertainty/    # Phase transition sweep
│   ├── 02_null_model/               # Configuration null ensemble
│   ├── 03_forman_ricci/             # Forman vs Ollivier
│   ├── 04_uncertainty_scaling/      # Entropy at phase transition
│   ├── 05_hypercomplex/             # S³, S⁷, S¹⁵ embeddings
│   ├── 06_spectral_geometry/        # Eigenvalue validation
│   ├── 07_scale_n500/               # N=100/200 scaling
│   └── 08_epsilon_diagnostic/       # Epsilon parameter validation
│
├── stdlib/                      # Sounio standard library extensions
│   └── math/                    # clifford.sio, homology_curvature.sio, etc.
│
├── data/                        # Data directory
│   ├── raw/                     # Original SWOW data (not in git)
│   ├── processed/               # Processed networks
│   └── external/                # External datasets
│
├── results/                     # Computed results
│   ├── experiments/             # Phase transition data
│   ├── sounio/                  # Sounio experiment outputs
│   └── figures/                 # Generated figures
│
├── manuscript/                  # Academic manuscript
│   ├── main.md                  # Complete manuscript
│   └── figures/                 # Publication figures
│
├── docs/                        # Documentation
│   ├── INDEX.md                 # Master documentation index
│   ├── REPRODUCIBILITY.md       # Reproduction guide
│   ├── session_reports/         # Work session reports
│   ├── planning/                # Checklists, roadmaps
│   └── research_reports/        # Scientific findings
│
├── scripts/                     # Utility scripts
│   ├── build_rust_libs.sh
│   ├── zenodo_publish.py        # Zenodo integration
│   └── cleanup_repository.py    # Repository maintenance
│
├── tools/                       # Development tools
│   └── zenodo_new_version.py
│
├── k8s/                         # Kubernetes deployments
│   ├── ricci-flow-deployment.yaml
│   └── structural-nulls-job.yaml
│
└── config/                      # Configuration files
    └── babelnet_conf.yml
```

---

## Build Commands

### Julia Setup
```bash
# Install dependencies
julia --project=julia -e 'using Pkg; Pkg.instantiate()'

# Run tests
julia --project=julia -e 'using Pkg; Pkg.test()'
# OR
julia --project=julia julia/test/runtests.jl

# Run phase transition experiment (validated reference)
julia phase_transition_pure_julia.jl
```

### Rust Setup
```bash
cd rust

# Build all workspace members
cargo build --release

# Run tests
cargo test --workspace

# Run benchmarks
cargo bench --workspace

# Format and lint
cargo fmt --all
cargo clippy --workspace -- -D warnings
```

### Python Setup
```bash
# Install dependencies (typically via requirements.txt or manually)
pip install networkx numpy scipy pandas matplotlib seaborn GraphRicciCurvature pytest

# Run tests
cd code/analysis
python -m pytest tests/ -v

# Run analysis pipeline
python run_analysis_pipeline.py
```

### Sounio Experiments
```bash
# Each experiment has its own run.sh script
cd experiments/01_epistemic_uncertainty
bash run.sh

# Or compile and run manually (requires Sounio compiler)
souc run phase_transition.sio
```

### Docker (Full Environment)
```bash
# Build image
docker build -t hyperbolic-semantic-networks .

# Run container
docker run -it -v $(pwd):/workspace hyperbolic-semantic-networks
```

---

## Code Style Guidelines

### Julia
- **Indentation**: 4 spaces
- **Naming**: CamelCase for types, snake_case for functions
- **Documentation**: Comprehensive docstrings for all public functions
- **Module organization**: `src/ModuleName/SubModule.jl`, included in main module
- **Testing**: Use `@testset` for grouping, tests in `test/test_*.jl`

### Rust
- **Formatting**: Use `cargo fmt --all`
- **Linting**: Use `cargo clippy --workspace -- -D warnings`
- **Safety**: All FFI functions must validate inputs
- **Testing**: Use `#[cfg(test)]` for unit tests
- **Benchmarking**: Use criterion for performance-critical code

### Python
- **Style**: Follow PEP 8
- **Formatting**: Use `black` (see Makefile target `make format`)
- **Type hints**: Add where possible
- **Testing**: Use `pytest` with fixtures for common setup
- **Scripts**: Many legacy scripts use v6.4 versioning scheme

### Sounio
- **Effects**: Explicitly track with `with IO, Mut, Div, Panic`
- **Types**: Use fixed-size arrays `[T; N]` for performance
- **Comments**: Heavy documentation of mathematical formulas
- **Structure**: Clear separation of LCG, Graph, BFS, Measure, Sinkhorn, curvature

---

## Testing Instructions

### Test Organization

**Julia Tests** (`julia/test/`):
- `runtests.jl` - Main test runner
- `test_preprocessing.jl` - Data loading tests
- `test_curvature.jl` - Curvature computation tests
- `test_analysis.jl` - Analysis pipeline tests
- `test_integration.jl` - End-to-end tests
- `test_regression.jl` - Regression tests
- `test_properties.jl` - Property-based tests
- `test_performance.jl` - Benchmarks (optional, requires BenchmarkTools)

**Rust Tests**:
- Unit tests in each crate (`src/*.rs` with `#[cfg(test)]`)
- Benchmarks in `benches/` directory

**Python Tests** (`code/analysis/tests/`):
- `test_curvature.py` - Curvature computation validation
- `test_network_building.py` - Network construction tests
- `conftest.py` - pytest fixtures

### Running Tests

```bash
# Julia
julia --project=julia -e 'using Pkg; Pkg.test()'

# Rust
cd rust && cargo test --workspace

# Python
cd code/analysis && python -m pytest tests/ -v

# All (via CI)
# See .github/workflows/ci.yml for full CI pipeline
```

### Validation

The project validates against:
1. **Q1 Literature**: Ollivier 2009, Ni et al. 2015, 2019
2. **Python Baseline**: GraphRicciCurvature library
3. **Julia Reference**: Validated phase transition at N=200
4. **Cross-language**: Numerical agreement between Julia/Rust/Sounio

---

## Deployment & Distribution

### GitHub Releases
- Use semantic versioning (current: v2.0.0)
- Tag format: `v{major}.{minor}.{patch}`
- See `scripts/prepare_release.sh` and `scripts/push_release.sh`

### Zenodo Integration
- Config in `.zenodo.json`
- DOI tracked in `ZENODO_DOI.txt`
- Publish with: `python scripts/zenodo_publish.py`
- Requires `ZENODO_ACCESS_TOKEN` environment variable

### Kubernetes Deployment
- Job definitions in `k8s/`
- Used for distributed Ricci flow and null model generation
- Requires cluster with node labels for GPU/CPU workloads

### Docker
- `Dockerfile` provides complete reproducible environment
- Based on `julia:1.9` with Rust toolchain
- Pre-installs Julia and Rust dependencies

---

## Security Considerations

### Input Validation
- **Rust FFI**: All exported functions validate inputs before processing
- **Julia**: Graph validation in `Utils/Validation.jl`
- **Python**: Input sanitization in preprocessing scripts

### Data Handling
- Large data files (>100MB) excluded from git (see `.gitignore`)
- Sensitive data should be placed in `data/external/` (gitignored)
- SWOW data requires separate download (see data documentation)

### Dependencies
- Regular updates via `cargo update` and `Pkg.update()`
- Check for security advisories: `cargo audit` (if installed)
- Python: Use `pip-audit` for vulnerability scanning

### Environment Secrets
- `ZENODO_ACCESS_TOKEN` for publication
- Kubernetes configs may contain cluster-specific paths
- Never commit API keys or credentials

---

## Key Conventions

### Version Numbering
- **Major**: Significant architectural changes
- **Minor**: New features, analyses, or experiments
- **Patch**: Bug fixes, documentation updates

### File Naming
- Julia scripts: `snake_case.jl`
- Python scripts: `snake_case.py` or `SCREAMING_SNAKE_CASE_v6.4.py` (legacy)
- Sounio: `snake_case.sio`
- Results: `{experiment_name}_{language}.csv/json`

### Documentation
- All modules have module-level docstrings/comments
- Complex algorithms reference academic papers
- Session reports track work progress in `docs/session_reports/`

---

## Quick Reference

### Most Common Tasks

```bash
# Run validated phase transition experiment
julia phase_transition_pure_julia.jl

# Build Rust libraries
cd rust && cargo build --release

# Run Sounio experiment
bash experiments/01_epistemic_uncertainty/run.sh

# Clean repository
python scripts/cleanup_repository.py

# Generate all figures
cd code/analysis && python generate_final_figures.py
```

### Important File Locations
- Main module: `julia/src/HyperbolicSemanticNetworks.jl`
- Curvature computation: `julia/src/Curvature/OllivierRicci.jl`
- Rust FFI: `julia/src/Curvature/FFI.jl`
- Core Sounio experiment: `experiments/01_epistemic_uncertainty/phase_transition.sio`
- Manuscript: `manuscript/main.md`

---

## Contact & Citation

**Author**: Dr. Demetrios Chiuratto Agourakis  
**Email**: demetrios@agourakis.med.br  
**ORCID**: 0000-0002-8596-5097  
**Repository**: https://github.com/agourakis82/hyperbolic-semantic-networks  
**DOI**: 10.5281/zenodo.17655231

### Citation
```bibtex
@software{hyperbolic_semantic_networks,
  title = {Hyperbolic Geometry of Semantic Networks: Cross-Linguistic Evidence},
  author = {Agourakis, Demetrios C.},
  year = {2025},
  doi = {10.5281/zenodo.17655231},
  url = {https://github.com/agourakis82/hyperbolic-semantic-networks}
}
```

---

*Last updated: 2025-02-22*  
*For the latest information, see README.md and docs/INDEX.md*
