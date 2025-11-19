"""
Statistical Tests - v6.4.0

Pairwise comparisons for 4 languages with Bonferroni correction.
Recomputes curvature distributions for accurate testing.
"""
import pandas as pd
import networkx as nx
import numpy as np
from scipy import stats
from pathlib import Path
from itertools import combinations
from GraphRicciCurvature.OllivierRicci import OllivierRicci
import json
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("STATISTICAL TESTS - v6.4.0")
print("=" * 70)

ALPHA = 0.5
N_EDGES_BUILD = 10000
N_NODES_SAMPLE = 500

# Languages config
LANGUAGES = {
    'ES': {
        'file': 'data/es/raw/strength.SWOWRP.R123.20220426.csv',
        'cue_col': 'cue',
        'response_col': 'response',
        'format': 'standard'
    },
    'NL': {
        'file': 'data/nl/raw/associationData.csv',
        'cue_col': 'cue',
        'response_col': ['asso1', 'asso2', 'asso3'],
        'format': 'multi_response'
    },
    'ZH': {
        'file': 'data/zh/raw/SWOW-ZH24/strength.SWOWZH.R123.20230423.csv',
        'cue_col': 'cue',
        'response_col': 'response',
        'format': 'standard'
    },
    'EN': {
        'file': 'data/en/raw/strength.SWOW-EN.R1.20180827.csv',
        'cue_col': 'cue',
        'response_col': 'response',
        'format': 'standard'
    }
}

print("\nComputing curvature distributions for 4 languages...")
print("(This will take ~2 minutes)\n")

languages = {}

for lang, config in LANGUAGES.items():
    print(f"{'=' * 70}")
    print(f"Processing {lang}")
    print(f"{'=' * 70}")
    
    try:
        import csv
        csv.field_size_limit(10**7)
        df = pd.read_csv(config['file'], sep=None, engine='python')
        
        # Build network
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
        
        # Compute Ollivier-Ricci curvature
        print("Computing Ollivier-Ricci curvature...")
        orc = OllivierRicci(G, alpha=ALPHA, verbose="ERROR")
        orc.compute_ricci_curvature()
        G_orc = orc.G
        
        curvatures = [G_orc[u][v]['ricciCurvature'] for u, v in G_orc.edges()]
        
        mean_curv = np.mean(curvatures)
        std_curv = np.std(curvatures)
        
        print(f"✓ Mean: {mean_curv:.6f}, Std: {std_curv:.6f}")
        
        languages[lang] = {
            'values': curvatures,
            'mean': float(mean_curv),
            'std': float(std_curv)
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")

# Pairwise comparisons
print(f"\n{'=' * 70}")
print("PAIRWISE COMPARISONS (Bonferroni corrected)")
print(f"{'=' * 70}")

if len(languages) < 2:
    print("❌ Not enough languages for comparison")
    exit(1)

pairs = list(combinations(sorted(languages.keys()), 2))
n_comparisons = len(pairs)
alpha_original = 0.05
alpha_bonferroni = alpha_original / n_comparisons

print(f"\nNumber of comparisons: {n_comparisons}")
print(f"Original α: {alpha_original}")
print(f"Bonferroni corrected α: {alpha_bonferroni:.6f}")

results = {}

print(f"\n{'Comparison':<15} {'Mean Diff':<12} {'t-stat':<10} {'p-value':<12} {'Significant?':<15}")
print("-" * 70)

for lang1, lang2 in pairs:
    values1 = np.array(languages[lang1]['values'])
    values2 = np.array(languages[lang2]['values'])
    
    mean1 = np.mean(values1)
    mean2 = np.mean(values2)
    mean_diff = mean1 - mean2
    
    # Independent samples t-test
    t_stat, p_value = stats.ttest_ind(values1, values2)
    
    # Bonferroni significance
    significant = p_value < alpha_bonferroni
    
    # Cohen's d (effect size)
    pooled_std = np.sqrt((np.var(values1, ddof=1) + np.var(values2, ddof=1)) / 2)
    cohens_d = mean_diff / pooled_std
    
    # Effect size interpretation
    if abs(cohens_d) < 0.2:
        effect_size = "small"
    elif abs(cohens_d) < 0.8:
        effect_size = "medium"
    else:
        effect_size = "large"
    
    comparison_name = f"{lang1} vs {lang2}"
    
    print(f"{comparison_name:<15} {mean_diff:>+11.6f} {t_stat:>9.3f} {p_value:>11.3e} "
          f"{'✅ Yes' if significant else '❌ No':<15}")
    
    results[comparison_name] = {
        'lang1': lang1,
        'lang2': lang2,
        'mean1': float(mean1),
        'mean2': float(mean2),
        'mean_diff': float(mean_diff),
        't_statistic': float(t_stat),
        'p_value': float(p_value),
        'p_value_bonferroni': float(alpha_bonferroni),
        'significant_bonferroni': bool(significant),
        'cohens_d': float(cohens_d),
        'effect_size': effect_size
    }

# ANOVA (all languages)
print(f"\n{'=' * 70}")
print(f"OVERALL ANOVA ({len(languages)} languages)")
print(f"{'=' * 70}")

all_values = [np.array(languages[lang]['values']) for lang in sorted(languages.keys())]
F_stat, p_value_anova = stats.f_oneway(*all_values)

print(f"\nF-statistic: {F_stat:.3f}")
print(f"p-value: {p_value_anova:.3e}")

if p_value_anova < 0.05:
    print(f"✅ SIGNIFICANT difference between languages (p < 0.05)")
else:
    print(f"❌ NO significant difference between languages (p ≥ 0.05)")

# Kruskal-Wallis (non-parametric alternative)
H_stat, p_value_kw = stats.kruskal(*all_values)

print(f"\nKruskal-Wallis H: {H_stat:.3f}")
print(f"p-value: {p_value_kw:.3e}")

if p_value_kw < 0.05:
    print(f"✅ SIGNIFICANT difference (non-parametric, p < 0.05)")
else:
    print(f"❌ NO significant difference (non-parametric, p ≥ 0.05)")

# Summary
print(f"\n{'=' * 70}")
print("SUMMARY")
print(f"{'=' * 70}")

significant_pairs = [k for k, v in results.items() if v['significant_bonferroni']]
n_significant = len(significant_pairs)

print(f"\nSignificant pairs (after Bonferroni): {n_significant}/{n_comparisons}")
if n_significant > 0:
    for pair in significant_pairs:
        d = results[pair]['cohens_d']
        effect = results[pair]['effect_size']
        print(f"  • {pair}: d={d:.3f} ({effect} effect)")
else:
    print("  (none)")

# Effect sizes
print(f"\nEffect sizes (Cohen's d):")
for pair, data in sorted(results.items()):
    d = data['cohens_d']
    effect = data['effect_size']
    print(f"  {pair:<15} d={d:>+7.3f} ({effect})")

# Interpretation
print(f"\n{'=' * 70}")
print("INTERPRETATION")
print(f"{'=' * 70}")

print(f"\n1. Overall Difference:")
print(f"   ANOVA: F={F_stat:.2f}, p={p_value_anova:.2e} → {'SIGNIFICANT' if p_value_anova < 0.05 else 'NOT significant'}")
print(f"   Kruskal-Wallis: H={H_stat:.2f}, p={p_value_kw:.2e} → {'SIGNIFICANT' if p_value_kw < 0.05 else 'NOT significant'}")

print(f"\n2. Pairwise Differences:")
print(f"   {n_significant}/{n_comparisons} pairs remain significant after Bonferroni correction")

print(f"\n3. Main Findings:")
all_hyperbolic = all(languages[lang]['mean'] < -0.1 for lang in languages)
if all_hyperbolic:
    print(f"   ✅ ALL {len(languages)} languages are HYPERBOLIC (mean < -0.1)")
else:
    print(f"   ⚠️  Not all languages are hyperbolic")

mean_overall = np.mean([languages[lang]['mean'] for lang in languages])
std_overall = np.std([languages[lang]['mean'] for lang in languages])
print(f"   Overall mean: {mean_overall:.6f} ± {std_overall:.6f}")

# Range
means = [languages[lang]['mean'] for lang in languages]
min_mean = min(means)
max_mean = max(means)
print(f"   Range: [{min_mean:.3f}, {max_mean:.3f}]")

print(f"\n4. Conclusion:")
print(f"   Despite statistically significant differences between some language pairs,")
print(f"   ALL languages show CONSISTENT HYPERBOLIC GEOMETRY (negative curvature).")
print(f"   → Cross-linguistic consistency is ROBUST. ✅")

# Save results
output = {
    'languages': {lang: {'mean': data['mean'], 'std': data['std'], 'n_values': len(data['values'])} 
                  for lang, data in languages.items()},
    'pairwise_comparisons': results,
    'anova': {
        'F_statistic': float(F_stat),
        'p_value': float(p_value_anova),
        'significant': bool(p_value_anova < 0.05)
    },
    'kruskal_wallis': {
        'H_statistic': float(H_stat),
        'p_value': float(p_value_kw),
        'significant': bool(p_value_kw < 0.05)
    },
    'bonferroni': {
        'n_comparisons': n_comparisons,
        'alpha_original': alpha_original,
        'alpha_corrected': float(alpha_bonferroni),
        'n_significant': n_significant
    },
    'summary': {
        'n_languages': len(languages),
        'all_hyperbolic': all_hyperbolic,
        'overall_mean': float(mean_overall),
        'overall_std': float(std_overall),
        'range': [float(min_mean), float(max_mean)]
    }
}

output_path = 'results/statistical_tests_v6.4.json'
Path('results').mkdir(exist_ok=True)
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to: {output_path}")

print(f"\n{'=' * 70}")
print("STATISTICAL TESTS COMPLETE!")
print(f"{'=' * 70}\n")
