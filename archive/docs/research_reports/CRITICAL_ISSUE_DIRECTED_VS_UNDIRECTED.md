# 🚨 CRITICAL METHODOLOGICAL INCONSISTENCY DISCOVERED
**Issue:** DIRECTED vs. UNDIRECTED graph analysis  
**Impact:** FATAL - invalidates all comparisons  
**Status:** Requires immediate resolution

---

## PROBLEM IDENTIFIED

### **Discrepância de Valores:**

**Table 1 (compute_curvature_FINAL.py):**
- Spanish: κ = -0.155 (computed on UNDIRECTED graph)
- Nodes: 443, Edges: 583 (undirected)

**Null Script (07_structural_nulls_single_lang.py):**
- Spanish: κ_real = -0.382 (computed on DIRECTED graph!)
- Nodes: 443, Edges: 749 (directed)

**Difference:** 2.5× more negative when using directed!

---

## ROOT CAUSE

**Our direct curvature computation (`compute_curvature_FINAL.py`):**
```python
G_undir = G.to_undirected()  ← Converts to UNDIRECTED
orc = OllivierRicci(G_undir, alpha=0.5)
κ_mean = -0.155
```

**Null script (`07_structural_nulls_single_lang.py`):**
```python
# Loads directed graph
G = nx.DiGraph()
# Computes on DIRECTED graph (no to_undirected!)
orc = OllivierRicci(G, alpha=0.5)  ← DIRECTED!
κ_real = -0.382
```

**METHODOLOGICAL MISMATCH!**

---

## IMPLICATIONS

### **Which is CORRECT?**

**Manuscript §2.3 states:**
> "We computed Ollivier-Ricci curvature... preserving the directed and 
> weighted nature of semantic associations"

**This suggests DIRECTED is the intended methodology!**

**But Table 1 values are from UNDIRECTED analysis!**

---

## RESOLUTION OPTIONS

### **Option A: ALL UNDIRECTED (Simpler, Standard)**
**Action:**
- Fix null script to use `.to_undirected()`
- Keep Table 1 values (already undirected)
- Update §2.3 to clarify "analyzed as undirected"

**Pro:** Standard practice in network geometry  
**Con:** Manuscript claimed "directed" analysis

---

###  **Option B: ALL DIRECTED (Match Manuscript Text)**
**Action:**
- RECOMPUTE Table 1 using DIRECTED graphs
- Keep null results (already directed)
- Values will be MORE NEGATIVE:
  - Spanish: -0.155 → -0.382
  - English: -0.258 → -0.545
  - Chinese: -0.214 → -0.541

**Pro:** Matches §2.3 claim  
**Con:** Directed OR curvature less standard

---

## WHICH OPTION IS BETTER?

**RECOMMENDATION: Option A (UNDIRECTED)**

**Rationale:**
1. **Literature standard:** OR curvature typically computed on undirected graphs
2. **Interpretability:** Undirected curvature measures local geometry without directionality effects
3. **Simplicity:** Table 1 already has these values, less recomputation
4. **Manuscript fix:** Just clarify §2.3 (one sentence change)

**Fix for §2.3:**
```markdown
OLD: "preserving the directed and weighted nature"
NEW: "We converted directed networks to undirected (symmetrizing associations) 
      before curvature computation, following standard practice in network 
      geometry. Weights were preserved."
```

---

## IMMEDIATE ACTION REQUIRED

**KILL current null jobs** (using directed, inconsistent)

**RERUN with UNDIRECTED:**
- Fix `07_structural_nulls_single_lang.py` line ~35:
  ```python
  def load_real_network(edge_file):
      G = nx.DiGraph()
      # ... load edges ...
      G_undir = G.to_undirected()  ← ADD THIS
      return G_undir  ← RETURN UNDIRECTED
  ```

**RERUN all 3 nulls** (will be fast, ~10 min each)

---

**STATUS:** Manuscript has ANOTHER fatal inconsistency  
**PRIORITY:** CRITICAL (must fix before any submission)  
**ETA:** 1 hour to fix + rerun

---

**Estamos descobrindo camadas de inconsistências metodológicas!**  
**Isso explica POR QUE peer review é essencial!** 🔬


