#!/usr/bin/env python3
"""
RICCI FLOW REAL - Ollivier-Ricci Flow on Semantic Networks

Goal: Test if semantic networks are at Ricci flow equilibrium
Method: Full Ollivier-Ricci flow using GraphRicciCurvature library
Author: Darwin Cluster Analysis
Date: 2025-11-05
"""

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Tuple

import networkx as nx
import numpy as np
import pandas as pd
from GraphRicciCurvature.OllivierRicci import OllivierRicci

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_network(edge_file: Path) -> nx.Graph:
    """
    Load semantic network from edge file.
    
    Args:
        edge_file: Path to CSV file with source, target, weight columns
    
    Returns:
        NetworkX Graph (undirected, weighted, largest connected component)
    """
    logger.info(f"Loading network from {edge_file}")
    
    # Load edges
    df = pd.read_csv(edge_file)
    logger.info(f"Loaded {len(df)} edges")
    
    # Build directed graph first
    G_dir = nx.DiGraph()
    for _, row in df.iterrows():
        G_dir.add_edge(row['source'], row['target'], weight=row['weight'])
    
    logger.info(f"Built directed graph: {G_dir.number_of_nodes()} nodes, {G_dir.number_of_edges()} edges")
    
    # Convert to undirected (standard practice for Ricci curvature)
    G = G_dir.to_undirected()
    logger.info(f"Converted to undirected: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # Keep only largest connected component
    if not nx.is_connected(G):
        components = list(nx.connected_components(G))
        largest_cc = max(components, key=len)
        G = G.subgraph(largest_cc).copy()
        logger.info(f"Extracted LCC: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    return G


def compute_initial_metrics(G: nx.Graph) -> Dict:
    """
    Compute network-level metrics before Ricci flow.
    
    Args:
        G: NetworkX graph
    
    Returns:
        Dictionary with metrics
    """
    logger.info("Computing initial metrics...")
    
    # Clustering coefficient
    clustering_dict = nx.clustering(G, weight='weight')
    C = np.mean(list(clustering_dict.values()))
    
    # Density
    n = G.number_of_nodes()
    m = G.number_of_edges()
    density = 2 * m / (n * (n - 1)) if n > 1 else 0
    
    # Average degree
    degrees = [d for n, d in G.degree()]
    avg_degree = np.mean(degrees)
    
    # Ollivier-Ricci curvature (network-level average)
    try:
        orc = OllivierRicci(G, alpha=0.5, weight='weight', verbose='INFO')
        orc.compute_ricci_curvature()
        
        curvatures = [d['ricciCurvature'] for u, v, d in orc.G.edges(data=True)]
        kappa = np.mean(curvatures)
        kappa_std = np.std(curvatures)
        
        logger.info(f"Ollivier-Ricci curvature computed: κ = {kappa:.4f} ± {kappa_std:.4f}")
    except Exception as e:
        logger.error(f"Curvature computation failed: {e}")
        kappa = None
        kappa_std = None
    
    metrics = {
        'n_nodes': n,
        'n_edges': m,
        'density': density,
        'clustering': C,
        'avg_degree': avg_degree,
        'kappa': kappa,
        'kappa_std': kappa_std
    }
    
    logger.info(f"Initial metrics: C={C:.4f}, κ={kappa:.4f}, density={density:.6f}")
    
    return metrics


def run_ricci_flow(G: nx.Graph, iterations: int = 200, step: float = 0.5, 
                   alpha: float = 0.5) -> Tuple[nx.Graph, List[Dict]]:
    """
    Run REAL Ollivier-Ricci flow on network.
    
    This is the actual Ricci flow implementation from GraphRicciCurvature,
    NOT a simplified version!
    
    Args:
        G: Input graph
        iterations: Number of flow iterations
        step: Flow step size (η parameter)
        alpha: Idleness parameter for Ollivier-Ricci
    
    Returns:
        Tuple of (evolved graph, trajectory of metrics)
    """
    logger.info("="*70)
    logger.info("STARTING RICCI FLOW")
    logger.info("="*70)
    logger.info(f"Parameters: iterations={iterations}, step={step}, α={alpha}")
    logger.info("")
    
    # Initialize Ollivier-Ricci
    orc = OllivierRicci(G, alpha=alpha, weight='weight', verbose='INFO')
    
    # Compute initial curvature
    logger.info("Computing initial curvature...")
    orc.compute_ricci_curvature()
    
    # Track trajectory
    trajectory = []
    
    # Initial metrics
    metrics_0 = compute_network_metrics(orc.G, step=0)
    trajectory.append(metrics_0)
    logger.info(f"Step 0: C={metrics_0['clustering']:.4f}, κ={metrics_0['kappa']:.4f}")
    
    # Run Ricci flow
    logger.info("")
    logger.info("Running Ricci flow...")
    logger.info("")
    
    start_time = time.time()
    
    for i in range(1, iterations + 1):
        # Perform one step of Ricci flow
        # This modifies edge weights according to: w(e) ← w(e) + step * κ(e)
        orc.compute_ricci_flow(iterations=1, step=step)
        
        # Compute metrics at this step
        metrics_i = compute_network_metrics(orc.G, step=i)
        trajectory.append(metrics_i)
        
        # Log progress every 10 steps
        if i % 10 == 0 or i == iterations:
            elapsed = time.time() - start_time
            logger.info(f"Step {i}/{iterations}: C={metrics_i['clustering']:.4f}, κ={metrics_i['kappa']:.4f} | {elapsed/i:.2f}s/step")
        
        # Check convergence
        if i > 10:
            delta_C = abs(trajectory[-1]['clustering'] - trajectory[-2]['clustering'])
            delta_kappa = abs(trajectory[-1]['kappa'] - trajectory[-2]['kappa'])
            
            if delta_C < 0.0001 and delta_kappa < 0.001:
                logger.info(f"CONVERGED at step {i}: ΔC={delta_C:.6f}, Δκ={delta_kappa:.6f}")
                break
    
    total_time = time.time() - start_time
    logger.info("")
    logger.info(f"Ricci flow completed in {total_time:.2f}s ({total_time/len(trajectory):.2f}s/step)")
    
    return orc.G, trajectory


def compute_network_metrics(G: nx.Graph, step: int) -> Dict:
    """
    Compute network-level metrics at a given flow step.
    
    Args:
        G: NetworkX graph
        step: Current iteration number
    
    Returns:
        Dictionary with metrics
    """
    # Clustering
    clustering_dict = nx.clustering(G, weight='weight')
    C = np.mean(list(clustering_dict.values()))
    
    # Density
    n = G.number_of_nodes()
    m = G.number_of_edges()
    density = 2 * m / (n * (n - 1)) if n > 1 else 0
    
    # Curvature (from edge attributes)
    curvatures = []
    for u, v, d in G.edges(data=True):
        if 'ricciCurvature' in d:
            curvatures.append(d['ricciCurvature'])
    
    kappa = np.mean(curvatures) if curvatures else 0.0
    kappa_std = np.std(curvatures) if curvatures else 0.0
    
    return {
        'step': step,
        'n_nodes': n,
        'n_edges': m,
        'density': density,
        'clustering': C,
        'kappa': kappa,
        'kappa_std': kappa_std,
        'timestamp': time.time()
    }


def generate_configuration_null(G: nx.Graph, alpha: float = 0.5, seed: int = 42) -> nx.Graph:
    """
    Generate configuration model null preserving degree sequence.
    
    Args:
        G: Input graph (undirected)
        alpha: Idleness parameter
        seed: Random seed
    
    Returns:
        Configuration model null (undirected, weighted)
    """
    logger.info("Generating configuration model null...")
    
    np.random.seed(seed)
    
    # Get degree sequence
    degrees = [d for n, d in G.degree()]
    
    # Create configuration model
    G_null = nx.configuration_model(degrees, create_using=nx.Graph(), seed=seed)
    
    # Remove self-loops and parallel edges
    G_null = nx.Graph(G_null)
    G_null.remove_edges_from(nx.selfloop_edges(G_null))
    
    # Relabel nodes to match original
    mapping = dict(zip(G_null.nodes(), G.nodes()))
    G_null = nx.relabel_nodes(G_null, mapping)
    
    # Assign random weights from original distribution
    weights = [d['weight'] for u, v, d in G.edges(data=True)]
    for u, v in G_null.edges():
        G_null[u][v]['weight'] = np.random.choice(weights)
    
    # Keep only largest connected component
    if not nx.is_connected(G_null):
        components = list(nx.connected_components(G_null))
        largest_cc = max(components, key=len)
        G_null = G_null.subgraph(largest_cc).copy()
    
    logger.info(f"Config null: {G_null.number_of_nodes()} nodes, {G_null.number_of_edges()} edges")
    
    return G_null


def save_results(language: str, network_type: str, initial_metrics: Dict, 
                final_metrics: Dict, trajectory: List[Dict], output_dir: Path):
    """Save Ricci flow results to JSON."""
    
    results = {
        'language': language,
        'network_type': network_type,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'parameters': {
            'iterations': len(trajectory),
            'alpha': 0.5,
            'step': 0.5
        },
        'initial_metrics': initial_metrics,
        'final_metrics': final_metrics,
        'deltas': {
            'delta_C': final_metrics['clustering'] - initial_metrics['clustering'],
            'delta_kappa': final_metrics['kappa'] - initial_metrics['kappa'],
            'delta_density': final_metrics['density'] - initial_metrics['density']
        },
        'trajectory': trajectory,
        'convergence': {
            'converged': len(trajectory) < 200,
            'steps_to_convergence': len(trajectory)
        }
    }
    
    # Save
    output_file = output_dir / f'ricci_flow_{language}_{network_type}.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to: {output_file}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Run Ricci flow on semantic networks')
    parser.add_argument('--language', required=True, choices=['spanish', 'english', 'chinese'],
                       help='Language to analyze')
    parser.add_argument('--network-type', required=True, choices=['real', 'config'],
                       help='Network type (real or configuration null)')
    parser.add_argument('--edge-file', required=True, type=Path,
                       help='Path to edge file')
    parser.add_argument('--output-dir', required=True, type=Path,
                       help='Output directory for results')
    parser.add_argument('--iterations', type=int, default=200,
                       help='Maximum Ricci flow iterations')
    parser.add_argument('--step', type=float, default=0.5,
                       help='Ricci flow step size (η)')
    parser.add_argument('--alpha', type=float, default=0.5,
                       help='Idleness parameter (α)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed (for config null generation)')
    
    args = parser.parse_args()
    
    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("="*70)
    logger.info("RICCI FLOW ANALYSIS - REAL IMPLEMENTATION")
    logger.info("="*70)
    logger.info(f"Language:     {args.language}")
    logger.info(f"Network type: {args.network_type}")
    logger.info(f"Edge file:    {args.edge_file}")
    logger.info(f"Output dir:   {args.output_dir}")
    logger.info(f"Parameters:   iterations={args.iterations}, step={args.step}, α={args.alpha}")
    logger.info("="*70)
    logger.info("")
    
    # Load network
    G_real = load_network(args.edge_file)
    
    # Generate config null if requested
    if args.network_type == 'config':
        logger.info("")
        logger.info("Generating configuration model null...")
        G = generate_configuration_null(G_real, alpha=args.alpha, seed=args.seed)
    else:
        G = G_real
    
    logger.info("")
    logger.info("="*70)
    logger.info("COMPUTING INITIAL METRICS")
    logger.info("="*70)
    logger.info("")
    
    # Compute initial metrics
    initial_metrics = compute_initial_metrics(G)
    
    logger.info("")
    logger.info("Initial network state:")
    logger.info(f"  Nodes:      {initial_metrics['n_nodes']}")
    logger.info(f"  Edges:      {initial_metrics['n_edges']}")
    logger.info(f"  Clustering: {initial_metrics['clustering']:.4f}")
    logger.info(f"  Curvature:  {initial_metrics['kappa']:.4f} ± {initial_metrics['kappa_std']:.4f}")
    logger.info(f"  Density:    {initial_metrics['density']:.6f}")
    logger.info("")
    
    # Run Ricci flow
    logger.info("="*70)
    logger.info("RUNNING RICCI FLOW (This may take several hours!)")
    logger.info("="*70)
    logger.info("")
    
    G_evolved, trajectory = run_ricci_flow(
        G, 
        iterations=args.iterations,
        step=args.step,
        alpha=args.alpha
    )
    
    # Compute final metrics
    logger.info("")
    logger.info("="*70)
    logger.info("COMPUTING FINAL METRICS")
    logger.info("="*70)
    logger.info("")
    
    final_metrics = trajectory[-1]
    
    logger.info("")
    logger.info("Final network state:")
    logger.info(f"  Clustering: {final_metrics['clustering']:.4f}")
    logger.info(f"  Curvature:  {final_metrics['kappa']:.4f} ± {final_metrics['kappa_std']:.4f}")
    logger.info(f"  Density:    {final_metrics['density']:.6f}")
    logger.info("")
    
    # Calculate deltas
    delta_C = final_metrics['clustering'] - initial_metrics['clustering']
    delta_kappa = final_metrics['kappa'] - initial_metrics['kappa']
    delta_density = final_metrics['density'] - initial_metrics['density']
    
    logger.info("="*70)
    logger.info("CHANGES (Δ)")
    logger.info("="*70)
    logger.info(f"  ΔC:       {delta_C:+.4f} ({abs(delta_C)/initial_metrics['clustering']*100:.1f}% change)")
    logger.info(f"  Δκ:       {delta_kappa:+.4f} ({abs(delta_kappa)/abs(initial_metrics['kappa'])*100:.1f}% change)")
    logger.info(f"  Δdensity: {delta_density:+.6f}")
    logger.info("")
    
    # Equilibrium test
    equilibrium_threshold_C = 0.02
    equilibrium_threshold_kappa = 0.05
    
    is_equilibrium = (abs(delta_C) < equilibrium_threshold_C and 
                     abs(delta_kappa) < equilibrium_threshold_kappa)
    
    logger.info("="*70)
    logger.info("EQUILIBRIUM TEST")
    logger.info("="*70)
    logger.info(f"  Thresholds: |ΔC| < {equilibrium_threshold_C}, |Δκ| < {equilibrium_threshold_kappa}")
    logger.info(f"  Observed:   |ΔC| = {abs(delta_C):.4f}, |Δκ| = {abs(delta_kappa):.4f}")
    logger.info("")
    
    if is_equilibrium:
        logger.info("  ✅ NETWORK IS AT RICCI FLOW EQUILIBRIUM!")
        verdict = "equilibrium"
    elif abs(delta_C) < 2*equilibrium_threshold_C and abs(delta_kappa) < 2*equilibrium_threshold_kappa:
        logger.info("  ✓ Network is NEAR equilibrium")
        verdict = "near_equilibrium"
    else:
        logger.info("  ✗ Network is FAR from equilibrium")
        verdict = "far_from_equilibrium"
    
    logger.info("")
    
    # Save results
    logger.info("="*70)
    logger.info("SAVING RESULTS")
    logger.info("="*70)
    logger.info("")
    
    results = save_results(
        args.language,
        args.network_type,
        initial_metrics,
        final_metrics,
        trajectory,
        args.output_dir
    )
    
    logger.info("")
    logger.info("="*70)
    logger.info("ANALYSIS COMPLETE ✅")
    logger.info("="*70)
    logger.info(f"Language:    {args.language}")
    logger.info(f"Type:        {args.network_type}")
    logger.info(f"Verdict:     {verdict}")
    logger.info(f"Steps:       {len(trajectory)}")
    logger.info("="*70)
    
    return results


if __name__ == '__main__':
    main()

