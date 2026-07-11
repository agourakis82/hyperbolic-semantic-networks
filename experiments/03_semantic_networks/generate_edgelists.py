#!/usr/bin/env python3
"""
Generate integer edge lists for Sounio semantic network ORC.

Input:  data/processed/*.csv (source, target, weight columns)
Output: experiments/03_semantic_networks/data/{network}.edgelist
        Largest connected component (LCC), matching unified_semantic_orc.jl.
        Format: "u v\\n" (0-indexed, undirected, deduplicated)
        Also writes: {network}.meta
"""

import json
import os
from collections import defaultdict, deque

DATA = "data/processed"
OUT = "experiments/03_semantic_networks/data"
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.makedirs(os.path.join(REPO, OUT), exist_ok=True)

NETWORKS = {
    "swow_es": ("spanish_edges_FINAL.csv", "results/unified/swow_es_exact_lp.json"),
    "swow_en": ("english_edges_FINAL.csv", "results/unified/swow_en_exact_lp.json"),
    "swow_zh": ("chinese_edges_FINAL.csv", "results/unified/swow_zh_exact_lp.json"),
    "swow_nl": ("dutch_edges_FINAL.csv", "results/unified/swow_nl_exact_lp.json"),
    "conceptnet_en": ("conceptnet_en_edges.csv", "results/unified/conceptnet_en_exact_lp.json"),
    "conceptnet_pt": ("conceptnet_pt_edges.csv", "results/unified/conceptnet_pt_exact_lp.json"),
    "wordnet_en": ("wordnet_edges.csv", "results/unified/wordnet_en_exact_lp.json"),
    "babelnet_ru": ("babelnet_ru_edges.csv", "results/unified/babelnet_ru_exact_lp.json"),
    "babelnet_ar": ("babelnet_ar_edges.csv", "results/unified/babelnet_ar_exact_lp.json"),
}


def largest_connected_component(edges, n_nodes):
    adj = defaultdict(set)
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    visited = set()
    components = []
    for start in range(n_nodes):
        if start in visited:
            continue
        q = deque([start])
        comp = {start}
        visited.add(start)
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v not in visited:
                    visited.add(v)
                    comp.add(v)
                    q.append(v)
        components.append(comp)
    lcc = max(components, key=len)
    old_to_new = {old: i for i, old in enumerate(sorted(lcc))}
    lcc_edges = set()
    for u, v in edges:
        if u in lcc and v in lcc:
            a, b = old_to_new[u], old_to_new[v]
            lcc_edges.add((min(a, b), max(a, b)))
    return sorted(lcc_edges), len(lcc), len(lcc_edges)


for net_id, (csv_name, json_path) in NETWORKS.items():
    csv_path = os.path.join(REPO, DATA, csv_name)
    json_full = os.path.join(REPO, json_path)

    if not os.path.exists(csv_path):
        print(f"  SKIP {net_id}: {csv_path} not found")
        continue

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
            edges_set.add((min(u, v), max(u, v)))

    full_n = len(node2id)
    lcc_edges, n, e = largest_connected_component(edges_set, full_n)

    deg = [0] * n
    for u, v in lcc_edges:
        deg[u] += 1
        deg[v] += 1
    max_deg = max(deg) if deg else 0

    out_path = os.path.join(REPO, OUT, f"{net_id}.edgelist")
    with open(out_path, "w") as f:
        for u, v in lcc_edges:
            f.write(f"{u} {v}\n")

    kappa_ref = None
    geometry_ref = "unknown"
    ref_n = ref_e = None
    if os.path.exists(json_full):
        with open(json_full) as jf:
            jd = json.load(jf)
            kappa_ref = jd.get("kappa_mean")
            geometry_ref = jd.get("geometry", "unknown")
            ref_n = jd.get("N")
            ref_e = jd.get("E")

    meta_path = os.path.join(REPO, OUT, f"{net_id}.meta")
    with open(meta_path, "w") as f:
        f.write(f"N={n}\n")
        f.write(f"E={e}\n")
        f.write(f"max_deg={max_deg}\n")
        f.write(f"full_N={full_n}\n")
        f.write(f"full_E={len(edges_set)}\n")
        f.write(f"graph=lcc\n")
        f.write(f"kappa_ref={kappa_ref}\n")
        f.write(f"geometry={geometry_ref}\n")
        f.write(f"ref_N={ref_n}\n")
        f.write(f"ref_E={ref_e}\n")

    match = ""
    if ref_n is not None and (ref_n != n or ref_e != e):
        match = f" MISMATCH ref N={ref_n} E={ref_e}"
    elif ref_n is not None:
        match = " ref_ok"

    kappa_str = f"{kappa_ref:.6f}" if kappa_ref is not None else "N/A"
    print(
        f"  OK {net_id:15s}: LCC N={n:4d} E={e:4d} max_deg={max_deg:3d} "
        f"kappa_ref={kappa_str}{match}"
    )

print("Done. LCC edge lists in", os.path.join(REPO, OUT))
