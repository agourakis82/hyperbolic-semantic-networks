# Cover Letter

**To:** Editor-in-Chief, *Journal of Complex Networks*
**From:** Demetrios C. Agourakis
**Date:** March 7, 2026
**Subject:** Manuscript Submission — "When Are Semantic Networks Hyperbolic? A Curvature Phase Transition Theory with Cross-Linguistic Validation"

---

Dear Editors of *Journal of Complex Networks*,

I am pleased to submit the manuscript entitled **"When Are Semantic Networks Hyperbolic? A Curvature Phase Transition Theory with Cross-Linguistic Validation"** for your consideration.

## Why This Work Matters

Whether semantic networks are hyperbolic is a foundational question in cognitive network science, yet no quantitative criterion existed for predicting when hyperbolicity arises or why it fails. This manuscript provides an empirically supported two-parameter model — combining network density and clustering — that correctly classifies the geometry of all 11 networks studied across 7 languages and one clinical dataset.

## Novel Contributions

**First, a curvature sign change with finite-size scaling.** Using exact linear programming to compute Ollivier-Ricci curvature on random k-regular graphs, we identify a sign change in mean curvature at a critical density eta_c(N) = 3.75 - 14.62/sqrt(N) (R^2 = 0.995, N in {50, 100, 200, 500, 1000}). This scaling law provides a quantitative boundary separating hyperbolic from spherical network geometry.

**Second, a bridge finding in real cognitive data.** The Dutch SWOW network (eta = 7.56 >> eta_c = 3.10) is the first real semantic network observed to cross the phase boundary into spherical geometry (kappa = +0.099), directly confirming the density-driven sign change.

**Third, metric dependence of hyperbolicity.** Embedding all 11 networks into unit spheres via the Cayley-Dickson tower (S^3, S^7, S^15) and computing geodesic-cost ORC, we show that 10/11 networks become spherical at d=4 and all 11 by d=8. Semantic hyperbolicity is an artifact of the hop-count metric, not an intrinsic topological property.

**Fourth, formal verification.** A Lean 4 formalization comprising 25 modules and 8097 lines provides machine-checked proofs of Wasserstein non-negativity, curvature boundedness, and regime exclusivity, with 0 sorry statements in 7 core ORC-theory modules. An independent implementation in the Sounio language cross-validates all results (33/33 sign agreement with Julia exact LP).

## Scope and Methods

The analysis covers 11 semantic networks: SWOW (Spanish, English, Chinese, Dutch), ConceptNet (English, Portuguese), WordNet, BabelNet (Russian, Arabic), and a depression symptom network — spanning 7 languages and 3 language families. Curvature is computed via exact LP (HiGHS solver), eliminating Sinkhorn regularization bias. Degree-matched null models reveal that semantic organization makes networks *less* hyperbolic than random graphs, the opposite of naive expectation.

## Fit with Nature Communications

This manuscript bridges network geometry theory, cognitive science, and formal verification — disciplines that are individually active but rarely integrated. The finding that hyperbolicity is metric-dependent challenges a foundational assumption in network embedding, while the formal verification methodology sets a new standard for computational reproducibility in network science.

## Suggested Reviewers

1. **Dr. Cynthia Siew** (National University of Singapore)
   Email: cynthia.siew@nus.edu.sg — Cognitive network science, semantic networks

2. **Dr. Fragkiskos Papadopoulos** (Cyprus University of Technology)
   Email: fragkiskos.papadopoulos@cut.ac.cy — Hyperbolic network geometry

3. **Dr. Simon De Deyne** (University of Melbourne)
   Email: simon.dedeyne@unimelb.edu.au — SWOW datasets, word associations

4. **Dr. Chien-Chung Ni** (Meta AI Research)
   Email: nichien@meta.com — Ollivier-Ricci curvature, GraphRicciCurvature library

5. **Dr. Danielle S. Bassett** (University of Pennsylvania)
   Email: dsb@seas.upenn.edu — Network neuroscience, cognitive biomarkers

## Competing Interests

I declare no competing interests. This research received no specific funding.

---

Thank you for considering this manuscript. I believe it makes significant contributions to network geometry theory, cognitive network science, and formal verification methodology.

Sincerely,

**Demetrios C. Agourakis**
Independent Researcher
Email: demetrios@agourakis.med.br
ORCID: 0000-0002-8596-5097

---

**Attachments:**

1. Main manuscript (PDF) — v3.0, 13 pages
2. Figure files (8 figures, PDF/PNG)
3. Code repository link (GitHub)
