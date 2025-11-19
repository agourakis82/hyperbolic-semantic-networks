#!/usr/bin/env python3
"""
CLUSTERING MODERATION VALIDATION
Validate that clustering moderates hyperbolic geometry across synthetic networks

Method: Generate synthetic networks with controlled clustering, measure correlation
Author: Final Validation
Date: 2025-11-05
"""

import json
import logging
import numpy as np
import networkx as nx
from pathlib import Path
from scipy import stats
from GraphRicciCurvature.OllivierRicci import OllivierRicci

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def compute_network_metrics(G: nx.Graph, alpha: float = 0.5) -> dict:
    """Compute clustering and curvature for a network"""
    
    # Clustering (weighted if weights present)
    clustering_dict = nx.clustering(G, weight='weight' if nx.is_weighted(G) else None)
    C = np.mean(list(clustering_dict.values()))
    
    # Curvature
    try:
        orc = OllivierRicci(G, alpha=alpha, weight='weight' if nx.is_weighted(G) else None, verbose='ERROR')
        orc.compute_ricci_curvature()
        curvatures = [d['ricciCurvature'] for u, v, d in orc.G.edges(data=True)]
        kappa = np.mean(curvatures)
        kappa_std = np.std(curvatures)
    except Exception as e:
        logger.warning(f"Curvature computation failed: {e}")
        kappa = None
        kappa_std = None
    
    return {
        'clustering': C,
        'kappa': kappa,
        'kappa_std': kappa_std,
        'n_nodes': G.number_of_nodes(),
        'n_edges': G.number_of_edges()
    }


def main():
    logger.info("="*70)
    logger.info("CLUSTERING MODERATION VALIDATION")
    logger.info("="*70)
    logger.info("")
    logger.info("Testing: Does clustering coefficient moderate hyperbolic geometry?")
    logger.info("Method: Synthetic networks with varying clustering")
    logger.info("")
    
    n = 500
    k = 6  # Target mean degree
    seed = 42
    
    results = []
    
    # 1. Erdős-Rényi (very low clustering)
    logger.info("1/9: Erdős-Rényi...")
    p = k / (n - 1)
    G_er = nx.erdos_renyi_graph(n, p, seed=seed)
    # Keep LCC
    if not nx.is_connected(G_er):
        lcc = max(nx.connected_components(G_er), key=len)
        G_er = G_er.subgraph(lcc).copy()
    metrics_er = compute_network_metrics(G_er)
    metrics_er['model'] = 'ER'
    results.append(metrics_er)
    logger.info(f"   ER: C={metrics_er['clustering']:.4f}, κ={metrics_er['kappa']:.4f}")
    
    # 2-6. Watts-Strogatz with varying rewiring probability (varying clustering)
    for i, p_rewire in enumerate([0.01, 0.05, 0.1, 0.3, 0.5], start=2):
        logger.info(f"{i}/9: Watts-Strogatz (p={p_rewire})...")
        G_ws = nx.watts_strogatz_graph(n, k, p_rewire, seed=seed+i)
        metrics_ws = compute_network_metrics(G_ws)
        metrics_ws['model'] = f'WS(p={p_rewire})'
        metrics_ws['p_rewire'] = p_rewire
        results.append(metrics_ws)
        logger.info(f"   WS(p={p_rewire}): C={metrics_ws['clustering']:.4f}, κ={metrics_ws['kappa']:.4f}")
    
    # 7. Barabási-Albert (scale-free, moderate clustering)
    logger.info("7/9: Barabási-Albert...")
    m = k // 2
    G_ba = nx.barabasi_albert_graph(n, m, seed=seed)
    metrics_ba = compute_network_metrics(G_ba)
    metrics_ba['model'] = 'BA'
    results.append(metrics_ba)
    logger.info(f"   BA: C={metrics_ba['clustering']:.4f}, κ={metrics_ba['kappa']:.4f}")
    
    # 8. Configuration model from real semantic network
    logger.info("8/9: Configuration model (from Spanish real)...")
    # Load Spanish real
    import pandas as pd
    df_edges = pd.read_csv('data/processed/spanish_edges_FINAL.csv')
    G_real_dir = nx.DiGraph()
    for _, row in df_edges.iterrows():
        G_real_dir.add_edge(row['source'], row['target'], weight=row['weight'])
    G_real = G_real_dir.to_undirected()
    
    # LCC
    if not nx.is_connected(G_real):
        lcc = max(nx.connected_components(G_real), key=len)
        G_real = G_real.subgraph(lcc).copy()
    
    # Generate config
    degrees = [d for n, d in G_real.degree()]
    G_config = nx.configuration_model(degrees, create_using=nx.Graph(), seed=seed)
    G_config = nx.Graph(G_config)
    G_config.remove_edges_from(nx.selfloop_edges(G_config))
    
    # Relabel
    mapping = dict(zip(G_config.nodes(), G_real.nodes()))
    G_config = nx.relabel_nodes(G_config, mapping)
    
    # Weights
    weights = [d['weight'] for u, v, d in G_real.edges(data=True)]
    for u, v in G_config.edges():
        G_config[u][v]['weight'] = np.random.choice(weights)
    
    # LCC
    if not nx.is_connected(G_config):
        lcc = max(nx.connected_components(G_config), key=len)
        G_config = G_config.subgraph(lcc).copy()
    
    metrics_config = compute_network_metrics(G_config)
    metrics_config['model'] = 'Config(Spanish)'
    results.append(metrics_config)
    logger.info(f"   Config: C={metrics_config['clustering']:.4f}, κ={metrics_config['kappa']:.4f}")
    
    # 9. Real Spanish network
    logger.info("9/9: Spanish Real...")
    metrics_real = compute_network_metrics(G_real)
    metrics_real['model'] = 'Real(Spanish)'
    results.append(metrics_real)
    logger.info(f"   Real: C={metrics_real['clustering']:.4f}, κ={metrics_real['kappa']:.4f}")
    
    # Statistical analysis
    logger.info("")
    logger.info("="*70)
    logger.info("STATISTICAL ANALYSIS")
    logger.info("="*70)
    logger.info("")
    
    # Extract C and κ
    C_values = [r['clustering'] for r in results if r['kappa'] is not None]
    kappa_values = [r['kappa'] for r in results if r['kappa'] is not None]
    
    # Pearson correlation
    r_pearson, p_pearson = stats.pearsonr(C_values, kappa_values)
    
    # Spearman correlation (robust)
    r_spearman, p_spearman = stats.spearmanr(C_values, kappa_values)
    
    # Linear regression
    from sklearn.linear_model import LinearRegression
    X = np.array(C_values).reshape(-1, 1)
    y = np.array(kappa_values)
    
    model = LinearRegression()
    model.fit(X, y)
    
    r2 = model.score(X, y)
    slope = model.coef_[0]
    intercept = model.intercept_
    
    logger.info("CORRELATION TESTS:")
    logger.info(f"  Pearson:  r={r_pearson:+.4f}, p={p_pearson:.6f} {'✅ SIGNIFICANT' if p_pearson < 0.05 else '(NS)'}")
    logger.info(f"  Spearman: ρ={r_spearman:+.4f}, p={p_spearman:.6f} {'✅ SIGNIFICANT' if p_spearman < 0.05 else '(NS)'}")
    logger.info("")
    logger.info("LINEAR REGRESSION:")
    logger.info(f"  κ = {intercept:.4f} + {slope:.4f}·C")
    logger.info(f"  R² = {r2:.4f}")
    logger.info("")
    
    # Effect size
    cohen_d = (np.max(kappa_values) - np.min(kappa_values)) / np.std(kappa_values)
    
    logger.info(f"EFFECT SIZE:")
    logger.info(f"  Cohen's d = {cohen_d:.4f} ({interpret_cohen_d(cohen_d)})")
    logger.info("")
    
    # Save
    output_data = {
        'test_performed': 'clustering_moderation_validation',
        'timestamp': '2025-11-05',
        'n_models': len(results),
        'models': results,
        'statistical_tests': {
            'pearson': {'r': float(r_pearson), 'p': float(p_pearson)},
            'spearman': {'rho': float(r_spearman), 'p': float(p_spearman)},
            'linear_regression': {
                'slope': float(slope),
                'intercept': float(intercept),
                'R2': float(r2)
            }
        },
        'effect_size': {
            'cohen_d': float(cohen_d),
            'interpretation': interpret_cohen_d(cohen_d)
        },
        'conclusion': 'Clustering significantly moderates hyperbolic geometry' if p_pearson < 0.05 else 'No significant relationship'
    }
    
    Path('results/final_validation').mkdir(parents=True, exist_ok=True)
    with open('results/final_validation/clustering_moderation_validation.json', 'w') as f:
        json.dump(output_data, f, indent=2)
    
    logger.info("✅ Results saved to: results/final_validation/clustering_moderation_validation.json")
    logger.info("")
    logger.info("="*70)
    logger.info("VALIDATION COMPLETE ✅")
    logger.info("="*70)


def interpret_cohen_d(d):
    """Interpret Cohen's d effect size"""
    abs_d = abs(d)
    if abs_d < 0.2:
        return "negligible"
    elif abs_d < 0.5:
        return "small"
    elif abs_d < 0.8:
        return "medium"
    else:
        return "large"


if __name__ == '__main__':
    main()

