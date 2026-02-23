import Lake
open Lake DSL

package «HyperbolicSemanticNetworks» where
  -- Settings applied to both builds and interactive editing
  leanOptions := #[
    ⟨`pp.unicode.fun, true⟩, -- pretty-prints `fun a ↦ b`
    ⟨`pp.proofs.withType, false⟩,
    ⟨`autoImplicit, false⟩,
    ⟨`relaxedAutoImplicit, false⟩,
    ⟨`linter.unusedSectionVars, false⟩
  ]
  -- Add any additional package configuration options here

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "v4.17.0"

@[default_target]
lean_lib «HyperbolicSemanticNetworks» where
  -- Add any library configuration options here
  globs := #[.submodules `HyperbolicSemanticNetworks]

require checkdecls from git "https://github.com/PatrickMassot/checkdecls.git"

meta if get_config? env = some "dev" then
require «doc-gen4» from git
  "https://github.com/leanprover/doc-gen4" @ "main"

/-! # Hyperbolic Semantic Networks - Lean Formalization

This project formalizes the mathematical foundations of the paper:
"Boundary Conditions for Hyperbolic Geometry in Semantic Networks"

## Structure

- **Basic.lean**: Graph definitions and network metrics
- **Curvature.lean**: Ollivier-Ricci curvature formalization  
- **Wasserstein.lean**: Optimal transport theory
- **PhaseTransition.lean**: Critical point analysis
- **Bounds.lean**: Provable bounds on curvature and clustering
- **Consistency.lean**: Cross-implementation verification

## Build Instructions

```bash
# Build the project
lake build

# Run tests
lake test

# Generate documentation
lake -R -Kenv=dev build HyperbolicSemanticNetworks:docs
```

## Key Theorems

1. `curvature_bounds`: κ ∈ [-1, 1] for all valid inputs
2. `clustering_bounds`: C ∈ [0, 1] for all networks
3. `phase_transition_critical`: Characterization of ⟨k⟩²/N ≈ 2.5
4. `implementation_equivalence`: Julia/Rust/Sounio compute same values

## References

- Ollivier (2009): Ricci curvature of Markov chains
- Ni et al. (2015, 2019): Community detection on networks via Ricci flow
- Agourakis (2025): Hyperbolic Geometry of Semantic Networks (this work)
-/