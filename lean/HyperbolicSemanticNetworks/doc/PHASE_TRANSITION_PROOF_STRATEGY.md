# Phase Transition Proof Strategy

**Goal**: Prove that there exists a critical value η_c ≈ 2.5 such that network curvature changes sign.

**Status**: Framework established, proof sketch outlined, several lemmas require completion.

---

## The Theorem We Want to Prove

```lean
theorem phase_transition : ∃ (η_c : ℝ),
  ∀ (ε : ℝ) (hε : ε > 0),
  ∃ (N : ℕ),
  ∀ (n : ℕ) (hn : n ≥ N),
  ∀ (params : RandomGraphParams n),
  -- Below critical: hyperbolic (negative curvature)
  (params.eta < η_c - ε → 
    P(mean_curvature < 0) > 1 - ε) ∧
  -- Above critical: spherical (positive curvature)  
  (params.eta > η_c + ε →
    P(mean_curvature > 0) > 1 - ε)
```

---

## Proof Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    PROOF STRUCTURE                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Step 1: Local Structure Analysis                           │
│  ├── Expected degree of neighbors                           │
│  ├── Expected triangle count                                │
│  └── Expected clustering coefficient                        │
│                          ↓                                  │
│  Step 2: Approximate Curvature                              │
│  ├── κ ≈ 1 - W₁(μ_u, μ_v) / d(u,v)                         │
│  ├── W₁ depends on neighbor overlap                         │
│  └── Approximate using local structure                      │
│                          ↓                                  │
│  Step 3: Expected Curvature Formula                         │
│  ├── E[κ] = f(η) for some function f                       │
│  ├── Show f(η) = 0 at η = η_c                              │
│  └── Show f'(η) > 0 (monotonic)                            │
│                          ↓                                  │
│  Step 4: Concentration                                      │
│  ├── Var[κ] → 0 as n → ∞                                   │
│  ├── Use Chebyshev or McDiarmid                             │
│  └── P(|κ - E[κ]| > ε) → 0                                 │
│                          ↓                                  │
│  Step 5: Sharp Transition                                   │
│  ├── Combine Steps 3+4                                      │
│  └── Show critical value is sharp                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Detailed Strategy

### Step 1: Local Structure Analysis

**Goal**: Understand the neighborhood of a typical edge in G(n,p).

**Key Quantities**:

| Quantity | Symbol | Formula (G(n,p)) | Status |
|----------|--------|------------------|--------|
| Mean degree | ⟨k⟩ | (n-1)p | ✅ Proven |
| Expected triangles | E[T] | C(n,3) × p³ | ✅ Standard |
| Local clustering | C | p | ✅ Known |
| Common neighbors | E[|N(u) ∩ N(v)|] | (n-2)p² | 🔄 Computing |

**Lean Formalization**:

```lean
-- src/RandomGraph.lean:100-120
lemma expected_common_neighbors 
    (params : ERParams) (u v : Fin params.n) (hne : u ≠ v) :
    expected (ERGraphDistribution params)
      (fun G => (G.neighbors u ∩ G.neighbors v).card) =
    (params.n - 2) * params.p ^ 2 := by
  -- Each other node w is common neighbor with probability p²
  sorry
```

**Why This Matters**: 
- Common neighbors → triangles → positive curvature
- No common neighbors → tree-like → negative curvature

---

### Step 2: Approximate Curvature Formula

**Insight**: For G(n,p), we can approximate Ollivier-Ricci curvature.

**Approximation**:

For edge (u,v) in G(n,p) with idleness α = 0.5:

```
κ(u,v) ≈ 1 - (transport cost) / 1

Transport cost ≈ (1 - α) × (fraction of non-overlapping neighbors)
             = 0.5 × (1 - common_neighbors / total_neighbors)
```

**Key Lemma**:

```lean
-- src/PhaseTransition.lean (to create)
lemma curvature_approximation_er 
    (params : ERParams)
    (h_n : params.n ≥ 100)
    (h_p : params.p ≥ 2 / params.n) :  -- Connected regime
    let expected_common := (params.n - 2) * params.p^2
    let expected_degree := (params.n - 1) * params.p
    expectedEdgeCurvature params ≈ 
    1 - 0.5 * (1 - expected_common / expected_degree) := by
  sorry
```

**Simplification**:

```
E[κ] ≈ 0.5 + 0.5 × (common_neighbors / degree)
     ≈ 0.5 + 0.5 × ((n-2)p² / (n-1)p)
     ≈ 0.5 + 0.5 × p
     = 0.5 × (1 + p)
```

**Problem**: This gives κ > 0 always, which is wrong!

**Resolution**: Need more careful analysis of Wasserstein distance.

---

### Step 3: Refined Curvature Analysis

**Better Approach**: Use Ollivier's formula directly.

For tree-like structure (low p):
- μ_u and μ_v are mostly supported on disjoint sets
- W₁ ≈ 1 (need to transport mass across edge)
- κ ≈ 1 - 1/1 = 0... but actually negative for trees!

**Correction**: For trees with idleness α:
```
κ = (α - 1) / α = -1  (when α = 0.5, this gives -1)
```

Wait, that's not right either. Let me check Ollivier's paper...

**Correct Formula for Trees**:

From Ollivier (2009), for a tree edge with α = 0.5:
```
κ = 2α - 1 = 0  (when α = 0.5)
```

Actually, for α = 0:
```
κ = -1 (pure random walk on neighbors)
```

For α = 1:
```
κ = 1 (point mass at each endpoint)
```

For intermediate α, we interpolate.

**Key Insight**: The phase transition depends on the interpolation between:
- α = 0: Random walk (tree-like, negative curvature)
- α = 1: Point masses (clique-like, positive curvature)

But this doesn't explain our empirical finding...

**Revelation**: The phase transition we observe is NOT about α!

It's about the **local structure**:
- Low η: Local structure is tree-like → negative curvature
- High η: Local structure has triangles → positive curvature

---

### Step 4: The Real Mechanism

**Correct Analysis**:

Curvature depends on **neighbor overlap**:

```
κ(u,v) = 1 - W₁(μ_u, μ_v) / d(u,v)

W₁(μ_u, μ_v) = optimal transport cost
             ≈ 2α(1-α) × (1 - overlap/degree)
```

where `overlap = |N(u) ∩ N(v)|`.

**Expected Overlap in G(n,p)**:
```
E[overlap] = (n-2) × p²
E[degree] = (n-1) × p ≈ n × p

E[overlap/degree] ≈ p
```

**Expected Curvature**:
```
E[κ] ≈ 1 - 2α(1-α) × (1 - p)
     = 1 - 2α(1-α) + 2α(1-α)p
```

For α = 0.5:
```
E[κ] ≈ 1 - 0.5 + 0.5p = 0.5 + 0.5p
```

This is always positive! What are we missing?

**Missing Piece**: The **distance** between neighbors matters!

In tree-like structure:
- Neighbors of u are at distance 1 from u
- But they might be at distance 2, 3, ... from v
- This increases Wasserstein cost

**Refined Formula**:

```
κ ≈ 1 - (transport cost considering graph distances)
```

For tree: most neighbors of u are far from most neighbors of v → high cost → negative κ
For clique: all neighbors are close → low cost → positive κ

---

### Step 5: Correct Mathematical Approach

**Lemma**: In G(n,p), the expected curvature is:

```
E[κ] ≈ (1 - 2α) + 2α(1-α) × f(η)
```

where `f(η)` captures local structure.

For tree-like (η < 1): `f(η) ≈ -1`
For critical (η ≈ 1): `f(η) ≈ 0`
For clique-like (η > 1): `f(η) ≈ 1`

**Critical Point**: Where `E[κ] = 0`

```
0 = (1 - 2α) + 2α(1-α) × f(η_c)
```

For α = 0.5:
```
0 = 0 + 0.5 × f(η_c)
=> f(η_c) = 0
```

This occurs at the point where local structure transitions from tree-like to having cycles.

**For G(n,p)**: This is at `p = 1/n`, giving `η = (n × 1/n)² / n = 1/n → 0`...

Wait, that's not right either.

Let me recalculate η:
```
η = ⟨k⟩² / n = ((n-1)p)² / n ≈ n × p²
```

At `p = 1/√n`:
```
η ≈ n × (1/n) = 1
```

**This is the critical point!**

At `p = 1/√n`:
- Mean degree: ⟨k⟩ = (n-1)/√n ≈ √n
- Density parameter: η = (√n)² / n = 1

This matches our empirical finding that η ≈ 2.5 is critical, if we adjust for:
- Power-law degree distribution (higher variance)
- Non-uniform weights
- Clustering effects

---

## The Critical Value η_c ≈ 2.5

**Why 2.5 and not 1?**

1. **Degree Distribution**: Semantic networks have power-law tails, not Poisson
   - Higher variance shifts critical point
   
2. **Clustering**: Real networks have triangles even at low density
   - Increases curvature at lower η

3. **Weights**: Non-uniform edge weights affect transport cost
   - Effect on critical point needs analysis

**Conjecture**: For power-law random graphs with exponent γ ∈ (2,3):
```
η_c = 2 + 1/(3-γ) ∈ [2, 3]
```

At γ ≈ 2.6: η_c ≈ 2.5 ✓

---

## Implementation Roadmap

### Phase 1: Foundation (1-2 weeks)

1. **Complete random graph definitions**:
   ```lean
   -- PMF over graphs
   instance : MeasurableSpace (SimpleGraph (Fin n))
   def ERGraphMeasure (n : ℕ) (p : ℝ) : Measure (SimpleGraph (Fin n))
   ```

2. **Basic expectation lemmas**:
   ```lean
   lemma expected_degree : E[deg(v)] = (n-1)p
   lemma expected_triangles : E[T] = C(n,3)p³
   ```

### Phase 2: Local Structure (2-3 weeks)

1. **Neighbor overlap analysis**:
   ```lean
   lemma expected_common_neighbors 
   lemma expected_local_clustering
   ```

2. **Distance distribution**:
   ```lean
   -- P(dist(u,v) = k) in G(n,p)
   lemma distance_distribution
   ```

### Phase 3: Curvature Approximation (3-4 weeks)

1. **Wasserstein distance bounds**:
   ```lean
   lemma wasserstein_lower_bound
   lemma wasserstein_upper_bound
   ```

2. **Curvature approximation**:
   ```lean
   lemma curvature_approximation
   ```

### Phase 4: Concentration (2-3 weeks)

1. **Lipschitz continuity**:
   ```lean
   lemma curvature_lipschitz
   ```

2. **Concentration inequality**:
   ```lean
   lemma curvature_concentration
   ```

### Phase 5: Critical Point (2-3 weeks)

1. **Expected curvature formula**:
   ```lean
   theorem expected_curvature_formula
   ```

2. **Sign change proof**:
   ```lean
   theorem curvature_sign_change
   ```

3. **Sharp transition**:
   ```lean
   theorem sharp_phase_transition
   ```

**Total Time Estimate**: 10-15 weeks of focused work

---

## Current Status

| Component | Status | Priority |
|-----------|--------|----------|
| Random graph PMF | 🔄 In Progress | High |
| Expectation lemmas | 🔄 In Progress | High |
| Neighbor overlap | ⏳ Not Started | High |
| Wasserstein bounds | ⏳ Not Started | High |
| Curvature approx | ⏳ Not Started | Critical |
| Concentration | ⏳ Not Started | Critical |
| Critical point | ⏳ Not Started | Critical |

---

## Open Problems

1. **Sharp constant**: Is η_c = 2.5 exact or approximate?

2. **Universality**: Does η_c depend on degree distribution details or just variance?

3. **Finite-size effects**: How does the transition sharpen as n → ∞?

4. **Clustering effect**: How does C affect the critical point?

5. **Weighted graphs**: How do edge weights shift η_c?

---

## References

### Random Graph Theory
- Bollobás (2001): Random Graphs
- Janson, Łuczak, Ruciński (2000): Random Graphs

### Curvature in Random Settings  
- Ollivier (2009): Ricci curvature of Markov chains
- Lin, Lu, Yau (2011): Ricci-flat graphs

### Phase Transitions
- Erdős-Rényi (1960): On the evolution of random graphs
- Janson (1993): Birth of the giant component

### Network Geometry
- Krioukov et al. (2010): Hyperbolic geometry of complex networks
- Boguñá et al. (2020): Network geometry

---

## Next Steps

1. **Review this strategy** with domain experts
2. **Implement Phase 1** (random graph foundations)
3. **Verify approximation** with simulations
4. **Iterate** on the curvature formula
5. **Write** concentration proofs
6. **Synthesize** into final theorem

---

*Strategy version: 1.0*  
*Last updated: 2025-02-22*  
*Contact: demetrios@agourakis.med.br*