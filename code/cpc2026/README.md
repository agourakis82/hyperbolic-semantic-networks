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

Figures land in `figures/cpc2026/`.

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

