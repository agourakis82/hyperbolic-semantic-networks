#!/usr/bin/env python3
"""
ENTROPIA SHANNON vs. ESPECTRAL
Comparação sistemática para detectar pathology
"""

import networkx as nx
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import linalg
import json

print("="*70)
print("ENTROPIA: SHANNON vs. ESPECTRAL")
print("Qual detecta melhor a pathology?")
print("="*70)
print()

# ============================================================================
# IMPLEMENTAÇÕES DE ENTROPIA
# ============================================================================

def compute_shannon_entropy_transition(G):
    """
    Shannon Entropy baseada em probabilidades de transição
    H = -Σ p_i log(p_i)
    
    Como usado no KEC original (transition entropy)
    """
    entropies = []
    
    for node in G.nodes():
        # Get outgoing edges (if directed) or all edges (if undirected)
        if G.is_directed():
            neighbors = list(G.successors(node))
            edges = [(node, n) for n in neighbors]
        else:
            neighbors = list(G.neighbors(node))
            edges = [(node, n) for n in neighbors]
        
        if not edges:
            entropies.append(0.0)
            continue
        
        # Get edge weights
        weights = []
        for u, v in edges:
            w = G[u][v].get('weight', 1.0) if G.has_edge(u, v) else 1.0
            weights.append(w)
        
        # Normalize to probabilities
        weights = np.array(weights)
        probs = weights / weights.sum()
        
        # Shannon entropy
        H = -np.sum(probs * np.log2(probs + 1e-10))
        entropies.append(H)
    
    # Network-level: mean entropy
    return np.mean(entropies) if entropies else 0.0


def compute_shannon_entropy_degree(G):
    """
    Shannon Entropy baseada em distribuição de graus
    H = -Σ p(k) log(p(k))
    
    Mede heterogeneidade da distribuição de graus
    """
    degrees = [d for n, d in G.degree()]
    
    if not degrees:
        return 0.0
    
    # Count degree frequencies
    degree_counts = pd.Series(degrees).value_counts()
    
    # Normalize to probabilities
    probs = degree_counts / degree_counts.sum()
    
    # Shannon entropy
    H = -np.sum(probs * np.log2(probs + 1e-10))
    
    return H


def compute_spectral_entropy(G):
    """
    Entropia Espectral baseada em autovalores do Laplaciano
    H_spectral = -Σ λ_i log(λ_i)
    
    Onde λ_i são os autovalores normalizados do Laplaciano
    
    Vantagens:
    - Captura estrutura GLOBAL da rede
    - Sensível a connectivity, clustering, modularity
    - Complementar à Shannon (local)
    """
    # Get largest connected component
    if not nx.is_connected(G):
        components = list(nx.connected_components(G))
        largest_cc = max(components, key=len)
        G = G.subgraph(largest_cc).copy()
    
    if G.number_of_nodes() < 2:
        return 0.0
    
    # Compute normalized Laplacian
    L = nx.normalized_laplacian_matrix(G).toarray()
    
    # Eigenvalues
    eigenvalues = linalg.eigvalsh(L)
    
    # Normalize (sum to 1)
    # Some eigenvalues may be negative due to numerical errors, take abs
    eigenvalues = np.abs(eigenvalues)
    eigenvalues = eigenvalues / eigenvalues.sum()
    
    # Spectral entropy
    # Remove zeros
    eigenvalues = eigenvalues[eigenvalues > 1e-10]
    
    H_spectral = -np.sum(eigenvalues * np.log2(eigenvalues + 1e-10))
    
    return H_spectral


def compute_von_neumann_entropy(G):
    """
    Von Neumann Entropy (quantum-inspired)
    H_vn = -Tr(ρ log(ρ))
    
    Onde ρ é a densidade de probabilidade derivada do Laplaciano
    
    Similar à espectral mas com normalização diferente
    """
    if not nx.is_connected(G):
        components = list(nx.connected_components(G))
        largest_cc = max(components, key=len)
        G = G.subgraph(largest_cc).copy()
    
    if G.number_of_nodes() < 2:
        return 0.0
    
    # Laplacian matrix
    L = nx.laplacian_matrix(G).toarray()
    
    # Normalize by trace to get density matrix
    trace = np.trace(L)
    if trace <= 0:
        return 0.0
    
    rho = L / trace
    
    # Eigenvalues of density matrix
    eigenvalues = linalg.eigvalsh(rho)
    eigenvalues = np.abs(eigenvalues)
    eigenvalues = eigenvalues[eigenvalues > 1e-10]
    
    # Von Neumann entropy
    H_vn = -np.sum(eigenvalues * np.log2(eigenvalues + 1e-10))
    
    return H_vn

# ============================================================================
# LOAD NETWORKS AND COMPARE
# ============================================================================

print("LOADING SEMANTIC NETWORKS")
print("-"*70)
print()

# Load our SWOW networks
networks = {}
languages = ['spanish', 'english', 'chinese']

for lang in languages:
    edge_file = f'data/processed/{lang}_edges.csv'
    if Path(edge_file).exists():
        df_edges = pd.read_csv(edge_file)
        G = nx.Graph()
        
        for _, row in df_edges.iterrows():
            weight = row.get('strength', 1.0) if 'strength' in df_edges.columns else 1.0
            G.add_edge(row['source'], row['target'], weight=weight)
        
        networks[lang] = G
        print(f"✅ {lang}: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

print()

# Also load depression networks (if available)
depression_levels = ['minimum', 'mild', 'moderate', 'severe']
for level in depression_levels:
    edge_file = f'data/processed/depression_networks/depression_{level}_edges.csv'
    if Path(edge_file).exists():
        df_edges = pd.read_csv(edge_file)
        G = nx.Graph()
        
        for _, row in df_edges.iterrows():
            G.add_edge(row['source'], row['target'], weight=row.get('weight', 1.0))
        
        networks[f'depression_{level}'] = G
        print(f"✅ depression_{level}: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

print()

# ============================================================================
# COMPUTE ALL ENTROPY TYPES
# ============================================================================

print("="*70)
print("COMPUTING ALL ENTROPY TYPES")
print("="*70)
print()

results = []

for name, G in networks.items():
    print(f"\n{name.upper()}:")
    print("-"*70)
    
    # Shannon (transition)
    H_shannon_trans = compute_shannon_entropy_transition(G)
    print(f"  Shannon (transition): {H_shannon_trans:.4f}")
    
    # Shannon (degree)
    H_shannon_deg = compute_shannon_entropy_degree(G)
    print(f"  Shannon (degree):     {H_shannon_deg:.4f}")
    
    # Spectral
    H_spectral = compute_spectral_entropy(G)
    print(f"  Spectral:             {H_spectral:.4f}")
    
    # Von Neumann
    H_von_neumann = compute_von_neumann_entropy(G)
    print(f"  Von Neumann:          {H_von_neumann:.4f}")
    
    # Also compute clustering for reference
    C = nx.average_clustering(G, weight='weight')
    
    # Number of components (fragmentation)
    n_components = nx.number_connected_components(G)
    
    results.append({
        'network': name,
        'n_nodes': G.number_of_nodes(),
        'n_edges': G.number_of_edges(),
        'clustering': C,
        'n_components': n_components,
        'H_shannon_transition': H_shannon_trans,
        'H_shannon_degree': H_shannon_deg,
        'H_spectral': H_spectral,
        'H_von_neumann': H_von_neumann
    })

print()

# ============================================================================
# SAVE RESULTS
# ============================================================================

df_results = pd.DataFrame(results)
df_results.to_csv('results/entropy_comparison_shannon_vs_spectral.csv', index=False)

print("="*70)
print("RESULTS SUMMARY")
print("="*70)
print()
print(df_results[['network', 'clustering', 'H_shannon_transition', 'H_spectral']].to_string(index=False))
print()

# ============================================================================
# ANALYSIS: WHICH ENTROPY IS BETTER?
# ============================================================================

print("="*70)
print("ANALYSIS: WHICH ENTROPY DETECTS PATHOLOGY BETTER?")
print("="*70)
print()

# Check depression severity progression
depression_rows = df_results[df_results['network'].str.contains('depression', na=False)]

if len(depression_rows) > 0:
    print("DEPRESSION SEVERITY PROGRESSION:")
    print()
    
    severity_order = ['depression_minimum', 'depression_mild', 'depression_moderate', 'depression_severe']
    depression_ordered = depression_rows.set_index('network').reindex(severity_order).reset_index()
    
    print("Shannon (transition):")
    for _, row in depression_ordered.iterrows():
        print(f"  {row['network']:25s}: {row['H_shannon_transition']:.4f}")
    
    print("\nShannon (degree):")
    for _, row in depression_ordered.iterrows():
        print(f"  {row['network']:25s}: {row['H_shannon_degree']:.4f}")
    
    print("\nSpectral:")
    for _, row in depression_ordered.iterrows():
        print(f"  {row['network']:25s}: {row['H_spectral']:.4f}")
    
    print("\nVon Neumann:")
    for _, row in depression_ordered.iterrows():
        print(f"  {row['network']:25s}: {row['H_von_neumann']:.4f}")
    
    print()
    
    # Check correlation with severity
    severity_numeric = [0, 1, 2, 3]  # minimum=0, mild=1, moderate=2, severe=3
    
    from scipy.stats import spearmanr
    
    print("CORRELATION WITH SEVERITY (Spearman's ρ):")
    print()
    
    corr_shannon_trans, p_shannon_trans = spearmanr(severity_numeric, depression_ordered['H_shannon_transition'])
    corr_shannon_deg, p_shannon_deg = spearmanr(severity_numeric, depression_ordered['H_shannon_degree'])
    corr_spectral, p_spectral = spearmanr(severity_numeric, depression_ordered['H_spectral'])
    corr_von_neumann, p_von_neumann = spearmanr(severity_numeric, depression_ordered['H_von_neumann'])
    
    print(f"  Shannon (transition): ρ = {corr_shannon_trans:+.3f}, p = {p_shannon_trans:.4f}")
    print(f"  Shannon (degree):     ρ = {corr_shannon_deg:+.3f}, p = {p_shannon_deg:.4f}")
    print(f"  Spectral:             ρ = {corr_spectral:+.3f}, p = {p_spectral:.4f}")
    print(f"  Von Neumann:          ρ = {corr_von_neumann:+.3f}, p = {p_von_neumann:.4f}")
    
    print()
    
    # Find best
    correlations = {
        'Shannon (transition)': abs(corr_shannon_trans),
        'Shannon (degree)': abs(corr_shannon_deg),
        'Spectral': abs(corr_spectral),
        'Von Neumann': abs(corr_von_neumann)
    }
    
    best_entropy = max(correlations.items(), key=lambda x: x[1])
    
    print(f"🏆 BEST ENTROPY FOR SEVERITY DETECTION:")
    print(f"   {best_entropy[0]}: |ρ| = {best_entropy[1]:.3f}")

print()

# Save with correlation results
with open('results/entropy_comparison_with_correlations.json', 'w') as f:
    output = {
        'all_networks': results,
        'depression_analysis': {
            'correlations': {
                'shannon_transition': {'rho': float(corr_shannon_trans), 'p': float(p_shannon_trans)},
                'shannon_degree': {'rho': float(corr_shannon_deg), 'p': float(p_shannon_deg)},
                'spectral': {'rho': float(corr_spectral), 'p': float(p_spectral)},
                'von_neumann': {'rho': float(corr_von_neumann), 'p': float(p_von_neumann)}
            },
            'best': best_entropy[0]
        } if len(depression_rows) > 0 else {}
    }
    json.dump(output, f, indent=2)

print("="*70)
print("✅ ENTROPY COMPARISON COMPLETE!")
print("="*70)
print()
print("Files saved:")
print("  - results/entropy_comparison_shannon_vs_spectral.csv")
print("  - results/entropy_comparison_with_correlations.json")

