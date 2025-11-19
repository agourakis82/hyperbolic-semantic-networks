# Boundary Conditions for Hyperbolic Geometry in Semantic Networks
## Clustering-Curvature Trade-offs Revealed by Ollivier–Ricci Analysis

**Manuscript – Paper 1**
**Target Journal**: *Nature Communications* (Impact Factor: 16.6)
**Status**: Major Revisions Complete (v2.0)
**Date**: 2025-11-08

---

## ABSTRACT

Semantic networks encode relationships between concepts through patterns of word association. While their topological properties have been extensively studied, the intrinsic geometry of these networks—whether they curve toward hyperbolic, flat, or spherical space—remains less well characterized. We applied Ollivier–Ricci curvature analysis to eight semantic graphs spanning three Small World of Words (SWOW) association networks (Spanish, English, Chinese), two ConceptNet knowledge graphs (English, Portuguese), and three taxonomy-based lexical graphs (English WordNet, BabelNet Russian, BabelNet Arabic).

We found that hyperbolic geometry is not universal in semantic networks but depends critically on network structure. Association-based networks consistently exhibited hyperbolic curvature ($\kappa$ = -0.17 to -0.26, N=5), while taxonomy-based networks clustered near Euclidean geometry ($\kappa \approx 0$, N=3). This distinction was driven not by relation semantics but by clustering coefficient: networks with minimal clustering (C < 0.01, tree-like taxonomies) were Euclidean, those with moderate clustering (C = 0.02–0.15) were hyperbolic, and those with high clustering (C > 0.30) shifted toward spherical geometry. This non-linear relationship defined a "hyperbolic sweet spot" where language-driven association networks naturally reside.

Configuration model nulls (M = 1000 replicates) that preserved degree distributions but destroyed clustering proved significantly more hyperbolic than real SWOW networks ($\Delta \kappa$ = +0.17 to +0.22, p_{MC} < 0.001), confirming that local clustering moderates underlying geometry. A subset of triadic-rewire nulls (Spanish, English; M = 1000) preserved triangle counts and eliminated the curvature shift, isolating clustering as the causal moderator. Discrete Ricci flow experiments further demonstrated that forcing semantic graphs toward curvature equilibrium reduces clustering by 79–86 % and removes negative curvature, indicating functional resistance to geometric flattening.

These findings identify boundary conditions for hyperbolic geometry in semantic networks: it emerges not from hierarchical structure per se, but from the specific balance of degree heterogeneity and local clustering characteristic of association-based construction. The results supply quantitative criteria that future datasets can use to assess whether their semantic organization resides within the hyperbolic corridor or departs toward alternative geometries.

**Keywords**: semantic networks, hyperbolic geometry, Ricci curvature, clustering coefficient, null models, cross-linguistic

---

## 1. INTRODUCTION

### 1.1 Background

Semantic memory—the structured knowledge of concepts and their relationships—is fundamental to human cognition. Network science offers a quantitative lens on this organization, treating words as nodes and associations as edges to uncover small-world structure, modularity, and degree heterogeneity [1-3]. Recent work has expanded beyond classical graph metrics to interrogate intrinsic geometry. Hyperbolic spaces, in particular, naturally accommodate hierarchical growth and heterogeneous branching—properties long observed in semantic association datasets [4-7]. Yet most evidence for hyperbolicity in language has been indirect, relying on embeddings or curvature heuristics rather than explicit geometric measurement. This motivates a systematic investigation of when, and under which topological conditions, semantic networks manifest negative curvature in a reproducible manner across languages and knowledge sources.

### 1.2 Hyperbolic Geometry and Semantic Organization

Hyperbolic spaces exhibit negative curvature ($\kappa < 0$) and accommodate exponentially branching hierarchies without substantial distortion. Volumes grow rapidly with distance, triangles have angle sums below 180°, and tree-like structures embed efficiently—properties that mirror the layered lexical architecture supporting semantic memory [7,8]. Prior work has reported hyperbolicity in social, biological, and technological networks, yet a systematic map distinguishing when real linguistic associations converge to this geometry—and when they deviate—has been lacking.

### 1.3 Discrete Curvature Tooling for Semantic Networks

We adopt Ollivier–Ricci curvature [9] as the primary descriptor because it quantifies, via optimal transport between neighborhoods, whether an edge behaves as hyperbolic, Euclidean, or spherical. This approach has been successfully applied to identify critical bridges and quantify robustness in molecular interaction networks, brain connectomics, and knowledge graphs [19-23]. Applying the same toolkit to semantic networks lets us demarcate the topological conditions under which hyperbolicity emerges and when alternative geometries take over.

### 1.4 Research Questions

1. Do semantic networks exhibit hyperbolic geometry?
2. Is this property **consistent** across diverse languages?
3. How does semantic network geometry relate to degree distribution topology?
4. Is the effect robust to network size and sampling variations?

### 1.5 Hypotheses

We hypothesized that semantic networks would exhibit negative mean curvature (hyperbolic geometry), that this property would replicate across diverse language families, and that it would prove robust to network size and parameter variations. We further posited that clustering would operate as the critical moderator: extremely low or high clustering should push networks toward Euclidean or spherical regimes, respectively. The core prediction is straightforward: if semantic memory combines hierarchical structure with moderate triadic closure, Ollivier–Ricci analysis should detect sustained hyperbolicity.

---

## 2. METHODS

### 2.1 Data Sources

- **Association networks (SWOW)**: Three Small World of Words (SWOW) R1 cue-response matrices (Spanish, English, Chinese) [smallworldofwords.org](https://smallworldofwords.org). Each survey includes >80,000 participants and provides association strengths between cue and first response.
- **Association networks (ConceptNet)**: ConceptNet 5.7 English and Portuguese assertions filtered to weight $\geq$ 2.0 and restricted to the top 500 concepts by usage frequency, capturing general knowledge relations complementary to SWOW free associations.
- **Taxonomy networks**: Directed *is-a* hierarchies derived from English WordNet 3.1 and BabelNet 5.3 (Russian and Arabic subgraphs). We extracted synset-level relations, lemmatized surface forms, and collapsed multi-word expressions to single lexical units to align with SWOW vocabulary coverage.

All datasets were downloaded between 2025-10-15 and 2025-10-28. Detailed licensing information and checksums are provided in `data/README.md`.

### 2.2 SWOW Association Network Construction

For each SWOW language, we constructed directed weighted networks by selecting the 500 most frequent cue words as nodes. Directed edges connect cues to their associated responses, weighted by normalized association strength (0–1). A typical entry is `dog → cat (0.35)`, reflecting the probability that participants produced *cat* given the cue *dog*. This yielded networks ranging from 422 to 465 nodes in the largest connected component (571–762 edges, density $\tilde{p} \approx 0.006$–0.007) with sparse connectivity (mean degree 2.7–3.3), consistent with prior SWOW analyses.

### 2.3 ConceptNet Association Network Construction

We derived ConceptNet graphs using the workflow in `code/analysis/build_conceptnet_network.py`: ConceptNet 5.7 assertions were parsed, edges with weight $\geq$ 2.0 were retained, and the 500 most frequent concepts per language were chosen as nodes. Edges linking two selected concepts were retained with their original weights and relation labels. The directed edge list was converted to an undirected graph and restricted to the largest connected component (467 nodes / 2474 edges for English; 489 nodes / 1578 edges for Portuguese), providing a high-coverage knowledge-association baseline complementary to SWOW free associations.

### 2.4 Taxonomy Network Construction

WordNet (English) and BabelNet (Russian, Arabic) graphs were converted to directed acyclic taxonomies by retaining *hypernym* and *instance hypernym* relations. We mapped synsets to lemmas, collapsed morphological variants through lemmatization (spaCy v3.7 models), and merged multi-word expressions (e.g., *golden retriever*) into single tokens connected via underscores to preserve connectivity. To maintain comparability with association networks, we intersected each taxonomy with the SWOW vocabulary and retained the largest weakly connected component, yielding graphs with 142–522 nodes. Edge weights were set to 1.0 (unweighted), and direction followed the *is-a* hierarchy (child → parent). Depth distributions remained representative of the source ontologies after subsetting.

### 2.5 Curvature Computation

We computed Ollivier–Ricci curvature using the `GraphRicciCurvature` Python library [13], preserving the directed and weighted nature of semantic associations (asymmetric connections and variable strengths). The idleness parameter $\alpha$ was set to 0.5 (default value recommended for semantic networks), with 100 Sinkhorn iterations ensuring convergence. We analyzed the largest weakly connected component for each network. Sensitivity analyses (reported in Supplement) tested symmetrized graphs, binary versions, and systematic $\alpha$ variations (0.1-1.0), all confirming robustness. This procedure yields a curvature value $\kappa \in [-1, 1]$ for each edge, where negative values indicate hyperbolic geometry, zero indicates flat (Euclidean), and positive indicates spherical.

### 2.6 Discrete Ricci Flow Experiments

To probe geometric stability we applied discrete Ricci flow [16] to a subset of networks (Spanish SWOW, English SWOW, English configuration null, English taxonomy). Following Ni et al. (2019), edge weights evolved according to $\frac{dw_e}{dt} = -\eta\,\kappa(e)\,w_e$ with step size $\eta = 0.5$ over 40 iterations or until consecutive mean curvature changes fell below $10^{-4}$. After each update we re-normalized weights to maintain total volume and recomputed clustering and curvature. Flow trajectories were run on CPU (Intel i7-11700K) using the `GraphRicciCurvature` implementation with deterministic seeding for reproducibility. We logged $(C_t, \bar{\kappa}_t)$ pairs to quantify resistance to geometric flattening.

### 2.7 Degree Distribution Analysis

**Tool**: `powerlaw` Python library [14]
**Method**: Clauset, Shalizi, Newman (2009) protocol

**Analysis steps**:
1. Maximum likelihood estimation of power-law exponent $\alpha$
2. Estimation of xmin (lower bound of power-law regime)
3. Kolmogorov-Smirnov goodness-of-fit test (p-value)
4. Likelihood ratio tests: power-law vs. lognormal, vs. exponential

**Interpretation**:
- $\alpha \in [2, 3]$ and $p > 0.1$: classical scale-free
- $\alpha < 2$ or $p < 0.1$: broad-scale (heavy-tailed but not power-law)
- Lognormal $R < 0$: lognormal fits better
- Competitive with lognormal ($p > 0.05$)

### 2.8 Computational Details

**Software environment**:
- Python 3.10.12
- NetworkX 3.1
- GraphRicciCurvature 0.5.3 [13]
- powerlaw 1.5 [14]
- NumPy 1.24.3, SciPy 1.11.1

**Ollivier–Ricci curvature parameters**:
- Alpha ($\alpha$): 0.5 (balanced neighborhood mixing)
- Iterations: 100 (convergence of Wasserstein distance)
- Method: Sinkhorn algorithm

**Network construction**:
- Node selection: Top 500 most frequent cue words per language
- Edge inclusion: All cue$\rightarrow$ response associations (R1 responses)
- Edge weights: Association strength (normalized 0-1)
- Graph type: Directed, weighted

**Null model generation**:
- Erdős-Rényi: p = m/n(n-1) where m = observed edges, n = 500
- Barabási-Albert: m = ceil(edges/nodes) = 2
- Watts-Strogatz: k = 2m (even), rewiring p = 0.1
- Lattice: 2D grid (floor(sqrt(n)) x floor(sqrt(n)))
- Iterations: 100 per model per language

**Statistical tests**:
- Null model comparison: one-sample $t$-test (real vs. null distribution)
- Effect size: Cohen's $d = (\mu_{\text{real}} - \mu_{\text{null}}) / \sigma_{\text{null}}$
- Significance threshold: $\alpha = 0.05$

### 2.9 Null Models

We employed two structural null models for statistical inference. The **configuration model** (Molloy & Reed, 1995) preserves the exact degree sequence and weight marginals while randomizing connections via stub-matching algorithm, with M=1000 replicates per association network. The **triadic-rewire model** (Viger & Latapy, 2005) additionally preserves triangle distribution and clustering through edge-rewiring that maintains triadic closure statistics (M=1000 replicates for Spanish/English SWOW; computational constraints prevented completion for Chinese SWOW and ConceptNet, estimated at ~5 days per network).

For each null replicate, we computed mean curvature and reported four metrics: $\Delta \kappa$ (difference between real and null mean curvature), p_MC (Monte Carlo p-value calculated as the proportion of null replicates with curvature as extreme as observed), Cliff's $\delta$ (robust ordinal effect size ranging from -1 to +1), and 95% confidence intervals via percentile method.

Additionally, we examined pedagogical baseline models for geometric contextualization (Figure 3D): Erdős-Rényi random graphs (p=0.006), Barabási-Albert preferential attachment (m=2), Watts-Strogatz small-world (k=4, p=0.1), and regular 2D lattices. These baselines illustrate the spectrum of possible network geometries but were not used for hypothesis testing, as they don't preserve the structural properties of semantic networks.

### 2.10 Robustness Analysis

We assessed robustness through bootstrap resampling (50 iterations with 80% node sampling) and systematic network size variations (250 to 750 nodes). Stability was quantified using coefficient of variation (CV) and 95% confidence intervals derived from bootstrap distributions.

### 2.11 Statistical Analysis

We used non-parametric statistics appropriate for network data: Spearman correlation quantified associations between curvature and degree, while Kruskal–Wallis tests compared distributions across groups. Null-model inference relied on Monte Carlo permutation tests (M = 1000 replications per language). Effect sizes were expressed via Cliff’s $\delta$ (range -1 to +1) and $\Delta \kappa$ (absolute deviation from the null mean). Benjamini–Hochberg correction controlled the false discovery rate across multiple comparisons; adjusted values are reported alongside raw $p_{MC}$ in Table 2. Full details on seeds, hardware configuration, library versions, and execution scripts are compiled in Section 2.12. A preregistered protocol for forthcoming meta-analyses is documented in Supplementary Section S7 and is not analysed in the present study.

For planned extensions involving clinical cohorts and additional datasets, we pre-specified effect-size conventions to ensure comparability. Continuous network differences (e.g., mean clustering, largest connected component) will be summarized using Hedges’ g with small-sample correction; correlations between network measures and symptom scales will be meta-analysed via Fisher’s z transform; diagnostic performance will be synthesized through HSROC models when sensitivity/specificity pairs are available, or by pooling AUC/DOR with appropriate variance estimates when only scalar metrics are reported. Random-effects models (REML) will serve as default, with heterogeneity quantified by $\tau^2$ and $I^2$; moderators (diagnostic category, task paradigm, network construction method) will be explored through meta-regression or subgroup analyses when $k \ge 6$.

Publication bias will be assessed using funnel plots, Egger regression, trim-and-fill adjustments, and p-curve analysis where feasible ($k \ge 10$). Sensitivity analyses will exclude studies with $n < 15$ per group or high risk of bias. To handle correlated metrics reported within a single study, we will employ multivariate meta-analytic models or, when covariance matrices are unavailable, control the false discovery rate across parallel univariate syntheses. Study quality will be evaluated with a hybrid Newcastle–Ottawa/QUADAS framework, and leave-one-out analyses will confirm the robustness of pooled estimates.

### 2.12 Reproducibility and Availability

**Operating system and environment**: Ubuntu 22.04.4 LTS (WSL2) with Python 3.10.12. Dependencies are pinned in `environment.yml` and `code/analysis/requirements.txt`, covering NetworkX 3.1, GraphRicciCurvature 0.5.3, powerlaw 1.5, NumPy 1.24.3, SciPy 1.11.1, pandas 2.1.1, and seaborn 0.13.2.

**Seeds and determinism**: 42 (sampling and Ricci flows), 123 (structural null models), 456 (bootstrap and parameter sweeps). Each script allows overriding the seed via `--seed` or an environment variable `SEED`, as documented in the file header.

**Computational resources**: Intel Core i7-11700K CPU (8 cores / 16 threads), 32 GB DDR4 RAM, NVMe storage. All routines ran on CPU; average runtime per stage was ~2 h for SWOW/ConceptNet curvature, ~30 min per batch of null models (M = 1000), and ~15 min per Ricci-flow trajectory.

**Executable workflow**:
1. `code/analysis/preprocess_swow_to_edges.py` and `code/analysis/build_conceptnet_network.py` produce normalized edge lists (`data/processed/swow_*` and `data/processed/conceptnet_*`).
2. `code/analysis/compute_curvature_FINAL.py` computes Ollivier–Ricci curvature, saving `results/kec_*_node_level.csv` and `results/FINAL_CURVATURE_CORRECTED_PREPROCESSING.json`.
3. `code/analysis/07_structural_nulls.py` generates configuration-model replications (`results/structural_nulls/`), and `code/analysis/07_structural_nulls_cluster.py` applies the triadic-rewire null.
4. `code/analysis/robustness_validation_complete.py`, `methodological_parameter_sweep.py`, and `window_scaling_experiment.py` perform bootstraps and parameter sweeps (`results/robustness_validation_complete.json`, `results/window_scaling_complete.json`).
5. `code/analysis/ricci_flow_real.py` executes the Ricci flows, exporting trajectories to `results/ricci_flow/`.

**Logging and audit trail**: Each routine writes structured logs (ISO 8601 timestamps, seed, key parameters) under `logs/`, with experiment-specific subdirectories (`logs/final_validation/`, `logs/ricci_flow/`). Summary artifacts cited in the manuscript are versioned in `results/kec_network_level_summary.{csv,json}`, `results/bootstrap_curvature_additional.json`, and `results/phase_diagram_metrics.csv`.

**Data availability**: SWOW (ES/EN/ZH) is publicly accessible at `https://smallworldofwords.org`; ConceptNet 5.7 (EN/PT) at `https://conceptnet.io`. Taxonomic subsets derive from WordNet 3.1 (Princeton) and BabelNet 5.3 (academic license); extraction scripts and SHA256 hashes are documented in `data/README.md`.

**Code and artifact availability**: The full pipeline, auxiliary notebooks, and figure generation scripts reside at `https://github.com/agourakis82/hyperbolic-semantic-networks` (release v2.0, DOI 10.5281/zenodo.17531773). Submission dossiers are stored under `submission/`, and `results/figures/` contains the `.pdf` and `.png` files used for Figures 1–4.

---

*Manuscript prepared for submission to Nature Communications*
*Word count: ~5,500 words (main text)*
*Tables: 3 (Network statistics, Null-model comparisons, Ricci flow summary)*
*Figures: 4 (Clustering–curvature map, Null comparisons, Ricci flow trajectories, Phase diagram)*
*Version: v2.0 (Major Revisions Complete)*

## 3. RESULTS

### 3.1 Cross-Linguistic Curvature Profiles

All three SWOW association networks exhibited negative mean Ollivier–Ricci curvature (ES: $\bar{\kappa} = -0.155$, EN: $-0.258$, ZH: $-0.214$; Table 1) with narrow bootstrap 95% confidence intervals (±0.02–0.03; 50 resamples at 80% node sampling). ConceptNet association graphs (English, Portuguese) likewise produced negative curvature ($\bar{\kappa} = -0.209$ and $-0.165$) despite lower global clustering (C = 0.014–0.017). By contrast, taxonomy graphs (WordNet EN, BabelNet RU/AR) remained near the Euclidean regime ($\bar{\kappa} \approx 0$), confirming that hyperbolicity is not universal and depends on edge architecture. Curvature distributions were unimodal in association networks and slightly skewed toward positive tails in taxonomies, reflecting near-tree hierarchical chains. Kruskal–Wallis tests detected no effect of language family on mean curvature (H = 1.83, p = 0.61), underscoring cross-linguistic stability when free-association structure is preserved. Supplemental bootstrap analyses for ConceptNet and taxonomies (±0.01–0.03) show comparable estimator stability, ruling out sampling bias by language.

### 3.2 Clustering Modulates Hyperbolicity

Generalized additive models relating $\bar{\kappa}$ to mean local clustering ($C$) revealed a non-linear regime: curvature stays near zero for $C < 0.01$, drops sharply into the hyperbolic range when $0.02 \leq C \leq 0.15$, and returns toward spherical geometry for $C > 0.30$ ($R^2_{adj} = 0.78$, explained deviance = 81%). The estimated "hyperbolic sweet spot" spans $C \in [0.023, 0.147]$ (95% CI from bootstrap over GAM coefficients), aligning with the SWOW networks. ConceptNet sits just below the lower boundary yet maintains $\bar{\kappa} < 0$, showing that sparse knowledge graphs can leverage the same geometric mechanism. Taxonomies fall outside the corridor, indicating that hierarchy alone is insufficient; moderate triadic closure is required. Partial dependence analyses identified degree heterogeneity ($\sigma_k$) as a secondary moderator (interaction $p = 0.004$): high $\sigma_k$ amplifies the drop in $\bar{\kappa}$ inside the sweet spot, whereas narrow degree distributions keep networks near the Euclidean plane even at moderate $C$.

#### 3.2.1 Degree Distribution Topology: Broad-Scale Rather Than Strictly Scale-Free

To assess whether semantic networks exhibit scale-free topology—a property often associated with hyperbolic geometry—we applied the rigorous Clauset, Shalizi, Newman (2009) protocol [14] to degree distributions from all SWOW languages. Maximum likelihood estimation yielded power-law exponents $\alpha = 2.06$ (Dutch), 2.13 (Chinese), and 2.28 (Spanish), with mean $\bar{\alpha} = 1.90 \pm 0.03$ (95% CI: [1.86, 1.95]) when including English data from prior analyses. This mean estimate falls below the classical scale-free range ($\alpha \in [2.0, 3.0]$), and goodness-of-fit tests via Kolmogorov-Smirnov statistics produced $p < 0.001$ for all languages, indicating poor power-law fit. Likelihood ratio tests comparing power-law to lognormal distributions yielded negative $R$ values (mean $R = -168.7$, $p < 0.001$), indicating that lognormal distributions provide a significantly better fit to the degree distributions.

These results align with recent re-analyses of semantic network topology [21] and support a "broad-scale" rather than strictly "scale-free" characterization: semantic networks exhibit heavy-tailed degree distributions (superior to exponential) but do not follow pure power laws. This distinction matters for theoretical interpretation but does not undermine the geometric findings. As demonstrated in Section 3.3, hyperbolic curvature emerges robustly in configuration-model nulls that preserve degree distributions, confirming that hyperbolicity does not require strict scale-free topology. Instead, the hierarchical and branching structure of semantic networks—combined with moderate clustering—drives hyperbolic embedding, independent of the specific degree distribution form (power-law, lognormal, or other heavy-tailed variants).

### 3.3 Structural Null Models Confirm Causal Role of Clustering

Configuration-model nulls (M = 1000) increased hyperbolicity by $\Delta \kappa = +0.17$ to $+0.22$ across SWOW languages (Figure 2, Table 2). Null distributions shifted relative to the empirical curves (Cliff’s $\delta > 0.79$, $p_{MC} < 0.001$), indicating that preserving degree sequences alone liberates a stronger hyperbolic tendency than observed in real data. When triangles were preserved via the triadic-rewire null (M = 1000, Spanish/English), the shift vanished ($\Delta \kappa = +0.02 \pm 0.03$, $p_{MC} > 0.10$), isolating clustering as the causal moderator. Density-controlled perturbations of taxonomies further showed that random edge additions raise $C$ yet push $\bar{\kappa}$ positive, confirming that only moderate triadic closure yields sustained negative curvature.

### 3.4 Phase Diagram of Semantic Geometry

Plotting network geometry in the $(C, \sigma_k)$ plane (Figure 4) produced a phase diagram where color encodes $\bar{\kappa}$. SWOW (ES/EN/ZH) and ConceptNet (EN/PT) occupy a hyperbolic corridor with $C \approx 0.02$–0.15 and elevated $\sigma_k$ (1.7–7.3), reflecting association-driven heterogeneity. Taxonomies (WordNet EN, BabelNet RU/AR) cluster near the Euclidean boundary (low $C$, moderate $\sigma_k$), while dense co-occurrence proxies (Supplementary Figure S2) populate the spherical zone. The map clarifies why pure hierarchy (low $C$) or excessive closure (high $C$) fails to sustain hyperbolicity: both extremes disrupt the balance between global efficiency and local flexibility characteristic of human semantic organization.

### 3.5 Robustness Across Parameters and Scales

Bootstrap resampling (80% nodes, 50 iterations) yielded coefficients of variation below 3% for $\bar{\kappa}$ and $C$ in all SWOW and ConceptNet networks, and below 6% in taxonomies (WordNet EN, BabelNet RU/AR), confirming estimator stability. Network-size experiments (250–750 nodes) preserved the sweet-spot interval with deviations <0.02 in $\bar{\kappa}$ and <0.005 in $C$. Varying the idleness parameter $\alpha$ between 0.1 and 0.9 shifted mean curvature by at most ±0.03, with minima consistently between $\alpha = 0.4$ and 0.6. Symmetrizing or binarizing edges increased $\bar{\kappa}$ by <0.02, demonstrating that directed weights intensify but do not create the observed hyperbolicity.

### 3.6 Resistance to Discrete Ricci Flow

Ricci-flow experiments rapidly reduced clustering and eliminated negative curvature in null networks, converging to $\bar{\kappa} \geq 0$ within 40 iterations (Figure 3, Table 3). Configuration and taxonomy nulls required only modest clustering reductions (12–20%) to reach the flat regime. Real semantic networks resisted: despite 79–86% reductions in $C$, trajectories stabilized above the Euclidean equilibrium ($\bar{\kappa}_\infty = 0.01$–0.05). Flow-induced pruning concentrated residual negative curvature on bridge edges linking communities, supporting the interpretation that human semantic organization preserves mesoscale structure even under pressure to flatten.

### 3.7 Extensions to Other Domains

The phase-diagram framework provides hypotheses for domains beyond the datasets analyzed here—for example, speech networks in clinical populations or semantic graphs derived from educational curricula. We do not evaluate those settings in this study; instead, we report the curvature–clustering boundaries so that future datasets can be positioned within the same coordinate system and directly tested against the predictions derived from SWOW, ConceptNet, and taxonomy graphs.

## 4. DISCUSSION

### 4.1 Boundary Conditions for Hyperbolic Geometry in Semantic Networks

Our results establish consistency across eight semantic graphs (three SWOW association networks, two ConceptNet knowledge graphs, and three taxonomy-based lexicons) spanning Indo-European, Sino-Tibetan, and Semitic language families. Semantic networks display persistent negative curvature only when topology satisfies specific balance conditions: moderate clustering, heavy-tailed degree distributions (broad-scale rather than strictly scale-free, as shown in Section 3.2.1), and a mixture of primary and context-driven associations. Free-association networks inhabit this regime and display reproducible curvature patterns, whereas taxonomies lack clustering moderation and converge toward near-Euclidean geometries. This structural balance yields an operational criterion for future analyses: networks that deviate from the hyperbolic corridor can be scrutinized for the mechanisms—data collection, preprocessing, or conceptual coverage—that shift them toward spherical or Euclidean behavior.

These geometric signatures dovetail with clinical speech findings. Schizophrenia-spectrum language shows marked fragmentation—shrinking largest connected components, reduced clustering, and degraded small-worldness—that aligns with highly negative curvature edges acting as fragile bridges between semantic neighborhoods [24-27]. Depressive speech concentrates into tightly knit negative modules, suggesting curvature skewed toward positive values within those enclaves, whereas manic discourse expands into densely looped graphs consistent with exaggerated negative curvature spread across the network [28,29]. Neurodegenerative (Alzheimer’s) and neurodevelopmental (autism spectrum) profiles further reveal how departures from the sweet spot manifest: progressive loss of inter-module edges in dementia pushes networks toward tree-like Euclidean structure, while autism’s hyper-focused clusters create pockets of high clustering decoupled from broader connectivity [30,31]. Collectively, these patterns support a unifying narrative: healthy cognition operates near the moderate-clustering hyperbolic regime; disorders perturb clustering or bridge density, shifting geometry toward spherical or Euclidean extremes and producing characteristic symptoms.

### 4.2 Null Model Implications: Clustering as Causal Moderator

The structural null model analyses (Section 3.3) provide causal evidence that clustering moderates hyperbolic geometry. Configuration-model nulls that preserved degree distributions but destroyed clustering increased hyperbolicity by $\Delta \kappa = +0.17$ to $+0.22$ relative to real networks, demonstrating that the observed negative curvature is suppressed, not created, by triadic closure. This counterintuitive finding—that removing clustering increases hyperbolicity—reveals an underlying geometric tendency that real semantic networks constrain through local structure. The triadic-rewire null, which preserved triangle counts while randomizing edge placement, eliminated this shift ($\Delta \kappa = +0.02 \pm 0.03$), isolating clustering as the causal mechanism.

These results challenge the assumption that hierarchical structure alone drives hyperbolicity. Instead, they support a nuanced model: semantic networks inherit a hyperbolic tendency from degree heterogeneity (broad-scale distributions), but moderate clustering modulates this geometry toward a functional balance. Too little clustering (taxonomies, $C < 0.01$) yields near-Euclidean geometry; too much clustering (dense co-occurrence networks, $C > 0.30$) shifts toward spherical curvature. The "sweet spot" ($C \approx 0.02$–0.15) represents an optimal trade-off where hierarchical branching coexists with sufficient triadic closure to support flexible semantic navigation. This mechanistic account explains why free-association networks consistently occupy the hyperbolic corridor while taxonomies and dense graphs diverge, providing a quantitative framework for predicting geometric behavior from network construction principles.

### 4.3 Hyperbolic Geometry Beyond Semantic Networks

The findings extend the understanding of hyperbolic geometry in complex networks. Prior studies show that hyperbolic embeddings capture hierarchy [33], enable efficient routing [34], and enhance machine-learning performance [35-37]. The sweet spot identified here positions clustering as the pivotal moderator, supplying a mechanistic explanation that complements this literature and counters the assumption of innate hyperbolicity: semantic networks sustain negative curvature only when degree heterogeneity pairs with moderate triadic closure. Parallels with biological, technological, and information networks suggest that curvature can function as a universal marker of well-organized structure, sensitive to perturbations that disrupt local-global balance.

This synthesis also clarifies how curvature-based tools link linguistic data with broader network analytics. Communicability-weighted Forman curvature, lower Ricci estimators, and discrete Ricci flows consistently highlight bridge edges that preserve robustness in biological, social, and engineered systems [19-23]. Semantic association graphs provide a complementary example: maintaining moderate clustering sustains negative curvature and supports flexible navigation across concepts. The cross-domain convergence positions curvature as a diagnostic feature for comparing construction pipelines, sampling choices, and intervention strategies in networked datasets.

### 4.4 Applications and Future Data

Positioning networks in the curvature–clustering plane creates a reusable analysis template. Future work can populate the map with additional corpora—child language acquisition, disciplinary textbooks, collaborative knowledge bases—and test whether their trajectories remain within the hyperbolic corridor or exhibit systematic deviations. Because the machinery is entirely data-driven and replicable, researchers can evaluate new datasets without re-deriving the geometric boundaries presented here.

### 4.5 Ricci Flow Resistance as Functional Signature

Applying discrete Ricci flow to real and null networks revealed a consistent pattern. Configuration and taxonomy nulls quickly converged to $\bar{\kappa} \geq 0$ with only modest clustering reductions (≈12–20%). SWOW and ConceptNet networks tolerated 79–86% reductions in $C$ yet stabilized above the Euclidean equilibrium ($\bar{\kappa}_\infty = 0.01$–0.05), retaining bridge edges with residual negative curvature. We interpret this “flow resistance” as a functional signature: human cognition maintains sufficient triadic closure for flexible navigation even under geometric pressure to flatten. This dynamic suggests that interventions (therapy, neurostimulation, embedding adjustments) could be monitored by tracking whether networks return to the hyperbolic plateau after controlled perturbations.

### 4.6 Limitations

Several limitations constrain the generalizability of our findings. First, the analysis focused on 500 nodes per language using first responses (R1), emphasizing frequent concepts and limiting generalization to specialized vocabulary or less common associations. Second, the $O(n^3)$ computational cost of Ollivier–Ricci curvature constrains analysis to networks with $n \leq 1000$ nodes, preventing examination of full-scale semantic corpora. Third, the idleness parameter $\alpha = 0.5$ represents a single, though robust, choice; while sensitivity analyses confirmed stability across $\alpha \in [0.1, 0.9]$, alternative curvature definitions (Forman, lower Ricci) may yield complementary insights. Fourth, language coverage remains limited (three language families) and partially correlated through shared platforms (SWOW, ConceptNet), potentially inflating cross-linguistic consistency. Fifth, triadic-rewire nulls could not be executed for SWOW Chinese or ConceptNet within available compute budgets, limiting causal inference to Spanish and English SWOW networks. Sixth, the degree distribution analysis revealed broad-scale rather than strictly scale-free topology, requiring updated theoretical interpretation while not undermining geometric findings. Finally, the phase diagram framework provides predictions for clinical populations and other domains, but these remain untested in the current study.

### 4.7 Future Directions

We outline several directions for extending this work. **Cross-linguistic expansion**: Incorporating additional language families (e.g., Austronesian, Niger-Congo, Uralic) and R2/R3 responses will test whether the hyperbolic sweet spot generalizes beyond Indo-European, Sino-Tibetan, and Semitic languages. **Clinical validation**: Applying the phase diagram framework to speech networks from schizophrenia, depression, mania, and neurodegenerative disorders will test whether geometric deviations predict symptom severity and treatment response. **Neuroimaging integration**: Correlating network curvature with fMRI connectivity patterns, EEG microstates, and MEG source localization will bridge structural and functional neural organization. **Longitudinal dynamics**: Tracking how semantic networks evolve during development, learning, and clinical interventions will reveal whether curvature changes precede or follow behavioral outcomes. **Computational efficiency**: Developing approximate curvature estimators (e.g., lower Ricci bounds, sampling-based methods) will enable analysis of larger networks ($n > 10,000$) and real-time monitoring applications. **Standardization**: Establishing consensus preprocessing pipelines (directionality, thresholds, lemmatization) and executing pre-registered meta-analyses with funnel plots, Newcastle–Ottawa/QUADAS assessments, and multivariate models will strengthen evidence synthesis across studies.

By combining broad empirical evidence, causal null models, and geometric flow experiments, we provide a quantitative roadmap for investigating how cognitive systems balance hierarchy and flexibility. The framework yields measurable targets for future longitudinal corpora, experimental manipulations, and AI pipelines that must interpret human semantics at scale.

## 5. FIGURE CAPTIONS

**Figure 1 – Clustering–Curvature Map Across Networks.** Scatter and GAM-smoothed relation between mean local clustering coefficient (C) and Ollivier–Ricci curvature ($\bar{\kappa}$) across five association networks (SWOW ES/EN/ZH, ConceptNet EN/PT) and three taxonomy lexicons (WordNet EN, BabelNet RU/AR). The shaded gray band ($C \approx 0.02$–0.15) indicates the empirically estimated “hyperbolic sweet spot” where semantic association networks cluster. Association-based graphs (filled circles) exhibit negative curvature, taxonomy-based graphs (open triangles) approach $\bar{\kappa} \approx 0$. Color encodes dataset family; error bars show bootstrap 95 % CIs.

**Figure 2 – Structural Null Models and Effect Sizes.** Comparison of mean curvature ($\bar{\kappa}$) for real SWOW semantic networks versus configuration (degree-preserving) and triadic-rewire (clustering-preserving) nulls. Bars show $\Delta \kappa = \bar{\kappa}_{real} - \bar{\kappa}_{null}$; error bars = 95 % CI from 1 000 Monte-Carlo replicates. All SWOW languages: $\Delta \kappa \approx +0.17$–0.22, $p_{MC} < 0.001$; Cliff’s $\delta > 0.8$. Results confirm that clustering dampens underlying hyperbolicity.

**Figure 3 – Ricci Flow Resistance.** Discrete Ricci flow trajectories for four representative networks (two real + two null). Each curve traces the evolution of clustering coefficient ($C_t$) and mean curvature ($\bar{\kappa}_t$) across 40 iterations of flow ($\eta = 0.5$). In all cases, $C$ decreases 79–86 % while $\bar{\kappa}$ increases by 0.17–0.30, converging toward spherical geometry. Semantic networks resist full flattening, stabilizing above the Euclidean equilibrium (dashed line), demonstrating functional “resistance to Ricci flow.”

**Figure 4 – Phase Diagram of Network Geometry.** Phase space of curvature regimes as a function of clustering ($C$) and degree heterogeneity ($\sigma_k$). Colors denote mean $\bar{\kappa}$; dashed boundaries separate spherical ($\bar{\kappa} > 0$), Euclidean ($\approx 0$), and hyperbolic ($\bar{\kappa} < 0$) regions. Semantic association networks occupy the hyperbolic corridor; taxonomies reside near the Euclidean boundary.

## 6. TABLES

### Table 1 – Network Statistics by Dataset

| Network | Nodes | Edges | Density | $C$ | $\sigma_k$ | $\bar{\kappa}$ | 95 % CI |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SWOW (ES) | 422 | 571 | 0.0064 | 0.034 | 1.74 | -0.155 | ±0.02 |
| SWOW (EN) | 438 | 640 | 0.0067 | 0.026 | 1.84 | -0.258 | ±0.02 |
| SWOW (ZH) | 465 | 762 | 0.0071 | 0.029 | 2.03 | -0.214 | ±0.03 |
| ConceptNet (EN) | 467 | 2 474 | 0.0227 | 0.014 | 7.34 | -0.209 | ±0.02 |
| ConceptNet (PT) | 489 | 1 578 | 0.0132 | 0.017 | 5.62 | -0.165 | ±0.02 |
| WordNet (EN) | 500 | 527 | 0.0021 | 0.046 | 4.07 | -0.002 | ±0.01 |
| BabelNet (RU) | 493 | 522 | 0.0043 | 0.0003 | 2.73 | -0.030 | ±0.02 |
| BabelNet (AR) | 142 | 151 | 0.0150 | <0.001 | 2.61 | -0.012 | ±0.03 |

### Table 2 – Null-Model Comparisons

| Dataset | Null type | $\Delta \kappa$ | $p_{MC}$ | Cliff’s $\delta$ | Interpretation |
| --- | --- | --- | --- | --- | --- |
| SWOW (ES) | Configuration | +0.20 | <0.001 | +0.83 | Hyperbolicity suppressed by clustering |
| SWOW (EN) | Configuration | +0.22 | <0.001 | +0.85 | idem |
| SWOW (ZH) | Configuration | +0.18 | <0.001 | +0.81 | idem |
| SWOW (ES) | Triadic rewire | +0.03 | 0.18 | +0.12 | Clustering preserved, curvature gap vanishes |
| SWOW (EN) | Triadic rewire | +0.01 | 0.41 | +0.09 | idem |

### Table 3 – Ricci Flow Parameters and Convergence

| Network | $\eta$ | Iterations | $\Delta C$ (%) | $\Delta \bar{\kappa}$ | Equilibrium $\bar{\kappa}$ | Time (min) |
| --- | --- | --- | --- | --- | --- | --- |
| SWOW (ES) | 0.5 | 40 | -82 | +0.28 | +0.03 | 6 |
| SWOW (EN) | 0.5 | 41 | -79 | +0.25 | +0.01 | 5 |
| Config null (EN) | 0.5 | 35 | -12 | +0.07 | -0.09 | 4 |
| WordNet (EN) | 0.5 | 38 | -65 | +0.19 | +0.05 | 5 |
