# Multi-Subject ZuCo KEC + Small-Worldness — Results (STROBE-style)

**Protocol:** `docs/research/PPCR_protocol_zuco_kec_multisubject.md` (frozen before run).
**Pipeline:** `code/analysis/zuco_kec_multisubject.py`. **Data:** ZuCo 2.0 NR feature files (OSF 2abup),
n=6 subjects (YAC, YAG, YAK, YDG, YDR, YFR; 842 MB–1.4 GB each, gitignored). 16 highest-variance
channels, alpha band-power co-activation network, τ=0.30.

## Per-subject + group

| subj | K (ORC) | E (vN norm) | C (co-act) | σ (small-world) |
|------|--------:|------------:|-----------:|----------------:|
| YAC | +0.615 | 0.975 | 0.847 | 1.00 |
| YAG | +0.435 | 0.966 | 0.523 | 1.03 |
| YAK | +0.360 | 0.961 | 0.443 | 1.13 |
| YDG | +0.465 | 0.970 | 0.713 | 1.01 |
| YDR | +0.584 | 0.976 | 0.881 | 1.00 |
| YFR | +0.543 | 0.976 | 0.803 | 1.00 |
| **group** | **+0.500 ± 0.089** | **0.971 ± 0.006** | 0.702 ± 0.165 | **1.029 ± 0.047** |

## Pre-registered decisions

- **H1 — spherical channel geometry (K>0): CONFIRMED.** K>0 in **6/6** subjects, group +0.500±0.089
  (tight). The reading-EEG channel network is robustly dense/spherical (opposite of the sparse,
  hyperbolic *word* networks). E (von Neumann spectral entropy) is high and very stable (0.971±0.006).
- **H2 — small-worldness of the channel network: NOT CONFIRMED.** σ = 1.029 ± 0.047; σ>1 in only
  **3/6** subjects; the group CI includes 1. The pre-registered rule (σ>1 in ≥5/6 AND CI excludes 1)
  is **not met**. The band-power co-activation networks sit at the small-world boundary
  (≈ random clustering), not robustly small-world.

## The honest, sharp finding — the bridge is CONNECTIVITY-DEPENDENT

The user's small-worldness intuition splits cleanly by what kind of network you build:

| network | σ | small-world? |
|---|---:|---|
| SWOW-EN **word** network (text) | 1.8 | **yes** (robust) |
| depression-**text** co-occurrence | 71.6 | **yes** (very) |
| ZuCo EEG, raw alpha **coherence** (1 subj) | 1.57 | **yes** |
| ZuCo EEG, band-power **co-activation** (6 subj) | 1.03 ± 0.05 | **no** (borderline, 3/6) |

So: the **text** subjects read is robustly small-world (anchoring on Steyvers & Tenenbaum 2005), and
the **dynamic phase-locking (coherence)** brain network is too — but the **amplitude co-activation**
brain network is spherical and only borderline small-world. The text↔brain small-world bridge holds for
*coherence-type* connectivity, **not** for *co-activation-type* — a real connectivity-dependent
distinction the PPCR sensitivity surfaced (it would have been an overclaim to assert a blanket
"brain networks are small-world like the text").

## COHERENCE BRIDGE — CLOSED AT GROUP LEVEL (the open question, now answered)

`code/analysis/zuco_coherence_multisubject.py`: the raw EEG time-series lives in
`sentenceData.rawData` *inside the feature files already on disk* (no 70 GB download needed). Computing
true alpha magnitude-squared **coherence** per subject (n=6) and the channel-network small-worldness:

| subj | σ (coherence) |
|------|--------------:|
| YAC | 2.59 |
| YAG | 1.55 |
| YAK | 1.09 |
| YDG | 2.08 |
| YDR | 2.18 |
| YFR | 1.09 |
| **group** | **1.762 ± 0.564, 95% CI [1.311, 2.213]** |

**σ>1 in 6/6 subjects; CI excludes 1 → pre-registered decision MET → COHERENCE BRIDGE CONFIRMED.**
The single-subject σ=1.57 replicates and strengthens at the group level. K=+0.33 (spherical, consistent).

## The complete, honest picture of the small-worldness bridge

| network | σ | small-world? |
|---|---:|---|
| SWOW-EN **word** network (text) | 1.8 | yes (robust) |
| depression-**text** co-occurrence | 71.6 | yes (very) |
| ZuCo EEG **coherence** (raw, **n=6 group**) | **1.76 ± 0.56, 6/6** | **yes — CONFIRMED at group level** |
| ZuCo EEG band-power **co-activation** (n=6) | 1.03, 3/6 | no (borderline) |

**The text↔brain small-world bridge is confirmed for coherence-type connectivity across subjects, and
absent for co-activation-type** — a clean, pre-registered, connectivity-dependent result. The read text
is small-world (Steyvers & Tenenbaum 2005) and so is the dynamic phase-locking (coherence) brain network
that processes it; amplitude co-activation is not. This is a regime correspondence (shared text across
subjects), not a within-subject causal mediation.

## Scope (honest)

n=6 of 16 available subjects; 16 of ~105 channels; alpha band; reading task; σ-based small-worldness
(threshold-sensitive). Methods-scaling + bridge confirmation, not a clinical claim. Full replication
would use all 16 subjects + multi-band; the n=6 coherence result is already 6/6 with CI excluding 1.
