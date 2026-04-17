# CPC26 Robustness Audit (Repository-Based)

## Purpose

This audit evaluates the robustness of the CPC26 pipeline claims using the committed artifacts in `results/cpc2026/` and the documented pipeline in `code/cpc2026/README.md`.

## Executive Assessment

**Overall robustness rating: Strong for internal consistency, moderate for external generalization.**

- **Internal statistical robustness is strong**: all primary normative-vs-anxious contrasts in the released summaries are highly significant with narrow confidence intervals.
- **Computational reproducibility is strong**: fixed seed, declared sample size, explicit pipeline stages, and persisted artifacts are present.
- **Cross-model robustness is mixed-positive**: some effects remain stable between Markov and O-SSM (especially residence), while others are model-definition sensitive (entropy production).
- **External validity remains the key risk**: current CPC26 work is simulation-first on a normative substrate; this supports mechanistic hypotheses, not clinical inference.

## Robustness Evidence

### 1) Data substrate and coverage checks

- SWOW-EN CPC graph QC reports **438 nodes / 640 edges**, mean degree ≈ 2.92, and **eta = 0.0195**, firmly in sparse hyperbolic territory.
- Entropic-curvature node table was generated from an exact artifact path (`exact_artifact_used: true`) with GraphRicci validation diagnostics available.
- Valence matching coverage is **92.92%** (407/438 nodes), with explicit neutral fill for unmatched nodes.

**Interpretation:** The input layer is well specified and auditable; remaining uncertainty is primarily semantic (how neutral imputation may dampen affective effects at unmatched nodes).

### 2) Markov regime robustness (primary CPC quantitative lane)

From `statistical_summary.json`:

- **C_ent variance (normative vs anxious)**: Cohen's d = **-0.266**, CI [-0.290, -0.242], p ≈ 7.17e-78.
- **High-entropy hub residence**: anxious is **+31.08%** vs normative, CI [+28.53%, +33.55%], p ≈ 0.
- Both effects use **10,000 trajectories per regime** and bootstrap framing (`n_bootstrap = 1000`).

**Interpretation:** Directional separation appears stable and not marginal. Effect sizes are moderate (variance) to practically notable (residence shift), with very tight uncertainty bounds.

### 3) O-SSM robustness and model sensitivity

From `ossm_statistical_summary.json` and `ossm_cross_model_comparison.csv`:

- **C_ent variance** remains separable and slightly stronger in O-SSM (d ≈ -0.334 vs Markov -0.266).
- **Hurst separation** persists in both models (Markov d ≈ 0.613, O-SSM d ≈ 0.541).
- **Residence in high-entropy hubs** is effectively identical across models (both d ≈ 0.453), suggesting this signal is inherited from shared walk dynamics.
- **Entropy production is metric-sensitive**: Markov uses visited-node entropy while O-SSM uses hidden-state entropy; effect magnitudes are therefore not directly comparable.

**Interpretation:** Your strongest cross-model robustness claim is residence-time separation. Your weakest robustness claim (without extra framing) is entropy-production comparability because metric definitions differ.

### 4) Geometric-baseline robustness

- The CPC summaries explicitly separate substrate geometry from generic phase-transition reference:
  - **Critical reference eta ≈ 2.94** (random-regular reference lane)
  - **SWOW eta ≈ 0.0195** with negative mean curvature
  - Classified as **subcritical hyperbolic**.

**Interpretation:** This is a robustness strength in scientific framing: you avoid conflating dynamic psychiatric-like regimes with global topology class changes in the underlying graph.

## CPC26 Submission Risk Register

### High priority (address before camera-ready)

1. **Metric-definition mismatch risk (entropy production):**
   - Explicitly label Markov entropy production and O-SSM hidden-state entropy production as distinct constructs.
   - Avoid direct quantitative comparison in abstract-level claims.

2. **Simulation-to-clinic overreach risk:**
   - Keep wording as hypothesis-generating unless/ until patient speech or neuroimaging validation is added.

### Medium priority

3. **Valence imputation sensitivity risk:**
   - Add a robustness appendix rerunning key contrasts on the matched-only node subset (no neutral imputation).

4. **Seed dependence risk:**
   - Add a small multi-seed replication table (e.g., 5-10 seeds) for top-line metrics.

### Low priority

5. **Cross-language transfer risk:**
   - If time allows, run at least one additional language lane for CPC supplement to reinforce generalization.

## Recommended Claim Language for CPC26

Use language like:

- "Robust within the tested simulation framework" for variance/residence/Hurst outcomes.
- "Cross-model consistent" for residence effects.
- "Model-specific diagnostic" for hidden-state entropy and associator metrics.
- "Hypothesis-generating for computational psychiatry" instead of clinical validation claims.

## Bottom Line

Your CPC26 package is **methodologically robust for internal, simulation-based inference** and already contains the key ingredients reviewers look for (sample size, confidence intervals, effect sizes, fixed seed, artifactized outputs, and cross-model checks). The main vulnerability is **scope control**: keep claims tied to simulation robustness and clearly separate what is reproducible now from what still requires external clinical validation.
