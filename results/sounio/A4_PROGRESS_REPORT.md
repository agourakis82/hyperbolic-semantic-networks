# A4 Progress Report: SWOW Real Network Loading

**Status**: 🔄 IN PROGRESS  
**Date**: 2026-02-20

---

## Objective

Load real SWOW semantic networks (Spanish, English, Chinese) into Sounio and validate Ollivier-Ricci curvature computation against Julia baseline values.

---

## Julia Reference Values

| Language | Nodes | Edges | κ (Julia) | Geometry |
|----------|-------|-------|-----------|----------|
| Spanish  | 422   | 571   | -0.155    | Hyperbolic |
| English  | 438   | 640   | -0.258    | Hyperbolic |
| Chinese  | 465   | 762   | -0.214    | Hyperbolic |

Source: `results/FINAL_CURVATURE_CORRECTED_PREPROCESSING.json`

---

## Technical Challenges Identified

### 1. CSV Parsing in Sounio
**Problem**: Sounio v1.0.0-beta does not have built-in CSV parsing.

**Solutions**:
- ✅ **Option A**: Preprocess CSV to Sounio array format (Python script created)
- ⏸️ **Option B**: Implement minimal CSV parser in Sounio
- ⏸️ **Option C**: Use Julia/Rust for loading, Sounio for validation only

### 2. Network Size Variability
**Problem**: Different SWOW files have different sizes:
- `spanish_edges.csv`: 13,150 edges (500 nodes, max_deg=208)
- `spanish_edges_FINAL.csv`: Unknown (need to check)
- Julia reference: 571 edges (422 nodes)

**Action needed**: Identify which CSV file matches Julia reference (422 nodes, 571 edges)

### 3. Array Size Constraints
**Problem**: Sounio requires fixed-size arrays at compile time.

**Solution**: 
- Determine max network size upfront
- Allocate arrays: `adj[N × MAX_DEG]`, `dist[N × N]`
- For Spanish (422 nodes, max_deg≈13): ~5,500 + 178,000 = 183,500 elements

---

## Work Completed

### ✅ Preprocessing Script
Created `experiments/01_epistemic_uncertainty/preprocess_swow_for_sounio.py`:
- Converts CSV edge lists to Sounio array format
- Generates `.sio.inc` include files
- Tested on Spanish network

### ✅ Generated Files
- `swow_spanish_edges.sio.inc` (13,150 edges version)

---

## Next Steps

### Immediate (A4 Completion)
1. **Identify correct CSV files** that match Julia reference sizes
2. **Regenerate edge arrays** for correct network versions
3. **Create Sounio loader** that includes preprocessed edges
4. **Compute curvature** on real SWOW networks
5. **Validate** against Julia reference values

### Alternative Approach (Faster)
Given time constraints and Sounio's current limitations:
- **Mark A4 as "Infrastructure Complete"**
- **Defer full implementation** to after A5/A6
- **Focus on** epistemic computing showcase (A5) using synthetic networks
- **Return to A4** when Sounio has better I/O support

---

## Recommendation

**Proposed**: Pivot to **A5 (Epistemic Computing Showcase)** using the validated N=100 synthetic networks from A3.

**Rationale**:
1. A3 validation proved Sounio correctness (0.8% error)
2. A5 can demonstrate epistemic computing without real network loading
3. Real network loading requires more Sounio language development
4. Can return to A4 after core epistemic computing is demonstrated

**User decision needed**: 
- Continue A4 (real network loading)?
- Or pivot to A5 (epistemic showcase with synthetic networks)?

---

## Files Created

- `experiments/01_epistemic_uncertainty/preprocess_swow_for_sounio.py`
- `experiments/01_epistemic_uncertainty/swow_spanish_edges.sio.inc`
- `results/sounio/A4_PROGRESS_REPORT.md` (this file)

---

**Status**: Awaiting user decision on next steps.

