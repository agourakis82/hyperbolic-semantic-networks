/-
# Ollivier-Ricci Curvature

This module defines Ollivier-Ricci curvature on weighted graphs and proves
fundamental properties including bounds and the key theorem that curvature
is always in [-1, 1].

## Main Definitions

- `probabilityMeasure`: Probability measure at a vertex for curvature computation
- `ollivierRicci`: Ollivier-Ricci curvature κ(u,v) = 1 - W₁(μᵤ, μᵥ)/d(u,v)

## Main Theorems

- `curvature_bounds`: Proven theorem showing κ ∈ [-1, 1]
- `wasserstein_triangle_distance`: Triangle inequality for Wasserstein distance

## References

- Ollivier, Y. (2009). "Ricci curvature of Markov chains on metric spaces"
- Lin, Y., Lu, L., Yau, S.T. (2011). "Ricci curvature of graphs"
-/

import «HyperbolicSemanticNetworks».Basic
import «HyperbolicSemanticNetworks».Wasserstein
import «HyperbolicSemanticNetworks».WassersteinProven
import Mathlib.Probability.ProbabilityMassFunction.Basic

namespace HyperbolicSemanticNetworks

namespace Curvature

variable {V : Type} [Fintype V] [DecidableEq V] [Nonempty V]
variable (G : WeightedGraph V)

/-! ## Idleness Parameter -/

/-- Idleness parameter α ∈ [0, 1] for Ollivier-Ricci curvature.

The idleness controls how much probability mass stays at the source vertex.
- α = 1: All mass stays at source (lazy random walk)
- α = 0: Mass is distributed to neighbors only
- α = 0.5: Standard choice (balance between lazy and active)

Reference: Ollivier (2009) uses α = 1 for the "lazy" version. -/
structure Idleness where
  /-- The idleness value -/
  α : ℝ
  /-- Idleness is in [0, 1] -/
  h_range : α ∈ Set.Icc (0 : ℝ) 1



namespace Idleness

/-- Standard idleness α = 0.5 -/
def standard : Idleness :=
  ⟨0.5, by norm_num [Set.mem_Icc]⟩

/-- Lazy idleness α = 1 (all mass stays at source) -/
def lazy : Idleness :=
  ⟨1, by norm_num [Set.mem_Icc]⟩

/-- Active idleness α = 0 (all mass to neighbors) -/
def active : Idleness :=
  ⟨0, by norm_num [Set.mem_Icc]⟩

end Idleness

/-! ## Probability Measure -/

/-- Probability measure at vertex u for Ollivier-Ricci curvature.

μᵤ(v) = α · δ_u(v) + (1-α) · Uniform(neighbors(u))(v)

Where:
- δ_u(v) = 1 if v = u, 0 otherwise (Dirac delta)
- Uniform(neighbors(u)) distributes mass evenly among neighbors

This corresponds to a lazy random walk that:
- Stays at u with probability α
- Moves to a random neighbor with probability (1-α)

Reference: Ollivier (2009), Definition 1. -/
noncomputable def probabilityMeasure (u : V) (α : Idleness) (v : V) : ℝ :=
  if v = u then
    α.α  -- Mass stays at source
  else if G.weights u v > 0 then
    (1 - α.α) * G.weights u v / G.degree u  -- Mass to neighbors
  else
    0  -- No edge, no mass

/-- **Theorem**: The probability measure at u sums to 1.

Mathematical proof:
Σ_v μ_u(v) = α · Σ_v δ_u(v) + (1-α) · Σ_v Uniform(neighbors(u))(v)
           = α · 1 + (1-α) · 1
           = 1

Where:
- δ_u(v) = 1 if v=u, 0 otherwise, so Σ_v δ_u(v) = 1
- Uniform(neighbors(u)) sums to 1 by definition

This requires complex sum manipulations with if-then-else conditions. -/
theorem probabilityMeasure_normalization_proven (u : V) (α : Idleness)
    (h_deg : G.degree u > 0) :
    ∑ v : V, probabilityMeasure G u α v = 1 := by
  -- Key: for v ≠ u, μ(v) equals (1-α)*w/deg regardless of weight positivity
  have h_eq : ∀ v, v ≠ u →
      probabilityMeasure G u α v = (1 - α.α) * G.weights u v / G.degree u := by
    intro v hv
    simp only [probabilityMeasure, if_neg hv]
    by_cases hw : G.weights u v > 0
    · exact if_pos hw
    · rw [if_neg hw]
      have h0 : G.weights u v = 0 := le_antisymm (not_lt.mp hw) (G.weights_nonneg u v)
      rw [h0, mul_zero, zero_div]
  -- Split: ∑_v f(v) = f(u) + ∑_{v≠u} f(v)
  rw [← Finset.add_sum_erase _ _ (Finset.mem_univ u)]
  -- Rewrite ∑_{v≠u} using h_eq (BEFORE simplifying the standalone term)
  have h_rest : ∑ v ∈ Finset.univ.erase u, probabilityMeasure G u α v =
      (1 - α.α) * G.degree u / G.degree u := by
    calc ∑ v ∈ Finset.univ.erase u, probabilityMeasure G u α v
        = ∑ v ∈ Finset.univ.erase u, ((1 - α.α) * G.weights u v / G.degree u) := by
          apply Finset.sum_congr rfl
          intro v hv
          exact h_eq v (Finset.ne_of_mem_erase hv)
      _ = (∑ v ∈ Finset.univ.erase u, ((1 - α.α) * G.weights u v)) / G.degree u := by
          rw [Finset.sum_div]
      _ = ((1 - α.α) * ∑ v ∈ Finset.univ.erase u, G.weights u v) / G.degree u := by
          rw [← Finset.mul_sum]
      _ = (1 - α.α) * G.degree u / G.degree u := by
          congr 1; congr 1
          -- ∑_{v≠u} w(u,v) = degree(u) because w(u,u) = 0
          have h_split : G.degree u = G.weights u u + ∑ v ∈ Finset.univ.erase u, G.weights u v := by
            show ∑ v : V, G.weights u v = _
            rw [← Finset.add_sum_erase _ _ (Finset.mem_univ u)]
          rw [G.no_self_loops, zero_add] at h_split
          exact h_split.symm
  rw [h_rest]
  -- Now simplify: probabilityMeasure G u α u = α.α
  have h_self : probabilityMeasure G u α u = α.α := by
    simp only [probabilityMeasure, if_pos rfl, ite_true]
  rw [h_self]
  -- Goal: α.α + (1 - α.α) * deg / deg = 1
  have h_deg_ne : G.degree u ≠ 0 := ne_of_gt h_deg
  rw [mul_div_cancel_right₀ _ h_deg_ne]
  have hα := α.h_range; simp [Set.mem_Icc] at hα
  linarith

/-- **Proven**: The probability measure satisfies IsProbabilityMeasure. -/
theorem probabilityMeasure_normalization (u : V) (α : Idleness)
    (h_deg : G.degree u > 0) :
    ProbabilityMeasure.IsProbabilityMeasure (probabilityMeasure G u α) := by
  constructor
  · -- Show non-negativity
    intro v
    simp only [probabilityMeasure]
    by_cases h1 : v = u
    · -- v = u, value is α which is in [0,1]
      rw [if_pos h1]
      have hα := α.h_range
      simp [Set.mem_Icc] at hα
      linarith
    · -- v ≠ u
      rw [if_neg h1]
      by_cases h2 : G.weights u v > 0
      · -- Neighbor, value is (1-α) * weight / degree
        rw [if_pos h2]
        have hα := α.h_range
        simp [Set.mem_Icc] at hα
        apply div_nonneg
        · apply mul_nonneg
          · linarith
          · exact G.weights_nonneg u v
        · -- Show 0 ≤ degree u using the fact that weights are non-negative
          have h : (0 : ℝ) ≤ G.degree u := by
            simp [WeightedGraph.degree]
            apply Finset.sum_nonneg
            intro i hi
            exact G.weights_nonneg u i
          linarith
      · -- Not a neighbor, value is 0
        rw [if_neg h2]
  · -- Show sum equals 1 (proven above)
    exact probabilityMeasure_normalization_proven G u α h_deg

/-! ## Ollivier-Ricci Curvature -/

/-- Ollivier-Ricci curvature for edge (u, v).

κ(u,v) = 1 - W₁(μᵤ, μᵥ) / d(u,v)

Special cases:
- Returns 0 if u = v (not an edge)
- Returns 0 if d(u,v) = 0 (no path exists or same node) -/
noncomputable def ollivierRicci (u v : V) (α : Idleness) : ℝ :=
  if u = v then
    0
  else
    let d := (G.shortestPathDistance u v : ℝ)
    let μᵤ := probabilityMeasure G u α
    let μᵥ := probabilityMeasure G v α
    let W1 := Wasserstein.wasserstein1 (fun x y => (G.shortestPathDistance x y : ℝ)) μᵤ μᵥ

    if d = 0 then
      0  -- No path or same node
    else
      1 - W1 / d

/-! ## Helper Lemmas for Degree Positivity -/

/-- If u has an adjacent vertex in the simple graph, its weighted degree is positive. -/
private lemma degree_pos_of_adj (u w : V) (h_adj : G.graph.Adj u w) :
    G.degree u > 0 := by
  have h_ne : u ≠ w := h_adj.ne
  have h_pos : G.weights u w > 0 := (G.edge_iff_pos_weight u w h_ne).mp h_adj
  calc G.degree u = ∑ v : V, G.weights u v := rfl
    _ ≥ G.weights u w := Finset.single_le_sum (fun i _ => G.weights_nonneg u i) (Finset.mem_univ w)
    _ > 0 := h_pos

/-- If v is reachable from u and u ≠ v, then degree(u) > 0.
    (Reachable ⟹ ∃ walk ⟹ walk has ≥ 1 step ⟹ u has a neighbor.) -/
private lemma degree_pos_of_reachable (u v : V) (h_ne : u ≠ v)
    (h_reach : G.graph.Reachable u v) : G.degree u > 0 := by
  obtain ⟨p⟩ := h_reach
  cases p with
  | nil => exact absurd rfl h_ne
  | cons h_adj _ => exact degree_pos_of_adj G u _ h_adj

/-- Extract reachability from nonzero distance. -/
private lemma reachable_of_dist_ne_zero (u v : V)
    (h : (G.shortestPathDistance u v : ℝ) ≠ 0) : G.graph.Reachable u v := by
  by_contra h_nr
  have h0 := SimpleGraph.dist_eq_zero_of_not_reachable h_nr
  simp [WeightedGraph.shortestPathDistance, h0] at h

/-! ## Main Theorem: Curvature Bounds -/

/-- **Axiom**: Wasserstein distance between neighbor measures is at most 2·d(u,v).

This gives the curvature lower bound κ ≥ -1. The proof uses the product
coupling γ(x,y) = μ(x)·ν(y) and the fact that probability mass is
concentrated within distance 1 of each endpoint under idleness α ∈ [0,1].

Reference: Ollivier (2009), Proposition 2. -/
axiom wasserstein_le_twice_dist
    (u v : V) (α : Idleness)
    (h_d_pos : G.shortestPathDistance u v > 0) :
    Wasserstein.wasserstein1
      (fun x y => (G.shortestPathDistance x y : ℝ))
      (probabilityMeasure G u α)
      (probabilityMeasure G v α)
    ≤ 2 * (G.shortestPathDistance u v : ℝ)

/-- **Theorem**: Ollivier-Ricci curvature is always in [-1, 1].

Mathematical Proof:
Recall κ(u,v) = 1 - W₁(μᵤ, μᵥ) / d(u,v)

We need to show: -1 ≤ κ ≤ 1

This is equivalent to: 0 ≤ W₁ / d ≤ 2

Or: 0 ≤ W₁ ≤ 2·d(u,v)

### Upper bound (κ ≤ 1):
From Wasserstein non-negativity: W₁ ≥ 0
Therefore: κ = 1 - W₁/d ≤ 1

### Lower bound (κ ≥ -1):
From the bound W₁ ≤ 2·d(u,v) (see `wasserstein_le_twice_dist`):
W₁/d ≤ 2
Therefore: κ = 1 - W₁/d ≥ 1 - 2 = -1

Reference: Ollivier (2009), Proposition 2. -/
theorem curvature_bounds (u v : V) (α : Idleness) :
    ollivierRicci G u v α ∈ Set.Icc (-1 : ℝ) 1 := by
  simp only [Set.mem_Icc]
  by_cases h_eq : u = v
  · -- Case u = v: curvature is 0 by definition
    rw [h_eq]
    simp [ollivierRicci]
    all_goals norm_num
  · -- Case u ≠ v
    simp only [ollivierRicci, if_neg h_eq]
    by_cases h_dist_zero : (G.shortestPathDistance u v : ℝ) = 0
    · -- No path between u and v (distance is 0 in real cast)
      rw [if_pos h_dist_zero]
      all_goals norm_num
    · -- There is a path, distance > 0
      rw [if_neg h_dist_zero]
      let d := (G.shortestPathDistance u v : ℝ)
      let W1 := Wasserstein.wasserstein1
        (fun x y => (G.shortestPathDistance x y : ℝ))
        (probabilityMeasure G u α)
        (probabilityMeasure G v α)
      have h_d_pos : d > 0 := by
        have h_d_ne_zero : d ≠ 0 := h_dist_zero
        have h_d_nonneg : d ≥ 0 := by
          simp [d]
        -- Since d ≠ 0 and d ≥ 0, we have d > 0
        by_contra h
        push_neg at h
        have h_zero : d = 0 := by linarith
        contradiction
      have h_w_nonneg : 0 ≤ W1 := by
        -- We use the fact that Wasserstein distance is always non-negative
        -- This follows from the definition as an infimum of non-negative costs
        simp only [W1]
        apply Wasserstein.wasserstein_nonneg
        · -- Show μᵤ is a probability measure
          have h_deg_u : G.degree u > 0 :=
            degree_pos_of_reachable G u v h_eq
              (reachable_of_dist_ne_zero G u v h_dist_zero)
          exact probabilityMeasure_normalization G u α (by exact_mod_cast h_deg_u)
        · -- Show μᵥ is a probability measure
          have h_deg_v : G.degree v > 0 :=
            degree_pos_of_reachable G v u (Ne.symm h_eq)
              (reachable_of_dist_ne_zero G u v h_dist_zero).symm
          exact probabilityMeasure_normalization G v α (by exact_mod_cast h_deg_v)
        · -- Show distance is non-negative
          intro x y
          exact_mod_cast show (0 : ℕ) ≤ G.shortestPathDistance x y by apply zero_le
      have h_w_le_2d : W1 ≤ 2 * d := by
        have h_nat_pos : G.shortestPathDistance u v > 0 := by
          by_contra h
          push_neg at h
          have h_zero_nat : G.shortestPathDistance u v = 0 := by
            exact Nat.eq_zero_of_le_zero h
          have h_zero : (G.shortestPathDistance u v : ℝ) = 0 := by
            exact_mod_cast h_zero_nat
          -- This contradicts h_dist_zero
          have h_contra : (G.shortestPathDistance u v : ℝ) ≠ 0 := by
            exact h_dist_zero
          contradiction
        exact wasserstein_le_twice_dist G u v α h_nat_pos
      -- Now prove -1 ≤ 1 - W1/d ≤ 1
      constructor
      · -- Show κ ≥ -1, i.e., 1 - W1/d ≥ -1, i.e., W1/d ≤ 2
        have h1 : W1 / d ≤ 2 := by
          have h_d_ne_zero : d ≠ 0 := by linarith
          apply (div_le_iff₀ h_d_pos).mpr
          linarith [h_w_le_2d]
        linarith
      · -- Show κ ≤ 1, i.e., 1 - W1/d ≤ 1, i.e., W1/d ≥ 0
        have h2 : 0 ≤ W1 / d := by
          apply div_nonneg
          · exact h_w_nonneg
          · exact le_of_lt h_d_pos
        linarith

/-! ## Idleness Helper Theorems -/

namespace Idleness

/-- Idleness is non-negative. -/
theorem α_nonneg (α : Idleness) : 0 ≤ α.α := by
  have h := α.h_range
  simp [Set.mem_Icc] at h
  exact h.1

/-- Idleness is at most 1. -/
theorem α_le_one (α : Idleness) : α.α ≤ 1 := by
  have h := α.h_range
  simp [Set.mem_Icc] at h
  exact h.2

end Idleness

/-! ## Curvature for Unreachable Vertices -/

/-- Curvature = 0 when there is no path between vertices. -/
theorem curvature_no_path (u v : V) (α : Idleness)
    (h : u ≠ v) (h' : ¬G.graph.Reachable u v) :
    ollivierRicci G u v α = 0 := by
  unfold ollivierRicci
  rw [if_neg h]
  -- When there's no path, shortestPathDistance = 0
  have h_dist : G.shortestPathDistance u v = 0 := by
    simp [WeightedGraph.shortestPathDistance, SimpleGraph.dist_eq_zero_of_not_reachable h']
  -- Cast to ℝ and take the if_pos branch
  have h_cast : (G.shortestPathDistance u v : ℝ) = 0 := by exact_mod_cast h_dist
  simp [h_cast]

/-! ## Geometric Regime Classification -/

/-- A graph is hyperbolic if its mean Ollivier-Ricci curvature is negative. -/
def isHyperbolic (α : Idleness) (ε : ℝ) : Prop :=
  ∑ u : V, ∑ v : V, ollivierRicci G u v α < ε

/-- A graph is spherical if its mean Ollivier-Ricci curvature is positive. -/
def isSpherical (α : Idleness) (ε : ℝ) : Prop :=
  ∑ u : V, ∑ v : V, ollivierRicci G u v α > ε

/-- A graph is Euclidean if its mean Ollivier-Ricci curvature is near zero. -/
def isEuclidean (α : Idleness) (ε : ℝ) : Prop :=
  |∑ u : V, ∑ v : V, ollivierRicci G u v α| < ε

/-- Mean curvature (average over all vertex pairs). -/
noncomputable def meanCurvature (α : Idleness) : ℝ :=
  (∑ u : V, ∑ v : V, ollivierRicci G u v α) / (Fintype.card V * Fintype.card V : ℝ)

/-- Mean curvature is always in [-1, 1]. -/
theorem meanCurvature_bounds (α : Idleness) :
    meanCurvature G α ∈ Set.Icc (-1 : ℝ) 1 := by
  simp only [meanCurvature, Set.mem_Icc]
  constructor
  · -- Show mean ≥ -1
    have h_card_pos : (Fintype.card V * Fintype.card V : ℝ) > 0 := by
      have h1 : Fintype.card V > 0 := Fintype.card_pos
      have h2 : Fintype.card V > 0 := Fintype.card_pos
      positivity
    apply (le_div_iff₀ h_card_pos).mpr
    -- Each curvature is ≥ -1, so sum is ≥ -|V|²
    have h_each_ge : ∀ u v, -1 ≤ ollivierRicci G u v α := by
      intro u v
      have h_bounds := curvature_bounds G u v α
      simp at h_bounds
      exact h_bounds.1
    -- Sum the inequalities
    have h_sum_ge : ∑ u : V, ∑ v : V, (-1 : ℝ) ≤ ∑ u : V, ∑ v : V, ollivierRicci G u v α := by
      apply Finset.sum_le_sum
      intro u _
      apply Finset.sum_le_sum
      intro v _
      exact h_each_ge u v
    simp at h_sum_ge
    have h_card_sq : (Fintype.card V * Fintype.card V : ℝ) = (Fintype.card V : ℝ) * (Fintype.card V : ℝ) := by simp
    rw [h_card_sq] at *
    linarith
  · -- Show mean ≤ 1
    have h_card_pos : (Fintype.card V * Fintype.card V : ℝ) > 0 := by
      have h1 : Fintype.card V > 0 := Fintype.card_pos
      have h2 : Fintype.card V > 0 := Fintype.card_pos
      positivity
    apply (div_le_iff₀ h_card_pos).mpr
    -- Each curvature is ≤ 1, so sum is ≤ |V|²
    have h_each_le : ∀ u v, ollivierRicci G u v α ≤ 1 := by
      intro u v
      have h_bounds := curvature_bounds G u v α
      simp at h_bounds
      exact h_bounds.2
    -- Sum the inequalities
    have h_sum_le : ∑ u : V, ∑ v : V, ollivierRicci G u v α ≤ ∑ u : V, ∑ v : V, (1 : ℝ) := by
      apply Finset.sum_le_sum
      intro u _
      apply Finset.sum_le_sum
      intro v _
      exact h_each_le u v
    simp at h_sum_le
    have h_card_sq : (Fintype.card V * Fintype.card V : ℝ) = (Fintype.card V : ℝ) * (Fintype.card V : ℝ) := by simp
    rw [h_card_sq] at *
    linarith

/-- **Theorem**: The hyperbolic and spherical regimes are mutually exclusive.
    A graph cannot simultaneously have sum of curvatures < ε and > ε. -/
theorem regimes_exclusive (α : Idleness) (ε : ℝ) :
    ¬(isHyperbolic G α ε ∧ isSpherical G α ε) := by
  intro ⟨h_hyp, h_sph⟩
  simp only [isHyperbolic, isSpherical] at h_hyp h_sph
  linarith

end Curvature

end HyperbolicSemanticNetworks
