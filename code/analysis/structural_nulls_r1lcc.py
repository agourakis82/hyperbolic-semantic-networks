#!/usr/bin/env python3
"""
Degree-matched configuration-model nulls for the R1/LCC-canonical SWOW networks.

Replaces the pre-correction run (07_structural_nulls.py, directed graphs on
{lang}_edges.csv) with a run that matches the canonical unified ORC pipeline
(julia/scripts/unified_semantic_orc.jl and config_model_nulls.jl):

  - input:   data/processed/{lang}_edges_FINAL.csv  (R1-canonical)
  - graph:   undirected, simple, largest connected component
  - ORC:     alpha = 0.5, uniform neighbour mass, integer hop-distance costs,
             exact Wasserstein-1 per edge via LP (scipy linprog, HiGHS)
  - nulls:   connected double-edge swaps (degree-preserving Maslov-Sneppen
             chain conditioned on connectivity, networkx implementation,
             10x|E| swaps per null), M = 1000. Plain rejection sampling is
             infeasible here: on these sparse LCCs fewer than ~20% of
             unconstrained rewires stay connected (0.75% for swow_es).
  - stats:   DIRECTIONAL gap delta_kappa = kappa_real - mean(kappa_null),
             one-sided Monte-Carlo p per tail, two-sided p, Cliff's delta,
             95% percentile CI, z-score.

Validation gate: the real kappa_mean recomputed here must match the canonical
results/unified/{id}_exact_lp.json within TOL before any nulls are generated.

Author: Demetrios Chiuratto Agourakis
Date: 2026-07-11
"""

import json
import subprocess
import sys
import time
from collections import deque
from multiprocessing import Pool
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from scipy.optimize import linprog

REPO = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO / "data" / "processed"
REF_DIR = REPO / "results" / "unified"
OUT_DIR = REPO / "results" / "structural_nulls"

ALPHA = 0.5
M_TARGET = 1000
MAX_ATTEMPTS_FACTOR = 1.05  # small buffer; the connected chain never disconnects
SWAP_FACTOR = 10         # successful swaps per rewire = SWAP_FACTOR * |E|
TOL = 5e-3               # gate: |kappa_real(here) - kappa_ref(exact_lp.json)| must be < TOL
WORKERS = 14             # CPU-discipline ceiling on the shared pod

NETWORKS = [
    ("swow_es", "spanish_edges_FINAL.csv"),
    ("swow_en", "english_edges_FINAL.csv"),
    ("swow_zh", "chinese_edges_FINAL.csv"),
    ("swow_nl", "dutch_edges_FINAL.csv"),
]


# ---------------------------------------------------------------- graph utils
def load_lcc(csv_path: Path):
    """Undirected simple graph, largest connected component, as adjacency sets."""
    df = pd.read_csv(csv_path)
    nodes = sorted(set(df["source"]).union(df["target"]))
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    adj = [set() for _ in range(n)]
    for s, t in zip(df["source"], df["target"]):
        u, v = idx[s], idx[t]
        if u != v:
            adj[u].add(v)
            adj[v].add(u)
    comp = _components(adj)
    lcc = max(comp, key=len)
    remap = {old: new for new, old in enumerate(sorted(lcc))}
    adj_l = [set() for _ in range(len(lcc))]
    for old in lcc:
        for w in adj[old]:
            if w in remap:
                adj_l[remap[old]].add(remap[w])
    full_n = n
    full_e = sum(len(a) for a in adj) // 2
    return adj_l, full_n, full_e


def _components(adj):
    n = len(adj)
    seen = [False] * n
    comps = []
    for s in range(n):
        if seen[s]:
            continue
        comp, dq = [], deque([s])
        seen[s] = True
        while dq:
            u = dq.popleft()
            comp.append(u)
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    dq.append(v)
        comps.append(comp)
    return comps


def edges_of(adj):
    return [(u, v) for u in range(len(adj)) for v in adj[u] if u < v]


def is_connected(adj):
    return len(_components(adj)) == 1


def apsp(adj):
    """Integer hop distances via BFS from every node."""
    n = len(adj)
    D = np.full((n, n), -1, dtype=np.int32)
    for s in range(n):
        row = D[s]
        row[s] = 0
        dq = deque([s])
        while dq:
            u = dq.popleft()
            du = row[u]
            for v in adj[u]:
                if row[v] < 0:
                    row[v] = du + 1
                    dq.append(v)
    return D


# ------------------------------------------------------------------------ ORC
def w1_exact(mu, nu, C):
    n, m = len(mu), len(nu)
    c = C.flatten()
    A_eq = np.zeros((n + m, n * m))
    for i in range(n):
        A_eq[i, i * m:(i + 1) * m] = 1.0
    for j in range(m):
        A_eq[n + j, j::m] = 1.0
    b_eq = np.concatenate([mu, nu])
    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs")
    if not res.success:
        return float("nan")
    return res.fun


def edge_curvature(adj, u, v, D):
    mu_u = {u: ALPHA}
    mu_v = {v: ALPHA}
    for z in adj[u]:
        mu_u[z] = mu_u.get(z, 0.0) + (1 - ALPHA) / len(adj[u])
    for z in adj[v]:
        mu_v[z] = mu_v.get(z, 0.0) + (1 - ALPHA) / len(adj[v])
    support = sorted(set(mu_u) | set(mu_v))
    pos = {node: i for i, node in enumerate(support)}
    k = len(support)
    mu = np.zeros(k)
    nu = np.zeros(k)
    for node, p in mu_u.items():
        mu[pos[node]] = p
    for node, p in mu_v.items():
        nu[pos[node]] = p
    C = np.array([[float(D[a, b]) for b in support] for a in support])
    w1 = w1_exact(mu, nu, C)
    d_uv = float(D[u, v])
    if d_uv == 0.0 or np.isnan(w1):
        return 0.0
    return 1.0 - w1 / d_uv


def mean_kappa(adj):
    D = apsp(adj)
    kappas = [edge_curvature(adj, u, v, D) for u, v in edges_of(adj)]
    return float(np.mean(kappas))


# ---------------------------------------------------------------- null models
def rewire_connected(adj, seed):
    """Degree-preserving double-edge-swap chain conditioned on connectivity
    (networkx connected_double_edge_swap), 10x|E| swaps."""
    G = nx.Graph()
    G.add_nodes_from(range(len(adj)))
    G.add_edges_from(edges_of(adj))
    nx.connected_double_edge_swap(G, nswap=SWAP_FACTOR * G.number_of_edges(),
                                  seed=seed)
    out = [set() for _ in range(len(adj))]
    for u, v in G.edges():
        out[u].add(v)
        out[v].add(u)
    return out


_G_ADJ = None


def _init_worker(adj):
    global _G_ADJ
    _G_ADJ = adj


def _one_null(seed):
    g = rewire_connected(_G_ADJ, seed)
    if not is_connected(g):   # invariant of the chain; belt-and-braces
        return None
    return mean_kappa(g)


# ----------------------------------------------------------------------- main
def run_network(net_id, filename, base_seed):
    csv_path = DATA_DIR / filename
    adj, full_n, full_e = load_lcc(csv_path)
    N = len(adj)
    E = len(edges_of(adj))

    ref_path = REF_DIR / f"{net_id}_exact_lp.json"
    ref = json.loads(ref_path.read_text())
    kappa_ref = ref["kappa_mean"]

    t0 = time.time()
    kappa_real = mean_kappa(adj)
    print(f"[{net_id}] N={N} E={E} (full {full_n}/{full_e}) "
          f"kappa_real={kappa_real:+.6f} ref={kappa_ref:+.6f} "
          f"({time.time()-t0:.1f}s)", flush=True)

    gate_ok = abs(kappa_real - kappa_ref) < TOL
    if not gate_ok:
        print(f"[{net_id}] GATE FAIL: |{kappa_real:.6f} - {kappa_ref:.6f}| >= {TOL}",
              flush=True)
        return {
            "network_id": net_id, "status": "GATE_FAIL",
            "kappa_real_recomputed": kappa_real, "kappa_ref_exact_lp": kappa_ref,
        }

    seeds = [base_seed + k for k in range(int(M_TARGET * MAX_ATTEMPTS_FACTOR))]
    null_kappas = []
    with Pool(WORKERS, initializer=_init_worker, initargs=(adj,)) as pool:
        for r in pool.imap_unordered(_one_null, seeds, chunksize=4):
            if r is not None:
                null_kappas.append(r)
                if len(null_kappas) % 100 == 0:
                    print(f"[{net_id}] {len(null_kappas)}/{M_TARGET} nulls "
                          f"({time.time()-t0:.0f}s)", flush=True)
            if len(null_kappas) >= M_TARGET:
                pool.terminate()
                break
    null_kappas = np.array(null_kappas[:M_TARGET])
    M = len(null_kappas)

    null_mean = float(null_kappas.mean())
    null_std = float(null_kappas.std(ddof=1))
    delta = kappa_real - null_mean                       # directional, signed
    p_lower = float((1 + np.sum(null_kappas <= kappa_real)) / (M + 1))
    p_upper = float((1 + np.sum(null_kappas >= kappa_real)) / (M + 1))
    p_two = float(min(1.0, 2 * min(p_lower, p_upper)))
    cliffs = float((np.sum(null_kappas < kappa_real)
                    - np.sum(null_kappas > kappa_real)) / M)
    ci = np.percentile(null_kappas, [2.5, 97.5])
    z = (kappa_real - null_mean) / null_std if null_std > 0 else float("nan")

    result = {
        "network_id": net_id,
        "input_file": f"data/processed/{filename}",
        "graph": "lcc_undirected_simple",
        "N": N, "E": E, "full_N": full_n, "full_E": full_e,
        "orc": {"alpha": ALPHA, "cost": "integer_hop_distance",
                "w1_solver": "scipy.linprog(method=highs)_exact_LP"},
        "kappa_real": kappa_real,
        "kappa_ref_exact_lp": kappa_ref,
        "gate_abs_diff_vs_ref": abs(kappa_real - kappa_ref),
        "null_model": "connected_double_edge_swap_degree_preserving(networkx)",
        "swaps_per_null": f"{SWAP_FACTOR}x|E|",
        "connected_nulls_only": True,
        "M": M,
        "kappa_null_mean": null_mean,
        "kappa_null_std": null_std,
        "kappa_null_CI95": [float(ci[0]), float(ci[1])],
        "delta_kappa_directional": delta,
        "p_MC_lower_tail": p_lower,
        "p_MC_upper_tail": p_upper,
        "p_MC_two_sided": p_two,
        "cliffs_delta": cliffs,
        "z_score": float(z),
        "seed_base": base_seed,
        "runtime_s": round(time.time() - t0, 1),
    }
    out = OUT_DIR / f"{net_id}_configuration_nulls_r1lcc.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"[{net_id}] DONE M={M} null_mean={null_mean:+.6f} "
          f"delta={delta:+.6f} p_lower={p_lower:.4g} p_upper={p_upper:.4g} "
          f"-> {out.relative_to(REPO)}", flush=True)
    return result


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    summary = {
        "generator": "code/analysis/structural_nulls_r1lcc.py",
        "git_head_at_run": head,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "networks": [],
    }
    for k, (net_id, filename) in enumerate(NETWORKS):
        summary["networks"].append(run_network(net_id, filename, 42_000 + 10_000 * k))
    out = OUT_DIR / "configuration_nulls_r1lcc_summary.json"
    out.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"summary -> {out.relative_to(REPO)}", flush=True)


if __name__ == "__main__":
    main()
