#!/usr/bin/env python3
"""
octonion_associator_density_matched.py

The associator-energy ordering (mild>severe>moderate>minimum) is 21/21 permutation-stable
(octonion_associator_permutation_test.py) but the absolute energy tracks density — mild is
densest. This script applies the SAME density-matching used for curvature: subsample every
group to common N*, <k>*, recompute the 8 graph-derived features on the subsample, and
compute associator energy. Reps give a CI. If the ordering survives matched density, the
associator axis is a real group contrast, not a density artifact.
"""
import csv, json, time
from pathlib import Path
import networkx as nx, numpy as np
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from octonion_associator_permutation_test import assoc, load_graph, NODE_METRICS

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "results/unified/octonion_associator_density_matched.json"
GROUPS = ["minimum", "mild", "moderate", "severe"]


def match(g, n_star, k_star, rng):
    nodes = rng.choice(list(g.nodes()), size=min(n_star, g.number_of_nodes()), replace=False)
    h = g.subgraph(nodes).copy()
    h = h.subgraph(max(nx.connected_components(h), key=len)).copy()
    tE = int(round(k_star * h.number_of_nodes() / 2.0))
    e = list(h.edges())
    if len(e) > tE:
        drop = rng.choice(len(e), size=len(e) - tE, replace=False)
        h.remove_edges_from([e[i] for i in drop])
        h = h.subgraph(max(nx.connected_components(h), key=len)).copy()
    return h


def features_sub(group_metrics, h):
    clustering = nx.clustering(h); pr = nx.pagerank(h, max_iter=200); core = nx.core_number(h)
    kap = {n: float(group_metrics[n]["kappa"]) if n in group_metrics else 0.0 for n in h.nodes()}
    feats = {}
    for n in h.nodes():
        m = group_metrics.get(n, {})
        grad = np.mean([kap[w] for w in h.neighbors(n)]) - kap[n] if h.degree(n) else 0.0
        feats[n] = np.array([kap[n], float(m.get("entropy_norm", 0.0)), float(m.get("C_ent", 0.0)),
                             np.log1p(h.degree(n)), clustering[n], pr[n], grad, float(core[n])])
    F = np.array([feats[n] for n in h.nodes()]); mu, sd = F.mean(0), F.std(0); sd[sd == 0] = 1
    Fz = (F - mu) / sd
    return {n: Fz[i] for i, n in enumerate(h.nodes())}


def energy(h, feats, max_triples=20000, seed=0):
    rng = np.random.default_rng(seed)
    triples = [(u, v, w) for u, v in h.edges() for w in nx.common_neighbors(h, u, v)]
    if not triples: return 0.0
    if len(triples) > max_triples:
        triples = [triples[i] for i in rng.choice(len(triples), max_triples, replace=False)]
    acc = 0.0
    for u, v, w in triples:
        e = assoc(feats[u], feats[v], feats[w]); acc += float(e @ e)
    return acc / len(triples)


def main():
    N_STAR, K_STAR, REPS = 1200, 8.0, 8
    graphs = {g: load_graph(g) for g in GROUPS}
    metrics = {g: {} for g in GROUPS}
    for r in csv.DictReader(open(NODE_METRICS)):
        if r["severity"] in metrics: metrics[r["severity"]][r["node"]] = r

    out = {"n_star": N_STAR, "k_star": K_STAR, "reps": REPS, "basis": "identity (ordering is 21/21 perm-stable)", "results": {}}
    t0 = time.time()
    for g in GROUPS:
        rng = np.random.default_rng(42)
        es = []
        for _ in range(REPS):
            h = match(graphs[g], N_STAR, K_STAR, rng)
            es.append(energy(h, features_sub(metrics[g], h), seed=int(rng.integers(1e6))))
        ea = np.array(es)
        out["results"][g] = {"energy_mean": float(ea.mean()), "energy_std": float(ea.std(ddof=1)),
                             "energy_se": float(ea.std(ddof=1) / np.sqrt(len(ea)))}
        print(f"[{g}] matched-density energy = {ea.mean():.3f} +/- {ea.std(ddof=1):.3f} (SE {ea.std(ddof=1)/np.sqrt(len(ea)):.3f})", flush=True)
    order = sorted(GROUPS, key=lambda g: -out["results"][g]["energy_mean"])
    out["order_hi_to_lo"] = order
    out["minimum_lowest"] = (order[-1] == "minimum")
    out["t_s"] = round(time.time() - t0, 1)
    print(f"\nmatched-density energy order (hi->lo): {'>'.join(order)}  minimum_lowest={out['minimum_lowest']}")
    OUT.write_text(json.dumps(out, indent=2)); print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
