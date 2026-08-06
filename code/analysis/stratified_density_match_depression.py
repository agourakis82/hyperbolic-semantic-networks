#!/usr/bin/env python3
"""DECISIVE pre-conference stress test: does the depression-severity κ ordering survive the STRICTER
stratified density-DISTRIBUTION match?

The flagship conference finding (subclinical 'minimum' most hyperbolic; minimum>moderate>severe>mild
in most-negative-κ) survived MEAN density-matching (common N, ⟨k⟩) + a 6-cell phase diagram. But mean-
matching ≠ matching the density DISTRIBUTION. On chb01 this week, a range-clip match said 'significant'
while the stratified distribution-match flipped it to null (p=0.88). This applies the same stricter
control to the depression data, edge-level:

  * per-edge Ollivier-Ricci κ (exact OT, lazy walk α=0.5) on each group's network (subsampled to a
    common N for equal node count)
  * per-edge local-density covariate d_e = mean endpoint degree (the quantity ORC is most sensitive to)
  * bin edges by pooled d_e deciles; within each bin compare the 4 groups at MATCHED local density
  * verdict: does the canonical ordering survive at matched density (curvature-specific) or collapse
    (density-carried)?

Honest, two-sided. This decides how the HK/Yale talks should frame ORC.
"""

import csv
import json
import os
import random
from pathlib import Path
import numpy as np
import networkx as nx
import ot

EDGES = Path(__file__).resolve().parents[2] / "data/processed/depression_networks_optimal"
OUT = Path(__file__).resolve().parents[2] / "results/unified"
GROUPS = ["minimum", "mild", "moderate", "severe"]
ALPHA = 0.5
N_SUB = int(os.environ.get("N_SUB", "1000"))   # common node count per group (env-overridable)
SEED = 20260527
N_BINS = 10


def load_graph(group):
    g = nx.Graph()
    with open(EDGES / f"depression_{group}_edges.csv") as f:
        for row in csv.DictReader(f):
            if row["source"] != row["target"]:
                g.add_edge(row["source"], row["target"])
    cc = max(nx.connected_components(g), key=len)
    g = g.subgraph(cc).copy()
    return g


def subsample(g, n, rng):
    if g.number_of_nodes() <= n:
        h = g
    else:
        nodes = rng.sample(list(g.nodes()), n)
        h = g.subgraph(nodes).copy()
    cc = max(nx.connected_components(h), key=len)
    return nx.convert_node_labels_to_integers(h.subgraph(cc).copy())


def lazy_measure(g, x):
    nbrs = list(g.neighbors(x))
    m = {x: ALPHA}
    if nbrs:
        w = (1.0 - ALPHA) / len(nbrs)
        for z in nbrs:
            m[z] = m.get(z, 0.0) + w
    return m


def per_edge_kappa(g):
    """Return arrays: kappa per edge, and mean-endpoint-degree per edge."""
    deg = dict(g.degree())
    dist_cache = {}
    ks, dens = [], []
    for u, v in g.edges():
        mu, nu = lazy_measure(g, u), lazy_measure(g, v)
        sn, tn = list(mu), list(nu)
        a = np.array([mu[s] for s in sn]); b = np.array([nu[t] for t in tn])
        M = np.empty((len(sn), len(tn)))
        for i, s in enumerate(sn):
            ds = dist_cache.get(s)
            if ds is None:
                ds = nx.single_source_shortest_path_length(g, s)
                dist_cache[s] = ds
            for j, t in enumerate(tn):
                M[i, j] = ds.get(t, len(g))
        w1 = ot.emd2(a, b, M)
        ks.append(1.0 - w1)                       # d(u,v)=1 for an edge
        dens.append(0.5 * (deg[u] + deg[v]))
    return np.array(ks), np.array(dens)


N_SEEDS = int(os.environ.get("N_SEEDS", "8"))


def one_draw(seed):
    """One subsample+stratified-match draw. Returns (raw_means, matched_means, matched_edge_kappa_by_group)."""
    rng = random.Random(seed)
    per = {}
    for grp in GROUPS:
        g = subsample(load_graph(grp), N_SUB, rng)
        ks, dens = per_edge_kappa(g)
        per[grp] = {"kappa": ks, "dens": dens}
    raw = {grp: float(per[grp]["kappa"].mean()) for grp in GROUPS}
    all_d = np.concatenate([per[g]["dens"] for g in GROUPS])
    edges = np.quantile(all_d, np.linspace(0, 1, N_BINS + 1)); edges[-1] += 1e-9
    matched = {g: [] for g in GROUPS}
    for b in range(N_BINS):
        lo, hi = edges[b], edges[b + 1]
        pools = {g: per[g]["kappa"][(per[g]["dens"] >= lo) & (per[g]["dens"] < hi)] for g in GROUPS}
        m = min(len(pools[g]) for g in GROUPS)
        if m < 5:
            continue
        for g in GROUPS:
            matched[g].extend(rng.sample(list(pools[g]), m))
    matched_mean = {g: float(np.mean(matched[g])) for g in GROUPS}
    return raw, matched_mean, matched


def main():
    from scipy.stats import mannwhitneyu
    raws, matcheds, min_most, order_pres, mw_ps = [], [], 0, 0, []
    last_matched_edges = None
    for s in range(N_SEEDS):
        raw, mm, matched_edges = one_draw(SEED + s)
        raws.append(raw); matcheds.append(mm); last_matched_edges = matched_edges
        mo = sorted(GROUPS, key=lambda g: mm[g])
        if mo.index("minimum") == 0:
            min_most += 1
        ro = sorted(GROUPS, key=lambda g: raw[g])
        if mo == ro:
            order_pres += 1
        # significance: minimum matched edges vs pooled clinical matched edges (more negative κ?)
        clin = matched_edges["mild"] + matched_edges["moderate"] + matched_edges["severe"]
        U, p = mannwhitneyu(matched_edges["minimum"], clin, alternative="less")  # H1: minimum < clinical
        mw_ps.append(p)
        print(f"seed {SEED+s}: matched order={mo}  min_κ={mm['minimum']:+.4f}  "
              f"clin_med κ≈{np.median(clin):+.4f}  MW(min<clin) p={p:.2e}")

    # aggregate matched means ± across seeds
    agg = {g: (float(np.mean([m[g] for m in matcheds])), float(np.std([m[g] for m in matcheds]))) for g in GROUPS}
    print(f"\n=== {N_SEEDS} seeds ===")
    print("matched mean κ (mean±sd across seeds):")
    for g in sorted(GROUPS, key=lambda g: agg[g][0]):
        print(f"  {g:9s}: {agg[g][0]:+.4f} ± {agg[g][1]:.4f}")
    print(f"minimum-most-hyperbolic in {min_most}/{N_SEEDS} seeds; full raw-order preserved in {order_pres}/{N_SEEDS}")
    print(f"MW(minimum<clinical) matched-edge p: median={np.median(mw_ps):.2e}, max={max(mw_ps):.2e}")

    survives = (min_most == N_SEEDS) and (max(mw_ps) < 0.01)
    verdict = ("SURVIVES — subclinical-most-hyperbolic holds at matched density-distribution in ALL seeds "
               "with p<.01; the conference biomarker is robust to the strictest density control. Show this slide."
               if survives else
               "FRAGILE — does not hold across all seeds / not significant; reframe as density-sensitive lens.")
    print(f"\nVERDICT: {verdict}")

    OUT.mkdir(parents=True, exist_ok=True)
    tag = "" if N_SUB == 1000 else f"_N{N_SUB}"
    with open(OUT / f"stratified_density_match_depression{tag}.json", "w") as f:
        json.dump({"params": {"alpha": ALPHA, "n_sub": N_SUB, "n_bins": N_BINS, "n_seeds": N_SEEDS},
                   "matched_mean_kappa_mean_sd": {g: agg[g] for g in GROUPS},
                   "minimum_most_hyperbolic_seeds": f"{min_most}/{N_SEEDS}",
                   "raw_order_preserved_seeds": f"{order_pres}/{N_SEEDS}",
                   "mw_min_lt_clin_p_median": float(np.median(mw_ps)),
                   "mw_min_lt_clin_p_max": float(max(mw_ps)),
                   "verdict": verdict}, f, indent=2)
    print(f"wrote {OUT / 'stratified_density_match_depression.json'}")


if __name__ == "__main__":
    main()
