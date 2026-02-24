import «HyperbolicSemanticNetworks».Basic
import «HyperbolicSemanticNetworks».Wasserstein
import «HyperbolicSemanticNetworks».Curvature
import «HyperbolicSemanticNetworks».PhaseTransition
import «HyperbolicSemanticNetworks».Bounds
import «HyperbolicSemanticNetworks».Consistency
import «HyperbolicSemanticNetworks».Axioms
import «HyperbolicSemanticNetworks».DynamicNetworks
/-!
# Hyperbolic Semantic Networks - Lean 4 Formalization

This is the main entry point for the Lean 4 formalization of
"Boundary Conditions for Hyperbolic Geometry in Semantic Networks".

## Module Structure

- **Basic.lean**: Graph definitions, probability measures, clustering
- **Wasserstein.lean**: Optimal transport, Wasserstein-1 distance
- **Curvature.lean**: Ollivier-Ricci curvature definition and properties
- **PhaseTransition.lean**: Phase transition at ⟨k⟩²/N ≈ 2.5
- **Bounds.lean**: Provable bounds on all metrics
- **Consistency.lean**: Cross-implementation verification
- **DynamicNetworks.lean**: Time-varying networks, temporal ORC stability

## Key Theorems

| Theorem | Statement | Location |
|---------|-----------|----------|
| `curvature_bounds` | κ ∈ [-1, 1] | `Curvature.lean` |
| `clustering_bounds` | C ∈ [0, 1] | `Clustering` in `Basic.lean` |
| `mean_curvature_bounds` | κ̄ ∈ [-1, 1] | `Curvature.lean` |
| `probability_normalization` | Σ μ = 1 | `Curvature.lean` |
| `wasserstein_nonneg` | W₁ ≥ 0 | `Wasserstein.lean` |
| `temporal_ORC_stability` | \|κ̄(W(t)) - κ̄(W(0))\| ≤ L·δ·t | `DynamicNetworks.lean` |
| `sweetSpot_persistence` | κ̄(W(0)) < -γ → κ̄(W(t)) < 0 | `DynamicNetworks.lean` |

## Citation

```bibtex
@software{hsn_lean_formalization,
  title = {Lean 4 Formalization of Hyperbolic Semantic Networks},
  author = {Agourakis, Demetrios C.},
  year = {2025},
  url = {https://github.com/agourakis82/hyperbolic-semantic-networks}
}
```
-/


/-! Re-export commonly used definitions -/

namespace HyperbolicSemanticNetworks

/-! ## Version Information -/

/-- Formalization version (matches paper). -/
def FORMALIZATION_VERSION : String := "2.0.0"

/-- Lean version required. -/
def LEAN_VERSION : String := "4.17.0"

/-- Paper reference. -/
def PAPER_REFERENCE : String :=
  "Agourakis (2025). Boundary Conditions for Hyperbolic Geometry in Semantic Networks. Nature Communications (submitted)."

end HyperbolicSemanticNetworks
