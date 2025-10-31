# Supplementary Material S1: Detailed Methods

**Manuscript**: Consistent Evidence for Hyperbolic Geometry in Semantic Networks  
**Authors**: Chiuratto Agourakis, D.  
**Journal**: Network Science

---

## S1.1 Network Construction (Extended)

### Data Preprocessing

**SWOW Dataset Download**:
```python
# Download from smallworldofwords.org
# Files: SWOW-EN.R100.csv, SWOW-ES.R100.csv, SWOW-NL.R100.csv, SWOW-ZH.R100.csv
```

**Node Selection Criteria**:
1. Select top 500 most frequent cue words (ranked by total response frequency)
2. Exclude non-alphabetic tokens (numbers, punctuation)
3. Lowercase normalization (Spanish/Dutch/English)
4. Character encoding: UTF-8 (Chinese)

**Edge Construction**:
- Type: Directed (cue → response)
- Weight: Forward strength R1 (first response probability)
- Formula: weight(u→v) = count(u→v) / total_responses(u)
- Threshold: Include all R1 responses (no minimum threshold for base network)

**Graph Properties** (per language):

| Language | Nodes | Edges | Mean Degree | Density | Components |
|----------|-------|-------|-------------|---------|------------|
| Spanish  | 500   | 776   | 3.10        | 0.0031  | 1 (WCC)    |
| Dutch    | 500   | 817   | 3.27        | 0.0033  | 1 (WCC)    |
| Chinese  | 500   | 799   | 3.20        | 0.0032  | 1 (WCC)    |
| English  | 500   | 815   | 3.26        | 0.0033  | 1 (WCC)    |

---

## S1.2 Ollivier-Ricci Curvature (Extended)

### Algorithm Details

**Implementation**: GraphRicciCurvature v0.5.3 (Python)

**Parameters**:
- `alpha` (α): 0.5 (balanced transport)
- `method`: "OllivierRicci"
- `weight`: "weight" (edge attribute)
- `base`: 1.0 (Wasserstein exponent)
- `exp_power`: 1 (no exponential decay)
- `proc`: 8 (parallel processes)
- `shortest_path`: "all_pairs" (precompute)

**Convergence Criteria**:
- Max iterations: 100
- Tolerance: 1e-6 (Wasserstein distance change)
- Typical convergence: 15-30 iterations

**Computation Time** (per language):
- Curvature initialization: ~5 min
- Iterative refinement: ~45 min  
- Validation: ~10 min
- **Total**: ~60 min per language

### Mathematical Details

**Ollivier-Ricci Curvature Formula**:

For edge (u,v), curvature κ(u,v) is defined as:

κ(u,v) = 1 - W₁(μᵤ, μᵥ) / d(u,v)

where:
- μᵤ, μᵥ are probability measures on neighborhoods N(u), N(v)
- W₁ is the 1-Wasserstein (Earth Mover's) distance
- d(u,v) is the graph distance (here: 1 for direct edges)

**Neighborhood Measure** (α = 0.5):

μᵤ(x) = {
  0.5           if x = u (self-loop probability)
  0.5/deg(u)    if x ∈ N(u) (neighbors equally weighted)
  0             otherwise
}

**Wasserstein Distance** (computed via linear programming):

W₁(μᵤ, μᵥ) = min_{T} Σ T(x,y) · d(x,y)

subject to: Σ_y T(x,y) = μᵤ(x), Σ_x T(x,y) = μᵥ(y)

where T is the optimal transport plan.

---

## S1.3 Null Model Generation (Extended)

### Erdős-Rényi (ER)

**Parameters**:
- n = 500 (nodes)
- p = m / (n(n-1)) where m = observed edges
- p_spanish = 776 / 249500 = 0.00311
- p_dutch = 817 / 249500 = 0.00327
- p_chinese = 799 / 249500 = 0.00320
- p_english = 815 / 249500 = 0.00327

**Generation**:
```python
import networkx as nx
G_er = nx.erdos_renyi_graph(n=500, p=0.0032, seed=123)
```

**Iterations**: 100 per language  
**Total**: 400 ER graphs

### Barabási-Albert (BA)

**Parameters**:
- n = 500 (nodes)
- m = ⌈edges/nodes⌉ = ⌈800/500⌉ = 2 (edges added per new node)

**Generation**:
```python
G_ba = nx.barabasi_albert_graph(n=500, m=2, seed=123)
```

**Iterations**: 100 per language  
**Total**: 400 BA graphs

### Watts-Strogatz (WS)

**Parameters**:
- n = 500 (nodes)
- k = 2m = 4 (initial neighbors, must be even)
- p = 0.1 (rewiring probability, standard)

**Generation**:
```python
G_ws = nx.watts_strogatz_graph(n=500, k=4, p=0.1, seed=123)
```

**Iterations**: 100 per language  
**Total**: 400 WS graphs

### Lattice (2D Grid)

**Parameters**:
- side = ⌊√500⌋ = 22
- Total nodes = 22 × 22 = 484 (≈500)
- Structure: Regular 2D grid with 4-connectivity

**Generation**:
```python
G_lattice = nx.grid_2d_graph(22, 22)
# Convert to simple graph (remove tuple node labels)
G_lattice = nx.convert_node_labels_to_integers(G_lattice)
```

**Iterations**: 100 per language  
**Total**: 400 Lattice graphs

---

## S1.4 Statistical Tests (Extended)

### Null Model Comparison

**Test**: One-sample t-test  
**Null hypothesis**: μ_real = μ_null  
**Alternative**: μ_real ≠ μ_null (two-tailed)

**For each language × model**:
```python
from scipy import stats

# Real curvature
kappa_real = -0.152  # Spanish example

# Null curvatures (N=100)
kappa_nulls = [-0.998, -0.997, ..., -0.999]  # ER example

# T-test
t_stat, p_value = stats.ttest_1samp(kappa_nulls, kappa_real)

# Effect size (Cohen's d)
mean_null = np.mean(kappa_nulls)
std_null = np.std(kappa_nulls)
cohens_d = (kappa_real - mean_null) / std_null
```

**Results** (all 16 comparisons):
- All p < 0.0001 (highly significant)
- All Cohen's d > 10 (very large effect)

### Parameter Sensitivity

**Test**: Coefficient of Variation (CV)

CV = (σ / |μ|) × 100%

where:
- σ = standard deviation across parameter values
- μ = mean across parameter values

**Interpretation**:
- CV < 10%: Highly robust
- CV < 15%: Robust
- CV > 20%: Sensitive

**Our results**: CV = 11.5% (ROBUST)

---

## S1.5 Power-Law Fitting (Extended)

### Clauset et al. (2009) Protocol

**Step 1**: Estimate xmin (lower bound of power-law regime)

For each candidate xmin:
1. Fit power-law to data ≥ xmin
2. Compute KS statistic
3. Select xmin minimizing KS

**Step 2**: Estimate α (power-law exponent)

Maximum likelihood estimator:

α = 1 + n [Σᵢ ln(xᵢ / xmin)]⁻¹

where n = number of data points ≥ xmin

**Step 3**: Goodness-of-fit test

1. Generate 100 synthetic power-law datasets (same n, α, xmin)
2. Fit each synthetic dataset
3. Compute KS statistic for each
4. p-value = fraction of synthetic KS ≥ observed KS

**Interpretation**:
- p > 0.1: Plausible power-law
- p < 0.1: Poor power-law fit

**Step 4**: Likelihood ratio test

Compare power-law vs. alternative distributions:

R = ln(ℒ_powerlaw / ℒ_alternative)

- R > 0: Power-law better
- R < 0: Alternative better
- |R| > 2.6: Significant (p < 0.01)

**Our results**:
- All p < 0.001 (poor power-law fit)
- All R_lognormal < -150 (lognormal much better)
- Conclusion: Broad-scale, not scale-free

---

## S1.6 Computational Resources

**Hardware**:
- CPU: Intel Core i7-11700K @ 3.6 GHz
- Cores: 8 physical, 16 threads
- RAM: 32 GB DDR4 @ 3200 MHz
- Storage: 1 TB NVMe SSD
- GPU: Not used (curvature is CPU-only)

**Software**:
- OS: Ubuntu 22.04 LTS
- Python: 3.10.12
- NetworkX: 3.1
- NumPy: 1.24.3
- SciPy: 1.11.1
- Matplotlib: 3.7.1
- Seaborn: 0.12.2
- GraphRicciCurvature: 0.5.3
- powerlaw: 1.5

**Runtime Breakdown** (per language):

| Task | Time | RAM | CPU |
|------|------|-----|-----|
| Network construction | 5 min | 500 MB | 10% |
| OR curvature computation | 60 min | 2 GB | 95% |
| Null model generation | 30 min | 1 GB | 80% |
| Power-law fitting | 10 min | 200 MB | 50% |
| Sensitivity analysis | 20 min | 800 MB | 90% |
| **Total** | **125 min** | **Peak 2 GB** | **Avg 65%** |

**Total for 4 languages**: ~8.5 hours (parallelizable)

---

## S1.7 Data Availability

**SWOW Data**:
- Source: https://smallworldofwords.org
- Files downloaded:
  - `SWOW-EN.R100.csv` (English, 12,292 cues, 10.5 MB)
  - `SWOW-ES.R100.csv` (Spanish, 9,156 cues, 7.8 MB)
  - `SWOW-NL.R100.csv` (Dutch, 12,571 cues, 10.9 MB)
  - `SWOW-ZH.R100.csv` (Chinese, 8,842 cues, 9.1 MB)
- License: CC BY-NC-SA 4.0
- Citation: De Deyne et al. (2019)

**Processed Data** (in our repository):
- Edge lists: `data/processed/{lang}_edges.csv`
- Node lists: `data/processed/{lang}_nodes.csv`
- Curvature values: `data/processed/{lang}_curvatures.csv`
- Network statistics: `data/processed/{lang}_stats.json`

**Code Availability**:
- Repository: https://github.com/agourakis82/hyperbolic-semantic-networks
- DOI: 10.5281/zenodo.17489685
- License: MIT
- Main scripts:
  - `code/analysis/compute_curvature.py`
  - `code/analysis/generate_null_models.py`
  - `code/analysis/sensitivity_analysis.py`
  - `code/analysis/powerlaw_fitting.py`

---

**End of Supplementary Material S1**

