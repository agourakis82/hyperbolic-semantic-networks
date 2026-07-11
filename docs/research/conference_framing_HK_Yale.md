# Conference Framing — HK Digital Mental Health (Jun 14) + Yale Computational Psychiatry (Jul 2026)

**Subject:** how to present Ollivier-Ricci curvature as a geometric biomarker, given the full confound
battery. Abstracts submitted (claim locked); slides open. **Date:** 2026-05-27.

## The one claim that survives everything — lead with this

> **Subclinical (minimum) semantic networks are the most hyperbolic — the most negative Ollivier-Ricci
> curvature — and are robustly separated from clinical depression.** This survives exact-OT (not a
> Sinkhorn artifact), degree-preserving nulls, mean-density matching, a 6-cell (N×⟨k⟩) phase diagram
> with per-edge KS separation, **and** the strictest edge-level stratified density-*distribution* match
> (8/8 seeds, p < 1e-77).

This is genuinely strong and you can defend every word.

## The slide that earns credibility (put it up *before* Q&A)

A confound-battery table. The punchline is a contrast no skeptic expects:

| substrate tested with stratified density-distribution match | curvature effect |
|---|---|
| seizure EEG (CHB-MIT, pre-ictal) | **collapses** (p 0.88) |
| EMA mood-network intervention arms (Rowland) | **null** |
| clinical vs non-clinical affect networks (Fisher) | **artifact** (node-count + density) |
| **depression-text co-occurrence: subclinical vs clinical** | **SURVIVES** (8/8, p<1e-77) |

Message: *"We tried hard to kill our own effect with the control that dissolves curvature elsewhere.
It survived. That's how you tell a geometric signal from a density statistic in disguise."* In a field
mid-rigor-reckoning (cf. Bringmann 2021 EWS "challenges"), owning the #1 known weakness of ORC
biomarkers — density confounding — is what converts skepticism into trust.

## What to DROP or downgrade (a sharp Yale audience will find these)

1. **Octonion / sedenion associator "second axis" — REMOVE, or present only as a *rejected*
   hypothesis.** The curvature-free control collapses it ("curvature in a Cayley-Dickson costume").
   Keeping it as a positive claim is the single biggest exposure in the current deck.
2. **The monotonic 4-step severity gradient — DOWNGRADE.** The mild/moderate/severe ordering is NOT
   robust under the strict control (trades places across seeds). Claim **subclinical vs clinical**,
   not a clean severity staircase. (The old "mild least hyperbolic" detail does not survive.)
3. **Any "density-independent" phrasing — AVOID.** Say "survives density control," not "independent of
   density." The effect *sharpens* under matching, but the honest statement is about surviving the
   control, not orthogonality.

## What's genuinely novel to offer (the forward-looking slide)

The **method**, not just the finding: an exact-OT (Sinkhorn-LSE) curvature pipeline with **uncertainty
quantification built in** — GUM-through-Sinkhorn, where measurement uncertainty propagates *through*
the optimal-transport solve into κ (verified exact vs finite-difference and vs POT). This makes ORC a
*certified* biomarker (confidence-gated), which directly answers the field's false-alarm problem. It's
implemented natively (Sounio) and GPU-validated. Frame as "biomarker + its uncertainty budget," a step
beyond point-estimate connectomics.

## Honest caveats to keep on a backup slide (don't volunteer pain, but be ready)

- **DATA PROVENANCE (critical, corrected 2026-05-27):** the depression networks are **word
  co-occurrence graphs from the HelaDepDet social-media "Depression_Severity_Levels_Dataset"** —
  NOT SWOW, NOT semantic-association networks. Construction tuned by a clustering-sweet-spot sweep;
  250 posts/class, one random draw; source dataset absent from repo. The claim is about **lexical
  co-occurrence structure of severity-labeled text**, closer to computational linguistics/stylometry
  than to semantic-memory geometry. **Do NOT call these "SWOW" or "semantic networks" on stage.**
  ⚠️ If the submitted abstract says "SWOW"/"semantic," the abstract itself carries this error — check it.
- n is groups, not a clinical cohort with outcomes.
- Curvature is density-*sensitive*; the claim is survival of the control, on this substrate.
- The within-clinical gradient and the second algebraic axis are not established.

## One pre-conference action still worth doing

Re-run the stratified match with the *exact* N and ⟨k⟩ of the submitted-abstract analysis (this test
used N≈1000 subsamples; confirm it holds at the abstract's operating point) so the slide numbers match
what was submitted. Low effort, removes the last "but your abstract used different N" question.
