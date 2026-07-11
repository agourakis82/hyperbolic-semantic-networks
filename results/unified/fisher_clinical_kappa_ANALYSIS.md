# Multi-Subject Affect-Network Curvature — Clinical (Fisher2017) vs Non-Clinical

**Date:** 2026-05-27 · **Pipeline:** `code/analysis/fisher_clinical_kappa.py` (reuses the exact-OT κ
core from `kossakowski_geometric_csd.py`). **Data:** open `jmbh/EmotionTimeSeries` archive
(`data/external/emotion_timeseries/`, gitignored). One Ollivier-Ricci κ per subject (whole-series
affect network), bootstrap-stable; Mann-Whitney + rank-biserial; robustness sweep.

- **Clinical:** Fisher2017 — 40 MDD/GAD patients, ~128 beeps each.
- **Non-clinical:** Rowland2020 (n=125) + Bringmann2016 (n=95) → 218 subjects.

## Result: CONFOUND-DOMINATED — no clean clinical effect

The fixes the n=1 Pilot 3 lacked (218+40 subjects, group inference) revealed that **the
clinical-vs-non-clinical κ difference is not robustly estimable from these heterogeneous cohorts** —
the sign of the effect depends on an analytic choice more fundamental than any hyperparameter.

| comparison | clinical κ | non-clinical κ | effect (rank-biserial) | p | direction |
|---|---:|---:|---:|---:|---|
| **harmonized** 4-item {sad,anxious,angry,positive} (same items both groups) | 0.602 | 0.572 | −0.20 | .049 | clinical **higher** (less hyperbolic) |
| **native** items (16 vs 6–8 nodes) | 0.414 | 0.475 | +0.52 | <1e-4 | clinical **lower** (more hyperbolic) |

**Three reasons it is not a result:**

1. **Item-set sign flip.** Native vs harmonized give *opposite directions*. The strong native effect
   (rank-biserial up to **0.98** for the partial metric) is almost entirely a **node-count artifact**
   — Fisher has ~16 mood items, the comparison cohorts 6–8; more nodes systematically shifts κ. The
   harmonized control (identical 4 items) flips the sign and shrinks the effect ~5×.
2. **Density confound.** Even in the harmonized network, `corr(κ, graph-density) = +0.73` (clinical) /
   +0.80 (non-clinical) — the same trap as the static depression work (corr(κ,⟨k⟩)≈0.99). The small
   harmonized κ gap could be a density difference, not a curvature-specific one.
3. **Borderline significance + residual cohort confounds.** The "robust" harmonized effect has
   p-values clustered at the edge (.026–.054; the 6/8 "robust" count includes p=.049 cells and misses
   p=.054 cells). And harmonizing items removes the *item* confound but not the **protocol /
   population / country / sampling-rate** differences between Fisher and the Dutch/other cohorts.

**Hyperparameter robustness was real but irrelevant:** the harmonized clinical>non direction held in
6/8 (τ, ridge, beep-subsample) cells — but robustness to τ/ridge does not rescue a finding whose sign
flips with the item-set choice and that is density-confounded.

## Honest verdict

**No clean clinical-vs-non-clinical affect-network curvature effect survives.** This is the same
deflationary pattern the program has hit before (density confound in the severity ordering;
window-width artifact in Pilot 3's lead claim; the octonion/sedenion nulls): a multi-subject test,
done with the confound controls built in, shows the apparent effect is an artifact of methodological
choices (node count, density), not clinical status.

**Methodological takeaway (the actual contribution):** cross-dataset comparisons of network curvature
are dominated by node-count and density confounds; a *harmonized-item, density-controlled* design is
mandatory, and even then heterogeneous-cohort confounds remain. A valid clinical-vs-non-clinical κ
test needs **one dataset containing both groups with identical items and protocol** — not an
aggregation of separately-collected cohorts. (This is exactly what TRANS-ID + its healthy-control or
within-study design would provide; cf. `geometric_csd_multisubject_SCOPE.md`.)

The robust *language/method* contributions are unaffected (GUM-through-Sinkhorn, exact uncertainty
propagation; `gum_sinkhorn_RESULTS.md`). This clinical comparison is reported as **confound-dominated /
not established**, not as a positive finding.
