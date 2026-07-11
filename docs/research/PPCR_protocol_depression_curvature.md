# Pre-Registration Protocol — Network Curvature of Depression-Severity Text
### Reconstructed under PPCR (Principles and Practice of Clinical Research) methodology

**Status:** PROTOCOL — written and frozen *before* the rebuilt-data analysis is run (the PPCR
discipline: protocol precedes data). **Version:** 1.0 · **Date:** 2026-05-27 ·
**Author:** D. C. Agourakis. **Supersedes** the sweep-tuned, mislabeled, single-draw pipeline that the
2026-05-27 provenance audit found defective (`repo_provenance_audit_2026-05-27.md`).

> *Why a protocol at all.* The original analysis failed PPCR on five counts: (1) no a-priori hypothesis;
> (2) construction parameters chosen by a "clustering sweet-spot" sweep = garden-of-forking-paths;
> (3) a single random sample (`random_state=42`); (4) the density confounder uncontrolled; (5) the data
> mislabeled ("SWOW/semantic" for social-media co-occurrence). This protocol fixes all five *before*
> looking at any rebuilt result.

---

## 1. Background & rationale

Ollivier–Ricci curvature (ORC) characterises whether a network's local geometry is hyperbolic (κ<0),
Euclidean (κ≈0), or spherical (κ>0). A prior exploratory analysis suggested that co-occurrence networks
built from depression-severity-labeled text differ in curvature by severity (subclinical most
hyperbolic). That analysis was confound-dominated and non-reproducible. Here we test the same question
*de novo* on the real, re-acquired HelaDepDet corpus, with confounding controlled and the analysis plan
fixed in advance.

**Object, stated honestly:** these are **word co-occurrence networks of depression-severity-labeled
social-media text** — in the computational-psychiatry / speech-graph tradition (Mota 2012; Bedi 2015;
Kenett 2018). They are **not** SWOW free-association networks and not semantic-memory maps. No claim is
made about any individual's brain or diagnosis.

## 2. Research question (FINER + PICOT)

**FINER:** *Feasible* (public corpus, exact-OT ORC tractable at the chosen scale); *Interesting* &
*Relevant* (geometric biomarkers in computational psychiatry); *Novel* (curvature of severity-stratified
text networks, with a confound battery rarely applied); *Ethical* (public, de-identified, aggregate).

**PICOT:**
- **P** (population/unit): co-occurrence networks built from samples of depression-severity-labeled
  posts (HelaDepDet, N=41,873; strata minimum/mild/moderate/severe).
- **I/E** (exposure): severity stratum (ordinal: minimum < mild < moderate < severe).
- **C** (comparison): between strata, primarily **subclinical (minimum) vs the pooled clinical strata**.
- **O** (outcome): mean Ollivier–Ricci curvature κ of the co-occurrence network (per-edge κ, exact OT).
- **T** (time): cross-sectional (no longitudinal component).

## 3. Objectives

- **Primary:** estimate and test the difference in network ORC κ between the subclinical (minimum)
  stratum and the pooled clinical strata, **after controlling for network density** (the known confounder).
- **Secondary:** (a) the ordinal severity trend in κ; (b) robustness to network-construction parameters;
  (c) reproducibility across independent post-samples.

## 4. Hypotheses (frozen a priori)

- **Primary endpoint:** sign and significance of the minimum-vs-pooled-clinical κ difference under the
  **stratified density-distribution-matched** comparison (defined in §9).
- **H0 (primary):** at matched density, median κ of minimum = median κ of pooled clinical strata.
- **H1 (primary, two-sided):** they differ. *A-priori expected direction* (from the exploratory signal
  and the fragility framing): minimum more negative (more hyperbolic) — **tested two-sided, not assumed.**
- **Secondary H0:** κ does not vary monotonically across the four ordinal strata.

## 5. Study design

Observational, cross-sectional, network-level comparison. **Unit of analysis = a constructed network**
(per stratum, per independent post-sample). Multiple independent samples (seeds) provide the replication
distribution; per-edge κ within a network provides the matched-comparison distribution.

## 6. Population, sampling, inclusion/exclusion

- **Sampling frame:** the full HelaDepDet corpus (provenance: `data/external/.../PROVENANCE.md`,
  MD5 63b3ab81…).
- **Sampling:** stratified random sample of **n = 250 posts per stratum** (primary, for comparability
  with the exploratory baseline), drawn under **K = 10 independent seeds** (replacing the single
  `random_state=42`). Robustness arm at n ∈ {250, 500} (§ SAP sensitivity).
- **Inclusion:** posts with non-empty text and a valid stratum label.
- **Exclusion:** none beyond the above (no outcome-dependent exclusion — guards selection bias).

## 7. Variables

- **Exposure:** severity stratum (ordinal).
- **Outcome:** mean ORC κ (per-edge, exact optimal transport, lazy random walk α=0.5, edge distance=1).
- **Pre-specified confounders / nuisance variables:**
  1. **Network density** (mean endpoint degree per edge; whole-network ⟨k⟩) — the *primary confounder*
     (prior work: corr(κ,⟨k⟩) ≈ 0.8–0.99).
  2. Network size N (nodes).
  3. Text volume per stratum (total tokens) and vocabulary richness — upstream drivers of density.
- These are **measured and reported**; the primary analysis **controls density by stratified
  distribution matching** (§9); N is equalized by subsampling to a common node count.

## 8. Network construction — PRE-SPECIFIED (no sweep)

Fixed in advance, **justified by convention, not chosen to hit a clustering target** (the sweep is
abandoned):
- Tokenisation: lowercase words of length ≥ 5 (long-word convention; reduces stopword dominance).
- Co-occurrence within a sliding **window = 5** tokens; undirected edge, weight = co-occurrence count.
- Largest connected component; subsample to a common **N_node = 1000** per network for size-comparability.
- **Blinding to outcome:** construction parameters are identical across strata and are NOT re-tuned per
  stratum or to optimise any κ contrast. The severity label is used ONLY at the comparison step (§9).
- **Pre-specified robustness grid** (sensitivity, not primary): window ∈ {3,5,10}, min-word-len ∈ {3,5}.
  The primary claim must survive this grid, not just the single configuration.

## 9. Statistical Analysis Plan (SAP) — frozen a priori

- **Primary analysis:** for each seed, compute per-edge κ + per-edge density covariate (mean endpoint
  degree) for all four strata at common N_node; pool edges; bin density into deciles; **match equal edge
  counts per stratum per bin** (equate the density *distribution*, not just its mean); compare minimum vs
  pooled-clinical matched-edge κ by **Mann–Whitney U** (two-sided), with **rank-biserial** effect size.
  Aggregate across K=10 seeds: report median/worst-case p and the matched κ (mean ± SD across seeds).
- **Decision rule (primary):** reject H0 iff minimum is the most-hyperbolic stratum in **≥ 8/10 seeds**
  AND the worst-case matched-edge p < 0.05 (Bonferroni-safe given the single primary contrast).
- **Secondary:** ordinal trend (Jonckheere–Terpstra or matched-mean rank across the 4 strata) — reported
  but **not** required for the primary claim (the exploratory 4-step gradient was non-robust; we
  pre-specify that only the subclinical-vs-clinical contrast is confirmatory).
- **Sensitivity / robustness (pre-specified):** (i) construction grid §8; (ii) n ∈ {250,500};
  (iii) density-residualised (ANCOVA) cross-check of the matched result.
- **Multiplicity:** one primary contrast → no inflation; secondary/sensitivity reported as exploratory.
- **Missing data:** none expected (text + label complete); empty-after-tokenisation networks excluded
  before analysis, logged.

## 10. Sample size / power

- The exploratory matched contrast gave rank-biserial ≈ 0.46–0.48 (large) at thousands of matched edges
  per seed; matched edge counts here (~10³/seed) yield power > 0.99 to detect rank-biserial ≥ 0.2 at
  α=0.05. The **binding** sample-size choice is therefore the **number of seeds (K=10)** for the
  replication decision rule (≥8/10), not within-network power.
- Minimum detectable effect (MDE) at the network level is governed by between-seed variability of matched
  κ (exploratory SD ≈ 0.01); K=10 resolves a between-stratum gap of ~0.02 (the observed gap was ~0.08).

## 11. Bias & validity

- **Selection bias:** random stratified sampling, no outcome-dependent exclusion, K seeds.
- **Measurement bias:** identical, outcome-blinded construction across strata; exact OT (no
  regularisation bias); per-edge κ.
- **Confounding:** density controlled by stratified distribution matching (primary) + ANCOVA
  (sensitivity); size equalised; text-volume/vocabulary reported.
- **Internal validity:** the confound battery (matching + residualisation + robustness grid) is the core.
- **External validity (limits, stated):** one aggregated social-media corpus (Twitter/Reddit, English);
  labels are post-level BDI-3/DSAS annotations, **not** clinical diagnoses of individuals; co-occurrence
  text networks ≠ semantic-memory networks ≠ brain networks. No generalisation to patients is claimed.

## 12. Reproducibility

Documented provenance + MD5 (§ PROVENANCE.md); fixed seed list; deterministic pipeline; code committed;
results JSON with per-seed values; STROBE-style reporting. Anyone with the public corpus reproduces it.

## 13. Pre-registered outcomes (all reported equally — honesty contract)

1. **Confirmatory positive:** primary decision rule met (minimum most hyperbolic ≥8/10, p<.05 matched)
   → a real, density-controlled, honestly-labeled result suitable for HK/Yale/WCP, framed as
   *depression-text co-occurrence network geometry*.
2. **Null:** decision rule not met → the exploratory signal does not survive proper rebuild; reported as
   an honest negative (the audit's deflationary pattern), conferences reframed accordingly.
3. **Partial:** survives at primary config but not the robustness grid → reported as construction-dependent.

**The octonion/FEP/"SWOW-semantic"/4-step-gradient claims are NOT part of this protocol** and are not
revived. The FEP fabrication is quarantined, not rebuilt (no real FEP cohort exists in-repo).

## 14. Ethics

Public, de-identified, aggregate corpus; post-level annotations; no individual-level or diagnostic
claims; CC-respecting use with citation. IRB not applicable (public secondary data, no human contact).

## 15. Reporting

STROBE (observational) checklist for the write-up; figures show the confound battery (raw vs
density-matched) explicitly; limitations §11 stated prominently.

---

*Frozen 2026-05-27 before execution. Execution: `code/analysis/ppcr_depression_curvature_rebuild.py`,
results in `results/unified/ppcr_depression_curvature_rebuild.json` + `_ANALYSIS.md`.*
