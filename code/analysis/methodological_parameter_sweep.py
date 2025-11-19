#!/usr/bin/env python3
"""
METHODOLOGICAL PARAMETER SWEEP
Systematic testing of network construction parameters
"""

import pandas as pd
import networkx as nx
import numpy as np
from pathlib import Path
import re
from collections import Counter
import json
from tqdm import tqdm
import nltk
from nltk.corpus import stopwords

# Download stopwords if needed
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

STOPWORDS = set(stopwords.words('english'))

print("="*70)
print("METHODOLOGICAL PARAMETER SWEEP")
print("Finding optimal parameters for social media semantic networks")
print("="*70)
print()

# ============================================================================
# LOAD DATA
# ============================================================================

data_file = 'data/external/Depression_Severity_Levels_Dataset/Depression_Severity_Levels_Dataset.csv'
df = pd.read_csv(data_file)

# Sample for testing (faster)
df_test = df.sample(n=500, random_state=42)  # 500 posts for quick testing

print(f"Test sample: {len(df_test)} posts")
print()

# ============================================================================
# EXPERIMENT 1: WINDOW SIZE SWEEP
# ============================================================================

print("="*70)
print("EXPERIMENT 1: WINDOW SIZE SWEEP")
print("="*70)
print()

window_sizes = [2, 3, 4, 5, 7, 10, 15, 20, 50]
window_results = []

print("Testing window sizes: ", window_sizes)
print()

for window_size in tqdm(window_sizes, desc="Window sizes"):
    # Build network
    G = nx.Graph()
    
    for text in df_test['text']:
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        
        for i in range(len(words)):
            for j in range(i+1, min(i+window_size, len(words))):
                if words[i] != words[j]:
                    if G.has_edge(words[i], words[j]):
                        G[words[i]][words[j]]['weight'] += 1
                    else:
                        G.add_edge(words[i], words[j], weight=1)
    
    # Get LCC
    if len(G) > 0:
        components = list(nx.connected_components(G))
        largest_cc = max(components, key=len)
        G_lcc = G.subgraph(largest_cc).copy()
        
        # Compute metrics
        C = nx.average_clustering(G_lcc, weight='weight')
        n_nodes = G_lcc.number_of_nodes()
        n_edges = G_lcc.number_of_edges()
        density = nx.density(G_lcc)
        
        in_sweet_spot = 0.02 <= C <= 0.15
        
        window_results.append({
            'window_size': window_size,
            'n_nodes': n_nodes,
            'n_edges': n_edges,
            'clustering': C,
            'density': density,
            'in_sweet_spot': in_sweet_spot
        })
        
        status = "✅ SWEET SPOT" if in_sweet_spot else "❌"
        print(f"  Window {window_size:3d}: C = {C:.4f}, Nodes = {n_nodes:5d}, Density = {density:.4f} {status}")

print()

# ============================================================================
# EXPERIMENT 2: NODE SELECTION (Content Words)
# ============================================================================

print("="*70)
print("EXPERIMENT 2: NODE SELECTION (Content vs. All Words)")
print("="*70)
print()

node_selection_methods = {
    'all_words': lambda words: words,
    'no_stopwords': lambda words: [w for w in words if w not in STOPWORDS],
    'long_words': lambda words: [w for w in words if len(w) >= 5],
    'content_only': lambda words: [w for w in words if w not in STOPWORDS and len(w) >= 4]
}

node_results = []

for method_name, filter_func in tqdm(node_selection_methods.items(), desc="Node selection"):
    # Build network with window=5 (reasonable)
    G = nx.Graph()
    
    for text in df_test['text']:
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        words = filter_func(words)
        
        window_size = 5
        for i in range(len(words)):
            for j in range(i+1, min(i+window_size, len(words))):
                if words[i] != words[j]:
                    if G.has_edge(words[i], words[j]):
                        G[words[i]][words[j]]['weight'] += 1
                    else:
                        G.add_edge(words[i], words[j], weight=1)
    
    # Get LCC
    if len(G) > 0:
        components = list(nx.connected_components(G))
        largest_cc = max(components, key=len)
        G_lcc = G.subgraph(largest_cc).copy()
        
        C = nx.average_clustering(G_lcc, weight='weight')
        n_nodes = G_lcc.number_of_nodes()
        n_edges = G_lcc.number_of_edges()
        
        in_sweet_spot = 0.02 <= C <= 0.15
        
        node_results.append({
            'method': method_name,
            'n_nodes': n_nodes,
            'n_edges': n_edges,
            'clustering': C,
            'in_sweet_spot': in_sweet_spot
        })
        
        status = "✅ SWEET SPOT" if in_sweet_spot else "❌"
        print(f"  {method_name:15s}: C = {C:.4f}, Nodes = {n_nodes:5d} {status}")

print()

# ============================================================================
# EXPERIMENT 3: SENTENCE-LEVEL NETWORKS
# ============================================================================

print("="*70)
print("EXPERIMENT 3: SENTENCE-LEVEL vs. WINDOW-BASED")
print("="*70)
print()

# Sentence-level: edges only within same sentence
G_sentence = nx.Graph()

for text in tqdm(df_test['text'], desc="Building sentence-level network"):
    # Split into sentences (simple split by punctuation)
    sentences = re.split(r'[.!?]+', text)
    
    for sentence in sentences:
        words = re.findall(r'\b[a-z]{4,}\b', sentence.lower())
        words = [w for w in words if w not in STOPWORDS]
        
        # Connect all words in same sentence (complete graph)
        for i in range(len(words)):
            for j in range(i+1, len(words)):
                if words[i] != words[j]:
                    if G_sentence.has_edge(words[i], words[j]):
                        G_sentence[words[i]][words[j]]['weight'] += 1
                    else:
                        G_sentence.add_edge(words[i], words[j], weight=1)

# Get LCC
if len(G_sentence) > 0:
    components = list(nx.connected_components(G_sentence))
    largest_cc = max(components, key=len)
    G_lcc_sentence = G_sentence.subgraph(largest_cc).copy()
    
    C_sentence = nx.average_clustering(G_lcc_sentence, weight='weight')
    n_nodes_sentence = G_lcc_sentence.number_of_nodes()
    n_edges_sentence = G_lcc_sentence.number_of_edges()
    
    in_sweet_spot_sentence = 0.02 <= C_sentence <= 0.15
    
    status = "✅ SWEET SPOT" if in_sweet_spot_sentence else "❌"
    print(f"  Sentence-level: C = {C_sentence:.4f}, Nodes = {n_nodes_sentence}, Edges = {n_edges_sentence} {status}")

print()

# ============================================================================
# SAVE ALL RESULTS
# ============================================================================

print("="*70)
print("SAVING RESULTS")
print("="*70)
print()

results = {
    'window_size_sweep': window_results,
    'node_selection': node_results,
    'sentence_level': {
        'clustering': C_sentence,
        'n_nodes': n_nodes_sentence,
        'n_edges': n_edges_sentence,
        'in_sweet_spot': in_sweet_spot_sentence
    }
}

with open('results/methodological_parameter_sweep.json', 'w') as f:
    json.dump(results, f, indent=2)

# Also save as CSV
df_window = pd.DataFrame(window_results)
df_window.to_csv('results/window_size_sweep.csv', index=False)

df_nodes = pd.DataFrame(node_results)
df_nodes.to_csv('results/node_selection_sweep.csv', index=False)

print("✅ Saved:")
print("  - results/methodological_parameter_sweep.json")
print("  - results/window_size_sweep.csv")
print("  - results/node_selection_sweep.csv")
print()

# ============================================================================
# ANALYSIS
# ============================================================================

print("="*70)
print("ANALYSIS: FINDING OPTIMAL PARAMETERS")
print("="*70)
print()

# Find window sizes that hit sweet spot
sweet_spot_windows = [r for r in window_results if r['in_sweet_spot']]

if sweet_spot_windows:
    print("✅ SWEET SPOT ACHIEVED WITH:")
    for r in sweet_spot_windows:
        print(f"   Window size {r['window_size']}: C = {r['clustering']:.4f}")
else:
    print("⚠️ No window size hit sweet spot")
    print("   Closest:")
    closest = min(window_results, key=lambda r: abs(r['clustering'] - 0.085))
    print(f"   Window size {closest['window_size']}: C = {closest['clustering']:.4f}")

print()

# Find node selection methods that hit sweet spot
sweet_spot_nodes = [r for r in node_results if r['in_sweet_spot']]

if sweet_spot_nodes:
    print("✅ SWEET SPOT ACHIEVED WITH:")
    for r in sweet_spot_nodes:
        print(f"   {r['method']}: C = {r['clustering']:.4f}")
else:
    print("⚠️ No node selection hit sweet spot")
    print("   Closest:")
    closest = min(node_results, key=lambda r: abs(r['clustering'] - 0.085))
    print(f"   {closest['method']}: C = {closest['clustering']:.4f}")

print()

if in_sweet_spot_sentence:
    print("✅ SENTENCE-LEVEL NETWORK IN SWEET SPOT!")
    print(f"   C = {C_sentence:.4f}")
else:
    print(f"⚠️ Sentence-level: C = {C_sentence:.4f}")

print()

# ============================================================================
# RECOMMENDATIONS
# ============================================================================

print("="*70)
print("RECOMMENDATIONS")
print("="*70)
print()

# Find best overall
all_methods = []

for r in window_results:
    all_methods.append({
        'method': f"Window {r['window_size']}",
        'clustering': r['clustering'],
        'in_sweet_spot': r['in_sweet_spot'],
        'distance_from_center': abs(r['clustering'] - 0.085)
    })

for r in node_results:
    all_methods.append({
        'method': r['method'],
        'clustering': r['clustering'],
        'in_sweet_spot': r['in_sweet_spot'],
        'distance_from_center': abs(r['clustering'] - 0.085)
    })

all_methods.append({
    'method': 'Sentence-level',
    'clustering': C_sentence,
    'in_sweet_spot': in_sweet_spot_sentence,
    'distance_from_center': abs(C_sentence - 0.085)
})

# Sort by distance from sweet spot center (0.085)
all_methods_sorted = sorted(all_methods, key=lambda x: x['distance_from_center'])

print("TOP 5 METHODS (closest to sweet spot center = 0.085):")
for i, method in enumerate(all_methods_sorted[:5], 1):
    status = "✅" if method['in_sweet_spot'] else "⚠️"
    print(f"{i}. {method['method']:20s}: C = {method['clustering']:.4f} {status}")

print()

# BEST METHOD
best_method = all_methods_sorted[0]
print(f"🏆 BEST METHOD: {best_method['method']}")
print(f"   Clustering: {best_method['clustering']:.4f}")
print(f"   In sweet spot: {best_method['in_sweet_spot']}")

print()
print("="*70)
print("✅ PARAMETER SWEEP COMPLETE!")
print("="*70)
print()
print("🎯 NEXT: Rebuild depression networks with optimal parameters!")

