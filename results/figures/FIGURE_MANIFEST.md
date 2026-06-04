# Figure manifest — v2.0-final (7-graph dataset)

The manuscript analyzes **7 semantic graphs** (4 SWOW + 3 taxonomy; ConceptNet removed).
Figures 1 and 4 depend on that dataset and were **regenerated** from
`results/phase_diagram_metrics_7graph.csv` (script: `code/analysis/generate_7graph_figures.py`).

| Manuscript | CANONICAL file (use this) | Superseded (8-graph, do NOT use) |
| --- | --- | --- |
| **Figure 1 – Clustering–Curvature Map** | `figure1_clustering_curvature_7graph.png` | `clustering_curvature_spectrum.png` |
| Figure 2 – Structural Null Models | `clustering_moderation_comparison.png` (SWOW ES/EN/ZH; unaffected) | — |
| Figure 3 – Ricci Flow Resistance | (representative networks; unaffected) | — |
| **Figure 4 – Phase Diagram** | `figure4_phase_diagram_7graph.png` | (no 8-graph phase-diagram PNG in repo) |

Figures 2 and 3 are unchanged by the ConceptNet removal (null models run on SWOW ES/EN/ZH;
Ricci-flow on representative real+null networks). Only Figures 1 and 4 contained ConceptNet points.

ACTION: the PDF build / submission portal should pull `figure1_clustering_curvature_7graph.png`
and `figure4_phase_diagram_7graph.png` for Figures 1 and 4.
