#!/usr/bin/env python3
"""
Preprocess SWOW CSV files into Sounio-compatible edge array format.

Converts CSV edge lists into hardcoded Sounio arrays that can be
compiled directly into the binary.

Usage:
    python preprocess_swow_for_sounio.py spanish
    python preprocess_swow_for_sounio.py english
    python preprocess_swow_for_sounio.py chinese
"""

import sys
import pandas as pd
from pathlib import Path

def preprocess_swow(language: str):
    """Convert SWOW CSV to Sounio edge array format."""
    
    # Load edge list
    edge_file = Path(f"../../data/processed/{language}_edges.csv")
    if not edge_file.exists():
        print(f"ERROR: {edge_file} not found")
        return
    
    df = pd.read_csv(edge_file)
    print(f"Loaded {language}: {len(df)} edges")
    
    # Get unique nodes
    nodes = sorted(set(df['source'].unique()) | set(df['target'].unique()))
    node_to_id = {node: i for i, node in enumerate(nodes)}
    
    n_nodes = len(nodes)
    n_edges = len(df)
    
    print(f"  Nodes: {n_nodes}")
    print(f"  Edges: {n_edges}")
    
    # Convert to integer edge list (undirected - add both directions)
    edges = []
    for _, row in df.iterrows():
        u = node_to_id[row['source']]
        v = node_to_id[row['target']]
        edges.append((u, v))
    
    # Compute max degree
    from collections import Counter
    deg = Counter()
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
    
    max_deg = max(deg.values())
    print(f"  Max degree: {max_deg}")
    
    # Generate Sounio code
    output_file = Path(f"swow_{language}_edges.sio.inc")
    
    with open(output_file, 'w') as f:
        f.write(f"// SWOW {language.capitalize()} Network - Auto-generated\n")
        f.write(f"// Nodes: {n_nodes}, Edges: {n_edges}, Max Degree: {max_deg}\n\n")
        
        f.write(f"let N_NODES: usize = {n_nodes};\n")
        f.write(f"let N_EDGES: usize = {n_edges};\n")
        f.write(f"let MAX_DEG: usize = {max_deg};\n\n")
        
        # Write edge array
        f.write(f"let EDGES: [(usize, usize); {n_edges}] = [\n")
        for i, (u, v) in enumerate(edges):
            f.write(f"    ({u}, {v})")
            if i < len(edges) - 1:
                f.write(",")
            f.write("\n")
        f.write("];\n\n")
        
        # Write node names for reference
        f.write("// Node ID -> Word mapping:\n")
        for i, node in enumerate(nodes[:20]):  # First 20 only
            f.write(f"// {i}: {node}\n")
        if len(nodes) > 20:
            f.write(f"// ... ({len(nodes) - 20} more nodes)\n")
    
    print(f"\n✅ Generated: {output_file}")
    print(f"\nTo use in Sounio:")
    print(f"  1. Include in your .sio file")
    print(f"  2. Build graph with: build_from_edges(EDGES, N_EDGES, N_NODES)")
    print()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python preprocess_swow_for_sounio.py <language>")
        print("  language: spanish, english, or chinese")
        sys.exit(1)
    
    language = sys.argv[1].lower()
    if language not in ['spanish', 'english', 'chinese']:
        print(f"ERROR: Unknown language '{language}'")
        print("  Supported: spanish, english, chinese")
        sys.exit(1)
    
    preprocess_swow(language)

