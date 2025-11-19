#!/usr/bin/env python3
"""
QUICK: Extract healthy controls clustering from SWOW networks
"""

import pandas as pd
import networkx as nx
import json

print("="*70)
print("EXTRACTING HEALTHY CONTROLS FROM SWOW")
print("="*70)
print()

# Load SWOW networks
languages = ['spanish', 'english', 'chinese']
healthy_controls = []

for lang in languages:
    edge_file = f'data/processed/{lang}_edges_FINAL.csv'
    
    try:
        print(f"Loading {lang}...")
        df_edges = pd.read_csv(edge_file)
        
        # Build network
        G = nx.Graph()
        for _, row in df_edges.iterrows():
            G.add_edge(row['source'], row['target'], weight=row['weight'])
        
        # Compute clustering
        C_weighted = nx.average_clustering(G, weight='weight')
        C_binary = nx.average_clustering(G)
        
        healthy_controls.append({
            'language': lang.capitalize(),
            'source': 'SWOW',
            'population': 'Healthy',
            'n_nodes': G.number_of_nodes(),
            'n_edges': G.number_of_edges(),
            'clustering_weighted': C_weighted,
            'clustering_binary': C_binary
        })
        
        print(f"  ✅ {lang.capitalize()}: C_w={C_weighted:.4f}, C_b={C_binary:.4f}")
        
    except Exception as e:
        print(f"  ❌ {lang}: {e}")

print()

# Compute statistics
if healthy_controls:
    df_healthy = pd.DataFrame(healthy_controls)
    
    print("Healthy Baseline Statistics:")
    print(f"  Mean C_weighted: {df_healthy['clustering_weighted'].mean():.4f}")
    print(f"  Std C_weighted:  {df_healthy['clustering_weighted'].std():.4f}")
    print(f"  Range:           [{df_healthy['clustering_weighted'].min():.4f}, {df_healthy['clustering_weighted'].max():.4f}]")
    print()
    
    # Save
    df_healthy.to_csv('results/healthy_controls_swow.csv', index=False)
    print("✅ Saved: results/healthy_controls_swow.csv")
    
    # Also save as JSON
    with open('results/healthy_controls_swow.json', 'w') as f:
        json.dump({
            'healthy_controls': healthy_controls,
            'statistics': {
                'mean_clustering': float(df_healthy['clustering_weighted'].mean()),
                'std_clustering': float(df_healthy['clustering_weighted'].std()),
                'min_clustering': float(df_healthy['clustering_weighted'].min()),
                'max_clustering': float(df_healthy['clustering_weighted'].max()),
                'n_languages': len(healthy_controls)
            }
        }, f, indent=2)
    
    print("✅ Saved: results/healthy_controls_swow.json")

print()
print("="*70)
print("✅ HEALTHY CONTROLS EXTRACTED!")
print("="*70)

