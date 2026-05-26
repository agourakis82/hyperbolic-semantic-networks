#!/usr/bin/env python3
"""
octonion_associator_curvature_free.py — discriminating test for axis orthogonality.

The original 8-tuple put kappa (e0) and kappa-gradient (e6) INSIDE the octonion, so the
associator energy could be re-encoding curvature rather than measuring an orthogonal
non-associative structure. This variant uses a CURVATURE-FREE 8-tuple (purely structural,
no kappa anywhere) and repeats the density-matched test.

If the ordering mild>severe>moderate>minimum survives with NO curvature in the algebra,
the associator is a genuine second axis. If it scrambles, "axis 2" was curvature in disguise.

Curvature-free 8-tuple (all per-subsample, structural only):
  e0 log_degree  e1 clustering  e2 pagerank  e3 core_number
  e4 eigenvector_centrality  e5 avg_neighbor_degree  e6 triangles  e7 square_clustering
"""
import json, time
from pathlib import Path
import networkx as nx, numpy as np
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from octonion_associator_permutation_test import assoc, load_graph

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "results/unified/octonion_associator_curvature_free.json"
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


def features_curv_free(h):
    clustering = nx.clustering(h)
    pr = nx.pagerank(h, max_iter=200)
    core = nx.core_number(h)
    try:
        eig = nx.eigenvector_centrality_numpy(h)
    except Exception:
        eig = nx.eigenvector_centrality(h, max_iter=500)
    avgnbr = nx.average_neighbor_degree(h)
    tri = nx.triangles(h)
    sq = nx.square_clustering(h)
    feats = {}
    for n in h.nodes():
        feats[n] = np.array([np.log1p(h.degree(n)), clustering[n], pr[n], float(core[n]),
                             eig[n], avgnbr[n], float(tri[n]), sq[n]])
    F = np.array([feats[n] for n in h.nodes()]); mu, sd = F.mean(0), F.std(0); sd[sd == 0] = 1
    Fz = (F - mu) / sd
    return {n: Fz[i] for i, n in enumerate(h.nodes())}


def energy(h, feats, max_triples=20000, seed=0):
    rng = np.random.default_rng(seed)
    triples = [(u, v, w) for u, v in h.edges() for w in nx.common_neighbors(h, u, v)]
    if not triples: return 0.0, 0
    nt_all = len(triples)
    if len(triples) > max_triples:
        triples = [triples[i] for i in rng.choice(len(triples), max_triples, replace=False)]
    acc = 0.0
    for u, v, w in triples:
        e = assoc(feats[u], feats[v], feats[w]); acc += float(e @ e)
    return acc / len(triples), nt_all


def main():
    N_STAR, K_STAR, REPS = 1200, 8.0, 8
    graphs = {g: load_graph(g) for g in GROUPS}
    out = {"n_star": N_STAR, "k_star": K_STAR, "reps": REPS,
           "feature_set": "curvature-free structural (no kappa)", "results": {}}
    t0 = time.time()
    for g in GROUPS:
        rng = np.random.default_rng(42)
        es, nts = [], []
        for _ in range(REPS):
            h = match(graphs[g], N_STAR, K_STAR, rng)
            e, nt = energy(h, features_curv_free(h), seed=int(rng.integers(1e6)))
            es.append(e); nts.append(nt)
        ea = np.array(es)
        out["results"][g] = {"energy_mean": float(ea.mean()), "energy_std": float(ea.std(ddof=1)),
                             "energy_se": float(ea.std(ddof=1) / np.sqrt(len(ea))),
                             "mean_triples": float(np.mean(nts))}
        print(f"[{g}] curv-free energy = {ea.mean():.3f} +/- {ea.std(ddof=1):.3f} "
              f"(SE {ea.std(ddof=1)/np.sqrt(len(ea)):.3f}, triples~{np.mean(nts):.0f})", flush=True)
    order = sorted(GROUPS, key=lambda g: -out["results"][g]["energy_mean"])
    out["order_hi_to_lo"] = order
    out["minimum_lowest"] = (order[-1] == "minimum")
    out["matches_full_feature_order"] = (order == ["mild", "severe", "moderate", "minimum"])
    out["t_s"] = round(time.time() - t0, 1)
    print(f"\ncurv-free order (hi->lo): {'>'.join(order)}")
    print(f"minimum_lowest={out['minimum_lowest']}  matches_full_feature_order={out['matches_full_feature_order']}")
    print("VERDICT: genuine 2nd axis" if out['minimum_lowest'] else "VERDICT: was curvature in disguise")
    OUT.write_text(json.dumps(out, indent=2)); print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
