# CPC 2026 Pipeline

This directory contains the reproducible Python pipeline for the Computational Psychiatry Conference (CPC) 2026 extension:

**Entropic Curvature in Hyperbolic Semantic Manifolds Indexes Psychopathology-Like Transitions**

## Scope

The pipeline is intentionally reviewer-friendly:

- `valence_loader.py`: downloads and merges Warriner et al. (2013) valence norms onto the validated SWOW-EN graph.
- `entropic_curvature.py`: computes node-level `kappa`, local Shannon entropy, and `C_ent`.
- `trajectory_simulator.py`: simulates regime-specific semantic trajectories and caches a 2D disk embedding for visualization.
- `analysis.py`: computes effect sizes, residence times, entropy production, Hurst exponents, and the geometry reference summary.
- `generate_figures.py`: builds the CPC 2026 figure set as PDF + PNG.
- `ossm_bridge/`: exports 8D SWOW node vectors and compact CSV bundles for the canonical Sounio repo.
- `ossm_reference_simulator.py`: generates the full paper-scale O-SSM artifacts in Python.
- `ossm_analysis.py`: computes O-SSM metrics, subspace occupancy, attractor summaries, and Markov-vs-O-SSM comparisons.
- `generate_ossm_figures.py`: builds the O-SSM figure set as PDF + PNG.
- `network_geometry_claim_gate.py`: audits depression ORC / entropic-curvature
  evidence and emits a conference-safe exploratory network-geometry scope gate.
- `sounio_claim_gate.py`: runs the network-geometry claim audit through the
  Sounio claim spine in `experiments/sounio_cpc2026/`.
- `common.py`: shared paths, graph loading, exact-ORC wrapping, and utility functions.

## Data Choices

This pipeline uses the repo's validated sparse English SWOW graph:

- Input graph: `data/processed/english_edges_FINAL.csv`
- Graph restriction: largest connected component only
- ORC source: `results/unified/swow_en_exact_lp.json`

That means the paper-facing CPC analysis is anchored to the same SWOW-EN substrate already validated elsewhere in the repository.

## Outputs

Main artifacts land in `results/cpc2026/`:

- `node_metrics.parquet`
- `trajectories_{regime}.parquet`
- `trajectory_statistics.parquet`
- `statistical_summary.json`
- `poincare_embedding.parquet`
- `example_trajectories.parquet`
- `ossm_trajectories_{regime}.csv.gz`
- `ossm_trajectory_statistics.parquet`
- `ossm_statistical_summary.json`
- `ossm_cross_model_comparison.csv`
- `ossm_release_manifest.json`
- `depression_orc_network_geometry_scope_gate.json`
- `sounio_depression_orc_claim_gate.json`

Figures land in `figures/cpc2026/`.

Conference claim memo:

- `submission/cpc2026/depression_orc_network_geometry_claim.md`

Bounded canonical Sounio parity outputs are copied into:

- `results/cpc2026/sounio_parity/`

Versioned snapshot note:

- The repository tracks compressed paper-scale O-SSM trajectory archives as `ossm_trajectories_{regime}.csv.gz`.
- The raw `ossm_trajectories_{regime}.csv` files remain local-only because they exceed GitHub's file-size limits.
- The large bridge tensors are versioned as `trajectories_{regime}_input.npz`; the raw `.npy` tensors remain local-only for the same reason.

## Reproduction

Run the whole pipeline from the repository root:

```bash
make cpc2026
```

Or step by step:

```bash
python3 code/cpc2026/valence_loader.py
python3 code/cpc2026/entropic_curvature.py
python3 code/cpc2026/trajectory_simulator.py
python3 code/cpc2026/analysis.py
python3 code/cpc2026/generate_figures.py
```

For the cross-repo O-SSM extension:

```bash
python3 code/cpc2026/ossm_bridge/node_features.py
python3 code/cpc2026/ossm_bridge/trajectory_generator.py
python3 code/cpc2026/ossm_bridge/export_to_sounio.py
python3 code/cpc2026/ossm_reference_simulator.py
python3 code/cpc2026/ossm_analysis.py
python3 code/cpc2026/generate_ossm_figures.py
```

Or from the root:

```bash
make cpc2026-ossm
```

For the depression ORC network-geometry claim audit:

```bash
python3 code/cpc2026/network_geometry_claim_gate.py
# or
make cpc2026-network-geometry
```

For the Sounio-native claim spine:

```bash
python3 code/cpc2026/sounio_claim_gate.py
# or
make cpc2026-sounio-claim
```

The gate is intentionally conservative. It permits exploratory
network-geometry scope-gate language for conference framing, but rejects/avoids
biomarker-candidate, validated clinical biomarker, diagnostic,
clinical-utility, individual-level prediction, treatment-selection, or
external-validation claims until context-of-use and external validation
artifacts exist.

## Smoke Test

For a fast end-to-end check:

```bash
python3 code/cpc2026/valence_loader.py --smoke-test
python3 code/cpc2026/entropic_curvature.py --smoke-test
python3 code/cpc2026/trajectory_simulator.py --smoke-test --include-exploratory-engines
python3 code/cpc2026/analysis.py --smoke-test --bootstrap 200
python3 code/cpc2026/generate_figures.py
```

## Notes

- The biased graph walk is the primary quantitative engine used for the CPC results.
- The Langevin-like and hybrid engines are implemented as exploratory companions and produce cached example trajectories when requested.
- The generic geometric phase transition near `⟨k⟩²/N ≈ 2.5` is imported from the repo's validated random-regular reference results; SWOW-EN itself remains far below that density threshold.
- The canonical Sounio checkout is `github.com/sounio-lang/sounio`; the Sounio lane currently serves as an executable parity path, while the full paper-scale O-SSM artifacts are generated by the Python reference mirror here.
