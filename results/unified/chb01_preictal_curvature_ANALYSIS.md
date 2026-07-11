# Pre-ictal EEG Network Curvature — CHB-MIT chb01 (the loop-closing transition test)

**Date:** 2026-05-27 · `code/analysis/chb01_preictal_curvature.py` · reuses the exact-OT κ core.
**Data:** PhysioNet CHB-MIT chb01 (23-ch bipolar 10-20, 256 Hz). Interictal baseline: chb01_01, _02
(seizure-free). Pre-ictal: 30-min run-up before 4 seizures (chb01_03 @2996 s, _04 @1467, _16 @1015,
_18 @1720). Per 30-s window: |Pearson| connectivity network → exact-OT Ollivier-Ricci mean κ.

This was the substrate chosen to fix every Kossakowski flaw at once: a **spontaneous, second-marked,
within-patient** critical transition with dense neural data and a fixed montage. It does fix those —
and the result is a **clean, decisive density artifact.**

## Result: DENSITY ARTIFACT (no curvature-specific pre-ictal signal)

| test | result | reading |
|------|--------|---------|
| raw pre-ictal vs interictal κ | med 0.226 vs 0.183, rank-biserial −0.46, **p<1e-4** | large apparent shift |
| onset trend (κ slope toward seizure) | **2/4** seizures negative-sloped | inconsistent — a level shift, not a monotonic critical-slowing run-up |
| corr(κ, density), interictal | **+0.76** | strongly density-entangled |
| density-residualized (ANCOVA) | **p=0.10** | shift not significant after linear density adjustment |
| **density-stratified-matched (decisive)** | **median p=0.88, κ-diff −0.0005** | **shift VANISHES when density distributions are equated** |
| band-matched (weak control) | p<1e-4 | misleading — clips range but doesn't equate distributions |

**Interpretation.** The raw pre-ictal κ increase is real but is **entirely explained by the well-known
pre-ictal rise in connectivity density (synchronization)**. At matched density there is *no* curvature-
specific difference (κ-diff ≈ 0, p=0.88). The band-matched test that looked significant was fooled by
residual within-band density-distribution differences; the stratified match (equates the distributions)
and the residualized ANCOVA agree: nothing survives. There is also no consistent slowing-down trend
toward onset (2/4).

## The meta-finding (across the whole empirical arc)

This is the **fourth independent substrate** on which an apparent Ollivier-Ricci curvature effect
dissolved into network density once properly controlled:

1. Depression severity ordering — `corr(κ,⟨k⟩)=0.99`, density confound (`depression_nulls_exact_ot_ANALYSIS.md`).
2. Fisher clinical vs non-clinical — node-count + density artifact (`fisher_clinical_kappa_ANALYSIS.md`).
3. Rowland within-dataset arms — null at matched density (`rowland_within_kappa_ANALYSIS.md`).
4. **chb01 pre-ictal EEG — density artifact at matched density (here).**

**Across semantic word-association networks, EMA mood networks, intervention arms, and seizure EEG,
every apparent network-curvature group/state effect is explained by network density once density is
properly controlled.** That convergence — on four very different data types — is itself the robust
empirical result of this program: *graph Ollivier-Ricci curvature, as a group/state biomarker on these
networks, is a density statistic in disguise.* (Consistent with the static-network corr(κ,⟨k⟩)≈0.99 and
the octonion/sedenion nulls — the discipline kept catching the same confound wearing different costumes.)

## Scope / honesty

n=1 patient, one connectivity measure (broadband |Pearson| on bipolar montage), one window length.
Band-limited connectivity (e.g. high-γ, where pre-ictal effects concentrate) and more patients could
differ — but the *density confound* would still need the stratified control, which is the point. This
does not claim seizures lack pre-ictal dynamics (they have well-documented synchronization); it claims
**curvature adds nothing beyond density** here.

The verified **language/method** contribution is untouched and is what stands: GUM-through-Sinkhorn —
exact uncertainty propagation through the optimal-transport solve (`gum_sinkhorn_RESULTS.md`). The
*neuroscience/biomarker* claims are, across all substrates, **not established** — density-confounded.
