# arXiv Submission

**Title:** When Are Semantic Networks Hyperbolic? A Curvature Phase Transition Theory with Cross-Linguistic Validation

**Authors:** Demetrios C. Agourakis

**Abstract:**

Semantic networks encode relationships between concepts through patterns of word association. Whether these networks exhibit hyperbolic geometry — and why — remains an open question with implications for cognitive architecture and network embedding. We present an empirically supported two-parameter model combining a curvature sign change in random graphs with analysis of 16 semantic networks across 7 languages and one clinical dataset, including an explicit train/test split for out-of-sample validation.

Using exact linear programming to compute Ollivier-Ricci curvature, we find that the density parameter eta = <k>^2/N is necessary but not sufficient for predicting hyperbolicity. Random k-regular graphs undergo a sign change in mean curvature at a critical density eta_c(N) = 3.75 - 14.62/sqrt(N) (R^2 = 0.995, N in {50, 100, 200, 500, 1000}). All semantic networks except Dutch SWOW fall below this threshold, yet taxonomies (WordNet, BabelNet) are near-Euclidean while association networks (SWOW, ConceptNet) are hyperbolic. A second parameter, the clustering coefficient C, separates these regimes: C* ≈ 0.05 fitted on 11 training networks correctly classifies 4/5 held-out test networks across three languages and two association protocols (EAT, USF).

Dutch SWOW (eta = 7.56 >> eta_c = 3.10) is spherical (kappa = +0.10), confirming the sign-change prediction. Sphere-embedded ORC across the Cayley-Dickson tower (S^3, S^7, S^15) flips 10/11 networks to positive curvature at d=4 and all 11 by d=8, demonstrating that semantic hyperbolicity is entirely metric-dependent. Curvature saturates to a positive asymptote (empirical exponent beta-bar = 0.28 << JL bound 0.5) at d >= 32. Degree-matched null models show that semantic organization makes networks less hyperbolic than random graphs with the same degree. A Lean 4 formalization (25 modules, 0 sorry in 7 core modules) provides machine-checked proofs of curvature bounds and regime exclusivity. The universal phase boundary maps structurally onto the loop-condensation critical point of Combinatorial Quantum Gravity; taxonomic networks (WordNet, BabelNet) are Euclidean because caterpillar-tree LLY flow converges to zero (arXiv:2601.02673), providing the first theoretical explanation for their geometric classification.

**Comments:** 20 pages, 10 figures, 7 tables, 30 references. Full code: github.com/agourakis82/hyperbolic-semantic-networks

**Categories:**

- Primary: cs.SI (Social and Information Networks)
- Secondary: math.CO (Combinatorics)
- Tertiary: physics.soc-ph (Physics and Society)

**Keywords:** semantic networks, Ollivier-Ricci curvature, phase transition, hyperbolic geometry, clustering coefficient, cross-linguistic, formal verification, Cayley-Dickson, Lean 4

**Character count:** ~1,580 (within arXiv 1,920-character limit)
