# Supplementary Material S3: Code Repository Guide

**Repository**: https://github.com/agourakis82/hyperbolic-semantic-networks  
**DOI**: 10.5281/zenodo.17489685  
**License**: MIT

---

## Repository Structure

```
hyperbolic-semantic-networks/
├── data/
│   ├── raw/                    # SWOW original data
│   │   ├── SWOW-ES.R100.csv   # Spanish (9,156 cues)
│   │   ├── SWOW-NL.R100.csv   # Dutch (12,571 cues)
│   │   ├── SWOW-ZH.R100.csv   # Chinese (8,842 cues)
│   │   └── SWOW-EN.R100.csv   # English (12,292 cues)
│   └── processed/              # Derived networks
│       ├── spanish_edges.csv   # Edge list (776 edges)
│       ├── spanish_nodes.csv   # Node attributes (500 nodes)
│       ├── spanish_curvatures.csv  # Computed κ values
│       └── ... (same for other languages)
│
├── code/
│   └── analysis/
│       ├── 01_download_swow.py         # Download SWOW data
│       ├── 02_construct_networks.py    # Build networks from SWOW
│       ├── 03_compute_curvature.py     # OR curvature computation
│       ├── 04_generate_null_models.py  # ER/BA/WS/Lattice
│       ├── 05_sensitivity_analysis.py  # Parameter sweeps
│       ├── 06_powerlaw_fitting.py      # Clauset 2009 protocol
│       ├── generate_figure7_sensitivity.py  # Figure 7
│       └── generate_figure8_scalefree.py    # Figure 8
│
├── results/
│   ├── curvatures/            # OR curvature outputs
│   ├── null_models/           # Null model results
│   ├── sensitivity/           # Sensitivity analysis
│   └── powerlaw/              # Power-law fitting
│
├── manuscript/
│   ├── main.md                # Main manuscript (this)
│   ├── figures/               # All figures (PNG + PDF)
│   ├── supplement/            # S1, S2, S3
│   ├── cover_letter.md
│   └── response_to_reviewers.md
│
├── requirements.txt           # Python dependencies
├── README.md                  # Quick start guide
├── LICENSE                    # MIT License
└── CITATION.cff               # Citation metadata
```

---

## Complete Analysis Pipeline

### Step 0: Setup Environment

```bash
# Clone repository
git clone https://github.com/agourakis82/hyperbolic-semantic-networks.git
cd hyperbolic-semantic-networks

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**`requirements.txt`**:
```
networkx==3.1
numpy==1.24.3
scipy==1.11.1
matplotlib==3.7.1
seaborn==0.12.2
pandas==2.0.3
GraphRicciCurvature==0.5.3
powerlaw==1.5
statsmodels==0.14.0
```

---

### Step 1: Download SWOW Data

```bash
cd code/analysis
python 01_download_swow.py
```

**What it does**:
- Downloads 4 SWOW datasets from smallworldofwords.org
- Saves to `data/raw/`
- Validates file integrity (checksums)

**Output**:
```
Downloaded: SWOW-ES.R100.csv (7.8 MB)
Downloaded: SWOW-NL.R100.csv (10.9 MB)
Downloaded: SWOW-ZH.R100.csv (9.1 MB)
Downloaded: SWOW-EN.R100.csv (10.5 MB)
✅ All files validated
```

**Runtime**: ~5 minutes (depends on connection)

---

### Step 2: Construct Networks

```bash
python 02_construct_networks.py --languages es nl zh en
```

**What it does**:
- Selects top 500 frequent cue words per language
- Builds directed weighted networks (cue → response)
- Computes edge weights (association strength)
- Saves edge lists and node attributes

**Parameters**:
- `--n-nodes`: 500 (default)
- `--response-type`: R1 (first response, default)
- `--seed`: 42 (reproducibility)

**Output** (per language):
```
Spanish: 500 nodes, 776 edges
  Saved: data/processed/spanish_edges.csv
  Saved: data/processed/spanish_nodes.csv
```

**Runtime**: ~2 minutes per language (total 8 min)

---

### Step 3: Compute OR Curvature

```bash
python 03_compute_curvature.py --languages es nl zh en --alpha 0.5
```

**What it does**:
- Loads networks from Step 2
- Computes Ollivier-Ricci curvature (GraphRicciCurvature library)
- Uses α=0.5, max_iter=100, tolerance=1e-6
- Saves curvature values per edge

**Parameters**:
- `--alpha`: 0.5 (transport parameter, default)
- `--method`: OllivierRicci (default)
- `--proc`: 8 (parallel processes)
- `--seed`: 42

**Output** (per language):
```
Spanish:
  Edges processed: 776
  Convergence: 28 iterations (mean)
  Mean κ: -0.104
  Median κ: +0.010
  Std κ: 0.162
  Saved: data/processed/spanish_curvatures.csv
```

**Runtime**: ~60 minutes per language (total 4 hours)

**Parallelization**:
```bash
# Run all 4 languages in parallel (4 cores)
parallel python 03_compute_curvature.py --language {} ::: es nl zh en

# Runtime: ~60 minutes (parallelized)
```

---

### Step 4: Generate Null Models

```bash
python 04_generate_null_models.py --n-iterations 100 --seed 123
```

**What it does**:
- Generates 4 null model types (ER, BA, WS, Lattice)
- 100 iterations per model per language = 1,600 null networks
- Computes OR curvature for each
- Performs one-sample t-tests

**Parameters**:
- `--n-iterations`: 100 (default)
- `--models`: er,ba,ws,lattice (default: all)
- `--seed`: 123

**Output**:
```
ER (Spanish): 100 iterations
  Mean κ_null: -0.998 ± 0.004
  Real κ: -0.152
  t-test: t=194.6, p<0.0001, d=211.5
  
... (16 total comparisons)

Summary: 16/16 significant (p<0.0001)
Saved: results/null_models/null_models_results.json
```

**Runtime**: ~30 minutes (all 1,600 networks)

---

### Step 5: Sensitivity Analysis

```bash
python 05_sensitivity_analysis.py \
  --parameters n_nodes,edge_threshold,alpha_param \
  --seed 456
```

**What it does**:
- Tests 3 parameters with 4-5 values each
- Recomputes curvature for each configuration
- Calculates CV (coefficient of variation)

**Parameters tested**:
- `n_nodes`: [250, 500, 750, 1000]
- `edge_threshold`: [0.1, 0.15, 0.2, 0.25]
- `alpha_param`: [0.1, 0.25, 0.5, 0.75, 1.0]

**Output**:
```
Parameter: n_nodes
  Mean κ: -0.160
  CV: 10.8%
  
Overall CV: 11.5% (ROBUST)
Saved: results/sensitivity/sensitivity_analysis.json
```

**Runtime**: ~20 minutes

---

### Step 6: Power-Law Fitting

```bash
python 06_powerlaw_fitting.py --protocol clauset2009
```

**What it does**:
- Applies Clauset et al. (2009) complete protocol
- Estimates α, xmin via MLE
- KS goodness-of-fit test (bootstrap p-value)
- Likelihood ratio tests (vs. lognormal, exponential)

**Output**:
```
Spanish:
  α: 1.91
  xmin: 1
  KS: 0.640
  p-value: 0.000 (poor fit)
  R (lognormal): -173.8 (favors lognormal)
  R (exponential): +10.0 (favors power-law)
  
Conclusion: Broad-scale (lognormal > power-law > exponential)
Saved: results/powerlaw/scale_free_analysis.json
```

**Runtime**: ~10 minutes

---

### Step 7: Generate Figures

```bash
python generate_figure7_sensitivity.py  # Figure 7
python generate_figure8_scalefree.py    # Figure 8
```

**Output**:
```
✅ Figure 7: figure7_sensitivity_heatmaps.png (359 KB, 300 DPI)
✅ Figure 8: figure8_scalefree_diagnostics.png (483 KB, 300 DPI)
```

**Runtime**: <1 minute each

---

## Total Runtime Summary

| Step | Sequential | Parallel (4 cores) |
|------|------------|-------------------|
| 0. Setup | 5 min | 5 min |
| 1. Download | 5 min | 5 min |
| 2. Networks | 8 min | 8 min |
| 3. Curvature | 240 min (4h) | 60 min (1h) |
| 4. Null models | 30 min | 30 min |
| 5. Sensitivity | 20 min | 20 min |
| 6. Power-law | 10 min | 10 min |
| 7. Figures | 2 min | 2 min |
| **Total** | **320 min (5.3h)** | **140 min (2.3h)** |

**Recommendation**: Use parallel execution for Step 3

---

## Verification

After running pipeline, verify outputs match paper:

```bash
# Check curvatures match Table 1
grep "Mean κ" results/curvatures/spanish_stats.json
# Expected: -0.104

# Check null models match Table 3A
grep "p-value" results/null_models/null_models_results.json
# Expected: all <0.0001

# Check sensitivity matches Section 3.4
grep "Overall CV" results/sensitivity/sensitivity_analysis.json
# Expected: 11.5%

# Check power-law matches Table 2
grep "alpha" results/powerlaw/scale_free_analysis.json
# Expected: 1.90 ± 0.03
```

**All values should match manuscript exactly.**

---

## Troubleshooting

**Issue**: `ModuleNotFoundError: GraphRicciCurvature`  
**Fix**: `pip install GraphRicciCurvature==0.5.3`

**Issue**: `MemoryError` during curvature computation  
**Fix**: Reduce to 250 nodes or use machine with >16GB RAM

**Issue**: Curvature values slightly different  
**Fix**: Check random seed (must be 42 for reproducibility)

**Issue**: Slow curvature computation  
**Fix**: Use `--proc 8` for parallel processing

---

## Expected Files After Complete Run

```
data/processed/
├── spanish_edges.csv (776 rows)
├── spanish_nodes.csv (500 rows)
├── spanish_curvatures.csv (776 rows)
├── ... (×4 languages)

results/
├── curvatures/*.json (4 files)
├── null_models/null_models_results.json (35 KB)
├── sensitivity/sensitivity_analysis.json (7 KB)
└── powerlaw/scale_free_analysis.json (2 KB)

manuscript/figures/
├── figure7_sensitivity_heatmaps.png (359 KB)
└── figure8_scalefree_diagnostics.png (483 KB)
```

**Total disk space**: ~2 GB (including SWOW raw data)

---

## Citation

If you use this code, please cite:

```bibtex
@article{agourakis2025hyperbolic,
  title={Consistent Evidence for Hyperbolic Geometry in Semantic Networks Across Four Languages},
  author={Chiuratto Agourakis, Demetrios},
  journal={Network Science},
  year={2025},
  doi={10.5281/zenodo.17489685}
}
```

---

**End of Supplementary Material S3**

