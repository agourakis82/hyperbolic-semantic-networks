#!/usr/bin/env python3
"""
Compute Curvature and Complete KEC for Depression Networks
"""

import pandas as pd
import networkx as nx
import numpy as np
from pathlib import Path
from GraphRicciCurvature.OllivierRicci import OllivierRicci
from scipy import linalg
from scipy.stats import spearmanr, pearsonr
import json

print("="*70)
print("COMPUTING CURVATURE + COMPLETE KEC FOR DEPRESSION")
print("="*70)
print()

# Load optimal networks
networks = {}
severity_levels = ['minimum', 'mild', 'moderate', 'severe']

for level in severity_levels:
    edge_file = f'data/processed/depression_networks_optimal/depression_{level}_edges.csv'
    if Path(edge_file).exists():
        df_edges = pd.read_csv(edge_file)
        G = nx.Graph()
        for _, row in df_edges.iterrows():
            G.add_edge(row['source'], row['target'], weight=row['weight'])
        networks[level] = G
        print(f"✅ Loaded {level}: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

print()

# ============================================================================
# COMPUTE OLLIVIER-RICCI CURVATURE
# ============================================================================

print("="*70)
print("COMPUTING OLLIVIER-RICCI CURVATURE")
print("="*70)
print()

curvature_results = {}

for level, G in networks.items():
    print(f"\n{level.upper()}:")
    print("-"*70)
    
    # Compute OR curvature
    orc = OllivierRicci(G, alpha=0.5, verbose="ERROR")
    orc.compute_ricci_curvature()
    
    # Extract edge curvatures
    edge_curvatures = [orc.G[u][v]['ricciCurvature'] for u, v in orc.G.edges()]
    
    # Mean curvature
    kappa = np.mean(edge_curvatures)
    kappa_std = np.std(edge_curvatures)
    
    print(f"  κ (curvature): {kappa:.4f} ± {kappa_std:.4f}")
    print(f"  Range: [{np.min(edge_curvatures):.4f}, {np.max(edge_curvatures):.4f}]")
    
    curvature_results[level] = {
        'mean': kappa,
        'std': kappa_std,
        'min': np.min(edge_curvatures),
        'max': np.max(edge_curvatures),
        'values': edge_curvatures
    }

print()

# ============================================================================
# COMPUTE SPECTRAL ENTROPY
# ============================================================================

print("="*70)
print("COMPUTING SPECTRAL ENTROPY")
print("="*70)
print()

spectral_results = {}

for level, G in networks.items():
    print(f"{level.upper()}:")
    
    # Normalized Laplacian
    L = nx.normalized_laplacian_matrix(G).toarray()
    
    # Eigenvalues
    eigenvalues = linalg.eigvalsh(L)
    eigenvalues = np.abs(eigenvalues)
    eigenvalues = eigenvalues / eigenvalues.sum()
    eigenvalues = eigenvalues[eigenvalues > 1e-10]
    
    # Spectral entropy
    H_spectral = -np.sum(eigenvalues * np.log2(eigenvalues + 1e-10))
    
    print(f"  H_spectral: {H_spectral:.4f}")
    
    spectral_results[level] = H_spectral

print()

# ============================================================================
# LOAD CLUSTERING (already computed)
# ============================================================================

df_metrics = pd.read_csv('results/depression_optimal_metrics.csv')

# ============================================================================
# COMPUTE COMPLETE KEC
# ============================================================================

print("="*70)
print("COMPUTING COMPLETE KEC")
print("="*70)
print()

kec_results = []

for level in severity_levels:
    # Get metrics
    row = df_metrics[df_metrics['severity'] == level].iloc[0]
    
    C = row['clustering']
    fragmentation = row['fragmentation']
    density = row['density']
    
    kappa = curvature_results[level]['mean']
    H_spectral = spectral_results[level]
    
    # Normalize to 0-1 (simple approach - can refine later)
    # Using empirical ranges
    kappa_z = (kappa - (-0.3)) / (0.1 - (-0.3))  # Assume range [-0.3, 0.1]
    H_spectral_z = (H_spectral - 5.0) / (12.0 - 5.0)  # Assume range [5, 12]
    C_z = C / 0.3  # Normalize clustering
    
    # KEC with spectral
    KEC_spectral = (H_spectral_z + kappa_z - C_z) / 3
    
    # Also compute with fragmentation instead of clustering
    frag_z = fragmentation / 0.01  # Normalize
    KEC_frag = (H_spectral_z + kappa_z + frag_z) / 3
    
    kec_results.append({
        'severity': level,
        'severity_numeric': severity_levels.index(level),
        'clustering': C,
        'curvature': kappa,
        'H_spectral': H_spectral,
        'fragmentation': fragmentation,
        'clustering_z': C_z,
        'curvature_z': kappa_z,
        'H_spectral_z': H_spectral_z,
        'fragmentation_z': frag_z,
        'KEC_spectral': KEC_spectral,
        'KEC_frag': KEC_frag
    })
    
    print(f"\n{level.upper()}:")
    print(f"  C (clustering):   {C:.4f} (z={C_z:.3f})")
    print(f"  κ (curvature):    {kappa:.4f} (z={kappa_z:.3f})")
    print(f"  H (spectral):     {H_spectral:.4f} (z={H_spectral_z:.3f})")
    print(f"  Fragmentation:    {fragmentation:.4f} (z={frag_z:.3f})")
    print(f"  KEC (spectral):   {KEC_spectral:.4f}")
    print(f"  KEC (frag):       {KEC_frag:.4f}")

print()

# ============================================================================
# STATISTICAL ANALYSIS
# ============================================================================

print("="*70)
print("STATISTICAL ANALYSIS - SEVERITY CORRELATION")
print("="*70)
print()

df_kec = pd.DataFrame(kec_results)

# Test correlations
severity_num = df_kec['severity_numeric'].values

correlations = {}
for metric in ['clustering', 'curvature', 'H_spectral', 'fragmentation', 'KEC_spectral', 'KEC_frag']:
    values = df_kec[metric].values
    rho, p = spearmanr(severity_num, values)
    r, p_pearson = pearsonr(severity_num, values)
    
    correlations[metric] = {
        'spearman_rho': rho,
        'spearman_p': p,
        'pearson_r': r,
        'pearson_p': p_pearson
    }
    
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "n.s."
    print(f"{metric:20s}: ρ = {rho:+.3f}, p = {p:.4f} {sig}")

print()

# Find best predictor
best_metric = max(correlations.items(), key=lambda x: abs(x[1]['spearman_rho']))
print(f"🏆 BEST PREDICTOR OF SEVERITY:")
print(f"   {best_metric[0]}: |ρ| = {abs(best_metric[1]['spearman_rho']):.3f}")

# ============================================================================
# SAVE ALL RESULTS
# ============================================================================

df_kec.to_csv('results/depression_complete_kec.csv', index=False)

with open('results/depression_kec_correlations.json', 'w') as f:
    json.dump(correlations, f, indent=2)

# Save curvature details
with open('results/depression_curvature_details.json', 'w') as f:
    # Convert numpy arrays to lists
    output = {}
    for level, data in curvature_results.items():
        output[level] = {
            'mean': float(data['mean']),
            'std': float(data['std']),
            'min': float(data['min']),
            'max': float(data['max'])
        }
    json.dump(output, f, indent=2)

print("\n✅ Saved:")
print("  - results/depression_complete_kec.csv")
print("  - results/depression_kec_correlations.json")
print("  - results/depression_curvature_details.json")

print("\n" + "="*70)
print("✅ COMPLETE ANALYSIS DONE!")
print("="*70)

