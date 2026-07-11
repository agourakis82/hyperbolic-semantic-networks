#!/usr/bin/env python3
"""Deterministic ORC core: LCC graphs, exact LP W1, Sinkhorn baselines."""

from __future__ import annotations

import csv
import json
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
from scipy.optimize import linprog

ALPHA = Fraction(1, 2)
SEED_BOOTSTRAP = 456
SEED_SYNTHETIC = 42

Edge = Tuple[int, int]


@dataclass
class Graph:
    n: int
    edges: List[Edge]
    adj: Dict[int, List[int]]

    @property
    def e(self) -> int:
        return len(self.edges)


def load_lcc_from_csv(csv_path: Path) -> Graph:
    node2id: Dict[str, int] = {}
    edges_set = set()
    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            s = row["source"].strip()
            t = row["target"].strip()
            if s == t:
                continue
            for name in (s, t):
                if name not in node2id:
                    node2id[name] = len(node2id)
            u, v = node2id[s], node2id[t]
            edges_set.add((min(u, v), max(u, v)))
    n_full = len(node2id)
    adj_full: Dict[int, set] = defaultdict(set)
    for u, v in edges_set:
        adj_full[u].add(v)
        adj_full[v].add(u)

    visited = set()
    components: List[set] = []
    for start in range(n_full):
        if start in visited:
            continue
        q = deque([start])
        comp = {start}
        visited.add(start)
        while q:
            u = q.popleft()
            for v in adj_full[u]:
                if v not in visited:
                    visited.add(v)
                    comp.add(v)
                    q.append(v)
        components.append(comp)
    lcc = max(components, key=len)
    old_to_new = {old: i for i, old in enumerate(sorted(lcc))}
    edges: List[Edge] = []
    adj: Dict[int, List[int]] = defaultdict(list)
    for u, v in sorted(edges_set):
        if u in lcc and v in lcc:
            a, b = old_to_new[u], old_to_new[v]
            edges.append((a, b))
            adj[a].append(b)
            adj[b].append(a)
    for u in adj:
        adj[u] = sorted(set(adj[u]))
    return Graph(n=len(lcc), edges=edges, adj=dict(adj))


def apsp(g: Graph) -> np.ndarray:
    n = g.n
    d = np.full((n, n), -1, dtype=int)
    for src in range(n):
        dist = [-1] * n
        dist[src] = 0
        q = deque([src])
        while q:
            u = q.popleft()
            for v in g.adj[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    q.append(v)
        d[src] = dist
    return d


def lazy_measure_rational(g: Graph, node: int) -> Dict[int, Fraction]:
    mu: Dict[int, Fraction] = {node: ALPHA}
    nbrs = g.adj[node]
    if nbrs:
        w = (Fraction(1, 1) - ALPHA) / len(nbrs)
        for z in nbrs:
            mu[z] = mu.get(z, Fraction(0, 1)) + w
    return mu


def lazy_measure_float(g: Graph, node: int) -> Dict[int, float]:
    mu: Dict[int, float] = {node: float(ALPHA)}
    nbrs = g.adj[node]
    if nbrs:
        w = (1.0 - float(ALPHA)) / len(nbrs)
        for z in nbrs:
            mu[z] = mu.get(z, 0.0) + w
    return mu


def _support_pair(
    mu: Dict[int, float], nu: Dict[int, float]
) -> Tuple[List[int], np.ndarray, np.ndarray, np.ndarray]:
    nodes = sorted(set(mu) | set(nu))
    idx = {nd: i for i, nd in enumerate(nodes)}
    mu_vec = np.array([mu.get(nd, 0.0) for nd in nodes], dtype=float)
    nu_vec = np.array([nu.get(nd, 0.0) for nd in nodes], dtype=float)
    return nodes, mu_vec, nu_vec, idx


def exact_w1_lp(
    mu_vec: np.ndarray, nu_vec: np.ndarray, cost: np.ndarray
) -> float:
    n = len(mu_vec)
    c = cost.reshape(-1)
    a_eq = []
    b_eq = []
    for i in range(n):
        row = np.zeros(n * n)
        for j in range(n):
            row[i * n + j] = 1.0
        a_eq.append(row)
        b_eq.append(mu_vec[i])
    for j in range(n):
        row = np.zeros(n * n)
        for i in range(n):
            row[i * n + j] = 1.0
        a_eq.append(row)
        b_eq.append(nu_vec[j])
    res = linprog(
        c,
        A_eq=np.array(a_eq),
        b_eq=np.array(b_eq),
        bounds=(0.0, None),
        method="highs",
    )
    if not res.success:
        raise RuntimeError(f"LP failed: {res.message}")
    return float(res.fun)


def sinkhorn_primal(
    mu_vec: np.ndarray,
    nu_vec: np.ndarray,
    cost: np.ndarray,
    epsilon: float,
    max_iter: int,
) -> float:
    n = len(mu_vec)
    k = np.exp(-cost / epsilon)
    u = np.ones(n)
    v = np.ones(n)
    floor = 1e-300
    for _ in range(max_iter):
        for i in range(n):
            s = max(np.dot(k[i], v), floor)
            u[i] = mu_vec[i] / s
        for j in range(n):
            s = max(np.dot(k[:, j], u), floor)
            v[j] = nu_vec[j] / s
    p = (u[:, None] * k) * v[None, :]
    return float((p * cost).sum())


def sinkhorn_lse(
    mu_vec: np.ndarray,
    nu_vec: np.ndarray,
    cost: np.ndarray,
    epsilon: float,
    max_iter: int,
) -> float:
    n = len(mu_vec)
    log_mu = np.log(np.maximum(mu_vec, 1e-300))
    log_nu = np.log(np.maximum(nu_vec, 1e-300))
    logk = -cost / epsilon
    logu = np.zeros(n)
    logv = np.zeros(n)
    for _ in range(max_iter):
        for i in range(n):
            logu[i] = log_mu[i] - np.logaddexp.reduce(logk[i] + logv)
        for j in range(n):
            logv[j] = log_nu[j] - np.logaddexp.reduce(logk[:, j] + logu)
    p = np.exp(logu[:, None] + logk + logv[None, :])
    return float((p * cost).sum())


def edge_kappa_lp(g: Graph, d: np.ndarray, u: int, v: int) -> float:
    d_uv = int(d[u, v])
    if d_uv <= 0:
        return 0.0
    mu = lazy_measure_float(g, u)
    nu = lazy_measure_float(g, v)
    nodes, mu_vec, nu_vec, _ = _support_pair(mu, nu)
    c = np.array(
        [[d[nodes[i], nodes[j]] for j in range(len(nodes))] for i in range(len(nodes))],
        dtype=float,
    )
    w1 = exact_w1_lp(mu_vec, nu_vec, c)
    return 1.0 - w1 / d_uv


def mean_kappa_lp(g: Graph, d: np.ndarray) -> float:
    kappas = [edge_kappa_lp(g, d, u, v) for u, v in g.edges]
    return float(np.mean(kappas))


def edge_data(g: Graph, d: np.ndarray, u: int, v: int) -> dict:
    d_uv = int(d[u, v])
    mu = lazy_measure_float(g, u)
    nu = lazy_measure_float(g, v)
    nodes, mu_vec, nu_vec, _ = _support_pair(mu, nu)
    c = np.array(
        [[d[nodes[i], nodes[j]] for j in range(len(nodes))] for i in range(len(nodes))],
        dtype=float,
    )
    w1_lp = exact_w1_lp(mu_vec, nu_vec, c)
    w1_primal_05 = sinkhorn_primal(mu_vec, nu_vec, c, 0.5, 80)
    w1_lse_001 = sinkhorn_lse(mu_vec, nu_vec, c, 0.01, 1000)
    k_lp = 1.0 - w1_lp / d_uv
    return {
        "u": u,
        "v": v,
        "d_uv": d_uv,
        "support_size": len(nodes),
        "W1_exact_lp": w1_lp,
        "W1_sinkhorn_primal_eps0.5_iter80": w1_primal_05,
        "W1_sinkhorn_lse_eps0.01_iter1000": w1_lse_001,
        "kappa_exact_lp": k_lp,
        "kappa_primal_eps0.5": 1.0 - w1_primal_05 / d_uv,
        "kappa_lse_eps0.01": 1.0 - w1_lse_001 / d_uv,
    }


def load_julia_ref(repo: Path, lang: str) -> dict:
    return json.loads(
        (repo / f"results/unified/swow_{lang}_exact_lp.json").read_text()
    )


NETWORKS = {
    "en": "english_edges_FINAL.csv",
    "es": "spanish_edges_FINAL.csv",
    "zh": "chinese_edges_FINAL.csv",
    "nl": "dutch_edges_FINAL.csv",
}
