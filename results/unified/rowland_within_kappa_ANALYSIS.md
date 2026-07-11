# Within-Dataset Affect-Network Curvature — Rowland2020 (the confound-clean test)

**Date:** 2026-05-27 · `code/analysis/rowland_within_kappa.py` · reuses the exact-OT κ core.
**Data:** Rowland & Wenzel (2020), open `jmbh/EmotionTimeSeries`. 125 subjects, between-subject arms
group 1 (n=64) / group 2 (n=61), 40 days × 6 beeps/day, **8 mood items, identical for both arms**.

This is the design Fisher-vs-non-clinical could not be: ONE dataset, ONE protocol, SAME items, SAME
node count, density matched (0.89 both arms). So node-count and cross-cohort confounds are gone; only
group (and time) vary.

## Result: HONEST NEGATIVE — no between-arm and no intervention-induced κ effect

**Test A — between-arm per-subject κ:** no difference.

| metric | med κ g1 | med κ g2 | rank-biserial | p | sweep cells sig |
|--------|---------:|---------:|--------------:|--:|:---:|
| partial | 0.295 | 0.288 | −0.03 | .78 | — |
| pearson | 0.469 | 0.472 | −0.05 | .60 | **0/8** |
| hyperbolic | 0.429 | 0.432 | −0.07 | .52 | — |

Density identical between arms (0.89/0.89); `corr(κ, density)=0.77` (the familiar confound, but here
it can't drive a group difference because the groups don't differ in density). Density-residualized
between-arm p = .083 — also null.

**Test B — temporal Δκ (κ days 21–40 − κ days 1–20), by arm** (manipulated-transition analog): null.

| metric | med Δκ g1 | med Δκ g2 | rank-biserial | p |
|--------|----------:|----------:|--------------:|--:|
| partial | −0.013 | +0.004 | +0.18 | .084 |
| pearson | +0.008 | −0.011 | −0.18 | .096 |
| hyperbolic | −0.000 | −0.017 | −0.20 | **.062** |

No arm shows a robust κ shift over the study, and the arms do not differ (all p > .05; the hyperbolic
hint at .062 is not significant and not robust). The cleanest open analog to "does curvature track an
induced change in the affect network" is **null**.

## Convergent conclusion (with Fisher)

- **Fisher cross-dataset** (`fisher_clinical_kappa_ANALYSIS.md`): apparent clinical κ effect was
  **confound-dominated** — the strong native-item effect was a node-count artifact (sign flipped under
  item harmonization; density-confounded).
- **Rowland within-dataset** (here): with all those confounds removed, the between-group and
  intervention-induced κ effects are **null**.

Together: **affect-network Ollivier-Ricci curvature does not carry a robust group or
intervention-tracking signal once node-count, cohort, and density confounds are controlled — on the
open data we can access.** This is the same deflationary pattern as the density confound in the static
severity ordering, the window-width artifact in Pilot 3, and the octonion/sedenion nulls.

## Scope of the negative (do not over-read)

This is a null in a **non-clinical mindfulness RCT** (both arms likely fairly healthy; arm contrasts
may be genuinely small) — it does **not** disprove a clinical-vs-healthy curvature difference. It
shows that the *confound-clean designs available in open data* yield no signal. A real clinical-vs-
healthy κ test still requires **one dataset containing both clinical and control groups with identical
items and protocol** (TRANS-ID-class; `geometric_csd_multisubject_SCOPE.md`). The open-data branch is
closed with a clean negative; the controlled-cohort question remains open and is the only path that
could still turn positive.

The language/method contributions (GUM-through-Sinkhorn, exact uncertainty propagation through the OT
solve; `gum_sinkhorn_RESULTS.md`) are independent of this and stand.
