#!/usr/bin/env python3
"""
Compute KEC Metrics for Psychopathology Networks
Using validated KEC framework from pcs-meta-repo
"""

import sys
from pathlib import Path
import networkx as nx
import pandas as pd
import numpy as np
import json

# Import KEC framework (copied from pcs-meta-repo)
from kec_framework import compute_kec_metrics

# Try to convert NetworkX to igraph
try:
    import igraph as ig
except ImportError:
    print("⚠️ igraph not installed. Installing...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "python-igraph"], check=True)
    import igraph as ig

print("="*70)
print("COMPUTE KEC FOR PSYCHOPATHOLOGY NETWORKS")
print("Using validated framework from pcs-meta-repo")
print("="*70)
print()

# ============================================================================
# FUNCTION: Convert NetworkX to igraph
# ============================================================================

def networkx_to_igraph(G_nx):
    """Convert NetworkX graph to igraph graph"""
    print(f"Converting NetworkX graph to igraph...")
    print(f"  Nodes: {G_nx.number_of_nodes()}")
    print(f"  Edges: {G_nx.number_of_edges()}")
    
    # Create igraph
    G_ig = ig.Graph(directed=G_nx.is_directed())
    
    # Add nodes
    node_list = list(G_nx.nodes())
    G_ig.add_vertices(len(node_list))
    G_ig.vs["name"] = node_list
    
    # Add edges with weights
    edges = []
    weights = []
    for u, v, data in G_nx.edges(data=True):
        u_idx = node_list.index(u)
        v_idx = node_list.index(v)
        edges.append((u_idx, v_idx))
        weights.append(data.get('weight', 1.0))
    
    G_ig.add_edges(edges)
    G_ig.es["weight"] = weights
    
    print(f"✅ Converted to igraph")
    print()
    
    return G_ig

# ============================================================================
# LOAD OUR SEMANTIC NETWORKS
# ============================================================================

print("LOADING SEMANTIC NETWORKS")
print("-"*70)

# We have edge lists from SWOW
networks = {}

languages = {
    'spanish': 'data/processed/spanish_edges.csv',
    'english': 'data/processed/english_edges.csv',
    'chinese': 'data/processed/chinese_edges.csv'
}

for lang, edge_file in languages.items():
    if Path(edge_file).exists():
        print(f"Loading {lang}...")
        df_edges = pd.read_csv(edge_file)
        
        # Build NetworkX graph
        G_nx = nx.Graph()  # Undirected
        for _, row in df_edges.iterrows():
            weight = row.get('strength', 1.0) if 'strength' in df_edges.columns else 1.0
            G_nx.add_edge(row['source'], row['target'], weight=weight)
        
        # Convert to igraph
        G_ig = networkx_to_igraph(G_nx)
        networks[lang] = G_ig
        
        print(f"  ✅ {lang}: {G_ig.vcount()} nodes, {G_ig.ecount()} edges")
    else:
        print(f"  ⚠️ {lang}: File not found")

print()

# ============================================================================
# COMPUTE KEC METRICS
# ============================================================================

print("="*70)
print("COMPUTING KEC METRICS")
print("="*70)
print()

all_kec_results = {}

for lang, G_ig in networks.items():
    print(f"\n{'='*70}")
    print(f"Language: {lang.upper()}")
    print(f"{'='*70}\n")
    
    # Compute KEC using pcs-meta-repo function
    kec_df = compute_kec_metrics(G_ig)
    
    print(f"✅ Computed KEC for {len(kec_df)} nodes")
    print()
    print("Summary statistics:")
    print(kec_df[['entropy', 'curvature', 'coherence']].describe())
    print()
    
    # Compute network-level KEC
    mean_entropy = kec_df['entropy'].mean()
    mean_curvature = kec_df['curvature'].mean()
    mean_coherence = kec_df['coherence'].mean()  # Note: this is actually modularity (graph-level)
    
    # Normalize to 0-1 (simple min-max for now)
    # In real analysis, use cross-network normalization
    
    network_kec = (mean_entropy + mean_curvature - mean_coherence) / 3
    
    print(f"NETWORK-LEVEL KEC:")
    print(f"  H (entropy):    {mean_entropy:.3f}")
    print(f"  κ (curvature):  {mean_curvature:.3f}")
    print(f"  C (coherence):  {mean_coherence:.3f}")
    print(f"  KEC:            {network_kec:.3f}")
    print()
    
    all_kec_results[lang] = {
        'node_level': kec_df,
        'network_level': {
            'entropy': mean_entropy,
            'curvature': mean_curvature,
            'coherence': mean_coherence,
            'kec': network_kec
        }
    }
    
    # Save node-level results
    output_file = f'results/kec_{lang}_node_level.csv'
    kec_df.to_csv(output_file, index=False)
    print(f"✅ Saved: {output_file}")

# ============================================================================
# SAVE NETWORK-LEVEL SUMMARY
# ============================================================================

print("\n" + "="*70)
print("NETWORK-LEVEL KEC SUMMARY")
print("="*70)
print()

summary = {}
for lang, results in all_kec_results.items():
    summary[lang] = results['network_level']

summary_df = pd.DataFrame(summary).T
print(summary_df)
print()

summary_df.to_csv('results/kec_network_level_summary.csv')

# Save as JSON too
with open('results/kec_network_level_summary.json', 'w') as f:
    # Convert numpy types to python types for JSON
    json_summary = {}
    for lang, metrics in summary.items():
        json_summary[lang] = {k: float(v) for k, v in metrics.items()}
    json.dump(json_summary, f, indent=2)

print("✅ Saved:")
print("  - results/kec_network_level_summary.csv")
print("  - results/kec_network_level_summary.json")
print()

print("="*70)
print("✅ KEC COMPUTATION COMPLETE!")
print("="*70)
print()
print("🎯 NEXT: Apply same methods to MDD vs. Control networks!")

