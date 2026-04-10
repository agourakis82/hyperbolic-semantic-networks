#!/usr/bin/env python3
"""
A2: Threshold Sweep & Graph Export — ABIDE-I FC → Binary Adjacency → Edge Lists

For each subject's Fisher z-transformed FC matrix, applies multiple correlation
thresholds to produce binary graphs, computes graph statistics (N, E, mean_k, eta),
and exports edge lists for Julia ORC computation.

Key: eta_c(N=200) = 3.75 - 14.62/sqrt(200) = 2.72

Usage:
    python code/fmri/abide_threshold_graphs.py

Output:
    data/processed/abide_graphs/{file_id}_t{threshold}_edges.csv  — edge lists
    results/fmri/abide_threshold_stats.json                       — per-subject stats
"""

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

# ── Paths ────────────────────────────────────────────────────────────────────

FC_DIR = Path("data/processed/abide_fc")
GRAPH_DIR = Path("data/processed/abide_graphs")
GRAPH_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR = Path("results/fmri")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
PHENO_CSV = Path("data/processed/abide_phenotypic_matched.csv")

# ── Parameters ───────────────────────────────────────────────────────────────

THRESHOLDS = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50]
N_ROIS = 200
ETA_C_200 = 3.75 - 14.62 / (200 ** 0.5)  # ≈ 2.72

# ── Functions ────────────────────────────────────────────────────────────────


def threshold_to_graph(z_fc, threshold):
    """Binary adjacency from |z_fc| > threshold. Returns edge list and stats."""
    adj = (np.abs(z_fc) > threshold).astype(int)
    np.fill_diagonal(adj, 0)
    # Make symmetric (should already be, but enforce)
    adj = np.maximum(adj, adj.T)

    # Edge list (upper triangle only to avoid duplicates)
    rows, cols = np.triu_indices(N_ROIS, k=1)
    mask = adj[rows, cols] > 0
    edges = list(zip(rows[mask].tolist(), cols[mask].tolist()))

    n_edges = len(edges)
    if n_edges == 0:
        return edges, {"n_edges": 0, "mean_k": 0, "eta": 0, "lcc_frac": 0}

    degrees = adj.sum(axis=1)
    mean_k = degrees.mean()
    eta = mean_k ** 2 / N_ROIS

    # LCC via BFS
    lcc_frac = _lcc_fraction(adj)

    return edges, {
        "n_edges": n_edges,
        "mean_k": round(float(mean_k), 2),
        "eta": round(float(eta), 4),
        "lcc_frac": round(float(lcc_frac), 4),
        "max_degree": int(degrees.max()),
        "min_degree": int(degrees.min()),
    }


def _lcc_fraction(adj):
    """Fraction of nodes in largest connected component."""
    n = adj.shape[0]
    visited = np.zeros(n, dtype=bool)
    max_size = 0
    for start in range(n):
        if visited[start]:
            continue
        # BFS
        queue = [start]
        visited[start] = True
        size = 0
        while queue:
            node = queue.pop(0)
            size += 1
            for nb in range(n):
                if adj[node, nb] > 0 and not visited[nb]:
                    visited[nb] = True
                    queue.append(nb)
        max_size = max(max_size, size)
    return max_size / n


def export_edgelist(edges, filepath):
    """Write edges as CSV: source,target."""
    with open(filepath, "w") as f:
        f.write("source,target\n")
        for u, v in edges:
            f.write(f"{u},{v}\n")


def main():
    if not PHENO_CSV.exists():
        print("ERROR: Run compute_abide_fc.py first.")
        return

    pheno = pd.read_csv(PHENO_CSV)
    print(f"Processing {len(pheno)} subjects × {len(THRESHOLDS)} thresholds")
    print(f"eta_c(N=200) = {ETA_C_200:.3f}")

    all_stats = []

    for _, row in pheno.iterrows():
        file_id = row["file_id"]
        fc_path = FC_DIR / f"{file_id}_fc.npz"

        if not fc_path.exists():
            print(f"  SKIP {file_id}: FC file missing")
            continue

        data = np.load(fc_path)
        z_fc = data["z_fc"]

        subject_stats = {
            "file_id": file_id,
            "dx_group": int(row["dx_group"]),
            "site_id": row["site_id"],
            "age": float(row["age"]),
            "eta_c": round(ETA_C_200, 4),
            "thresholds": {},
        }

        for t in THRESHOLDS:
            edges, stats = threshold_to_graph(z_fc, t)

            # Export edge list
            edge_file = GRAPH_DIR / f"{file_id}_t{t:.2f}_edges.csv"
            if edges:
                export_edgelist(edges, edge_file)

            stats["threshold"] = t
            stats["above_eta_c"] = stats["eta"] > ETA_C_200
            subject_stats["thresholds"][f"{t:.2f}"] = stats

        all_stats.append(subject_stats)

    # Save full stats
    out_path = RESULTS_DIR / "abide_threshold_stats.json"
    with open(out_path, "w") as f:
        json.dump(all_stats, f, indent=2)

    # Print summary table
    print(f"\n{'='*80}")
    print(f"{'Threshold':>10} {'Mean η':>8} {'Mean k':>8} {'η>η_c':>7} {'LCC>0.95':>9}")
    print(f"{'-'*80}")

    for t in THRESHOLDS:
        etas = [s["thresholds"][f"{t:.2f}"]["eta"] for s in all_stats
                if f"{t:.2f}" in s["thresholds"]]
        ks = [s["thresholds"][f"{t:.2f}"]["mean_k"] for s in all_stats
              if f"{t:.2f}" in s["thresholds"]]
        above = sum(1 for e in etas if e > ETA_C_200)
        lccs = [s["thresholds"][f"{t:.2f}"]["lcc_frac"] for s in all_stats
                if f"{t:.2f}" in s["thresholds"]]
        conn = sum(1 for l in lccs if l > 0.95)

        print(f"{t:>10.2f} {np.mean(etas):>8.2f} {np.mean(ks):>8.1f} "
              f"{above:>4}/{len(etas):<3} {conn:>5}/{len(lccs):<3}")

    # Per-group summary at t=0.30
    t_key = "0.30"
    for dx, label in [(1, "ASD"), (2, "Control")]:
        group_etas = [s["thresholds"][t_key]["eta"] for s in all_stats
                      if s["dx_group"] == dx and t_key in s["thresholds"]]
        if group_etas:
            print(f"\n{label} (n={len(group_etas)}): "
                  f"η = {np.mean(group_etas):.3f} ± {np.std(group_etas):.3f}")

    print(f"\nResults saved to: {out_path}")
    print(f"Edge lists saved to: {GRAPH_DIR}/")


if __name__ == "__main__":
    main()
