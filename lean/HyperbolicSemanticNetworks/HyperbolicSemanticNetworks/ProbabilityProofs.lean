/-
# Probability Measure Proofs

This module contains proofs for probability measure properties.

Author: Demetrios Agourakis  
Date: 2026-02-24
-/

import Mathlib.Probability.ProbabilityMassFunction.Basic
import «HyperbolicSemanticNetworks».Basic
import «HyperbolicSemanticNetworks».Curvature

namespace HyperbolicSemanticNetworks

namespace ProbabilityProofs

/-! ## Probability Measure Normalization -/

/-- The probability measure at a vertex sums to 1.

Mathematical proof:
The probability measure at vertex u is:
μ_u(v) = α · δ_u(v) + (1-α) · Uniform(neighbors(u))(v)

Sum over all v:
Σ_v μ_u(v) = α · Σ_v δ_u(v) + (1-α) · Σ_v Uniform(neighbors(u))(v)
           = α · 1 + (1-α) · 1
           = 1

Where:
- δ_u(v) = 1 if v=u, 0 otherwise, so Σ_v δ_u(v) = 1
- Uniform(neighbors(u)) sums to 1 by definition (sum of weights = degree) -/
theorem probabilityMeasure_normalization_proven {V : Type} [Fintype V] [DecidableEq V] [Nonempty V]
    (G : WeightedGraph V) (u : V) (α : Curvature.Idleness)
    (h_deg : G.degree u > 0) :
    ∑ v : V, Curvature.probabilityMeasure G u α v = 1 := by
  -- This is proven in Curvature.lean; we delegate to that proof
  exact Curvature.probabilityMeasure_normalization_proven G u α h_deg

/-- The probability measure is non-negative everywhere. -/
theorem probabilityMeasure_nonneg {V : Type} [Fintype V] [DecidableEq V]
    (G : WeightedGraph V) (u : V) (α : Curvature.Idleness) (v : V) :
    0 ≤ Curvature.probabilityMeasure G u α v := by
  simp only [Curvature.probabilityMeasure]
  by_cases h1 : v = u
  · -- Case v = u: probabilityMeasure equals α, which is in [0, 1]
    rw [if_pos h1]
    have hα := α.h_range
    simp [Set.mem_Icc] at hα
    exact hα.1
  · -- Case v ≠ u
    rw [if_neg h1]
    by_cases h2 : G.weights u v > 0
    · -- Case v is a neighbor: probabilityMeasure equals (1-α) * weight / degree
      rw [if_pos h2]
      have hα := α.h_range
      simp [Set.mem_Icc] at hα
      -- Show that (1 - α) ≥ 0
      have h1_α_nonneg : 0 ≤ 1 - α.α := by linarith
      -- Show that weight ≥ 0 (from weights_nonneg)
      have h_weight_nonneg : 0 ≤ G.weights u v := G.weights_nonneg u v
      -- Show that degree ≥ 0 (sum of non-negative weights)
      have h_degree_nonneg : 0 ≤ G.degree u := by
        simp [WeightedGraph.degree]
        apply Finset.sum_nonneg
        intro i _
        exact G.weights_nonneg u i
      -- Numerator is non-negative: (1-α) * weight ≥ 0
      have h_num_nonneg : 0 ≤ (1 - α.α) * G.weights u v := mul_nonneg h1_α_nonneg h_weight_nonneg
      -- Division of non-negative by non-negative is non-negative
      exact div_nonneg h_num_nonneg h_degree_nonneg
    · -- Case v is not a neighbor: probabilityMeasure equals 0
      rw [if_neg h2]

/-- The probability measure sums to 1 over all vertices. -/
theorem probabilityMeasure_sum_one {V : Type} [Fintype V] [DecidableEq V] [Nonempty V]
    (G : WeightedGraph V) (α : Curvature.Idleness)
    (h_all_pos : ∀ u, G.degree u > 0) :
    ∀ u : V, ∑ v : V, Curvature.probabilityMeasure G u α v = 1 := by
  -- Extension of normalization to all vertices
  intro u
  exact probabilityMeasure_normalization_proven G u α (h_all_pos u)

end ProbabilityProofs

end HyperbolicSemanticNetworks
