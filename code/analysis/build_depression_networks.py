#!/usr/bin/env python3
"""
Build Semantic Networks from Depression Social Media Data
HelaDepDet dataset: 41K posts with 4 severity levels
"""

import pandas as pd
import networkx as nx
import numpy as np
from pathlib import Path
import re
from collections import Counter
import json

print("="*70)
print("BUILDING SEMANTIC NETWORKS FROM DEPRESSION DATA")
print("Dataset: HelaDepDet (41K posts, 4 severity levels)")
print("="*70)
print()

# ============================================================================
# LOAD DATA
# ============================================================================

print("LOADING DATASET")
print("-"*70)

data_file = 'data/external/Depression_Severity_Levels_Dataset/Depression_Severity_Levels_Dataset.csv'
df = pd.read_csv(data_file)

print(f"✅ Loaded {len(df):,} posts")
print()
print("Label distribution:")
print(df['label'].value_counts())
print()

# ============================================================================
# SAMPLE DATA (stratified by severity)
# ============================================================================

print("SAMPLING DATA (stratified)")
print("-"*70)

# Sample 250 posts per severity level = 1,000 total
# This is manageable and representative
n_per_class = 250

sampled_dfs = []
for label in ['minimum', 'mild', 'moderate', 'severe']:
    label_df = df[df['label'] == label].sample(n=n_per_class, random_state=42)
    sampled_dfs.append(label_df)

df_sample = pd.concat(sampled_dfs, ignore_index=True)

print(f"✅ Sampled {len(df_sample)} posts ({n_per_class} per severity level)")
print()

# ============================================================================
# BUILD SEMANTIC NETWORKS
# ============================================================================

print("BUILDING SEMANTIC CO-OCCURRENCE NETWORKS")
print("-"*70)
print()

def build_cooccurrence_network(texts, window_size=10, min_freq=2):
    """
    Build co-occurrence network from texts
    
    Args:
        texts: List of text strings
        window_size: Sliding window for co-occurrence
        min_freq: Minimum word frequency to include
    
    Returns:
        NetworkX Graph
    """
    # Tokenize all texts
    all_words = []
    for text in texts:
        # Simple tokenization (lowercase, remove non-alpha)
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        all_words.extend(words)
    
    # Count word frequencies
    word_counts = Counter(all_words)
    
    # Filter by minimum frequency
    valid_words = {word for word, count in word_counts.items() if count >= min_freq}
    
    # Build co-occurrence matrix
    G = nx.Graph()
    
    for text in texts:
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        # Filter to valid words
        words = [w for w in words if w in valid_words]
        
        # Add edges within window
        for i in range(len(words)):
            for j in range(i+1, min(i+window_size, len(words))):
                if words[i] != words[j]:
                    if G.has_edge(words[i], words[j]):
                        G[words[i]][words[j]]['weight'] += 1
                    else:
                        G.add_edge(words[i], words[j], weight=1)
    
    return G

# Build network for each severity level
networks = {}

for label in ['minimum', 'mild', 'moderate', 'severe']:
    print(f"Building network for: {label}")
    
    label_texts = df_sample[df_sample['label'] == label]['text'].tolist()
    
    G = build_cooccurrence_network(label_texts, window_size=10, min_freq=5)
    
    # Get largest connected component
    if len(G) > 0:
        components = list(nx.connected_components(G))
        if components:
            largest_cc = max(components, key=len)
            G_lcc = G.subgraph(largest_cc).copy()
            
            print(f"  Network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
            print(f"  LCC: {G_lcc.number_of_nodes()} nodes, {G_lcc.number_of_edges()} edges")
            print()
            
            networks[label] = G_lcc
        else:
            print(f"  ⚠️ No components found")
    else:
        print(f"  ⚠️ Empty network")

print()

# ============================================================================
# SAVE NETWORKS AS EDGE LISTS
# ============================================================================

print("SAVING NETWORKS")
print("-"*70)

output_dir = Path('data/processed/depression_networks')
output_dir.mkdir(parents=True, exist_ok=True)

for label, G in networks.items():
    # Save edge list
    edge_file = output_dir / f'depression_{label}_edges.csv'
    edges = []
    for u, v, data in G.edges(data=True):
        edges.append({
            'source': u,
            'target': v,
            'weight': data['weight']
        })
    
    df_edges = pd.DataFrame(edges)
    df_edges.to_csv(edge_file, index=False)
    
    print(f"✅ Saved: {edge_file.name} ({len(edges)} edges)")

print()

# ============================================================================
# COMPUTE BASIC METRICS
# ============================================================================

print("COMPUTING BASIC NETWORK METRICS")
print("-"*70)
print()

metrics_summary = []

for label, G in networks.items():
    # Clustering
    clustering = nx.average_clustering(G, weight='weight')
    
    # Connected components
    n_components = nx.number_connected_components(G)
    
    # Component sizes
    component_sizes = [len(c) for c in nx.connected_components(G)]
    median_size = np.median(component_sizes) if component_sizes else 0
    
    # Degree
    degrees = [d for n, d in G.degree()]
    avg_degree = np.mean(degrees) if degrees else 0
    
    metrics = {
        'severity': label,
        'n_nodes': G.number_of_nodes(),
        'n_edges': G.number_of_edges(),
        'clustering': clustering,
        'n_components': n_components,
        'median_component_size': median_size,
        'avg_degree': avg_degree,
        'in_sweet_spot': 0.02 <= clustering <= 0.15
    }
    
    metrics_summary.append(metrics)
    
    print(f"{label.upper()}:")
    print(f"  Nodes: {metrics['n_nodes']}")
    print(f"  Edges: {metrics['n_edges']}")
    print(f"  Clustering: {metrics['clustering']:.3f} {'✅ IN SWEET SPOT' if metrics['in_sweet_spot'] else '❌ OUT'}")
    print(f"  Components: {metrics['n_components']}")
    print(f"  Median component size: {metrics['median_component_size']:.0f}")
    print()

# Save summary
df_metrics = pd.DataFrame(metrics_summary)
df_metrics.to_csv('results/depression_networks_basic_metrics.csv', index=False)

print("✅ Saved: results/depression_networks_basic_metrics.csv")
print()

# ============================================================================
# INITIAL ANALYSIS
# ============================================================================

print("="*70)
print("INITIAL FINDINGS")
print("="*70)
print()

print("Sweet Spot Analysis:")
for row in metrics_summary:
    status = "✅ IN" if row['in_sweet_spot'] else "❌ OUT"
    print(f"  {row['severity']:10s}: C = {row['clustering']:.3f} {status}")

print()
print("Fragmentation Analysis:")
for row in metrics_summary:
    print(f"  {row['severity']:10s}: {row['n_components']} components (median size: {row['median_component_size']:.0f})")

print()
print("="*70)
print("✅ NETWORK BUILDING COMPLETE!")
print("="*70)
print()
print("🎯 NEXT: Compute curvature (κ) and KEC for all severity levels!")

