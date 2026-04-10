import «HyperbolicSemanticNetworks».Basic
import «HyperbolicSemanticNetworks».Wasserstein
import «HyperbolicSemanticNetworks».WassersteinProven
import «HyperbolicSemanticNetworks».Curvature
import «HyperbolicSemanticNetworks».PhaseTransition
import «HyperbolicSemanticNetworks».Bounds
import «HyperbolicSemanticNetworks».Consistency
import «HyperbolicSemanticNetworks».Axioms
import «HyperbolicSemanticNetworks».DynamicNetworks
import «HyperbolicSemanticNetworks».Hypercomplex
import «HyperbolicSemanticNetworks».RandomGraph
import «HyperbolicSemanticNetworks».RicciFlow
import «HyperbolicSemanticNetworks».SpectralGeometry
import «HyperbolicSemanticNetworks».Validation
import «HyperbolicSemanticNetworks».McDiarmid
import «HyperbolicSemanticNetworks».ProbabilityProofs
import «HyperbolicSemanticNetworks».TestExtraction
import «HyperbolicSemanticNetworks».LaTeXExport
import «HyperbolicSemanticNetworks».ComputationalVerification
import «HyperbolicSemanticNetworks».RandomGeometric
import «HyperbolicSemanticNetworks».SounioVerification
import «HyperbolicSemanticNetworks».OctonionGraph
import «HyperbolicSemanticNetworks».DepressionNetworks
/-!
# Hyperbolic Semantic Networks - Lean 4 Formalization

This is the main entry point for the Lean 4 formalization of
"Boundary Conditions for Hyperbolic Geometry in Semantic Networks".

## Module Structure

### Core Modules
- **Basic.lean**: Graph definitions, probability measures, clustering
- **Wasserstein.lean**: Optimal transport, Wasserstein-1 distance
- **WassersteinProven.lean**: Proofs (not axioms) for Wasserstein properties
- **Curvature.lean**: Ollivier-Ricci curvature definition and properties
- **PhaseTransition.lean**: Phase transition at ⟨k⟩²/N ≈ 2.5
- **Bounds.lean**: Provable bounds on all metrics
- **Consistency.lean**: Cross-implementation verification

### Extensions
- **RandomGraph.lean**: G(n,p) and configuration model
- **RandomGeometric.lean**: Random geometric graphs, ORC convergence to manifolds
- **RicciFlow.lean**: Discrete Ricci flow on networks
- **SpectralGeometry.lean**: Eigenvalues, Cheeger inequality
- **DynamicNetworks.lean**: Time-varying networks, temporal ORC stability
- **Hypercomplex.lean**: Cayley-Dickson tower (𝕆, 𝕊), brain network geometry
- **Axioms.lean**: Concentration inequalities (McDiarmid)

### Utilities
- **ProbabilityProofs.lean**: Proofs of probability measure properties
- **TestExtraction.lean**: Generate test vectors for Julia/Rust/Sounio
- **LaTeXExport.lean**: Paper-ready LaTeX documentation
- **ComputationalVerification.lean**: Verify experimental claims
- **Validation.lean**: Epistemic status tracking

## Key Theorems

| Theorem | Statement | Location |
|---------|-----------|----------|
| `curvature_bounds` | κ ∈ [-1, 1] | `Curvature.lean` |
| `clustering_bounds` | C ∈ [0, 1] | `Clustering` in `Basic.lean` |
| `mean_curvature_bounds` | κ̄ ∈ [-1, 1] | `Curvature.lean` |
| `probability_normalization` | Σ μ = 1 | `Curvature.lean` |
| `wasserstein_nonneg` | W₁ ≥ 0 | `Wasserstein.lean` |
| `wasserstein_symmetric_proven` | W₁(μ,ν) = W₁(ν,μ) | `WassersteinProven.lean` |
| `flow_preserves_positivity` | Ricci flow keeps weights positive | `RicciFlow.lean` |
| `cheeger_inequality` | λ₂/2 ≤ h_G ≤ √(2·d_max·λ₂) | `SpectralGeometry.lean` |
| `expectedEdges_ER` | E[|E|] = C(n,2)·p | `RandomGraph.lean` |
| `temporal_ORC_stability` | \|κ̄(W(t)) - κ̄(W(0))\| ≤ L·δ·t | `DynamicNetworks.lean` |
| `sweetSpot_persistence` | κ̄(W(0)) < -γ → κ̄(W(t)) < 0 | `DynamicNetworks.lean` |
| `brain_geometry_trichotomy` | Every octonion state is hyperbolic, spherical, or critical | `Hypercomplex.lean` |
| `probabilityMeasure_nonneg` | μᵤ(v) ≥ 0 | `ProbabilityProofs.lean` |
| `twoNode_curvature_bounds` | κ ∈ [0,1] for 2-node graph | `ProbabilityProofs.lean` |
| `orc_converges_to_manifold_curvature` | ORC → Ricci curvature (Krioukov et al.) | `RandomGeometric.lean` |
| `hyperbolic_orc_convergence` | ORC → -1 in hyperbolic space | `RandomGeometric.lean` |

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
def FORMALIZATION_VERSION : String := "2.1.2"

/-- Lean version required. -/
def LEAN_VERSION : String := "4.17.0"

/-- Paper reference. -/
def PAPER_REFERENCE : String :=
  "Agourakis (2025). Boundary Conditions for Hyperbolic Geometry in Semantic Networks. Nature Communications (submitted)."

end HyperbolicSemanticNetworks
