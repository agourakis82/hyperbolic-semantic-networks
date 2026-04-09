# Entropic Curvature in Hyperbolic Semantic Manifolds Indexes Psychopathology-Like Transitions

## Abstract

[PLACEHOLDER: Replace with the abstract derived from `results/cpc2026/ossm_statistical_summary.json`; results reported here supersede the projections in the accepted conference abstract.]

Paragraph 1 topic sentence: This paper introduces entropic curvature as a node-level geometric marker on the validated SWOW-EN semantic graph and tests whether simulated cognitive regimes separate along that landscape.

Paragraph 2 topic sentence: Using Ollivier-Ricci curvature, local transition entropy, and regime-specific semantic trajectory simulations, we quantify variance, residence time, entropy production, and long-range temporal structure across normative and pathology-like conditions.

Paragraph 3 topic sentence: The revised journal abstract must replace the poster-era projected numbers with the observed O-SSM-aware results and explicitly note when the full-paper values supersede the accepted conference abstract.

## Introduction

### 1. Geometric biomarkers remain underdeveloped in computational psychiatry

Topic sentence: Computational psychiatry has rich dynamical models of instability, rumination, and divergent thought, but it still lacks graph-geometric biomarkers that are interpretable at the level of local semantic structure.

[PLACEHOLDER: Review attractor-based, predictive-processing, active-inference, and network-psychopathology approaches.]

### 2. Semantic networks offer a natural substrate for psychiatric regime simulations

Topic sentence: Word-association graphs capture the mesoscale organization of semantic memory and provide a principled substrate for simulating exploration, trapping, and divergence in conceptual space.

[PLACEHOLDER: Position SWOW, speech-graph methods, and semantic network science.]

### 3. Hyperbolic geometry and Ollivier-Ricci curvature quantify local semantic structure

Topic sentence: Prior work in this repository established that semantic networks occupy a hyperbolic corridor governed by degree density and clustering, making curvature a natural local descriptor of semantic accessibility.

[PLACEHOLDER: Cite the repository's cross-linguistic ORC results and the validated phase-transition reference.]

### 4. Entropic curvature extends local geometry with transition uncertainty

Topic sentence: We define entropic curvature as the product of local Ollivier-Ricci curvature and one minus normalized transition entropy, yielding a node-wise index that penalizes diffuse neighborhoods while preserving geometric sign.

[PLACEHOLDER: Motivate interpretability and relation to uncertainty, branching, and hub structure.]

### 5. The present paper tests regime shifts in simulated semantic trajectories

Topic sentence: We evaluate whether normative, anxious, ruminative, and psychotic-like semantic trajectories separate on the entropic-curvature landscape and whether those separations generate clinically meaningful hypotheses for neuroimaging and ecological monitoring.

[PLACEHOLDER: State explicit hypotheses and paper roadmap.]

## Methods

### 2.1 Graph Construction: SWOW-EN

Topic sentence: All CPC analyses use the repository's validated sparse SWOW-EN graph, derived from `english_edges_FINAL.csv` and restricted to its largest connected component for compatibility with the exact-LP curvature artifact.

[PLACEHOLDER: Report node/edge counts, weighting scheme, largest-component restriction, and preprocessing provenance.]

### 2.2 Ollivier-Ricci Curvature

Topic sentence: Node-level curvature was derived from the validated exact-LP edge curvatures produced by the Julia reference pipeline, with a Python GraphRicciCurvature cross-check retained as a quality-control diagnostic.

[PLACEHOLDER: Specify alpha, exact artifact path, and node-wise aggregation rule.]

### 2.3 Entropic Curvature Definition

Topic sentence: For each node, local transition entropy was computed from normalized outgoing edge weights and combined with mean incident-edge curvature to define `C_ent(v) = κ_local(v) * (1 - H(v) / log(deg(v)))`.

[PLACEHOLDER: Clarify the degree-1 convention and the rationale for entropy normalization.]

### 2.4 Valence Annotation

Topic sentence: Warriner et al. (2013) affective norms were merged to SWOW-EN lemmas by lowercase exact matching, with unmatched nodes assigned neutral valence and coverage reported explicitly.

[PLACEHOLDER: Insert exact coverage from `results/cpc2026/valence_coverage.json`.]

### 2.5 Cognitive Trajectory Simulation

#### 2.5.1 Primary engine: biased Markov chain on the graph

Topic sentence: The primary quantitative engine is a weighted graph walk whose transition probabilities combine edge strength, temperature-dependent entropy penalty, and optional negative-valence priming.

[PLACEHOLDER: Insert the exact formula used in `trajectory_simulator.py` and the default parameter table.]

#### 2.5.2 Exploratory engine: Langevin-like dynamics on disk coordinates

Topic sentence: A companion exploratory engine evolves continuous positions on a cached 2D disk embedding under stochastic drift tied to local entropic curvature before snapping positions back to the nearest graph node.

[PLACEHOLDER: Emphasize that this engine is exploratory unless it is used directly in reported quantitative claims.]

#### 2.5.3 Exploratory engine: hybrid graph-plus-disk dynamics

Topic sentence: A hybrid engine interleaves graph-constrained jumps with continuous relaxation on the embedding, providing a bridge between discrete and continuous semantic dynamics.

[PLACEHOLDER: Document whether this engine contributes to the final paper or remains supplementary.]

#### 2.5.4 Octonionic State Space Model

Topic sentence: We complement the memoryless Markov baseline with an octonionic state space model whose hidden state evolves by non-associative composition, allowing persistent attractor structure and context-sensitive trajectory modulation.

[PLACEHOLDER: Insert the state update equation `h_{t+1} = sigma(A h_t B + C x_t)` in paper notation and define the 8D node input vector.]

#### 2.5.5 Regime parametrization in the O-SSM

Topic sentence: In the O-SSM, regime differences are encoded through temperature, initial-state geometry, and valence gating rather than solely through the graph transition kernel, enabling path dependence without introducing supervised fitting.

[PLACEHOLDER: Document balanced, negative-attractor, rigid, and dispersed initial states; report that the first pass uses structured deterministic weights rather than trained parameters.]

#### 2.5.6 Canonical Sounio implementation and Python full-artifact mirror

Topic sentence: Because the canonical `sounio-lang/sounio` checkout provides validated octonion arithmetic but not a full benchmark-recovered O-SSM package, we pair a runnable Sounio implementation for executable parity with a Python reference engine that generates the full paper-scale artifacts.

[PLACEHOLDER: Clarify which figures/statistics come from the Python full run and which Sounio outputs currently serve as parity/smoke validation.]

### 2.6 Statistical Analysis

Topic sentence: We quantified trajectory-level variance in entropic curvature, residence time in high-entropy hubs, entropy production rate, and Hurst exponents estimated by detrended fluctuation analysis.

[PLACEHOLDER: Insert bootstrap count, effect-size definitions, p-value tests, and trajectory-level summary table.]

### 2.7 O-SSM-Specific Dynamical Metrics

Topic sentence: For the octonionic model we additionally quantified associator norm, hidden-state entropy, quaternionic subspace occupancy across the seven Fano-plane triples, and recurrence-based attractor diagnostics.

[PLACEHOLDER: Define the associator norm, occupancy rule, and recurrence thresholds used in `ossm_analysis.py`.]

### 2.8 Cross-Model Comparison

Topic sentence: Markov and O-SSM outputs were compared side by side to determine which regime contrasts survive a memoryful dynamical model and which remain inherited from the common input trajectories.

[PLACEHOLDER: Insert the comparison table specification and explain any metric-definition asymmetries.]

### 2.9 Phase-Transition Reference

Topic sentence: The generic geometric phase transition near `⟨k⟩²/N ≈ 2.5` was taken from the repository's validated random-regular reference curve and used only as a contextual geometry baseline, not as a property of the sparse SWOW-EN substrate itself.

[PLACEHOLDER: Clarify the distinction between generic graph geometry and simulated psychiatric regimes on SWOW-EN.]

### 2.10 Code and Data Availability

Topic sentence: All CPC-specific code resides in `code/cpc2026/`, with outputs in `results/cpc2026/` and figures in `figures/cpc2026/`, enabling exact regeneration from the repository root.

[PLACEHOLDER: Add DOI/release language if a CPC-specific release is minted.]

## Results

### 3.1 Node-level entropic curvature maps the validated SWOW-EN manifold

Topic sentence: The SWOW-EN substrate shows a heterogeneous distribution of local curvature and transition entropy, yielding a nontrivial entropic-curvature landscape rather than a simple degree proxy.

[PLACEHOLDER: Insert descriptive statistics for node-level `kappa`, `entropy`, and `C_ent`.]

### 3.2 Regime-specific trajectories separate in entropic-curvature variance

Topic sentence: Trajectory-level variance in `C_ent` distinguishes the simulated regimes, providing the direct comparison needed to evaluate the poster's large-effect claim.

[PLACEHOLDER: Insert observed Cohen's d, confidence interval, and p-value.]

### 3.3 Pathology-like regimes alter residence time in high-entropy hubs

Topic sentence: The anxious and ruminative conditions spend systematically different amounts of time in top-entropy hubs, indicating altered exploration of semantically diffuse neighborhoods.

[PLACEHOLDER: Insert the observed percent change and uncertainty interval.]

### 3.4 Temporal structure diverges across regimes

Topic sentence: Hurst exponents estimated from `C_ent` time series reveal whether pathology-like regimes exhibit weaker long-range persistence or more fragmented fluctuations than the normative baseline.

[PLACEHOLDER: Insert boxplot interpretation and actual mean/CI values.]

### 3.5 The SWOW-EN substrate sits far below the generic geometric transition

Topic sentence: Although the repository's validated random-regular reference crosses curvature zero near `⟨k⟩²/N ≈ 2.5`, the sparse SWOW-EN graph itself remains deep in the subcritical hyperbolic regime.

[PLACEHOLDER: Insert `swow_eta`, reference `eta_c`, and interpretive sentence about substrate vs regime dynamics.]

### 3.6 The O-SSM introduces structured non-associative regime fingerprints

Topic sentence: Once persistent octonionic state is added, the regimes differ not only in output variability but also in associator activation, hidden-state entropy, and occupation of specific quaternionic subspaces.

[PLACEHOLDER: Insert the main associator and subspace occupancy findings, including whether pathological regimes activate stronger non-associativity.]

### 3.7 Markov and O-SSM models diverge in what they separate

Topic sentence: Cross-model comparison shows which findings are inherited from the shared graph input walk and which emerge only after adding memoryful octonionic state dynamics.

[PLACEHOLDER: Insert the side-by-side table and summarize whether the O-SSM increases, decreases, or qualitatively reorganizes regime separation.]

## Discussion

### 4.1 Entropic curvature as an interpretable semantic instability marker

Topic sentence: Entropic curvature combines local geometry and neighborhood uncertainty into a single scalar that is easier to interpret psychologically than curvature or entropy alone.

[PLACEHOLDER: Explain how positive, near-zero, and negative values map onto semantic accessibility and branching.]

### 4.2 Relation to existing computational psychiatry models

Topic sentence: The simulated regime shifts can be read alongside attractor-depth, stochastic search, and predictive-processing accounts of anxiety, rumination, and psychosis-like thought.

[PLACEHOLDER: Link the CPC outputs to computational psychiatry theory without overstating simulation realism.]

### 4.3 Clinical predictions for fMRI, EEG, and EMA

Topic sentence: If entropic curvature captures meaningful instability in semantic exploration, then speech-derived semantic trajectories should predict measurable alterations in cortical variability, temporal autocorrelation, and ecological symptom fluctuation.

[PLACEHOLDER: State concrete, testable predictions for fMRI, EEG, and EMA.]

### 4.4 Limitations

Topic sentence: The current study is a simulation study on a normative semantic substrate, not a patient dataset, so any psychiatric interpretation must remain explicitly hypothesis-generating.

[PLACEHOLDER: Cover valence matching limitations, embedding approximations, and model-selection caveats.]

### 4.5 Future directions

Topic sentence: The next empirical step is to align semantic trajectories with clinical speech graphs and brain-network geometry, potentially extending into the repository's FSNN, hypercomplex, and formalized Sounio branches.

[PLACEHOLDER: Mention planned validation against real speech or neuroimaging data.]

### 4.6 Non-associativity as a cognitive mechanism

Topic sentence: The associator term makes precise the idea that affective-semantic composition is order-sensitive, so `(fear ∘ anger) ∘ sadness` need not occupy the same cognitive basin as `fear ∘ (anger ∘ sadness)`.

[PLACEHOLDER: Connect the associator interpretation to compositional cognition, the O-SSM benchmark paper, and explicit caveats about mechanistic overreach.]

## References

Topic sentence: The final reference list should be compiled from `manuscript/references.bib`, augmented with any computational psychiatry, DFA, and affective-norm citations added during drafting.

[PLACEHOLDER: Cite from `manuscript/references.bib`; do not duplicate final BibTeX inline here.]
