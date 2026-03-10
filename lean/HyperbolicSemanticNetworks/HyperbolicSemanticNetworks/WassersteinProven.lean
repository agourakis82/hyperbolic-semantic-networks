/-
# Wasserstein-1 Distance: Proven Theorems

This module contains PROOFS (not axioms) for key Wasserstein properties.

## Status

| Property | Wasserstein.lean | This Module |
|----------|-----------------|-------------|
| Non-negativity | ✅ proven | ✅ proven |
| Symmetry | ⚠️ axiom | ✅ proven |
| Triangle inequality | ⚠️ axiom | ✅ proven |

All key Wasserstein properties are now fully proven. The triangle inequality proof uses:
- `gluedCoupling'` definition with verified marginals ✅
- Cost bound lemma `glued_coupling_cost_bound` ✅
- Main theorem `wasserstein_triangle_proven` ✅

The cost bound follows the standard optimal transport proof strategy but
requires complex sum manipulations with if-then-else conditions for the
ν(v) = 0 case. The algebraic structure of the proof is documented.

Author: Demetrios Agourakis
Date: 2026-02-24
Version: 2.2.0
-/

import Mathlib.Probability.ProbabilityMassFunction.Basic
import Mathlib.Data.Real.Basic
import Mathlib.Order.Interval.Set.Basic
import Mathlib.Topology.MetricSpace.Basic
import Mathlib.Algebra.BigOperators.Ring.Finset
import «HyperbolicSemanticNetworks».Basic
import «HyperbolicSemanticNetworks».Wasserstein

namespace HyperbolicSemanticNetworks

noncomputable section

namespace Wasserstein

variable {V : Type} [Fintype V] [DecidableEq V]

/-! ## Proven Symmetry Theorem

The proof constructs the transposed coupling and shows it has the same cost. -/

/-- The transposed coupling: γ^T(u,v) = γ(v,u). -/
def transposeCoupling {μ ν : V → ℝ} (γ : Coupling μ ν) : Coupling ν μ where
  γ u v := γ.γ v u
  γ_nonneg u v := γ.γ_nonneg v u
  marginal_μ u := by
    simpa using γ.marginal_ν u
  marginal_ν v := by
    simpa using γ.marginal_μ v

/-- Cost of transposed coupling equals cost of original when distance is symmetric. -/
lemma transpose_coupling_cost {μ ν : V → ℝ} (γ : Coupling μ ν)
    (d : V → V → ℝ) (h_sym : ∀ u v, d u v = d v u) :
    couplingCost d (transposeCoupling γ) = couplingCost d γ := by
  simp [couplingCost, transposeCoupling]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro v _
  apply Finset.sum_congr rfl
  intro u _
  rw [h_sym v u]

/-- Wasserstein distance is symmetric when the metric is symmetric.

This REPLACES the axiom `wasserstein_symmetric` in Wasserstein.lean. -/
theorem wasserstein_symmetric_proven {μ ν : V → ℝ}
    (d : V → V → ℝ) (h_sym : ∀ u v, d u v = d v u) :
    wasserstein1 d μ ν = wasserstein1 d ν μ := by
  unfold wasserstein1
  have h_set_eq : {c | ∃ γ : Coupling μ ν, couplingCost d γ = c} =
                  {c | ∃ γ : Coupling ν μ, couplingCost d γ = c} := by
    ext c
    constructor
    · rintro ⟨γ, hγ_cost⟩
      use transposeCoupling γ
      rw [←hγ_cost]
      exact transpose_coupling_cost γ d h_sym
    · rintro ⟨γ, hγ_cost⟩
      use transposeCoupling γ
      rw [←hγ_cost]
      exact transpose_coupling_cost γ d h_sym
  rw [h_set_eq]

/-! ## Triangle Inequality Proof -/

/-- Key lemma: when ν(y) = 0, γ₁(x,y) = 0 for all x. -/
lemma coupling_zero_of_marginal_zero_proven {μ ν : V → ℝ}
    (γ : Coupling μ ν) (y : V) (h : ν y = 0) (x : V) :
    γ.γ x y = 0 := by
  have h_sum := γ.marginal_ν y
  rw [h] at h_sum
  have h_nonneg : ∀ u, 0 ≤ γ.γ u y := fun u => γ.γ_nonneg u y
  have h_x_le : γ.γ x y ≤ 0 := by
    have h_sum_eq : ∑ u : V, γ.γ u y = 0 := h_sum
    have h_x_le_sum : γ.γ x y ≤ ∑ u : V, γ.γ u y := by
      apply Finset.single_le_sum (fun i _ => h_nonneg i)
      simp
    linarith
  linarith [h_nonneg x, h_x_le]

/-- ν is non-negative at all points (derived from coupling marginal). -/
lemma nu_nonneg_from_coupling {μ ν : V → ℝ} (γ : Coupling μ ν) (v : V) : 0 ≤ ν v := by
  have h_sum := γ.marginal_ν v
  have h_nonneg : ∀ u, 0 ≤ γ.γ u v := fun u => γ.γ_nonneg u v
  have h_ν_nonneg : 0 ≤ ∑ u, γ.γ u v := by
    apply Finset.sum_nonneg
    intro i _
    exact h_nonneg i
  linarith [h_sum, h_ν_nonneg]

/-- Helper: Define the glued coupling value with safe division. -/
def gluedCouplingVal {μ ν ρ : V → ℝ} (γ₁ : Coupling μ ν) (γ₂ : Coupling ν ρ) (u w : V) : ℝ :=
  ∑ v : V, if ν v = 0 then 0 else γ₁.γ u v * γ₂.γ v w / ν v

/-- The glued coupling: γ'(u,w) = Σ_v [γ₁(u,v) · γ₂(v,w) / ν(v)] when ν(v) ≠ 0.

This is the standard gluing construction from optimal transport theory.
When ν(v) = 0, the term contributes 0 (since γ₁(u,v) = 0 from marginal constraint). -/
def gluedCoupling' {μ ν ρ : V → ℝ} (γ₁ : Coupling μ ν) (γ₂ : Coupling ν ρ) :
    Coupling μ ρ where
  γ u w := gluedCouplingVal γ₁ γ₂ u w
  γ_nonneg u w := by
    simp [gluedCouplingVal]
    apply Finset.sum_nonneg
    intro v _
    split_ifs with h
    · rfl
    · apply div_nonneg
      · apply mul_nonneg
        · exact γ₁.γ_nonneg u v
        · exact γ₂.γ_nonneg v w
      · have h_ν_nonneg : 0 ≤ ν v := nu_nonneg_from_coupling γ₁ v
        linarith
  marginal_μ u := by
    simp [gluedCouplingVal]
    rw [Finset.sum_comm]
    have h_sum : ∀ v : V, ∑ w : V, (if ν v = 0 then 0 else γ₁.γ u v * γ₂.γ v w / ν v)
        = γ₁.γ u v := by
      intro v
      split_ifs with h
      · have h_zero : γ₁.γ u v = 0 := coupling_zero_of_marginal_zero_proven γ₁ v h u
        simp [h_zero]
      · have h₂ : ∑ w : V, γ₂.γ v w = ν v := γ₂.marginal_μ v
        calc
          ∑ w : V, γ₁.γ u v * γ₂.γ v w / ν v
            = γ₁.γ u v * (∑ w : V, γ₂.γ v w) / ν v := by
              rw [Finset.mul_sum]
              simp [Finset.sum_div]
          _ = γ₁.γ u v * ν v / ν v := by rw [h₂]
          _ = γ₁.γ u v := by field_simp [h]
    simp_rw [h_sum]
    exact γ₁.marginal_μ u
  marginal_ν w := by
    simp [gluedCouplingVal]
    rw [Finset.sum_comm]
    have h_sum : ∀ v : V, ∑ u : V, (if ν v = 0 then 0 else γ₁.γ u v * γ₂.γ v w / ν v)
        = γ₂.γ v w := by
      intro v
      split_ifs with h
      · have h_zero : γ₂.γ v w = 0 := by
          have h_sum := γ₂.marginal_μ v
          rw [h] at h_sum
          have h_nonneg : ∀ w, 0 ≤ γ₂.γ v w := fun w => γ₂.γ_nonneg v w
          have h_le : γ₂.γ v w ≤ ∑ w' : V, γ₂.γ v w' := by
            apply Finset.single_le_sum (fun i _ => h_nonneg i)
            simp
          linarith [h_nonneg w, h_le]
        simp [h_zero]
      · have h₁ : ∑ u : V, γ₁.γ u v = ν v := γ₁.marginal_ν v
        have h₃ : ∑ u : V, γ₁.γ u v * γ₂.γ v w / ν v = γ₂.γ v w := by
          have h₄ : ∀ u : V, γ₁.γ u v * γ₂.γ v w / ν v = γ₁.γ u v * (γ₂.γ v w / ν v) := by
            intro u
            ring_nf
          simp_rw [h₄]
          rw [←Finset.sum_mul]
          rw [h₁]
          field_simp [h]
        simpa using h₃
    simp_rw [h_sum]
    exact γ₂.marginal_ν w

/-- Helper lemmas for sum index ordering. -/
lemma couplingCost_γ1_eq {μ ν : V → ℝ} (d : V → V → ℝ)
    (γ₁ : Coupling μ ν) :
    ∑ v : V, ∑ u : V, d u v * γ₁.γ u v = couplingCost d γ₁ := by
  simp [couplingCost]
  rw [Finset.sum_comm]

lemma couplingCost_γ2_eq {ν ρ : V → ℝ} (d : V → V → ℝ)
    (γ₂ : Coupling ν ρ) :
    ∑ v : V, ∑ w : V, d v w * γ₂.γ v w = couplingCost d γ₂ := by
  simp [couplingCost]

-- The triangle inequality proof is decomposed into three sub-lemmas
-- to avoid kernel timeout on the monolithic proof.

/-- Step 1: Expand couplingCost of the glued coupling into a triple sum. -/
lemma glued_coupling_cost_expand {μ ν ρ : V → ℝ} (d : V → V → ℝ)
    (γ₁ : Coupling μ ν) (γ₂ : Coupling ν ρ) :
    couplingCost d (gluedCoupling' γ₁ γ₂) =
    ∑ u : V, ∑ w : V, ∑ v : V,
      (if ν v = 0 then 0 else γ₁.γ u v * γ₂.γ v w / ν v) * d u w := by
  simp [couplingCost, gluedCoupling', gluedCouplingVal]
  congr 1; ext u; congr 1; ext w
  rw [Finset.mul_sum]; congr 1; ext v; split_ifs <;> ring

/-- Step 2: Apply pointwise triangle inequality d(u,w) ≤ d(u,v) + d(v,w) under the sum. -/
lemma glued_cost_triangle_pointwise {μ ν ρ : V → ℝ} (d : V → V → ℝ)
    (γ₁ : Coupling μ ν) (γ₂ : Coupling ν ρ)
    (h_tri : ∀ u v w, d u w ≤ d u v + d v w)
    (h_nn : ∀ u v w, 0 ≤ (if ν v = 0 then 0 else γ₁.γ u v * γ₂.γ v w / ν v)) :
    ∑ u : V, ∑ w : V, ∑ v : V,
      (if ν v = 0 then 0 else γ₁.γ u v * γ₂.γ v w / ν v) * d u w ≤
    ∑ u : V, ∑ w : V, ∑ v : V,
      (if ν v = 0 then 0 else γ₁.γ u v * γ₂.γ v w / ν v) * (d u v + d v w) := by
  apply Finset.sum_le_sum; intro u _
  apply Finset.sum_le_sum; intro w _
  apply Finset.sum_le_sum; intro v _
  apply mul_le_mul_of_nonneg_left (h_tri u v w) (h_nn u v w)

/-- Step 3: Factor the expanded sum into couplingCost d γ₁ + couplingCost d γ₂. -/
lemma split_glued_cost {μ ν ρ : V → ℝ} (d : V → V → ℝ)
    (γ₁ : Coupling μ ν) (γ₂ : Coupling ν ρ) :
    ∑ u : V, ∑ w : V, ∑ v : V,
      (if ν v = 0 then 0 else γ₁.γ u v * γ₂.γ v w / ν v) * (d u v + d v w) ≤
    couplingCost d γ₁ + couplingCost d γ₂ := by
  simp_rw [mul_add, Finset.sum_add_distrib]
  apply add_le_add
  · -- Part 1: ∑ u w v, (if …) * d u v ≤ couplingCost d γ₁
    apply le_of_eq
    conv_lhs => arg 2; ext u; rw [Finset.sum_comm]
    unfold couplingCost
    congr 1; ext u; congr 1; ext v
    split_ifs with h
    · simp [coupling_zero_of_marginal_zero_proven γ₁ v h u]
    · have h₂ : ∑ w : V, γ₂.γ v w = ν v := γ₂.marginal_μ v
      have hν_ne : ν v ≠ 0 := ne_of_gt (lt_of_le_of_ne (nu_nonneg_from_coupling γ₁ v) (Ne.symm h))
      conv_lhs => arg 2; ext i; rw [show γ₁.γ u v * γ₂.γ v i / ν v * d u v = d u v * γ₁.γ u v / ν v * γ₂.γ v i from by ring]
      rw [← Finset.mul_sum, h₂, div_mul_cancel₀ _ hν_ne]
  · -- Part 2: ∑ u w v, (if …) * d v w ≤ couplingCost d γ₂
    apply le_of_eq
    unfold couplingCost
    -- LHS: ∑ u, ∑ w, ∑ v, (if ν v = 0 then 0 else γ₁.γ u v * γ₂.γ v w / ν v) * d v w
    -- RHS: ∑ v, ∑ w, d v w * γ₂.γ v w
    -- Step 1: swap innermost two sums in LHS:  ∑ u, ∑ w, ∑ v → ∑ u, ∑ v, ∑ w
    conv_lhs => arg 2; ext u; rw [Finset.sum_comm]
    -- Step 2: swap outermost: ∑ u, ∑ v → ∑ v, ∑ u
    rw [Finset.sum_comm]
    -- Now LHS: ∑ v, ∑ u, ∑ w, (if ν v = 0 then ...) * d v w
    -- Step 3: swap middle sums: ∑ u, ∑ w → ∑ w, ∑ u
    congr 1; ext v
    rw [Finset.sum_comm]
    -- Now: ∑ w, ∑ u, (if ν v = 0 then ...) * d v w
    congr 1; ext w
    -- Goal: ∑ u, (if ν v = 0 then 0 else γ₁.γ u v * γ₂.γ v w / ν v) * d v w = d v w * γ₂.γ v w
    split_ifs with h
    · -- ν v = 0 case: everything is 0
      simp
      have h_zero : γ₂.γ v w = 0 := by
        have hmarg := γ₂.marginal_μ v
        rw [h] at hmarg
        have := Finset.sum_eq_zero_iff_of_nonneg (fun i _ => γ₂.γ_nonneg v i) |>.mp hmarg w (Finset.mem_univ w)
        linarith [γ₂.γ_nonneg v w]
      simp [h_zero]
    · -- ν v ≠ 0: collapse ∑ u γ₁(u,v) = ν v, then cancel
      have h₁ : ∑ u : V, γ₁.γ u v = ν v := γ₁.marginal_ν v
      have hν_ne : ν v ≠ 0 := ne_of_gt (lt_of_le_of_ne (nu_nonneg_from_coupling γ₁ v) (Ne.symm h))
      conv_lhs => arg 2; ext u; rw [show γ₁.γ u v * γ₂.γ v w / ν v * d v w = d v w * γ₂.γ v w / ν v * γ₁.γ u v from by ring]
      rw [← Finset.mul_sum, h₁, div_mul_cancel₀ _ hν_ne]

/-- Key lemma: The cost of the glued coupling is bounded by the sum of costs.
    Composed from three sub-lemmas to avoid kernel timeout. -/
lemma glued_coupling_cost_bound {μ ν ρ : V → ℝ} (d : V → V → ℝ)
    (γ₁ : Coupling μ ν) (γ₂ : Coupling ν ρ)
    (h_tri : ∀ u v w, d u w ≤ d u v + d v w) :
    couplingCost d (gluedCoupling' γ₁ γ₂) ≤ couplingCost d γ₁ + couplingCost d γ₂ := by
  have h_nn : ∀ u v w, 0 ≤ (if ν v = 0 then 0 else γ₁.γ u v * γ₂.γ v w / ν v) := by
    intro u v w
    split_ifs with h
    · rfl
    · apply div_nonneg
      · exact mul_nonneg (γ₁.γ_nonneg u v) (γ₂.γ_nonneg v w)
      · exact le_of_lt (lt_of_le_of_ne (nu_nonneg_from_coupling γ₁ v) (Ne.symm h))
  calc couplingCost d (gluedCoupling' γ₁ γ₂)
      = ∑ u, ∑ w, ∑ v, (if ν v = 0 then 0 else γ₁.γ u v * γ₂.γ v w / ν v) * d u w :=
          glued_coupling_cost_expand d γ₁ γ₂
    _ ≤ ∑ u, ∑ w, ∑ v, (if ν v = 0 then 0 else γ₁.γ u v * γ₂.γ v w / ν v) * (d u v + d v w) :=
          glued_cost_triangle_pointwise d γ₁ γ₂ h_tri h_nn
    _ ≤ couplingCost d γ₁ + couplingCost d γ₂ :=
          split_glued_cost d γ₁ γ₂

/-- **Theorem**: Triangle inequality for Wasserstein distance.

W₁(μ, ρ) ≤ W₁(μ, ν) + W₁(ν, ρ)

The proof uses the gluing construction and shows that for any couplings
γ₁ ∈ Γ(μ,ν) and γ₂ ∈ Γ(ν,ρ), the glued coupling γ' ∈ Γ(μ,ρ) satisfies:
cost(γ') ≤ cost(γ₁) + cost(γ₂)

Taking infimum over optimal couplings gives the result.

This REPLACES the axiom `wasserstein_triangle` in Wasserstein.lean. -/
theorem wasserstein_triangle_proven {μ ν ρ : V → ℝ} (d : V → V → ℝ)
    (hμ : ProbabilityMeasure.IsProbabilityMeasure μ)
    (hν : ProbabilityMeasure.IsProbabilityMeasure ν)
    (hρ : ProbabilityMeasure.IsProbabilityMeasure ρ)
    (h_metric : ∀ u v, d u v ≥ 0) (_h_sym : ∀ u v, d u v = d v u)
    (h_tri : ∀ u v w, d u w ≤ d u v + d v w) :
    wasserstein1 d μ ρ ≤ wasserstein1 d μ ν + wasserstein1 d ν ρ := by
  -- Strategy: Show that the infimum over couplings of (μ,ρ) is at most
  -- the sum of infima over couplings of (μ,ν) and (ν,ρ).
  -- This follows from the gluing construction and the cost bound.

  apply le_of_forall_pos_le_add
  intro ε hε

  unfold wasserstein1

  -- The sets of achievable costs
  let S₁ := {c | ∃ γ : Coupling μ ν, couplingCost d γ = c}
  let S₂ := {c | ∃ γ : Coupling ν ρ, couplingCost d γ = c}
  let S₃ := {c | ∃ γ : Coupling μ ρ, couplingCost d γ = c}

  -- Show S₁ and S₂ are nonempty by constructing product couplings
  have h_S₁_nonempty : S₁.Nonempty := by
    let γ_prod : Coupling μ ν := {
      γ := fun u v => μ u * ν v,
      γ_nonneg := by
        intro u v
        apply mul_nonneg
        · exact hμ.1 u
        · exact hν.1 v,
      marginal_μ := by
        intro u
        calc
          ∑ v : V, μ u * ν v = μ u * ∑ v : V, ν v := by rw [Finset.mul_sum]
          _ = μ u * 1 := by rw [hν.2]
          _ = μ u := by ring,
      marginal_ν := by
        intro v
        calc
          ∑ u : V, μ u * ν v = (∑ u : V, μ u) * ν v := by rw [Finset.sum_mul]
          _ = 1 * ν v := by rw [hμ.2]
          _ = ν v := by ring
    }
    use couplingCost d γ_prod
    use γ_prod

  have h_S₂_nonempty : S₂.Nonempty := by
    let γ_prod : Coupling ν ρ := {
      γ := fun u v => ν u * ρ v,
      γ_nonneg := by
        intro u v
        apply mul_nonneg
        · exact hν.1 u
        · exact hρ.1 v,
      marginal_μ := by
        intro u
        calc
          ∑ v : V, ν u * ρ v = ν u * ∑ v : V, ρ v := by rw [Finset.mul_sum]
          _ = ν u * 1 := by rw [hρ.2]
          _ = ν u := by ring,
      marginal_ν := by
        intro v
        calc
          ∑ u : V, ν u * ρ v = (∑ u : V, ν u) * ρ v := by rw [Finset.sum_mul]
          _ = 1 * ρ v := by rw [hν.2]
          _ = ρ v := by ring
    }
    use couplingCost d γ_prod
    use γ_prod

  have h_S₁_bdd_below : BddBelow S₁ := ⟨0, by
    intro x hx
    rcases hx with ⟨γ, hγ⟩
    rw [←hγ]
    simp [couplingCost]
    apply Finset.sum_nonneg
    intro u _
    apply Finset.sum_nonneg
    intro v _
    apply mul_nonneg
    · exact h_metric u v
    · exact γ.γ_nonneg u v⟩

  have h_S₂_bdd_below : BddBelow S₂ := ⟨0, by
    intro x hx
    rcases hx with ⟨γ, hγ⟩
    rw [←hγ]
    simp [couplingCost]
    apply Finset.sum_nonneg
    intro u _
    apply Finset.sum_nonneg
    intro v _
    apply mul_nonneg
    · exact h_metric u v
    · exact γ.γ_nonneg u v⟩

  have h_S₃_bdd_below : BddBelow S₃ := ⟨0, by
    intro x hx
    rcases hx with ⟨γ, hγ⟩
    rw [←hγ]
    simp [couplingCost]
    apply Finset.sum_nonneg
    intro u _
    apply Finset.sum_nonneg
    intro v _
    apply mul_nonneg
    · exact h_metric u v
    · exact γ.γ_nonneg u v⟩

  -- Get c₁ close to sInf S₁
  have h_c₁ : ∃ c₁ ∈ S₁, c₁ < sInf S₁ + ε / 2 := by
    apply exists_lt_of_csInf_lt h_S₁_nonempty
    linarith

  -- Get c₂ close to sInf S₂
  have h_c₂ : ∃ c₂ ∈ S₂, c₂ < sInf S₂ + ε / 2 := by
    apply exists_lt_of_csInf_lt h_S₂_nonempty
    linarith

  rcases h_c₁ with ⟨c₁, hc₁, h_c₁_lt⟩
  rcases h_c₂ with ⟨c₂, hc₂, h_c₂_lt⟩

  rcases hc₁ with ⟨γ₁, hγ₁⟩
  rcases hc₂ with ⟨γ₂, hγ₂⟩

  -- Construct the glued coupling and its cost
  let γ' := gluedCoupling' γ₁ γ₂
  let c₃ := couplingCost d γ'

  have hc₃ : c₃ ∈ S₃ := by use γ'

  have h_cost_bound : c₃ ≤ c₁ + c₂ := by
    rw [←hγ₁, ←hγ₂]
    exact glued_coupling_cost_bound d γ₁ γ₂ h_tri

  have h_sInf_S₃_le_c₃ : sInf S₃ ≤ c₃ := csInf_le h_S₃_bdd_below hc₃

  -- Combine all the inequalities
  have h_sInf_S₃_le : sInf S₃ ≤ sInf S₁ + sInf S₂ + ε := by
    linarith

  exact h_sInf_S₃_le

end Wasserstein

end

end HyperbolicSemanticNetworks
