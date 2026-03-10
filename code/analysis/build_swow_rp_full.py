#!/usr/bin/env python3
"""
Build full SWOW-RP graph without the TOP_N=500 cap.

Expects the balanced R70 file at:
  data/scratch/SWOW-RP/data/SWOW/raw/SWOW-RP.R70.csv

Output:
  data/processed/swow_rp_full_edges.csv   (source,target,weight)

Also outputs node mapping for hyperedge extraction:
  data/processed/swow_rp_full_nodes.json  ({name: id})
"""
import csv
import json
import collections
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "data" / "processed"
SCRATCH_DIR = REPO_ROOT / "data" / "scratch"

MIN_WEIGHT = 0.01

# Possible locations for raw R70 data
RAW_CANDIDATES = [
    SCRATCH_DIR / "SWOW-RP" / "data" / "SWOW" / "raw" / "SWOW-RP.R70.csv",
    SCRATCH_DIR / "SWOW-RP" / "data" / "SWOW" / "SWOW-RP.R70.csv",
    SCRATCH_DIR / "swow_rp_raw.csv",
]

# Spell corrections
CORRECTIONS_PATH = SCRATCH_DIR / "SWOW-RP" / "data" / "dictionaries" / "responseCorrections.csv"


def load_corrections():
    """Load response corrections: original -> corrected."""
    corr = {}
    if not CORRECTIONS_PATH.exists():
        print(f"  No corrections file at {CORRECTIONS_PATH}")
        return corr
    with open(CORRECTIONS_PATH, encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                corr[row[0].strip().lower()] = row[1].strip().lower()
    print(f"  Loaded {len(corr)} spell corrections")
    return corr


def find_raw_data():
    """Find the R70 CSV file."""
    for p in RAW_CANDIDATES:
        if p.exists():
            return p
    # Try glob for any matching pattern
    for p in (SCRATCH_DIR / "SWOW-RP").rglob("*R70*"):
        if p.suffix in (".csv", ".tsv"):
            return p
    return None


def parse_r70(csv_path, corrections):
    """Parse R70 CSV → directed (cue, response) pairs with association strength."""
    pairs = collections.Counter()
    cue_totals = collections.Counter()
    # Also track per-cue response sets for later hyperedge extraction
    cue_responses = collections.defaultdict(set)

    with open(csv_path, encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        fieldnames = [c.lower().strip() for c in (reader.fieldnames or [])]

        # Detect columns
        resp_cols = []
        cue_col = None
        for fn in fieldnames:
            if fn in ("cue", "cueword", "stimulus"):
                cue_col = fn
            elif fn in ("r1", "r2", "r3", "response", "response1", "response2", "response3"):
                resp_cols.append(fn)

        if not cue_col or not resp_cols:
            raise ValueError(f"Cannot detect cue/response columns. Found: {fieldnames}")

        print(f"  Columns: cue={cue_col}, responses={resp_cols}")
        n_rows = 0
        for row in reader:
            row_lower = {k.lower().strip(): v for k, v in row.items()}
            cue = row_lower.get(cue_col, "").strip().lower()
            if not cue:
                continue
            # Apply correction to cue
            cue = corrections.get(cue, cue)
            n_rows += 1
            for rc in resp_cols:
                resp = row_lower.get(rc, "").strip().lower()
                if resp and resp != cue and resp not in ("x", "na", "n/a", "none", ""):
                    resp = corrections.get(resp, resp)
                    pairs[(cue, resp)] += 1
                    cue_totals[cue] += 1
                    cue_responses[cue].add(resp)

        print(f"  Parsed {n_rows} rows, {len(pairs)} unique directed pairs")
        print(f"  Unique cues: {len(cue_totals)}, unique responses: {len(set(r for _,r in pairs))}")

    return pairs, cue_totals, cue_responses


def build_full_graph(pairs, cue_totals):
    """Build undirected weighted edge list without TOP_N cap."""
    # Compute association strengths
    edges = []
    for (cue, resp), count in pairs.items():
        w = count / max(cue_totals[cue], 1)
        if w >= MIN_WEIGHT:
            edges.append((cue, resp, w))

    print(f"  Directed edges (w >= {MIN_WEIGHT}): {len(edges)}")

    # Convert to undirected (max weight per pair)
    weight = {}
    for u, v, w in edges:
        pair = (min(u, v), max(u, v))
        if w > weight.get(pair, -1):
            weight[pair] = w
    undirected = [(u, v, w) for (u, v), w in weight.items()]

    print(f"  Undirected edges: {len(undirected)}")

    # Extract LCC
    nodes = set()
    adj = collections.defaultdict(set)
    for u, v, _ in undirected:
        nodes.add(u)
        nodes.add(v)
        adj[u].add(v)
        adj[v].add(u)

    print(f"  Total nodes before LCC: {len(nodes)}")

    # BFS to find LCC
    visited = set()
    largest_comp = set()
    for start in nodes:
        if start in visited:
            continue
        comp = set()
        queue = [start]
        while queue:
            n = queue.pop()
            if n in visited:
                continue
            visited.add(n)
            comp.add(n)
            queue.extend(nb for nb in adj[n] if nb not in visited)
        if len(comp) > len(largest_comp):
            largest_comp = comp

    lcc_edges = [(u, v, w) for u, v, w in undirected
                 if u in largest_comp and v in largest_comp]
    print(f"  LCC nodes: {len(largest_comp)}, LCC edges: {len(lcc_edges)}")

    return lcc_edges, largest_comp


def save_results(edges, lcc_nodes):
    """Save edge list and node mapping."""
    # Build node map (sorted for reproducibility)
    node_map = {name: i for i, name in enumerate(sorted(lcc_nodes))}

    # Save edges
    out_path = DATA_DIR / "swow_rp_full_edges.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source", "target", "weight"])
        for u, v, w in sorted(edges):
            writer.writerow([u, v, f"{w:.6f}"])
    print(f"  Saved {len(edges)} edges → {out_path.name}")

    # Save node map for hyperedge extraction
    nodes_path = DATA_DIR / "swow_rp_full_nodes.json"
    with open(nodes_path, "w") as f:
        json.dump(node_map, f, indent=2, ensure_ascii=False)
    print(f"  Saved {len(node_map)} node mappings → {nodes_path.name}")

    return node_map


def main():
    print("=" * 60)
    print("Build Full SWOW-RP Graph (no TOP_N cap)")
    print("=" * 60)

    csv_path = find_raw_data()
    if csv_path is None:
        print("\n  ERROR: Raw SWOW-RP R70 data not found.")
        print("  Expected at one of:")
        for p in RAW_CANDIDATES:
            print(f"    {p}")
        print("\n  To obtain the data:")
        print("  1. Visit https://smallworldofwords.org/project/research/")
        print("  2. Request/download the Rioplatense Spanish R70 balanced dataset")
        print("  3. Place the CSV at one of the paths above")
        print("  4. Rerun this script")
        return

    print(f"  Found raw data: {csv_path}")
    corrections = load_corrections()
    pairs, cue_totals, cue_responses = parse_r70(csv_path, corrections)
    edges, lcc_nodes = build_full_graph(pairs, cue_totals)
    node_map = save_results(edges, lcc_nodes)

    # Save cue_responses for hyperedge extraction
    cue_resp_path = DATA_DIR / "swow_rp_full_cue_responses.json"
    cue_resp_serializable = {cue: sorted(resps) for cue, resps in cue_responses.items()
                              if cue in lcc_nodes}
    with open(cue_resp_path, "w", encoding="utf-8") as f:
        json.dump(cue_resp_serializable, f, indent=2, ensure_ascii=False)
    print(f"  Saved cue-response sets → {cue_resp_path.name}")

    # Summary stats
    N = len(lcc_nodes)
    E = len(edges)
    k_mean = 2 * E / N if N > 0 else 0
    eta = k_mean**2 / N if N > 0 else 0
    print(f"\n  Summary: N={N}, E={E}, <k>={k_mean:.1f}, η={eta:.3f}")
    print(f"  Phase prediction: {'SPHERICAL' if eta > 3.75 else 'HYPERBOLIC'} (η_c≈3.75)")


if __name__ == "__main__":
    main()
