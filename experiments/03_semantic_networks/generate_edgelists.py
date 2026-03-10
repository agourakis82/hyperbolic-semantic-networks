#!/usr/bin/env python3
"""
Generate integer edge lists for Phase 3 Sounio semantic network analysis.

Input:  data/processed/*.csv (source, target, weight columns)
Output: experiments/03_semantic_networks/data/{network}.edgelist
        Format: "u v\n" lines (0-indexed integer node IDs, undirected, no duplicates)
        Also writes: {network}.meta  (N E kappa_ref geometry_ref)

Networks targeted (fit in MAX_N=500, MAX_DEG=100):
  swow_es, swow_en, swow_zh, swow_nl, conceptnet_en, conceptnet_pt,
  wordnet_en, babelnet_ru, babelnet_ar
"""

import os
import json

DATA = "data/processed"
OUT  = "experiments/03_semantic_networks/data"
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.makedirs(os.path.join(REPO, OUT), exist_ok=True)

# Map: network_id -> (csv_path, result_json_key)
NETWORKS = {
    "swow_es":       ("spanish_edges_FINAL.csv",   "results/unified/swow_es_exact_lp.json"),
    "swow_en":       ("english_edges_FINAL.csv",    "results/unified/swow_en_exact_lp.json"),
    "swow_zh":       ("chinese_edges_FINAL.csv",    "results/unified/swow_zh_exact_lp.json"),
    "swow_nl":       ("dutch_edges.csv",            "results/unified/swow_nl_exact_lp.json"),
    "conceptnet_en": ("conceptnet_en_edges.csv",    "results/unified/conceptnet_en_exact_lp.json"),
    "conceptnet_pt": ("conceptnet_pt_edges.csv",    "results/unified/conceptnet_pt_exact_lp.json"),
    "wordnet_en":    ("wordnet_edges.csv",           "results/unified/wordnet_en_exact_lp.json"),
    "babelnet_ru":   ("babelnet_ru_edges.csv",       "results/unified/babelnet_ru_exact_lp.json"),
    "babelnet_ar":   ("babelnet_ar_edges.csv",       "results/unified/babelnet_ar_exact_lp.json"),
}

for net_id, (csv_name, json_path) in NETWORKS.items():
    csv_path  = os.path.join(REPO, DATA, csv_name)
    json_full = os.path.join(REPO, json_path)

    if not os.path.exists(csv_path):
        print(f"  SKIP {net_id}: {csv_path} not found")
        continue

    # Read edges
    node2id = {}
    edges_set = set()
    with open(csv_path) as f:
        header = f.readline().strip().split(",")
        src_col = header.index("source")
        tgt_col = header.index("target")
        for line in f:
            parts = line.strip().split(",")
            if len(parts) <= max(src_col, tgt_col):
                continue
            s, t = parts[src_col].strip(), parts[tgt_col].strip()
            if s == t:
                continue
            for n in (s, t):
                if n not in node2id:
                    node2id[n] = len(node2id)
            u, v = node2id[s], node2id[t]
            edge = (min(u, v), max(u, v))
            edges_set.add(edge)

    edges = sorted(edges_set)
    N = len(node2id)
    E = len(edges)

    # Max degree check
    deg = [0] * N
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
    max_deg = max(deg) if deg else 0

    # Write edge list
    out_path = os.path.join(REPO, OUT, f"{net_id}.edgelist")
    with open(out_path, "w") as f:
        for u, v in edges:
            f.write(f"{u} {v}\n")

    file_size = os.path.getsize(out_path)

    # Read reference kappa from JSON
    kappa_ref = None
    geometry_ref = "unknown"
    if os.path.exists(json_full):
        with open(json_full) as jf:
            jd = json.load(jf)
            kappa_ref = jd.get("kappa_mean")
            geometry_ref = jd.get("geometry", "unknown")

    # Write metadata
    meta_path = os.path.join(REPO, OUT, f"{net_id}.meta")
    with open(meta_path, "w") as f:
        f.write(f"N={N}\n")
        f.write(f"E={E}\n")
        f.write(f"max_deg={max_deg}\n")
        f.write(f"kappa_ref={kappa_ref}\n")
        f.write(f"geometry={geometry_ref}\n")

    size_kb = file_size / 1024
    fit = "OK" if max_deg <= 100 and N <= 500 else "WARN"
    kappa_str = f"{kappa_ref:.3f}" if kappa_ref is not None else "N/A"
    print(f"  {fit} {net_id:15s}: N={N:4d} E={E:6d} max_deg={max_deg:3d} size={size_kb:.1f}KB kappa={kappa_str} [{geometry_ref}]")

print("Done. Files in", os.path.join(REPO, OUT))
