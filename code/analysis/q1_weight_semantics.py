#!/usr/bin/env python3
"""
Q1 TEST 2.2: WEIGHT SEMANTICS VALIDATION
Critical test from Q1 reviewer

Goal: Test both metric and affinity interpretations of weights
Method: Compute clustering with both conventions, compare Ricci flow behavior
Author: Darwin Q1 Agent
Date: 2025-11-05
"""

import argparse
import json
import logging
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def compute_clustering_both_conventions(G: nx.Graph) -> dict:
    """
    Compute clustering with both weight interpretations
    
    1. Affinity (standard): Higher weight = stronger connection
    2. Metric (Ricci flow): weight as length, convert to affinity first
    
    Returns:
        Dictionary with both clustering values
    """
    logger.info("Computing clustering - AFFINITY interpretation (w = strength)...")
    
    # Method 1: Weights as affinity (Onnela/Barrat formula)
    clustering_affinity = nx.clustering(G, weight='weight')
    C_affinity_mean = np.mean(list(clustering_affinity.values()))
    
    logger.info(f"  Clustering (affinity): {C_affinity_mean:.4f}")
    
    # Method 2: Convert weights to metric (distance), then back to affinity for clustering
    logger.info("Computing clustering - METRIC interpretation (w = 1/strength)...")
    
    G_metric = G.copy()
    
    # Convert: affinity → metric (length)
    # d = 1 / w_affinity (or similar monotonic transform)
    for u, v, data in G_metric.edges(data=True):
        w_affinity = data.get('weight', 1.0)
        # Metric: d = 1/w (larger affinity → smaller distance)
        d_metric = 1.0 / max(w_affinity, 1e-6)  # Avoid division by zero
        G_metric[u][v]['weight_metric'] = d_metric
    
    # For clustering, need to convert back: affinity_for_clustering = 1/d
    # But we can also compute clustering on metric directly (inverse interpretation)
    
    # Option A: Compute on metric weights directly
    clustering_metric_direct = nx.clustering(G_metric, weight='weight_metric')
    C_metric_direct = np.mean(list(clustering_metric_direct.values()))
    
    # Option B: Convert metric back to affinity for clustering
    G_metric_to_affinity = G_metric.copy()
    for u, v, data in G_metric_to_affinity.edges(data=True):
        d = data['weight_metric']
        # Affinity = 1/d
        w_new = 1.0 / max(d, 1e-6)
        G_metric_to_affinity[u][v]['weight'] = w_new
    
    clustering_metric_converted = nx.clustering(G_metric_to_affinity, weight='weight')
    C_metric_converted = np.mean(list(clustering_metric_converted.values()))
    
    logger.info(f"  Clustering (metric, direct): {C_metric_direct:.4f}")
    logger.info(f"  Clustering (metric → affinity): {C_metric_converted:.4f}")
    
    # Binary clustering (unweighted, for reference)
    clustering_binary = nx.clustering(G)
    C_binary = np.mean(list(clustering_binary.values()))
    
    logger.info(f"  Clustering (binary, unweighted): {C_binary:.4f}")
    
    results = {
        'C_affinity': float(C_affinity_mean),
        'C_metric_direct': float(C_metric_direct),
        'C_metric_converted': float(C_metric_converted),
        'C_binary': float(C_binary),
        'interpretation': {
            'affinity': 'Onnela/Barrat formula, w = strength',
            'metric_direct': 'Computed on d = 1/w (inverse weights)',
            'metric_converted': 'd = 1/w, then clustering on w_new = 1/d',
            'binary': 'Unweighted (ignore edge weights)'
        }
    }
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Test weight semantics')
    parser.add_argument('--language', required=True, choices=['spanish', 'english', 'chinese'])
    parser.add_argument('--edge-file', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    
    args = parser.parse_args()
    
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("="*70)
    logger.info("Q1 TEST 2.2: WEIGHT SEMANTICS VALIDATION")
    logger.info("="*70)
    logger.info(f"Language: {args.language}")
    logger.info("")
    
    # Load network
    df_edges = pd.read_csv(args.edge_file)
    
    G_dir = nx.DiGraph()
    for _, row in df_edges.iterrows():
        G_dir.add_edge(row['source'], row['target'], weight=row['weight'])
    
    G = G_dir.to_undirected()
    
    if not nx.is_connected(G):
        components = list(nx.connected_components(G))
        largest_cc = max(components, key=len)
        G = G.subgraph(largest_cc).copy()
    
    logger.info(f"Network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    logger.info("")
    
    # Test both conventions
    results = compute_clustering_both_conventions(G)
    
    # Add metadata
    results['language'] = args.language
    results['n_nodes'] = G.number_of_nodes()
    results['n_edges'] = G.number_of_edges()
    
    # Save
    output_file = args.output_dir / f'weight_semantics_{args.language}.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info("")
    logger.info(f"Results saved to: {output_file}")
    logger.info("")
    logger.info("="*70)
    logger.info("KEY INSIGHT:")
    logger.info("="*70)
    logger.info(f"Affinity (standard):        C = {results['C_affinity']:.4f}")
    logger.info(f"Binary (unweighted):        C = {results['C_binary']:.4f}")
    logger.info(f"Metric (for Ricci flow):    C = {results['C_metric_converted']:.4f}")
    logger.info("")
    logger.info("Use C_affinity for manuscript (standard practice)")
    logger.info("Use C_metric_converted for Ricci flow context")
    logger.info("="*70)
    
    return results


if __name__ == '__main__':
    main()

