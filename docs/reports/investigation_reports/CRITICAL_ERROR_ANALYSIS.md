# 🚨 CRITICAL ERROR ANALYSIS - Dataset Inconsistency
**Date:** November 5, 2025  
**Severity:** FATAL (manuscript invalid)  
**Reviewer:** #1 (100% correct)

---

## PROBLEM IDENTIFIED

### **Inconsistency:**
- **Table 1:** Chinese κ = -0.189 (hyperbolic)
- **§3.4 text:** Chinese κ = +0.161 (spherical)
- **Magnitude:** Opposite signs, Δκ ≈ 0.35

### **Root Cause:**
**TWO DIFFERENT DATASETS mixed in manuscript!**

**Original Analysis (Table 1):**
```
Chinese network: 500 nodes, 799 edges
κ_mean = -0.189 (NEGATIVE - hyperbolic)
Source: Unknown (original v1.7-v1.8 analysis)
```

**Substructure Analysis (executed today in response to simulated review):**
```
Chinese network: 500 nodes, 9,055 edges (11x denser!)
κ_mean = +0.173 (POSITIVE - spherical)
Source: data/processed/chinese_edges.csv (freshly preprocessed)
```

**These are COMPLETELY DIFFERENT NETWORKS!**

---

## WHY THIS HAPPENED

### **Timeline of Error:**

1. **Original manuscript (v1.7-v1.8):**
   - Used Chinese network with 799 edges
   - Computed κ = -0.189 (hyperbolic)
   - Consistent with other 3 languages

2. **Today (simulated peer review response):**
   - Ran `preprocess_swow_to_edges.py` 
   - Generated NEW chinese_edges.csv with different parameters
   - Result: 9,055 edges (much denser network)
   - Computed κ = +0.173 on THIS NEW NETWORK

3. **Integration error:**
   - Rewrote §3.4 based on NEW substructure results
   - Did NOT update Table 1 (still has OLD values)
   - Created catastrophic inconsistency

---

## WHICH DATASET IS CORRECT?

### **Need to determine:**

**Option A: Original dataset (799 edges) is correct**
- Table 1 stays as-is
- DELETE §3.4 (script-geometry hypothesis)
- Manuscript conclusion: "4/4 languages hyperbolic"
- Conservative but consistent

**Option B: New dataset (9,055 edges) is correct**
- UPDATE Table 1 to match new analysis
- KEEP §3.4 (script-geometry hypothesis)
- Manuscript conclusion: "3/4 alphabetic hyperbolic, 1/1 logographic spherical"
- Revolutionary but requires complete reanalysis

**Option C: BOTH are wrong (need to re-preprocess)**
- Find ORIGINAL preprocessing parameters
- Regenerate Chinese network matching Spanish/English/Dutch methodology
- Recompute everything consistently

---

## IMMEDIATE ACTIONS REQUIRED

### **Step 1: Locate Original Chinese Network (URGENT)**

```bash
# Search for original edge file or processing script
find . -name "*chinese*" -type f | grep -v ".git"

# Check if original raw data still exists
ls -lh data/raw/SWOW-ZH*/

# Check git history for original preprocessing
git log --all --full-history -- "data/processed/chinese*"
```

### **Step 2: Compare Preprocessing Parameters**

For Spanish/English/Dutch (which ARE consistent):
```python
# What parameters were used?
# - Edge weight threshold?
# - Number of nodes selected (top N)?
# - R1 only or R1+R2+R3?
# - Minimum weight cutoff?
```

For Chinese (which is INCONSISTENT):
```python
# What parameters SHOULD have been used?
# Match exactly to other 3 languages
```

### **Step 3: Decision Matrix**

| Scenario | Chinese edges | Action | Manuscript Impact |
|----------|---------------|--------|-------------------|
| **A** | 799 (original) | Keep Table 1, delete §3.4 | Conservative, 4/4 hyperbolic |
| **B** | 9,055 (new) | Update Table 1, keep §3.4 | Revolutionary, script-geometry |
| **C** | Recompute | Full reanalysis | Unknown until done |

---

## REVIEWER'S VERDICT: CORRECT

Reviewer #1 is **100% RIGHT:**

> "Esta contradição de sinal oposto torna o manuscrito cientificamente inválido 
> até que seja resolvida."

**Verdict:** REJECT with invitation to resubmit after correction

**Timeline for correction:**
- Option A or B: 2-3 days (choose & update)
- Option C: 1-2 weeks (full reanalysis)

---

## RECOMMENDATION

### **My Assessment:**

**Most Likely Scenario:** Original analysis (799 edges) is correct because:
1. It's consistent with Table 3A (κ_real ≈ 0.001, near-zero)
2. It matches the N edges for other languages (776-817 range)
3. The 9,055 edge network is suspiciously dense (mean degree 36.22 vs ~3.2 for others)

**Preprocessing error in chinese_edges.csv:**
- Likely used wrong threshold or aggregation
- Should have filtered to match Spanish/English/Dutch density

**CORRECT ACTION:**

1. **Find/regenerate Chinese network with ~800 edges** (matching others)
2. **Recompute curvature on THIS network**
3. **If κ still negative:** Keep Table 1, delete §3.4, paper is 4/4 hyperbolic (less exciting but solid)
4. **If κ becomes positive:** Extraordinary finding, but need full robustness check

---

## CRITICAL LESSON

**Never mix datasets mid-analysis!**

When responding to reviews:
- ✅ Run NEW tests on SAME data
- ❌ DON'T generate NEW data and mix with OLD results
- ✅ ALWAYS verify consistency across all tables/figures/text

This error would have been caught by:
- Cross-checking Table 1 vs. text values
- Verifying edge counts match across languages
- Running consistency checks before finalizing

---

**STATUS:** Manuscript INVALID until resolved  
**PRIORITY:** CRITICAL (blocks all other revisions)  
**OWNER:** Must be fixed by author


