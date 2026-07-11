# GUM-through-Sinkhorn — Results Summary

**Date:** 2026-05-27 · **Toolchain:** `./bin/souc run` (Sounio native) · all artifacts `//@ run-pass`.

Implements the *certified geometric early-warning* program: the optimal-transport solve defining
Ollivier–Ricci curvature κ runs on uncertainty-typed numbers, so a measurement uncertainty budget
propagates **through** the solve into κ, and the early warning is a confidence-gated obligation.
Full proposal + corrected theory status: `docs/research/geometric_critical_slowing_down_PROPOSAL.md`.

## Artifacts and verified outputs

| Stage | File (Sounio repo) | Token | Key numbers |
|---|---|---|---|
| 1 | `examples/semantic_orc/gum_sinkhorn_2x2_single_edge.sio` | `GUM_SINKHORN_2X2_PASS` | κ=−0.500322, σ=0.1938; dose-response: n_eff 30 → conf 612, gate **0**; n_eff 300 → conf 877, gate **1** |
| 2 | `stdlib/epistemic/knowledge_transcendental.sio` | `ALL PASS` (8/8) | ep_exp/ep_log/ep_logsumexp2; logsumexp variance matches FD-Jacobian |
| 3 | `examples/semantic_orc/epistemic_sinkhorn_orc.sio` | `EPISTEMIC_SINKHORN_PASS` | forward-AD epistemic Sinkhorn; Var(κ) matches FD to ratio **0.999997**; value diff 3.4e-7 |
| 4 | `examples/hyperbolic_semantic_networks/gum_sinkhorn_transition_sweep.sio` | `GUM_SINKHORN_SWEEP_PASS` | κ −0.5→−2.0, conf 726→849, gate fires λ=0.3; OU var 0.12→0.76, ac1 0.48→0.93 |

## Headline result (Stage 3)

The Sinkhorn fixed point solved natively on forward-mode AD dual numbers (each scalar carries its
gradient w.r.t. the measured marginals). The GUM variance of κ is then **exact** — matching the
finite-difference ground truth to **0.0003%**. No mainstream numerical stack expresses an OT solver
over an uncertainty-typed scalar without first rebuilding the epistemic number system; in Sounio the
epistemic number *is* the scalar type.

**External cross-tool check (POT / Python, not a Sounio self-comparison):** the same 2×2 bottleneck
edge gives POT exact κ = **−0.500000**, POT Sinkhorn(ε=0.05) κ = **−0.500201**, vs. Sounio forward-AD
κ = **−0.500322** — agreement within the entropic-regularization bias. This rules out a shared bug
between the two Sounio artifacts (which compare against each other) by anchoring to an independent
optimal-transport solver.

## Stage-1 certified dose-response (the false-alarm fix)

Same below-baseline curvature (κ=−0.5 < baseline 0):

| n_eff | confidence | gate fires? |
|------:|-----------:|:-----------:|
| 30 | 612 | **no** (uncertainty too high) |
| 300 | 877 | **yes** (drop certified) |

The confidence-gated geometric signal fires only when sampling certifies the drop — the gate behaves
consistently with its certification design (it is a deterministic function of κ, σ, threshold).
This *motivates* a route to the field's open false-alarm problem, but is **not** itself a
false-alarm-rate measurement: that requires a comparative trial against a competing detector with
repeated draws on real EMA data, which is not done here.

## Methodological finding

Naïve **scalar** variance propagation through the Sinkhorn u↔v fixed-point iteration is wrong —
it re-injects marginal variance each iteration and ignores u–v correlation, inflating Var(κ) by
**~249×** over 64 iterations. Carrying a **gradient vector** (forward-mode AD) recovers the exact
result, since differentiating a contraction's iterates converges to the implicit-function-theorem
derivative. *GUM-through-an-iterative-solver needs sensitivity tracking, not scalar variance.*

## Theory status (external math-review, xai/Grok 4.1, logged 2026-05-27)

- **Rigorous:** (a) CD(K,∞) ⇒ λ₁≥K and e^{−Kt} contraction; (d) forward-AD = IFT fixed-point derivative.
- **Heuristic (analogy, NOT identity):** (b) discrete Ollivier κ vs continuous CD(K,∞) curvature;
  (c) curvature-flattening ⇔ critical slowing down (two distinct operators).
- **Tightened:** (e) binomial over-estimates Var(κ) only when all ∂κ/∂pᵢ share sign.

The Sounio contribution rests on the rigorous (d). The clinical early-warning claim remains blocked
on real ESM data (Kossakowski 2017); the sweep is a pipeline + well-posed-comparison demonstration,
not a lead-time result.
