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
│   ├── 01_epistemic_uncertainty/   # Phase transition sweep
│   ├── 02_null_model/              # Configuration null model ensemble
│   ├── 03_forman_ricci/            # Forman vs Ollivier comparison
│   ├── 04_uncertainty_scaling/     # Uncertainty at phase transition
│   ├── 05_hypercomplex/           # Hypercomplex curvature embedding
│   └── 06_spectral_geometry/     # Spectral gap phase transition
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

## Sounio Experiments

All experiments are self-contained `.sio` programs demonstrating the phase transition
with Sounio's effect system (`with IO, Mut, Div, Panic`) and type-safe fixed-size arrays.

### Experiment 01: Phase Transition Sweep

Ollivier-Ricci curvature across k-regular graphs (N=20, k=2..18).
Demonstrates the universal transition from hyperbolic to spherical geometry.

```bash
bash experiments/01_epistemic_uncertainty/run.sh
# → results/sounio/phase_transition_sounio.csv
```

### Experiment 02: Configuration Null Model Ensemble

5 independent realizations per k-value from the configuration model C(N,k).
Tests whether curvature is a structural invariant of the degree sequence.

```bash
bash experiments/02_null_model/run.sh
# → results/sounio/configuration_null.csv
```

### Experiment 03: Forman-Ricci vs Ollivier-Ricci

Compares two discrete Ricci curvature notions on the same graphs:

- **Forman**: combinatorial O(deg²) per edge, no optimal transport
- **Ollivier**: optimal transport O(n² × sinkhorn_iter) per edge

```bash
bash experiments/03_forman_ricci/run.sh
# → results/sounio/forman_comparison.csv
```

### Experiment 04: Uncertainty Scaling at Phase Transition

Multi-seed ensemble analysis with Shannon entropy of geometry classification.
Shows that epistemic uncertainty peaks at the phase transition (k²/N ≈ 2.5).

```bash
bash experiments/04_uncertainty_scaling/run.sh
# → results/sounio/uncertainty_scaling.csv
```

### Experiment 05: Hypercomplex Curvature Embedding

Embeds graph nodes into hypercomplex hyperspheres — S³ (quaternion), S⁷ (octonion),
S¹⁵ (sedenion) — via landmark BFS distances, then computes Ollivier-Ricci curvature
using geodesic distances instead of integer hop-counts. Showcases Hamilton product
(associative) and Cayley-Dickson product (non-associative).

- **Phase A** (N=20): Validates embeddings reproduce the known phase transition
- **Phase B** (N=50): Breaks the N=20 barrier using landmark-based embedding

```bash
bash experiments/05_hypercomplex/run.sh
# → results/sounio/hypercomplex_curvature.csv
```

### Experiment 06: Spectral Geometry of Phase Transition

Independent validation via eigenvalues of the adjacency matrix. Computes the second
eigenvalue λ₂ using power iteration on the shifted matrix (A+kI) with deflation
against the known trivial eigenvector. Derives spectral gap, algebraic connectivity,
Cheeger constant lower bound, and Friedman ratio.

- **Phase A** (N=20): Spectral + Ollivier-Ricci curvature for direct comparison
- **Phase B** (N=50): Spectral only (cross-reference with experiment 05)

```bash
bash experiments/06_spectral_geometry/run.sh
# → results/sounio/spectral_phase_transition.csv
```

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

### Complete

- Julia reference implementation (N=200, 11 networks)
- Rust performance implementation (Sinkhorn + null models)
- Sounio graph module (in [Sounio repo](https://github.com/sounio-lang/sounio))
- Phase transition discovery and validation
- Sounio Experiments 01-06 (phase transition, null model, Forman, uncertainty, hypercomplex, spectral)
- Scientific documentation

### In Progress

- Cross-language benchmarking (Julia vs Sounio numerical agreement)
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
