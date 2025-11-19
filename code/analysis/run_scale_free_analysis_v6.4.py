"""
Scale-Free Analysis - v6.4.0

Verifica se SWOW networks são scale-free (power-law degree distribution).
Crítico para interpretar geometria hiperbólica.
"""
import pandas as pd
import networkx as nx
import numpy as np
from pathlib import Path
import json
import matplotlib.pyplot as plt
import powerlaw
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("SCALE-FREE ANALYSIS - v6.4.0")
print("=" * 70)

# Config
N_EDGES_BUILD = 10000
N_NODES_SAMPLE = 500

# Languages
LANGUAGES = {
    'es': {
        'file': 'data/es/raw/strength.SWOWRP.R123.20220426.csv',
        'cue_col': 'cue',
        'response_col': 'response',
        'format': 'standard'
    },
    'nl': {
        'file': 'data/nl/raw/associationData.csv',
        'cue_col': 'cue',
        'response_col': ['asso1', 'asso2', 'asso3'],
        'format': 'multi_response'
    },
    'zh': {
        'file': 'data/zh/raw/SWOW-ZH24/strength.SWOWZH.R123.20230423.csv',
        'cue_col': 'cue',
        'response_col': 'response',
        'format': 'standard'
    }
}

results = {}

for lang, config in LANGUAGES.items():
    print(f"\n{'=' * 70}")
    print(f"ANALYZING {lang.upper()}")
    print(f"{'=' * 70}")
    
    try:
        # Load and build network (same as before)
        import csv
        csv.field_size_limit(10**7)
        df = pd.read_csv(config['file'], sep=None, engine='python')
        
        if config['format'] == 'standard':
            df_build = df.head(N_EDGES_BUILD)
            G_full = nx.from_pandas_edgelist(
                df_build, source=config['cue_col'], 
                target=config['response_col'], create_using=nx.Graph()
            )
        elif config['format'] == 'multi_response':
            edges_list = []
            for _, row in df.head(N_EDGES_BUILD * 3).iterrows():
                cue = row[config['cue_col']]
                for asso_col in config['response_col']:
                    if pd.notna(row[asso_col]):
                        edges_list.append({'source': cue, 'target': row[asso_col]})
                if len(edges_list) >= N_EDGES_BUILD:
                    break
            df_edges = pd.DataFrame(edges_list)
            G_full = nx.from_pandas_edgelist(
                df_edges, source='source', target='target', create_using=nx.Graph()
            )
        
        # Get largest connected component
        if not nx.is_connected(G_full):
            largest_cc = max(nx.connected_components(G_full), key=len)
            G_full = G_full.subgraph(largest_cc).copy()
        
        # Sample subgraph
        if G_full.number_of_nodes() > N_NODES_SAMPLE:
            import random
            random.seed(42)
            start_node = random.choice(list(G_full.nodes()))
            sampled_nodes = {start_node}
            current_nodes = [start_node]
            
            while len(sampled_nodes) < N_NODES_SAMPLE and current_nodes:
                current = current_nodes.pop(0)
                neighbors = list(G_full.neighbors(current))
                for neighbor in neighbors:
                    if neighbor not in sampled_nodes:
                        sampled_nodes.add(neighbor)
                        current_nodes.append(neighbor)
                        if len(sampled_nodes) >= N_NODES_SAMPLE:
                            break
            
            G = G_full.subgraph(sampled_nodes).copy()
        else:
            G = G_full
        
        print(f"Network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        
        # Get degree distribution
        degrees = [G.degree(n) for n in G.nodes()]
        degrees_array = np.array(degrees)
        
        print(f"\nDegree statistics:")
        print(f"  Mean: {np.mean(degrees):.2f}")
        print(f"  Median: {np.median(degrees):.2f}")
        print(f"  Std: {np.std(degrees):.2f}")
        print(f"  Min: {np.min(degrees)}")
        print(f"  Max: {np.max(degrees)}")
        
        # Power-law fit using powerlaw library
        print(f"\n1. Power-Law Fit...")
        
        fit = powerlaw.Fit(degrees, discrete=True, verbose=False)
        alpha = fit.alpha
        xmin = fit.xmin
        sigma = fit.sigma
        
        print(f"  α (exponent): {alpha:.3f} ± {sigma:.3f}")
        print(f"  x_min: {xmin}")
        
        # Expected for scale-free: α ∈ [2, 3]
        if 2.0 <= alpha <= 3.0:
            print(f"  ✅ α ∈ [2, 3] - CONSISTENT with scale-free!")
        else:
            print(f"  ⚠️  α outside [2, 3] - NOT typical scale-free")
        
        # Compare power-law vs exponential
        print(f"\n2. Power-Law vs Exponential...")
        
        R_exp, p_exp = fit.distribution_compare('power_law', 'exponential', normalized_ratio=True)
        
        print(f"  R (loglikelihood ratio): {R_exp:.3f}")
        print(f"  p-value: {p_exp:.4f}")
        
        if p_exp < 0.05:
            if R_exp > 0:
                print(f"  ✅ Power-law is SIGNIFICANTLY better (p<0.05)")
            else:
                print(f"  ❌ Exponential is SIGNIFICANTLY better (p<0.05)")
        else:
            print(f"  ○ No significant difference (p≥0.05)")
        
        # Compare power-law vs lognormal
        print(f"\n3. Power-Law vs Lognormal...")
        
        R_log, p_log = fit.distribution_compare('power_law', 'lognormal', normalized_ratio=True)
        
        print(f"  R (loglikelihood ratio): {R_log:.3f}")
        print(f"  p-value: {p_log:.4f}")
        
        if p_log < 0.05:
            if R_log > 0:
                print(f"  ✅ Power-law is SIGNIFICANTLY better (p<0.05)")
            else:
                print(f"  ⚠️  Lognormal is SIGNIFICANTLY better (p<0.05)")
        else:
            print(f"  ○ No significant difference (p≥0.05)")
        
        # Interpretation
        print(f"\n4. INTERPRETATION:")
        
        scale_free_score = 0
        if 2.0 <= alpha <= 3.0:
            scale_free_score += 1
            print(f"  • Exponent α in [2,3]: YES ✅")
        else:
            print(f"  • Exponent α in [2,3]: NO ❌")
        
        if p_exp < 0.05 and R_exp > 0:
            scale_free_score += 1
            print(f"  • Better than exponential: YES ✅")
        else:
            print(f"  • Better than exponential: NO/UNCLEAR ⚠️")
        
        if p_log >= 0.05 or (p_log < 0.05 and R_log > 0):
            scale_free_score += 1
            print(f"  • Competitive with lognormal: YES ✅")
        else:
            print(f"  • Competitive with lognormal: NO ⚠️")
        
        print(f"\n  Scale-Free Score: {scale_free_score}/3")
        
        if scale_free_score >= 2:
            verdict = "LIKELY SCALE-FREE"
            verdict_symbol = "⭐"
        elif scale_free_score == 1:
            verdict = "PARTIALLY SCALE-FREE"
            verdict_symbol = "⚠️"
        else:
            verdict = "NOT SCALE-FREE"
            verdict_symbol = "❌"
        
        print(f"  Verdict: {verdict_symbol} {verdict}")
        
        # Save results
        results[lang] = {
            'n_nodes': G.number_of_nodes(),
            'n_edges': G.number_of_edges(),
            'degree_mean': float(np.mean(degrees)),
            'degree_median': float(np.median(degrees)),
            'degree_std': float(np.std(degrees)),
            'degree_min': int(np.min(degrees)),
            'degree_max': int(np.max(degrees)),
            'powerlaw': {
                'alpha': float(alpha),
                'sigma': float(sigma),
                'xmin': int(xmin)
            },
            'comparison_exponential': {
                'R': float(R_exp),
                'p': float(p_exp),
                'better': bool(p_exp < 0.05 and R_exp > 0)
            },
            'comparison_lognormal': {
                'R': float(R_log),
                'p': float(p_log),
                'better': bool(p_log < 0.05 and R_log > 0),
                'competitive': bool(p_log >= 0.05 or (p_log < 0.05 and R_log > 0))
            },
            'scale_free_score': int(scale_free_score),
            'verdict': verdict,
            'degrees': degrees,  # For plotting
            'success': True
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        results[lang] = {'error': str(e), 'success': False}

# Summary
print(f"\n{'=' * 70}")
print("SUMMARY")
print(f"{'=' * 70}")

successful = {k: v for k, v in results.items() if v.get('success', False)}

print(f"\n{'Language':<10} {'α':<10} {'Score':<8} {'Verdict':<25}")
print("-" * 70)
for lang, res in successful.items():
    print(f"{lang.upper():<10} {res['powerlaw']['alpha']:<10.3f} "
          f"{res['scale_free_score']}/3{'':<4} {res['verdict']:<25}")

# Overall verdict
all_scale_free = all(res['scale_free_score'] >= 2 for res in successful.values())
some_scale_free = any(res['scale_free_score'] >= 2 for res in successful.values())

print(f"\n{'=' * 70}")
if all_scale_free:
    print("⭐⭐⭐ ALL networks are LIKELY SCALE-FREE")
    print("  → Supports interpretation: scale-free → hyperbolic")
elif some_scale_free:
    print("⚠️  MIXED results: some scale-free, some not")
    print("  → Scale-free hypothesis PARTIALLY supported")
else:
    print("❌ NO network is clearly scale-free")
    print("  → Scale-free hypothesis NOT supported")
    print("  → Hyperbolic geometry may have OTHER causes")

# Save results
output_path = 'results/scale_free_analysis_v6.4.json'
Path('results').mkdir(exist_ok=True)

results_to_save = {}
for lang, res in results.items():
    res_copy = res.copy()
    if 'degrees' in res_copy:
        res_copy['n_degrees'] = len(res_copy['degrees'])
        del res_copy['degrees']
    results_to_save[lang] = res_copy

with open(output_path, 'w') as f:
    json.dump(results_to_save, f, indent=2)

print(f"\nResults saved to: {output_path}")

# Create figures
if len(successful) >= 1:
    print(f"\nGenerating figures...")
    Path('figures').mkdir(exist_ok=True)
    
    n_langs = len(successful)
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    
    for idx, (lang, res) in enumerate(successful.items()):
        if idx < 4:
            ax = axes[idx]
            degrees = res['degrees']
            
            # Log-log plot (characteristic of power-law)
            degree_counts = np.bincount(degrees)
            degree_vals = np.arange(len(degree_counts))
            
            # Remove zeros
            mask = degree_counts > 0
            degree_vals_filtered = degree_vals[mask]
            degree_counts_filtered = degree_counts[mask]
            
            # Plot
            ax.scatter(degree_vals_filtered, degree_counts_filtered, 
                      alpha=0.6, s=50, color=colors[idx], label='Data')
            
            # Power-law fit line
            alpha = res['powerlaw']['alpha']
            xmin = res['powerlaw']['xmin']
            x_fit = np.logspace(np.log10(xmin), np.log10(max(degrees)), 50)
            y_fit = (x_fit ** (-alpha)) * (xmin ** alpha) * degree_counts_filtered[0]
            ax.plot(x_fit, y_fit, 'r--', linewidth=2, 
                   label=f'Power-law α={alpha:.2f}')
            
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.set_xlabel('Degree k')
            ax.set_ylabel('Count P(k)')
            ax.set_title(f"{lang.upper()}: {res['verdict']}", 
                        fontweight='bold', fontsize=11)
            ax.legend()
            ax.grid(True, alpha=0.3, which='both')
    
    # Hide unused subplots
    for idx in range(len(successful), 4):
        axes[idx].axis('off')
    
    plt.tight_layout()
    plt.savefig('figures/degree_distribution_powerlaw_v6.4.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Figure saved: figures/degree_distribution_powerlaw_v6.4.png")

print(f"\n{'=' * 70}")
print("SCALE-FREE ANALYSIS COMPLETE!")
print(f"{'=' * 70}\n")

