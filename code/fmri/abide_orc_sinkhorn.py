#!/usr/bin/env python3
"""
B3: Sinkhorn ORC Cross-Validation — ABIDE-I Brain Graphs

Fast approximate ORC via GraphRicciCurvature (Sinkhorn) for all subjects.
Used as: (1) quick full-cohort analysis, (2) cross-validation against Julia LP.

Usage:
    python code/fmri/abide_orc_sinkhorn.py
    python code/fmri/abide_orc_sinkhorn.py --threshold 0.50

Output:
    results/fmri/abide_orc_sinkhorn_t{threshold}.json
"""

import argparse
import json
import time
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from GraphRicciCurvature.OllivierRicci import OllivierRicci

# ── Paths ────────────────────────────────────────────────────────────────────

GRAPH_DIR = Path("data/processed/abide_graphs")
PHENO_CSV = Path("data/processed/abide_phenotypic_matched.csv")
RESULTS_DIR = Path("results/fmri")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

ALPHA = 0.5
ETA_C_200 = 3.75 - 14.62 / (200 ** 0.5)


def load_graph(edge_file):
    """Load edge CSV → NetworkX graph."""
    df = pd.read_csv(edge_file)
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(int(row["source"]), int(row["target"]))
    return G


def compute_orc_sinkhorn(G):
    """Compute ORC via Sinkhorn (GraphRicciCurvature library)."""
    orc = OllivierRicci(G, alpha=ALPHA, verbose="ERROR", proc=1)
    orc.compute_ricci_curvature()
    kappas = [
        orc.G[u][v]["ricciCurvature"]
        for u, v in orc.G.edges()
    ]
    return kappas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=float, default=0.40)
    args = parser.parse_args()
    threshold = args.threshold

    pheno = pd.read_csv(PHENO_CSV)
    print(f"ABIDE-I Brain ORC — Sinkhorn (α={ALPHA}, threshold={threshold})")
    print(f"η_c(N=200) = {ETA_C_200:.3f}")
    print(f"Subjects: {len(pheno)}")
    print("=" * 60)

    results = []
    for _, row in pheno.iterrows():
        file_id = row["file_id"]
        edge_file = GRAPH_DIR / f"{file_id}_t{threshold:.2f}_edges.csv"

        if not edge_file.exists():
            print(f"  SKIP {file_id}: edge file missing")
            continue

        t0 = time.time()
        G = load_graph(edge_file)

        # LCC
        if not nx.is_connected(G):
            lcc_nodes = max(nx.connected_components(G), key=len)
            G = G.subgraph(lcc_nodes).copy()

        N = G.number_of_nodes()
        E = G.number_of_edges()
        mean_k = 2 * E / N
        eta = mean_k ** 2 / N

        kappas = compute_orc_sinkhorn(G)
        kappa_mean = np.mean(kappas)
        kappa_std = np.std(kappas)
        frac_pos = np.mean([k > 0 for k in kappas])
        elapsed = time.time() - t0

        geometry = "SPHERICAL" if (eta > ETA_C_200 and kappa_mean > 0) else \
                   "HYPERBOLIC" if (eta < ETA_C_200 and kappa_mean < 0) else \
                   "ANOMALOUS"

        print(f"  {file_id}: N={N}, E={E}, η={eta:.2f}, "
              f"κ̄={kappa_mean:+.4f} ({geometry}) [{elapsed:.1f}s]")

        results.append({
            "file_id": file_id,
            "dx_group": int(row["dx_group"]),
            "site_id": row["site_id"],
            "threshold": threshold,
            "N": N,
            "n_edges": E,
            "mean_k": round(mean_k, 2),
            "eta": round(eta, 4),
            "kappa_mean": round(float(kappa_mean), 6),
            "kappa_std": round(float(kappa_std), 6),
            "frac_positive": round(float(frac_pos), 4),
            "geometry": geometry,
            "elapsed_s": round(elapsed, 1),
        })

    # Summary
    print("\n" + "=" * 60)
    for dx, label in [(1, "ASD"), (2, "Control")]:
        group = [r for r in results if r["dx_group"] == dx]
        if group:
            etas = [r["eta"] for r in group]
            kappas = [r["kappa_mean"] for r in group]
            print(f"  {label} (n={len(group)}): η={np.mean(etas):.2f}±{np.std(etas):.2f}, "
                  f"κ̄={np.mean(kappas):+.4f}±{np.std(kappas):.4f}")

    out_path = RESULTS_DIR / f"abide_orc_sinkhorn_t{threshold:.2f}.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {out_path}")


if __name__ == "__main__":
    main()
