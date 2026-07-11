# Scope — Multi-Subject, Spontaneous-Transition Test of Geometric Critical Slowing Down

**Status:** pre-registration-style design scope (no data in hand yet). **Date:** 2026-05-27.
**Predecessors:** synthetic + language artifacts (`gum_sinkhorn_RESULTS.md`); single-case Pilot 3
(`kossakowski_geometric_csd_ANALYSIS.md`) — which produced a *robust descriptive* curvature dip but
**honest negatives** on "κ leads scalar EWS" (window-width artifact, 4/8) and "holds across metrics"
(partial-corr fails), and could not claim anticipation because the κ drop came *after* the known
medication taper.

## 1. Why this study (what it fixes)

Pilot 3's three fatal limitations are exactly what a multi-subject, spontaneous-transition design
removes:

| Pilot 3 limitation | Fix here |
|---|---|
| n = 1; lead-times are anecdotes | N ≈ 40+ subjects, ~12–25 documented transitions → lead-time becomes a *distribution* with group inference |
| Exogenous trigger (abrupt med switch) → κ drop not anticipatory | Transitions at *individually-variable, not schedule-locked* times → the anticipation question is well-posed |
| "κ leads scalar EWS" was a window-width artifact | Robustness sweep is **mandatory and pre-registered**, not post-hoc |

## 2. Data (the gating dependency — secure access FIRST)

**Primary target — TRANS-ID Tapering** (Wichers/Helmich group, Groningen). N=41 remitted recurrent-MDD
patients, 5×/day EMA, ~4 months, **21,180 observations**, with prospectively documented symptom
transitions/relapse. The restlessness-prodrome analysis showed transitions detectable ≥1 month before
core-symptom onset in ~67% of recurring cases — i.e. real, datable prodromal transitions.
- Protocol: TRANS-ID Tapering (BMJ Open / ResearchGate 365376466); site: https://www.transid.nl/?lang=en
- **ACCESS RESOLVED (2026-05-27): the raw EMA data is NOT openly downloadable — it is request-only.**
  - OSF project `osf.io/h75p9/` holds only the **study-protocol PDF + analysis-code folders** ("EWS",
    "sudden-gradual regression", "SPC restlessness") — **no raw dataset**. Related: `osf.io/a8572/`
    (project/questionnaire), `osf.io/zbwkp/` (protocol), `osf.io/ef2ku/` (analytical methods). Code +
    questionnaires only.
  - Data-availability statement (Smit et al. 2025, *Clin Psych Sci*; PMC10123048; N=56,
    ~30,404 completed questionnaires, median 542.5/participant): *"The data that support the findings
    of this study are available from the corresponding author upon reasonable request. The data are
    not publicly available due to privacy or ethical restrictions."*
  - **Route:** email the corresponding author **Arnout C. Smit** (and/or PI **Marieke Wichers**),
    **ICPE, UMCG / University of Groningen** (umcgresearch.org/w/icpe). Expect a **Data Use Agreement**
    under UMCG research-data-handling policy (researchcode.umcgresearch.org) + a reasonable-use/analysis
    plan; possibly ethics/DAC review. **Timeline: weeks-to-months, human-in-the-loop — not a download.**
  - **Implication for sequencing:** P0 is a slow administrative dependency. **Build P2 (per-subject
    pipeline) now on the OPEN data we already hold** — the Kossakowski 2017 single case (CC-BY,
    `osf.io/j4fg8`, already in `data/external/kossakowski_csd/`) is the open exemplar of this exact
    lineage — plus any openly-downloadable secondary cohort, so the code is validated and waiting when
    the TRANS-ID DUA clears. Do not block the build on the data request.

**Caveat carried forward (state in the paper):** TRANS-ID's taper is still a *gradual* perturbation,
so "spontaneous" is **relative** to Kossakowski's abrupt switch, not absolute. The taper-onset date is
known per subject → it becomes a **modeled covariate and the baseline to beat** (§5). A fully
trigger-free design (naturalistic relapse monitoring, no medication change) is rarer; secondary
candidates below approach it.

**Secondary / replication candidates** (heterogeneous; for robustness, not the primary test):
- PCT-while-tapering RCT secondary-analysis ESM cohort (remitted recurrent MDD + healthy controls;
  PMC10700372) — has non-relapsers as built-in negative controls.
- Cross-cultural EMA treatment-response cohort, N=300, 6×/day (OSF `ezpc3`) — larger, treatment not taper.
- `jmbh/EmotionTimeSeries` (7 open ESM emotion series) — small, mixed; sanity/replication only.
- At-risk-youth large-scale diary EWS study (Schreuder et al., PMC9475781) — transitions in youth.

## 3. Unit of analysis & transition definition (pre-registered, a priori)

- **Unit = a documented transition** (relapse / sustained symptom shift), not a subject. Subjects may
  contribute 0 (non-relapsers → controls) or ≥1 transition.
- **Transition onset = clinically/operationally defined a priori** (e.g., the dataset's own relapse
  criterion, or a sustained SCL/symptom crossing), **fixed before computing any κ**. (Pilot 3's
  post-hoc dep-midpoint onset is explicitly disallowed here.)
- **Per-subject baseline window** = the stable pre-prodromal stretch; **prodromal window** = the
  documented run-up.

## 4. Pipeline (reuse Pilot 3 machinery)

Per subject: z-standardize items → sliding-window affect network → exact-OT LLY-ORC κ(t) under the
three metrics (`code/analysis/kossakowski_geometric_csd.py` core: `kappa_one`, `lazy_measure`,
`mean_kappa_graph`, `poincare_metric`) → beep-bootstrap κ confidence per window → transition-locked
alignment (time relative to each subject's transition onset). Classical scalar EWS (variance, lag-1
autocorrelation of a negative-affect composite) computed on the **identical windows/beeps** (the
same-data comparison verified in Pilot 3).

## 5. Pre-registered hypotheses & the test that actually matters

- **H1 (descriptive, replication of Pilot 3):** κ (Pearson, hyperbolic) drops in the prodromal window
  vs. baseline — tested as a multilevel (subjects = random effect) pre/post contrast.
- **H2 (the real question — anticipation beyond the trigger):** the κ-based warning fires earlier than
  **(a)** the scalar EWS *and* **(b)** the trivial "taper-onset" predictor. **H2b is the crux:** does
  geometry beat simply knowing the taper started? If κ's lead over the transition does not exceed the
  taper-onset baseline, the "anticipatory" claim fails again — now with N to say so.
- **H3 (specificity):** non-relapsers (controls) do **not** show the κ dip → the signal is transition-
  specific, not generic drift.

Inference: multilevel survival / mixed-effects model with transition as the event; lead-time as a
per-transition outcome with subject random effects; report the lead-time *distribution*, not a mean.

## 6. MANDATORY controls (every lesson the program has paid for)

1. **Window-width robustness sweep, pre-registered** — the control that killed Pilot 3's headline.
   Grid (≥ WIN∈{14,21,28}, τ, ridge, α); the headline holds only if it survives a pre-declared
   fraction of cells **and** the lead distribution stays positive across them.
2. **Cross-metric** — partial / Pearson / hyperbolic; pre-declare the primary metric *or* require
   concordance. (Partial-corr failed in Pilot 3 — decide its status a priori.)
3. **Same-window same-data** κ vs scalar-EWS comparison (no data-pooling asymmetry).
4. **Density control** — report `corr(κ, ⟨k⟩)` per window; density-match or covary it out
   (the corr≈0.99 trap from the static depression work).
5. **Taper-onset covariate (H2b)** — the exogenous trigger modeled explicitly, not ignored.
6. **Permutation / label-shuffle null** — shuffle transition onsets within subject; **non-relapser
   controls** as the between-subject null.
7. **Multiple-comparison / garden-of-forking-paths** discipline — full pre-registration of the grid,
   metrics, onset rule, and the ≥k/n robustness threshold *before* touching the prodromal windows.

## 7. The Sounio / epistemic angle (honest placement)

The per-subject, per-window κ uncertainty is quantified by **beep-bootstrap** (the honest real-data
engine; Pilot 3). The **GUM-through-Sinkhorn** epistemic-Sinkhorn (validated to match
finite-difference/POT on the 2×2 case) is the *native-language realization* of the same "propagate
measurement uncertainty through the OT solve" principle and supplies the **confidence-gated warning**
type — useful as the deployment-facing certified gate, **not** as the inferential engine for the
study. Do not overclaim it as the source of the statistics.

## 8. Power (rough, to refine once data/codebook in hand)

N=41, ~50% recurrence ⇒ ~20 transitions + ~20 control subjects. A within-subject pre/post κ shift of
~1 SD (Pilot 3 saw 4–8 bootstrap-σ in the one case) is detectable; the *lead-over-scalar-EWS*
distribution is the harder, lower-powered test — likely needs the secondary cohorts pooled. Treat
TRANS-ID alone as adequately powered for H1/H3, **underpowered-but-indicative for H2**, and
pre-register pooling with the secondary cohorts for H2.

## 9. Three honest outcomes (named before running)

1. **Real anticipatory geometric signal:** κ dip is transition-specific (H3), leads scalar EWS
   robustly across the sweep (H2a), **and** beats the taper-onset baseline (H2b) → a genuine,
   multi-subject, trigger-controlled result. The strong claim Pilot 3 could not make.
2. **Descriptive-only:** H1/H3 hold (κ marks destabilization, transition-specifically) but H2 fails
   (no lead beyond scalar EWS or beyond knowing the taper) → curvature is a *correlate* of
   reorganization, not an earlier detector. The likely Pilot-3-consistent outcome.
3. **Null:** κ dip is not transition-specific or not robust → honest negative, retire the clinical
   thread (octonion/sedenion-null precedent).

## 10. Phased plan & deliverables

- **P0 — Data access (BLOCKER):** locate/secure TRANS-ID (+ ≥1 secondary). Get codebook, transition
  labels, taper-onset dates. Nothing downstream proceeds without this.
- **P1 — Pre-registration:** freeze §3/§5/§6 (onset rule, metric, sweep grid, thresholds, nulls) on OSF
  *before* analysis. This is the integrity-critical step.
- **P2 — Per-subject pipeline:** generalize the Pilot 3 code to a per-subject loop + transition-locked
  alignment + the mandatory sweep, on the new schema.
- **P3 — Multilevel inference + nulls + controls.**
- **P4 — Write-up:** result *or* honest negative, with the full sweep table (the Pilot 3 standard).

**Critical reuse:** `code/analysis/kossakowski_{geometric_csd,robustness_sweep}.py` (κ core, sweep,
bootstrap, alignment scaffolding). **New:** per-subject driver + multilevel model + OSF pre-registration.

## 11. Honesty contract

Onset rule, metrics, sweep grid, and robustness threshold pre-registered before prodromal data is
touched. H2b (beat the taper-onset baseline) is the load-bearing test — geometry must beat *knowing
the trigger fired*, or the anticipatory claim is not made. "Spontaneous" is stated as *relative* given
the taper. Outcome (2) or (3) is reported as fully as outcome (1), per program precedent.
