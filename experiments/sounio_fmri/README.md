# Sounio-fMRI Hypercomplex Geometric Deep Learning

## Overview

This implementation pushes the boundaries of **geometric deep learning** by integrating four cutting-edge methodologies for analyzing fMRI brain data and semantic networks:

1. **Geometric Scattering Transforms** - Multi-scale wavelet-based feature extraction
2. **Clifford Algebra G(3,0,1)** - Unified geometric algebra for 4D fMRI data
3. **Persistent Homology + Curvature Fusion** - Combining topology and geometry
4. **Riemannian Manifold State-Space Models** - Dynamics on curved manifolds

All with **epistemic uncertainty quantification** through Sounio's effect system.

## Architecture

```
fMRI 4D Data (x, y, z, signal)
    ↓
[Python Bridge] extract_hcp_data.py
    ↓
Quaternion Time-Series CSV
    ↓
[Sounio] Geometric Scattering Transform
    ↓
Multi-Scale Scattering Coefficients ± Uncertainty
    ↓
[Sounio] Clifford Algebra G(3,0,1)
    ↓
Multivector Representations
    ↓
[Sounio] Persistent Homology + OR Curvature
    ↓
Fused Geometric-Topological Features
    ↓
[Sounio] Riemannian Manifold
    ↓
State-Space Evolution on Manifold
    ↓
Semantic-Brain Correspondence ± Epistemic Bounds
```

## File Structure

```
hyperbolic-semantic-networks/
├── code/fmri/
│   ├── extract_hcp_data.py          # HCP data extraction bridge
│   └── validate_pipeline.py         # Validation & benchmarking
│
├── stdlib/math/                      # Sounio standard library extensions
│   ├── scattering.sio               # Geometric scattering transforms
│   ├── clifford.sio                 # Clifford algebra G(3,0,1)
│   ├── homology_curvature.sio       # Persistent homology + curvature fusion
│   └── riemannian_manifold.sio      # Manifold state-space models
│
└── experiments/sounio_fmri/
    └── integrated_pipeline.sio      # Complete integrated pipeline
```

## Key Innovations

### 1. Geometric Scattering Transforms

Wavelet-based multi-scale analysis on graphs:

```sounio
// First-order: S_1[j] = |W_j x|
// Second-order: S_2[j1,j2] = |W_j2 |W_j1 x||

let scattering = geometric_scattering_transform(
    signal, graph, config
);

// Each coefficient includes epistemic uncertainty
// std_err = σ/√n
```

**Scientific basis**: Perlmutter et al. "Understanding Graph Neural Networks with Generalized Geometric Scattering Transforms" (2023)

### 2. Clifford Algebra G(3,0,1)

Unified geometric algebra replacing separate quaternion/octonion types:

```sounio
// 4D fMRI: (x, y, z, signal) as multivector
let mv = from_fmri_4d(x, y, z, signal);

// Geometric product: ab = a·b + a∧b
let product = geometric_product(a, b);

// Rotations as rotors: v' = R v R⁻¹
let rotated = apply_rotor(rotor, vector);
```

**Scientific basis**: CliffordNet (arXiv:2601.06793) - "All You Need is Geometric Algebra"

### 3. Persistent Homology + Curvature Fusion

Combining local geometry (Ollivier-Ricci) with global topology (persistence):

```sounio
// Build filtration from graph
let filtration = build_filtration(graph, n_steps);

// Compute persistence barcodes
let barcode_0d = persistence_0d(filtration);
let barcode_1d = persistence_1d(filtration);

// Fuse with curvature
let fused = fuse_curvature_persistence(
    graph, curvature, barcode_0d, barcode_1d
);
```

**Scientific basis**: 
- "Network curvature as a hallmark of brain structural connectivity" (Nature Communications, 2019)
- Persistent homology literature (Ghrist, Carlsson)

### 4. Riemannian Manifold State-Space

Model brain dynamics as geodesic flow on curved manifolds:

```sounio
// Build metric from functional connectivity
let metrics = build_brain_metric(graph, coords, curvature);

// Create state-space model
let ssm = create_brain_ssm(manifold, semantic_embedding);

// Track correspondence trajectory
let trajectory = track_semantic_brain_correspondence(
    ssm, initial_state, n_steps
);
```

**Scientific basis**: GeoDynamics (NeurIPS 2025) - State-space models on Riemannian manifolds

## Epistemic Uncertainty Tracking

Every computation tracks uncertainty through Sounio's effect system:

```sounio
fn compute_curvature(g: Graph) -> EpistemicResult
    with Panic,    // Bounds checking
         Div,      // Division by zero protection
         Alloc,    // Memory tracking
         Confidence // Uncertainty propagation
{
    // Curvature computation with automatic uncertainty
    let curvature = ollivier_ricci_curvature(g);
    
    // Standard error from finite sampling
    let std_err = compute_standard_error(curvature);
    
    EpistemicResult {
        coefficients: curvature,
        std_err: std_err,
        scale: 0,
    }
}
```

## Usage

### 1. Extract HCP fMRI Data

```bash
cd code/fmri
python extract_hcp_data.py \
    --fmri /path/to/hcp/fmri.nii.gz \
    --output-dir ../../results/fmri \
    --atlas glasser_360 \
    --subject 100307
```

### 2. Run Integrated Pipeline (Sounio)

```bash
cd experiments/sounio_fmri
souc compile integrated_pipeline.sio -o pipeline
./pipeline
```

### 3. Validate Results

```bash
cd code/fmri
python validate_pipeline.py --mode full
```

## Validation Criteria

The pipeline is validated against:

| Test | Target | Threshold |
|------|--------|-----------|
| Julia baseline | Curvature MAE | < 1% |
| Synthetic networks | Known properties | 100% pass |
| Scattering stability | Deformation robustness | < 20% error |
| Clifford operations | Mathematical axioms | < 1e-10 error |
| Uncertainty calibration | Coverage rate | 90-99% |
| Literature benchmarks | Published values | < 20% deviation |

## Scientific Impact

### Methodological Innovations

1. **First** unified framework combining scattering + Clifford + homology + manifolds
2. **First** epistemic uncertainty quantification in geometric deep learning for neuroscience
3. **First** hypercomplex state-space models on brain manifolds

### Publication Potential

- **Target**: Nature Methods or Nature Machine Intelligence
- **Novelty**: Geometric deep learning with certified uncertainty
- **Impact**: New paradigm for brain network analysis

## Dependencies

### Python (Data Extraction)
- `nilearn` - fMRI processing
- `nibabel` - NIfTI I/O
- `numpy`, `pandas` - Data manipulation
- `networkx` - Graph operations
- `scipy` - Scientific computing

### Sounio (Core Pipeline)
- Sounio compiler (latest)
- Standard library with hypercomplex extensions

## Performance Requirements

- **RAM**: 64GB+ for persistent homology on large graphs
- **GPU**: Recommended for Clifford operations and manifold optimization
- **Storage**: ~1TB for intermediate representations
- **Time**: ~2-4 hours per subject (full pipeline)

## Timeline

- **Phase 1** (Months 1-2): Scattering + Clifford implementation
- **Phase 2** (Months 3-4): Homology + Manifold integration
- **Phase 3** (Months 5-6): Full pipeline + validation
- **Phase 4** (Months 7-8): Manuscript preparation

## Citation

If you use this code, please cite:

```bibtex
@software{sounio_fmri_hypercomplex,
  title={Hypercomplex Geometric Deep Learning for fMRI-Semantic Analysis},
  author={Agourakis, Demetrios C.},
  year={2025},
  url={https://github.com/agourakis82/hyperbolic-semantic-networks}
}
```

## References

1. Perlmutter et al. (2023) - Geometric scattering transforms
2. CliffordNet (2025) - Geometric algebra networks
3. Nature Communications (2019) - Network curvature in brain
4. GeoDynamics (2025) - State-space models on manifolds
5. Ollivier (2009) - Ricci curvature of Markov chains
6. Ghrist (2008) - Barcodes: The persistent topology of data

## License

MIT License - See LICENSE file for details

## Contact

Demetrios Chiuratto Agourakis
- Email: demetrios@agourakis.med.br
- ORCID: 0000-0002-8596-5097
- GitHub: @agourakis82
