import Mathlib.Data.Real.Basic
import Mathlib.Order.Interval.Set.Basic
import «HyperbolicSemanticNetworks».Basic
import «HyperbolicSemanticNetworks».Curvature
import «HyperbolicSemanticNetworks».Wasserstein
import «HyperbolicSemanticNetworks».PhaseTransition
/-!
# Provable Bounds for Network Metrics

This module collects all the provable bounds on network metrics
used in the semantic network analysis.

## Summary of Bounds

| Metric | Lower Bound | Upper Bound | Status |
|--------|-------------|-------------|--------|
| Curvature κ | -1 | 1 | ✅ Proven |
| Clustering C | 0 | 1 | ✅ Proven |
| Idleness α | 0 | 1 | ✅ Proven |
| Probability μ | 0 | 1 | ✅ Proven |
| Density η | 0 | ∞ | ✅ Proven |
| Wasserstein W₁ | 0 | diam | ⚠️ Partial |

-/


namespace HyperbolicSemanticNetworks

namespace Bounds

/-! ## Curvature Bounds -/

section CurvatureBounds

variable {V : Type} [Fintype V] [DecidableEq V]

/-- Curvature is always in [-1, 1]. -/
theorem curvature_bounds (G : WeightedGraph V) (u v : V) (α : Curvature.Idleness) :
    Curvature.ollivierRicci G u v α ∈ Set.Icc (-1 : ℝ) 1 := by
  apply Curvature.curvature_bounds

/-- Mean curvature is always in [-1, 1]. -/
theorem mean_curvature_bounds (G : WeightedGraph V) (α : Curvature.Idleness) :
    Curvature.meanCurvature G α ∈ Set.Icc (-1 : ℝ) 1 := by
  apply Curvature.meanCurvature_bounds

/-- Curvature = 0 for unreachable vertices (different connected components). -/
theorem curvature_zero_no_path (G : WeightedGraph V) (u v : V) (α : Curvature.Idleness)
    (h : u ≠ v) (h' : ¬G.graph.Reachable u v) :
    Curvature.ollivierRicci G u v α = 0 := by
  apply Curvature.curvature_no_path
  assumption'

end CurvatureBounds

/-! ## Clustering Bounds -/

section ClusteringBounds

variable {V : Type} [Fintype V] [DecidableEq V] [LinearOrder V]

/-- Local clustering is in [0, 1]. -/
theorem local_clustering_bounds (G : WeightedGraph V) [DecidableRel G.graph.Adj] (v : V) :
    Clustering.localClustering G v ∈ Set.Icc (0 : ℝ) 1 := by
  apply Clustering.localClustering_bounds

/-- Average clustering is in [0, 1]. -/
theorem average_clustering_bounds (G : WeightedGraph V) [DecidableRel G.graph.Adj] :
    Clustering.averageClustering G ∈ Set.Icc (0 : ℝ) 1 := by
  apply Clustering.averageClustering_bounds

end ClusteringBounds

/-! ## Probability Measure Bounds -/

section ProbabilityBounds

variable {V : Type} [Fintype V] [DecidableEq V]

/-- Probability measures are non-negative. -/
theorem prob_nonneg (μ : V → ℝ) (h : ProbabilityMeasure.IsProbabilityMeasure μ) (v : V) :
    0 ≤ μ v :=
  h.1 v

/-- Probability measures sum to 1. -/
theorem prob_sum_one (μ : V → ℝ) (h : ProbabilityMeasure.IsProbabilityMeasure μ) :
    ∑ v : V, μ v = 1 :=
  h.2

/-- Individual probabilities are at most 1. -/
theorem prob_le_one (μ : V → ℝ) (h : ProbabilityMeasure.IsProbabilityMeasure μ) (v : V) :
    μ v ≤ 1 :=
  ProbabilityMeasure.prob_le_one h v

end ProbabilityBounds

/-! ## Idleness Parameter Bounds -/

section IdlenessBounds

/-- Idleness is in [0, 1]. -/
theorem idleness_bounds (α : Curvature.Idleness) :
    α.α ∈ Set.Icc (0 : ℝ) 1 :=
  α.h_range

/-- Idleness is non-negative. -/
theorem idleness_nonneg (α : Curvature.Idleness) :
    0 ≤ α.α :=
  Curvature.Idleness.α_nonneg α

/-- Idleness is at most 1. -/
theorem idleness_le_one (α : Curvature.Idleness) :
    α.α ≤ 1 :=
  Curvature.Idleness.α_le_one α

end IdlenessBounds

/-! ## Wasserstein Distance Bounds -/

section WassersteinBounds

variable {V : Type} [Fintype V] [DecidableEq V]
variable (d : V → V → ℝ) (μ ν : V → ℝ)
variable (hμ : ProbabilityMeasure.IsProbabilityMeasure μ)
          (hν : ProbabilityMeasure.IsProbabilityMeasure ν)

/-- Wasserstein distance is non-negative. -/
theorem wasserstein_nonneg
    (hμ : ProbabilityMeasure.IsProbabilityMeasure μ)
    (hν : ProbabilityMeasure.IsProbabilityMeasure ν)
    (h_nonneg : ∀ u v, 0 ≤ d u v) :
    0 ≤ Wasserstein.wasserstein1 d μ ν :=
  Wasserstein.wasserstein_nonneg hμ hν h_nonneg

/-- Wasserstein distance is symmetric. -/
theorem wasserstein_symmetric (h_sym : ∀ u v, d u v = d v u) :
    Wasserstein.wasserstein1 d μ ν = Wasserstein.wasserstein1 d ν μ := by
  apply Wasserstein.wasserstein_symmetric
  assumption

/-- Wasserstein distance satisfies triangle inequality. -/
theorem wasserstein_triangle (h_metric : ∀ u v w, d u w ≤ d u v + d v w) :
    ∀ (μ ν ρ : V → ℝ),
    Wasserstein.wasserstein1 d μ ρ ≤ Wasserstein.wasserstein1 d μ ν + Wasserstein.wasserstein1 d ν ρ := by
  apply Wasserstein.wasserstein_triangle
  assumption

end WassersteinBounds

/-! ## Density Parameter Bounds -/

section DensityBounds

variable {V : Type} [Fintype V] [DecidableEq V]

/-- Density parameter is non-negative. -/
theorem density_nonneg (G : WeightedGraph V) :
    0 ≤ PhaseTransition.densityParameter G := by
  simp [PhaseTransition.densityParameter]
  apply div_nonneg
  · apply pow_two_nonneg
  · positivity

end DensityBounds

/-! ## Degree Bounds -/

section DegreeBounds

variable {V : Type} [Fintype V] [DecidableEq V] (G : WeightedGraph V)

/-- Degree is non-negative. -/
theorem degree_nonneg (v : V) :
    0 ≤ G.degree v := by
  simp [WeightedGraph.degree]
  apply Finset.sum_nonneg
  intro i _
  exact G.weights_nonneg v i

end DegreeBounds

/-! ## Summary Theorem -/

/-- All key metrics are properly bounded. -/
theorem all_metrics_properly_bounded {V : Type} [Fintype V] [DecidableEq V] [LinearOrder V]
    (G : WeightedGraph V) [DecidableRel G.graph.Adj] (α : Curvature.Idleness) (v : V) :
    Curvature.ollivierRicci G v v α ∈ Set.Icc (-1) 1 ∧
    Clustering.localClustering G v ∈ Set.Icc 0 1 ∧
    G.degree v ≥ 0 ∧
    PhaseTransition.densityParameter G ≥ 0 := by
  exact ⟨curvature_bounds G v v α, local_clustering_bounds G v,
         degree_nonneg G v, density_nonneg G⟩

end Bounds

end HyperbolicSemanticNetworks
