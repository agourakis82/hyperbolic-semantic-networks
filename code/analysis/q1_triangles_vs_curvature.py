#!/usr/bin/env python3
"""
Q1 TEST 2.1: TRIANGLES VS CURVATURE ANALYSIS
Critical test from Q1 reviewer

Goal: Quantify relationship between triangles and Ollivier-Ricci curvature
Method: Per-edge regression + distribution tests
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
from scipy import stats
from GraphRicciCurvature.OllivierRicci import OllivierRicci
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def count_edge_triangles(G: nx.Graph, u, v) -> int:
    """Count triangles containing edge (u,v)"""
    return len(list(nx.common_neighbors(G, u, v)))


def compute_edge_metrics(G: nx.Graph, alpha: float = 0.5) -> pd.DataFrame:
    """
    Compute per-edge metrics: triangles, curvature, degrees, betweenness
    
    Args:
        G: NetworkX graph (undirected)
        alpha: Idleness parameter for Ollivier-Ricci
    
    Returns:
        DataFrame with edge-level metrics
    """
    logger.info("Computing Ollivier-Ricci curvature...")
    orc = OllivierRicci(G, alpha=alpha, weight='weight', verbose='INFO')
    orc.compute_ricci_curvature()
    
    logger.info("Computing edge metrics...")
    
    # Edge betweenness
    logger.info("Computing edge betweenness...")
    edge_betweenness = nx.edge_betweenness_centrality(G, weight='weight')
    
    # Collect metrics per edge
    edge_data = []
    
    for u, v, data in orc.G.edges(data=True):
        # Triangle count
        n_triangles = count_edge_triangles(G, u, v)
        
        # Degrees
        deg_u = G.degree(u)
        deg_v = G.degree(v)
        deg_min = min(deg_u, deg_v)
        deg_max = max(deg_u, deg_v)
        
        # Curvature
        kappa = data.get('ricciCurvature', 0.0)
        
        # Betweenness
        betw = edge_betweenness.get((u, v), edge_betweenness.get((v, u), 0.0))
        
        # Weight
        weight = data.get('weight', 1.0)
        
        edge_data.append({
            'edge': f"{u}--{v}",
            'n_triangles': n_triangles,
            'has_triangle': int(n_triangles > 0),
            'kappa': kappa,
            'deg_min': deg_min,
            'deg_max': deg_max,
            'betweenness': betw,
            'weight': weight
        })
    
    df = pd.DataFrame(edge_data)
    
    logger.info(f"Computed metrics for {len(df)} edges")
    logger.info(f"Edges with triangles: {df['has_triangle'].sum()} ({df['has_triangle'].mean()*100:.1f}%)")
    logger.info(f"Curvature range: [{df['kappa'].min():.3f}, {df['kappa'].max():.3f}]")
    
    return df


def test_triangles_curvature_relationship(df: pd.DataFrame) -> dict:
    """
    Test relationship between triangles and curvature
    
    Tests:
    1. Logistic regression: P(has_triangle) ~ κ + controls
    2. Distribution test: κ | T>0 vs κ | T=0
    3. Correlation: n_triangles vs κ
    
    Returns:
        Dictionary with test results
    """
    logger.info("")
    logger.info("="*70)
    logger.info("TEST 1: Logistic Regression - P(has_triangle) ~ κ + controls")
    logger.info("="*70)
    
    # Prepare features
    X = df[['kappa', 'deg_min', 'deg_max', 'betweenness']].values
    y = df['has_triangle'].values
    
    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Logistic regression
    model = LogisticRegression(max_iter=1000)
    model.fit(X_scaled, y)
    
    # Coefficients
    coef_kappa = model.coef_[0][0]
    coef_deg_min = model.coef_[0][1]
    coef_deg_max = model.coef_[0][2]
    coef_betw = model.coef_[0][3]
    
    # Accuracy
    y_pred = model.predict(X_scaled)
    accuracy = (y_pred == y).mean()
    
    logger.info(f"Coefficients (standardized):")
    logger.info(f"  κ:          {coef_kappa:+.4f} {'(+triangles if >0)' if coef_kappa > 0 else '(-triangles if <0)'}")
    logger.info(f"  deg_min:    {coef_deg_min:+.4f}")
    logger.info(f"  deg_max:    {coef_deg_max:+.4f}")
    logger.info(f"  betweenness:{coef_betw:+.4f}")
    logger.info(f"Accuracy: {accuracy:.3f}")
    
    logger.info("")
    logger.info("="*70)
    logger.info("TEST 2: Distribution Test - κ | T>0 vs κ | T=0")
    logger.info("="*70)
    
    # Split by triangle presence
    kappa_with_triangles = df[df['has_triangle'] == 1]['kappa'].values
    kappa_no_triangles = df[df['has_triangle'] == 0]['kappa'].values
    
    # Kolmogorov-Smirnov test
    ks_stat, ks_pvalue = stats.ks_2samp(kappa_with_triangles, kappa_no_triangles)
    
    # Means
    mean_with = np.mean(kappa_with_triangles)
    mean_without = np.mean(kappa_no_triangles)
    
    # Wilcoxon (Mann-Whitney U)
    u_stat, u_pvalue = stats.mannwhitneyu(kappa_with_triangles, kappa_no_triangles, alternative='two-sided')
    
    logger.info(f"κ | T>0:  mean={mean_with:.4f}, n={len(kappa_with_triangles)}")
    logger.info(f"κ | T=0:  mean={mean_without:.4f}, n={len(kappa_no_triangles)}")
    logger.info(f"Difference: {mean_with - mean_without:+.4f}")
    logger.info(f"")
    logger.info(f"KS test:  D={ks_stat:.4f}, p={ks_pvalue:.4f} {'✅ SIGNIFICANT' if ks_pvalue < 0.05 else '(NS)'}")
    logger.info(f"Mann-Whitney U: U={u_stat:.0f}, p={u_pvalue:.4f} {'✅' if u_pvalue < 0.05 else '(NS)'}")
    
    logger.info("")
    logger.info("="*70)
    logger.info("TEST 3: Correlation - n_triangles vs κ")
    logger.info("="*70)
    
    # Pearson correlation
    r_pearson, p_pearson = stats.pearsonr(df['n_triangles'], df['kappa'])
    
    # Spearman correlation (robust to outliers)
    r_spearman, p_spearman = stats.spearmanr(df['n_triangles'], df['kappa'])
    
    logger.info(f"Pearson:  r={r_pearson:+.4f}, p={p_pearson:.4f} {'✅' if p_pearson < 0.05 else '(NS)'}")
    logger.info(f"Spearman: ρ={r_spearman:+.4f}, p={p_spearman:.4f} {'✅' if p_spearman < 0.05 else '(NS)'}")
    
    # Results summary
    results = {
        'logistic_regression': {
            'coef_kappa': float(coef_kappa),
            'coef_deg_min': float(coef_deg_min),
            'coef_deg_max': float(coef_deg_max),
            'coef_betweenness': float(coef_betw),
            'accuracy': float(accuracy)
        },
        'distribution_test': {
            'mean_with_triangles': float(mean_with),
            'mean_without_triangles': float(mean_without),
            'difference': float(mean_with - mean_without),
            'ks_statistic': float(ks_stat),
            'ks_pvalue': float(ks_pvalue),
            'mann_whitney_u': float(u_stat),
            'mann_whitney_p': float(u_pvalue)
        },
        'correlation': {
            'pearson_r': float(r_pearson),
            'pearson_p': float(p_pearson),
            'spearman_rho': float(r_spearman),
            'spearman_p': float(p_spearman)
        }
    }
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Test triangles vs curvature relationship')
    parser.add_argument('--language', required=True, choices=['spanish', 'english', 'chinese'])
    parser.add_argument('--edge-file', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--alpha', type=float, default=0.5)
    
    args = parser.parse_args()
    
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("="*70)
    logger.info("Q1 TEST 2.1: TRIANGLES VS CURVATURE")
    logger.info("="*70)
    logger.info(f"Language: {args.language}")
    logger.info(f"Edge file: {args.edge_file}")
    logger.info(f"Alpha: {args.alpha}")
    logger.info("")
    
    # Load network
    logger.info("Loading network...")
    df_edges = pd.read_csv(args.edge_file)
    
    G_dir = nx.DiGraph()
    for _, row in df_edges.iterrows():
        G_dir.add_edge(row['source'], row['target'], weight=row['weight'])
    
    # Convert to undirected
    G = G_dir.to_undirected()
    
    # Keep LCC
    if not nx.is_connected(G):
        components = list(nx.connected_components(G))
        largest_cc = max(components, key=len)
        G = G.subgraph(largest_cc).copy()
    
    logger.info(f"Network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    logger.info("")
    
    # Compute edge metrics
    df_metrics = compute_edge_metrics(G, alpha=args.alpha)
    
    # Test relationship
    test_results = test_triangles_curvature_relationship(df_metrics)
    
    # Save detailed data
    df_metrics.to_csv(args.output_dir / f'edge_metrics_{args.language}.csv', index=False)
    logger.info(f"Edge metrics saved to: {args.output_dir / f'edge_metrics_{args.language}.csv'}")
    
    # Save test results
    results = {
        'language': args.language,
        'alpha': args.alpha,
        'n_edges': len(df_metrics),
        'n_edges_with_triangles': int(df_metrics['has_triangle'].sum()),
        'pct_edges_with_triangles': float(df_metrics['has_triangle'].mean() * 100),
        'tests': test_results
    }
    
    output_file = args.output_dir / f'triangles_curvature_{args.language}.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to: {output_file}")
    logger.info("")
    logger.info("="*70)
    logger.info("ANALYSIS COMPLETE ✅")
    logger.info("="*70)
    
    # Key finding
    if test_results['logistic_regression']['coef_kappa'] > 0:
        logger.info("🔑 KEY FINDING: Higher κ → MORE likely to have triangles (canonical)")
    else:
        logger.info("🔥 ANOMALY: Higher κ → LESS likely to have triangles (unexpected!)")
    
    if test_results['distribution_test']['mann_whitney_p'] < 0.05:
        if test_results['distribution_test']['difference'] > 0:
            logger.info("✅ Edges with triangles have HIGHER κ (expected)")
        else:
            logger.info("⚠️  Edges with triangles have LOWER κ (semantic network anomaly!)")
    
    return results


if __name__ == '__main__':
    main()

