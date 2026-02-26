# fMRI Brain Connectivity Analysis
# Hyperbolic Semantic Networks Project

This directory contains code for analyzing brain connectivity networks from fMRI data and correlating them with semantic network geometry.

## Quick Start

### 1. Download HCP Data

**Option A: Automated (AWS S3)**
```bash
# Verify AWS CLI is installed
python code/fmri/download_hcp_data.py --method verify

# Download 10 subjects from AWS S3 (free, no credentials needed)
python code/fmri/download_hcp_data.py --method aws
```

**Option B: Manual (ConnectomeDB)**
```bash
# Print manual download instructions
python code/fmri/download_hcp_data.py --method manual

# Then follow the instructions to download from:
# https://db.humanconnectome.org
```

### 2. Construct Brain Networks

```bash
# Extract time series and build connectivity matrices
python code/fmri/brain_network_construction.py \
    --subjects 100307 100408 101107 \
    --parcellation schaefer400 \
    --threshold 0.3
```

### 3. Compute Curvature

```bash
# Apply Ollivier-Ricci curvature to brain graphs
julia code/fmri/compute_brain_curvature.jl \
    --input results/fmri/connectivity_matrices/ \
    --output results/fmri/curvature/
```

### 4. Correlate with Semantic Networks

```bash
# Semantic-brain correlation analysis
python code/fmri/semantic_brain_correlation.py \
    --semantic-data results/swow/ \
    --brain-data results/fmri/curvature/ \
    --method mantel
```

## Directory Structure

```
code/fmri/
├── README.md                          # This file
├── HCP_DOWNLOAD_GUIDE.md              # Detailed download instructions
├── download_hcp_data.py               # Automated download script
├── brain_network_construction.py      # Time series → connectivity matrix
├── compute_brain_curvature.jl         # Curvature computation (Julia)
├── semantic_brain_correlation.py      # Correlation analysis
└── visualization/
    ├── plot_brain_networks.py         # Network visualization
    └── plot_correlations.py           # Correlation plots
```

## Data Flow

```
HCP fMRI Data (CIFTI)
    ↓
Parcellated Time Series (400 regions × timepoints)
    ↓
Pearson Correlation Matrix (400 × 400)
    ↓
Thresholded Brain Graph (r > 0.3)
    ↓
Ollivier-Ricci Curvature (κ_brain per edge)
    ↓
Network-Level Metrics (mean κ, clustering, degree)
    ↓
Correlation with Semantic Networks
```

## Requirements

### Python Packages
```bash
# Already installed in .venv/
pip install nilearn nibabel networkx scipy statsmodels pingouin
```

### Julia Packages
```julia
# Use existing hyperbolic-semantic-networks Julia environment
using Pkg
Pkg.activate(".")
# Already has: Graphs, LightGraphs, Statistics, CSV, DataFrames
```

### External Tools (Optional)
- **Connectome Workbench**: For CIFTI manipulation
  - Download: https://www.humanconnectome.org/software/get-connectome-workbench
  - Only needed if applying custom parcellations

## Expected Output

### Brain Network Metrics (per subject)
- `results/fmri/connectivity_matrices/<subject_id>_rest_schaefer400.npy`
- `results/fmri/curvature/<subject_id>_curvature.csv`

### Correlation Results
- `results/fmri/correlation/mantel_test_results.csv`
- `results/fmri/correlation/node_correspondence.csv`
- `results/fmri/correlation/network_metrics_comparison.csv`

### Figures
- `results/fmri/figures/brain_network_<subject_id>.png`
- `results/fmri/figures/semantic_brain_correlation.png`
- `results/fmri/figures/curvature_distribution.png`

## Validation Criteria

✓ **Brain networks are valid graphs**: No isolated nodes, connected components  
✓ **Curvature values in bounds**: κ ∈ [-1, 1]  
✓ **Correlation is significant**: p < 0.05 after FDR correction  
✓ **Effect size is meaningful**: r > 0.3 (medium effect)

## Troubleshooting

**Issue**: AWS download fails  
**Solution**: Use manual download from ConnectomeDB

**Issue**: CIFTI files don't have Schaefer parcellation  
**Solution**: Apply parcellation with Connectome Workbench (see HCP_DOWNLOAD_GUIDE.md)

**Issue**: Correlation is not significant  
**Solution**: Check sample size (need N≥30 for power), verify data quality

## Next Steps

After completing proof-of-concept (10 subjects):
1. Scale to 100+ subjects (Task B7)
2. Add additional fMRI tasks (working memory, social cognition)
3. Test cross-linguistic brain-semantic correlations
4. Prepare manuscript figures

## References

- Van Essen et al. (2013). The WU-Minn Human Connectome Project. NeuroImage.
- Schaefer et al. (2018). Local-Global Parcellation of the Human Cerebral Cortex. Cerebral Cortex.
- Ollivier (2009). Ricci curvature of Markov chains on metric spaces. Journal of Functional Analysis.

