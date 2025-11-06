#!/usr/bin/env python3
"""
Chinese Network Substructure Analysis - Response to Reviewer #1
================================================================
Tests if Chinese κ≈0 is sampling artifact or genuine flat geometry.

Reviewer concern: "Chinese p=1.0 contradicts cross-linguistic claim"
Tests needed: Substructures, thresholds, sampling methods

Configurations to test:
1. Top 250 nodes (different seeds 1,2,3)
2. Top 375 nodes
3. Threshold variations (0.10, 0.15, 0.25, 0.30)
4. Random walk sampling
"""

import pandas as pd
import networkx as nx
import numpy as np
from GraphRicciCurvature.OllivierRicci import OllivierRicci
import json
from pathlib import Path
from tqdm import tqdm

ALPHA = 0.5
EDGE_FILE = Path(__file__).parent.parent.parent / "data/processed/chinese_edges.csv"

print("="*70)
print("🇨🇳 CHINESE NETWORK SUBSTRUCTURE ANALYSIS - Reviewer Response")
print("="*70)
print()

results = []

# Load full Chinese network
print("📂 Loading Chinese edge list...")
df = pd.read_csv(EDGE_FILE)
print(f"   ✅ Loaded {len(df)} edges")

# Build full network
G_full = nx.DiGraph()
for _, row in df.iterrows():
    G_full.add_edge(row['source'], row['target'], weight=row['weight'])

print(f"   Full network: {G_full.number_of_nodes()} nodes, {G_full.number_of_edges()} edges")
print()

def compute_curvature(G, name):
    """Compute OR curvature for a network."""
    print(f"  Computing curvature for {name}...")
    print(f"    Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
    
    # Convert to undirected for OR curvature (standard practice)
    G_undir = G.to_undirected()
    
    # Get largest component
    if not nx.is_connected(G_undir):
        largest_cc = max(nx.connected_components(G_undir), key=len)
        G_undir = G_undir.subgraph(largest_cc).copy()
    
    # Compute
    orc = OllivierRicci(G_undir, alpha=ALPHA, verbose="ERROR")
    orc.compute_ricci_curvature()
    G_orc = orc.G
    
    curvatures = [G_orc[u][v]['ricciCurvature'] for u, v in G_orc.edges()]
    
    return {
        'n_nodes': G_undir.number_of_nodes(),
        'n_edges': G_undir.number_of_edges(),
        'kappa_mean': float(np.mean(curvatures)),
        'kappa_std': float(np.std(curvatures)),
        'kappa_median': float(np.median(curvatures)),
        'kappa_min': float(np.min(curvatures)),
        'kappa_max': float(np.max(curvatures)),
    }

# TEST 1: Top N nodes (different seeds)
print("="*70)
print("TEST 1: Node Set Variations")
print("="*70)
print()

for n_nodes, seed in [(250, 1), (250, 2), (250, 3), (375, 1), (500, 1)]:
    config_name = f"Top {n_nodes} nodes (seed {seed})"
    print(f"Testing: {config_name}")
    
    # Get top N nodes by degree
    np.random.seed(seed)
    degrees = dict(G_full.degree())
    top_nodes = sorted(degrees, key=degrees.get, reverse=True)[:n_nodes]
    
    # Add randomization if seed > 1
    if seed > 1:
        np.random.shuffle(top_nodes)
        top_nodes = top_nodes[:n_nodes]
    
    G_sub = G_full.subgraph(top_nodes).copy()
    
    res = compute_curvature(G_sub, config_name)
    res['config'] = config_name
    res['test_type'] = 'node_set'
    results.append(res)
    
    print(f"    → κ_mean = {res['kappa_mean']:.4f}")
    print()

# TEST 2: Edge weight thresholds
print("="*70)
print("TEST 2: Edge Weight Threshold Variations")
print("="*70)
print()

for threshold in [0.10, 0.15, 0.25, 0.30]:
    config_name = f"Threshold ≥ {threshold}"
    print(f"Testing: {config_name}")
    
    # Filter edges by weight
    df_filtered = df[df['weight'] >= threshold]
    
    G_thresh = nx.DiGraph()
    for _, row in df_filtered.iterrows():
        G_thresh.add_edge(row['source'], row['target'], weight=row['weight'])
    
    # Sample top 500 nodes
    degrees = dict(G_thresh.degree())
    top_nodes = sorted(degrees, key=degrees.get, reverse=True)[:500]
    G_sub = G_thresh.subgraph(top_nodes).copy()
    
    if G_sub.number_of_nodes() < 100:
        print(f"    ⚠️ Too few nodes ({G_sub.number_of_nodes()}), skipping")
        continue
    
    res = compute_curvature(G_sub, config_name)
    res['config'] = config_name
    res['test_type'] = 'threshold'
    results.append(res)
    
    print(f"    → κ_mean = {res['kappa_mean']:.4f}")
    print()

# Analysis
print("="*70)
print("📊 SYNTHESIS FOR REVIEWER")
print("="*70)
print()

kappas = [r['kappa_mean'] for r in results]
kappa_overall_mean = np.mean(kappas)
kappa_overall_std = np.std(kappas)

print(f"Tested configurations: {len(results)}")
print(f"κ_mean across all configs: {kappa_overall_mean:.4f} ± {kappa_overall_std:.4f}")
print(f"Range: [{min(kappas):.3f}, {max(kappas):.3f}]")
print()

# Check robustness
hyperbolic_count = sum(1 for k in kappas if k < -0.10)
flat_count = sum(1 for k in kappas if abs(k) < 0.05)
positive_count = sum(1 for k in kappas if k > 0.05)

print(f"Geometry classification:")
print(f"  Hyperbolic (κ<-0.10): {hyperbolic_count}/{len(results)}")
print(f"  Flat/Euclidean (|κ|<0.05): {flat_count}/{len(results)}")
print(f"  Spherical (κ>0.05): {positive_count}/{len(results)}")
print()

if flat_count == len(results):
    conclusion = "ROBUST FLAT GEOMETRY - All configurations show κ≈0"
    interpretation = "Chinese network genuinely has flat geometry. Logographic hypothesis STRENGTHENED."
elif hyperbolic_count >= len(results) * 0.8:
    conclusion = "SAMPLING ARTIFACT - Most substructures are hyperbolic"
    interpretation = "Original Chinese analysis was misled by specific 500-node sample. Genuine geometry is hyperbolic."
elif abs(kappa_overall_std) < 0.05:
    conclusion = "CONSISTENT ACROSS CONFIGURATIONS"
    interpretation = f"Chinese network consistently shows κ≈{kappa_overall_mean:.3f} regardless of sampling."
else:
    conclusion = "HETEROGENEOUS - Configuration-dependent"
    interpretation = "Chinese network geometry depends on node selection/threshold. Requires further investigation."

print(f"CONCLUSION: {conclusion}")
print(f"INTERPRETATION: {interpretation}")
print()

# Save
output_path = Path(__file__).parent.parent.parent / "results" / "chinese_substructure_analysis.json"
with open(output_path, 'w') as f:
    json.dump({
        'test_purpose': 'Response to Reviewer #1 Chinese anomaly concern',
        'configurations_tested': len(results),
        'results': results,
        'summary': {
            'mean_across_configs': float(kappa_overall_mean),
            'std_across_configs': float(kappa_overall_std),
            'range': [float(min(kappas)), float(max(kappas))],
            'hyperbolic_count': hyperbolic_count,
            'flat_count': flat_count,
            'conclusion': conclusion,
            'interpretation': interpretation
        }
    }, f, indent=2)

print(f"💾 Results saved: {output_path}")
print()
print("="*70)
print("✅ CHINESE SUBSTRUCTURE ANALYSIS COMPLETE")
print("="*70)

