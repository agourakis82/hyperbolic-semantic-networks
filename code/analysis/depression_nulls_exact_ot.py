#!/usr/bin/env python3
"""
depression_nulls_exact_ot.py — Exact-OT ORC + degree-preserving null models
for all four depression severity groups.

Ports the methodology of julia/scripts/config_model_nulls.jl (Julia unavailable):
  - Exact Wasserstein-1 via network simplex (POT ot.emd2) — no Sinkhorn bias
  - Lazy random walk measures, alpha = 0.5
  - Largest connected component only
  - Maslov-Sneppen degree-preserving edge rewiring (10*E swaps)
  - z-score, empirical p, delta_kappa per group

Ground-truth check: minimum group kappa_real must match
results/unified/depression_minimum_exact_lp.json (kappa_mean = -0.130267)
and the existing null z-score (~403) in config_model_nulls.json.

Usage:
  python3 depression_nulls_exact_ot.py --groups minimum --n-nulls 3 --time-only
  python3 depression_nulls_exact_ot.py --groups all --n-nulls 5
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
OUT = REPO / "results/unified/depression_nulls_exact_ot.json"

ALPHA = 0.5
GROUPS = ["minimum", "mild", "moderate", "severe"]


def load_graph(group):
    """Load undirected simple graph, largest connected component."""
    path = EDGES_DIR / f"depression_{group}_edges.csv"
    g = nx.Graph()
    with open(path) as f:
        for row in csv.DictReader(f):
            s, t = row["source"], row["target"]
            if s != t:
                g.add_edge(s, t)
    if nx.number_connected_components(g) > 1:
        cc = max(nx.connected_components(g), key=len)
        g = g.subgraph(cc).copy()
    return nx.convert_node_labels_to_integers(g)


def lazy_measure(g, x, alpha=ALPHA):
    """Lazy random-walk probability measure at node x."""
    nbrs = list(g.neighbors(x))
    m = {x: alpha}
    if nbrs:
        w = (1.0 - alpha) / len(nbrs)
        for z in nbrs:
            m[z] = m.get(z, 0.0) + w
    return m


def edge_curvature(g, u, v, dist_cache):
    """Exact Ollivier-Ricci curvature of edge (u,v) via network-simplex OT."""
    mu, nu = lazy_measure(g, u), lazy_measure(g, v)
    src_nodes = list(mu.keys())
    tgt_nodes = list(nu.keys())
    a = np.array([mu[n] for n in src_nodes], dtype=np.float64)
    b = np.array([nu[n] for n in tgt_nodes], dtype=np.float64)
    # Ground cost = shortest-path distance (cached single-source BFS).
    M = np.empty((len(src_nodes), len(tgt_nodes)), dtype=np.float64)
    for i, s in enumerate(src_nodes):
        ds = dist_cache.get(s)
        if ds is None:
            ds = nx.single_source_shortest_path_length(g, s)
            dist_cache[s] = ds
        for j, t in enumerate(tgt_nodes):
            M[i, j] = ds.get(t, len(g))  # disconnected => large
    w1 = ot.emd2(a, b, M)
    return 1.0 - w1  # d(u,v)=1 for an edge


def mean_curvature(g):
    dist_cache = {}
    ks = [edge_curvature(g, u, v, dist_cache) for u, v in g.edges()]
    return float(np.mean(ks)), np.array(ks)


def maslov_sneppen(g, n_swaps_factor=10, seed=0):
    """Degree-preserving double-edge swap (Maslov-Sneppen)."""
    h = g.copy()
    E = h.number_of_edges()
    nx.double_edge_swap(h, nswap=n_swaps_factor * E, max_tries=n_swaps_factor * E * 20, seed=seed)
    return h


def run_group(group, n_nulls, base_seed=42, time_only=False):
    t0 = time.time()
    g = load_graph(group)
    N, E = g.number_of_nodes(), g.number_of_edges()
    kappa_real, _ = mean_curvature(g)
    t_real = time.time() - t0
    print(f"[{group}] N={N} E={E} kappa_real={kappa_real:.6f} "
          f"(real pass {t_real:.1f}s)", flush=True)
    if time_only:
        return {"network_id": f"depression_{group}", "N": N, "E": E,
                "kappa_real": kappa_real, "t_real_s": round(t_real, 1),
                "est_full_s": round(t_real * (1 + n_nulls), 1)}

    null_kappas = []
    for i in range(n_nulls):
        ts = time.time()
        h = maslov_sneppen(g, seed=base_seed + i)
        kn, _ = mean_curvature(h)
        null_kappas.append(kn)
        print(f"  [{group}] null {i+1}/{n_nulls} kappa={kn:.6f} "
              f"({time.time()-ts:.1f}s)", flush=True)

    nk = np.array(null_kappas)
    null_mean, null_std = float(nk.mean()), float(nk.std(ddof=1)) if n_nulls > 1 else None
    z = (kappa_real - null_mean) / null_std if null_std else None
    p_emp = float(np.mean(nk <= kappa_real))  # one-sided: real more hyperbolic?
    return {
        "network_id": f"depression_{group}", "N": N, "E": E,
        "mean_degree": 2.0 * E / N,
        "kappa_real": kappa_real,
        "kappa_null_mean": null_mean, "kappa_null_std": null_std,
        "null_kappas": null_kappas, "n_nulls": n_nulls,
        "delta_kappa": kappa_real - null_mean,
        "z_score": z, "p_empirical": p_emp,
        "t_total_s": round(time.time() - t0, 1),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--groups", default="all")
    ap.add_argument("--n-nulls", type=int, default=5)
    ap.add_argument("--time-only", action="store_true")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    groups = GROUPS if args.groups == "all" else args.groups.split(",")
    results = {
        "method": "maslov_sneppen_edge_rewiring_10E + exact_OT (POT network simplex)",
        "alpha": ALPHA, "seed": args.seed, "n_nulls": args.n_nulls,
        "results": [],
    }
    for grp in groups:
        results["results"].append(
            run_group(grp, args.n_nulls, args.seed, args.time_only))

    if not args.time_only:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(results, indent=2))
        print(f"\nWrote {OUT}")
    print(json.dumps(results["results"], indent=2))


if __name__ == "__main__":
    main()
