# Reproducibility Guide

**Date**: 2025-11-08  
**Version**: 1.0

## Overview

Complete guide for reproducing all analyses and results from the Hyperbolic Semantic Networks project.

## Environment Setup

### Option 1: Docker (Recommended)

```bash
# Build Docker image
docker build -t hyperbolic-semantic-networks .

# Run container
docker run -it -v $(pwd):/workspace hyperbolic-semantic-networks

# Inside container
julia --project=julia
```

### Option 2: Local Setup

#### Prerequisites

- Julia 1.9+
- Rust toolchain (stable)
- Python 3.10+ (for baseline comparison)

#### Installation

```bash
# Clone repository
git clone https://github.com/agourakis82/hyperbolic-semantic-networks.git
cd hyperbolic-semantic-networks

# Install Julia dependencies
julia --project=julia -e 'using Pkg; Pkg.instantiate()'

# Install Rust dependencies
cd rust
cargo build --release
cd ..

# Install Python dependencies (for baseline)
pip install -r code/analysis/requirements.txt
```

## Data Setup

### Required Data Files

1. **SWOW Data**: Download from https://smallworldofwords.org
2. **ConceptNet**: Download from https://conceptnet.io
3. **Taxonomies**: WordNet, BabelNet dumps

### Data Validation

```bash
# Verify data checksums
julia --project=julia scripts/validate_data.jl

# Expected output: All checksums match
```

## Running Analyses

### Paper 1: Hyperbolic Geometry Boundaries

```bash
# Full pipeline
julia --project=julia scripts/paper1/full_pipeline.jl

# Individual steps
julia --project=julia scripts/paper1/01_preprocess.jl
julia --project=julia scripts/paper1/02_compute_curvature.jl
julia --project=julia scripts/paper1/03_null_models.jl
julia --project=julia scripts/paper1/04_analysis.jl
julia --project=julia scripts/paper1/05_figures.jl
```

### Generate All Figures

```bash
julia --project=julia scripts/generate_all_figures.jl
```

### Generate All Tables

```bash
julia --project=julia scripts/generate_all_tables.jl
```

## Reproducing Results

### Expected Outputs

All results should match published values within numerical tolerance:

- Curvature values: ±1e-6
- Network metrics: ±1e-4
- Statistical tests: p-values ±1e-3

### Validation

```bash
# Compare with published results
julia --project=julia scripts/validate_results.jl

# Expected: All validations pass
```

## Version Information

### Software Versions

- Julia: 1.9.x (see `julia/Manifest.toml`)
- Rust: stable (see `rust/Cargo.lock`)
- All dependencies: Pinned in `Manifest.toml` and `Cargo.lock`

### Data Versions

- SWOW: Version specified in data/README.md
- ConceptNet: Version specified in data/README.md
- Taxonomies: Versions specified in data/README.md

## Troubleshooting

### Common Issues

1. **Julia package errors**
   ```bash
   julia --project=julia -e 'using Pkg; Pkg.resolve()'
   ```

2. **Rust build errors**
   ```bash
   cd rust
   cargo clean
   cargo build --release
   ```

3. **Data not found**
   - Check data files are in correct locations
   - Verify checksums match

### Getting Help

- Check `docs/` for detailed documentation
- Review `RUNME.md` for step-by-step instructions
- Open issue on GitHub

## Reproducibility Checklist

- [ ] All software versions match
- [ ] All data files present and validated
- [ ] All analyses run successfully
- [ ] All results match published values
- [ ] All figures generated correctly
- [ ] All tables generated correctly

## Next Steps

1. Follow setup instructions
2. Run full pipeline
3. Validate results
4. Generate figures and tables

---

**Status**: Guide complete, ready for use

