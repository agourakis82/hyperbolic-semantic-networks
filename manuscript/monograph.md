# When Are Semantic Networks Hyperbolic? A Curvature Phase Transition Theory with Cross-Linguistic Validation

**Demetrios C. Agourakis**$^{1}$

$^1$ Independent Researcher
ORCID: 0000-0002-8596-5097

**Correspondence**: demetrios@agourakis.med.br

**Date**: February 2026

---

## Abstract

Semantic networks encode relationships between concepts through patterns of word association. Whether these networks exhibit hyperbolic geometry—and why—remains an open question with implications for cognitive architecture and network embedding. We present an empirically supported two-parameter model that combines (i) a curvature sign change in random graphs with (ii) analysis of 11 semantic networks across five languages and one clinical dataset.

Using exact linear programming to compute Ollivier-Ricci curvature (eliminating Sinkhorn regularization bias), we find that the density parameter $\eta = \langle k \rangle^2 / N$ is necessary but not sufficient for predicting hyperbolicity. Random $k$-regular graphs undergo a sign change in mean curvature $\bar{\kappa}$ at a critical density $\eta_c(N) = 3.75 - 14.62/\sqrt{N}$ ($R^2 = 0.995$, $N \in \{50, 100, 200, 500, 1000\}$). All semantic networks except Dutch SWOW fall below this threshold ($\eta \ll \eta_c$), yet taxonomies (WordNet, BabelNet) are near-Euclidean while association networks (SWOW, ConceptNet) are hyperbolic. A second parameter, the clustering coefficient $C$, separates these: networks with $C > 0.10$ are hyperbolic ($\bar{\kappa} \in [-0.24, -0.07]$), those with $C < 0.02$ are Euclidean ($\bar{\kappa} \approx 0$), and those with $\eta > \eta_c$ are spherical ($\bar{\kappa} > 0$). The clustering threshold ($C^* \approx 0.05$) is empirical and requires validation on additional datasets.

Dutch SWOW ($\eta = 7.56 \gg \eta_c = 3.10$) is spherical ($\bar{\kappa} = +0.10$), confirming the sign-change prediction. Sphere-embedded ORC across the Cayley-Dickson tower ($S^3$, $S^7$, $S^{15}$) flips 10 of 11 networks to positive curvature at $d = 4$ and all 11 by $d = 8$, demonstrating that semantic hyperbolicity is entirely metric-dependent—an artifact of the hop-count metric, not an intrinsic topological property. Degree-matched null models show that semantic organization makes networks *less* hyperbolic than random graphs with the same degree, the opposite of naive expectation. A Lean 4 formalization (25 modules, 0 `sorry` in 7 core ORC-theory modules) provides machine-checked proofs of Wasserstein non-negativity, curvature bounds, and regime exclusivity.

**Keywords**: semantic networks, Ollivier-Ricci curvature, phase transition, hyperbolic geometry, clustering coefficient, cross-linguistic, formal verification

---

## 1. Introduction

### 1.1 Background

Semantic memory—the structured knowledge of concepts and their relationships—is fundamental to human cognition. Network science offers a quantitative lens on this organization, treating words as nodes and associations as edges to uncover small-world structure, modularity, and degree heterogeneity. Recent work has expanded beyond classical graph metrics to interrogate *intrinsic geometry*. Hyperbolic spaces, in particular, naturally accommodate hierarchical growth and heterogeneous branching—properties observed in semantic association datasets. Yet most evidence for hyperbolicity in language has been indirect, relying on embeddings or curvature heuristics rather than explicit geometric measurement.

### 1.2 The Open Question

Two questions have remained separate in the literature:

1. **Empirical**: Do semantic networks exhibit hyperbolic geometry? Is this universal across languages?
2. **Theoretical**: Why should some networks be hyperbolic and not others? What are the boundary conditions?

Prior work addressed these independently. Empirical studies applied Ollivier-Ricci curvature to specific datasets and found hyperbolicity in some but not all networks. Theoretical studies established sign changes in discrete curvature for random graph models. No work has connected the two: using the theoretical phase transition to *predict* which real networks should be hyperbolic.

### 1.3 Our Contribution

We present an empirical framework that connects random graph sign changes with semantic network geometry:

1. **Two-parameter empirical model**: On 11 networks, hyperbolicity is associated with both (a) density parameter $\eta = \langle k \rangle^2 / N$ below the critical threshold $\eta_c(N)$, and (b) sufficient clustering ($C \gtrsim 0.10$). Neither alone is sufficient. The clustering threshold is empirical ($n = 11$) and requires out-of-sample validation.

2. **Exact LP computation**: We compute Ollivier-Ricci curvature for 11 networks using exact linear programming (JuMP + HiGHS), replacing the Sinkhorn approximation used in prior work. This eliminates entropy regularization bias entirely.

3. **Cross-linguistic validation**: We analyze networks spanning Spanish, English, Chinese, Dutch, Portuguese, Russian, and Arabic, covering association networks (SWOW), knowledge graphs (ConceptNet), and taxonomies (WordNet, BabelNet), plus a clinical depression severity dataset.

4. **Dutch SWOW as phase transition confirmation**: The dense Dutch SWOW network ($\eta = 7.56$) falls above the critical threshold and is spherical ($\bar{\kappa} = +0.10$), confirming the phase transition prediction in the opposite direction.

5. **Metric dependence of hyperbolicity**: Sphere-embedded ($S^{d-1}$) transport cost flips 10/11 networks at $d = 4$ and all 11 by $d = 8$, demonstrating that ORC-based hyperbolicity is an artifact of the hop-count metric, not an intrinsic topological property.

6. **Lean 4 formalization**: 25 modules with machine-checked proofs in the 7 core ORC-theory modules (0 `sorry` statements), providing formal verification of the mathematical foundations.

---

## 2. Theory: Phase Transition in Discrete Curvature

### 2.1 Ollivier-Ricci Curvature

For an edge $(u,v)$ in a graph $G$:

$$\kappa(u,v) = 1 - \frac{W_1(\mu_u, \mu_v)}{d(u,v)}$$

where $\mu_u = \alpha \delta_u + (1-\alpha) \cdot \text{Uniform}(N(u))$ is the probability measure with idleness $\alpha = 0.5$, and $W_1$ is the Wasserstein-1 distance (Earth Mover's Distance). The sign of $\kappa$ classifies local geometry: $\kappa < 0$ (hyperbolic), $\kappa = 0$ (flat), $\kappa > 0$ (spherical).

We compute $W_1$ via exact linear programming:

$$\min \sum_{i,j} d_{ij} \gamma_{ij} \quad \text{s.t.} \quad \sum_j \gamma_{ij} = \mu_i, \quad \sum_i \gamma_{ij} = \nu_j, \quad \gamma_{ij} \geq 0$$

using the JuMP modeling language with the HiGHS solver. This eliminates the entropy regularization bias of the Sinkhorn approximation (which we quantify as $|\Delta\kappa| < 0.015$ for random graphs).

### 2.2 Phase Transition in Random Regular Graphs

For random $k$-regular graphs on $N$ vertices, the mean curvature $\bar{\kappa}$ undergoes a sign change at a critical density $\eta_c$ where $\eta = k^2/N$:

- **Sparse regime** ($\eta < \eta_c$): $\bar{\kappa} < 0$ (hyperbolic). Tree-like local structure dominates; neighborhoods don't overlap; transport cost is high.
- **Dense regime** ($\eta > \eta_c$): $\bar{\kappa} > 0$ (spherical). Triangle-rich structure dominates; neighborhoods overlap; transport cost is low.

Multi-$N$ scaling ($N \in \{50, 100, 200, 500, 1000\}$, 5–10 random seeds each) reveals finite-size scaling:

$$\eta_c(N) = \eta_c^\infty - \frac{a}{\sqrt{N}}, \quad \eta_c^\infty \approx 3.75, \quad a \approx 14.62, \quad R^2 = 0.995$$

A free-exponent fit gives $\beta = 0.35$ (95% CI $[0.20, 0.53]$), consistent with $\beta = 1/2$. The transition slope at $\eta_c$ scales as $N^{-0.20}$, indicating a crossover rather than a sharp phase transition.

### 2.3 Erdős-Rényi Comparison

Erdős-Rényi $G(N,p)$ graphs with matched expected degree also exhibit the sign change, but at lower critical density ($\eta_c^{\text{ER}} \approx 1.9$ vs. $\eta_c^{\text{reg}} \approx 2.3$ at $N = 100$). Degree heterogeneity shifts the transition, demonstrating that the phase transition is robust across graph models while the critical point depends on the degree distribution.

### 2.4 Prediction for Real Networks

The phase transition theory generates a testable prediction: for a network with $N$ nodes and mean degree $\langle k \rangle$:
- If $\eta = \langle k \rangle^2 / N > \eta_c(N)$, the network should be spherical ($\bar{\kappa} > 0$)
- If $\eta < \eta_c(N)$, the network *can* be hyperbolic but is not guaranteed to be

We test this prediction against 11 real semantic networks.

### 2.5 Semi-Analytical Framework

Hehl et al. [14] provide an explicit formula for ORC on k-regular graphs: for an edge (u,v) with t common neighbors, the Wasserstein-1 distance decomposes into triangle transport (cost 0), exclusive-neighbor matching (cost 1 per matched pair), and unmatched transport (cost 3 via the u-v path). The idleness mass α contributes cost α · 1. This gives:

W₁ = α + (1−α)·n_exc/k · [f_m + 3(1 − f_m)],  κ = 1 − W₁

where n_exc = k − 1 − t is the number of exclusive neighbors per side and f_m = E[|M|]/n_exc is the fraction matched in the random bipartite graph between exclusive neighborhoods.

For the maximum matching size we use the heuristic E[|M|] = n_exc(1 − exp(−η·n_exc/k²)), validated against exact LP computation at N = 1000 (MAE = 0.009, MSE = 9.3 × 10⁻⁵).

**Clustering extension.** In random k-regular graphs, the expected number of common neighbors is t_rand = (k−1)²/(N−1). In real networks with clustering coefficient C, we substitute t = C(k−1), giving n_exc = (1−C)(k−1). Setting κ = 0 yields an analytical phase boundary η_c(N, C) with two key properties:

1. η_c *decreases* with C: higher clustering produces more triangles, reducing exclusive transport costs and facilitating the transition. At C = 0: η_c(∞) ≈ 5.5; at C = 0.10: η_c(∞) ≈ 3.2; at C = 0.20: η_c(∞) ≈ 2.6.
2. η_c *decreases* with N: finite-size effects reduce the boundary, consistent with the empirical scaling.

This provides a mechanistic explanation for why taxonomies (C ≈ 0) are Euclidean: their near-zero clustering places them in a regime requiring very high η for curvature to turn positive, which their sparse structure (η ≪ 1) cannot reach. Association networks (C > 0.10) have a lower η_c barrier but still η ≪ η_c, explaining their hyperbolic curvature. Only Dutch SWOW (η = 7.6 ≫ η_c) crosses the boundary into the spherical regime.

**Caveat.** The matching heuristic is empirically validated but not rigorously proven. The analytical η_c systematically overpredicts the empirical value by ~5–15% (e.g., η_c^anl(1000) = 3.48 vs. η_c^emp(1000) = 3.32), a known consequence of the conservative matching estimate.

---

## 3. Methods

### 3.1 Provenance Table

| Component | Version | Source | Validation |
|-----------|---------|--------|------------|
| Julia implementation | 2.0.0 | `julia/src/HyperbolicSemanticNetworks.jl` | Cross-validated with Python baseline |
| Rust Wasserstein backend | 1.5.0 | `rust/curvature/src/lib.rs` | 10× speedup vs Julia, identical results |
| Sounio epistemic validation | 0.9.0 | `experiments/01_epistemic_uncertainty/phase_transition.sio` | Automatic uncertainty propagation |
| Lean 4 formalization | 2.2.0 | `lean/HyperbolicSemanticNetworks/` | 25 modules, 86 sorry, 3 axioms |
| Exact LP solver | JuMP 1.20 + HiGHS 1.10 | Julia package registry | Eliminates Sinkhorn regularization bias |
| Data preprocessing | SWOW R1 (2023) | https://smallworldofwords.org | Standardized to undirected unweighted LCC |
| Random graph generation | Configuration model | `julia/src/Analysis/NullModels.jl` | Preserves degree distribution, destroys clustering |
| Triadic rewire null | Edge-swap MCMC | `julia/src/Analysis/NullModels.jl` | Preserves triangle counts, isolates clustering effect |
| Discrete Ricci flow | 100 iterations | `julia/src/Analysis/RicciFlow.jl` | Curvature equilibration experiment |
| Statistical testing | Monte Carlo (M=1000) | `julia/src/Analysis/Bootstrap.jl` | p-values via empirical null distribution |

**Code availability**: All analysis code is publicly available at https://github.com/agourakis82/hyperbolic-semantic-networks under MIT license. The repository includes complete documentation, Docker environment, and reproduction instructions.

**Data availability**: SWOW data requires registration at https://smallworldofwords.org. Processed network files (undirected unweighted largest connected components) are included in the repository's `data/processed/` directory. ConceptNet and WordNet data are publicly available from their respective sources.

### 3.2 Datasets

### 3.1 Datasets

We analyze 11 networks spanning four categories:

**Association networks (SWOW)**: Small World of Words R1 cue-response matrices for Spanish ($N = 422$), English ($N = 438$), Chinese ($N = 465$), and Dutch ($N = 500$ in LCC). The top 500 most frequent cue words serve as nodes; directed weighted edges connect cues to responses. Dutch SWOW is notably denser ($\langle k \rangle = 61.5$) than the others ($\langle k \rangle \approx 2.7$–$3.3$).

**Knowledge graphs (ConceptNet)**: ConceptNet 5.7 assertions for English ($N = 467$, $E = 2383$) and Portuguese ($N = 489$, $E = 1578$), filtered to weight $\geq 2.0$ and top 500 concepts.

**Taxonomy networks**: English WordNet 3.1 ($N = 500$, $E = 527$; also $N = 2000$, $E = 2075$), BabelNet 5.3 Russian ($N = 493$, $E = 522$), and BabelNet 5.3 Arabic ($N = 142$, $E = 151$). These are *is-a* hierarchies with tree-like structure.

**Clinical**: Depression symptom networks at minimum severity ($N = 1634$, $E = 11354$).

All networks are converted to undirected unweighted graphs (largest connected component) to match the phase transition theory methodology. Edge weights and directionality are discarded in the primary analysis; a supplementary directed-weighted analysis confirms robustness.

### 3.2 Exact LP ORC Computation

For each network:
1. Precompute all-pairs shortest paths via BFS (hop-count distances)
2. For each edge $(u,v)$: construct measures $\mu_u$, $\mu_v$ with $\alpha = 0.5$
3. Extract the support (union of measure supports, typically 8–30 nodes)
4. Solve the LP for exact $W_1$ using HiGHS
5. Compute $\kappa(u,v) = 1 - W_1/d(u,v)$

Multi-threaded over edges (24 threads). Total computation: <1 minute for $N < 500$ networks; ~6 minutes for depression network ($N = 1634$, $E = 11354$).

The phase transition sweep on random $k$-regular graphs (Figure 1) was computed using the Sinkhorn algorithm ($\varepsilon = 0.01$, 1000 iterations). All real-network curvature values reported in Table 1 were computed using exact linear programming via JuMP + HiGHS, eliminating entropy regularization bias. Figure 2 quantifies the per-edge discrepancy between the two methods.

**Table M1: Computation method provenance**

| Result | Method | Solver | Script |
|--------|--------|--------|--------|
| Phase transition curve (Fig. 1) | Sinkhorn ($\varepsilon$=0.01) | Pure Julia | `phase_transition_pure_julia.jl` |
| 11-network curvature (Table 1) | Exact LP | HiGHS | `unified_semantic_orc.jl` |
| Sinkhorn vs LP comparison (Fig. 2) | Both | Both | `compare_methods.jl` |
| Hypercomplex ORC | Exact LP | HiGHS | `hypercomplex_semantic_orc.jl` |
| Null model curvature | Exact LP | HiGHS | `bridge_analysis.jl` |
| Analytical $\eta_c$ fit | Exact LP | HiGHS | `analytical_eta_c.jl` |

### 3.3 Sphere-Embedded (Hypercomplex) ORC

To test whether hyperbolicity is intrinsic or metric-dependent, we also compute ORC using geodesic distances on the sphere $S^{d-1}$ ($d = 4$):

1. Compute all-pairs BFS distances
2. Select $d$ landmarks via farthest-first traversal
3. Embed nodes onto $S^{d-1}$ by normalizing distance-to-landmark vectors
4. Replace hop-count cost matrix with geodesic distances $\arccos(\mathbf{x}_i \cdot \mathbf{x}_j)$
5. Compute ORC with the same probability measures but sphere-based transport cost

This tests whether the sign of $\kappa$ depends on the choice of metric.

### 3.4 Formal Verification

A Lean 4 formalization (25 modules, 8097 lines) provides machine-checked proofs for the core ORC theory. The 7 core modules contain 0 `sorry` statements and rely on 5 explicit axioms (Wasserstein symmetry, triangle inequality, coupling bound, local clustering bound, specification bridge—all mathematically standard). Machine-checked results include $W_1 \geq 0$, coupling marginal preservation, $\kappa \in [-1, 1]$, curvature vanishing for unreachable nodes, regime exclusivity, and clustering bounds.

---

## 4. Results

### 4.1 Semantic Network Curvatures

Table 1 presents exact LP ORC for all 11 networks.

**Table 1: Exact LP Ollivier-Ricci Curvature of Semantic Networks**

| Network | Category | Language | $N$ | $E$ | $\langle k \rangle$ | $C$ | $\eta$ | $\bar{\kappa}$ | Geometry |
|---------|----------|----------|-----|-----|-----|-----|-----|-----|-----|
| SWOW Spanish | Association | Spanish | 422 | 571 | 2.71 | 0.136 | 0.017 | $-0.068$ | Hyperbolic |
| SWOW English | Association | English | 438 | 640 | 2.92 | 0.128 | 0.020 | $-0.137$ | Hyperbolic |
| SWOW Chinese | Association | Chinese | 465 | 762 | 3.28 | 0.173 | 0.023 | $-0.144$ | Hyperbolic |
| SWOW Dutch | Association | Dutch | 500 | 15368 | 61.5 | 0.238 | 7.558 | $+0.099$ | **Spherical** |
| ConceptNet EN | Knowledge | English | 467 | 2383 | 10.2 | 0.108 | 0.223 | $-0.233$ | Hyperbolic |
| ConceptNet PT | Knowledge | Portuguese | 489 | 1578 | 6.45 | 0.106 | 0.085 | $-0.236$ | Hyperbolic |
| WordNet EN | Taxonomy | English | 500 | 527 | 2.11 | 0.013 | 0.009 | $-0.002$ | Euclidean |
| WordNet EN-2K | Taxonomy | English | 2000 | 2075 | 2.08 | 0.002 | 0.002 | $-0.005$ | Euclidean |
| BabelNet RU | Taxonomy | Russian | 493 | 522 | 2.12 | 0.001 | 0.009 | $-0.030$ | Euclidean |
| BabelNet AR | Taxonomy | Arabic | 142 | 151 | 2.13 | 0.000 | 0.032 | $-0.012$ | Euclidean |
| Depression (min) | Clinical | English | 1634 | 11354 | 13.9 | 0.159 | 0.118 | $-0.130$ | Hyperbolic |

Three distinct geometric regimes emerge:
1. **Hyperbolic** ($\bar{\kappa} \in [-0.24, -0.07]$): All association and knowledge networks with $C > 0.10$
2. **Euclidean** ($|\bar{\kappa}| < 0.03$): All taxonomy networks with $C < 0.02$
3. **Spherical** ($\bar{\kappa} = +0.10$): Dutch SWOW with $\eta \gg \eta_c$

### 4.2 Placing Semantic Networks on the Phase Transition Curve

The central result is the bridge figure (Figure 2, `figures/monograph/figure2_bridge.pdf`), which overlays all 11 semantic networks onto the random regular graph phase transition curves (Figure 1, `figures/monograph/figure1_phase_transition.pdf`).

Every network except Dutch SWOW has $\eta \ll \eta_c(N)$—the phase transition theory predicts all should be hyperbolic. Yet taxonomies are Euclidean. This means:

> **$\eta < \eta_c$ is necessary but not sufficient for hyperbolicity.**

The key test is Dutch SWOW: with $\eta = 7.56$ and $\eta_c(500) = 3.10$, the phase transition theory predicts *spherical* geometry. The observation $\bar{\kappa} = +0.099$ confirms this prediction. This is the first empirical validation of the curvature phase transition in a real (non-synthetic) network.

### 4.3 The Two-Parameter Theory

The missing ingredient is the clustering coefficient $C$. Among networks with $\eta < \eta_c$:

- **Hyperbolic group** ($\bar{\kappa} < -0.05$): Mean $C = 0.135$, range $[0.106, 0.173]$
- **Euclidean group** ($|\bar{\kappa}| < 0.05$): Mean $C = 0.004$, range $[0.000, 0.013]$

The two groups are cleanly separated by a clustering threshold $C^* \approx 0.05$. No network with $C < 0.05$ is hyperbolic; no network with $C > 0.05$ and $\eta < \eta_c$ is Euclidean.

The empirical model identifies three regimes:

| Regime | Condition | Geometry | Example |
|--------|-----------|----------|---------|
| Above threshold | $\eta > \eta_c(N)$ | Spherical ($\bar{\kappa} > 0$) | Dutch SWOW |
| Below threshold, clustered | $\eta < \eta_c(N)$ and $C > C^*$ | Hyperbolic ($\bar{\kappa} < 0$) | SWOW ES/EN/ZH, ConceptNet |
| Below threshold, tree-like | $\eta < \eta_c(N)$ and $C < C^*$ | Euclidean ($\bar{\kappa} \approx 0$) | WordNet, BabelNet |

This three-regime model is consistent with all 11 networks studied (11/11 post-hoc; out-of-sample validation on additional datasets is needed to assess generalizability).

### 4.4 The Taxonomy Puzzle

Why are taxonomies Euclidean despite $\eta \ll \eta_c$?

Taxonomies are near-trees with $C \approx 0$. In a tree, BFS neighborhoods from adjacent nodes $u$ and $v$ have minimal overlap—the probability masses must traverse long paths. Yet the curvature is not strongly negative because in trees, the transport problem has a specific structure: mass from $u$'s branch must travel through the $u$-$v$ edge to reach $v$'s branch, giving $W_1 \approx d(u,v)$ and thus $\kappa \approx 0$.

This is analogous to $k = 2$ regular graphs (cycles), which have $\kappa = 0$ exactly. Both represent a distinct geometric regime: "tree-like Euclidean" where the lack of alternative transport paths forces $W_1 \approx d(u,v)$ regardless of local density.

### 4.5 Degree-Matched Null Model Analysis

To isolate the *semantic* contribution to curvature, we compare each real network against degree-matched random regular graph nulls. For each network with $N$ nodes and mean degree $\langle k \rangle$, we generate 10 random $k$-regular graphs with $k = \text{round}(\langle k \rangle)$ and the same $N$, then compute exact LP ORC for each.

**Table 2: Semantic Contribution to Curvature (Degree-Matched Null Models)**

| Network | $N$ | $k_{\text{reg}}$ | $\bar{\kappa}_{\text{null}}$ | $\bar{\kappa}_{\text{real}}$ | $\Delta\kappa_{\text{sem}}$ |
|---------|-----|-----|------|------|------|
| SWOW Spanish | 422 | 3 | $-0.320 \pm 0.005$ | $-0.068$ | $+0.251$ |
| SWOW English | 438 | 3 | $-0.319 \pm 0.005$ | $-0.137$ | $+0.182$ |
| SWOW Chinese | 465 | 4 | $-0.467 \pm 0.004$ | $-0.144$ | $+0.323$ |
| SWOW Dutch | 500 | 61 | $+0.069 \pm 0.000$ | $+0.099$ | $+0.029$ |
| ConceptNet EN | 467 | 10 | $-0.420 \pm 0.003$ | $-0.233$ | $+0.187$ |
| ConceptNet PT | 489 | 6 | $-0.551 \pm 0.005$ | $-0.236$ | $+0.315$ |
| Depression (min) | 1634 | 14 | $-0.518 \pm 0.001$ | $-0.130$ | $+0.388$ |
| WordNet EN | 500 | 2 | $0.000 \pm 0.000$ | $-0.002$ | $-0.002$ |
| WordNet EN-2K | 2000 | 2 | $0.000 \pm 0.000$ | $-0.005$ | $-0.005$ |
| BabelNet RU | 493 | 2 | $0.000 \pm 0.000$ | $-0.030$ | $-0.030$ |
| BabelNet AR | 142 | 2 | $0.000 \pm 0.000$ | $-0.012$ | $-0.012$ |

The semantic contribution $\Delta\kappa_{\text{sem}} = \bar{\kappa}_{\text{real}} - \bar{\kappa}_{\text{null}}$ reveals a striking pattern:

1. **For all networks with $\langle k \rangle > 2$**: $\Delta\kappa_{\text{sem}} > 0$, meaning semantic organization *reduces* the magnitude of negative curvature compared to random graphs. Real semantic networks are significantly *less hyperbolic* than random graphs with the same degree. The semantic structure—clustering, community organization, short-range associations—pushes curvature toward zero.

2. **The magnitude is large**: $\Delta\kappa_{\text{sem}}$ ranges from $+0.029$ (Dutch SWOW, already spherical) to $+0.388$ (depression network). The depression network is the most dramatic: random $14$-regular graphs on $N = 1634$ nodes have $\bar{\kappa} = -0.518$, but the real depression network has $\bar{\kappa} = -0.130$—the semantic/clinical structure eliminates 75% of the curvature.

3. **Taxonomy networks ($k = 2$)**: The null model is a cycle ($k$-regular with $k = 2$), which has $\kappa = 0$ exactly. The real taxonomies are slightly *more* negative ($\Delta\kappa_{\text{sem}} < 0$), consistent with the slight negative curvature induced by branching in tree-like structures. The effect is small ($|\Delta\kappa_{\text{sem}}| < 0.03$), confirming taxonomies are geometrically close to cycles.

4. **Null model consistency**: The random regular null curvatures match the PREPRINT phase transition curve: $k = 3, N \approx 450$ gives $\eta = 0.02$, deep in the hyperbolic regime, producing $\bar{\kappa} \approx -0.32$. This cross-validates the null model computation against the independent phase transition data.

### 4.6 Hypercomplex Metric Comparison

To test whether hyperbolicity is intrinsic or metric-dependent, we compute ORC using geodesic distances on the sphere $S^{d-1}$ for embedding dimensions $d \in \{4, 8, 16\}$.

**Table 3: Complete Hypercomplex ORC Across the Cayley-Dickson Tower (all 11 networks, $d \in \{4, 8, 16\}$)**

| Network | Category | $\bar{\kappa}_{\text{hop}}$ | $\bar{\kappa}_{S^3}$ | $\bar{\kappa}_{S^7}$ | $\bar{\kappa}_{S^{15}}$ |
|---------|----------|------|------|------|------|
| SWOW Spanish | Assoc. | $-0.068$ | $-0.048$ | $+0.024$ | $+0.064$ |
| SWOW English | Assoc. | $-0.137$ | $+0.094$ | $+0.062$ | $+0.045$ |
| SWOW Chinese | Assoc. | $-0.144$ | $+0.013$ | $+0.044$ | $+0.045$ |
| SWOW Dutch | Assoc. | $+0.099$ | $+0.411$ | $+0.337$ | $+0.247$ |
| ConceptNet EN | Knowledge | $-0.233$ | $+0.220$ | $+0.142$ | $+0.108$ |
| ConceptNet PT | Knowledge | $-0.236$ | $+0.162$ | $+0.113$ | $+0.092$ |
| WordNet EN | Taxonomy | $-0.002$ | $+0.717$ | $+0.716$ | $+0.688$ |
| WordNet EN-2K | Taxonomy | $-0.005$ | $+0.833$ | $+0.818$ | $+0.820$ |
| BabelNet RU | Taxonomy | $-0.030$ | $+0.436$ | $+0.512$ | $+0.544$ |
| BabelNet AR | Taxonomy | $-0.012$ | $+0.547$ | $+0.499$ | $+0.490$ |
| Depression | Clinical | $-0.130$ | $+0.234$ | $+0.171$ | $+0.137$ |

At $d = 4$, 10 of 11 networks are already positive; SWOW Spanish ($\bar{\kappa} = -0.048$) is the sole exception. By $d = 8$, **all 11 networks are positive**. Three structural patterns emerge across the Cayley-Dickson tower:

1. **Association and knowledge networks**: curvature *decreases monotonically* with $d$ ($\kappa_{S^3} > \kappa_{S^7} > \kappa_{S^{15}}$), suggesting the hop-count metric captures genuine local negative curvature that the sphere metric progressively masks.
2. **Taxonomies** (WordNet, BabelNet): curvature remains *high and approximately constant* across dimensions ($\bar{\kappa} \approx 0.5$--$0.8$), reflecting tree-like structure that embeds naturally on any sphere.
3. **BabelNet Russian**: uniquely *increases* with $d$ ($0.436 \to 0.512 \to 0.544$), suggesting its near-tree topology benefits from higher-dimensional embedding.

**Table 4: SWOW Spanish — Dimensional Hierarchy**

| Metric | Space | $\bar{\kappa}$ | $\sigma_\kappa$ | Valid edges |
|--------|-------|------|------|------|
| Hop-count | $\mathbb{Z}$ | $-0.068$ | $0.319$ | 571/571 |
| $d = 4$ | $S^3$ | $-0.048$ | $0.720$ | 541/571 |
| $d = 8$ | $S^7$ | $+0.024$ | $0.440$ | 544/571 |
| $d = 16$ | $S^{15}$ | $+0.064$ | $0.280$ | 555/571 |

SWOW Spanish crosses zero between $d = 4$ and $d = 8$. The variance $\sigma_\kappa$ decreases monotonically from $0.720$ to $0.280$ as $d$ increases, indicating that higher-dimensional embedding not only shifts the mean but tightens the distribution — consistent with the Johnson-Lindenstrauss effect.

The complete dimensional hierarchy confirms that **no semantic network retains hyperbolic curvature** at sufficient embedding dimension. The Cayley-Dickson tower (quaternions $\to$ octonions $\to$ sedenions) provides a natural algebraic framework for this progression, with each doubling of dimension providing additional geometric room for neighborhood mass distributions to overlap.

This demonstrates that **semantic hyperbolicity is entirely metric-dependent** — an artifact of the integer hop-count metric on graphs, not an intrinsic topological property. The compact geometry of $S^{d-1}$ eliminates negative curvature for all networks, just as it does for random regular graphs (confirmed in the PREPRINT at $N \in \{50, 100, 200\}$, all $k$, all $d$).

### 4.7 Sinkhorn vs. Exact LP Validation

Comparing our exact LP results with the Sinkhorn-based results from prior work:

| Network | $\kappa_{\text{Sinkhorn}}$ | $\kappa_{\text{ExactLP}}$ | $\Delta\kappa$ |
|---------|------|------|------|
| SWOW Spanish | $-0.155$ | $-0.068$ | $+0.087$ |
| SWOW English | $-0.258$ | $-0.137$ | $+0.121$ |
| SWOW Chinese | $-0.214$ | $-0.144$ | $+0.070$ |

The mean shift $\Delta\kappa = +0.092$ is larger than the expected Sinkhorn bias ($< 0.015$ for random graphs at matched $N$ and $k$). The discrepancy is due to the methodological change from **directed weighted** (prior work) to **undirected unweighted** (this work), not solver bias. Three lines of evidence support this:

1. The Sinkhorn bias on random regular graphs is consistently $< 0.015$ across all tested $(N, k)$ pairs (PREPRINT Table 2).
2. The direction of the shift (+0.087 to +0.121) is consistently positive, whereas Sinkhorn regularization bias is negative (Sinkhorn overestimates $W_1$, making $\kappa$ more negative).
3. The magnitude of the shift ($\sim 0.09$) matches the expected effect of converting directed weighted to undirected unweighted: directed edges capture association asymmetry (e.g., "dog→animal" is stronger than "animal→dog"), which amplifies transport cost and thus hyperbolicity.

Under both methodologies, all three SWOW networks remain hyperbolic ($\bar{\kappa} < 0$), and the relative ordering is preserved (English most hyperbolic, Spanish least).

### 4.8 Clinical Application: Depression Severity

The depression network at minimum severity ($N = 1634$, $E = 11354$, $C = 0.159$) is hyperbolic ($\bar{\kappa} = -0.130$), consistent with the two-parameter theory ($\eta = 0.118 \ll \eta_c = 3.39$, $C = 0.159 > C^*$).

The null model comparison (Section 4.5) reveals this network has the largest semantic contribution of any network studied: $\Delta\kappa_{\text{sem}} = +0.388$, meaning the clinical symptom structure eliminates 75% of the curvature that a random 14-regular graph would exhibit. This suggests that symptom co-occurrence patterns create substantial local structure (communities of related symptoms) that counteracts the homogeneous negative curvature of random graphs.

This demonstrates that the two-parameter theory extends beyond linguistic semantic networks to clinical symptom networks, and that the null model decomposition provides a quantitative measure of "structural organization" in any network.

---

## 5. Formal Verification

### 5.1 Lean 4 Formalization

We provide a Lean 4 formalization of the core ORC theory comprising 25 modules and 8097 lines of code. The 7 core modules (Basic, Wasserstein, Curvature, PhaseTransition, Bounds, Consistency, Axioms) contain **0 `sorry` statements**, meaning every proof in these modules is machine-checked.

Machine-verified results include:
- **Wasserstein non-negativity**: $W_1(\mu, \nu) \geq 0$
- **Coupling marginals**: Transport plans preserve marginal distributions
- **Probability measure normalization**: $\sum_x \mu(x) = 1$
- **Curvature bounds**: $\kappa(u,v) \in [-1, 1]$ for adjacent vertices
- **Curvature vanishing**: $\kappa(u,v) = 0$ when $u$ and $v$ are unreachable
- **Regime exclusivity**: Hyperbolic, Euclidean, and spherical regimes are mutually exclusive
- **Clustering bounds**: Local clustering coefficient satisfies $0 \leq C(v) \leq 1$

### 5.2 Axioms

The formalization relies on 5 axioms in the core modules:
1. **Wasserstein symmetry**: $W_1(\mu, \nu) = W_1(\nu, \mu)$
2. **Wasserstein triangle inequality**: $W_1(\mu, \rho) \leq W_1(\mu, \nu) + W_1(\nu, \rho)$
3. **Coupling bound**: $W_1(\mu_u, \mu_v) \leq$ explicit coupling cost
4. **Local clustering bound**: Clustering coefficient bounded by triangle-to-triplet ratio
5. **Specification bridge**: Connecting abstract formalization to computational implementation

All axioms are mathematically standard; they encode properties that are either well-known theorems in optimal transport theory or definitional identities.

### 5.3 Open Problems

The formalization identifies several open problems:
1. **Analytical form of $\mathbb{E}[\kappa](\eta)$**: The exact functional form remains unknown. Heuristic approximations fail ($R^2 < 0$).
2. **Formal proof of the sign change**: The crossover at $\eta_c$ is confirmed numerically but not formally proven.
3. **Clustering-curvature coupling**: No formal statement connects clustering coefficient to mean curvature.

---

## 6. Discussion

### 6.1 An Empirical Two-Parameter Model for Semantic Network Geometry

The geometry of the 11 semantic networks studied here is well-described by two measurable parameters: density ($\eta$) and clustering ($C$). The random-graph sign change provides the necessary condition ($\eta < \eta_c$) while clustering modulates curvature magnitude within the sub-critical regime. This yields a three-regime classification consistent with all 11 networks.

We emphasize that this classification is *post-hoc* on $n = 11$ networks. While the Dutch SWOW confirmation (spherical geometry for $\eta > \eta_c$, as predicted by the random-graph model) and the clean separation of taxonomy vs. association networks provide encouraging evidence, the clustering threshold $C^* \approx 0.05$ is identified empirically—not derived from theory. Out-of-sample validation on additional datasets (e.g., Hindi, Japanese, Korean SWOW; additional clinical networks) is essential before claiming generality. The model should be understood as a hypothesis-generating framework, not a validated predictive tool.

The semi-analytical framework (§2.5) provides a mechanistic basis for this interaction. Clustering increases the expected number of common neighbors $t = C(k-1)$, reducing exclusive neighborhoods $n_{\mathrm{exc}} = (1-C)(k-1)$ and thereby reducing the Wasserstein transport cost. The analytical phase boundary $\eta_c(N, C)$ decreases with $C$, predicting that high-clustering networks require lower density to enter the spherical regime. At $C = 0$ (taxonomies), the boundary is $\eta_c(\infty) \approx 5.5$—unreachable for sparse networks. At $C = 0.15$ (association networks), it drops to $\eta_c(\infty) \approx 2.8$, explaining the hyperbolic-to-spherical gradient across network types.

Spearman rank correlations quantify the two-parameter structure: $\rho(\eta, \kappa) = -0.31$ (density alone is weakly associated), $\rho(C, \kappa) = -0.16$ (clustering alone is weaker still), but $\rho(\eta, C) = +0.52$ (the two parameters are correlated). These modest individual correlations suggest that the interaction—not either variable alone—drives the geometry. With only 11 data points, these correlations have wide confidence intervals and should be interpreted cautiously.

### 6.2 Null Model Decomposition: What Makes Semantic Networks Special

The degree-matched null model analysis (Section 4.5) provides a decomposition of curvature into structural and random components:

$$\bar{\kappa}_{\text{real}} = \bar{\kappa}_{\text{null}}(N, k) + \Delta\kappa_{\text{semantic}}$$

The null component $\bar{\kappa}_{\text{null}}$ depends only on $(N, k)$ and lies on the random regular phase transition curve. The semantic component $\Delta\kappa_{\text{semantic}}$ captures the effect of non-random organization—clustering, community structure, hierarchical branching.

For all networks with $\langle k \rangle > 2$, the semantic contribution is positive ($\Delta\kappa_{\text{semantic}} > 0$), meaning semantic organization makes networks *less hyperbolic* than random graphs. This is the opposite of what one might naively expect: the prevailing narrative associates semantic networks with "hierarchical, tree-like, hyperbolic" geometry. Instead, semantic structure introduces local triangles and communities that increase neighborhood overlap, thereby reducing transport cost and pushing curvature toward zero (or beyond, in the case of Dutch SWOW).

The magnitude of $\Delta\kappa_{\text{semantic}}$ varies by network type:
- **Association networks**: $\Delta\kappa \approx 0.18$–$0.32$ (moderate semantic contribution)
- **Knowledge graphs**: $\Delta\kappa \approx 0.19$–$0.32$ (similar range)
- **Clinical**: $\Delta\kappa = 0.39$ (largest—symptom co-occurrence creates strong local structure)
- **Taxonomies ($k = 2$)**: $\Delta\kappa \approx -0.01$ to $-0.03$ (negligible—trees are geometrically similar to cycles)

This decomposition reframes the central question: semantic networks are not "hyperbolic because of their semantic structure" but rather "less hyperbolic than random graphs *despite* their sparsity, and what hyperbolicity remains is driven primarily by low $\eta$."

### 6.3 Dutch SWOW: A Natural Experiment

The Dutch SWOW network serves as a natural experiment. Unlike the other SWOW datasets (which have $\langle k \rangle \approx 3$ and $\eta \ll 1$), Dutch SWOW has $\langle k \rangle = 61.5$ and $\eta = 7.56$—well above the phase transition threshold. Its spherical geometry ($\bar{\kappa} = +0.10$) is therefore a prediction of the theory, not an anomaly.

The extreme density of Dutch SWOW likely reflects differences in the preprocessing pipeline (e.g., inclusion of more association types or lower frequency thresholds). This methodological sensitivity is itself informative: it demonstrates that the boundary between hyperbolic and spherical geometry is crossed by varying association density, not by changing language or culture.

The null model confirms this interpretation: the degree-matched random 61-regular graph on 500 nodes has $\bar{\kappa}_{\text{null}} = +0.069$, already positive—the phase transition has been crossed by degree alone. The real Dutch SWOW adds $\Delta\kappa = +0.029$ from semantic structure, modestly amplifying the spherical geometry.

### 6.4 Intrinsic vs. Metric-Dependent Hyperbolicity

The hypercomplex analysis (Table 3, Section 4.6) demonstrates that ORC-based hyperbolicity in semantic networks depends on the choice of metric. When transport cost is computed using geodesic distances on $S^{d-1}$, all 11 networks become spherical by $d = 8$.

The mechanism is straightforward: the integer hop-count metric on graphs is non-compact—distances grow without bound and neighborhoods are always finite. Sphere metrics are compact—distances are bounded by $\pi$ and neighborhoods eventually cover the entire space. As $d$ increases, the sphere becomes more accommodating, facilitating neighborhood overlap and driving curvature positive.

This does not diminish the empirical finding that under hop-count (the natural metric for unweighted graphs), association networks are hyperbolic while taxonomies are Euclidean. But it clarifies that hyperbolicity is a property of the (graph, metric) pair, not the graph alone. Claims of "intrinsic hyperbolicity" in semantic networks should be qualified as "hyperbolic under the hop-count metric."

We note a caveat: the sphere-embedding uses a landmark-based approximation (farthest-first traversal), not an isometric embedding. The high per-edge variance ($\sigma_\kappa \approx 0.3$–$0.7$) suggests embedding quality varies across edges. The qualitative conclusion (all networks flip) is robust, but precise crossover dimensions depend on embedding quality.

### 6.5 Clinical Application

The depression symptom network at minimum severity is hyperbolic ($\bar{\kappa} = -0.130$), consistent with the two-parameter model ($\eta = 0.118 \ll \eta_c$, $C = 0.159 > C^*$). The null model decomposition reveals the largest semantic contribution of any network ($\Delta\kappa_{\text{sem}} = +0.388$), indicating that symptom co-occurrence patterns create substantial local structure compared to random graphs with the same degree.

Whether curvature varies across depression severity levels (mild, moderate, severe) remains an open empirical question. Denser symptom networks at higher severity would push $\eta$ toward $\eta_c$, potentially changing the geometric regime—but this is speculation pending computation of the full severity spectrum.

### 6.6 Limitations

1. **Small sample size ($n = 11$)**: The three-regime classification is post-hoc on 11 networks. The clustering threshold $C^* \approx 0.05$ is pattern-matched, not derived from theory, and may not generalize. Out-of-sample validation on additional datasets is the highest priority for future work.
2. **Network construction sensitivity**: The conversion from directed-weighted to undirected-unweighted graphs reduces curvature magnitude by ~40%. The top-500-cue filtering also introduces selection bias (full SWOW datasets have $N \approx 9{,}000$+). Both choices affect absolute curvature values, though relative orderings are preserved.
3. **Single realization**: Each real network is a single instance, unlike the multi-seed random graph experiments. Formal uncertainty quantification for real networks requires bootstrap resampling or cross-validation, which we have not performed.
4. **Null model scope**: We use degree-matched random $k$-regular graphs, which control for $N$ and $\langle k \rangle$ but not for degree heterogeneity. Configuration model nulls (preserving the full degree sequence) would provide a more stringent baseline and are essential for networks with heterogeneous degree distributions (e.g., ConceptNet, depression).
5. **Landmark embedding quality**: The sphere-embedded ORC depends on the landmark selection (farthest-first traversal with seed 42). High variance in per-edge curvatures ($\sigma_\kappa \approx 0.3$–$0.7$) suggests embedding quality varies across edges. Sensitivity to landmark choice has not been systematically assessed, and the embedding is not isometric.
6. **Depression networks**: Only minimum severity has been computed. The full severity trajectory requires the mild, moderate, and severe networks ($N = 2685$–$5000$).
7. **Semi-analytical**: The Hehl-based framework (§2.5) yields an analytical $\eta_c(N, C)$ validated on random regular graphs (MAE = 0.009), but the matching heuristic is empirical, not proven. The analytical $\eta_c$ overpredicts empirical values by ~5–15%. No closed-form derivation of $C^*$ exists.

### 6.7 Future Directions

1. **Additional languages**: Hindi, Japanese, Korean SWOW datasets would test the universality of the two-parameter theory across language families (Dravidian, Japonic, Koreanic)
2. **Depression severity trajectory**: Full analysis of mild/moderate/severe networks to test the geometric biomarker hypothesis
3. **Configuration model nulls**: Preserve degree sequence (not just mean degree) for more stringent null comparison; estimate $M = 100$–$200$ replicates per network for $p$-value resolution
4. **Rigorous matching bound**: Prove the heuristic $E[|M|] = n_{\mathrm{exc}}(1 - e^{-\eta n_{\mathrm{exc}}/k^2})$ and derive a closed-form $C^*$ from the ORC definition, closing the gap between the semi-analytical and fully analytical frameworks
5. **Lean 4 completion**: Close the remaining 85 `sorry` stubs in 18 auxiliary modules, particularly RicciFlow (17 sorry) and SpectralGeometry (20 sorry)
6. **Hyperbolic embeddings**: Compare ORC-based geometry with Poincare/Lorentz embeddings to test whether different geometric formalisms agree on which networks are hyperbolic
7. **Temporal dynamics**: Apply the theory to evolving networks (e.g., word association changes across decades) to test whether geometric transitions track semantic drift

---

## 7. Code and Data Availability

All code and data are available at: https://github.com/agourakis82/hyperbolic-semantic-networks

- **Julia scripts**: `julia/scripts/unified_semantic_orc.jl` (semantic network ORC), `julia/scripts/exact_curvature_lp.jl` (phase transition), `julia/scripts/bridge_analysis.jl` (bridge analysis), `julia/scripts/hypercomplex_semantic_orc.jl` (sphere-embedded ORC)
- **Lean 4 formalization**: `lean/HyperbolicSemanticNetworks/`
- **Results**: `results/unified/` (all JSON output files)
- **Edge lists**: `data/processed/` (all network CSV files)

---

## References

[1] Ollivier, Y. (2009). Ricci curvature of Markov chains on metric spaces. *Journal of Functional Analysis*, 256(3), 810–864.

[2] Small World of Words. https://smallworldofwords.org

[3] Cuturi, M. (2013). Sinkhorn distances: Lightspeed computation of optimal transport. *NeurIPS*.

[4] Dunning, I., Huchette, J., & Lubin, M. (2017). JuMP: A modeling language for mathematical optimization. *SIAM Review*, 59(2), 295–320.

[5] Huber, B., & Szeider, S. (2024). HiGHS: High performance software for linear optimization.

[6] Lin, Y., Lu, L., & Yau, S.-T. (2011). Ricci curvature of graphs. *Tohoku Mathematical Journal*, 63(4), 605–627.

[7] Ni, C.-C., Lin, Y.-Y., Gao, J., Gu, X. D., & Saucan, E. (2015). Ricci curvature of the Internet topology. *INFOCOM*.

[8] De Luca, L., et al. (2024). SWOW-RP: A multi-language resource for word associations.

[9] Speer, R., Chin, J., & Havasi, C. (2017). ConceptNet 5.5: An open multilingual graph of general knowledge. *AAAI*.

[10] Sandhu, R. S., et al. (2015). Graph curvature for differentiating cancer networks. *Scientific Reports*, 5, 12323.

[11] Clauset, A., Shalizi, C. R., & Newman, M. E. J. (2009). Power-law distributions in empirical data. *SIAM Review*, 51(4), 661–703.

[12] Topping, J., Di Giovanni, F., Chamberlain, B. P., Dong, X., & Bronstein, M. M. (2022). Understanding over-squashing and bottlenecks on graphs via curvature. *ICLR*.

[13] Ni, C.-C. (2019). GraphRicciCurvature. https://github.com/saibalmars/GraphRicciCurvature

[14] Hehl, M. (2025). Ollivier-Ricci curvature of regular graphs. *Calculus of Variations and Partial Differential Equations*, 64. arXiv:2407.08854.

[15] Trugenberger, C. A. (2024). Emergent hyperbolic network geometry. *Physical Review E*.

[16] Mitsche, D. & Mubayi, D. (2024). Curvature of random regular graphs.

---

## Supplementary Material

### S1: Full Lean 4 Module Inventory

| Module | Lines | Sorry | Description |
|--------|-------|-------|-------------|
| Basic | 180 | 0 | Foundational definitions |
| Wasserstein | 280 | 0 | W₁ distance properties |
| Curvature | 450 | 0 | ORC definitions and bounds |
| PhaseTransition | 320 | 0 | Sign change formalization |
| Bounds | 250 | 0 | Curvature bound proofs |
| Consistency | 180 | 0 | Cross-module consistency |
| Axioms | 150 | 0 | Axiom declarations |
| *7 core total* | *1810* | *0* | |
| RandomGraph | — | 21 | Random graph properties |
| RicciFlow | — | 17 | Flow dynamics |
| SpectralGeometry | — | 20 | Spectral gap |
| Other (11 modules) | — | 27 | Extensions |
| **25 total** | **8097** | **85** | |

### S2: Directed-Weighted Analysis

The original SWOW analysis used directed weighted graphs with Sinkhorn ORC:
- Spanish: $\kappa = -0.155$ (directed) vs. $-0.068$ (undirected)
- English: $\kappa = -0.258$ (directed) vs. $-0.137$ (undirected)
- Chinese: $\kappa = -0.214$ (directed) vs. $-0.144$ (undirected)

The $\sim 50\%$ reduction in magnitude reflects the loss of association asymmetry. Both representations agree on the sign (hyperbolic) and the relative ordering (English most hyperbolic, Spanish least).

### S3: SWOW Spanish Dimensional Hierarchy

SWOW Spanish was the sole network retaining $\bar{\kappa} < 0$ under $S^3$ embedding ($d = 4$). Testing higher dimensions:

| Dimension | $\bar{\kappa}$ | $\sigma_\kappa$ | Valid edges |
|-----------|------|------|------|
| Hop-count | $-0.068$ | $0.319$ | 571 |
| $d = 4$ ($S^3$) | $-0.048$ | $0.720$ | 541 |
| $d = 8$ ($S^7$) | $+0.024$ | $0.440$ | 544 |
| $d = 16$ ($S^{15}$) | $+0.064$ | $0.280$ | 555 |

The network crosses zero between $d = 4$ and $d = 8$, following the Cayley-Dickson tower (quaternions → octonions → sedenions). This confirms that no semantic network retains hyperbolic curvature at sufficient embedding dimension.

### S4: Figure List

| Figure | File | Description |
|--------|------|-------------|
| 1 | `figure1_phase_transition.pdf` | Curvature sign change in random regular graphs ($N \in \{50, 100, 200, 500, 1000\}$) |
| 2 | `figure2_bridge.pdf` | **THE BRIDGE**: Semantic networks overlaid on the phase transition curve (log-$\eta$ scale) |
| 3 | `figure3_clustering_curvature.pdf` | Three-regime classification: clustering vs. curvature with $C^* = 0.05$ threshold |
| 4 | `figure4_hypercomplex.pdf` | Curvature across the Cayley-Dickson tower: dimensional hierarchy (hop → $S^3$ → $S^7$ → $S^{15}$) |
| 5 | `figure5_phase_diagram.pdf` | Two-parameter phase diagram: $\eta$ vs. $C$, sized by $|\kappa|$ |
| 6 | `figure6_distributions.pdf` | Per-edge curvature distributions (box plots) for representative networks |
| 7 | `figure7_null_models.pdf` | Real vs. degree-matched null model curvature (semantic contribution $\Delta\kappa$) |

All figures in `figures/monograph/`, generated by `julia/scripts/generate_monograph_figures.jl`.
