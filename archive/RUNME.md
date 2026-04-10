# RUNME — Full Reproduction Instructions

**Paper**: "When Are Semantic Networks Hyperbolic? A Curvature Phase Transition Theory with Cross-Linguistic Validation"
**Authors**: Demetrios C. Agourakis
**Zenodo DOI**: 10.5281/zenodo.18903099
**Version**: 4.0 (March 2026, Phase 8 complete)

---

## Prerequisites

```bash
# Julia >= 1.9
julia --version

# Rust >= 1.70
rustc --version

# Lean 4 / Lake (via elan)
lake --version

# Sounio (beta.4 — optional, for cross-validation)
SOUC="${HOME}/work/sounio-lang/artifacts/omega/souc-bin/souc-linux-x86_64-gpu"
"${SOUC}" --version   # souc 1.0.0-beta.4
```

Install Julia dependencies:

```bash
julia --project=julia -e 'using Pkg; Pkg.instantiate()'
```

---

## 1. Phase Transition (Table 1 + Figure 1)

```bash
# N=100 reference sweep (exact LP, ~30 min)
julia --project=julia julia/scripts/phase_transition_pure_julia.jl
# -> results/experiments/phase_transition_pure_julia.json

# N=1000 validation (~4 h)
julia --project=julia julia/scripts/run_n1000.jl

# Finite-size scaling curve (N in {50,100,200,500,1000})
julia --project=julia julia/scripts/run_er_comparison.jl
# -> eta_c(N) = 3.75 - 14.62/sqrt(N), R^2=0.995
```

---

## 2. Semantic Network ORC (Tables 2-6 + Figures 2,3,5,6,7,8)

```bash
# Exact LP ORC on all 11 networks (~2 h total)
julia --project=julia julia/scripts/unified_semantic_orc.jl
# -> results/unified/*_exact_lp.json

# Bridge analysis + null models
julia --project=julia julia/scripts/bridge_analysis.jl

# Analytical phase boundary (Hehl formula)
julia --project=julia julia/scripts/analytical_eta_c.jl
```

---

## 3. Hypercomplex Embedding (Table 7 + Figure 4, Appendix C + Table 8)

```bash
# Cayley-Dickson tower d in {4,8,16,32,64,128} for N=100 k-regular graphs
# Each takes ~3-10 min
for d in 4 8 16 32 64 128; do
    julia --project=julia julia/scripts/hypercomplex_lp.jl --N 100 --d $d
done
# -> results/experiments/hypercomplex_lp_n100_d{4,8,16,32,64,128}.json

# Power-law fit beta-bar (Appendix C)
julia --project=julia julia/scripts/powerlaw_fit_kappa_d.jl
# -> results/unified/powerlaw_fit_kappa_d.json
# Key finding: beta-bar = 0.283 +/- 0.034 (below JL bound of 0.5 -- saturation)

# Semantic networks d in {4,8,16}
julia --project=julia julia/scripts/hypercomplex_semantic_orc.jl
```

---

## 4. Scale-Free Robustness (Appendix A + Figure 9)

```bash
julia --project=julia julia/scripts/run_ba_comparison.jl
julia --project=julia julia/scripts/run_ba_scaling.jl
```

---

## 5. Discrete Ricci Flow (Appendix B + Figure 10)

```bash
julia --project=julia julia/scripts/ricci_flow_semantic.jl
# -> results/experiments/ricci_flow_*.json (10 networks)
```

---

## 6. Generate All Figures

```bash
julia --project=julia julia/scripts/generate_monograph_figures.jl
# -> figures/monograph/figure{1..11}_*.{pdf,png}
# Includes Figure 11: power-law decay of kappa-bar vs d (log-log)
```

---

## 7. Compile Manuscript

```bash
cd manuscript/latex
pdflatex monograph.tex   # run twice for cross-references
pdflatex monograph.tex
# -> monograph.pdf (0 errors, 0 undefined references)
```

---

## 8. Lean 4 Formal Verification

```bash
cd lean/HyperbolicSemanticNetworks
lake build
# Expected: 0 errors; documented sorry declarations in non-core modules

# Verify core theorems (0 sorry)
lake env lean -e '#print axioms HyperbolicSemanticNetworks.Curvature.regimes_exclusive'
```

---

## 9. Rust Performance Kernels (Optional)

```bash
cd rust
cargo build --release
cargo test --workspace
cargo bench --bench wasserstein_bench
```

---

## 10. Phase 8 Sounio Science (Optional, beta.4 required)

```bash
SOUC="${HOME}/work/sounio-lang/artifacts/omega/souc-bin/souc-linux-x86_64-gpu"

# Phase 1: ORC sweep N=100 (sign change confirmed)
bash experiments/01_deep_integration/run.sh phase_transition_full

# Phase 3: Semantic network classification (9/9 correct)
"${SOUC}" run experiments/03_semantic_networks/semantic_orc.sio

# Phase 5 (Clinical): ADHD-200 FC -> ClinicalCurvatureProfile
"${SOUC}" run experiments/05_clinical/clinical_fc_orc.sio

# Phase 8A: Epistemic Ricci flow (uncertainty-aware, kappa CI per step)
"${SOUC}" run experiments/08_epistemic_flow/epistemic_ricci_flow.sio

# Phase 8C: Power-law cross-validation (Sounio vs Julia beta-bar)
"${SOUC}" run experiments/08_epistemic_flow/powerlaw_validate.sio
```

---

## Expected Key Numbers

| Result | Value | Source |
|--------|-------|--------|
| eta_c(N=100) | 2.29 | phase_transition_pure_julia.json |
| eta_c(infinity) | 3.75 | run_er_comparison.jl |
| SWOW Dutch kappa-bar | +0.099 | swow_nl_exact_lp.json |
| Power-law exponent | 0.283 +/- 0.034 | powerlaw_fit_kappa_d.json |
| Lean core sorry | 0 | lake build |
| ADHD subjects spherical | 10/10 | clinical_fc_orc.sio |

---

## Troubleshooting

**Julia FFI not found**: `cd rust/curvature && cargo build --release`

**Dependency conflicts**: `rm julia/Manifest.toml && julia --project=julia -e 'using Pkg; Pkg.instantiate()'`

**Lean timeout**: `cd lean/HyperbolicSemanticNetworks && lake build HyperbolicSemanticNetworks.Curvature`

**Sounio .exp() silent fail**: Use `sc_exp(x)` (Taylor series) instead of `.exp()` method
