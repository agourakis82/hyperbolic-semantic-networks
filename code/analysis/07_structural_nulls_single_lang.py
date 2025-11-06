#!/usr/bin/env python3
"""
Structural Null Models - Single Language Version (for parallel processing)
Generates configuration and triadic-rewire nulls for ONE language.
"""

import sys
import json
import logging
import argparse
from pathlib import Path
import numpy as np
import networkx as nx
from tqdm import tqdm
from scipy.stats import percentileofscore

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_real_network(edge_file):
    """Load real semantic network from preprocessed edges."""
    G = nx.DiGraph()
    
    with open(edge_file, 'r') as f:
        next(f)  # Skip header
        for line in f:
            source, target, weight = line.strip().split(',')
            G.add_edge(source, target, weight=float(weight))
    
    logger.info(f"Loaded {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G  # Return DIRECTED for null generation


def generate_configuration_null(G, alpha=0.5):
    """
    Generate configuration model null preserving degree sequence.
    CRITICAL FIX: If G is directed, convert to undirected FIRST,
    then generate undirected configuration model.
    This ensures null has same edge density as real network.
    """
    try:
        # Convert to undirected if directed
        if G.is_directed():
            G_work = G.to_undirected()
        else:
            G_work = G
        
        # Get degree sequence from UNDIRECTED graph
        degrees = [d for n, d in G_work.degree()]
        
        # Create UNDIRECTED configuration model
        G_null = nx.configuration_model(degrees, create_using=nx.Graph())
        
        # Remove self-loops and parallel edges
        G_null = nx.Graph(G_null)
        G_null.remove_edges_from(nx.selfloop_edges(G_null))
        
        # Relabel nodes to match original
        mapping = dict(zip(G_null.nodes(), G_work.nodes()))
        G_null = nx.relabel_nodes(G_null, mapping)
        
        # Assign random weights from original distribution
        weights = [d['weight'] for _, _, d in G_work.edges(data=True)]
        for u, v in G_null.edges():
            G_null[u][v]['weight'] = np.random.choice(weights)
        
        return G_null
    except Exception as e:
        logger.warning(f"Configuration null failed: {e}")
        return None


def generate_triadic_null(G, n_swaps=None, max_tries_per_swap=100, alpha=0.5):
    """
    Generate triadic-rewire null preserving triangle distribution.
    Uses double-edge swap with triangle-preserving constraint.
    """
    try:
        G_null = G.copy()
        
        if n_swaps is None:
            n_swaps = G.number_of_edges()  # Fix: reduced from * 10
        
        successful_swaps = 0
        for _ in range(n_swaps):
            for _ in range(max_tries_per_swap):
                # Sample two edges
                edges = list(G_null.edges())
                if len(edges) < 2:
                    break
                    
                edge1, edge2 = np.random.choice(len(edges), size=2, replace=False)
                u1, v1 = edges[edge1]
                u2, v2 = edges[edge2]
                
                # Check if swap is valid (no self-loops, no duplicates)
                if u1 == u2 or v1 == v2 or u1 == v2 or u2 == v1:
                    continue
                if G_null.has_edge(u1, v2) or G_null.has_edge(u2, v1):
                    continue
                
                # Count triangles before swap
                # Fix: Cache undirected graph to avoid repeated conversions
                G_undir = G_null.to_undirected()
                triangles_before = (
                    nx.triangles(G_undir, u1) +
                    nx.triangles(G_undir, v1) +
                    nx.triangles(G_undir, u2) +
                    nx.triangles(G_undir, v2)
                )
                
                # Perform swap
                w1 = G_null[u1][v1]['weight']
                w2 = G_null[u2][v2]['weight']
                
                G_null.remove_edge(u1, v1)
                G_null.remove_edge(u2, v2)
                G_null.add_edge(u1, v2, weight=w1)
                G_null.add_edge(u2, v1, weight=w2)
                
                # Count triangles after swap
                # Fix: Update undirected graph after swap
                G_undir = G_null.to_undirected()
                triangles_after = (
                    nx.triangles(G_undir, u1) +
                    nx.triangles(G_undir, v2) +
                    nx.triangles(G_undir, u2) +
                    nx.triangles(G_undir, v1)
                )
                
                # Accept swap if triangle count preserved or improved
                if abs(triangles_after - triangles_before) <= 2:
                    successful_swaps += 1
                    break
                else:
                    # Revert swap
                    G_null.remove_edge(u1, v2)
                    G_null.remove_edge(u2, v1)
                    G_null.add_edge(u1, v1, weight=w1)
                    G_null.add_edge(u2, v2, weight=w2)
        
        logger.debug(f"Successful swaps: {successful_swaps}/{n_swaps}")
        return G_null
        
    except Exception as e:
        logger.warning(f"Triadic null failed: {e}")
        return None


def compute_or_curvature(G, alpha=0.5, weight='weight'):
    """
    Compute network-level Ollivier-Ricci curvature.
    Returns mean curvature across all edges.
    Converts to UNDIRECTED before computation (standard practice).
    """
    try:
        from GraphRicciCurvature.OllivierRicci import OllivierRicci
        
        # Convert to undirected for curvature (standard practice)
        if G.is_directed():
            G_compute = G.to_undirected()
        else:
            G_compute = G
        
        orc = OllivierRicci(G_compute, alpha=alpha, weight=weight, verbose="ERROR")
        orc.compute_ricci_curvature()
        
        curvatures = [d['ricciCurvature'] for _, _, d in orc.G.edges(data=True)]
        return np.mean(curvatures)
    except Exception as e:
        logger.error(f"Curvature computation failed: {e}")
        return None


def monte_carlo_test(real_value, null_distribution):
    """Compute Monte Carlo p-value (two-tailed)."""
    n_nulls = len(null_distribution)
    n_extreme = np.sum(np.abs(null_distribution) >= np.abs(real_value))
    p_value = (n_extreme + 1) / (n_nulls + 1)  # +1 for continuity correction
    return p_value


def cliffs_delta(real_value, null_distribution):
    """
    Compute Cliff's Delta effect size.
    δ = (# pairs where null > real - # pairs where null < real) / (n_pairs)
    """
    null_array = np.array(null_distribution)
    n_greater = np.sum(null_array > real_value)
    n_less = np.sum(null_array < real_value)
    n_total = len(null_array)
    
    delta = (n_greater - n_less) / n_total
    return delta


def run_null_analysis(language, edge_file, null_type, M=1000, alpha=0.5, seed=123, output_dir=None):
    """
    Run null model analysis for a single language and null type.
    
    Parameters:
    -----------
    language : str
        Language code (e.g., 'english', 'spanish')
    edge_file : str
        Path to edge list CSV
    null_type : str
        'configuration' or 'triadic'
    M : int
        Number of null replicates
    alpha : float
        Idleness parameter for OR curvature
    seed : int
        Random seed
    output_dir : str
        Output directory for results
    """
    np.random.seed(seed)
    
    logger.info(f"{'='*60}")
    logger.info(f"Starting: {language} - {null_type}")
    logger.info(f"{'='*60}")
    
    # Load real network
    G_real = load_real_network(edge_file)
    
    # Compute real curvature
    logger.info(f"Computing real curvature...")
    kappa_real = compute_or_curvature(G_real, alpha=alpha)
    if kappa_real is None:
        logger.error(f"Failed to compute real curvature for {language}")
        return None
    
    logger.info(f"Real κ = {kappa_real:.4f}")
    
    # Generate nulls
    logger.info(f"Starting null generation (M={M})...")
    kappa_nulls = []
    
    null_func = generate_configuration_null if null_type == 'configuration' else generate_triadic_null
    
    pbar = tqdm(total=M, desc=f"{language}-{null_type}")
    valid_nulls = 0
    
    while valid_nulls < M:
        G_null = null_func(G_real, alpha=alpha)
        
        if G_null is not None:
            kappa_null = compute_or_curvature(G_null, alpha=alpha)
            
            if kappa_null is not None:
                kappa_nulls.append(kappa_null)
                valid_nulls += 1
                pbar.update(1)
    
    pbar.close()
    
    logger.info(f"Generated {valid_nulls}/{M} valid nulls")
    
    # Compute statistics
    delta_kappa = kappa_real - np.mean(kappa_nulls)
    p_mc = monte_carlo_test(kappa_real, kappa_nulls)
    cliff_delta = cliffs_delta(kappa_real, kappa_nulls)
    ci_lower, ci_upper = np.percentile(kappa_nulls, [2.5, 97.5])
    
    results = {
        'language': language,
        'null_type': null_type,
        'M': M,
        'alpha': alpha,
        'kappa_real': float(kappa_real),
        'kappa_null_mean': float(np.mean(kappa_nulls)),
        'kappa_null_std': float(np.std(kappa_nulls)),
        'delta_kappa': float(delta_kappa),
        'p_MC': float(p_mc),
        'cliff_delta': float(cliff_delta),
        'ci_95_lower': float(ci_lower),
        'ci_95_upper': float(ci_upper),
        'kappa_nulls': [float(k) for k in kappa_nulls]
    }
    
    # Print results
    logger.info(f"{null_type} RESULTS:")
    logger.info(f"  Δκ = {delta_kappa:.4f}")
    logger.info(f"  p_MC = {p_mc:.4f}")
    logger.info(f"  Cliff's δ = {cliff_delta:.4f}")
    
    # Save results
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{language}_{null_type}_nulls.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Saved: {output_file}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Run structural null analysis for a single language')
    parser.add_argument('--language', required=True, help='Language code (english, spanish, dutch, chinese)')
    parser.add_argument('--null-type', required=True, choices=['configuration', 'triadic'], help='Null model type')
    parser.add_argument('--edge-file', required=True, help='Path to edge list CSV')
    parser.add_argument('--output-dir', required=True, help='Output directory')
    parser.add_argument('--M', type=int, default=1000, help='Number of replicates')
    parser.add_argument('--alpha', type=float, default=0.5, help='Idleness parameter')
    parser.add_argument('--seed', type=int, default=123, help='Random seed')
    
    args = parser.parse_args()
    
    # Run analysis
    results = run_null_analysis(
        language=args.language,
        edge_file=args.edge_file,
        null_type=args.null_type,
        M=args.M,
        alpha=args.alpha,
        seed=args.seed,
        output_dir=args.output_dir
    )
    
    if results:
        logger.info("✅ Analysis completed successfully!")
        return 0
    else:
        logger.error("❌ Analysis failed!")
        return 1


if __name__ == '__main__':
    sys.exit(main())



