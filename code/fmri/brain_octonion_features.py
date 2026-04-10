#!/usr/bin/env python3
"""
C3-C4: Octonion Edge Labeling + Associator Field — ABIDE-I Brain Graphs

Assigns octonion labels to brain graph edges using two schemes:
  Scheme 1 (RSN-based): 7 Yeo RSNs → 7 imaginary units + 1 real
  Scheme 2 (FC-derived): local graph statistics → 8 octonion components

Then computes the associator field: for each 2-path u-v-w,
  A(u,v,w) = [l(u,v), l(v,w), l(w,x)] = (l(u,v)·l(v,w))·l(w,x) - l(u,v)·(l(v,w)·l(w,x))

Extracts 4 features per subject:
  1. mean_assoc_norm     — mean ||A|| over all 2-paths
  2. zero_frac           — fraction with ||A|| < ε
  3. assoc_entropy        — Shannon entropy of ||A|| distribution
  4. assoc_kappa_corr    — correlation of ||A|| with vertex ORC

Usage:
    python code/fmri/brain_octonion_features.py
    python code/fmri/brain_octonion_features.py --threshold 0.50

Output:
    results/fmri/abide_octonion_features_t{threshold}.json
"""

import argparse
import json
import time
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from scipy import stats as sp_stats

# ── Paths ────────────────────────────────────────────────────────────────────

FC_DIR = Path("data/processed/abide_fc")
GRAPH_DIR = Path("data/processed/abide_graphs")
PHENO_CSV = Path("data/processed/abide_phenotypic_matched.csv")
RESULTS_DIR = Path("results/fmri")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ── Octonion algebra (precomputed multiplication table) ──────────────────────

# Build 8x8 multiplication table: MUL_IDX[i,j] = target index, MUL_SIGN[i,j] = sign
FANO_TRIPLES = [(1,2,4), (2,3,5), (3,4,6), (4,5,7), (5,6,1), (6,7,2), (7,1,3)]

_MUL_IDX = np.zeros((8, 8), dtype=int)
_MUL_SIGN = np.zeros((8, 8))

def _build_mul_table():
    for i in range(8):
        for j in range(8):
            if i == 0 and j == 0:
                _MUL_IDX[i, j] = 0; _MUL_SIGN[i, j] = 1.0
            elif i == 0:
                _MUL_IDX[i, j] = j; _MUL_SIGN[i, j] = 1.0
            elif j == 0:
                _MUL_IDX[i, j] = i; _MUL_SIGN[i, j] = 1.0
            elif i == j:
                _MUL_IDX[i, j] = 0; _MUL_SIGN[i, j] = -1.0
            else:
                found = False
                for a, b, c in FANO_TRIPLES:
                    if i == a and j == b: _MUL_IDX[i,j] = c; _MUL_SIGN[i,j] = 1.0; found = True; break
                    if i == b and j == c: _MUL_IDX[i,j] = a; _MUL_SIGN[i,j] = 1.0; found = True; break
                    if i == c and j == a: _MUL_IDX[i,j] = b; _MUL_SIGN[i,j] = 1.0; found = True; break
                    if i == b and j == a: _MUL_IDX[i,j] = c; _MUL_SIGN[i,j] = -1.0; found = True; break
                    if i == c and j == b: _MUL_IDX[i,j] = a; _MUL_SIGN[i,j] = -1.0; found = True; break
                    if i == a and j == c: _MUL_IDX[i,j] = b; _MUL_SIGN[i,j] = -1.0; found = True; break
                if not found:
                    _MUL_IDX[i, j] = 0; _MUL_SIGN[i, j] = 0.0

_build_mul_table()


def oct_mul(a, b):
    """Multiply two octonions using precomputed table (fast)."""
    result = np.zeros(8)
    for i in range(8):
        if a[i] == 0:
            continue
        for j in range(8):
            if b[j] == 0:
                continue
            k = _MUL_IDX[i, j]
            s = _MUL_SIGN[i, j]
            result[k] += s * a[i] * b[j]
    return result


def oct_associator(a, b, c):
    """[a,b,c] = (ab)c - a(bc)"""
    ab = oct_mul(a, b)
    bc = oct_mul(b, c)
    return oct_mul(ab, c) - oct_mul(a, bc)


def oct_norm(a):
    return np.sqrt(np.sum(a**2))


# ── Edge labeling schemes ────────────────────────────────────────────────────

def label_edges_fc_derived(G, z_fc):
    """
    Scheme 2 (FC-derived): each edge gets an octonion from local statistics.
    e0 = edge weight (z-score)
    e1 = node u mean connectivity
    e2 = node v mean connectivity
    e3 = geometric mean of degrees
    e4 = clustering coefficient of u
    e5 = clustering coefficient of v
    e6 = neighbor overlap fraction (Jaccard)
    e7 = edge betweenness proxy (product of inverse degrees)
    """
    N = G.number_of_nodes()
    nodes = sorted(G.nodes())
    node_idx = {n: i for i, n in enumerate(nodes)}

    # Precompute per-node stats
    mean_fc = {n: np.mean(np.abs(z_fc[node_idx[n], :])) for n in nodes}
    clustering = nx.clustering(G)
    degrees = dict(G.degree())

    labels = {}
    for u, v in G.edges():
        ui, vi = node_idx[u], node_idx[v]
        du, dv = degrees[u], degrees[v]

        nbrs_u = set(G.neighbors(u))
        nbrs_v = set(G.neighbors(v))
        jaccard = len(nbrs_u & nbrs_v) / max(len(nbrs_u | nbrs_v), 1)

        label = np.array([
            z_fc[ui, vi],                              # e0: edge weight
            mean_fc[u],                                 # e1: u centrality
            mean_fc[v],                                 # e2: v centrality
            np.sqrt(du * dv) / N,                       # e3: degree geom mean
            clustering[u],                              # e4: u clustering
            clustering[v],                              # e5: v clustering
            jaccard,                                    # e6: neighbor overlap
            1.0 / (np.sqrt(du) * np.sqrt(dv) + 1e-10), # e7: inverse degree
        ])
        # Normalize to unit octonion
        norm = oct_norm(label)
        if norm > 1e-12:
            label = label / norm
        labels[(u, v)] = label
        labels[(v, u)] = label  # symmetric
    return labels


def label_edges_rsn_based(G, z_fc, rsn_assignment):
    """
    Scheme 1 (RSN-based): edges labeled by which RSNs they connect.
    e0 = edge weight (always present)
    e_{rsn_i XOR rsn_j} = edge weight (maps RSN pair to Fano plane index)
    """
    nodes = sorted(G.nodes())
    node_idx = {n: i for i, n in enumerate(nodes)}

    labels = {}
    for u, v in G.edges():
        ui, vi = node_idx[u], node_idx[v]
        w = z_fc[ui, vi]

        rsn_u = rsn_assignment.get(u, 0) % 7 + 1  # 1-7
        rsn_v = rsn_assignment.get(v, 0) % 7 + 1

        label = np.zeros(8)
        label[0] = w  # real part = edge weight

        if rsn_u == rsn_v:
            # Intra-network: strengthen real component
            label[0] *= 2.0
        else:
            # Inter-network: map to imaginary unit via Fano structure
            idx = ((rsn_u + rsn_v) % 7) + 1  # 1-7
            label[idx] = w

        norm = oct_norm(label)
        if norm > 1e-12:
            label = label / norm
        labels[(u, v)] = label
        labels[(v, u)] = label
    return labels


# ── Associator field computation ─────────────────────────────────────────────

def compute_associator_field(G, labels, max_triples=5000):
    """Compute associator norms for sampled 2-paths in G."""
    assoc_norms = []
    nodes = list(G.nodes())
    rng = np.random.RandomState(42)
    rng.shuffle(nodes)

    for v in nodes:
        nbrs = list(G.neighbors(v))
        n_nb = len(nbrs)
        # Sample pairs to keep O(N) per vertex for dense graphs
        max_pairs = min(n_nb * (n_nb - 1) // 2, 50)
        pair_count = 0
        for i in range(n_nb):
            if pair_count >= max_pairs:
                break
            l_a = labels.get((nbrs[i], v), np.zeros(8))
            for j in range(i+1, min(i+6, n_nb)):  # limit inner loop
                w = nbrs[j]
                l_b = labels.get((v, w), np.zeros(8))
                w_nbrs = list(G.neighbors(w))
                if w_nbrs:
                    x = w_nbrs[0]
                    l_c = labels.get((w, x), np.zeros(8))
                    assoc = oct_associator(l_a, l_b, l_c)
                    assoc_norms.append(oct_norm(assoc))
                    pair_count += 1

                    if len(assoc_norms) >= max_triples:
                        return np.array(assoc_norms)
    return np.array(assoc_norms)


def extract_features(assoc_norms):
    """Extract 4 features from associator norm distribution."""
    if len(assoc_norms) == 0:
        return {"mean_assoc_norm": 0, "zero_frac": 1, "assoc_entropy": 0,
                "n_triples": 0}

    mean_norm = float(np.mean(assoc_norms))
    zero_frac = float(np.mean(assoc_norms < 1e-9))

    # Shannon entropy of binned norms
    if np.max(assoc_norms) > 1e-12:
        counts, _ = np.histogram(assoc_norms, bins=20)
        probs = counts / counts.sum()
        probs = probs[probs > 0]
        entropy = float(-np.sum(probs * np.log(probs)))
    else:
        entropy = 0.0

    return {
        "mean_assoc_norm": round(mean_norm, 6),
        "zero_frac": round(zero_frac, 6),
        "assoc_entropy": round(entropy, 4),
        "n_triples": len(assoc_norms),
    }


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=float, default=0.40)
    args = parser.parse_args()
    threshold = args.threshold

    pheno = pd.read_csv(PHENO_CSV)
    print(f"ABIDE-I Octonion Features (threshold={threshold})")
    print(f"Subjects: {len(pheno)}")
    print("=" * 60)

    # Simple RSN assignment: partition 200 ROIs into 7 groups by index
    rsn_map = {i: i % 7 for i in range(200)}

    results = []
    for _, row in pheno.iterrows():
        file_id = row["file_id"]
        edge_file = GRAPH_DIR / f"{file_id}_t{threshold:.2f}_edges.csv"
        fc_file = FC_DIR / f"{file_id}_fc.npz"

        if not edge_file.exists() or not fc_file.exists():
            continue

        t0 = time.time()

        # Load graph
        df = pd.read_csv(edge_file)
        G = nx.Graph()
        for _, r in df.iterrows():
            G.add_edge(int(r["source"]), int(r["target"]))
        if not nx.is_connected(G):
            lcc = max(nx.connected_components(G), key=len)
            G = G.subgraph(lcc).copy()

        # Load FC
        z_fc = np.load(fc_file)["z_fc"]

        # Scheme 2: FC-derived (primary)
        labels_fc = label_edges_fc_derived(G, z_fc)
        assoc_fc = compute_associator_field(G, labels_fc, max_triples=5000)
        feats_fc = extract_features(assoc_fc)

        # Scheme 1: RSN-based
        labels_rsn = label_edges_rsn_based(G, z_fc, rsn_map)
        assoc_rsn = compute_associator_field(G, labels_rsn, max_triples=5000)
        feats_rsn = extract_features(assoc_rsn)

        elapsed = time.time() - t0
        print(f"  {file_id}: FC_assoc={feats_fc['mean_assoc_norm']:.4f}, "
              f"RSN_assoc={feats_rsn['mean_assoc_norm']:.4f} [{elapsed:.1f}s]")

        results.append({
            "file_id": file_id,
            "dx_group": int(row["dx_group"]),
            "N": G.number_of_nodes(),
            "n_edges": G.number_of_edges(),
            "scheme_fc": feats_fc,
            "scheme_rsn": feats_rsn,
            "elapsed_s": round(elapsed, 1),
        })

    # Summary
    print("\n" + "=" * 60)
    for scheme_key, scheme_name in [("scheme_fc", "FC-derived"), ("scheme_rsn", "RSN-based")]:
        print(f"\n  {scheme_name} scheme:")
        for dx, label in [(1, "ASD"), (2, "Control")]:
            group = [r[scheme_key]["mean_assoc_norm"]
                     for r in results if r["dx_group"] == dx
                     and not np.isnan(r[scheme_key]["mean_assoc_norm"])]
            if group:
                print(f"    {label} (n={len(group)}): "
                      f"mean_assoc={np.mean(group):.4f} ± {np.std(group):.4f}")

        # Welch t-test
        asd_vals = [r[scheme_key]["mean_assoc_norm"]
                    for r in results if r["dx_group"] == 1
                    and not np.isnan(r[scheme_key]["mean_assoc_norm"])]
        ctrl_vals = [r[scheme_key]["mean_assoc_norm"]
                     for r in results if r["dx_group"] == 2
                     and not np.isnan(r[scheme_key]["mean_assoc_norm"])]
        if asd_vals and ctrl_vals:
            t_stat, p_val = sp_stats.ttest_ind(asd_vals, ctrl_vals, equal_var=False)
            d = (np.mean(asd_vals) - np.mean(ctrl_vals)) / \
                np.sqrt((np.var(asd_vals) + np.var(ctrl_vals)) / 2)
            print(f"    t={t_stat:.3f}, p={p_val:.4f}, Cohen's d={d:.3f}")

    out_path = RESULTS_DIR / f"abide_octonion_features_t{threshold:.2f}.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {out_path}")


if __name__ == "__main__":
    main()
