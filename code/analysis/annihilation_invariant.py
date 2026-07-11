#!/usr/bin/env python3
"""Phase A — Path B: Sedenion ZD-vertex discretization + edge-compatibility invariant.

For each depression severity graph:
  1. Build curvature-free 16D node features (no κ, no κ-gradient — octonion lesson).
  2. Assign each node to nearest of 84 algebraic ZD primitives (cosine similarity).
  3. Count edges whose (label_u, label_v) pair is a ZD pair (from 168 pairs) → ZD fraction.
  4. Kill-test 1 (random codebook): replace 84 ZD primitives with 84 random 2-sparse
     unit vectors; if separation persists the signal is geometric, not algebraic → reject.
  5. Kill-test 2: feature audit — confirm no curvature component in the 16D vector.
  6. Kill-test 3: ||F||² regression — does group predict from mean feature norm alone?

Then extend to ABIDE-I (ASD vs TD) with the same pipeline (7 Laplacian eigenvectors
padded to 16D).

Usage:
    python3 code/analysis/annihilation_invariant.py --substrate semantic
    python3 code/analysis/annihilation_invariant.py --substrate abide
    python3 code/analysis/annihilation_invariant.py  # both
"""

import argparse
import json
import math
import os
import random
import struct
import sys

try:
    import networkx as nx
    HAS_NX = True
except ImportError:
    HAS_NX = False

DEPRESSION_DIR = "data/processed/depression_networks_optimal"
ZD_GEOMETRY_PATH = "/workspace/sounio/artifacts/research/sedenion_zero_divisor_geometry.v1.json"
ABIDE_FRAMES_PATH = "/workspace/sounio/artifacts/research/abide/frames.bin"

GROUPS = ["minimum", "mild", "moderate", "severe"]
RANDOM_SEED = 42
N_PERMUTATIONS = 1000


# ── sedenion geometry ──────────────────────────────────────────────────────────

def load_zd_geometry(path=ZD_GEOMETRY_PATH):
    with open(path) as f:
        g = json.load(f)
    # Materialize each vertex as a unit-norm 16D vector.
    # vertex.support = [i, j], vertex.coefficients = [±1, ±1]
    # vector: coeff[0]/sqrt(2) at index i, coeff[1]/sqrt(2) at index j, 0 elsewhere
    verts = []
    for v in g["vertices"]:
        vec = [0.0] * 16
        s = v["support"]
        c = v["coefficients"]
        inv_sqrt2 = 1.0 / math.sqrt(2.0)
        vec[s[0]] = c[0] * inv_sqrt2
        vec[s[1]] = c[1] * inv_sqrt2
        verts.append(vec)

    # 168 unordered ZD pairs as frozenset of (lhs_vertex_id, rhs_vertex_id)
    pairs = set()
    for p in g["unordered_projective_pairs"]:
        pairs.add(frozenset([p["lhs"], p["rhs"]]))

    return verts, pairs


def random_codebook(n=84, dim=16, rng=None):
    """84 random 2-sparse unit-norm vectors with same structure as ZD primitives."""
    if rng is None:
        rng = random.Random(RANDOM_SEED + 1)
    verts = []
    inv_sqrt2 = 1.0 / math.sqrt(2.0)
    for _ in range(n):
        i, j = rng.sample(range(dim), 2)
        ci = rng.choice([-1.0, 1.0])
        cj = rng.choice([-1.0, 1.0])
        vec = [0.0] * dim
        vec[i] = ci * inv_sqrt2
        vec[j] = cj * inv_sqrt2
        verts.append(vec)
    # pairs: sample 168 random unordered pairs from (n*(n-1)/2) possible pairs
    all_pairs = [(a, b) for a in range(n) for b in range(a + 1, n)]
    chosen = rng.sample(all_pairs, 168)
    pairs = {frozenset([a, b]) for a, b in chosen}
    return verts, pairs


def nearest_vertex(feat, verts):
    """Assign feature vector to nearest ZD vertex (max cosine similarity)."""
    norm_f = math.sqrt(sum(x * x for x in feat))
    if norm_f < 1e-12:
        return 0
    best_vid = 0
    best_cos = -2.0
    for vid, v in enumerate(verts):
        dot = sum(feat[i] * v[i] for i in range(16))
        cos = dot / norm_f  # v is unit-norm by construction
        if cos > best_cos:
            best_cos = cos
            best_vid = vid
    return best_vid


def zd_edge_fraction(G, node_labels, zd_pairs):
    """Fraction of edges in G whose endpoint-label pair is a ZD pair."""
    total = 0
    zd_count = 0
    for u, v in G.edges():
        lu = node_labels.get(u, 0)
        lv = node_labels.get(v, 0)
        total += 1
        if frozenset([lu, lv]) in zd_pairs:
            zd_count += 1
    if total == 0:
        return 0.0, 0, 0
    return zd_count / total, zd_count, total


# ── features ──────────────────────────────────────────────────────────────────

FEATURE_NAMES = [
    "log_degree",          # 0
    "clustering",          # 1
    "core_number",         # 2
    "pagerank",            # 3
    "betweenness",         # 4 (approx for large graphs)
    "closeness",           # 5
    "load_centrality",     # 6
    "triangles",           # 7
    "avg_neighbor_degree", # 8
    "sq_clustering",       # 9
    "harmonic",            # 10
    "eigenvector",         # 11
    "eccentricity_inv",    # 12 (1/ecc, 0 if disconnected)
    "node_clique_number",  # 13 (max clique of node neighbourhood)
    "voterank",            # 14
    "hub_score",           # 15 (HITS)
]
# KILL-TEST 2 audit: none of these involve κ or κ-gradient. ✓


def compute_features(G):
    """Return dict node -> [16 floats], curvature-free."""
    n = G.number_of_nodes()
    nodes = list(G.nodes())

    deg = dict(G.degree())
    clust = nx.clustering(G)
    core = nx.core_number(G)
    pr = nx.pagerank(G, alpha=0.85, max_iter=200)
    # betweenness: approximate for large graphs
    k_sample = min(n, 500)
    bet = nx.betweenness_centrality(G, k=k_sample, normalized=True, seed=RANDOM_SEED)
    clos = nx.closeness_centrality(G)
    load = nx.load_centrality(G)
    tri = nx.triangles(G)
    and_ = nx.average_neighbor_degree(G)
    sqcl = nx.square_clustering(G)
    harm = nx.harmonic_centrality(G)

    # eigenvector centrality — may not converge; fall back to degree
    try:
        eig = nx.eigenvector_centrality(G, max_iter=500, tol=1e-6)
    except nx.PowerIterationFailedConvergence:
        max_d = max(deg.values()) if deg else 1
        eig = {nd: deg[nd] / max_d for nd in nodes}

    # eccentricity only on connected component
    if nx.is_connected(G):
        ecc = nx.eccentricity(G)
        ecc_inv = {nd: 1.0 / ecc[nd] if ecc[nd] > 0 else 0.0 for nd in nodes}
    else:
        ecc_inv = {nd: 0.0 for nd in nodes}

    # voterank: returns ordered list; convert to per-node rank (normalized)
    vr_list = nx.voterank(G)
    vr_rank = {nd: 0.0 for nd in nodes}
    for rank, nd in enumerate(vr_list):
        vr_rank[nd] = 1.0 - rank / max(len(vr_list), 1)

    # HITS hub score
    try:
        hub, _ = nx.hits(G, max_iter=300, tol=1e-6)
    except Exception:
        hub = {nd: 0.0 for nd in nodes}

    # node clique number (size of largest clique containing node — expensive; cap at 1000 nodes)
    if n <= 1000:
        ncn = nx.node_clique_number(G)
    else:
        ncn = {nd: 0 for nd in nodes}

    max_deg = max(deg.values()) if deg else 1
    max_core = max(core.values()) if core else 1
    max_tri = max(tri.values()) if tri else 1
    max_ncn = max(ncn.values()) if ncn else 1

    feats = {}
    for nd in nodes:
        d = deg[nd]
        f = [
            math.log1p(d) / math.log1p(max_deg),          # 0 log_degree
            clust.get(nd, 0.0),                             # 1 clustering
            core.get(nd, 0) / max(max_core, 1),             # 2 core_number (norm)
            pr.get(nd, 0.0),                                # 3 pagerank
            bet.get(nd, 0.0),                               # 4 betweenness
            clos.get(nd, 0.0),                              # 5 closeness
            load.get(nd, 0.0),                              # 6 load_centrality
            math.log1p(tri.get(nd, 0)) / math.log1p(max(max_tri, 1)),  # 7 triangles (log)
            and_.get(nd, 0.0) / max(max_deg, 1),            # 8 avg_neighbor_degree (norm)
            sqcl.get(nd, 0.0),                              # 9 sq_clustering
            harm.get(nd, 0.0) / max(n - 1, 1),             # 10 harmonic (norm)
            eig.get(nd, 0.0),                               # 11 eigenvector
            ecc_inv.get(nd, 0.0),                           # 12 eccentricity_inv
            ncn.get(nd, 0) / max(max_ncn, 1),              # 13 node_clique_number (norm)
            vr_rank.get(nd, 0.0),                           # 14 voterank
            hub.get(nd, 0.0),                               # 15 hub_score
        ]
        feats[nd] = f
    return feats


# ── permutation null ───────────────────────────────────────────────────────────

def permutation_null(G, node_feats, zd_verts, zd_pairs, n_perms=N_PERMUTATIONS, seed=RANDOM_SEED):
    """Shuffle node labels; return list of ZD fractions under null."""
    rng = random.Random(seed)
    labels_list = list(node_feats.items())  # (node, feat)
    node_order = [nd for nd, _ in labels_list]
    feat_list  = [f for _, f in labels_list]

    base_labels = {nd: nearest_vertex(f, zd_verts) for nd, f in zip(node_order, feat_list)}
    # We fix the vertex assignments and permute the mapping node→label
    label_values = list(base_labels.values())
    null_fracs = []
    for _ in range(n_perms):
        rng.shuffle(label_values)
        perm_labels = dict(zip(node_order, label_values))
        frac, _, _ = zd_edge_fraction(G, perm_labels, zd_pairs)
        null_fracs.append(frac)
    return null_fracs


def z_score(observed, null_list):
    mean = sum(null_list) / len(null_list)
    var  = sum((x - mean) ** 2 for x in null_list) / len(null_list)
    sd   = math.sqrt(var) if var > 0 else 1e-12
    return (observed - mean) / sd, mean, sd


# ── semantic substrate ─────────────────────────────────────────────────────────

def run_semantic(zd_verts, zd_pairs, rand_verts, rand_pairs):
    print("\n═══ SEMANTIC SUBSTRATE: depression severity networks ═══")

    print("\n[KILL-TEST 2] Feature audit (curvature-free check):")
    for i, name in enumerate(FEATURE_NAMES):
        flag = "  ✓" if "κ" not in name and "curv" not in name else "  ✗ CURVATURE"
        print(f"  f{i:02d} {name}{flag}")
    print("  → No curvature components in 16D feature vector. Kill-test 2 PASS (by construction).")

    results = {}
    for group in GROUPS:
        csv_path = os.path.join(DEPRESSION_DIR, f"depression_{group}_edges.csv")
        if not os.path.exists(csv_path):
            print(f"\n[SKIP] {group}: {csv_path} not found")
            continue

        print(f"\n── {group} ──")
        G = nx.Graph()
        with open(csv_path) as fh:
            next(fh)  # skip header
            for line in fh:
                parts = line.strip().split(",")
                if len(parts) >= 2:
                    G.add_edge(parts[0], parts[1])

        print(f"  nodes={G.number_of_nodes()}, edges={G.number_of_edges()}")
        n = G.number_of_nodes()

        print("  computing 16 curvature-free features...", end="", flush=True)
        feats = compute_features(G)
        print(" done")

        # Kill-test 3: ||F||² regression (mean norm per group)
        mean_norm_sq = sum(
            sum(x * x for x in f) for f in feats.values()
        ) / n
        print(f"  kill-test-3 mean‖F‖²={mean_norm_sq:.4f}")

        # Primary: algebraic ZD codebook
        node_labels = {nd: nearest_vertex(f, zd_verts) for nd, f in feats.items()}
        frac, zd_cnt, total = zd_edge_fraction(G, node_labels, zd_pairs)
        print(f"  ZD-edge fraction (algebraic): {frac:.4f}  ({zd_cnt}/{total})")

        # Permutation null
        print(f"  running {N_PERMUTATIONS} permutation nulls...", end="", flush=True)
        null_fracs = permutation_null(G, feats, zd_verts, zd_pairs)
        z, null_mean, null_sd = z_score(frac, null_fracs)
        print(f" done. null_mean={null_mean:.4f} null_sd={null_sd:.4f} z={z:.2f}")

        # Kill-test 1: random codebook
        node_labels_rand = {nd: nearest_vertex(f, rand_verts) for nd, f in feats.items()}
        frac_rand, zd_cnt_rand, _ = zd_edge_fraction(G, node_labels_rand, rand_pairs)
        null_rand = permutation_null(G, feats, rand_verts, rand_pairs)
        z_rand, null_rand_mean, _ = z_score(frac_rand, null_rand)
        print(f"  ZD-edge fraction (random codebook): {frac_rand:.4f}  z={z_rand:.2f}")

        results[group] = {
            "frac": frac, "z": z,
            "frac_rand": frac_rand, "z_rand": z_rand,
            "mean_norm_sq": mean_norm_sq,
        }

    # Kill-test 1 verdict: if algebraic z >> random z for same groups → algebraic signal
    print("\n── KILL-TEST 1 SUMMARY (algebraic vs random codebook) ──")
    print(f"  {'group':<12}  {'z_algebraic':>14}  {'z_random':>10}  verdict")
    for g, r in results.items():
        diff = r["z"] - r["z_rand"]
        v = "algebraic STRONGER" if diff > 2.0 else ("similar — GEOMETRIC, not algebraic" if abs(diff) <= 2.0 else "random STRONGER")
        print(f"  {g:<12}  {r['z']:>14.2f}  {r['z_rand']:>10.2f}  {v}")

    # Kill-test 3 verdict: does mean ||F||² rank match ZD fraction rank?
    if len(results) >= 2:
        norm_rank = sorted(results.keys(), key=lambda g: results[g]["mean_norm_sq"])
        zd_rank   = sorted(results.keys(), key=lambda g: results[g]["frac"])
        print(f"\n── KILL-TEST 3 SUMMARY (||F||² vs ZD-fraction ordering) ──")
        print(f"  ||F||² rank (low→high): {norm_rank}")
        print(f"  ZD frac rank (low→hi):  {zd_rank}")
        if norm_rank == zd_rank:
            print("  → Orderings MATCH → ZD signal may be norm-dominated → treat with caution")
        else:
            print("  → Orderings DIFFER → ZD signal is not a pure norm artifact")

    return results


# ── ABIDE substrate ────────────────────────────────────────────────────────────

def run_abide(zd_verts, zd_pairs, rand_verts, rand_pairs):
    print("\n═══ ABIDE-I SUBSTRATE: ASD vs TD ═══")

    if not os.path.exists(ABIDE_FRAMES_PATH):
        print(f"  [SKIP] frames.bin not found at {ABIDE_FRAMES_PATH}")
        return

    with open(ABIDE_FRAMES_PATH, "rb") as fh:
        n_asd = struct.unpack("<q", fh.read(8))[0]
        n_td  = struct.unpack("<q", fh.read(8))[0]
        total = n_asd + n_td
        print(f"  n_asd={n_asd}, n_td={n_td}, total={total}")

        # Each subject: 7 × 200 f64 = 1400 values
        subjects = []
        labels = ["ASD"] * n_asd + ["TD"] * n_td
        for i in range(total):
            raw = fh.read(7 * 200 * 8)
            vals = struct.unpack(f"<{7*200}d", raw)
            subjects.append(vals)

    # Build 16D feature per subject: first 16 of 7×200=1400 values
    # Use the 7 mean eigenvector values (mean over 200 ROIs per eigenvector) → 7D,
    # then pad to 16D with 7 std values + 2 zeros.
    def subject_feature(vals):
        evecs = [vals[k*200:(k+1)*200] for k in range(7)]
        means = [sum(e) / 200 for e in evecs]
        stds  = [math.sqrt(sum((x - means[k])**2 for x in evecs[k]) / 200) for k in range(7)]
        feat  = means + stds + [0.0, 0.0]  # 7+7+2 = 16
        return feat

    feats_asd = [subject_feature(subjects[i]) for i in range(n_asd)]
    feats_td  = [subject_feature(subjects[i]) for i in range(n_asd, total)]

    # Kill-test 3: mean ||F||² per group
    norm_sq_asd = sum(sum(x*x for x in f) for f in feats_asd) / n_asd
    norm_sq_td  = sum(sum(x*x for x in f) for f in feats_td)  / n_td
    print(f"  mean‖F‖² ASD={norm_sq_asd:.4f}, TD={norm_sq_td:.4f}")

    # Assign each subject to nearest ZD vertex
    labels_asd = [nearest_vertex(f, zd_verts) for f in feats_asd]
    labels_td  = [nearest_vertex(f, zd_verts) for f in feats_td]

    # Use label frequency distribution (not graph edges) — compare histograms
    def label_hist(lbls, n_verts=84):
        h = [0] * n_verts
        for l in lbls:
            h[l] += 1
        return h

    hist_asd = label_hist(labels_asd)
    hist_td  = label_hist(labels_td)

    # Fraction assigned to each vertex; compare using chi-squared-like statistic
    # Also compute: fraction of pairs (one ASD, one TD) that are ZD pairs
    def cross_zd_fraction(lbls_a, lbls_b, zd_pairs_set):
        count = 0
        total = len(lbls_a) * len(lbls_b)
        for la in lbls_a:
            for lb in lbls_b:
                if frozenset([la, lb]) in zd_pairs_set:
                    count += 1
        return count / total if total > 0 else 0.0

    frac_cross = cross_zd_fraction(labels_asd[:50], labels_td[:50], zd_pairs)
    print(f"  cross-group ZD fraction (first 50×50): {frac_cross:.4f}")

    # Permutation null: shuffle ASD/TD label assignment
    rng = random.Random(RANDOM_SEED)
    all_feats = feats_asd + feats_td
    all_labels_coded = [nearest_vertex(f, zd_verts) for f in all_feats]
    null_fracs = []
    for _ in range(200):  # fewer perms for ABIDE (n is large)
        rng.shuffle(all_labels_coded)
        f_null = cross_zd_fraction(all_labels_coded[:50], all_labels_coded[n_asd:n_asd+50], zd_pairs)
        null_fracs.append(f_null)
    z, null_mean, null_sd = z_score(frac_cross, null_fracs)
    print(f"  permutation null: mean={null_mean:.4f} sd={null_sd:.4f} z={z:.2f}")

    # Random codebook
    labels_asd_rand = [nearest_vertex(f, rand_verts) for f in feats_asd[:50]]
    labels_td_rand  = [nearest_vertex(f, rand_verts) for f in feats_td[:50]]
    frac_rand = cross_zd_fraction(labels_asd_rand, labels_td_rand, rand_pairs)
    print(f"  random codebook ZD fraction: {frac_rand:.4f}")

    print(f"\n  Kill-test 1: algebraic z={z:.2f}, random codebook frac={frac_rand:.4f}")
    if z > 2.0 and frac_rand < frac_cross:
        print("  → ABIDE: algebraic signal candidate (verify with full cross-ZD)")
    else:
        print("  → ABIDE: no clear algebraic signal over random codebook")


# ── main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--substrate", choices=["semantic", "abide", "both"], default="both")
    args = parser.parse_args()

    if not HAS_NX:
        print("ERROR: networkx not available. Install it first.")
        sys.exit(1)

    print("Loading ZD geometry...")
    zd_verts, zd_pairs = load_zd_geometry()
    print(f"  {len(zd_verts)} algebraic ZD vertices, {len(zd_pairs)} ZD pairs loaded")

    print("Building random codebook (kill-test 1)...")
    rand_verts, rand_pairs = random_codebook()
    print(f"  {len(rand_verts)} random vertices, {len(rand_pairs)} random pairs")

    print("\n[KILL-TEST 2] Feature set audit:")
    print("  16D features: " + ", ".join(FEATURE_NAMES))
    print("  Curvature (κ) present: NO  |  κ-gradient present: NO  ✓")

    sem_results = {}
    if args.substrate in ("semantic", "both"):
        sem_results = run_semantic(zd_verts, zd_pairs, rand_verts, rand_pairs)

    if args.substrate in ("abide", "both"):
        run_abide(zd_verts, zd_pairs, rand_verts, rand_pairs)

    # Final verdict
    print("\n══════════════════════════════════════════════")
    print("PHASE A VERDICT")
    print("══════════════════════════════════════════════")
    if sem_results:
        algebraic_wins = sum(
            1 for r in sem_results.values()
            if r["z"] - r["z_rand"] > 2.0
        )
        total_groups = len(sem_results)
        if algebraic_wins == total_groups:
            print(f"CANDIDATE SECOND AXIS: algebraic ZD codebook consistently stronger than")
            print(f"  random codebook across all {total_groups} groups (z-diff > 2.0).")
            print(f"  → Proceed to Phase B (curvature⊥annihilation orthogonality check).")
        elif algebraic_wins > 0:
            print(f"PARTIAL: algebraic signal in {algebraic_wins}/{total_groups} groups.")
            print(f"  → Informative partial result. Report as partial, not axis.")
        else:
            print(f"NULL RESULT: random codebook matches algebraic in all {total_groups} groups.")
            print(f"  → ZD discretization does not carry group structure beyond geometry.")
            print(f"  → Honest negative (like the octonion associator result).")


if __name__ == "__main__":
    main()
