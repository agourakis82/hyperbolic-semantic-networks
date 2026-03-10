"""
Extract hyperedges from ConceptNet and BabelNet edge lists.

Two types of hyperedges:
  Type A — Relation-cluster: connected components within each relation subgraph
  Type B — Multi-relation: concept pairs connected by ≥2 relation types, expanded
           with their shared neighbors

Processes: conceptnet_en, conceptnet_pt, babelnet_ru, babelnet_ar
Output: data/processed/{network}_hyperedges.json
"""
import json
import csv
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path("data/processed")

NETWORKS = [
    ("conceptnet_en", "conceptnet_en_edges.csv"),
    ("conceptnet_pt", "conceptnet_pt_edges.csv"),
    ("babelnet_ru", "babelnet_ru_edges.csv"),
    ("babelnet_ar", "babelnet_ar_edges.csv"),
]


def load_edges(csv_path):
    """Load edges with relation types. Returns list of (source, target, relation)."""
    edges = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            edges.append((row["source"], row["target"], row.get("relation", "unknown")))
    return edges


def build_node_map(edges):
    """Build node name → integer ID mapping."""
    nodes = set()
    for s, t, _ in edges:
        nodes.add(s)
        nodes.add(t)
    return {name: i for i, name in enumerate(sorted(nodes))}


def find_components(adj):
    """Find connected components via BFS."""
    visited = set()
    components = []
    for node in adj:
        if node in visited:
            continue
        comp = []
        queue = [node]
        while queue:
            v = queue.pop()
            if v in visited:
                continue
            visited.add(v)
            comp.append(v)
            queue.extend(n for n in adj[v] if n not in visited)
        if len(comp) >= 2:
            components.append(sorted(comp))
    return components


def extract_hyperedges(edges, node_map):
    """
    Extract two types of hyperedges:
      Type A: Connected components within each relation subgraph
      Type B: Concept pairs connected by ≥2 different relations
    """
    # Group edges by relation
    rel_edges = defaultdict(list)
    # Track multi-relation pairs
    pair_relations = defaultdict(set)

    for s, t, r in edges:
        sid, tid = node_map[s], node_map[t]
        rel_edges[r].append((sid, tid))
        pair = (min(sid, tid), max(sid, tid))
        pair_relations[pair].add(r)

    # --- Type A: relation-cluster hyperedges ---
    type_a = []
    relation_stats = {}
    for rel, redges in rel_edges.items():
        # Build adjacency for this relation
        adj = defaultdict(set)
        for u, v in redges:
            adj[u].add(v)
            adj[v].add(u)
        components = find_components(adj)
        type_a.extend(components)
        relation_stats[rel] = {
            "n_edges": len(redges),
            "n_components": len(components),
            "max_component_size": max(len(c) for c in components) if components else 0,
        }

    # --- Type B: multi-relation hyperedges ---
    type_b = []
    # Find pairs with ≥2 relations
    multi_pairs = {pair: rels for pair, rels in pair_relations.items() if len(rels) >= 2}

    # For each multi-relation pair, expand with shared neighbors
    # Build global adjacency
    adj_global = defaultdict(set)
    for s, t, _ in edges:
        sid, tid = node_map[s], node_map[t]
        adj_global[sid].add(tid)
        adj_global[tid].add(sid)

    for (u, v), rels in multi_pairs.items():
        # Shared neighbors
        shared = adj_global[u] & adj_global[v]
        he = sorted({u, v} | shared)
        if len(he) >= 2:
            type_b.append(he)

    # Deduplicate
    all_hyperedges = list({tuple(h) for h in type_a + type_b})
    all_hyperedges = [list(h) for h in sorted(all_hyperedges)]

    # Clique expansion (pairwise edges from hyperedges)
    pairwise = set()
    for he in all_hyperedges:
        for i in range(len(he)):
            for j in range(i + 1, len(he)):
                pairwise.add((he[i], he[j]))

    return all_hyperedges, type_a, type_b, pairwise, relation_stats


def process_network(net_id, csv_file):
    csv_path = DATA_DIR / csv_file
    if not csv_path.exists():
        print(f"  SKIP {net_id}: {csv_path} not found")
        return

    print(f"\n{'='*50}")
    print(f"Processing: {net_id}")
    print(f"{'='*50}")

    edges = load_edges(csv_path)
    print(f"  Edges: {len(edges)}")

    node_map = build_node_map(edges)
    n_nodes = len(node_map)
    print(f"  Nodes: {n_nodes}")

    # Count relation types
    rels = set(r for _, _, r in edges)
    print(f"  Relation types: {len(rels)}")

    all_he, type_a, type_b, pairwise, rel_stats = extract_hyperedges(edges, node_map)

    print(f"  Type A (relation-cluster): {len(type_a)}")
    print(f"  Type B (multi-relation): {len(type_b)}")
    print(f"  Total unique hyperedges: {len(all_he)}")
    print(f"  Pairwise projection edges: {len(pairwise)}")

    if all_he:
        sizes = [len(h) for h in all_he]
        print(f"  Mean hyperedge size: {sum(sizes)/len(sizes):.2f}")
        print(f"  Max hyperedge size: {max(sizes)}")

    # Top relations by component count
    top_rels = sorted(rel_stats.items(), key=lambda x: -x[1]["n_edges"])[:5]
    print(f"  Top relations:")
    for r, s in top_rels:
        print(f"    {r}: {s['n_edges']} edges, {s['n_components']} components, max={s['max_component_size']}")

    # Invert node_map for output
    id_to_name = {v: k for k, v in node_map.items()}

    result = {
        "network": net_id,
        "n_nodes": n_nodes,
        "nodes": {str(v): k for k, v in node_map.items()},
        "synset_hyperedges": type_a,  # reuse same field name for compatibility
        "hypernymy_hyperedges": type_b,
        "pairwise_edges": [list(e) for e in sorted(pairwise)],
        "stats": {
            "n_synset_hyperedges": len(type_a),
            "n_hypernymy_hyperedges": len(type_b),
            "n_pairwise_edges": len(pairwise),
            "mean_synset_size": sum(len(h) for h in all_he) / len(all_he) if all_he else 0,
            "n_relation_types": len(rels),
            "relation_stats": rel_stats,
        },
    }

    out_path = DATA_DIR / f"{net_id}_hyperedges.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"  Saved to {out_path}")


def main():
    for net_id, csv_file in NETWORKS:
        process_network(net_id, csv_file)
    print("\nDone.")


if __name__ == "__main__":
    main()
