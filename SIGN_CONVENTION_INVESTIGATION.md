# 🚨 SIGN CONVENTION INVESTIGATION - κ > 0 vs κ < 0
**Problem:** Inconsistent sign conventions across repos!  
**Impact:** CRITICAL - affects ALL interpretations  
**Priority:** Resolve IMMEDIATELY before any manuscript changes

---

## 📊 OBSERVED INCONSISTENCY

### **This Repo (hyperbolic-semantic-networks):**
**Convention:**
```
κ < 0  →  HYPERBOLIC (negative curvature)
κ = 0  →  EUCLIDEAN (flat)
κ > 0  →  SPHERICAL (positive curvature)
```

**Our values:**
- Spanish: κ = -0.155 (we call this "hyperbolic")
- Config null: κ = -0.240 (we call this "more hyperbolic")

---

### **pcs-meta-repo (KEC paper):**
**Convention (from track_d_alpha_paper):**
```
κ > 0  →  "Hyperbolic" (tree-like, hierarchical)
κ ≈ 0  →  Flat
κ < 0  →  Positively curved (high clustering)
```

**Their interpretation:**
- "κ > 0" = hyperbolic, hierarchical
- "κ < 0" = spherical, clustered

---

## 🔍 WHICH IS CORRECT?

### **Standard Mathematical Definition (Riemannian Geometry):**

**Gaussian curvature K:**
```
K < 0  →  HYPERBOLIC (saddle surface)
K = 0  →  FLAT (plane)
K > 0  →  SPHERICAL (sphere surface)
```

**Ricci curvature Ric:**
```
Ric < 0  →  HYPERBOLIC (volume grows exponentially)
Ric = 0  →  FLAT
Ric > 0  →  SPHERICAL (volume contracts)
```

**This is STANDARD in differential geometry!**

---

### **Ollivier-Ricci Definition:**

**From Ollivier (2009):**
```
κ_OR(x,y) = 1 - W₁(μₓ, μᵧ) / d(x,y)
```

Where:
- W₁ = Wasserstein distance
- d(x,y) = edge length

**Interpretation:**
- W₁ small → neighborhoods similar → κ close to 1 (POSITIVE)
- W₁ large → neighborhoods diverge → κ negative (or small positive)

**WAIT - Ollivier uses POSITIVE for "good" curvature (spherical)!**

---

## 🎯 RESOLVING THE CONFUSION

### **GraphRicciCurvature Library Convention:**

Need to check: Does library return:
- Standard Ricci (negative = hyperbolic)?
- Or Ollivier's definition (positive = spherical)?

**Test:**
```python
# Known hyperbolic network (tree)
G_tree = nx.balanced_tree(3, 3)
orc = OllivierRicci(G_tree, alpha=0.5)
orc.compute_ricci_curvature()
κ_tree = mean([...])

# If κ_tree < 0: Library uses standard (negative = hyperbolic)
# If κ_tree > 0: Library may use different convention
```

---

## 🔬 IMMEDIATE TEST NEEDED


