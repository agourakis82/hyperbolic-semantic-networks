# Pilot 3 — Geometric Critical Slowing Down on REAL ESM data (Kossakowski 2017)

**Date:** 2026-05-27 · **Pipeline:** `code/analysis/kossakowski_geometric_csd.py` ·
**Data:** Kossakowski et al. 2017 (doi:10.5334/jopd.29), `data/external/kossakowski_csd/`.

**Design:** single MDD patient, 1,473 usable momentary measurements over 239 days, double-blind
medication tapering. 12 mood items → time-varying affect network; 28-day sliding window, 4-day step
(54 windows). Phases: 1 baseline, 2 pre-reduction, **3 gradual dose reduction (the perturbation)**,
4 post-reduction, 5 follow-up. Outcome = weekly SCL-90 `dep` score.

**Pre-registered (user decision):** compute κ(t) under three edge metrics — partial correlation
(ridge precision), Pearson, hyperbolic-embedding (Poincaré geodesic) — and require the headline to
**hold across all three**. Uncertainty = beep-bootstrap (B=120) per window.

## Result

The depressive transition (sustained `dep` above the baseline→peak midpoint, 1.76) onsets **day 142**
(baseline dep 1.135 → plateau ~2.0–2.4 in phases 4–5).

| signal | baseline | first signal day | lead vs transition (d142) | bootstrap sd |
|--------|---------:|-----------------:|--------------------------:|-------------:|
| **κ hyperbolic** (drop) | 0.422 | **58** | **+84 d** | ~0.022 |
| **κ pearson** (drop) | 0.460 | **66** | **+76 d** | ~0.013 |
| classical lag-1 autocorr (rise) | — | 90 | +52 d | — |
| classical variance (rise) | — | 122 | +20 d | — |
| **κ partial** (drop) | 0.202 | **none** | — | ~0.026 |

**What happened to κ:** Pearson and hyperbolic curvature sat at ~0.45 / ~0.42 in baseline, **dropped
to a minimum (0.37 / 0.30) during the phase-3 dose-reduction window (days 58–118)**, then **recovered
to ≥ baseline in phase 5** — even though `dep` stayed high (~2.0). The drop is 4–8 bootstrap-σ, not
noise. So curvature marks the **destabilization window**, not the depression *level* — consistent
with early-warning-signal theory (EWS flag the transition, not the post-transition state).

**On this single case, the curvature drop preceded both the depressive plateau (~76–84 days) and the
classical variance/autocorrelation EWS (~24–56 days).** The κ and scalar-EWS signals are computed on
the **identical 28-day windows and the identical beeps** (`rolling_ews(rows, idx_by_window)` uses the
same `idx` as κ), so the lead is not a window-size/data-pooling artifact between the two estimators.

**Reframe (important — this is NOT "κ predicted the transition").** The dose taper *began* on day ~42
(phase 3 start, 24 Sep). The κ minimum is days 58–66 — i.e. κ fires **~16–24 days *after* the known
intervention started**. So the honest statement is: **κ tracked the medication-induced destabilization
earlier than the scalar EWS did (on the same windows), and well before that destabilization reached the
depressive plateau** — *not* that κ anticipated an endogenous transition with no known trigger. An
oracle aware of the taper schedule would have flagged instability at day 42 with no geometry at all.
Curvature responding to dynamical reorganization (not just to outcome) is the interesting part; the
"early-warning-signal" framing the field uses does not cleanly apply to a known-perturbation design.

## Caveats — why this is hypothesis-generating, not a result (read in full)

1. **n = 1.** A single patient. Every "lead time" is one observation, not a statistic. No inference
   beyond this individual is licensed. This is a case study on the canonical CSD dataset.
2. **The pre-registered cross-metric criterion PARTIALLY FAILS.** Partial-correlation κ shows **no**
   drop (signal = none; noisy at 0.15–0.27). The headline holds for **2 of 3** metrics (Pearson,
   hyperbolic), not all three. Honest status: metric-dependent.
3. **Confound with the exogenous perturbation.** The κ drop (days 58–66) falls inside phase 3, after
   the dose reduction began (~day 46). The geometric signal therefore **coincides with a known
   external trigger** — it cannot be cleanly called *anticipatory of an endogenous transition*. The
   "lead" over the dep-plateau partly reflects that the trigger precedes its own downstream effect.
4. **κ tracks destabilization, not severity.** κ recovers in phase 5 while depression persists, so it
   is not a depression-level readout — interpret it as a reorganization/instability marker.
5. **Onset definition is a choice.** Using the baseline→peak midpoint (day 142); a different
   threshold shifts the absolute leads (the *ordering* κ < scalar-EWS < plateau is more robust than
   the day counts).
6. **Modeling choices not yet swept:** window width (28 d), α (0.5), ridge (0.2), τ (0.10) are fixed;
   robustness to these is untested. Partial-correlation used ridge-precision (no GLASSO; sklearn
   absent).

## Robustness sweep (P3c) — the lead-over-scalar-EWS headline does NOT survive

`code/analysis/kossakowski_robustness_sweep.py`, 2×2×2 grid (WIN_DAYS∈{21,28} × τ∈{0.05,0.10} ×
ridge∈{0.1,0.2}). **Pre-registered:** headline = "both κ_pearson and κ_hyperbolic signal earlier than
the earliest scalar EWS" must hold ≥6/8 cells.

**Result: holds in 4/8 → NOT ROBUST (honest negative on the lead claim).**

| WIN_DAYS | cells | what happens |
|---------:|-------|--------------|
| 28 | 4/4 hold | scalar variance EWS fires late (day 122) → κ (58–66) leads |
| 21 | 0/4 hold | scalar **variance EWS fires early (day 46)** → κ (66–70) does **not** lead |

The "κ beats classical CSD indicators" claim is a **window-width artifact**: at 21-day windows the
variance indicator fires as early as the curvature dip. We therefore **do not claim κ leads the
scalar EWS.**

**What IS robust (8/8 cells):** the κ dip itself — both Pearson and hyperbolic κ drop and signal
during phase 3 (days 58–70) in every cell. The *existence and timing of the curvature drop during
destabilization* is stable; only its *superiority over scalar EWS* is not.

## Honest verdict

On the canonical single-case CSD dataset, network **Ollivier–Ricci curvature (Pearson + hyperbolic
metrics) reliably dropped during the dose-reduction destabilization** (robust across all 8
hyperparameter cells) — directionally consistent with the program's hypothesis and the static finding
(subclinical = most negative κ). **But the stronger claims do NOT survive:**

- κ **does not** robustly *lead* the classical scalar EWS — that holds only at 28-day windows (4/8),
  failing the pre-registered ≥6/8 (P3c). **Claim withdrawn.**
- The **partial-correlation metric shows no signal** — the cross-metric pre-registration is **not
  met** (2/3).
- The κ drop is **post-perturbation** (~16–24 days after the taper began), so it is **not
  anticipatory** of an endogenous transition.
- **n = 1.**

**Net:** a robust *descriptive* observation (curvature dips during medication-induced
destabilization), but an **honest negative** on the two claims that would have made it a result —
"κ leads scalar EWS" and "holds across all metrics." Like the octonion-associator and
sedenion-annihilation nulls before it, the strong version is reported as not-established. It
motivates a multi-subject test with spontaneous (un-triggered) transitions; it does **not** establish
a clinical early-warning signal, nor that curvature beats classical CSD.

This is the empirical complement to the *language* contribution (GUM-through-Sinkhorn, exact
uncertainty propagation through the OT solve, `results/unified/gum_sinkhorn_RESULTS.md`): here the
uncertainty is quantified by beep-bootstrap, the honest real-data analog.
