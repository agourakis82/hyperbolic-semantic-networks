# Theorem Mapping: Paper ↔ Lean

This document maps claims in the manuscript to formalized theorems in Lean 4.

---

## Quick Reference Table

| Paper Claim | Location | Lean Theorem | Status |
|-------------|----------|--------------|--------|
| κ ∈ [-1, 1] | Methods 2.5 | `curvature_bounds` | ✅ Proven |
| C ∈ [0, 1] | Methods 2.8 | `localClustering_bounds` | ✅ Proven |
| μ sums to 1 | Methods 2.5 | `probabilityMeasure_normalization` | ✅ Proven |
| η = ⟨k⟩²/N | Results 3.4 | `densityParameter` | ✅ Defined |
| Phase transition | Results 3.4 | `PhaseTransitionConjecture` | ⚠️ Conjecture |
| Null model shift | Results 3.3 | `configurationMoreHyperbolic` | ⚠️ Partial |

---

## Section-by-Section Mapping

### Section 2.5: Curvature Computation

**Paper Text**:
> "This procedure yields a curvature value κ ∈ [-1, 1] for each edge, where negative values indicate hyperbolic geometry, zero indicates flat (Euclidean), and positive indicates spherical."

**Lean Formalization**:
```lean
-- src/Curvature.lean:153
theorem curvature_bounds (u v : V) (α : Idleness) :
    ollivierRicci G u v α ∈ Set.Icc (-1 : ℝ) 1
```

**Proof Status**: ✅ Machine-checked  
**Proof Location**: `src/Curvature.lean:153-170`  
**Dependencies**: Wasserstein non-negativity, triangle inequality

---

**Paper Text**:
> "We analyzed the largest weakly connected component for each network."

**Lean Formalization**:
```lean
-- Implicit in graph definition
structure WeightedGraph (V : Type) [Fintype V] [DecidableEq V] where
  graph : SimpleGraph V
  -- ... connectivity handled by SimpleGraph
```

**Note**: Connected component extraction is a preprocessing step, formalized at the graph library level.

---

### Section 2.6: Discrete Ricci Flow

**Paper Text**:
> "Edge weights evolved according to dw_e/dt = -η·κ(e)·w_e"

**Lean Formalization**:
```lean
-- src/Analysis/RicciFlow.lean (planned)
structure RicciFlow where
  step : WeightedGraph V → WeightedGraph V
  convergence : ∃ n, step^[n] = step^[n+1]
```

**Proof Status**: ⚠️ Partial (convergence not proven)  
**Note**: Empirical convergence observed, formal proof requires fixed-point theory.

---

### Section 2.8: Computational Details

**Paper Text**:
> "Alpha (α): 0.5 (balanced neighborhood mixing)"

**Lean Formalization**:
```lean
-- src/Curvature.lean:45
def standard : Idleness where
  α := 0.5
  h_range := by norm_num [Set.mem_Icc]
```

**Proof Status**: ✅ Definition verified  
**Note**: Idleness bounds (α ∈ [0,1]) also proven.

---

### Section 3.1: Cross-Linguistic Curvature Profiles

**Paper Text**:
> "All three SWOW association networks exhibited negative mean Ollivier–Ricci curvature (ES: κ̄ = -0.155, EN: -0.258, ZH: -0.214)"

**Lean Formalization**:
```lean
-- src/PhaseTransition.lean:270
theorem SWOW_hyperbolic 
    (h_η : densityParameter G ∈ Set.Icc 1.5 2.0)
    (h_C : averageClustering G ∈ Set.Icc 0.02 0.05) :
    isHyperbolic G Idleness.standard
```

**Proof Status**: ⚠️ Empirical validation  
**Note**: This combines empirical data with model assumptions. Not a pure theorem.

---

### Section 3.2: Clustering Modulates Hyperbolicity

**Paper Text**:
> "Generalized additive models relating κ̄ to mean local clustering (C) revealed a non-linear regime"

**Lean Formalization**:
```lean
-- src/Basic.lean:195
theorem localClustering_bounds (v : V) :
    localClustering G v ∈ Set.Icc (0 : ℝ) 1
```

**Proof Status**: ✅ Machine-checked  
**Proof Strategy**: Counting argument showing triangles ≤ possible edges.

---

**Paper Text**:
> "The estimated 'hyperbolic sweet spot' spans C ∈ [0.023, 0.147]"

**Lean Formalization**:
```lean
-- src/PhaseTransition.lean:175
structure HyperbolicSweetSpot where
  C_min : ℝ := 0.02
  C_max : ℝ := 0.15
  h_hyperbolic : ∀ G, let C := averageClustering G
    C_min ≤ C ∧ C ≤ C_max → isHyperbolic G Idleness.standard
```

**Proof Status**: ⚠️ Empirical  
**Note**: Bounds are empirical estimates from data, not proven thresholds.

---

### Section 3.3: Structural Null Models

**Paper Text**:
> "Configuration-model nulls (M = 1000) increased hyperbolicity by Δκ = +0.17 to +0.22"

**Lean Formalization**:
```lean
-- src/PhaseTransition.lean:210
theorem configurationMoreHyperbolic 
    (G : WeightedGraph V)
    (G_null : WeightedGraph V)
    (h_sameDegree : ∀ v, G.degree v = G_null.degree v)
    (h_randomized : True) :
    meanCurvature G_null Idleness.standard ≤
    meanCurvature G Idleness.standard
```

**Proof Status**: ⚠️ Conjecture  
**Note**: Empirically observed but not yet proven. Requires showing that destroying clustering increases |κ̄|.

---

### Section 3.4: Phase Diagram

**Paper Text**:
> "Plotting network geometry in the (C, σ_k) plane produced a phase diagram where color encodes κ̄"

**Lean Formalization**:
```lean
-- src/PhaseTransition.lean:35
def densityParameter : ℝ :=
  let meanDegree := (∑ v : V, G.degree v) / (Fintype.card V : ℝ)
  meanDegree ^ 2 / (Fintype.card V : ℝ)

-- Alternative: η = 4E²/N³
lemma densityParameter_alt : 
  densityParameter G = 4 * m^2 / n^3
```

**Proof Status**: ✅ Definition verified  
**Note**: Parameter definition is pure mathematics, the critical value is empirical.

---

**Paper Text**:
> "Universal phase transition at ⟨k⟩²/N ≈ 2.5"

**Lean Formalization**:
```lean
-- src/PhaseTransition.lean:85
structure PhaseTransitionConjecture where
  criticalValue : ℝ  -- Empirically ≈ 2.5
  hyperbolicRegime : ∀ ε > 0, ∀ G, 
    densityParameter G < criticalValue - ε → isHyperbolic G
  sphericalRegime : ∀ ε > 0, ∀ G,
    densityParameter G > criticalValue + ε → isSpherical G
```

**Proof Status**: ⚠️ Conjecture  
**Research Needed**: 
- Random graph theory
- Concentration inequalities  
- Critical phenomena analysis

---

### Section 3.6: Resistance to Ricci Flow

**Paper Text**:
> "Semantic networks resisted: despite 79–86% reductions in C, trajectories stabilized above the Euclidean equilibrium"

**Lean Formalization**:
```lean
-- src/PhaseTransition.lean (planned)
theorem flowResistance 
    (G : WeightedGraph V)
    (h_real_network : isSemanticNetwork G) :
    ∀ n, curvature (flow^[n] G) > 0
```

**Proof Status**: ⚠️ Empirical observation  
**Note**: Requires formal definition of "semantic network" structure.

---

## Table 1: Network Statistics

| Paper Column | Lean Definition | Status |
|--------------|-----------------|--------|
| Nodes | `Fintype.card V` | ✅ |
| Edges | `G.graph.edgeFinset.card` | ✅ |
| Density | `2 * E / (N * (N-1))` | ✅ |
| C | `Clustering.averageClustering` | ✅ |
| σ_k | `degreeStd G` | ✅ |
| κ̄ | `Curvature.meanCurvature` | ✅ |

---

## Table 2: Null-Model Comparisons

| Paper Column | Lean Concept | Status |
|--------------|--------------|--------|
| Δκ | `meanCurvature G - meanCurvature G_null` | ✅ |
| p_MC | Monte Carlo p-value | ⚠️ Statistical |
| Cliff's δ | Effect size | ⚠️ Statistical |

---

## Implementation Verification

| Implementation | Formal Contract | Test Coverage |
|----------------|-----------------|---------------|
| Julia | `Consistency.Julia.CurvatureSpec` | Unit tests |
| Rust | `Consistency.Rust.WassersteinFFISpec` | FFI tests |
| Sounio | `Consistency.Sounio.CurvatureEffectSig` | Effect tracking |

---

## Confidence Levels

### Absolute Confidence (Machine-Checked)

- ✅ Curvature bounds: κ ∈ [-1, 1]
- ✅ Clustering bounds: C ∈ [0, 1]
- ✅ Probability normalization: Σμ = 1
- ✅ Idleness bounds: α ∈ [0, 1]
- ✅ Distance properties: d ≥ 0, symmetry

### High Confidence (Empirical + Theory)

- ⚠️ Phase transition exists: Strong empirical evidence
- ⚠️ Critical value ≈ 2.5: Empirical estimate
- ⚠️ Hyperbolic sweet spot: Empirical observation

### Medium Confidence (Partial Formalization)

- ⚠️ Null model shift: Empirically validated, not proven
- ⚠️ Flow resistance: Empirically observed
- ⚠️ Cross-linguistic consistency: Statistical

### Standard Confidence (Statistical/Empirical)

- ❌ SWOW specific values (Table 1)
- ❌ Monte Carlo p-values
- ❌ Effect sizes

---

## Recommendations for Paper

### What to Cite

**In Methods Section**:
> "The Ollivier-Ricci curvature computation has been formally verified to satisfy κ ∈ [-1, 1] for all valid inputs (see Lean 4 formalization in repository)."

**In Results Section**:
> "The phase transition at ⟨k⟩²/N ≈ 2.5 is an empirical discovery. We have formalized the parameter definition and conjecture structure in Lean 4, leaving the proof of universality to future work."

### Appendix Material

Include in supplementary materials:
1. Link to Lean repository
2. Summary of formalized theorems
3. Test vectors for reproduction

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2025-02-22 | Initial formalization |
| 2.0.1 | (planned) | Complete Wasserstein proofs |
| 2.1.0 | (planned) | Random graph models |

---

*For questions about the formalization, contact: demetrios@agourakis.med.br*