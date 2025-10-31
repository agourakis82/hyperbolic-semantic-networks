# Supplementary Material S2: Complete Statistical Results

---

## S2.1 Null Model Comparison (All Iterations)

### Spanish

**Erdős-Rényi (ER)**:
- Mean κ: -0.998 ± 0.004
- Real κ: -0.152
- t-statistic: 194.60
- p-value: < 0.0001
- Cohen's d: 211.50
- 95% CI (null): [-1.006, -0.990]

**Barabási-Albert (BA)**:
- Mean κ: -1.000 ± 0.000
- Real κ: -0.152
- t-statistic: ∞ (std=0)
- p-value: < 0.0001
- Cohen's d: ∞
- Note: All BA iterations identical (deterministic structure)

**Watts-Strogatz (WS)**:
- Mean κ: -0.697 ± 0.038
- Real κ: -0.152
- t-statistic: 14.12
- p-value: < 0.0001
- Cohen's d: 14.34
- 95% CI (null): [-0.773, -0.621]

**Lattice**:
- Mean κ: -1.000 ± 0.000
- Real κ: -0.152
- t-statistic: ∞ (std=0)
- p-value: < 0.0001
- Cohen's d: ∞

---

### Dutch

**Erdős-Rényi (ER)**:
- Mean κ: -0.999 ± 0.004
- Real κ: -0.171
- t-statistic: 228.87
- p-value: < 0.0001
- Cohen's d: 207.00

**Barabási-Albert (BA)**:
- Mean κ: -1.000 ± 0.000
- Real κ: -0.171
- t-statistic: ∞
- p-value: < 0.0001
- Cohen's d: ∞

**Watts-Strogatz (WS)**:
- Mean κ: -0.690 ± 0.034
- Real κ: -0.171
- t-statistic: 16.15
- p-value: < 0.0001
- Cohen's d: 15.26

**Lattice**:
- Mean κ: -1.000 ± 0.000
- Real κ: -0.171
- t-statistic: ∞
- p-value: < 0.0001
- Cohen's d: ∞

---

### Chinese

**Erdős-Rényi (ER)**:
- Mean κ: -0.998 ± 0.003
- Real κ: -0.189
- t-statistic: 226.41
- p-value: < 0.0001
- Cohen's d: 269.67

**Barabási-Albert (BA)**:
- Mean κ: -1.000 ± 0.000
- Real κ: -0.189
- t-statistic: ∞
- p-value: < 0.0001
- Cohen's d: ∞

**Watts-Strogatz (WS)**:
- Mean κ: -0.688 ± 0.037
- Real κ: -0.189
- t-statistic: 13.37
- p-value: < 0.0001
- Cohen's d: 13.49

**Lattice**:
- Mean κ: -1.000 ± 0.000
- Real κ: -0.189
- t-statistic: ∞
- p-value: < 0.0001
- Cohen's d: ∞

---

### English

**Erdős-Rényi (ER)**:
- Mean κ: -0.998 ± 0.003
- Real κ: -0.151
- t-statistic: 275.58
- p-value: < 0.0001
- Cohen's d: 282.33

**Barabási-Albert (BA)**:
- Mean κ: -1.000 ± 0.000
- Real κ: -0.151
- t-statistic: ∞
- p-value: < 0.0001
- Cohen's d: ∞

**Watts-Strogatz (WS)**:
- Mean κ: -0.694 ± 0.036
- Real κ: -0.151
- t-statistic: 16.70
- p-value: < 0.0001
- Cohen's d: 15.08

**Lattice**:
- Mean κ: -1.000 ± 0.000
- Real κ: -0.151
- t-statistic: ∞
- p-value: < 0.0001
- Cohen's d: ∞

---

## S2.2 Parameter Sensitivity (Full Tables)

### Network Size Sweep

| Language | 250 nodes | 500 nodes | 750 nodes | 1000 nodes | Mean | CV (%) |
|----------|-----------|-----------|-----------|------------|------|--------|
| Spanish  | -0.160    | -0.153    | -0.141    | -0.135     | -0.147 | 7.2  |
| Dutch    | -0.181    | -0.170    | -0.160    | -0.149     | -0.165 | 8.1  |
| Chinese  | -0.190    | -0.181    | -0.177    | -0.170     | -0.180 | 4.6  |
| English  | -0.168    | -0.153    | -0.139    | -0.132     | -0.148 | 10.3 |

**Overall Mean**: -0.160  
**Overall CV**: 10.8%  
**Interpretation**: ROBUST

### Edge Threshold Sweep

| Language | 0.10 | 0.15 | 0.20 | 0.25 | Mean | CV (%) |
|----------|------|------|------|------|------|--------|
| Spanish  | -0.166 | -0.146 | -0.140 | -0.134 | -0.147 | 9.8  |
| Dutch    | -0.188 | -0.167 | -0.158 | -0.147 | -0.165 | 10.5 |
| Chinese  | -0.208 | -0.187 | -0.178 | -0.166 | -0.185 | 9.4  |
| English  | -0.154 | -0.146 | -0.145 | -0.125 | -0.143 | 8.7  |

**Overall Mean**: -0.160  
**Overall CV**: 13.4%  
**Interpretation**: ROBUST

### Alpha Parameter Sweep

| Language | 0.1 | 0.25 | 0.5 | 0.75 | 1.0 | Mean | CV (%) |
|----------|-----|------|-----|------|-----|------|--------|
| Spanish  | -0.144 | -0.158 | -0.150 | -0.148 | -0.142 | -0.148 | 4.5  |
| Dutch    | -0.179 | -0.181 | -0.168 | -0.169 | -0.163 | -0.172 | 4.6  |
| Chinese  | -0.201 | -0.184 | -0.192 | -0.189 | -0.181 | -0.189 | 4.3  |
| English  | -0.158 | -0.159 | -0.155 | -0.146 | -0.153 | -0.154 | 3.5  |

**Overall Mean**: -0.166  
**Overall CV**: 10.2%  
**Interpretation**: ROBUST

---

## S2.3 Power-Law Fitting (Complete Results)

### Spanish

**MLE Estimates**:
- α (alpha): 1.91
- xmin: 1
- n_tail: 500 (all data points)

**Goodness-of-Fit**:
- KS statistic: 0.640
- p-value: 0.000 (poor fit)
- Bootstrap iterations: 100

**Distribution Comparisons**:
- Log-likelihood (power-law): -1823.4
- Log-likelihood (lognormal): -1649.6
- Log-likelihood (exponential): -1833.4
- R (vs. lognormal): -173.8 (favors lognormal, p<0.001)
- R (vs. exponential): +10.0 (favors power-law, p<0.05)

**Conclusion**: Lognormal > Power-law > Exponential

### Dutch

**MLE Estimates**:
- α: 1.89
- xmin: 1
- n_tail: 500

**Goodness-of-Fit**:
- KS: 0.656
- p-value: 0.000

**Distribution Comparisons**:
- R (vs. lognormal): -162.9 (favors lognormal, p<0.001)
- R (vs. exponential): +10.0 (favors power-law, p<0.05)

### Chinese

**MLE Estimates**:
- α: 1.86
- xmin: 1
- n_tail: 500

**Goodness-of-Fit**:
- KS: 0.616
- p-value: 0.000

**Distribution Comparisons**:
- R (vs. lognormal): -151.1 (favors lognormal, p<0.001)
- R (vs. exponential): +10.0 (favors power-law, p<0.05)

### English

**MLE Estimates**:
- α: 1.95
- xmin: 1
- n_tail: 500

**Goodness-of-Fit**:
- KS: 0.684
- p-value: 0.000

**Distribution Comparisons**:
- R (vs. lognormal): -187.1 (favors lognormal, p<0.001)
- R (vs. exponential): +10.0 (favors power-law, p<0.05)

---

## S2.4 Summary Statistics

**Cross-Language Aggregates**:

| Statistic | Value |
|-----------|-------|
| Mean κ (real) | -0.166 ± 0.042 |
| Mean κ (ER null) | -0.998 ± 0.001 |
| Mean κ (BA null) | -1.000 ± 0.000 |
| Mean κ (WS null) | -0.692 ± 0.004 |
| Mean κ (Lattice null) | -1.000 ± 0.000 |
| Overall CV (sensitivity) | 11.5% |
| Mean α (power-law) | 1.90 ± 0.03 |
| Mean R (vs. lognormal) | -168.7 ± 15.1 |

**Significance Tests**:
- Null models: 16/16 comparisons significant (p < 0.0001)
- Effect sizes: Mean Cohen's d = 165.4 (huge!)
- Consistency: 100% (4/4 languages hyperbolic)

---

**End of Supplementary Material S2**

