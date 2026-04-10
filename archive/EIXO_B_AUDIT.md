# Eixo B Audit

Date: 2026-04-09  
Repository: `hyperbolic-semantic-networks`

## Scope

This audit answers the requested Phase 0 questions for the CPC 2026 full-paper sprint:

1. Existing trajectory / Langevin / random-walk code
2. Existing `C_ent` implementation status
3. Available SWOW-EN data
4. Ready-to-use ORC infrastructure
5. Existing results in `results/`
6. Current `manuscript/main.md` scope

I audited `code/`, `experiments/`, `scripts/`, `julia/`, `rust/`, `archive/`, `docs/`, `manuscript/`, `data/`, and `results/`.

## Executive Summary

- There is **no existing CPC-style cognitive trajectory simulator** on SWOW-EN in this repo.
- There is **no existing implementation** of the requested entropic curvature
  `C_ent(v) = κ_local(v) * (1 - H(v)/log(deg(v)))`.
- There **are reusable components**:
  - validated exact Julia ORC on SWOW-EN,
  - node-level entropy code in Python,
  - prior attempts at node-level ORC averaging,
  - several Ricci-flow trajectory pipelines.
- The SWOW-EN situation is **not singular**: multiple processed graph variants exist, with materially different densities.
- The **canonical validated ORC path** is Julia exact LP on `data/processed/english_edges_FINAL.csv`, reduced to the largest connected component.
- The main manuscript is **the cross-linguistic geometry paper**, not the CPC 2026 psychiatric extension.

## 1. Existing Langevin / Biased Walk / Cognitive Trajectory Code

### Bottom line

I found **no implementation** of:

- Langevin dynamics on a Poincare embedding
- valence-biased Markov trajectories on SWOW-EN
- regime-specific cognitive trajectory simulation
- residence-time analysis on semantic walks
- Hurst / DFA analysis on semantic trajectories

What does exist is **adjacent dynamics infrastructure**, mostly Ricci-flow or embedding dashboards.

### Relevant files found

#### `code/analysis/ricci_flow_real.py`

- Path: `code/analysis/ricci_flow_real.py`
- What it does:
  - loads a semantic network CSV,
  - computes GraphRicciCurvature ORC,
  - runs discrete Ricci flow via `compute_ricci_flow`,
  - saves a **network-level trajectory** over flow steps.
- Why it matters:
  - it already produces time-indexed trajectories, but of **network metrics**, not of concept-to-concept walks.
- Not a match for CPC:
  - no Langevin,
  - no biased random walk,
  - no node trajectory.

#### `julia/scripts/ricci_flow_semantic.jl`

- Path: `julia/scripts/ricci_flow_semantic.jl`
- What it does:
  - Julia discrete Ricci flow on semantic networks,
  - saves trajectory JSON with stepwise `kappa_mean`, clustering, and weight statistics.
- Why it matters:
  - validated semantic-network dynamics infrastructure exists,
  - but it is still **Ricci flow on edge weights**, not simulated cognition.

#### `julia/scripts/analyze_ricci_flow.jl`

- Path: `julia/scripts/analyze_ricci_flow.jl`
- What it does:
  - post-processes Ricci-flow trajectory JSONs,
  - compares trajectories across networks.
- Not a simulator.

#### `julia/scripts/ricci_flow_surgery.jl`

- Path: `julia/scripts/ricci_flow_surgery.jl`
- What it does:
  - removes high-weight edges after Ricci flow,
  - detects resulting communities and hubs.
- Not a trajectory simulator, but part of existing graph-dynamics tooling.

#### `code/analysis/semantic_flow_visualization.py`

- Path: `code/analysis/semantic_flow_visualization.py`
- What it does:
  - loads arbitrary embeddings,
  - builds a k-NN graph,
  - computes ORC and a **pseudo-Ricci flow**,
  - computes persistence summaries,
  - creates a Plotly dashboard.
- Why it matters:
  - it is the closest thing to an embedding-based dynamics pipeline.
- Why it is not CPC-ready:
  - not SWOW-EN-specific,
  - not Poincare,
  - not Langevin,
  - not valence-biased,
  - acts on a derived k-NN graph from embeddings, not on the semantic graph itself.

#### `experiments/08_epistemic_flow/epistemic_ricci_flow.sio`

- Path: `experiments/08_epistemic_flow/epistemic_ricci_flow.sio`
- What it does:
  - uncertainty-aware Ricci flow on synthetic k-regular graphs,
  - outputs flow trajectories with confidence intervals.
- Important:
  - sophisticated dynamics exist in Sounio,
  - but on synthetic graphs, not SWOW-EN semantic walks.

#### `experiments/sounio_fmri/integrated_pipeline.sio`

- Path: `experiments/sounio_fmri/integrated_pipeline.sio`
- What it does:
  - placeholder fMRI pipeline with a `ManifoldTrajectory` concept,
  - tracks semantic-brain correspondence in principle.
- Important caveat:
  - many functions are `unimplemented!()`,
  - not usable for CPC 2026 semantic walk simulations.

#### `code/fmri/visualize_results.py`

- Path: `code/fmri/visualize_results.py`
- What it does:
  - creates a synthetic manifold trajectory visualization.
- Not relevant to SWOW-EN or CPC regime simulation.

#### Orchestration wrappers

- `scripts/run_ricci_flow_parallel.sh`
- `scripts/monitor_ricci_flow.sh`

These orchestrate Ricci-flow jobs but do not implement trajectory models themselves.

### Not found

- No `*.ipynb` notebooks in the repo
- No `gensim` / `PoincareModel` code
- No Euler-Maruyama implementation
- No biased semantic walk code
- No Hurst / DFA pipeline for semantic trajectories

## 2. Does `C_ent` already exist?

### Bottom line

**No.** I found no implementation of:

`C_ent(v) = κ_local(v) * (1 - H(v) / log(deg(v)))`

and no file named or described as entropic curvature.

### Closest existing components

#### `code/analysis/kec_framework.py`

- Path: `code/analysis/kec_framework.py`
- What exists:
  - `transition_entropy(g)` computes **node-level local transition entropy**.
  - `ricci_curvature(g)` computes **per-node average incident-edge ORC** using GraphRicciCurvature.
  - `meso_coherence(g)` computes community/modularity proxy.
- Why it matters:
  - this already contains 2 of the 3 ingredients needed for `C_ent`: local entropy and node-level curvature.
- Why it is not `C_ent`:
  - no `C_ent` formula,
  - no `log(deg(v))` normalization,
  - no dedicated SWOW-EN output for entropic curvature.

#### `code/analysis/entropy_comparison_shannon_vs_spectral.py`

- Path: `code/analysis/entropy_comparison_shannon_vs_spectral.py`
- What exists:
  - several **network-level** entropy measures,
  - not the requested node-level `H(v)` output table.

#### `code/analysis/clustering_moderation_analysis.py`

- Path: `code/analysis/clustering_moderation_analysis.py`
- What exists:
  - per-node average incident-edge curvature for Spanish,
  - correlation with local clustering.
- Useful as a pattern for node-level `κ(v)`.

#### `code/analysis/create_clustering_figures.py`

- Path: `code/analysis/create_clustering_figures.py`
- What exists:
  - same per-node average incident-edge curvature pattern,
  - figure generation, not a reusable metrics pipeline.

#### `julia/scripts/behavioral_correlation.jl`

- Path: `julia/scripts/behavioral_correlation.jl`
- What exists:
  - reconstructs **per-node mean curvature** for SWOW-EN from exact Julia `per_edge_curvatures`.
- This is especially relevant because it shows one exact-LP-compatible way to derive `κ_local(v)` from the validated Julia outputs.

### Existing outputs that look similar but are not reliable enough

#### `results/kec_english_node_level.csv`

- Path: `results/kec_english_node_level.csv`
- Columns:
  - `name, entropy, curvature, community, coherence`
- Problem:
  - `curvature` is constant `0.0` for every node,
  - `coherence` is also constant across nodes.
- I verified the same degeneracy in:
  - `results/kec_spanish_node_level.csv`
  - `results/kec_chinese_node_level.csv`

Conclusion: these files show that someone attempted node-level entropy + curvature, but the saved curvature outputs are **degenerate and not trustworthy** for CPC use.

## 3. What SWOW-EN data is available?

### Raw data

Raw SWOW-EN is **not committed to git**.

Evidence:

- `data/raw/DATA_DOWNLOAD.md`
- `docs/DATA_FILES_NOTE.md`

These indicate that large raw SWOW files are excluded and must be downloaded separately.

Documented raw filenames include:

- `data/raw/strength.SWOW-EN.R1.20180827.csv`
- `data/raw/SWOW-EN.complete.20180827.csv`

Neither raw file is present in the current checkout.

### Processed SWOW-EN graph variants

#### Variant A: `data/processed/english_edges.csv`

- Path: `data/processed/english_edges.csv`
- Shape:
  - 500 nodes
  - 13,495 undirected edges
  - 1 connected component
- Weights:
  - yes
  - integer/count-like
  - min = 1.0
  - max = 238.0
- Likely origin:
  - denser preprocessing using multiple responses or larger aggregation.

#### Variant B: `data/processed/english_edges_R1.csv`

- Path: `data/processed/english_edges_R1.csv`
- Shape:
  - 500 nodes
  - 5,465 undirected edges
  - 1 connected component
- Weights:
  - yes
  - count-like
- Likely origin:
  - R1-only preprocessing.

#### Variant C: `data/processed/english_edges_FINAL.csv`

- Path: `data/processed/english_edges_FINAL.csv`
- Shape:
  - 467 nodes
  - 661 undirected edges
  - 11 connected components
  - largest connected component = 438 nodes / 640 edges
- Weights:
  - yes
  - float / normalized-strength-like
  - example values around `0.07`, `0.15`, `0.22`
- Likely origin:
  - thresholded R1-strength preprocessing intended to reproduce the sparse Table 1 style graphs.

#### Variant D: `data/processed/english_edges_CORRECT.csv`

- Path: `data/processed/english_edges_CORRECT.csv`
- Status:
  - byte-identical to `english_edges_FINAL.csv` in this checkout.

### Supporting metadata / summaries

- `results/healthy_controls_swow.json`
  - English entry reports 467 nodes / 661 edges for SWOW English.
- `results/unified/swow_en_exact_lp.json`
  - validated ORC result on the **largest connected component**, 438 nodes / 640 edges.

### Edge weights

Yes, processed SWOW-EN files contain weights.

Important nuance:

- the validated Julia exact ORC pipeline currently **ignores weights** and computes ORC on an **undirected unweighted** graph built from `english_edges_FINAL.csv`.
- for the requested CPC `H(v)`, the weights remain useful because they define local transition probabilities.

### Valence / sentiment annotations

I found **no SWOW-EN valence dataset** already present in the repo.

Specifically, I did **not** find:

- Warriner et al. lexicon
- ANEW
- VAD/valence-arousal-dominance tables
- node-level sentiment annotations aligned to SWOW-EN

There are graph edges whose literal tokens happen to be words like `valence`, `arousal`, or `dominance` inside unrelated LWOW datasets, but that is **not** a lexical annotation resource.

Conclusion: valence data will need to be added externally, as requested.

## 4. What ORC computation infrastructure is ready to use?

### Best validated path

The most complete and validated SWOW-EN ORC pipeline is:

- `julia/scripts/unified_semantic_orc.jl`

This script:

- loads `data/processed/english_edges_FINAL.csv`,
- builds an undirected graph,
- extracts the largest connected component,
- computes all-pairs shortest paths,
- solves exact Wasserstein-1 transport with JuMP + HiGHS,
- computes exact Ollivier-Ricci curvature for every edge,
- saves results to `results/unified/swow_en_exact_lp.json`.

### Canonical validated output

- `results/unified/swow_en_exact_lp.json`

Key values in the current repo:

- `N = 438`
- `kappa_mean = -0.137147`
- `geometry = HYPERBOLIC`
- includes `per_edge_curvatures`

### Why this is the best foundation

- It is the repo's **exact** method, not an approximation.
- It is clearly the canonical path reused across the current paper machinery.
- It is consistent with the current validated cross-linguistic geometry workflow.

### Important limitation for CPC

The validated Julia path yields:

- network-level ORC summary
- full per-edge ORC vector

It does **not** directly save per-node `κ(v)`.

However:

- `julia/scripts/behavioral_correlation.jl` already shows how to reconstruct **per-node mean incident curvature** from `per_edge_curvatures`.

### Secondary Python infrastructure

Useful but less canonical:

- `code/analysis/compute_curvature_FINAL.py`
  - GraphRicciCurvature approximation on processed edge lists.
- `code/analysis/kec_framework.py`
  - node-level entropy + approximate ORC + community metrics.
- `code/analysis/clustering_moderation_analysis.py`
  - node-level average incident ORC example.

### Audit conclusion for Q4

If the goal is **maximum scientific continuity with the validated repo**, the best starting point is:

1. Use `english_edges_FINAL.csv`
2. Restrict to the 438-node / 640-edge largest connected component
3. Reuse the exact Julia ORC result from `results/unified/swow_en_exact_lp.json`
4. Derive node-level `κ(v)` from the exact per-edge curvatures

## 5. What results already exist in `results/`?

### Per-edge curvature

#### `results/unified/swow_en_exact_lp.json`

- exact LP ORC for SWOW-EN LCC
- contains:
  - `kappa_mean`
  - `kappa_std`
  - `per_edge_curvatures`
  - graph summary metrics

This is the strongest existing CPC-relevant result artifact.

### Per-node curvature / entropy attempts

#### `results/kec_english_node_level.csv`

- 500 rows
- columns:
  - `name`
  - `entropy`
  - `curvature`
  - `community`
  - `coherence`
- issue:
  - curvature is constant zero for all nodes

#### `results/kec_spanish_node_level.csv`
#### `results/kec_chinese_node_level.csv`

- same pattern: entropy exists, curvature degenerate.

Conclusion: these are not paper-ready, but they show prior intent to compute node-level quantities.

### Entropy outputs

#### `results/entropy_comparison_shannon_vs_spectral.csv`

- network-level entropy summary for:
  - Spanish
  - English
  - Chinese
  - depression severity networks

For English in the current file:

- `n_nodes = 500`
- `n_edges = 13495`
- `H_shannon_transition = 5.6669`

Important caveat:

- this file uses the **dense 500-node English graph** (`english_edges.csv`), not the sparse validated `english_edges_FINAL.csv`.

#### `results/entropy_comparison_with_correlations.json`

- same analysis in JSON form,
- includes depression comparison summaries.

### Trajectory data

#### `results/experiments/ricci_flow_swow_en.json`

- Julia semantic-network Ricci flow result
- includes a `trajectory` array with stepwise:
  - `kappa_mean`
  - `kappa_std`
  - `clustering`
  - weight statistics

#### `results/ricci_flow/ricci_flow_english_real.json`

- Python GraphRicciCurvature Ricci flow result
- includes:
  - `initial_metrics`
  - `final_metrics`
  - full `trajectory`

#### `results/semantic_flow/swow_en/semantic_flow_metrics.json`

- embedding-driven pseudo-flow metrics
- includes:
  - `metrics` per step,
  - graph entropy,
  - mean curvature,
  - clustering,
  - persistence summary

### Not found in `results/`

I did **not** find any existing result files for:

- semantic random-walk trajectories
- nodewise `C_ent`
- valence-biased walks
- Langevin trajectories
- residence times
- Hurst exponents
- DFA summaries
- entropy production over semantic walks

## 6. What is in `manuscript/main.md`?

### Bottom line

`manuscript/main.md` is the **cross-linguistic semantic geometry paper**, not the CPC psychiatric extension.

Title:

- `Boundary Conditions for Hyperbolic Geometry in Semantic Networks`

Subtitle:

- `Clustering-Curvature Trade-offs Revealed by Ollivier-Ricci Analysis`

### Current manuscript focus

The file is explicitly positioned as:

- `Paper 1`
- target journal: `Nature Communications`

Its content centers on:

- cross-linguistic ORC on SWOW / ConceptNet / WordNet / BabelNet,
- clustering-curvature relations,
- structural nulls,
- Ricci flow,
- boundary conditions for hyperbolic geometry.

### What it does not contain

I did **not** find CPC-specific content such as:

- entropic curvature `C_ent`
- psychopathology-like regime simulations on SWOW-EN
- Langevin dynamics
- valence-biased trajectories
- residence-time claims
- Hurst exponent / DFA results
- CPC 2026 title or abstract

### Mild overlap

The manuscript's future directions section mentions:

- clinical populations,
- pathology,
- neuroimaging integration,
- developmental and psychiatric applications.

But this is framing/future work, not the CPC analysis itself.

## Recommended Implementation Decision

For the CPC 2026 implementation, the cleanest scientifically defensible baseline is:

1. Treat `data/processed/english_edges_FINAL.csv` as the canonical SWOW-EN graph artifact.
2. Restrict to its largest connected component to remain consistent with validated ORC outputs.
3. Reuse exact Julia ORC from `results/unified/swow_en_exact_lp.json`.
4. Derive node-level `κ(v)` from the exact per-edge curvatures.
5. Compute node-level local entropy from the existing weights in `english_edges_FINAL.csv`.
6. Add external valence annotations explicitly, because none exist in-repo.
7. Build the CPC simulator from scratch in `code/cpc2026/`, prioritizing the biased Markov chain before any Langevin model.

## Audit Verdict

Phase 0 conclusion:

- **Core ORC infrastructure exists and is reusable.**
- **Node-level entropic curvature does not exist yet.**
- **CPC trajectory simulation code does not exist yet.**
- **Valence annotations do not exist yet.**
- **The repo contains enough validated geometric infrastructure to implement the CPC extension honestly, but not enough to claim the CPC abstract's promised results already exist.**
