#!/usr/bin/env python3
"""
WINDOW SCALING EXPERIMENT
Test hypothesis: Larger window compensates for sample size dilution effect
"""

import pandas as pd
import networkx as nx
import numpy as np
import re
from tqdm import tqdm
import json

print("="*70)
print("WINDOW SCALING EXPERIMENT")
print("Hypothesis: Larger window size compensates for dilution in large samples")
print("="*70)
print()

# Load data
df_full = pd.read_csv('data/external/Depression_Severity_Levels_Dataset/Depression_Severity_Levels_Dataset.csv')
df_moderate = df_full[df_full['label'] == 'moderate']

print(f"Total moderate posts: {len(df_moderate):,}")
print()

def build_network(texts, window_size=5, min_length=5):
    """Build co-occurrence network"""
    G = nx.Graph()
    for text in texts:
        if not isinstance(text, str):
            continue
        words = re.findall(rf'\b[a-z]{{{min_length},}}\b', text.lower())
        for i in range(len(words)):
            for j in range(i+1, min(i+window_size, len(words))):
                if words[i] != words[j]:
                    if G.has_edge(words[i], words[j]):
                        G[words[i]][words[j]]['weight'] += 1
                    else:
                        G.add_edge(words[i], words[j], weight=1)
    
    # Get LCC
    if G.number_of_nodes() > 0 and G.number_of_edges() > 0:
        components = list(nx.connected_components(G))
        largest_cc = max(components, key=len)
        return G.subgraph(largest_cc).copy()
    return G

# ============================================================================
# EXPERIMENT 1: FIXED n=2000, VARY WINDOW
# ============================================================================

print("="*70)
print("EXPERIMENT 1: n=2000, Variable Window Size")
print("="*70)
print()

sample_2000 = df_moderate.sample(n=2000, random_state=42)
texts_2000 = [t for t in sample_2000['text'].tolist() if isinstance(t, str)]

window_sizes = [3, 5, 7, 10, 15, 20, 30, 50]
results_window = []

for w in tqdm(window_sizes, desc="Testing window sizes"):
    G = build_network(texts_2000, window_size=w)
    
    if G.number_of_nodes() > 10:
        C = nx.average_clustering(G, weight='weight')
        density = nx.density(G)
        in_sweet_spot = 0.02 <= C <= 0.15
        
        results_window.append({
            'window_size': w,
            'nodes': G.number_of_nodes(),
            'edges': G.number_of_edges(),
            'clustering': C,
            'density': density,
            'in_sweet_spot': in_sweet_spot
        })
        
        print(f"  Window={w:2d}: N={G.number_of_nodes():5d}, E={G.number_of_edges():6d}, "
              f"C={C:.4f}, Sweet={'YES' if in_sweet_spot else 'NO'}")

print()

# Find optimal window for n=2000
df_window = pd.DataFrame(results_window)
optimal_windows = df_window[df_window['in_sweet_spot']]

if len(optimal_windows) > 0:
    print(f"✅ Window sizes that work for n=2000: {optimal_windows['window_size'].tolist()}")
    print(f"   Optimal window: {optimal_windows.iloc[0]['window_size']} (C={optimal_windows.iloc[0]['clustering']:.4f})")
else:
    print("❌ No window size brings n=2000 into sweet spot!")

print()

# ============================================================================
# EXPERIMENT 2: OPTIMAL WINDOW SCALING FUNCTION
# ============================================================================

print("="*70)
print("EXPERIMENT 2: Find Window Scaling Function")
print("="*70)
print()

sample_sizes = [100, 250, 500, 1000, 2000]
results_scaling = []

for n in tqdm(sample_sizes, desc="Testing sample sizes"):
    sample = df_moderate.sample(n=min(n, len(df_moderate)), random_state=42)
    texts = [t for t in sample['text'].tolist() if isinstance(t, str)]
    
    # Test multiple windows for each n
    for w in [5, 10, 15, 20, 30]:
        G = build_network(texts, window_size=w)
        
        if G.number_of_nodes() > 10:
            C = nx.average_clustering(G, weight='weight')
            in_sweet_spot = 0.02 <= C <= 0.15
            
            results_scaling.append({
                'n': n,
                'window': w,
                'nodes': G.number_of_nodes(),
                'clustering': C,
                'in_sweet_spot': in_sweet_spot
            })

df_scaling = pd.DataFrame(results_scaling)

print("\nResults by (n, window):")
print(df_scaling.pivot_table(index='window', columns='n', values='clustering'))
print()

# Find optimal window for each n
print("Optimal windows:")
for n in sample_sizes:
    df_n = df_scaling[df_scaling['n'] == n]
    optimal = df_n[df_n['in_sweet_spot']]
    
    if len(optimal) > 0:
        best = optimal.iloc[0]
        print(f"  n={n:4d}: window={best['window']:2d} → C={best['clustering']:.4f} ✅")
    else:
        print(f"  n={n:4d}: NO WINDOW WORKS ❌")

print()

# ============================================================================
# EXPERIMENT 3: THEORETICAL SCALING LAW
# ============================================================================

print("="*70)
print("EXPERIMENT 3: Theoretical Scaling Law")
print("="*70)
print()

print("Testing scaling functions:")
print()

# Try different scaling functions
scaling_functions = {
    'linear': lambda n: int(5 * (n / 250)),
    'sqrt': lambda n: int(5 * np.sqrt(n / 250)),
    'log': lambda n: int(5 * np.log(n / 250 + 1) + 5),
}

results_theory = []

for name, func in scaling_functions.items():
    print(f"\n{name.upper()} scaling: window(n) = {name}(n)")
    print("-"*70)
    
    for n in sample_sizes:
        w = func(n)
        w = max(3, min(w, 50))  # Bound between 3 and 50
        
        sample = df_moderate.sample(n=min(n, len(df_moderate)), random_state=42)
        texts = [t for t in sample['text'].tolist() if isinstance(t, str)]
        
        G = build_network(texts, window_size=w)
        
        if G.number_of_nodes() > 10:
            C = nx.average_clustering(G, weight='weight')
            in_sweet_spot = 0.02 <= C <= 0.15
            
            results_theory.append({
                'scaling': name,
                'n': n,
                'window': w,
                'clustering': C,
                'in_sweet_spot': in_sweet_spot
            })
            
            print(f"  n={n:4d} → w={w:2d}: C={C:.4f} {'✅' if in_sweet_spot else '❌'}")

print()

# ============================================================================
# SUMMARY & RECOMMENDATIONS
# ============================================================================

print("="*70)
print("SUMMARY & RECOMMENDATIONS")
print("="*70)
print()

# Best scaling function
df_theory = pd.DataFrame(results_theory)
success_rate = df_theory.groupby('scaling')['in_sweet_spot'].mean()

print("Success rate by scaling function:")
for scaling, rate in success_rate.items():
    print(f"  {scaling:10s}: {rate*100:5.1f}% in sweet spot")

print()

best_scaling = success_rate.idxmax()
print(f"✅ BEST SCALING: {best_scaling}")
print()

# Show recommended windows
print("Recommended windows by sample size:")
df_best = df_theory[df_theory['scaling'] == best_scaling]
for _, row in df_best.iterrows():
    status = "✅" if row['in_sweet_spot'] else "❌"
    print(f"  n={row['n']:4d} → window={row['window']:2d}  (C={row['clustering']:.4f}) {status}")

print()

# ============================================================================
# SAVE RESULTS
# ============================================================================

df_window.to_csv('results/window_scaling_experiment_fixed_n.csv', index=False)
df_scaling.to_csv('results/window_scaling_experiment_full.csv', index=False)
df_theory.to_csv('results/window_scaling_theory.csv', index=False)

results_summary = {
    'experiment': 'window_scaling',
    'date': '2025-11-06',
    'hypothesis': 'Larger window compensates for sample size dilution',
    'fixed_n_2000': results_window,
    'optimal_windows': df_scaling.to_dict('records'),
    'scaling_functions': {
        name: df_theory[df_theory['scaling'] == name].to_dict('records')
        for name in scaling_functions.keys()
    },
    'best_scaling': best_scaling,
    'success_rates': success_rate.to_dict()
}

with open('results/window_scaling_complete.json', 'w') as f:
    json.dump(results_summary, f, indent=2)

print("✅ Saved results:")
print("   - results/window_scaling_experiment_fixed_n.csv")
print("   - results/window_scaling_experiment_full.csv")
print("   - results/window_scaling_theory.csv")
print("   - results/window_scaling_complete.json")

print()
print("="*70)
print("✅ WINDOW SCALING EXPERIMENT COMPLETE!")
print("="*70)

