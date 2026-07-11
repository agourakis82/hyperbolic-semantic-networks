# Pre-Registration Protocol — Multi-Subject KEC of ZuCo Reading-EEG
### + the Small-Worldness text↔brain bridge · under PPCR

**Status:** PROTOCOL — frozen *before* the multi-subject analysis (PPCR: protocol precedes data).
**Date:** 2026-05-27 · **Author:** D. C. Agourakis. Extends the single-subject Lane-B closure
(`results/unified/zuco_kec.json`) and the certified Sounio KEC instrument
(`kec_spectral.sio` / `kec_epistemic_spectral.sio`).

## 1. Rationale & the small-worldness bridge

Network curvature/entropy/coherence (KEC) characterise the geometry of a network. Two substrates meet
in ZuCo: the **text** subjects read (a semantic/co-occurrence network) and the **brain** response
(an EEG channel network). A prior, classic result is that **semantic / word-association networks are
small-world** (Steyvers & Tenenbaum 2005). We have now observed the same on both sides here:

| network | σ (small-worldness) | verdict |
|---|---:|---|
| SWOW-EN word network | **1.8** | small-world |
| depression-text (min) | **71.6** | small-world (very high clustering) |
| **ZuCo EEG channel network (subj ZAB)** | **1.57** | small-world |

This motivates the bridge hypothesis: the small-world geometry of the read text is mirrored in the
small-world geometry of the neural channel network — testable across subjects. Small-worldness σ is
added as a **pre-registered KEC-adjacent measure** alongside K, E, C.

## 2. Question (PICOT)

- **P/unit:** per-subject ZuCo 2.0 natural-reading (NR) EEG channel network (n=16 subjects available,
  OSF 2abup; each ~842 MB sentence-level feature file → tractable subset downloaded).
- **Exposure:** subject (and, secondary, NR vs TSR task condition if TSR added).
- **Outcome:** KEC{K, E, C} of the channel network + small-worldness σ.
- **Comparison:** group-level distribution (subject = unit); and text-network vs brain-network σ.
- **T:** cross-sectional.

## 3. Hypotheses (frozen)

- **H1 (descriptive):** the ZuCo EEG channel network is small-world (σ>1) and spherical-leaning
  (K>0) **consistently across subjects** (per-subject σ and K with group CIs).
- **H2 (bridge):** brain-network small-worldness is present in the same regime as the read-text
  semantic network (both σ>1) — a qualitative text↔brain correspondence (NOT a per-subject causal link;
  the text is shared across subjects, so this is a regime statement, stated as such).
- **Primary endpoint:** the group mean (±CI) of channel-network σ across subjects, and the fraction of
  subjects with σ>1.

## 4. Data & honest connectivity caveat

- **Features, not raw time-series.** The OSF feature files give per-sentence band-power per channel
  (FFT bands), not continuous time-series. Therefore the channel network is built from **band-power
  co-activation** (correlation of per-channel band-power across sentences), and **C = mean
  co-activation** — NOT the magnitude-squared *coherence* used in the single-subject raw demo (which
  needs raw time-series). This is a declared substrate/feature limitation: feature-scale C ≠ raw-EEG
  coherence. (Raw coherence at scale would need the 70 GB raw set.)
- **Channels:** reduce the full montage to the 16 highest-variance channels per subject (Sounio Jacobi
  / GPU-kernel cap), pre-specified, blinded to any outcome.
- **Band:** alpha (8–13 Hz) primary; theta/beta as pre-registered sensitivity.

## 5. KEC + σ computation (pre-specified)

Per subject: band-power co-activation matrix (16×16) → threshold τ=0.30 → channel graph.
- **K** = mean Ollivier–Ricci curvature (exact OT).
- **E** = von Neumann spectral entropy (Sounio Jacobi instrument).
- **C** = mean off-diagonal co-activation.
- **σ** = (C_clust/C_rand)/(L/L_rand), 20 degree-matched random nulls.
Sounio-first: Python extracts the 16×16 matrix (I/O); the certified Sounio KEC computes E, λ₂ (verified
to match Python on the single-subject closure).

## 6. SAP

- Per-subject KEC + σ → group mean ± 95% CI (t or bootstrap over subjects).
- H1 decision: σ>1 in ≥ ⌈0.8·n⌉ subjects AND group-mean σ CI excludes 1.
- Sensitivity: band (alpha/theta/beta), τ ∈ {0.25,0.30,0.35}, n_channels ∈ {16, 24}.
- Confounds: per-subject network density (report; the κ↔density lesson), n_sentences, n_channels.

## 7. Validity & scope (honest)

Feature-scale co-activation (not raw coherence); subset of subjects; 16 of ~105 channels; reading task.
This is a **methods-scaling + small-worldness-bridge** study, not a clinical biomarker. No individual or
diagnostic claim. The text↔brain σ correspondence is a regime observation (shared text), not a
within-subject causal mediation.

## 8. Reproducibility

osfclient provenance (project 2abup), per-subject MD5s, fixed channel-selection + seeds, the certified
Sounio KEC instrument, results JSON. STROBE reporting.

## 9. Pre-registered outcomes

1. **Confirmatory:** channel-network small-world + spherical across subjects (H1), mirroring text σ (H2)
   → a clean text↔brain small-world bridge, certified-KEC-instrumented.
2. **Partial:** σ>1 but K or the bridge inconsistent → reported as such.
3. **Null:** channel networks not consistently small-world → honest negative.

*Execution: `code/analysis/zuco_kec_multisubject.py` (parse sentenceData → band-power co-activation →
KEC+σ per subject → group), results `results/unified/zuco_kec_multisubject.json`. Frozen before run.*
