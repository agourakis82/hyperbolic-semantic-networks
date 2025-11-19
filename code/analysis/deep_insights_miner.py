#!/usr/bin/env python3
"""
Deep Insights Miner - MCTS Agent DATA_MINER
============================================
Mines existing structural null JSONs for unreported patterns and insights.

Searches for:
1. Distribution properties (skewness, kurtosis, outliers)
2. Cross-language patterns
3. Config vs. Triadic differences
4. Variance stability
5. Confidence interval widths
6. Novel correlations
"""

import json
import numpy as np
from pathlib import Path
from scipy import stats
import pandas as pd

# Paths
RESULTS_DIR = Path("/home/agourakis82/workspace/hyperbolic-semantic-networks/results/structural_nulls")

def load_all_results():
    """Load all 6 JSON result files."""
    results = {}
    for json_file in RESULTS_DIR.glob("*.json"):
        with open(json_file, 'r') as f:
            data = json.load(f)
            key = f"{data['language']}_{data['null_type']}"
            results[key] = data
    return results

def analyze_null_distribution(nulls_array, name):
    """Deep statistical analysis of a null distribution."""
    return {
        'mean': np.mean(nulls_array),
        'median': np.median(nulls_array),
        'std': np.std(nulls_array),
        'min': np.min(nulls_array),
        'max': np.max(nulls_array),
        'range': np.max(nulls_array) - np.min(nulls_array),
        'skewness': stats.skew(nulls_array),
        'kurtosis': stats.kurtosis(nulls_array),
        'cv': (np.std(nulls_array) / abs(np.mean(nulls_array))) * 100,
        'q25': np.percentile(nulls_array, 25),
        'q75': np.percentile(nulls_array, 75),
        'iqr': np.percentile(nulls_array, 75) - np.percentile(nulls_array, 25),
        'ci_width': np.percentile(nulls_array, 97.5) - np.percentile(nulls_array, 2.5),
    }

def compare_distributions(dist1_array, dist2_array, name1, name2):
    """Compare two null distributions statistically."""
    # Kolmogorov-Smirnov test
    ks_stat, ks_pval = stats.ks_2samp(dist1_array, dist2_array)
    
    # Mann-Whitney U test
    u_stat, u_pval = stats.mannwhitneyu(dist1_array, dist2_array, alternative='two-sided')
    
    # Effect size (Cohen's d)
    mean_diff = np.mean(dist1_array) - np.mean(dist2_array)
    pooled_std = np.sqrt((np.var(dist1_array) + np.var(dist2_array)) / 2)
    cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0
    
    return {
        'ks_statistic': ks_stat,
        'ks_pvalue': ks_pval,
        'mannwhitney_u': u_stat,
        'mannwhitney_pvalue': u_pval,
        'cohens_d': cohens_d,
        'mean_difference': mean_diff,
    }

def main():
    print("="*70)
    print("🔍 DEEP INSIGHTS MINER - Agent DATA_MINER")
    print("="*70)
    print()
    
    # Load data
    print("📂 Loading all structural null results...")
    results = load_all_results()
    print(f"   ✅ Loaded {len(results)} result files\n")
    
    insights = []
    
    # ===== INSIGHT 1: Null Distribution Properties =====
    print("─" * 70)
    print("🔬 INSIGHT 1: Null Distribution Shape Analysis")
    print("─" * 70)
    
    dist_props = {}
    for key, data in results.items():
        if 'kappa_nulls' in data:
            nulls = np.array(data['kappa_nulls'])
            props = analyze_null_distribution(nulls, key)
            dist_props[key] = props
            
            print(f"\n{key}:")
            print(f"  Skewness: {props['skewness']:.3f} ({'right' if props['skewness'] > 0 else 'left'}-skewed)")
            print(f"  Kurtosis: {props['kurtosis']:.3f} ({'heavy' if props['kurtosis'] > 0 else 'light'} tails)")
            print(f"  CV: {props['cv']:.2f}%")
            print(f"  CI width: {props['ci_width']:.4f}")
            
            # Check for interesting patterns
            if abs(props['skewness']) > 0.5:
                insights.append({
                    'type': 'distribution_skew',
                    'priority': 0.6,
                    'finding': f"{key} null distribution is {'strongly right' if props['skewness'] > 0.5 else 'strongly left'}-skewed (skew={props['skewness']:.3f})",
                    'implication': "Asymmetric null distribution suggests..."
                })
            
            if props['kurtosis'] > 1.0:
                insights.append({
                    'type': 'heavy_tails',
                    'priority': 0.5,
                    'finding': f"{key} has heavy-tailed null distribution (kurtosis={props['kurtosis']:.3f})",
                    'implication': "Higher variance than normal, potential outliers"
                })
    
    # ===== INSIGHT 2: Cross-Language Patterns =====
    print("\n" + "─" * 70)
    print("🌍 INSIGHT 2: Cross-Language Null Comparison")
    print("─" * 70)
    
    # Compare Spanish vs. English (both have config+triadic)
    if 'spanish_configuration' in results and 'english_configuration' in results:
        sp_nulls = np.array(results['spanish_configuration']['kappa_nulls'])
        en_nulls = np.array(results['english_configuration']['kappa_nulls'])
        
        comp = compare_distributions(sp_nulls, en_nulls, "Spanish", "English")
        print(f"\nSpanish vs. English (configuration nulls):")
        print(f"  Mean diff: {comp['mean_difference']:.5f}")
        print(f"  Cohen's d: {comp['cohens_d']:.3f}")
        print(f"  KS p-value: {comp['ks_pvalue']:.3e}")
        
        if comp['ks_pvalue'] < 0.05:
            insights.append({
                'type': 'cross_language',
                'priority': 0.7,
                'finding': f"Spanish and English configuration null distributions differ significantly (p={comp['ks_pvalue']:.3e}, d={comp['cohens_d']:.3f})",
                'implication': "Language-specific topological properties affect null models"
            })
    
    # ===== INSIGHT 3: Config vs. Triadic =====
    print("\n" + "─" * 70)
    print("🔀 INSIGHT 3: Configuration vs. Triadic Comparison")
    print("─" * 70)
    
    for lang in ['spanish', 'english']:
        config_key = f"{lang}_configuration"
        triadic_key = f"{lang}_triadic"
        
        if config_key in results and triadic_key in results:
            config_nulls = np.array(results[config_key]['kappa_nulls'])
            triadic_nulls = np.array(results[triadic_key]['kappa_nulls'])
            
            comp = compare_distributions(config_nulls, triadic_nulls, "Config", "Triadic")
            
            # Calculate preservation ratio
            config_std = results[config_key]['kappa_null_std']
            triadic_std = results[triadic_key]['kappa_null_std']
            preservation_ratio = triadic_std / config_std if config_std > 0 else 1.0
            
            print(f"\n{lang.title()}:")
            print(f"  Config null variance: {config_std:.5f}")
            print(f"  Triadic null variance: {triadic_std:.5f}")
            print(f"  Variance ratio (triadic/config): {preservation_ratio:.3f}")
            print(f"  Cohen's d: {comp['cohens_d']:.3f}")
            
            if preservation_ratio < 0.5:
                insights.append({
                    'type': 'triadic_preservation',
                    'priority': 0.8,
                    'finding': f"{lang.title()}: Triadic nulls have {(1-preservation_ratio)*100:.1f}% less variance than configuration ({triadic_std:.4f} vs {config_std:.4f})",
                    'implication': "Triadic-rewire preserves significantly more structure, reducing null variance"
                })
    
    # ===== INSIGHT 4: Effect Size Heterogeneity =====
    print("\n" + "─" * 70)
    print("📊 INSIGHT 4: Effect Size Heterogeneity Across Languages")
    print("─" * 70)
    
    config_deltas = []
    config_langs = []
    for key, data in results.items():
        if 'configuration' in key and 'delta_kappa' in data:
            config_deltas.append(data['delta_kappa'])
            config_langs.append(data['language'])
    
    if len(config_deltas) > 1:
        delta_mean = np.mean(config_deltas)
        delta_std = np.std(config_deltas)
        delta_cv = (delta_std / delta_mean) * 100 if delta_mean > 0 else 0
        
        print(f"\nConfiguration Model Δκ across languages:")
        for lang, delta in zip(config_langs, config_deltas):
            print(f"  {lang:10s}: Δκ = {delta:.4f}")
        print(f"\n  Mean Δκ: {delta_mean:.4f}")
        print(f"  Std Δκ: {delta_std:.4f}")
        print(f"  CV: {delta_cv:.2f}%")
        
        # Q-statistic for heterogeneity (meta-analysis)
        Q = sum([(d - delta_mean)**2 for d in config_deltas])
        df = len(config_deltas) - 1
        Q_pvalue = 1 - stats.chi2.cdf(Q, df)
        I_squared = max(0, ((Q - df) / Q) * 100) if Q > 0 else 0
        
        print(f"\n  Heterogeneity (Q-statistic):")
        print(f"    Q = {Q:.3f}, df = {df}, p = {Q_pvalue:.3f}")
        print(f"    I² = {I_squared:.1f}%")
        
        if Q_pvalue > 0.05:
            insights.append({
                'type': 'effect_homogeneity',
                'priority': 0.9,
                'finding': f"Effect sizes are homogeneous across languages (Q={Q:.3f}, p={Q_pvalue:.3f}, I²={I_squared:.1f}%)",
                'implication': "Hyperbolic geometry is a consistent cross-linguistic phenomenon with uniform effect magnitude"
            })
    
    # ===== INSIGHT 5: Precision Analysis =====
    print("\n" + "─" * 70)
    print("🎯 INSIGHT 5: Null Model Precision (Confidence Interval Widths)")
    print("─" * 70)
    
    for key, data in results.items():
        if all(k in data for k in ['ci_95_lower', 'ci_95_upper', 'kappa_null_mean']):
            ci_width = data['ci_95_upper'] - data['ci_95_lower']
            ci_width_pct = (ci_width / abs(data['kappa_null_mean'])) * 100 if data['kappa_null_mean'] != 0 else 0
            
            print(f"\n{key}:")
            print(f"  CI width: {ci_width:.5f} ({ci_width_pct:.1f}% of mean)")
            print(f"  Precision: {'Excellent' if ci_width_pct < 10 else 'Good' if ci_width_pct < 20 else 'Moderate'}")
            
            if ci_width_pct < 10:
                insights.append({
                    'type': 'high_precision',
                    'priority': 0.7,
                    'finding': f"{key} shows excellent precision (CI width = {ci_width_pct:.1f}% of mean)",
                    'implication': "M=1000 provides very tight estimates, high statistical power"
                })
    
    # ===== INSIGHT 6: Outlier Detection =====
    print("\n" + "─" * 70)
    print("🔎 INSIGHT 6: Outlier Analysis in Null Distributions")
    print("─" * 70)
    
    for key, data in results.items():
        if 'kappa_nulls' in data:
            nulls = np.array(data['kappa_nulls'])
            Q1, Q3 = np.percentile(nulls, [25, 75])
            IQR = Q3 - Q1
            lower_fence = Q1 - 1.5 * IQR
            upper_fence = Q3 + 1.5 * IQR
            
            outliers_lower = nulls[nulls < lower_fence]
            outliers_upper = nulls[nulls > upper_fence]
            n_outliers = len(outliers_lower) + len(outliers_upper)
            outlier_pct = (n_outliers / len(nulls)) * 100
            
            print(f"\n{key}:")
            print(f"  Outliers: {n_outliers}/{len(nulls)} ({outlier_pct:.1f}%)")
            
            if outlier_pct > 5:
                insights.append({
                    'type': 'outliers',
                    'priority': 0.4,
                    'finding': f"{key} has {outlier_pct:.1f}% outliers in null distribution",
                    'implication': "Null model occasionally generates extreme networks"
                })
    
    # ===== SYNTHESIS =====
    print("\n" + "="*70)
    print("💡 SYNTHESIZED INSIGHTS FOR MANUSCRIPT")
    print("="*70)
    
    # Sort by priority
    insights_sorted = sorted(insights, key=lambda x: x['priority'], reverse=True)
    
    print(f"\nFound {len(insights_sorted)} insights (priority threshold = 0.6):\n")
    
    high_priority = [ins for ins in insights_sorted if ins['priority'] >= 0.6]
    for i, insight in enumerate(high_priority, 1):
        print(f"{i}. [{insight['type'].upper()}] (priority={insight['priority']:.2f})")
        print(f"   Finding: {insight['finding']}")
        print(f"   Implication: {insight['implication']}")
        print()
    
    # Save insights
    output_path = RESULTS_DIR.parent / "deep_insights_mined.json"
    with open(output_path, 'w') as f:
        json.dump({
            'insights': insights_sorted,
            'n_total': len(insights_sorted),
            'n_high_priority': len(high_priority),
            'distribution_properties': dist_props,
        }, f, indent=2)
    
    print(f"💾 Insights saved to: {output_path}")
    print(f"\n✅ DEEP MINING COMPLETE - {len(high_priority)} high-priority insights found!")

if __name__ == "__main__":
    main()

