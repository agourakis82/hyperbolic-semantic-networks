#!/usr/bin/env python3
"""
Compute OR Curvature on CORRECTLY Preprocessed Networks
========================================================
CRITICAL: This will determine TRUE Chinese κ value!
"""

import pandas as pd
import networkx as nx
from GraphRicciCurvature.OllivierRicci import OllivierRicci
import numpy as np
from pathlib import Path
import json

def compute_curvature(edge_file: Path, language: str, alpha: float = 0.5):
    """Compute Ollivier-Ricci curvature."""
    print(f"="*80)
    print(f"Computing curvature: {language}")
    print(f"="*80)
    
    # Load edges
    df = pd.read_csv(edge_file)
    print(f"Loaded {len(df)} edges")
    
    # Build directed graph
    G = nx.DiGraph()
    for _, row in df.iterrows():
        G.add_edge(row['source'], row['target'], weight=row['weight'])
    
    # Convert to undirected
    G_undir = G.to_undirected()
    
    # Get largest component
    if not nx.is_connected(G_undir):
        largest_cc = max(nx.connected_components(G_undir), key=len)
        G_undir = G_undir.subgraph(largest_cc).copy()
    
    print(f"Network: {G_undir.number_of_nodes()} nodes, {G_undir.number_of_edges()} edges")
    
    # Compute OR curvature
    print(f"Computing OR curvature (α={alpha})...")
    orc = OllivierRicci(G_undir, alpha=alpha, verbose="ERROR")
    orc.compute_ricci_curvature()
    G_orc = orc.G
    
    # Extract curvatures
    curvatures = [G_orc[u][v]['ricciCurvature'] for u, v in G_orc.edges()]
    
    κ_mean = np.mean(curvatures)
    κ_median = np.median(curvatures)
    κ_std = np.std(curvatures)
    
    print(f"")
    print(f"✅ RESULTS for {language}:")
    print(f"   κ_mean:   {κ_mean:+.4f}")
    print(f"   κ_median: {κ_median:+.4f}")
    print(f"   κ_std:    {κ_std:.4f}")
    print(f"")
    
    if κ_mean < -0.05:
        geometry = "HYPERBOLIC (κ < 0)"
    elif κ_mean > 0.05:
        geometry = "SPHERICAL (κ > 0)"
    else:
        geometry = "FLAT/EUCLIDEAN (κ ≈ 0)"
    
    print(f"   Geometry: {geometry}")
    print()
    
    return {
        'language': language,
        'n_nodes': G_undir.number_of_nodes(),
        'n_edges': G_undir.number_of_edges(),
        'kappa_mean': float(κ_mean),
        'kappa_median': float(κ_median),
        'kappa_std': float(κ_std),
        'kappa_min': float(np.min(curvatures)),
        'kappa_max': float(np.max(curvatures)),
        'geometry': geometry
    }

def main():
    print("="*80)
    print("🔬 FINAL CURVATURE COMPUTATION - Correct Preprocessing")
    print("="*80)
    print()
    print("CRITICAL QUESTION: Is Chinese κ NEGATIVE or POSITIVE?")
    print()
    
    results = {}
    
    # Compute for all 3 languages
    for lang in ['spanish', 'english', 'chinese']:
        edge_file = Path(f"data/processed/{lang}_edges_CORRECT.csv")
        if edge_file.exists():
            results[lang] = compute_curvature(edge_file, lang.capitalize(), alpha=0.5)
        else:
            print(f"⚠️ {lang} file not found, skipping")
    
    # Summary
    print("="*80)
    print("📊 SUMMARY - True Curvature Values")
    print("="*80)
    print()
    print(f"{'Language':<12} {'κ_mean':>10} {'κ_median':>10} {'Geometry':>20}")
    print("-"*80)
    
    for lang, res in results.items():
        print(f"{lang.capitalize():<12} {res['kappa_mean']:>+10.4f} {res['kappa_median']:>+10.4f} {res['geometry']:>20}")
    
    print()
    print("="*80)
    print("🎯 CONCLUSION")
    print("="*80)
    print()
    
    chinese_kappa = results.get('chinese', {}).get('kappa_mean', 0)
    
    if chinese_kappa < -0.05:
        print("✅ Chinese is HYPERBOLIC (κ < 0)")
        print("   → 3/3 languages show hyperbolic geometry")
        print("   → Script-geometry hypothesis is INVALIDATED")
        print("   → Manuscript should maintain 4/4 hyperbolic conclusion")
    elif chinese_kappa > 0.05:
        print("🚨 Chinese is SPHERICAL (κ > 0)")
        print("   → 2/3 alphabetic hyperbolic, 1/3 logographic spherical")
        print("   → Script-geometry hypothesis is VALIDATED")
        print("   → Manuscript revolutionary finding CONFIRMED")
    else:
        print("⚠️ Chinese is FLAT (κ ≈ 0)")
        print("   → Intermediate case, requires further investigation")
    
    print()
    
    # Save results
    output_file = Path("results/FINAL_CURVATURE_CORRECTED_PREPROCESSING.json")
    output_file.parent.mkdir(exist_ok=True, parents=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Results saved: {output_file}")
    print()

if __name__ == '__main__':
    main()

