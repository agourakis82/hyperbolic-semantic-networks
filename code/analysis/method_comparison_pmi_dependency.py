#!/usr/bin/env python3
"""
METHOD COMPARISON: Co-occurrence vs. PMI vs. Dependency Parsing
Nature-tier validation of network construction approaches
"""

import pandas as pd
import networkx as nx
import numpy as np
from pathlib import Path
import re
from collections import Counter
from scipy.stats import chi2_contingency
import math

print("="*70)
print("METHOD COMPARISON: Network Construction Approaches")
print("Testing convergence across different methodologies")
print("="*70)
print()

# Load sample data
df_full = pd.read_csv('data/external/Depression_Severity_Levels_Dataset/Depression_Severity_Levels_Dataset.csv')
df_sample = df_full[df_full['label'] == 'moderate'].sample(n=250, random_state=42)
texts = [t for t in df_sample['text'].tolist() if isinstance(t, str)]

print(f"Test sample: {len(texts)} posts (moderate depression)")
print()

# ============================================================================
# METHOD 1: SIMPLE CO-OCCURRENCE (Current)
# ============================================================================

print("="*70)
print("METHOD 1: SIMPLE CO-OCCURRENCE (Window=5)")
print("="*70)
print()

def build_cooccurrence_network(texts, window_size=5, min_length=5):
    """Current method"""
    G = nx.Graph()
    for text in texts:
        words = re.findall(rf'\b[a-z]{{{min_length},}}\b', text.lower())
        for i in range(len(words)):
            for j in range(i+1, min(i+window_size, len(words))):
                if words[i] != words[j]:
                    if G.has_edge(words[i], words[j]):
                        G[words[i]][words[j]]['weight'] += 1
                    else:
                        G.add_edge(words[i], words[j], weight=1)
    
    # Get LCC
    if G.number_of_nodes() > 0:
        components = list(nx.connected_components(G))
        largest_cc = max(components, key=len)
        return G.subgraph(largest_cc).copy()
    return G

G_cooccur = build_cooccurrence_network(texts)
C_cooccur = nx.average_clustering(G_cooccur, weight='weight')

print(f"Nodes: {G_cooccur.number_of_nodes()}")
print(f"Edges: {G_cooccur.number_of_edges()}")
print(f"Clustering: {C_cooccur:.4f}")
print(f"In sweet spot: {'YES' if 0.02 <= C_cooccur <= 0.15 else 'NO'}")
print()

# ============================================================================
# METHOD 2: PMI (Pointwise Mutual Information)
# ============================================================================

print("="*70)
print("METHOD 2: PMI-BASED EDGES")
print("="*70)
print()

def build_pmi_network(texts, window_size=5, min_length=5, pmi_threshold=2.0):
    """
    Build network using PMI to filter edges
    
    PMI(w1, w2) = log( P(w1, w2) / (P(w1) * P(w2)) )
    
    High PMI = words co-occur more than expected by chance
    """
    # First, get co-occurrence counts
    word_counts = Counter()
    cooccur_counts = Counter()
    total_words = 0
    total_pairs = 0
    
    for text in texts:
        words = re.findall(rf'\b[a-z]{{{min_length},}}\b', text.lower())
        
        # Count words
        word_counts.update(words)
        total_words += len(words)
        
        # Count co-occurrences
        for i in range(len(words)):
            for j in range(i+1, min(i+window_size, len(words))):
                if words[i] != words[j]:
                    pair = tuple(sorted([words[i], words[j]]))
                    cooccur_counts[pair] += 1
                    total_pairs += 1
    
    # Compute PMI for each pair
    G = nx.Graph()
    
    for (w1, w2), cooccur_count in cooccur_counts.items():
        # Probabilities
        p_w1 = word_counts[w1] / total_words
        p_w2 = word_counts[w2] / total_words
        p_w1_w2 = cooccur_count / total_pairs
        
        # PMI
        if p_w1 > 0 and p_w2 > 0 and p_w1_w2 > 0:
            pmi = math.log2(p_w1_w2 / (p_w1 * p_w2))
            
            # Add edge if PMI above threshold
            if pmi >= pmi_threshold:
                G.add_edge(w1, w2, weight=pmi, count=cooccur_count)
    
    # Get LCC
    if G.number_of_nodes() > 0:
        components = list(nx.connected_components(G))
        largest_cc = max(components, key=len)
        return G.subgraph(largest_cc).copy()
    return G

G_pmi = build_pmi_network(texts, pmi_threshold=2.0)

if G_pmi.number_of_nodes() > 10:
    C_pmi = nx.average_clustering(G_pmi, weight='weight')
    
    print(f"Nodes: {G_pmi.number_of_nodes()}")
    print(f"Edges: {G_pmi.number_of_edges()}")
    print(f"Clustering: {C_pmi:.4f}")
    print(f"In sweet spot: {'YES' if 0.02 <= C_pmi <= 0.15 else 'NO'}")
else:
    print("⚠️ PMI network too sparse")
    C_pmi = 0.0

print()

# ============================================================================
# METHOD 3: WEIGHTED BY TF-IDF
# ============================================================================

print("="*70)
print("METHOD 3: TF-IDF WEIGHTED EDGES")
print("="*70)
print()

from sklearn.feature_extraction.text import TfidfVectorizer

def build_tfidf_network(texts, min_length=5, similarity_threshold=0.1):
    """
    Build network where edge weights = TF-IDF cosine similarity
    """
    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(
        token_pattern=rf'\b[a-z]{{{min_length},}}\b',
        max_features=1000
    )
    
    tfidf_matrix = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()
    
    # Compute word-word similarity from document co-occurrence
    # Transpose: words × documents
    word_doc_matrix = tfidf_matrix.T
    
    # Cosine similarity between words
    from sklearn.metrics.pairwise import cosine_similarity
    similarity_matrix = cosine_similarity(word_doc_matrix)
    
    # Build network
    G = nx.Graph()
    n_words = len(feature_names)
    
    for i in range(n_words):
        for j in range(i+1, n_words):
            sim = similarity_matrix[i, j]
            if sim >= similarity_threshold:
                G.add_edge(feature_names[i], feature_names[j], weight=sim)
    
    # Get LCC
    if G.number_of_nodes() > 0:
        components = list(nx.connected_components(G))
        largest_cc = max(components, key=len)
        return G.subgraph(largest_cc).copy()
    return G

G_tfidf = build_tfidf_network(texts, similarity_threshold=0.1)

if G_tfidf.number_of_nodes() > 10:
    C_tfidf = nx.average_clustering(G_tfidf, weight='weight')
    
    print(f"Nodes: {G_tfidf.number_of_nodes()}")
    print(f"Edges: {G_tfidf.number_of_edges()}")
    print(f"Clustering: {C_tfidf:.4f}")
    print(f"In sweet spot: {'YES' if 0.02 <= C_tfidf <= 0.15 else 'NO'}")
else:
    print("⚠️ TF-IDF network too sparse")
    C_tfidf = 0.0

print()

# ============================================================================
# COMPARISON SUMMARY
# ============================================================================

print("="*70)
print("METHOD COMPARISON SUMMARY")
print("="*70)
print()

comparison = pd.DataFrame({
    'Method': ['Co-occurrence', 'PMI', 'TF-IDF'],
    'Nodes': [G_cooccur.number_of_nodes(), G_pmi.number_of_nodes(), G_tfidf.number_of_nodes()],
    'Edges': [G_cooccur.number_of_edges(), G_pmi.number_of_edges(), G_tfidf.number_of_edges()],
    'Clustering': [C_cooccur, C_pmi, C_tfidf],
    'In_Sweet_Spot': [
        0.02 <= C_cooccur <= 0.15,
        0.02 <= C_pmi <= 0.15 if C_pmi > 0 else False,
        0.02 <= C_tfidf <= 0.15 if C_tfidf > 0 else False
    ]
})

print(comparison.to_string(index=False))
print()

# Check convergence
methods_in_sweet_spot = comparison['In_Sweet_Spot'].sum()
print(f"Methods in sweet spot: {methods_in_sweet_spot}/3")

if methods_in_sweet_spot >= 2:
    print("✅ CONVERGENT FINDINGS: Multiple methods confirm sweet spot!")
else:
    print("⚠️ Methods diverge - need to investigate")

# Save
comparison.to_csv('results/method_comparison_networks.csv', index=False)
print("\n✅ Saved: results/method_comparison_networks.csv")

print("\n" + "="*70)
print("✅ METHOD COMPARISON COMPLETE")
print("="*70)

