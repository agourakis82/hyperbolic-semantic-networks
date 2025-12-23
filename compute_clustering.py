#!/usr/bin/env python3
"""
Compute clustering coefficients for all SWOW networks.
This completes the validation by providing missing metrics.
"""

import networkx as nx
import pandas as pd
import json
from pathlib import Path

def compute_network_metrics(edge_file):
    """Load network and compute comprehensive metrics."""
    df = pd.read_csv(edge_file)

    # Build undirected graph
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row['source'], row['target'], weight=row['weight'])

    # Get largest connected component
    if not nx.is_connected(G):
        Gcc = max(nx.connected_components(G), key=len)
        G = G.subgraph(Gcc).copy()

    # Compute metrics
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    clustering = nx.average_clustering(G)
    degrees = [d for _, d in G.degree()]
    avg_degree = sum(degrees) / len(degrees)

    # Degree distribution stats
    degree_min = min(degrees)
    degree_max = max(degrees)

    return {
        'n_nodes': n_nodes,
        'n_edges': n_edges,
        'clustering': clustering,
        'avg_degree': avg_degree,
        'degree_min': degree_min,
        'degree_max': degree_max
    }

def main():
    # Define networks to analyze
    networks = {
        'spanish': 'data/processed/spanish_edges_FINAL.csv',
        'english': 'data/processed/english_edges_FINAL.csv',
        'chinese': 'data/processed/chinese_edges_FINAL.csv',
        'dutch': 'data/processed/dutch_edges.csv'
    }

    results = {}

    print("Computing clustering coefficients for SWOW networks...\n")

    for lang, edge_file in networks.items():
        print(f"Processing {lang.upper()}...")
        metrics = compute_network_metrics(edge_file)
        results[lang] = metrics

        print(f"  N = {metrics['n_nodes']}")
        print(f"  E = {metrics['n_edges']}")
        print(f"  C = {metrics['clustering']:.6f}")
        print(f"  ⟨k⟩ = {metrics['avg_degree']:.2f}")
        print(f"  k_min = {metrics['degree_min']}, k_max = {metrics['degree_max']}")
        print()

    # Save results
    output_file = 'results/swow_clustering_coefficients.json'
    Path('results').mkdir(exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to {output_file}")

    # Check clustering regime
    print("\n" + "="*60)
    print("CLUSTERING REGIME ANALYSIS")
    print("="*60)
    print("Hyperbolic sweet spot: C = 0.02 to 0.15")
    print()

    for lang, metrics in results.items():
        C = metrics['clustering']
        if 0.02 <= C <= 0.15:
            regime = "✅ HYPERBOLIC REGIME"
        elif C > 0.15:
            regime = "⚠️  SPHERICAL REGIME (too clustered)"
        else:
            regime = "⚠️  EUCLIDEAN REGIME (too sparse)"

        print(f"{lang.upper():10s}: C = {C:.6f}  {regime}")

if __name__ == '__main__':
    main()
