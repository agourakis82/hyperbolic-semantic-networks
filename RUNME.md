# RUNME - Complete Reproduction Guide

**Project**: Hyperbolic Semantic Networks  
**Version**: 2.0 (Julia/Rust Migration)  
**Date**: 2025-11-08

## Quick Start

### Using Docker (Easiest)

```bash
docker build -t hyperbolic-semantic-networks .
docker run -it -v $(pwd):/workspace hyperbolic-semantic-networks
```

### Local Setup

```bash
# 1. Install Julia 1.9+ and Rust stable
# 2. Install dependencies
julia --project=julia -e 'using Pkg; Pkg.instantiate()'
cd rust && cargo build --release && cd ..

# 3. Download data (see data/README.md)
# 4. Run analyses
julia --project=julia scripts/paper1/full_pipeline.jl
```

## Complete Workflow

### Step 1: Environment Setup

```bash
# Verify installations
julia --version  # Should be 1.9+
rustc --version  # Should be stable
python --version  # Should be 3.10+ (for baseline)

# Install Julia packages
julia --project=julia -e 'using Pkg; Pkg.instantiate()'

# Build Rust libraries
cd rust
cargo build --release
cd ..
```

### Step 2: Data Preparation

```bash
# Download data files (see data/README.md for sources)
# Place in data/raw/

# Validate data
julia --project=julia scripts/validate_data.jl
```

### Step 3: Preprocessing

```bash
# Preprocess SWOW data
julia --project=julia scripts/preprocessing/swow.jl

# Preprocess ConceptNet
julia --project=julia scripts/preprocessing/conceptnet.jl

# Preprocess taxonomies
julia --project=julia scripts/preprocessing/taxonomies.jl
```

### Step 4: Compute Curvature

```bash
# Compute curvature for all networks
julia --project=julia scripts/analysis/compute_curvature.jl
```

### Step 5: Generate Null Models

```bash
# Configuration model
julia --project=julia scripts/analysis/null_models_configuration.jl

# Triadic-rewire (if implemented)
julia --project=julia scripts/analysis/null_models_triadic.jl
```

### Step 6: Statistical Analysis

```bash
# Bootstrap analysis
julia --project=julia scripts/analysis/bootstrap.jl

# Robustness analysis
julia --project=julia scripts/analysis/robustness.jl
```

### Step 7: Generate Figures

```bash
# All figures for Paper 1
julia --project=julia scripts/paper1/generate_figures.jl
```

### Step 8: Generate Tables

```bash
# All tables for Paper 1
julia --project=julia scripts/paper1/generate_tables.jl
```

## Paper-Specific Workflows

### Paper 1: Hyperbolic Geometry Boundaries

```bash
# Complete pipeline
julia --project=julia scripts/paper1/full_pipeline.jl

# This runs all steps above automatically
```

### Paper 2: Clinical Applications (Future)

```bash
# TBD - structure will be similar
julia --project=julia scripts/paper2/full_pipeline.jl
```

## Validation

### Compare with Python Baseline

```bash
# Run Python baseline
python code/analysis/compute_curvature_FINAL.py

# Compare results
julia --project=julia scripts/validation/compare_with_python.jl
```

### Validate Results

```bash
# Check all results match published values
julia --project=julia scripts/validation/validate_results.jl
```

## Expected Runtime

- Preprocessing: ~5-10 minutes
- Curvature computation: ~10-30 minutes (depending on network size)
- Null models: ~5-15 minutes
- Full pipeline: ~30-60 minutes

## Output Locations

- **Results**: `results/`
- **Figures**: `figures/paper1/`
- **Tables**: `tables/paper1/`
- **Logs**: `logs/`

## Troubleshooting

See `docs/REPRODUCIBILITY.md` for detailed troubleshooting.

## Next Steps

1. Follow setup instructions
2. Run complete pipeline
3. Validate results
4. Generate publication materials

---

**For detailed documentation, see `docs/REPRODUCIBILITY.md`**

