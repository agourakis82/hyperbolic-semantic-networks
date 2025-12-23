# Scientific Claims Validation Report

**Date**: 2025-12-23
**Analyst**: Claude (Sonnet 4.5)
**Purpose**: Verify every quantitative claim in the manuscript

---

## ⚠️ CRITICAL DISCREPANCY FOUND

### Curvature Values - CONFLICTING DATA SOURCES

#### Source 1: `results/FINAL_CURVATURE_CORRECTED_PREPROCESSING.json`
| Language | κ_mean | n_edges | n_nodes |
|----------|--------|---------|---------|
| Spanish | **-0.155** | 571 | 422 |
| English | **-0.258** | 640 | 438 |
| Chinese | **-0.214** | 762 | 465 |

#### Source 2: `data/processed/statistical_tests_v6.4.json`
| Language | κ_mean | n_values (edges?) |
|----------|--------|-------------------|
| ES (Spanish) | **-0.104** | 776 |
| EN (English) | **-0.197** | 811 |
| ZH (Chinese) | **-0.189** | 799 |
| NL (Dutch) | **-0.172** | 816 |

### **ISSUE: Which values are correct?**

**Differences**:
1. **Spanish**: -0.155 vs -0.104 (Δ = 0.051, 49% difference!)
2. **English**: -0.258 vs -0.197 (Δ = 0.061, 31% difference!)
3. **Chinese**: -0.214 vs -0.189 (Δ = 0.025, 13% difference)
4. **Edge counts don't match**: 571 vs 776 (Spanish), 640 vs 811 (English)

### **Possible Explanations**:

1. **Different preprocessing versions**:
   - FINAL_CURVATURE = "CORRECT" preprocessing (R1 only?)
   - statistical_tests = "v6.4" preprocessing (different threshold?)

2. **Different network sizes**:
   - Smaller networks (571-762 edges) → more extreme κ
   - Larger networks (776-816 edges) → more moderate κ

3. **Different subgraphs**:
   - Largest connected component only?
   - Different weight thresholds?

### **ACTION REQUIRED**:
1. ✅ Identify which preprocessing is used in manuscript
2. ✅ Check if manuscript cites specific file
3. ✅ Verify network construction parameters
4. ✅ Recompute or validate final values

---

## CLAIMS TO VERIFY

### Claim 1: Association Networks κ Range
**Manuscript**: "κ = -0.17 to -0.26"

**Evidence**:
- Source 1: -0.155 to -0.258 ✅ (close)
- Source 2: -0.104 to -0.197 ⚠️ (different range!)

**Status**: **NEEDS CLARIFICATION** - which preprocessing?

---

### Claim 2: Taxonomy Networks κ ≈ 0
**Manuscript**: "taxonomy-based networks clustered near Euclidean geometry (κ ≈ 0, N=3)"

**Need to check**:
- WordNet: κ = ?
- BabelNet Russian: κ = ?
- BabelNet Arabic: κ = ?

---

### Claim 3: Power-law Exponent α = 1.90 ± 0.03
**Manuscript**: "Broad-scale topology: α = 1.90 ± 0.03"

**Status**: NOT YET VERIFIED

---

### Claim 4: Configuration Nulls Δκ = +0.17 to +0.22
**Manuscript**: "Configuration model nulls... proved significantly more hyperbolic (Δκ = +0.17 to +0.22)"

**Status**: NOT YET VERIFIED

---

### Claim 5: Clustering Regimes
**Manuscript**: "C < 0.01 (tree-like), C = 0.02-0.15 (hyperbolic), C > 0.30 (spherical)"

**Status**: NOT YET VERIFIED - need clustering coefficients for all networks

---

### Claim 6: Ricci Flow Clustering Drop
**Manuscript**: "reduces clustering by 79–86%"

**Status**: NOT YET VERIFIED

---

## NEXT STEPS

1. **Resolve curvature discrepancy**
2. **Compute network metrics table**:
   - For each network: N, E, κ, C, ⟨k⟩, α
3. **Verify null model statistics**
4. **Check Ricci flow results**
5. **Validate all p-values and effect sizes**

---

## QUESTIONS FOR AUTHORS

1. Which preprocessing version is used in the manuscript?
2. Are the "FINAL_CURVATURE_CORRECTED_PREPROCESSING" values the authoritative ones?
3. Why do edge counts differ between data sources?
4. Which networks constitute the "N=5" association networks and "N=3" taxonomies?

