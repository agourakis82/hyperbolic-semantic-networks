"""
Robustness Analysis - v6.4.0

1. Bootstrap (50 iterations, reduzido por tempo)
2. Network sizes (250, 500, 750 nodes)
3. Confidence intervals
"""
import pandas as pd
import networkx as nx
import numpy as np
from pathlib import Path
import json
from GraphRicciCurvature.OllivierRicci import OllivierRicci
import matplotlib.pyplot as plt
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("ROBUSTNESS ANALYSIS - v6.4.0")
print("=" * 70)

ALPHA = 0.5
N_BOOTSTRAP = 50  # Reduced from 100 for time
NETWORK_SIZES = [250, 500, 750]

# Use Spanish as example (most complete data)
filepath = 'data/es/raw/strength.SWOWRP.R123.20220426.csv'

results = {}

# Part 1: Bootstrap Analysis
print(f"\n{'=' * 70}")
print(f"PART 1: BOOTSTRAP ANALYSIS ({N_BOOTSTRAP} iterations)")
print(f"{'=' * 70}")

try:
    import csv
    csv.field_size_limit(10**7)
    df = pd.read_csv(filepath, sep=None, engine='python')
    
    # Build full network
    N_EDGES_BUILD = 10000
    df_build = df.head(N_EDGES_BUILD)
    G_full = nx.from_pandas_edgelist(df_build, source='cue', target='response', create_using=nx.Graph())
    
    if not nx.is_connected(G_full):
        largest_cc = max(nx.connected_components(G_full), key=len)
        G_full = G_full.subgraph(largest_cc).copy()
    
    print(f"Full network: {G_full.number_of_nodes()} nodes, {G_full.number_of_edges()} edges")
    
    bootstrap_means = []
    N_NODES_SAMPLE = 500
    
    print(f"\nSampling {N_BOOTSTRAP} different 500-node subgraphs...")
    
    for i in tqdm(range(N_BOOTSTRAP), desc="Bootstrap"):
        try:
            # Random walk sampling with different seed
            import random
            random.seed(42 + i)
            
            start_node = random.choice(list(G_full.nodes()))
            sampled_nodes = {start_node}
            current_nodes = [start_node]
            
            while len(sampled_nodes) < N_NODES_SAMPLE and current_nodes:
                current = current_nodes.pop(0)
                neighbors = list(G_full.neighbors(current))
                random.shuffle(neighbors)
                for neighbor in neighbors:
                    if neighbor not in sampled_nodes:
                        sampled_nodes.add(neighbor)
                        current_nodes.append(neighbor)
                        if len(sampled_nodes) >= N_NODES_SAMPLE:
                            break
            
            G_sample = G_full.subgraph(sampled_nodes).copy()
            
            # Compute curvature
            orc = OllivierRicci(G_sample, alpha=ALPHA, verbose="ERROR")
            orc.compute_ricci_curvature()
            G_orc = orc.G
            
            curvatures = [G_orc[u][v]['ricciCurvature'] for u, v in G_orc.edges()]
            mean_curv = np.mean(curvatures)
            bootstrap_means.append(mean_curv)
            
        except Exception as e:
            print(f"\n  Warning: iteration {i} failed: {e}")
            continue
    
    # Calculate statistics
    bootstrap_means = np.array(bootstrap_means)
    mean_bootstrap = np.mean(bootstrap_means)
    std_bootstrap = np.std(bootstrap_means)
    ci_lower = np.percentile(bootstrap_means, 2.5)
    ci_upper = np.percentile(bootstrap_means, 97.5)
    
    print(f"\n✓ Bootstrap Results (N={len(bootstrap_means)}):")
    print(f"  Mean: {mean_bootstrap:.6f}")
    print(f"  Std: {std_bootstrap:.6f}")
    print(f"  95% CI: [{ci_lower:.6f}, {ci_upper:.6f}]")
    
    # Check stability
    cv = (std_bootstrap / abs(mean_bootstrap)) * 100  # Coefficient of variation
    print(f"  Coefficient of Variation: {cv:.2f}%")
    
    if cv < 20:
        print(f"  ✅ STABLE (CV < 20%)")
    elif cv < 50:
        print(f"  ⚠️  MODERATE stability (20% ≤ CV < 50%)")
    else:
        print(f"  ❌ UNSTABLE (CV ≥ 50%)")
    
    results['bootstrap'] = {
        'n_iterations': len(bootstrap_means),
        'mean': float(mean_bootstrap),
        'std': float(std_bootstrap),
        'ci_lower': float(ci_lower),
        'ci_upper': float(ci_upper),
        'cv_percent': float(cv),
        'stable': bool(cv < 20),
        'all_means': bootstrap_means.tolist(),
        'success': True
    }
    
except Exception as e:
    print(f"❌ Bootstrap analysis failed: {e}")
    results['bootstrap'] = {'error': str(e), 'success': False}

# Part 2: Network Size Analysis
print(f"\n{'=' * 70}")
print(f"PART 2: NETWORK SIZE ANALYSIS")
print(f"{'=' * 70}")

size_results = {}

for size in NETWORK_SIZES:
    print(f"\n--- Testing size={size} nodes ---")
    
    try:
        # Sample subgraph
        if G_full.number_of_nodes() > size:
            import random
            random.seed(42)
            start_node = random.choice(list(G_full.nodes()))
            sampled_nodes = {start_node}
            current_nodes = [start_node]
            
            while len(sampled_nodes) < size and current_nodes:
                current = current_nodes.pop(0)
                neighbors = list(G_full.neighbors(current))
                for neighbor in neighbors:
                    if neighbor not in sampled_nodes:
                        sampled_nodes.add(neighbor)
                        current_nodes.append(neighbor)
                        if len(sampled_nodes) >= size:
                            break
            
            G_size = G_full.subgraph(sampled_nodes).copy()
        else:
            G_size = G_full
        
        print(f"  Network: {G_size.number_of_nodes()} nodes, {G_size.number_of_edges()} edges")
        
        # Compute curvature
        print(f"  Computing curvature...")
        orc = OllivierRicci(G_size, alpha=ALPHA, verbose="ERROR")
        orc.compute_ricci_curvature()
        G_orc = orc.G
        
        curvatures = [G_orc[u][v]['ricciCurvature'] for u, v in G_orc.edges()]
        mean_curv = np.mean(curvatures)
        
        print(f"  Mean curvature: {mean_curv:.6f}")
        
        size_results[size] = {
            'n_nodes': G_size.number_of_nodes(),
            'n_edges': G_size.number_of_edges(),
            'curvature_mean': float(mean_curv),
            'curvature_std': float(np.std(curvatures)),
            'success': True
        }
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        size_results[size] = {'error': str(e), 'success': False}

# Check convergence
successful_sizes = {k: v for k, v in size_results.items() if v.get('success', False)}
if len(successful_sizes) >= 2:
    sizes_sorted = sorted(successful_sizes.keys())
    means_sorted = [successful_sizes[s]['curvature_mean'] for s in sizes_sorted]
    
    print(f"\n{'=' * 70}")
    print("CONVERGENCE ANALYSIS")
    print(f"{'=' * 70}")
    
    print(f"\n{'Size':<10} {'Nodes':<10} {'Edges':<10} {'Mean Curv':<12}")
    print("-" * 70)
    for size in sizes_sorted:
        res = successful_sizes[size]
        print(f"{size:<10} {res['n_nodes']:<10} {res['n_edges']:<10} {res['curvature_mean']:<12.6f}")
    
    # Check if converged (change < 5% from 500 to 750)
    if 500 in successful_sizes and 750 in successful_sizes:
        change_pct = abs((successful_sizes[750]['curvature_mean'] - successful_sizes[500]['curvature_mean']) 
                        / successful_sizes[500]['curvature_mean']) * 100
        
        print(f"\nChange 500→750: {change_pct:.2f}%")
        
        if change_pct < 5:
            print(f"  ✅ CONVERGED (change < 5%)")
        elif change_pct < 10:
            print(f"  ⚠️  NEAR convergence (5% ≤ change < 10%)")
        else:
            print(f"  ❌ NOT converged (change ≥ 10%)")

results['network_sizes'] = size_results

# Save results
output_path = 'results/robustness_analysis_v6.4.json'
Path('results').mkdir(exist_ok=True)

results_to_save = results.copy()
if 'bootstrap' in results_to_save and 'all_means' in results_to_save['bootstrap']:
    # Keep all_means for plotting
    pass

with open(output_path, 'w') as f:
    json.dump(results_to_save, f, indent=2)

print(f"\nResults saved to: {output_path}")

# Create figures
if results['bootstrap'].get('success', False):
    print(f"\nGenerating figures...")
    Path('figures').mkdir(exist_ok=True)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot 1: Bootstrap distribution
    bootstrap_means_arr = np.array(results['bootstrap']['all_means'])
    
    ax1.hist(bootstrap_means_arr, bins=20, color='#1f77b4', alpha=0.7, edgecolor='black')
    ax1.axvline(results['bootstrap']['mean'], color='r', linestyle='--', linewidth=2,
               label=f"Mean: {results['bootstrap']['mean']:.3f}")
    ax1.axvline(results['bootstrap']['ci_lower'], color='g', linestyle=':', linewidth=2,
               label=f"95% CI")
    ax1.axvline(results['bootstrap']['ci_upper'], color='g', linestyle=':', linewidth=2)
    ax1.set_xlabel('Mean Curvature')
    ax1.set_ylabel('Frequency')
    ax1.set_title(f'Bootstrap Distribution (N={results["bootstrap"]["n_iterations"]})',
                 fontweight='bold', fontsize=12)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Plot 2: Network size convergence
    if len(successful_sizes) >= 2:
        sizes_sorted = sorted(successful_sizes.keys())
        means_sorted = [successful_sizes[s]['curvature_mean'] for s in sizes_sorted]
        stds_sorted = [successful_sizes[s]['curvature_std'] for s in sizes_sorted]
        
        ax2.errorbar(sizes_sorted, means_sorted, yerr=stds_sorted, 
                    marker='o', markersize=10, capsize=10, linewidth=2,
                    color='#ff7f0e', label='Mean ± Std')
        ax2.axhline(0, color='k', linestyle=':', linewidth=1, alpha=0.5)
        ax2.set_xlabel('Network Size (nodes)')
        ax2.set_ylabel('Mean Curvature')
        ax2.set_title('Convergence with Network Size', fontweight='bold', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('figures/robustness_analysis_v6.4.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Figure saved: figures/robustness_analysis_v6.4.png")

print(f"\n{'=' * 70}")
print("ROBUSTNESS ANALYSIS COMPLETE!")
print(f"{'=' * 70}\n")

