/-
# HyperbolicSemanticNetworks - Main Module

This is the main import file for the Hyperbolic Semantic Networks formalization.

## Project Structure

The project is organized into the following modules:

- **Basic**: Graph types, weighted graphs, shortest paths
- **Measure**: Probability measures, Wasserstein distance
- **Curvature**: Ollivier-Ricci curvature definition and properties
- **TestExtraction**: Concrete test cases for cross-validation
- **WassersteinProven**: Proven properties of Wasserstein distance
- **Clustering**: Network clustering coefficients and properties
- **Spectral**: Spectral graph theory (Laplacian, eigenvalues, Cheeger)
- **RandomGraph**: Random graph models (Erdős-Rényi, Configuration)
- **PhaseTransition**: Phase transition conjecture at ⟨k⟩²/N ≈ 2.5
- **CrossValidation**: Numerical validation framework
- **Probabilistic**: Probabilistic bounds (McDiarmid inequality - axiom)
- **Convergence**: Convergence theorems for curvature
- **RicciFlow**: Ricci flow on weighted graphs
- **RandomGeometric**: RGGs and curvature convergence (Krioukov et al.)

## Key Features

1. **Proven Properties**: 
   - Wasserstein symmetry (via coupling bijection)
   - Laplacian symmetry and eigenvalue bounds
   - Ricci flow preserves edge weights

2. **Testable Implementations**: 
   - 6 concrete curvature test cases
   - JSON export for CI/CD validation

3. **Cross-Language Validation**: 
   - Julia reference implementation
   - Rust performance kernels  
   - Sounio type-safe experiments

## Author

Dr. Demetrios Agourakis  
Research: Hyperbolic Geometry of Semantic Networks  
Date: 2026-02-24  
Version: 2.1.2

## License

MIT License - See project LICENSE file
-/

-- Core modules
import «HyperbolicSemanticNetworks».Basic
import «HyperbolicSemanticNetworks».Measure
import «HyperbolicSemanticNetworks».Curvature
import «HyperbolicSemanticNetworks».TestExtraction
import «HyperbolicSemanticNetworks».WassersteinProven
import «HyperbolicSemanticNetworks».Clustering

-- Advanced modules
import «HyperbolicSemanticNetworks».Spectral
import «HyperbolicSemanticNetworks».RandomGraph
import «HyperbolicSemanticNetworks».PhaseTransition
import «HyperbolicSemanticNetworks».CrossValidation
import «HyperbolicSemanticNetworks».Probabilistic
import «HyperbolicSemanticNetworks».Convergence
import «HyperbolicSemanticNetworks».RicciFlow
import «HyperbolicSemanticNetworks».RandomGeometric

-- Clifford algebra and hypercomplex extensions
import «HyperbolicSemanticNetworks».Clifford
import «HyperbolicSemanticNetworks».HypercomplexPhase
import «HyperbolicSemanticNetworks».CliffordFMRI
import «HyperbolicSemanticNetworks».Visualization

-- Documentation modules
import «HyperbolicSemanticNetworks».Axioms

/-! ## Module Documentation -/

namespace HyperbolicSemanticNetworks

/-- Overall project version -/
def projectVersion : String := "2.1.2"

/-- Total number of modules -/
def moduleCount : Nat := 15

/-- Formalization completion percentage (estimated) -/
def completionPercentage : Nat := 76

/-- Number of proven theorems (estimated) -/
def theoremCount : Nat := 35

/-- Number of remaining axioms -/
def axiomCount : Nat := 9

/-- Core axioms that need proofs:

1. `probabilityMeasure_normalization` (Curvature.lean): Σ μ = 1
2. `wasserstein_le_twice_dist` (Curvature.lean): W₁ ≤ 2d
3. `curvature_bounds` (Curvature.lean): κ ∈ [-1, 1]
4. `mcdiarmid_inequality` (Axioms.lean): Concentration bounds
5. `wasserstein_triangle` (WassersteinProven.lean): W₁(u,w) ≤ W₁(u,v) + W₁(v,w)
6-9. Various properties in RandomGeometric (using `sorry`)

**Note**: These axioms are well-supported by:
- Extensive numerical validation
- Literature proofs (Ollivier 2009, Ni et al.)
- Cross-implementation agreement (Julia/Rust/Sounio)

They are formalization targets requiring Mathlib contributions.
-/
def coreAxioms : List String := 
  [ "probabilityMeasure_normalization"
  , "wasserstein_le_twice_dist"
  , "curvature_bounds"
  , "mcdiarmid_inequality"
  , "wasserstein_triangle"
  ]

/-- Project statistics summary. -/
def projectStats : String :=
  s!"Hyperbolic Semantic Networks Formalization v{projectVersion}\n" ++
  s!"Modules: {moduleCount}\n" ++
  s!"Completion: {completionPercentage}%\n" ++
  s!"Theorems: {theoremCount}\n" ++
  s!"Axioms remaining: {axiomCount}\n" ++
  s!"Test cases: 6 curvature + 2 Wasserstein"

end HyperbolicSemanticNetworks
