#!/usr/bin/env python3
"""
depression_density_matched_orc.py — Density-matched exact-OT ORC across severity.

The null-model analysis showed corr(kappa_real, <k>) = +0.991: the severity
curvature ordering is almost entirely a density confound. This script removes
that confound by subsampling all four groups to a COMMON node count N* and a
COMMON mean degree k*, then recomputing exact-OT mean curvature S times per
group. Only a residual kappa difference at matched density is interpretable as
a severity effect.

Protocol per group, repeated S times:
  1. sample N* nodes uniformly from the largest-CC node set
  2. induced subgraph -> largest connected component
  3. random-thin edges to target mean degree k* (re-take largest CC)
  4. exact-OT mean kappa (POT network simplex, lazy walk alpha=0.5)

Output: results/unified/depression_density_matched_orc.json
"""
import argparse
import csv
import json
import time
from pathlib import Path

import networkx as nx
import numpy as np
import ot

REPO = Path(__file__).resolve().parents[2]
EDGES_DIR = REPO / "data/processed/depression_networks_optimal"
OUT = REPO / "results/unified/depression_density_matched_orc.json"

ALPHA = 0.5
GROUPS = ["minimum", "mild", "moderate", "severe"]


def load_graph(group):
    g = nx.Graph()
    with open(EDGES_DIR / f"depression_{group}_edges.csv") as f:
        for row in csv.DictReader(f):
            s, t = row["source"], row["target"]
            if s != t:
                g.add_edge(s, t)
    cc = max(nx.connected_components(g), key=len)
    return nx.convert_node_labels_to_integers(g.subgraph(cc).copy())


def lazy_measure(g, x, alpha=ALPHA):
    nbrs = list(g.neighbors(x))
    m = {x: alpha}
    if nbrs:
        w = (1.0 - alpha) / len(nbrs)
        for z in nbrs:
            m[z] = m.get(z, 0.0) + w
    return m


def mean_curvature(g):
    dist_cache = {}
    ks = []
    for u, v in g.edges():
        mu, nu = lazy_measure(g, u), lazy_measure(g, v)
        sn, tn = list(mu.keys()), list(nu.keys())
        a = np.array([mu[n] for n in sn]); b = np.array([nu[n] for n in tn])
        M = np.empty((len(sn), len(tn)))
        for i, s in enumerate(sn):
            ds = dist_cache.get(s) or dist_cache.setdefault(
                s, nx.single_source_shortest_path_length(g, s))
            for j, t in enumerate(tn):
                M[i, j] = ds.get(t, len(g))
        ks.append(1.0 - ot.emd2(a, b, M))
    return float(np.mean(ks))


def density_match(g, n_star, k_star, rng):
    """Subsample to N* nodes and thin to mean degree k* on the largest CC."""
    nodes = rng.choice(g.number_of_nodes(), size=min(n_star, g.number_of_nodes()),
                       replace=False)
    h = g.subgraph(nodes).copy()
    cc = max(nx.connected_components(h), key=len)
    h = h.subgraph(cc).copy()
    target_E = int(round(k_star * h.number_of_nodes() / 2.0))
    edges = list(h.edges())
    if len(edges) > target_E:
        drop = rng.choice(len(edges), size=len(edges) - target_E, replace=False)
        h.remove_edges_from([edges[i] for i in drop])
        cc = max(nx.connected_components(h), key=len)
        h = h.subgraph(cc).copy()
    return h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-star", type=int, default=1500)
    ap.add_argument("--k-star", type=float, default=10.0)
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    out = {"protocol": "node-subsample to N* + edge-thin to <k>* on largest CC",
           "n_star": args.n_star, "k_star": args.k_star, "reps": args.reps,
           "alpha": ALPHA, "seed": args.seed, "results": []}

    for grp in GROUPS:
        g = load_graph(grp)
        rng = np.random.default_rng(args.seed)
        kappas, achieved_N, achieved_k = [], [], []
        t0 = time.time()
        for r in range(args.reps):
            h = density_match(g, args.n_star, args.k_star, rng)
            kappas.append(mean_curvature(h))
            achieved_N.append(h.number_of_nodes())
            achieved_k.append(2.0 * h.number_of_edges() / h.number_of_nodes())
        ka = np.array(kappas)
        rec = {
            "group": grp, "full_N": g.number_of_nodes(),
            "matched_N_mean": float(np.mean(achieved_N)),
            "matched_k_mean": float(np.mean(achieved_k)),
            "kappa_matched_mean": float(ka.mean()),
            "kappa_matched_std": float(ka.std(ddof=1)),
            "kappa_matched_ci95": [float(ka.mean() - 1.96 * ka.std(ddof=1) / np.sqrt(len(ka))),
                                   float(ka.mean() + 1.96 * ka.std(ddof=1) / np.sqrt(len(ka)))],
            "kappas": kappas, "t_s": round(time.time() - t0, 1),
        }
        out["results"].append(rec)
        print(f"[{grp}] matched N≈{rec['matched_N_mean']:.0f} <k>≈{rec['matched_k_mean']:.1f} "
              f"kappa={rec['kappa_matched_mean']:+.4f}±{rec['kappa_matched_std']:.4f} "
              f"CI95={rec['kappa_matched_ci95'][0]:+.4f},{rec['kappa_matched_ci95'][1]:+.4f} "
              f"({rec['t_s']}s)", flush=True)

    OUT.write_text(json.dumps(out, indent=2))
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
