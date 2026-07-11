# Repo-wide data-provenance audit — hyperbolic-semantic-networks (2026-05-27)

Forensic audit of data lineage across the repo (3 parallel auditors + direct verification), prompted
by the discovery that the "depression semantic networks" were mislabeled co-occurrence graphs. Findings
are tiered by severity. **This document records findings only; the flagged pre-existing artifacts were
NOT modified — those are decisions for the author.** (The one mislabel this session's own work
propagated — "SWOW" in the conference/analysis docs — was corrected separately.)

---

## TIER 1 — RESEARCH-INTEGRITY (must never reach a paper/talk)

**The "FEP / schizophrenia patient clustering coefficients" are fabricated provenance — PDF substring
artifacts mislabeled as graph metrics and promoted to a high-confidence patient cohort.**

Verified chain:
1. `darwin_agents_pdf_analysis.py` regex-scrapes numbers (`0.14, 0.04, 0.07, 0.08, 0.10, 0.12`) from
   the text of PMC10031728 (Nettekoven 2023).
2. **Direct verification:** the `context_snippet` for `0.14` in `data/manual_extraction/PMC10031728_manual_analysis.json`
   is *"...number of connected components ... ICC = 0.14..."* — an **intraclass correlation**
   (reliability stat), not a clustering coefficient. The source `PMC10031728_full_text.txt` contains
   **0 occurrences of "clustering coefficient"** (`grep -ic` = 0). The numbers are ICC values / page
   numbers (S142) / DOI fragments / processing times.
3. `PMC10031728_final_mapping.json` promotes these from `group:"Unknown"` → `group:"FEP",
   confidence:"high"`.
4. They surface as an empirical first-episode-psychosis cohort in `data/patient_control_metrics.csv`,
   `data/patient_control_statistics.json`, `data/final/strategy_a_final_report.json`
   (`"in_sweet_spot": true`, "FEP patients are WITHIN sweet spot"), and `data/final/patient_control_clustering_manual.csv`
   (auto-generated, not "manual").
5. `darwin_schizophrenia_extraction.py:57` hardcodes a *different* overlapping set
   `[0.04,0.05,0.09,0.10,0.12,0.14]` stamped `extraction_method="PDF_manual_extraction", n_subjects=1` —
   the values **disagree across the "manual" files**, which alone disproves a single real measurement.
6. `results/cross_disorder_comparison.json` ("First Episode Psychosis κ, n=6") is downstream of this.

**Verdict: FABRICATION-RISK.** No real FEP/psychosis cohort exists behind these numbers. Any clinical
clustering claim, "sweet-spot containment," or cross-disorder meta-analysis built on them would be
misconduct if published. **Action: quarantine these artifacts; they cannot be cited as empirical.**

`darwin_discovery_agents_fep.py` outputs a "Bayesian posterior" (0.20) from hand-typed priors — its own
conclusion is that the SWOW-vs-speech comparison is a methodological artifact; fine as self-critique,
dangerous if cited as a result.

---

## TIER 2 — MISLABEL + SOURCE-ABSENT (the conference-relevant layer)

- **Depression "semantic networks" = social-media word CO-OCCURRENCE graphs** (HelaDepDet
  `Depression_Severity_Levels_Dataset`, source **absent** from repo), construction sweep-tuned to a
  clustering "sweet spot," 250 posts/class, one draw. Already corrected in
  `stratified_density_match_depression_ANALYSIS.md` + conference docs + memory this session. **But**
  older artifacts and the `cpc2026_paper.md` draft still call the object "semantic networks."
- **`cpc2026_paper.md`** title — *"Entropic Curvature in Hyperbolic Semantic Manifolds Indexes
  Psychopathology-Like Transitions"* — sits over **simulated** O-SSM trajectories (anxious/ruminative/
  psychotic are Markov walks on SWOW-EN, not patients); Results are `[PLACEHOLDER]`. **OVERCLAIM** if
  submitted with that framing. Methods §4.4 honestly admits "a simulation study … not a patient dataset."
- **Cross-disorder figures** juxtapose SWOW free-association graphs with depression co-occurrence graphs
  under one "semantic networks" label — comparing different object classes; κ difference could be a
  construction-method artifact.

---

## TIER 3 — REPRODUCIBILITY / VERSION SMELLS (cleanup; doesn't sink the submitted paper)

- **Edge-version proliferation:** base / `_R1` / `_CORRECT` / `_FINAL` per language with *different
  semantics* (raw counts vs normalized strength 0–1). `_CORRECT` ≡ `_FINAL` byte-identical. Legacy
  scripts (`clustering_moderation_analysis.py`, `compute_kec_psychopathology.py`) still read the raw-count
  **orphan base files** — PR#212-class "ran on the wrong version" risk.
- **v6.4 analyses not reproducible:** input paths (`data/{en,es,nl,zh}/raw/…R123…`, `strength.SWOW*`)
  **don't exist**; English uses **R1** while ES/NL/ZH use **R123** in the same statistical test
  (contradicts the repo's own `DATA_DOWNLOAD.md`); networks built via `df.head(10000)` then BFS-sampled.
- **Edge counts equal hardcoded "target" comments** (776/815/817/799) with an uncited `strength_threshold=0.06`
  and `top_n=500` — looks reverse-engineered to a desired Table 1.
- **`dutch_edges.csv` has no producing script** yet backs the NL=817 cross-linguistic claim.
- **`russian/`, `multi-simlex/` raw = 0-byte placeholders** → any RU/EL output built from empty inputs.
- **"Hyperbolic sweet spot C≈0.02–0.15"** is a selected window from parameter/clustering sweeps
  (`methodological_parameter_sweep.py`) — same defect class as the depression sweep.

---

## CLEAN / sound (the good news)

- **Submitted Nature Communications manuscript** (`manuscript/main.md`, *"Boundary Conditions for
  Hyperbolic Geometry in Semantic Networks"*): its 8 graphs (SWOW es/en/zh, ConceptNet en/pt, WordNet en,
  BabelNet ru/ar) are **present and correctly labeled** (`results/unified/*_exact_lp.json`); SWOW is
  correctly called SWOW; **no depression/brain/clinical result is claimed as a finding** (clinical text
  is interpretive/future-work). *Caveat:* SWOW/ConceptNet/BabelNet raw sources are absent (documented as
  license-excluded) → results not re-derivable in-repo, but labels are honest.
- **WordNet** networks: NLTK-reproducible — CLEAN.
- **PubMed citations / PMIDs / papers_metadata**: real records (spot-checked), not hallucinated — CLEAN.
- **ABIDE fMRI**: correctly used, **honest null** (no ASD/TD ORC difference; classifiers at chance);
  inputs live in the external `/workspace/sounio/artifacts/research/abide/`, not this repo
  (SOURCE-ABSENT but honest). `compute_brain_curvature.jl` is an explicitly-caveated synthetic demo.
- **ADHD-200**: honest null, n=3 vs 7, self-flagged; source absent.
- **discovery_l (LWOW vs SWOW)**: separate, computationally honest-looking ORC study; inputs unverified
  here (not certified, but no darwin-style fabrication).

---

## Priority actions (author's call — not done here)

1. **Quarantine Tier-1**: remove/clearly mark the FEP/schizophrenia "clustering" artifacts and any
   cross-disorder result built on them as NON-EMPIRICAL. Highest priority — integrity.
2. **Tier-2 wording**: never call depression co-occurrence graphs "SWOW/semantic"; retitle/reframe
   `cpc2026_paper.md` as a simulation study (not a clinical finding) before any submission.
3. **Tier-3 hygiene**: collapse the edge-version proliferation to one canonical, documented version;
   make v6.4 inputs present + use a consistent R-set across languages; document the 0.06/top-500 choices
   or justify them; identify the dutch_edges builder.
4. The submitted NatComm paper appears safe as written, modulo the (legitimate) source-absence caveat.
