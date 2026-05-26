#!/usr/bin/env python3
"""
depression_phase_diagram.py — curvature-rank INVARIANCE SURFACE across (N, <k>).

Turns the single-point density-matched result into a 2-D phase diagram:
for every cell (N*, k*) in a grid, subsample all four groups to that size+density,
compute exact-OT mean kappa (reps), a per-cell degree-preserving null (z), and a
representative per-edge kappa distribution for KS separation tests.

Claim under test: the severity rank (minimum > moderate > severe > mild, most→least
hyperbolic) is invariant across the whole feasible (N, <k>) plane — a topological
robustness statement, not a single operating point.

Output: results/unified/depression_phase_diagram.json
"""
import argparse, csv, json, time, itertools
from pathlib import Path
import networkx as nx, numpy as np, ot
from scipy.stats import ks_2samp

REPO = Path(__file__).resolve().parents[2]
EDGES_DIR = REPO / "data/processed/depression_networks_optimal"
OUT = REPO / "results/unified/depression_phase_diagram.json"
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


def lazy(g, x):
    nb = list(g.neighbors(x)); m = {x: ALPHA}
    if nb:
        w = (1 - ALPHA) / len(nb)
        for z in nb: m[z] = m.get(z, 0.0) + w
    return m


def curvatures(g):
    dc = {}; ks = []
    for u, v in g.edges():
        mu, nu = lazy(g, u), lazy(g, v)
        sn, tn = list(mu), list(nu)
        a = np.array([mu[n] for n in sn]); b = np.array([nu[n] for n in tn])
        M = np.empty((len(sn), len(tn)))
        for i, s in enumerate(sn):
            ds = dc.get(s) or dc.setdefault(s, nx.single_source_shortest_path_length(g, s))
            for j, t in enumerate(tn): M[i, j] = ds.get(t, len(g))
        ks.append(1.0 - ot.emd2(a, b, M))
    return np.array(ks)


def match(g, n_star, k_star, rng):
    nodes = rng.choice(g.number_of_nodes(), size=min(n_star, g.number_of_nodes()), replace=False)
    h = g.subgraph(nodes).copy()
    h = h.subgraph(max(nx.connected_components(h), key=len)).copy()
    tE = int(round(k_star * h.number_of_nodes() / 2.0))
    e = list(h.edges())
    if len(e) > tE:
        drop = rng.choice(len(e), size=len(e) - tE, replace=False)
        h.remove_edges_from([e[i] for i in drop])
        h = h.subgraph(max(nx.connected_components(h), key=len)).copy()
    return h


def null_kappa(h, rng_seed):
    hr = h.copy()
    E = hr.number_of_edges()
    nx.double_edge_swap(hr, nswap=10 * E, max_tries=200 * E, seed=rng_seed)
    return float(curvatures(hr).mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", default="1000,1400")
    ap.add_argument("--k", default="6,8,10")
    ap.add_argument("--reps", type=int, default=6)
    ap.add_argument("--nulls", type=int, default=2)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    Ns = [int(x) for x in args.N.split(",")]
    ks = [float(x) for x in args.k.split(",")]

    graphs = {g: load_graph(g) for g in GROUPS}
    out = {"grid_N": Ns, "grid_k": ks, "reps": args.reps, "nulls": args.nulls,
           "alpha": ALPHA, "seed": args.seed, "cells": []}

    for N_star, k_star in itertools.product(Ns, ks):
        t0 = time.time()
        cell = {"N_star": N_star, "k_star": k_star, "groups": {}}
        edge_dists = {}
        for g in GROUPS:
            rng = np.random.default_rng(args.seed)
            kaps, last_dist = [], None
            for r in range(args.reps):
                h = match(graphs[g], N_star, k_star, rng)
                cv = curvatures(h)
                kaps.append(float(cv.mean())); last_dist = cv
            edge_dists[g] = last_dist
            ka = np.array(kaps)
            nulls = [null_kappa(match(graphs[g], N_star, k_star, np.random.default_rng(args.seed + 100 + i)),
                                 args.seed + 200 + i) for i in range(args.nulls)]
            nm = float(np.mean(nulls)); ns = float(np.std(nulls, ddof=1)) if args.nulls > 1 else None
            cell["groups"][g] = {
                "kappa_mean": float(ka.mean()), "kappa_std": float(ka.std(ddof=1)),
                "kappa_se": float(ka.std(ddof=1) / np.sqrt(len(ka))),
                "null_mean": nm, "null_std": ns,
                "z_vs_null": (float(ka.mean()) - nm) / ns if ns else None,
            }
        # rank (most→least hyperbolic) and whether it equals canonical
        order = sorted(GROUPS, key=lambda g: cell["groups"][g]["kappa_mean"])
        cell["rank"] = order
        cell["rank_matches_canonical"] = (order == ["minimum", "moderate", "severe", "mild"])
        # pairwise KS on per-edge distributions
        cell["ks"] = {}
        for a, b in itertools.combinations(GROUPS, 2):
            st, p = ks_2samp(edge_dists[a], edge_dists[b])
            cell["ks"][f"{a}|{b}"] = {"stat": float(st), "p": float(p)}
        cell["t_s"] = round(time.time() - t0, 1)
        out["cells"].append(cell)
        km = {g: round(cell["groups"][g]["kappa_mean"], 4) for g in GROUPS}
        print(f"[N={N_star} k={k_star}] rank={'>'.join(order)} canonical={cell['rank_matches_canonical']} "
              f"kappas={km} ({cell['t_s']}s)", flush=True)

    n_match = sum(c["rank_matches_canonical"] for c in out["cells"])
    out["rank_invariance"] = f"{n_match}/{len(out['cells'])} cells match canonical rank"
    print(f"\nRANK INVARIANCE: {out['rank_invariance']}")
    OUT.write_text(json.dumps(out, indent=2))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
