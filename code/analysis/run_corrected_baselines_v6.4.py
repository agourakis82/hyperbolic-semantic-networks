"""
Corrected Baseline Comparison - v6.4.0

Corrige problemas identificados:
1. ER: verificar p, componentes, distribuição
2. BA: testar m adequado para igualar edges (~800)
3. Comparação válida com SWOW
"""
import networkx as nx
import numpy as np
from pathlib import Path
import json
from GraphRicciCurvature.OllivierRicci import OllivierRicci
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("CORRECTED BASELINE COMPARISON - v6.4.0")
print("=" * 70)

# Config (match SWOW)
N_NODES = 500
N_EDGES_TARGET = 800
ALPHA = 0.5

np.random.seed(42)

results = {}

# Baseline 1: Erdős-Rényi (CORRECTED)
print(f"\n{'=' * 70}")
print("BASELINE 1: ERDŐS-RÉNYI (CORRECTED)")
print(f"{'=' * 70}")

try:
    # CORRECTION: Ensure proper p calculation
    p = (2 * N_EDGES_TARGET) / (N_NODES * (N_NODES - 1))
    print(f"Probability p = {p:.6f}")
    print(f"Expected edges = {p * N_NODES * (N_NODES - 1) / 2:.0f}")
    
    # Generate multiple times to get close to target
    best_G = None
    best_diff = float('inf')
    
    for attempt in range(10):
        G_temp = nx.erdos_renyi_graph(N_NODES, p, seed=42+attempt)
        
        # Ensure connected
        if not nx.is_connected(G_temp):
            largest_cc = max(nx.connected_components(G_temp), key=len)
            G_temp = G_temp.subgraph(largest_cc).copy()
        
        diff = abs(G_temp.number_of_edges() - N_EDGES_TARGET)
        if diff < best_diff:
            best_diff = diff
            best_G = G_temp
            if diff < 50:  # Close enough
                break
    
    G_random = best_G
    
    print(f"\nNetwork: {G_random.number_of_nodes()} nodes, {G_random.number_of_edges()} edges")
    print(f"Difference from target: {G_random.number_of_edges() - N_EDGES_TARGET:+d} edges")
    
    # Check degree distribution
    degrees_random = [G_random.degree(n) for n in G_random.nodes()]
    mean_deg = np.mean(degrees_random)
    expected_mean = (2 * G_random.number_of_edges()) / G_random.number_of_nodes()
    
    print(f"\nDegree statistics:")
    print(f"  Mean: {mean_deg:.2f} (expected: {expected_mean:.2f})")
    print(f"  Std: {np.std(degrees_random):.2f}")
    print(f"  Range: [{np.min(degrees_random)}, {np.max(degrees_random)}]")
    
    # Check if Poisson (characteristic of ER)
    # ER should have Poisson degree distribution: P(k) ~ λ^k * e^(-λ) / k!
    # where λ = mean degree
    
    print("\nComputing Ollivier-Ricci curvature...")
    orc_random = OllivierRicci(G_random, alpha=ALPHA, verbose="ERROR")
    orc_random.compute_ricci_curvature()
    G_random_orc = orc_random.G
    
    curv_random = [G_random_orc[u][v]['ricciCurvature'] for u, v in G_random_orc.edges()]
    mean_random = np.mean(curv_random)
    std_random = np.std(curv_random)
    
    print(f"\n✓ Results:")
    print(f"  Mean: {mean_random:.6f}")
    print(f"  Std: {std_random:.6f}")
    print(f"  Range: [{np.min(curv_random):.3f}, {np.max(curv_random):.3f}]")
    
    # Literature check: ER should be ~0
    if abs(mean_random) < 0.1:
        print(f"  ✅ Mean ≈ 0 (as expected for ER)")
    elif mean_random < -0.1:
        print(f"  ⚠️  Mean < -0.1 (unexpectedly negative)")
    else:
        print(f"  ⚠️  Mean > +0.1 (unexpectedly positive)")
    
    results['random_corrected'] = {
        'n_nodes': G_random.number_of_nodes(),
        'n_edges': G_random.number_of_edges(),
        'target_edges': N_EDGES_TARGET,
        'probability_p': float(p),
        'degree_mean': float(np.mean(degrees_random)),
        'degree_std': float(np.std(degrees_random)),
        'curvature_mean': float(mean_random),
        'curvature_std': float(std_random),
        'curvature_min': float(np.min(curv_random)),
        'curvature_max': float(np.max(curv_random)),
        'curvature_values': [float(c) for c in curv_random],
        'success': True
    }
except Exception as e:
    print(f"❌ Error: {e}")
    results['random_corrected'] = {'error': str(e), 'success': False}

# Baseline 2: Lattice (keep same)
print(f"\n{'=' * 70}")
print("BASELINE 2: LATTICE (unchanged from v6.3)")
print(f"{'=' * 70}")

try:
    grid_size = int(np.sqrt(N_NODES))
    G_lattice = nx.grid_2d_graph(grid_size, grid_size)
    G_lattice = nx.convert_node_labels_to_integers(G_lattice)
    
    print(f"Network: {G_lattice.number_of_nodes()} nodes, {G_lattice.number_of_edges()} edges")
    
    print("Computing Ollivier-Ricci curvature...")
    orc_lattice = OllivierRicci(G_lattice, alpha=ALPHA, verbose="ERROR")
    orc_lattice.compute_ricci_curvature()
    G_lattice_orc = orc_lattice.G
    
    curv_lattice = [G_lattice_orc[u][v]['ricciCurvature'] for u, v in G_lattice_orc.edges()]
    mean_lattice = np.mean(curv_lattice)
    
    print(f"\n✓ Results:")
    print(f"  Mean: {mean_lattice:.6f}")
    
    results['lattice'] = {
        'n_nodes': G_lattice.number_of_nodes(),
        'n_edges': G_lattice.number_of_edges(),
        'curvature_mean': float(mean_lattice),
        'curvature_std': float(np.std(curv_lattice)),
        'curvature_values': [float(c) for c in curv_lattice],
        'success': True
    }
except Exception as e:
    print(f"❌ Error: {e}")
    results['lattice'] = {'error': str(e), 'success': False}

# Baseline 3: Barabási-Albert (CORRECTED)
print(f"\n{'=' * 70}")
print("BASELINE 3: BARABÁSI-ALBERT (CORRECTED)")
print(f"={'=' * 70}")

print(f"\nTesting different m values to match ~{N_EDGES_TARGET} edges...")

ba_results = {}

for m in [1, 2, 3, 5]:
    print(f"\n--- Testing m={m} ---")
    
    try:
        G_ba = nx.barabasi_albert_graph(N_NODES, m, seed=42)
        n_edges = G_ba.number_of_edges()
        
        print(f"  Edges: {n_edges} (target: {N_EDGES_TARGET})")
        
        # Only compute curvature if reasonable number of edges
        if n_edges >= 400:
            print(f"  Computing Ollivier-Ricci curvature...")
            orc_ba = OllivierRicci(G_ba, alpha=ALPHA, verbose="ERROR")
            orc_ba.compute_ricci_curvature()
            G_ba_orc = orc_ba.G
            
            curv_ba = [G_ba_orc[u][v]['ricciCurvature'] for u, v in G_ba_orc.edges()]
            mean_ba = np.mean(curv_ba)
            
            print(f"  Mean curvature: {mean_ba:.6f}")
            
            ba_results[m] = {
                'n_edges': n_edges,
                'curvature_mean': float(mean_ba),
                'curvature_std': float(np.std(curv_ba)),
                'curvature_values': [float(c) for c in curv_ba],
                'hyperbolic': bool(mean_ba < -0.1)
            }
        else:
            print(f"  Skipping (too few edges)")
            ba_results[m] = {'n_edges': n_edges, 'skipped': True}
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        ba_results[m] = {'error': str(e)}

# Select best m (closest to target)
best_m = min([m for m in ba_results.keys() if 'curvature_mean' in ba_results[m]], 
             key=lambda m: abs(ba_results[m]['n_edges'] - N_EDGES_TARGET))

print(f"\n{'=' * 70}")
print(f"SELECTED: m={best_m} (closest to target)")
print(f"{'=' * 70}")

results['scalefree_corrected'] = {
    'n_nodes': N_NODES,
    'selected_m': int(best_m),
    **ba_results[best_m],
    'all_m_tested': {str(k): v for k, v in ba_results.items()},
    'success': True
}

# Baseline 4: Small-world (keep same)
print(f"\n{'=' * 70}")
print("BASELINE 4: WATTS-STROGATZ (unchanged from v6.3)")
print(f"{'=' * 70}")

try:
    k = 4
    p_ws = 0.1
    G_smallworld = nx.watts_strogatz_graph(N_NODES, k, p_ws, seed=42)
    
    print(f"Network: {G_smallworld.number_of_nodes()} nodes, {G_smallworld.number_of_edges()} edges")
    
    print("Computing Ollivier-Ricci curvature...")
    orc_sw = OllivierRicci(G_smallworld, alpha=ALPHA, verbose="ERROR")
    orc_sw.compute_ricci_curvature()
    G_sw_orc = orc_sw.G
    
    curv_sw = [G_sw_orc[u][v]['ricciCurvature'] for u, v in G_sw_orc.edges()]
    mean_sw = np.mean(curv_sw)
    
    print(f"\n✓ Results:")
    print(f"  Mean: {mean_sw:.6f}")
    
    results['smallworld'] = {
        'n_nodes': G_smallworld.number_of_nodes(),
        'n_edges': G_smallworld.number_of_edges(),
        'curvature_mean': float(mean_sw),
        'curvature_std': float(np.std(curv_sw)),
        'curvature_values': [float(c) for c in curv_sw],
        'success': True
    }
except Exception as e:
    print(f"❌ Error: {e}")
    results['smallworld'] = {'error': str(e), 'success': False}

# Load SWOW for comparison
print(f"\n{'=' * 70}")
print("LOADING SWOW RESULTS")
print(f"{'=' * 70}")

try:
    with open('results/multilingual_curvature_analysis_v6.3.json', 'r') as f:
        swow_results = json.load(f)
    
    swow_means = {}
    for lang, res in swow_results.items():
        if res.get('success', False):
            swow_means[lang] = res['curvature_mean']
    
    swow_overall_mean = np.mean(list(swow_means.values()))
    print(f"\nSWOW Mean Curvature: {swow_overall_mean:.6f}")
    print(f"  (Average across {len(swow_means)} languages)")
    
except Exception as e:
    print(f"⚠️  Could not load SWOW results: {e}")
    swow_overall_mean = None

# Comparison
print(f"\n{'=' * 70}")
print("COMPARISON: CORRECTED vs ORIGINAL")
print(f"{'=' * 70}")

print(f"\n{'Network':<15} {'Version':<12} {'N Edges':<10} {'Mean Curv':<12}")
print("-" * 70)

if results['random_corrected']['success']:
    print(f"{'Random (ER)':<15} {'v6.4 (new)':<12} "
          f"{results['random_corrected']['n_edges']:<10} "
          f"{results['random_corrected']['curvature_mean']:<12.6f}")
    # Original from v6.3 was -0.349
    print(f"{'Random (ER)':<15} {'v6.3 (old)':<12} {'764':<10} {'-0.349':<12}")

if results['scalefree_corrected']['success']:
    m_sel = results['scalefree_corrected']['selected_m']
    print(f"{'Scale-free (BA)':<15} {'v6.4 (m={m_sel})':<12} "
          f"{results['scalefree_corrected']['n_edges']:<10} "
          f"{results['scalefree_corrected']['curvature_mean']:<12.6f}")
    # Original from v6.3 was +0.002 with 499 edges
    print(f"{'Scale-free (BA)':<15} {'v6.3 (m=1)':<12} {'499':<10} {'+0.002':<12}")

if swow_overall_mean is not None:
    print(f"{'SWOW':<15} {'(reference)':<12} {'~800':<10} {swow_overall_mean:<12.6f}")

# Interpretation
print(f"\n{'=' * 70}")
print("INTERPRETATION OF CORRECTIONS")
print(f"{'=' * 70}")

if results['random_corrected']['success']:
    old_er = -0.349
    new_er = results['random_corrected']['curvature_mean']
    print(f"\nRandom (ER):")
    print(f"  v6.3: {old_er:.3f} (suspicious)")
    print(f"  v6.4: {new_er:.3f} (corrected)")
    
    if abs(new_er) < abs(old_er):
        print(f"  ✅ Correction moved closer to zero (expected for ER)")
    else:
        print(f"  ⚠️  Still far from zero - may need further investigation")

if results['scalefree_corrected']['success']:
    old_ba = +0.002
    new_ba = results['scalefree_corrected']['curvature_mean']
    print(f"\nScale-free (BA):")
    print(f"  v6.3 (m=1, 499 edges): {old_ba:.3f}")
    print(f"  v6.4 (m={results['scalefree_corrected']['selected_m']}, "
          f"{results['scalefree_corrected']['n_edges']} edges): {new_ba:.3f}")
    
    if new_ba < -0.1:
        print(f"  ✅ Now shows hyperbolic geometry (as expected for scale-free)")
    elif new_ba < 0:
        print(f"  ⚠️  Slightly negative but not strongly hyperbolic")
    else:
        print(f"  ⚠️  Still non-negative - scale-free with high m may differ")

# Save results
output_path = 'results/baseline_correction_v6.4.json'
results_to_save = {}
for name, res in results.items():
    res_copy = res.copy()
    if 'curvature_values' in res_copy:
        res_copy['n_curvature_values'] = len(res_copy['curvature_values'])
        del res_copy['curvature_values']
    if 'all_m_tested' in res_copy:
        cleaned_m = {}
        for m, data in res_copy['all_m_tested'].items():
            data_copy = data.copy()
            if 'curvature_values' in data_copy:
                del data_copy['curvature_values']
            cleaned_m[m] = data_copy
        res_copy['all_m_tested'] = cleaned_m
    results_to_save[name] = res_copy

with open(output_path, 'w') as f:
    json.dump(results_to_save, f, indent=2)

print(f"\nResults saved to: {output_path}")

# Create comparison figure
if results['random_corrected']['success'] and results['scalefree_corrected']['success']:
    print(f"\nGenerating comparison figure...")
    Path('figures').mkdir(exist_ok=True)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot 1: v6.3 vs v6.4 comparison
    networks = ['ER v6.3', 'ER v6.4', 'BA v6.3', f'BA v6.4\n(m={results["scalefree_corrected"]["selected_m"]})']
    means = [-0.349, results['random_corrected']['curvature_mean'], 
             +0.002, results['scalefree_corrected']['curvature_mean']]
    colors = ['#ff9999', '#1f77b4', '#ffcc99', '#ff7f0e']
    
    if swow_overall_mean is not None:
        networks.append('SWOW')
        means.append(swow_overall_mean)
        colors.append('#2ca02c')
    
    x_pos = range(len(networks))
    bars = ax1.bar(x_pos, means, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    
    # Highlight changes
    bars[0].set_hatch('//')  # Old
    bars[2].set_hatch('//')  # Old
    
    ax1.axhline(0, color='k', linestyle=':', linewidth=1, alpha=0.5)
    ax1.axhline(-0.155, color='g', linestyle='--', linewidth=2, alpha=0.7, label='SWOW mean')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(networks, rotation=15, ha='right')
    ax1.set_ylabel('Ollivier-Ricci Curvature')
    ax1.set_title('Baseline Correction: v6.3 → v6.4', fontweight='bold', fontsize=12)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Plot 2: All corrected baselines
    successful = {k: v for k, v in results.items() if v.get('success', False) and 'curvature_mean' in v}
    
    if len(successful) >= 2:
        bp_data = [res['curvature_values'] for res in successful.values()]
        bp_labels = [k.replace('_corrected', '\n(corrected)').replace('_', ' ').title() 
                    for k in successful.keys()]
        
        if swow_overall_mean is not None:
            bp_labels.append('SWOW\n(reference)')
        
        bp = ax2.boxplot(bp_data, labels=bp_labels, patch_artist=True)
        colors_box = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        for patch, color in zip(bp['boxes'], colors_box):
            patch.set_facecolor(color)
        
        ax2.axhline(0, color='k', linestyle=':', linewidth=1, alpha=0.5)
        if swow_overall_mean is not None:
            ax2.axhline(swow_overall_mean, color='g', linestyle='--', linewidth=2, alpha=0.7)
        ax2.set_ylabel('Ollivier-Ricci Curvature')
        ax2.set_title('Corrected Baselines Distribution', fontweight='bold', fontsize=12)
        ax2.grid(axis='y', alpha=0.3)
        ax2.tick_params(axis='x', rotation=15)
    
    plt.tight_layout()
    plt.savefig('figures/corrected_baselines_comparison_v6.4.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Figure saved: figures/corrected_baselines_comparison_v6.4.png")

print(f"\n{'=' * 70}")
print("CORRECTED BASELINE COMPARISON COMPLETE!")
print(f"{'=' * 70}\n")

