# Slide draft — "Is it curvature, or is it density?" (the credibility slide)

Build-ready content for HK / Yale. One slide + speaker notes. Drop into Keynote/PowerPoint/Beamer.

---

## SLIDE TITLE

**Is it curvature — or density in disguise?**
*A stress test our effect passes and four others fail*

## SLIDE BODY (the table is the slide)

Suggested layout: title top; the table center (4 rows, the last row highlighted/green, the others
greyed); the one-line takeaway in a bar across the bottom.

| Network substrate | Stratified density-distribution match | Curvature effect |
|---|---|:---:|
| Seizure EEG — pre-ictal (CHB-MIT) | matched | ✗ collapses (p = 0.88) |
| Mood-EMA intervention arms (Rowland) | matched | ✗ null |
| Clinical vs non-clinical affect nets (Fisher) | matched | ✗ artifact (node-count + density) |
| **depression-text co-occurrence — subclinical vs clinical** | **matched** | **✓ SURVIVES — 8/8 seeds, p < 1e-77** |

**Bottom bar (takeaway):**
> The control that dissolves curvature elsewhere *sharpens* our subclinical effect (κ-separation ×2.7).
> That is how you tell a geometric signal from a density statistic in disguise.

## SUPPORTING NUMBERS (small print / backup)

- Matched mean Ollivier-Ricci κ: **subclinical −0.174 ± 0.011** vs clinical −0.090 … −0.102.
- Edge-level control: per-edge exact-OT κ, matched on the endpoint-degree (local-density) *distribution*,
  not just its mean — the stricter form of density control.
- Full battery the effect survives: exact-OT · degree-preserving nulls · mean-density match ·
  6-cell (N×⟨k⟩) phase diagram (per-edge KS p<1e-80) · **stratified density-distribution match.**
- Confirmed at TWO operating points: N≈1000 (8/8 seeds, p<1e-77) and **N≈1500 — the abstract's point —
  (5/5 seeds, worst-case p=1.1e-221).** Numbers on this slide are safe to cite against the abstract.

## SPEAKER NOTES (≈45 s)

> "The first question anyone asks about a network-curvature biomarker is: isn't this just density?
> Sparser graphs are more hyperbolic, so a curvature difference can be a degree difference wearing a
> geometric costume. We took that seriously. We built the strictest control we could — matching the
> *distribution* of local density edge-by-edge across groups — and we ran it on four different
> substrates. On seizure EEG, on mood-sampling data, on clinical affect networks, the curvature effect
> collapses: it *was* density. On our subclinical-depression semantic networks, it survives in every
> resample at p below ten-to-the-minus-seventy-seven — and it actually gets *stronger* when we remove
> density, because density was masking it. So when we say subclinical semantic networks are the most
> hyperbolic, we mean it geometrically, not as a density artifact."

## PRESENTER GUARDRAILS (do not say on stage)

- ✗ "Curvature is independent of density." → ✓ "survives the density control" (the effect *is*
  density-sensitive; the claim is survival, not orthogonality).
- ✗ Monotonic 4-step severity gradient. → ✓ "subclinical vs clinical" (mild/mod/severe ordering is
  not robust; it trades places across resamples).
- ✗ Octonion / sedenion "second axis." → omit, or a single backup slide: "a non-associative second
  axis was tested and rejected — it re-encoded curvature (curvature-free control collapsed it)."

## OPTIONAL SECOND SLIDE — the method (forward-looking)

**Title:** *A biomarker that carries its own uncertainty*
- Exact-OT (Sinkhorn-LSE) curvature with measurement uncertainty propagated **through** the transport
  solve into κ (GUM-through-Sinkhorn) — verified exact vs finite-difference and vs POT.
- → a **confidence-gated** curvature: the warning fires only when the estimate is certified, directly
  addressing the false-alarm problem that dogs early-warning biomarkers.
- Implemented natively (Sounio), GPU-validated. "Point estimate → estimate + uncertainty budget."

---

*Sources in-repo:* `results/unified/stratified_density_match_depression_ANALYSIS.md`,
`…/chb01_preictal_curvature_ANALYSIS.md`, `…/rowland_within_kappa_ANALYSIS.md`,
`…/fisher_clinical_kappa_ANALYSIS.md`, `…/gum_sinkhorn_RESULTS.md`. Framing: `conference_framing_HK_Yale.md`.
