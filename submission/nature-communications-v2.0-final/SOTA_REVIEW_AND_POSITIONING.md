# SOTA review, reference curation & editorial positioning — v2.0-final

*Source: adversarially-verified deep-research sweep (22 primary sources, 25 claims verified, 21 confirmed / 4 killed, 2026-06-04). Cross-referenced against the current manuscript.*

## Verdict

The paper sits at the intersection of **three well-established but previously-unconnected literatures** (discrete network curvature; hyperbolic geometry of language; graph biomarkers in psychiatry). The central thesis is **plausible and defensible**, and the *mechanism* the manuscript now leads with — clustering as a **damper** of an underlying hyperbolic tendency — is **directly grounded in settled mathematics** (the ORC↔clustering decomposition κ = μ₀ − μ₂ − 2μ₃). The synthesis (weighted ORC + SWOW free-association × 4 languages + null models + Ricci flow + construction-dependence) appears **genuinely novel**, but rests on **n=7 networks** and a **weighted-vs-unweighted seam** that the literature does *not* resolve in the paper's favour.

## Two load-bearing risks (fix before submission)

### RISK 1 — Direct prior art the paper does not cite: Yamshchikov et al. 2020
**Yamshchikov, Nono Saha, Samenko & Jost (2020), "It Means More if It Sounds Good," COMPLEXIS (arXiv:2003.05758)** already applied **Ollivier-Ricci curvature to a WordNet synonym network using the identical GraphRicciCurvature library**, finding negative-ORC edges bridge semantic communities and positive-ORC edges stay within them. This is the single most likely *"why is this novel?"* reviewer challenge. **Must cite + differentiate explicitly:** (a) they used **unweighted** ORC, we use **weighted**; (b) their goal was **polysemy estimation**, not a curvature thesis or construction-dependence; (c) a **single English synonym/taxonomy graph** vs our **4-language free-association (SWOW) + taxonomy with explicit null models and Ricci flow**.

### RISK 2 — The weighted/unweighted choice is load-bearing for the *taxonomy* result (and the whole thesis)
Verification **REFUTED (0-3)** the convenient claim "trees have all-negative ORC" only in the sense that it *is* true under **unweighted hop-distance**: **pure trees are NEGATIVELY curved under unweighted ORC** (Ni et al. 2015). The manuscript claims tree-like **taxonomies are near-Euclidean** — which holds under our **weighted** measure but would likely *flip to hyperbolic under unweighted ORC*. So **"construction-dependence (association hyperbolic / taxonomy Euclidean)" may be partly a property of the weighted measure, not of construction alone.** A sharp reviewer will press this. **Action:** add a **weighted-vs-unweighted sensitivity analysis for the taxonomy networks** (does WordNet/BabelNet go negative under unweighted ORC?), and own the result either way. This is also exactly the axis where the companion **native exact unweighted machinery** is useful as an independent check.

## Curated references to ADD (with why)

| # | Reference | Why it matters | Where |
|---|---|---|---|
| **A** | **Ni, Lin, Gao, Saucan, Gu (2015)** "Ricci Curvature of the Internet Topology," IEEE INFOCOM, arXiv:1501.04138 | **Canonical method** (α-lazy-walk measure, α=0.5, LP Wasserstein — exactly our tooling) **AND** the construction-dependence precedent: curvature distributions "differ strongly by network type even when degree distributions match." | Methods §2.4 + Discussion |
| **B** | **Ni, Lin, Luo, Gao (2019)** "Community Detection on Networks with Ricci Flow," Sci. Rep. 9:9984 | The **bridge=negative / intra-community=positive** mechanism, verbatim; and **Ricci flow** on networks (we run Ricci-flow experiments). | §2.5 (Ricci flow) + §3.4/§4 |
| **C** | **Azarhooshang, Sengupta, DasGupta (2020)** "A Review of and Some Results for Ollivier-Ricci Network Curvature," Mathematics 8(9):1416 | The **κ = μ₀ − μ₂ − 2μ₃** decomposition — *the* mathematical basis for "low clustering ⇒ negative ⇒ clustering dampens." **Most load-bearing citation for the new thesis.** | §3.2 / §4 (cite prominently) |
| **D** | **Samal et al. (2018)** "Comparative analysis of two discretizations of Ricci curvature for complex networks," Sci. Rep. 8:8650 | Justifies **weighted ORC over Forman-Ricci** (ORC encodes clustering/3–5-cycles & betweenness; Forman mainly topology). Pre-empts "why ORC?" | §2.4 |
| **E** | **Yamshchikov et al. (2020)** arXiv:2003.05758 | **Direct prior art (RISK 1).** | Intro + Discussion (differentiate) |
| **F** | **Tifrea, Bécigneul, Ganea (2018/19)** "Poincaré GloVe," ICLR, arXiv:1810.06546 | Word log-co-occurrence graphs have **low δ-hyperbolicity** → independent motivation for hyperbolic geometry of language. *(Do NOT cite for embedding benchmark-superiority — that claim was refuted.)* | Intro §1.2 |
| **G** | **Li, Wu & Evans (2020)** "Social Centralization and Semantic Collapse," Poetics, arXiv:2001.09493 | Hyperbolic geometry models the **hierarchy + sparse bridging** of semantic networks. | Intro §1.2 |
| **H** | **Mota et al. (2012)** "Speech graphs provide a quantitative measure of thought disorder in psychosis," PLoS ONE 7(4):e34928 | Speech-graph measures separate schizophrenia/mania ~94% — the **clinical-hypothesis anchor** (note: global metrics, **not** curvature). | §4 clinical (hypothesis) |
| **I** | **Elumalai et al. (2022)** "Graph Ricci curvatures reveal atypical functional connectivity in ASD," Sci. Rep. 12 (s41598-022-12171-y) | ORC/FRC **as a clinical network biomarker** (brain, not speech) → feasibility for our hypothesis. | §4 clinical |
| **J** | **Simhal et al. (2020)** "Measuring robustness of brain networks in ASD with Ricci curvature," Sci. Rep. 10:10819 | Ricci curvature tracks robustness/clinical change → curvature→entropy→robustness framing. | §4 clinical |

*(Already cited and fine: Ollivier 2009 [9]; Jost & Liu 2014 [15] — but elevate it in §3.2/§4 as a mechanism citation; Clauset-Shalizi-Newman [14]; GraphRicciCurvature library [13].)*

## What the literature does NOT support — do not lean on these (verification-killed)
- ❌ "Hyperbolic embeddings beat Euclidean on similarity/analogy/hypernymy" (0-3) — don't invoke benchmark superiority.
- ❌ "2-D Poincaré disk represents trees without distortion" (1-2).
- ❌ "Ricci curvature finds clinical pathways missed by standard DTI/brain-network analysis" (0-3) — don't claim unique added value over conventional methods.
- ⚠️ "Trees are all-negative ORC" is true *unweighted* — handle with care (RISK 2).

## Editorial positioning

- **Differentiation:** the paper's defensible novelty is the **combination** — weighted ORC on **multilingual free-association** data + **null-model causal test** (clustering damper) + **Ricci-flow resistance** + the **construction-dependence** framing. Lead with that triplet; explicitly distinguish from Yamshchikov (semantic ORC, but unweighted/single-graph/polysemy) and Ni (mechanism + Internet, not language).
- **Venue (honest read):** given **n=7** and that the biomarker angle is **cross-domain/hypothetical** (no direct curvature-on-speech evidence exists), the evidence profile fits **Network Neuroscience, PNAS Nexus, or Patterns at least as well as Nature Communications.** Nat Comms is defensible *if* the paper adds the robustness analyses below; otherwise expect desk-reject risk on "incremental + small-n." Consider PNAS Nexus / Patterns as strong primary or fast-fallback targets.
- **Reviewer objections to pre-empt:** (1) n=7; (2) weighted-vs-unweighted robustness (RISK 2); (3) Yamshchikov novelty (RISK 1); (4) construction-dependence confounded with the two graph *types* (only 4 association + 3 taxonomy); (5) clinical overclaim (already softened — keep it a hypothesis).

## Prioritized suggestions to strengthen the paper

1. **(HIGH) Add Yamshchikov 2020 + a 2-sentence differentiation** (RISK 1). Cheapest, highest-impact.
2. **(HIGH) Weighted-vs-unweighted sensitivity, esp. for taxonomies** (RISK 2). Compute unweighted ORC on WordNet/BabelNet; report whether the Euclidean-taxonomy result survives. The native exact unweighted machinery is the tool.
3. **(HIGH) Cite the mechanism trio (C, B, A/Jost-Liu)** in §3.2/§4 so the "clustering damper" reads as *grounded in established theory*, not a new ad-hoc claim — this is the paper's strongest defensible move.
4. **(MED) Forward-citation sweep of Ni 2019 + Yamshchikov 2020 for 2025-2026 work** before finalizing the novelty claim (the search did not surface the most recent competitors).
5. **(MED) Expand n where cheap:** the configuration/triadic nulls and the network-size variants are *additional* (C, κ) observations already in the pipeline — use them to support the mechanism (not the GAM, which is descriptive at n=7).
6. **(LOW) Re-evaluate venue** against how much new empirical curvature-on-SWOW evidence remains after the above vs reinterpretation of established mechanisms.

---

## UPDATE 2026-06-04 — actions taken (tasks 1–3 executed)

**Task 1 (references + content) — DONE.** Added 10 references to `references.bib` (Jost–Liu 2014, Azarhooshang 2020, Samal 2018, Yamshchikov 2020, Tifrea 2019, Li–Wu–Evans 2020, Elumalai 2022, Simhal 2020, Sandhu 2015, Sia 2019). Added the **Yamshchikov 2020 differentiation** to §1.3 and the **weighted-vs-unweighted robustness** result to §3.5.

**Task 2 (weighted-vs-unweighted sensitivity) — RISK 2 RESOLVED (favourably).** Recomputed ORC on all 7 networks under weighted and unweighted edges (`results/weighted_vs_unweighted_orc.json`):

| | weighted κ̄ | unweighted κ̄ |
|---|---|---|
| SWOW ES / EN / ZH / NL | −0.155 / −0.258 / −0.214 / −0.270 | −0.068 / −0.137 / −0.144 / −0.196 |
| WordNet EN / BabelNet RU / AR | −0.002 / −0.030 / −0.012 | **identical** (edges are weight=1 by construction) |

Association networks are hyperbolic under **both** definitions; taxonomy edges are unweighted by construction, so "Euclidean taxonomy" is **not** a weighting artifact. **Construction-dependence is robust to the weighted/unweighted choice.** Bonus: the unweighted SWOW values reproduce the companion **exact rational-arithmetic** ORC implementation to ≤1e-3 (independent cross-validation).

**Task 3 (forward-citation sweep) — novelty CONFIRMED.** No 2025–2026 work applies ORC to SWOW/free-association networks; the speech-curvature biomarker gap is still open (2025 psychiatric-speech work uses acoustic/GCN/symptom-network methods, not curvature). New context: the field is moving to **hyperbolic LLMs** (HELM, 2025; arXiv:2505.24722) and there is a 2025 *Hyperbolic geometric graph representation learning* survey — useful "current direction" framing, but those are embedding/architecture works, not curvature **measurement** of association networks (our distinct contribution). Added Sia et al. 2019 (ORC community detection).
