#!/usr/bin/env python3
"""
Rebuild Depression Networks with OPTIMAL Parameters
Based on parameter sweep results: long_words method
"""

import pandas as pd
import networkx as nx
import numpy as np
from pathlib import Path
import re
from tqdm import tqdm

print("="*70)
print("REBUILDING DEPRESSION NETWORKS - OPTIMAL PARAMETERS")
print("Method: long_words (≥5 chars), Window size: 5")
print("="*70)
print()

# Load full dataset
data_file = 'data/external/Depression_Severity_Levels_Dataset/Depression_Severity_Levels_Dataset.csv'
df = pd.read_csv(data_file)

print(f"Full dataset: {len(df):,} posts")
print()

# Sample stratified (1,000 posts = 250 per level)
n_per_class = 250
sampled_dfs = []
for label in ['minimum', 'mild', 'moderate', 'severe']:
    label_df = df[df['label'] == label].sample(n=n_per_class, random_state=42)
    sampled_dfs.append(label_df)

df_sample = pd.concat(sampled_dfs, ignore_index=True)
print(f"Sample: {len(df_sample)} posts (250 per severity)")
print()

# ============================================================================
# BUILD NETWORKS WITH OPTIMAL PARAMETERS
# ============================================================================

def build_optimal_network(texts, window_size=5, min_word_length=5):
    """
    Build network with optimal parameters from sweep
    
    Parameters:
    - window_size: 5 (from sweep)
    - min_word_length: 5 (long_words method - best from sweep)
    """
    G = nx.Graph()
    
    for text in texts:
        # Extract long words only (≥5 chars)
        words = re.findall(rf'\b[a-z]{{{min_word_length},}}\b', text.lower())
        
        # Co-occurrence within window
        for i in range(len(words)):
            for j in range(i+1, min(i+window_size, len(words))):
                if words[i] != words[j]:
                    if G.has_edge(words[i], words[j]):
                        G[words[i]][words[j]]['weight'] += 1
                    else:
                        G.add_edge(words[i], words[j], weight=1)
    
    return G

print("BUILDING OPTIMIZED NETWORKS")
print("-"*70)
print()

networks = {}
metrics = []

for label in ['minimum', 'mild', 'moderate', 'severe']:
    print(f"Building: {label}")
    
    texts = df_sample[df_sample['label'] == label]['text'].tolist()
    
    G = build_optimal_network(texts, window_size=5, min_word_length=5)
    
    # Get LCC
    if len(G) > 0 and G.number_of_edges() > 0:
        components = list(nx.connected_components(G))
        largest_cc = max(components, key=len)
        G_lcc = G.subgraph(largest_cc).copy()
        
        # Compute metrics
        C = nx.average_clustering(G_lcc, weight='weight')
        n_components = nx.number_connected_components(G)
        component_sizes = [len(c) for c in components]
        median_size = np.median(component_sizes)
        
        # Fragmentation metric
        fragmentation = n_components / G.number_of_nodes() if G.number_of_nodes() > 0 else 0
        
        # Density
        density = nx.density(G_lcc)
        
        in_sweet_spot = 0.02 <= C <= 0.15
        
        print(f"  Total: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        print(f"  LCC: {G_lcc.number_of_nodes()} nodes, {G_lcc.number_of_edges()} edges")
        print(f"  Clustering: {C:.4f} {'✅ SWEET SPOT!' if in_sweet_spot else '⚠️'}")
        print(f"  Components: {n_components} (fragmentation = {fragmentation:.4f})")
        print(f"  Density: {density:.4f}")
        print()
        
        networks[label] = G_lcc
        
        metrics.append({
            'severity': label,
            'n_nodes': G_lcc.number_of_nodes(),
            'n_edges': G_lcc.number_of_edges(),
            'clustering': C,
            'n_components': n_components,
            'median_component_size': median_size,
            'fragmentation': fragmentation,
            'density': density,
            'in_sweet_spot': in_sweet_spot
        })

# Save edge lists
output_dir = Path('data/processed/depression_networks_optimal')
output_dir.mkdir(parents=True, exist_ok=True)

for label, G in networks.items():
    edge_file = output_dir / f'depression_{label}_edges.csv'
    edges = []
    for u, v, data in G.edges(data=True):
        edges.append({'source': u, 'target': v, 'weight': data['weight']})
    pd.DataFrame(edges).to_csv(edge_file, index=False)
    print(f"✅ Saved: {edge_file.name}")

# Save metrics
df_metrics = pd.DataFrame(metrics)
df_metrics.to_csv('results/depression_optimal_metrics.csv', index=False)

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print()
print(df_metrics[['severity', 'clustering', 'fragmentation', 'in_sweet_spot']].to_string(index=False))

print("\n✅ OPTIMAL NETWORKS BUILT!")

