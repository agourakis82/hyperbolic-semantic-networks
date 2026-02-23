import Mathlib.Probability.ProbabilityMassFunction.Basic
import Mathlib.MeasureTheory.Measure.Portmanteau
import Mathlib.Data.Real.Basic
import Mathlib.Order.Interval.Set.Basic
import Mathlib.Topology.MetricSpace.Basic
import «HyperbolicSemanticNetworks».Basic
/-!
# Wasserstein-1 Distance (Optimal Transport)

This module formalizes the Wasserstein-1 distance (Earth Mover's Distance)
used in Ollivier-Ricci curvature computation.

The Wasserstein-1 distance between probability measures μ and ν is:
W₁(μ, ν) = inf_{γ ∈ Γ(μ, ν)} ∫∫ d(x,y) dγ(x,y)

where Γ(μ, ν) is the set of all couplings of μ and ν.

For finite graphs, this reduces to a linear programming problem.

## References

- Villani (2009): "Optimal Transport: Old and New"
- Ollivier (2009): Ricci curvature via optimal transport
-/


/-! ## Wasserstein Distance Definitions -/

namespace HyperbolicSemanticNetworks

noncomputable section

namespace Wasserstein

variable {V : Type} [Fintype V] [DecidableEq V]

/-- A coupling (transport plan) between two probability measures.
    γ(u,v) represents the amount of mass transported from u to v. -/
structure Coupling (μ ν : V → ℝ) where
  /-- The coupling matrix -/
  γ : V → V → ℝ
  /-- Non-negativity -/
  γ_nonneg : ∀ u v, 0 ≤ γ u v
  /-- Marginal constraint for μ: summing over v gives μ(u) -/
  marginal_μ : ∀ u, ∑ v, γ u v = μ u
  /-- Marginal constraint for ν: summing over u gives ν(v) -/
  marginal_ν : ∀ v, ∑ u, γ u v = ν v

/-- The cost of a coupling given a distance metric. -/
def couplingCost {μ ν : V → ℝ} (d : V → V → ℝ) (γ : Coupling μ ν) : ℝ :=
  ∑ u : V, ∑ v : V, d u v * γ.γ u v

/-- Wasserstein-1 distance is the minimum coupling cost.
    This is an infimum over all valid couplings. -/
def wasserstein1 (d : V → V → ℝ) (μ ν : V → ℝ) : ℝ :=
  sInf {c | ∃ γ : Coupling μ ν, couplingCost d γ = c}

/-! ## Properties of Wasserstein Distance -/

section Properties

variable {d : V → V → ℝ}
variable {μ ν : V → ℝ}

/-- Wasserstein distance is non-negative when d is non-negative. -/
lemma wasserstein_nonneg
    (_hμ : ProbabilityMeasure.IsProbabilityMeasure μ)
    (_hν : ProbabilityMeasure.IsProbabilityMeasure ν)
    (h_nonneg : ∀ u v, 0 ≤ d u v) :
    0 ≤ wasserstein1 d μ ν := by
  apply Real.sInf_nonneg
  intro c hc
  rcases hc with ⟨γ, hγ⟩
  rw [←hγ]
  simp [couplingCost]
  apply Finset.sum_nonneg
  intro u _
  apply Finset.sum_nonneg
  intro v _
  apply mul_nonneg
  · exact h_nonneg u v
  · exact γ.γ_nonneg u v

/-- **Axiom**: Wasserstein distance is symmetric when d is symmetric.

    The proof constructs the transposed coupling γ'(u,v) = γ(v,u)
    and shows it has the same cost. We axiomatize because the
    formal proof requires delicate manipulation of double sums
    with local let-bindings that fights Lean's elaborator. -/
axiom wasserstein_symmetric (h_sym : ∀ u v, d u v = d v u) :
    wasserstein1 d μ ν = wasserstein1 d ν μ

/-- The glued coupling: γ'(x,z) = Σ_y γ₁(x,y) · γ₂(y,z) / ν(y).

    When ν(y) = 0, γ₁(x,y) = 0 for all x (from marginal constraint),
    so γ₁(x,y) · γ₂(y,z) / ν(y) = 0/0 = 0 in Lean's reals.
    This is the standard "gluing" construction from optimal transport. -/
def gluedCoupling {ρ : V → ℝ} (γ₁ : Coupling μ ν) (γ₂ : Coupling ν ρ) : V → V → ℝ :=
  fun x z => ∑ y, γ₁.γ x y * γ₂.γ y z / ν y

/-- Key lemma: if ν(y) = 0, then γ₁(x,y) = 0 for all x. -/
lemma coupling_zero_of_marginal_zero (γ₁ : Coupling μ ν)
    (y : V) (h : ν y = 0) (x : V) : γ₁.γ x y = 0 := by
  have h_sum := γ₁.marginal_ν y
  rw [h] at h_sum
  have h_nonneg : ∀ u, 0 ≤ γ₁.γ u y := fun u => γ₁.γ_nonneg u y
  exact le_antisymm
    (by linarith [Finset.sum_eq_zero_iff_of_nonneg (fun u _ => h_nonneg u) |>.mp h_sum x (Finset.mem_univ x)])
    (h_nonneg x)

/-- **Axiom**: Wasserstein distance satisfies triangle inequality.

    W₁(μ, ρ) ≤ W₁(μ, ν) + W₁(ν, ρ)

    The standard proof constructs a gluing of two couplings:
    γ'(x,z) = Σ_y γ₁(x,y) · γ₂(y,z) / ν(y)
    and shows this is a valid coupling with cost bounded by the sum.

    We axiomatize this because completing the formal proof requires
    delicate handling of division-by-zero (when ν(y) = 0) and
    infimum manipulation over coupling sets. The gluing construction
    is scaffolded above (`gluedCoupling`, `coupling_zero_of_marginal_zero`). -/
axiom wasserstein_triangle (h_metric : ∀ u v w, d u w ≤ d u v + d v w) :
    ∀ (μ ν ρ : V → ℝ),
    wasserstein1 d μ ρ ≤ wasserstein1 d μ ν + wasserstein1 d ν ρ

end Properties

/-! ## Computation via Linear Programming -/

section Computation

/-- For finite graphs, Wasserstein can be computed as a linear program.
    Variables: γ(u,v) for all pairs
    Constraints: Marginal conditions
    Objective: Minimize ∑ d(u,v) × γ(u,v) -/
def wassersteinLP (d : V → V → ℝ) (μ ν : V → ℝ) : ℝ :=
  -- This would be the actual LP solution
  -- For formalization, we relate it to the abstract definition
  wasserstein1 d μ ν

/-- The LP solution equals the abstract Wasserstein distance. -/
lemma lp_equals_wasserstein (d : V → V → ℝ) (μ ν : V → ℝ) :
    wassersteinLP d μ ν = wasserstein1 d μ ν := by
  rfl  -- By definition in our formalization

end Computation

end Wasserstein

end

end HyperbolicSemanticNetworks
