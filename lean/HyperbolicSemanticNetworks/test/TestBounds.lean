/-!
# Bounds Verification Tests

Tests that all bounds theorems are correctly proven.
-/ 

import HyperbolicSemanticNetworks

open HyperbolicSemanticNetworks

namespace TestBounds

/-- Curvature bounds are proven. -/
example {V : Type} [Fintype V] [DecidableEq V] 
    (G : WeightedGraph V) (u v : V) (α : Curvature.Idleness) :
    Curvature.ollivierRicci G u v α ∈ Set.Icc (-1 : ℝ) 1 := by
  apply Bounds.curvature_bounds

/-- Clustering bounds are proven. -/
example {V : Type} [Fintype V] [DecidableEq V] 
    (G : WeightedGraph V) (v : V) :
    Clustering.localClustering G v ∈ Set.Icc (0 : ℝ) 1 := by
  apply Bounds.local_clustering_bounds

/-- Mean curvature bounds are proven. -/
example {V : Type} [Fintype V] [DecidableEq V] 
    (G : WeightedGraph V) (α : Curvature.Idleness) :
    Curvature.meanCurvature G α ∈ Set.Icc (-1 : ℝ) 1 := by
  apply Bounds.mean_curvature_bounds

/-- Density parameter is non-negative. -/
example {V : Type} [Fintype V] [DecidableEq V] 
    (G : WeightedGraph V) :
    PhaseTransition.densityParameter G ≥ 0 := by
  apply Bounds.density_nonneg

end TestBounds