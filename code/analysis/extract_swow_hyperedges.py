#!/usr/bin/env python3
"""
Extract response-cluster hyperedges from SWOW-RP.

For each cue word, the set of all unique responses forms a hyperedge:
  hyperedge = {cue, resp1, resp2, ..., respK}

This captures the associative neighborhood structure that pairwise edges miss.

Requires:
  - data/processed/swow_rp_full_edges.csv (from build_swow_rp_full.py)
  - data/processed/swow_rp_full_nodes.json (node name→ID mapping)
  - data/processed/swow_rp_full_cue_responses.json (cue→[responses])

Output:
  data/processed/swow_rp_full_hyperedges.json
"""
import json
from pathlib import Path

DATA_DIR = Path("data/processed")
MAX_HYPEREDGE_SIZE = 50  # cap noisy large clusters


def main():
    print("=" * 60)
    print("Extract SWOW-RP Response-Cluster Hyperedges")
    print("=" * 60)

    # Load node map
    nodes_path = DATA_DIR / "swow_rp_full_nodes.json"
    if not nodes_path.exists():
        print(f"  ERROR: {nodes_path} not found. Run build_swow_rp_full.py first.")
        return
    with open(nodes_path) as f:
        node_map = json.load(f)
    n_nodes = len(node_map)
    print(f"  Nodes: {n_nodes}")

    # Load cue-response sets
    cr_path = DATA_DIR / "swow_rp_full_cue_responses.json"
    if not cr_path.exists():
        print(f"  ERROR: {cr_path} not found. Run build_swow_rp_full.py first.")
        return
    with open(cr_path, encoding="utf-8") as f:
        cue_responses = json.load(f)
    print(f"  Cues with responses: {len(cue_responses)}")

    # Load base pairwise edges
    import csv
    base_edges = set()
    edge_path = DATA_DIR / "swow_rp_full_edges.csv"
    with open(edge_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            s, t = row["source"], row["target"]
            if s in node_map and t in node_map:
                sid, tid = node_map[s], node_map[t]
                base_edges.add((min(sid, tid), max(sid, tid)))

    # Build hyperedges: for each cue, {cue} ∪ {responses in LCC}
    hyperedges = []
    sizes = []
    n_capped = 0
    for cue, responses in cue_responses.items():
        if cue not in node_map:
            continue
        members = {node_map[cue]}
        for r in responses:
            if r in node_map:
                members.add(node_map[r])
        if len(members) < 2:
            continue
        members = sorted(members)
        if len(members) > MAX_HYPEREDGE_SIZE:
            members = members[:MAX_HYPEREDGE_SIZE]
            n_capped += 1
        hyperedges.append(members)
        sizes.append(len(members))

    # Deduplicate
    hyperedges = [list(h) for h in sorted(set(tuple(h) for h in hyperedges))]

    print(f"  Hyperedges: {len(hyperedges)}")
    if sizes:
        print(f"  Mean size: {sum(sizes)/len(sizes):.1f}")
        print(f"  Max size: {max(sizes)} (capped {n_capped} at {MAX_HYPEREDGE_SIZE})")
        print(f"  Min size: {min(sizes)}")

    # Clique expansion (pairwise projection)
    pairwise = set()
    for he in hyperedges:
        for i in range(len(he)):
            for j in range(i + 1, len(he)):
                pairwise.add((he[i], he[j]))
    print(f"  Pairwise projection edges: {len(pairwise)}")

    # Build output JSON (compatible with resolution_curvature.jl)
    id_to_name = {int(v): k for k, v in node_map.items()}
    result = {
        "network": "swow_rp_full",
        "n_nodes": n_nodes,
        "nodes": {str(v): k for k, v in node_map.items()},
        "synset_hyperedges": hyperedges,
        "hypernymy_hyperedges": [],
        "pairwise_edges": [list(e) for e in sorted(pairwise)],
        "stats": {
            "n_synset_hyperedges": len(hyperedges),
            "n_hypernymy_hyperedges": 0,
            "n_pairwise_edges": len(pairwise),
            "mean_synset_size": sum(sizes) / len(sizes) if sizes else 0,
            "max_synset_size": max(sizes) if sizes else 0,
            "n_capped": n_capped,
            "max_hyperedge_cap": MAX_HYPEREDGE_SIZE,
        },
    }

    out_path = DATA_DIR / "swow_rp_full_hyperedges.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"  Saved → {out_path}")


if __name__ == "__main__":
    main()
