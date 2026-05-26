#!/usr/bin/env python3
"""
octonion_associator_permutation_test.py

The octonion associator [a,b,c] = (a·b)·c - a·(b·c) is a non-associativity invariant.
A fair objection (advisor): the 8 node features are a heterogeneous vector, so assigning
them to octonion basis units e0..e7 is arbitrary — under a basis permutation the absolute
associator energy changes. The SCIENTIFICALLY relevant question is therefore NOT "is the
energy basis-invariant" (it is not — octonion mult is non-commutative in components) but:

    Does the GROUP SEPARATION (e.g. minimum vs clinical) keep its sign/rank across random
    basis assignments?

If the ordering is stable across permutations, the associator axis is a defensible group
contrast despite basis-dependence of the absolute value. If it flips arbitrarily, drop it.

8 per-group node features (all graph-derived, per severity group):
  e0 kappa  e1 entropy_norm  e2 C_ent  e3 log_degree
  e4 clustering  e5 pagerank  e6 local kappa-gradient  e7 core_number
"""
import csv, json, time
from collections import defaultdict
from pathlib import Path
import networkx as nx, numpy as np

REPO = Path(__file__).resolve().parents[2]
EDGES_DIR = REPO / "data/processed/depression_networks_optimal"
NODE_METRICS = REPO / "results/cpc2026/depression_node_metrics.csv"
OUT = REPO / "results/unified/octonion_associator_permutation_test.json"
GROUPS = ["minimum", "mild", "moderate", "severe"]

# Octonion multiplication table (Cayley-Dickson, standard basis). mult[i][j] = (sign, index)
def _build_oct_table():
    # Quaternion-extended Cayley-Dickson construction.
    # Use known octonion table (e0=1). Signs per standard reference.
    T = [[(1, 0)] * 8 for _ in range(8)]
    # e0 is identity
    for i in range(8):
        T[0][i] = (1, i); T[i][0] = (1, i)
    # imaginary units square to -e0
    for i in range(1, 8):
        T[i][i] = (-1, 0)
    # triples (Fano lines) that multiply cyclically to +: standard octonion
    lines = [(1,2,3),(1,4,5),(1,7,6),(2,4,6),(2,5,7),(3,4,7),(3,6,5)]
    for a, b, c in lines:
        for x, y, z in [(a,b,c),(b,c,a),(c,a,b)]:
            T[x][y] = (1, z); T[y][x] = (-1, z)
    return T

OCT = _build_oct_table()

def omul(p, q):
    r = np.zeros(8)
    for i in range(8):
        if p[i] == 0.0: continue
        for j in range(8):
            if q[j] == 0.0: continue
            s, k = OCT[i][j]
            r[k] += s * p[i] * q[j]
    return r

def assoc(a, b, c):
    return omul(omul(a, b), c) - omul(a, omul(b, c))


def load_graph(group):
    g = nx.Graph()
    with open(EDGES_DIR / f"depression_{group}_edges.csv") as f:
        for row in csv.DictReader(f):
            s, t = row["source"], row["target"]
            if s != t: g.add_edge(s, t)
    return g.subgraph(max(nx.connected_components(g), key=len)).copy()


def node_features(group, g):
    """8-component per-node feature vector, z-scored per component."""
    # per-group metrics from CSV
    met = {}
    for r in csv.DictReader(open(NODE_METRICS)):
        if r["severity"] == group:
            met[r["node"]] = r
    clustering = nx.clustering(g)
    pr = nx.pagerank(g, max_iter=200)
    core = nx.core_number(g)
    kap = {n: float(met[n]["kappa"]) if n in met else 0.0 for n in g.nodes()}
    feats = {}
    for n in g.nodes():
        m = met.get(n, {})
        grad = np.mean([kap[w] for w in g.neighbors(n)]) - kap[n] if g.degree(n) else 0.0
        feats[n] = np.array([
            kap[n],
            float(m.get("entropy_norm", 0.0)),
            float(m.get("C_ent", 0.0)),
            np.log1p(g.degree(n)),
            clustering[n],
            pr[n],
            grad,
            float(core[n]),
        ])
    F = np.array([feats[n] for n in g.nodes()])
    mu, sd = F.mean(0), F.std(0); sd[sd == 0] = 1.0
    Fz = (F - mu) / sd
    return {n: Fz[i] for i, n in enumerate(g.nodes())}


def associator_energy(g, feats, perm, max_triples=20000, seed=0):
    """Mean |assoc|^2 over edge × common-neighbor triples, under basis permutation `perm`."""
    rng = np.random.default_rng(seed)
    # collect triples (u,v,w): edge (u,v) with common neighbor w
    triples = []
    for u, v in g.edges():
        cn = list(nx.common_neighbors(g, u, v))
        for w in cn:
            triples.append((u, v, w))
    if len(triples) > max_triples:
        idx = rng.choice(len(triples), size=max_triples, replace=False)
        triples = [triples[i] for i in idx]
    if not triples:
        return 0.0, 0
    acc = 0.0
    for u, v, w in triples:
        a = feats[u][perm]; b = feats[v][perm]; c = feats[w][perm]
        e = assoc(a, b, c)
        acc += float(e @ e)
    return acc / len(triples), len(triples)


def main():
    t0 = time.time()
    graphs = {g: load_graph(g) for g in GROUPS}
    feats = {g: node_features(g, graphs[g]) for g in GROUPS}
    print("features built", flush=True)

    identity = np.arange(8)
    n_perms = 20
    rng = np.random.default_rng(7)
    # permutations of the 7 IMAGINARY units (keep e0=identity fixed — permuting the
    # real unit would break the algebra's identity element).
    perms = [identity.copy()]
    for _ in range(n_perms):
        p = np.arange(8); p[1:] = 1 + rng.permutation(7); perms.append(p)

    results = {"n_perms": n_perms + 1, "energies": [], "rank_per_perm": []}
    canon_ranks = defaultdict(int)
    min_top = 0
    for pi, perm in enumerate(perms):
        en = {}
        for g in GROUPS:
            e, nt = associator_energy(graphs[g], feats[g], perm, seed=100 + pi)
            en[g] = e
        order = sorted(GROUPS, key=lambda g: -en[g])  # highest energy first
        results["energies"].append({"perm": perm.tolist(), **{g: en[g] for g in GROUPS}})
        results["rank_per_perm"].append(order)
        canon_ranks[tuple(order)] += 1
        if order[0] == "minimum": min_top += 1
        tag = "IDENTITY" if pi == 0 else f"perm{pi}"
        print(f"[{tag}] energy order(hi→lo)={'>'.join(order)} "
              f"min={en['minimum']:.3f} mild={en['mild']:.3f} "
              f"mod={en['moderate']:.3f} sev={en['severe']:.3f}", flush=True)

    results["minimum_is_highest_frac"] = min_top / len(perms)
    results["distinct_orderings"] = {">".join(k): v for k, v in canon_ranks.items()}
    results["t_s"] = round(time.time() - t0, 1)
    print(f"\nminimum-highest-energy in {min_top}/{len(perms)} basis assignments")
    print(f"distinct orderings: {results['distinct_orderings']}")
    OUT.write_text(json.dumps(results, indent=2))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
