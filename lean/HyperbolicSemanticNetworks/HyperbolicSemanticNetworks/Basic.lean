import Mathlib.Combinatorics.SimpleGraph.Basic
import Mathlib.Combinatorics.SimpleGraph.Metric
import Mathlib.Probability.ProbabilityMassFunction.Basic
import Mathlib.Data.Real.Basic
import Mathlib.Order.Interval.Set.Basic
/-!
# Basic Definitions for Semantic Networks

This module defines the foundational mathematical structures for semantic network analysis:
- Simple graphs with weighted edges
- Probability measures on graph nodes
- Network metrics (clustering, degree, etc.)

## References

- Ollivier (2009): "Ricci curvature of Markov chains on metric spaces"
- Ni et al. (2015): "Community detection on networks via Ricci flow"
-/


/-! ## Type Definitions -/

namespace HyperbolicSemanticNetworks

/-- A weighted simple graph for semantic networks.
    Weights represent association strengths (normalized to [0,1]). -/
structure WeightedGraph (V : Type) [Fintype V] [DecidableEq V] where
  /-- The underlying simple graph structure -/
  graph : SimpleGraph V
  /-- Edge weights: unconnected nodes have weight 0 -/
  weights : V → V → ℝ
  /-- Weights are non-negative -/
  weights_nonneg : ∀ u v, 0 ≤ weights u v
  /-- Symmetry for undirected graphs -/
  weights_sym : ∀ u v, weights u v = weights v u
  /-- No self-loops in semantic networks -/
  no_self_loops : ∀ v, weights v v = 0
  /-- Weights are positive exactly when there's an edge -/
  edge_iff_pos_weight : ∀ u v, u ≠ v → (graph.Adj u v ↔ weights u v > 0)

instance {V : Type} [Fintype V] [DecidableEq V] : Coe (WeightedGraph V) (SimpleGraph V) where
  coe G := G.graph

namespace WeightedGraph

variable {V : Type} [Fintype V] [DecidableEq V] (G : WeightedGraph V)

/-! ## Degree and Neighborhood -/

/-- The weighted degree of a node (sum of incident edge weights). -/
def degree (v : V) : ℝ :=
  ∑ u : V, G.weights v u

/-- The set of neighbors of a node (nodes connected by positive weight). -/
noncomputable def neighbors (v : V) : Finset V :=
  Finset.filter (fun u => decide (G.weights v u > 0) = true) Finset.univ

/-! ## Shortest Path Distance -/

/-- Shortest path distance (unweighted).
    Uses SimpleGraph.dist which returns 0 for unreachable pairs (junk value)
    and 0 for v = v. Returns ℕ. -/
noncomputable def shortestPathDistance (u v : V) : ℕ :=
  G.graph.dist u v

/-- Distance is symmetric. -/
lemma dist_symmetric (u v : V) :
    G.shortestPathDistance u v = G.shortestPathDistance v u := by
  simp [shortestPathDistance, SimpleGraph.dist_comm]

/-- Distance is zero for same node. -/
lemma dist_self_zero (v : V) :
    G.shortestPathDistance v v = 0 := by
  simp [shortestPathDistance]

/-- Distance is positive for different reachable nodes. -/
lemma dist_pos_of_ne {u v : V} (h : u ≠ v) (h' : G.graph.Reachable u v) :
    G.shortestPathDistance u v > 0 := by
  simp [shortestPathDistance]
  exact h'.pos_dist_of_ne h

end WeightedGraph

/-! ## Probability Measures for Curvature -/

namespace ProbabilityMeasure

variable {V : Type} [Fintype V] [DecidableEq V]

/-- A probability measure on graph nodes.
    In Ollivier-Ricci curvature, this represents the "ball" around a node. -/
def IsProbabilityMeasure (μ : V → ℝ) : Prop :=
  (∀ v, 0 ≤ μ v) ∧ (∑ v, μ v = 1)

/-- The support of a probability measure. -/
noncomputable def support (μ : V → ℝ) : Finset V :=
  Finset.filter (fun v => decide (μ v > 0) = true) Finset.univ

/-- Probability measures are bounded by 1. -/
lemma prob_le_one {μ : V → ℝ} (h : IsProbabilityMeasure μ) (v : V) :
    μ v ≤ 1 := by
  have h_total : ∑ w : V, μ w = 1 := h.2
  have h_nonneg : ∀ w, 0 ≤ μ w := h.1
  have : μ v ≤ ∑ w : V, μ w := by
    apply Finset.single_le_sum
    · intro i _
      exact h_nonneg i
    · simp
  rw [h_total] at this
  exact this

end ProbabilityMeasure

/-! ## Clustering Coefficient -/

noncomputable section

namespace Clustering

variable {V : Type} [Fintype V] [DecidableEq V] [LinearOrder V] (G : WeightedGraph V)
  [DecidableRel G.graph.Adj]

/-- Count triangles involving node v.
    A triangle is a pair of neighbors that are connected. -/
def triangleCount (v : V) : ℕ :=
  let N := G.neighbors v
  (Finset.filter (fun p : V × V => p.1 ∈ N ∧ p.2 ∈ N ∧ p.1 < p.2 ∧ G.graph.Adj p.1 p.2)
    (Finset.univ ×ˢ Finset.univ)).card

/-- Local clustering coefficient for node v.
    C(v) = 2 × triangles / (degree × (degree - 1))
    Returns 0 if degree < 2. -/
def localClustering (v : V) : ℝ :=
  let deg := (G.neighbors v).card
  if deg < 2 then
    0
  else
    (2 * triangleCount G v : ℝ) / (deg * (deg - 1) : ℝ)

/-- Helper: triangle count is at most the number of neighbor pairs. -/
lemma triangleCount_le_neighbor_pairs (v : V) :
    triangleCount G v ≤ (G.neighbors v).card * ((G.neighbors v).card - 1) / 2 := by
  sorry

/-- Local clustering is always in [0, 1]. -/
theorem localClustering_bounds (v : V) :
    localClustering G v ∈ Set.Icc (0 : ℝ) 1 := by
  simp only [Set.mem_Icc, localClustering]
  split_ifs with h_deg
  · exact ⟨le_refl 0, zero_le_one⟩
  · constructor
    · apply div_nonneg
      · positivity
      · have h_pos : (G.neighbors v).card ≥ 2 := by omega
        have hd : ((G.neighbors v).card : ℝ) ≥ 2 := by exact_mod_cast h_pos
        have hd1 : ((G.neighbors v).card : ℝ) - 1 ≥ 1 := by linarith
        positivity
    · have h_pos : (G.neighbors v).card ≥ 2 := by omega
      have h_ge1 : (G.neighbors v).card ≥ 1 := by omega
      have hd := triangleCount_le_neighbor_pairs G v
      have h2 : 2 * triangleCount G v ≤ (G.neighbors v).card * ((G.neighbors v).card - 1) := by
        have := Nat.div_mul_le_self ((G.neighbors v).card * ((G.neighbors v).card - 1)) 2
        omega
      have hcast : (2 * triangleCount G v : ℝ) ≤ ((G.neighbors v).card : ℝ) * (((G.neighbors v).card : ℝ) - 1) := by
        have h_sub_cast : ((G.neighbors v).card : ℝ) - 1 = (((G.neighbors v).card - 1 : ℕ) : ℝ) := by
          rw [Nat.cast_sub h_ge1]; norm_num
        rw [h_sub_cast, ← Nat.cast_mul, ← Nat.cast_ofNat]
        exact_mod_cast h2
      have hd2 : ((G.neighbors v).card : ℝ) ≥ 2 := by exact_mod_cast h_pos
      have hd1 : ((G.neighbors v).card : ℝ) - 1 ≥ 1 := by linarith
      have hdenom_pos : ((G.neighbors v).card : ℝ) * (((G.neighbors v).card : ℝ) - 1) > 0 := by positivity
      rw [div_le_one hdenom_pos]
      exact hcast

/-- Average clustering coefficient over all nodes. -/
def averageClustering : ℝ :=
  (∑ v : V, localClustering G v) / (Fintype.card V : ℝ)

/-- Average clustering is in [0, 1]. -/
theorem averageClustering_bounds :
    averageClustering G ∈ Set.Icc (0 : ℝ) 1 := by
  simp [averageClustering, Set.mem_Icc]
  constructor
  · -- ≥ 0
    apply div_nonneg
    · apply Finset.sum_nonneg
      intro v _
      exact (localClustering_bounds G v).1
    · exact Nat.cast_nonneg _
  · -- ≤ 1
    have h : ∑ v : V, localClustering G v ≤ Fintype.card V := by
      have h' : ∀ v, localClustering G v ≤ 1 := by
        intro v
        exact (localClustering_bounds G v).2
      calc ∑ v : V, localClustering G v
          ≤ ∑ v : V, (1 : ℝ) := by
            apply Finset.sum_le_sum
            intro v _
            exact h' v
        _ = Fintype.card V := by simp
    by_cases h_empty : Fintype.card V = 0
    · simp [h_empty]
    · have h_pos : (Fintype.card V : ℝ) > 0 := by
        exact Nat.cast_pos.mpr (Nat.pos_of_ne_zero h_empty)
      rw [div_le_one h_pos]
      exact h

end Clustering

end

end HyperbolicSemanticNetworks
