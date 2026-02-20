# Hyperbolic Geometry of Semantic Networks

**Cross-Linguistic Evidence from Word Association Data**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17655231.svg)](https://doi.org/10.5281/zenodo.17655231)
[![GitHub](https://img.shields.io/github/stars/agourakis82/hyperbolic-semantic-networks?style=social)](https://github.com/agourakis82/hyperbolic-semantic-networks)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

---

## Overview

This repository contains research on **network geometry** using Ollivier-Ricci curvature analysis across multiple implementations:

- **Julia**: Reference implementation (validated)
- **Rust**: Performance-focused implementation
- **Sounio**: Type-safe implementation with epistemic computing

**Latest Discovery**: Universal phase transition at **⟨k⟩²/N ≈ 2.5** determines network geometry

---

## Key Findings

### Phase Transition Discovery (Dec 2024)

- **Universal law**: Sparsity ratio ⟨k⟩²/N determines geometry
  - ⟨k⟩²/N < 2.0 → **Hyperbolic** (negative curvature)
  - ⟨k⟩²/N ≈ 2.5 → **Critical point** (phase transition)
  - ⟨k⟩²/N > 3.5 → **Spherical** (positive curvature)

- **Validated on**:
  - 11 synthetic networks (N=200, k=2..50)
  - 4 real semantic networks (SWOW: Spanish, English, Chinese, Dutch)
  - Transition at k≈22 (ratio≈2.49) for N=200

### Original Findings

- **8 semantic networks** analyzed (SWOW, ConceptNet, taxonomies)
- **Hyperbolic geometry** in moderate clustering regime (C ≈ 0.02–0.15)
- **Broad-scale topology**: α = 1.90 ± 0.03
- **Cross-linguistic consistency** across language families

---

## Repository Structure

```
hyperbolic-semantic-networks/
├── README.md                    # This file
├── CHANGELOG.md                 # Version history
├── CLEANUP_PLAN.md              # Organization and experiment plan
│
├── julia/                       # Julia implementation
│   ├── src/                     # Core modules
│   ├── experiments/             # Phase transition experiments
│   └── phase_transition_pure_julia.jl  # Validated experiment
│
├── rust/                        # Rust implementation
│   ├── curvature/               # Curvature computation
│   └── null_models/             # Random graph generation
│
├── experiments/                 # Sounio-powered experiments
│   ├── 01_epistemic_uncertainty/   # Uncertainty quantification
│   ├── 02_parallel_sweep/          # Parallel phase transitions
│   ├── 03_gpu_sinkhorn/            # GPU acceleration
│   ├── 04_cross_language/          # Julia/Rust/Sounio comparison
│   ├── 05_streaming/               # Real-time network monitoring
│   └── 06_refinement_types/        # Formal verification
│
├── results/                     # Computed results
│   ├── experiments/             # Phase transition data
│   ├── curvature/               # Curvature metrics
│   └── swow_clustering_coefficients.json
│
├── docs/                        # Organized documentation
│   ├── sounio/                  # Sounio implementation docs
│   ├── validation/              # Scientific validation reports
│   ├── INDEX.md                 # Master index
│   └── [various guides]
│
├── manuscript/                  # Main manuscript
│   ├── main.md                  # Complete manuscript
│   └── figures/                 # Publication figures
│
├── code/                        # Python analysis scripts
│   ├── analysis/                # Analysis pipeline
│   └── figures/                 # Figure generation
│
└── data/                        # Data
    ├── raw/                     # Original SWOW data
    └── processed/               # Processed networks
```

---

## Quick Start

### Requirements

**Julia**:
```bash
julia --project -e 'using Pkg; Pkg.instantiate()'
```

**Rust**:
```bash
cd rust && cargo build --release
```

**Sounio** (for new experiments):
```bash
cd path/to/sounio/compiler
cargo build --release
export PATH=$PATH:$(pwd)/target/release
```

### Run Phase Transition Experiment

```bash
# Julia (validated reference)
julia phase_transition_pure_julia.jl

# Results in: results/experiments/phase_transition_pure_julia.json
```

### Reproduce Analysis

```bash
# Complete analysis pipeline
cd code/analysis
python run_analysis_pipeline.py

# Generate figures
cd ../figures
python generate_all_figures.py
```

---

## New Experiments (Leveraging Sounio)

See [CLEANUP_PLAN.md](CLEANUP_PLAN.md) for full details.

### 1. Epistemic Uncertainty Tracking

**Question**: How does curvature uncertainty vary with network properties?

**Sounio Advantage**: Automatic uncertainty propagation

```bash
cd experiments/01_epistemic_uncertainty
# See README.md for details
```

### 2. Parallel Phase Sweep

**Question**: How fast can we sweep the phase transition with verified parallelism?

**Sounio Advantage**: Effect-tracked parallelism

### 3. GPU-Accelerated Sinkhorn

**Question**: Can GPU acceleration enable real-time curvature for large networks?

**Sounio Advantage**: GPU-native with first-class effects

### 4. Cross-Language Validation

**Question**: How do Julia, Rust, and Sounio compare?

**Sounio Advantage**: Type-safe FFI with effect tracking

### 5. Real-Time Network Monitoring

**Question**: Can we track geometry changes in evolving networks?

**Sounio Advantage**: Streaming effects + epistemic computing

### 6. Formal Verification

**Question**: Can we prove geometric properties at compile-time?

**Sounio Advantage**: Refinement types + SMT verification

---

## Key Results

### Phase Transition Data

| Network | N | ⟨k⟩ | ⟨k⟩²/N | κ_mean | Geometry |
|---------|---|-----|--------|--------|----------|
| Sparse | 200 | 3 | 0.05 | -0.287 | Hyperbolic |
| Medium | 200 | 22 | 2.42 | -0.013 | **Transition** |
| Dense | 200 | 30 | 4.50 | +0.073 | Spherical |

**Full data**: `results/experiments/phase_transition_pure_julia.json`

### Semantic Networks

| Language | N | ⟨k⟩ | ⟨k⟩²/N | κ | Prediction |
|----------|---|-----|--------|---|------------|
| Spanish | 9,246 | 3.0 | **0.001** | -0.155 | Hyperbolic ✓ |
| English | 10,571 | 3.1 | **0.001** | -0.258 | Hyperbolic ✓ |
| Chinese | 8,857 | 3.2 | **0.001** | -0.214 | Hyperbolic ✓ |
| Dutch | 2,962 | 61.6 | **1.280** | +0.125 | Spherical ✓ |

**Key Insight**: All semantic networks have ⟨k⟩²/N << 1, explaining universal hyperbolicity!

---

## Documentation

### Main Docs
- [CLEANUP_PLAN.md](CLEANUP_PLAN.md) - Organization and experiment roadmap
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development guide

### Scientific Reports
- [docs/validation/PHASE_TRANSITION_DISCOVERY.md](docs/validation/PHASE_TRANSITION_DISCOVERY.md) - Phase transition discovery
- [docs/validation/FINAL_VALIDATION_SUMMARY.md](docs/validation/FINAL_VALIDATION_SUMMARY.md) - Validation summary
- [docs/validation/DEEP_SCIENCE_ANALYSIS.md](docs/validation/DEEP_SCIENCE_ANALYSIS.md) - Mathematical foundations

### Sounio Implementation
- [docs/sounio/SOUNIO_IMPLEMENTATION_STATUS.md](docs/sounio/SOUNIO_IMPLEMENTATION_STATUS.md) - Implementation status
- [docs/sounio/SOUNIO_INTEGRATION_PLAN.md](docs/sounio/SOUNIO_INTEGRATION_PLAN.md) - Integration plan
- [docs/sounio/SOUNIO_ROADMAP.md](docs/sounio/SOUNIO_ROADMAP.md) - Development roadmap

### Full Index
- [docs/INDEX.md](docs/INDEX.md) - Complete documentation index

---

## Implementation Status

### ✅ Complete
- Julia reference implementation
- Rust performance implementation
- Sounio graph module (in [Sounio repo](https://github.com/sounio-lang/sounio))
- Phase transition discovery and validation
- Scientific documentation

### 🔬 In Progress
- Experiment 1: Epistemic uncertainty tracking
- Cross-language benchmarking
- GPU acceleration (when Sounio GPU ready)

### 📋 Planned
- Real-time network monitoring
- Formal verification with refinement types
- Publication: "Network Geometry in Sounio"

---

## Citation

### This Work

```bibtex
@software{hyperbolic_semantic_networks_julia_rust,
  title = {Hyperbolic Semantic Networks: Julia/Rust/Sounio Implementation},
  author = {Agourakis, Demetrios C.},
  year = {2025},
  doi = {10.5281/zenodo.17655231},
  url = {https://zenodo.org/records/17655231},
  version = {0.2.0}
}
```

### Phase Transition Discovery

```bibtex
@article{agourakis2024phase,
  title = {Universal Phase Transition in Network Geometry},
  author = {Agourakis, Demetrios C.},
  journal = {In preparation},
  year = {2024},
  note = {Transition at $\langle k \rangle^2 / N \approx 2.5$}
}
```

### SWOW Dataset

```bibtex
@article{de2019small,
  title={The Small World of Words English word association norms for over 12,000 cue words},
  author={De Deyne, Simon and Navarro, Danielle J and Perfors, Amy and Brysbaert, Marc and Storms, Gert},
  journal={Behavior Research Methods},
  volume={51},
  pages={987--1006},
  year={2019}
}
```

---

## Sounio Integration

The network geometry module has been implemented in the [Sounio programming language](https://github.com/sounio-lang/sounio) at `stdlib/graph/`, showcasing:

- ✅ **Effect system**: Explicit tracking of Alloc, Random, Confidence
- ✅ **Epistemic computing**: Automatic uncertainty propagation
- ✅ **Units of measure**: Dimensional type safety
- 🔜 **Refinement types**: SMT-verified network properties
- 🔜 **GPU acceleration**: First-class GPU effects
- 🔜 **Parallel computing**: Effect-tracked parallelism

See [GitHub Issue #13](https://github.com/sounio-lang/sounio/issues/13) for implementation details.

---

## License

- **Code**: MIT License
- **Data**: CC BY 4.0
- **Manuscript**: CC BY 4.0

See `LICENSE` for details.

---

## Contact

**Demetrios Chiuratto Agourakis**
Email: demetrios@agourakis.med.br
ORCID: 0000-0002-8596-5097
GitHub: [@agourakis82](https://github.com/agourakis82)

---

## Acknowledgments

- **Small World of Words** project team
- **Sounio** programming language development
- Julia and Rust communities

---

## Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

**Current Version**: v0.2.0 (Phase Transition + Sounio Implementation)

**Previous**: v0.1.0 (Initial Julia/Rust implementation)
