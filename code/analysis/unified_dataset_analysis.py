#!/usr/bin/env python3
"""
Unified analysis pipeline for all semantic network datasets
Computes: Curvature, Config nulls, Clustering-curvature relationship
"""

import json
import logging
import argparse
import numpy as np
import pandas as pd
import networkx as nx
from pathlib import Path
from tqdm import tqdm
from GraphRicciCurvature.OllivierRicci import OllivierRicci

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_network(edge_file):
    """Load network from edge list"""
    logger.info(f"Loading network from: {edge_file}")
    df = pd.read_csv(edge_file)
    
    G = nx.DiGraph()
    for _, row in df.iterrows():
        G.add_edge(row['source'], row['target'], weight=row['weight'])
    
    logger.info(f"  Nodes: {G.number_of_nodes():,}")
    logger.info(f"  Edges: {G.number_of_edges():,}")
    logger.info(f"  Density: {nx.density(G):.6f}")
    
    return G


def compute_curvature(G, alpha=0.5):
    """Compute Ollivier-Ricci curvature"""
    logger.info("Computing Ollivier-Ricci curvature...")
    
    # Convert to undirected for curvature
    G_undir = G.to_undirected()
    
    # Compute curvature
    orc = OllivierRicci(G_undir, alpha=alpha, weight='weight', verbose='ERROR')
    orc.compute_ricci_curvature()
    
    curvatures = [d['ricciCurvature'] for u, v, d in orc.G.edges(data=True)]
    
    logger.info(f"  Mean κ: {np.mean(curvatures):.4f}")
    logger.info(f"  Std κ: {np.std(curvatures):.4f}")
    logger.info(f"  Min κ: {np.min(curvatures):.4f}")
    logger.info(f"  Max κ: {np.max(curvatures):.4f}")
    
    return {
        'kappa_mean': float(np.mean(curvatures)),
        'kappa_std': float(np.std(curvatures)),
        'kappa_min': float(np.min(curvatures)),
        'kappa_max': float(np.max(curvatures)),
        'kappa_all': curvatures
    }


def compute_clustering(G):
    """Compute clustering coefficient"""
    G_undir = G.to_undirected()
    
    # Weighted clustering (Onnela-Barrat)
    clustering_dict = nx.clustering(G_undir, weight='weight')
    C_weighted = np.mean(list(clustering_dict.values()))
    
    # Binary clustering
    G_binary = G_undir.copy()
    for u, v in G_binary.edges():
        G_binary[u][v]['weight'] = 1.0
    clustering_binary = nx.average_clustering(G_binary, weight='weight')
    
    logger.info(f"  Clustering (weighted): {C_weighted:.4f}")
    logger.info(f"  Clustering (binary): {clustering_binary:.4f}")
    
    return {
        'clustering_weighted': float(C_weighted),
        'clustering_binary': float(clustering_binary)
    }


def main(dataset_name, edge_file, output_dir, alpha=0.5):
    logger.info("="*70)
    logger.info(f"UNIFIED ANALYSIS: {dataset_name.upper()}")
    logger.info("="*70)
    logger.info("")
    
    # Load network
    G = load_network(edge_file)
    logger.info("")
    
    # Compute clustering
    logger.info("Computing clustering...")
    clustering_results = compute_clustering(G)
    logger.info("")
    
    # Compute curvature
    curvature_results = compute_curvature(G, alpha=alpha)
    logger.info("")
    
    # Combine results
    results = {
        'dataset': dataset_name,
        'timestamp': '2025-11-06',
        'network_stats': {
            'n_nodes': G.number_of_nodes(),
            'n_edges': G.number_of_edges(),
            'density': nx.density(G)
        },
        'clustering': clustering_results,
        'curvature': curvature_results
    }
    
    # Save
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / f'{dataset_name}_curvature_results.json'
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"✅ Results saved to: {output_file}")
    logger.info("")
    logger.info("="*70)
    logger.info(f"✅ {dataset_name.upper()} ANALYSIS COMPLETE")
    logger.info("="*70)
    logger.info(f"  κ = {curvature_results['kappa_mean']:.4f} ± {curvature_results['kappa_std']:.4f}")
    logger.info(f"  C = {clustering_results['clustering_weighted']:.4f}")
    logger.info("="*70)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', required=True, help='Dataset name')
    parser.add_argument('--edge-file', required=True, help='Path to edge CSV file')
    parser.add_argument('--output-dir', default='results/multi_dataset', help='Output directory')
    parser.add_argument('--alpha', type=float, default=0.5, help='OR curvature alpha parameter')
    
    args = parser.parse_args()
    
    main(args.dataset, args.edge_file, args.output_dir, args.alpha)

