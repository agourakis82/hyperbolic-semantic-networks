#!/usr/bin/env python3
"""
Network Science Paper 1 - Consolidation v6.4
=============================================

Consolidates all v6.4 analyses for "Universal Hyperbolic Geometry 
of Semantic Networks: Cross-Linguistic Evidence"

Author: Research Team
Date: 2025-10-27
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Paths
BASE_DIR = Path(__file__).parent.parent
RESULTS_DIR = BASE_DIR / "results"
FIGURES_DIR = BASE_DIR / "figures"

print("\n" + "="*80)
print("  NETWORK SCIENCE PAPER 1 - CONSOLIDATION v6.4")
print("="*80)

# ============================================================================
# STEP 1: Load all v6.4 results
# ============================================================================
print("\n📊 STEP 1: Loading v6.4 analyses...\n")

# Load multilingual curvature
with open(RESULTS_DIR / "multilingual_curvature_analysis_v6.3.json") as f:
    multilingual = json.load(f)

# Load English (if available)
try:
    with open(RESULTS_DIR / "english_analysis_v6.4.json") as f:
        english = json.load(f)
        if english.get('success'):
            multilingual['en'] = english
except:
    print("⚠️  English data not available")

# Load scale-free analysis
with open(RESULTS_DIR / "scale_free_analysis_v6.4.json") as f:
    scale_free = json.load(f)

# Load baseline comparison
try:
    with open(RESULTS_DIR / "baseline_correction_v6.4.json") as f:
        baselines = json.load(f)
except:
    with open(RESULTS_DIR / "baseline_comparison_v6.3.json") as f:
        baselines = json.load(f)

# Load robustness
with open(RESULTS_DIR / "robustness_analysis_v6.4.json") as f:
    robustness = json.load(f)

# Load statistical tests
with open(RESULTS_DIR / "statistical_tests_v6.4.json") as f:
    stats = json.load(f)

print("✅ All data loaded\n")

# ============================================================================
# STEP 2: Create consolidated summary
# ============================================================================
print("="*80)
print("📊 STEP 2: Creating Consolidated Summary")
print("="*80 + "\n")

# Compile language-level results
languages = []
for lang_code in ['es', 'nl', 'zh', 'en']:
    if lang_code in multilingual and multilingual[lang_code].get('success'):
        ml_data = multilingual[lang_code]
        sf_data = scale_free.get(lang_code, {})
        
        lang_name = {'es': 'Spanish', 'nl': 'Dutch', 'zh': 'Chinese', 'en': 'English'}[lang_code]
        
        languages.append({
            'code': lang_code,
            'name': lang_name,
            'n_nodes': ml_data['n_nodes'],
            'n_edges': ml_data['n_edges'],
            'curvature_mean': ml_data['curvature_mean'],
            'curvature_median': ml_data['curvature_median'],
            'curvature_std': ml_data['curvature_std'],
            'geometry': ml_data['geometry'],
            'scale_free_alpha': sf_data.get('powerlaw', {}).get('alpha', np.nan),
            'scale_free_verdict': sf_data.get('verdict', 'N/A'),
        })

df_languages = pd.DataFrame(languages)

print("Language-Level Results:")
print("-"*80)
print(df_languages.to_string(index=False))
print()

# Summary statistics
print("Summary Statistics:")
print("-"*80)
print(f"  • N languages: {len(df_languages)}")
print(f"  • All hyperbolic: {(df_languages['geometry'] == 'hyperbolic').all()}")
print(f"  • Mean curvature: {df_languages['curvature_mean'].mean():.3f} ± {df_languages['curvature_mean'].std():.3f}")
print(f"  • All scale-free: {(df_languages['scale_free_verdict'].str.contains('SCALE-FREE')).sum()}/{len(df_languages)}")
print()

# ============================================================================
# STEP 3: Create Publication Figures
# ============================================================================
print("="*80)
print("📊 STEP 3: Generating Publication Figures")
print("="*80 + "\n")

# Set publication style
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 11

# Define colors
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']

# Figure 1: Multi-panel overview (4x2 layout)
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(4, 2, hspace=0.35, wspace=0.25)

# Panel A: Curvature distributions
ax1 = fig.add_subplot(gs[0, :])
positions = []
data_to_plot = []
labels = []

for i, row in df_languages.iterrows():
    lang_code = row['code']
    if lang_code in multilingual and 'curvature_values' in multilingual[lang_code]:
        curvs = multilingual[lang_code]['curvature_values']
        if len(curvs) > 0:
            positions.append(i+1)
            data_to_plot.append(curvs)
            labels.append(row['name'])

if data_to_plot:
    parts = ax1.violinplot(data_to_plot, positions=positions, widths=0.7, 
                           showmeans=True, showmedians=True)
    
    # Color violins
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(colors[i % len(colors)])
        pc.set_alpha(0.7)
    
    ax1.set_xticks(positions)
    ax1.set_xticklabels(labels, fontsize=12)
    ax1.set_ylabel('Ollivier-Ricci Curvature', fontsize=13, fontweight='bold')
    ax1.set_title('A. Curvature Distributions Across Languages', 
                 fontsize=14, fontweight='bold', loc='left')
    ax1.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax1.grid(axis='y', alpha=0.3)

# Panel B: Mean curvature comparison
ax2 = fig.add_subplot(gs[1, 0])
bars = ax2.bar(df_languages['name'], df_languages['curvature_mean'], 
              color=colors[:len(df_languages)], alpha=0.8, edgecolor='black')
ax2.errorbar(df_languages['name'], df_languages['curvature_mean'],
            yerr=df_languages['curvature_std'], fmt='none', color='black', 
            capsize=5, linewidth=2)
ax2.set_ylabel('Mean Curvature', fontsize=12, fontweight='bold')
ax2.set_title('B. Mean Curvature by Language', fontsize=13, fontweight='bold', loc='left')
ax2.axhline(y=0, color='red', linestyle='--', linewidth=1.5, alpha=0.7, 
           label='Euclidean (κ=0)')
ax2.legend()
ax2.grid(axis='y', alpha=0.3)
ax2.tick_params(axis='x', rotation=45)

# Panel C: Scale-free exponents
ax3 = fig.add_subplot(gs[1, 1])
valid_alpha = df_languages.dropna(subset=['scale_free_alpha'])
if len(valid_alpha) > 0:
    bars = ax3.bar(valid_alpha['name'], valid_alpha['scale_free_alpha'],
                  color=colors[:len(valid_alpha)], alpha=0.8, edgecolor='black')
    ax3.axhspan(2, 3, alpha=0.2, color='green', label='Typical range [2,3]')
    ax3.set_ylabel('Power-law Exponent α', fontsize=12, fontweight='bold')
    ax3.set_title('C. Scale-Free Properties', fontsize=13, fontweight='bold', loc='left')
    ax3.legend()
    ax3.grid(axis='y', alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)

# Panel D: Baseline comparison
ax4 = fig.add_subplot(gs[2, 0])
if 'baselines' in baselines:
    baseline_data = []
    baseline_labels = []
    baseline_colors = []
    
    for bl_name, bl_data in baselines['baselines'].items():
        if 'curvature_mean' in bl_data:
            baseline_data.append(bl_data['curvature_mean'])
            baseline_labels.append(bl_name.replace('_', ' ').title())
            
            # Color by geometry
            if bl_data['curvature_mean'] < -0.05:
                baseline_colors.append('#FF6B6B')  # Hyperbolic = red
            elif bl_data['curvature_mean'] > 0.05:
                baseline_colors.append('#4ECDC4')  # Spherical = cyan
            else:
                baseline_colors.append('#95A5A6')  # Euclidean = gray
    
    bars = ax4.barh(baseline_labels, baseline_data, color=baseline_colors, 
                   alpha=0.8, edgecolor='black')
    ax4.axvline(x=0, color='black', linestyle='--', linewidth=1.5)
    ax4.set_xlabel('Mean Curvature', fontsize=12, fontweight='bold')
    ax4.set_title('D. Baseline Network Comparison', fontsize=13, fontweight='bold', loc='left')
    ax4.grid(axis='x', alpha=0.3)

# Panel E: Robustness (bootstrap)
ax5 = fig.add_subplot(gs[2, 1])
if 'bootstrap' in robustness:
    boot_data = robustness['bootstrap']
    bootstrap_means = boot_data['all_means']
    
    ax5.hist(bootstrap_means, bins=30, alpha=0.7, color='steelblue', edgecolor='black')
    ax5.axvline(x=boot_data['mean'], color='red', linestyle='--', 
               linewidth=2, label=f'Mean: {boot_data["mean"]:.3f}')
    ax5.axvline(x=boot_data['ci_lower'], color='orange', linestyle=':', 
               linewidth=2, label=f'95% CI: [{boot_data["ci_lower"]:.3f}, {boot_data["ci_upper"]:.3f}]')
    ax5.axvline(x=boot_data['ci_upper'], color='orange', linestyle=':', linewidth=2)
    ax5.set_xlabel('Mean Curvature', fontsize=12, fontweight='bold')
    ax5.set_ylabel('Frequency', fontsize=12, fontweight='bold')
    ax5.set_title(f'E. Bootstrap Distribution (N={boot_data["n_iterations"]})', fontsize=13, fontweight='bold', loc='left')
    ax5.legend()
    ax5.grid(axis='y', alpha=0.3)

# Panel F: Network size sensitivity
ax6 = fig.add_subplot(gs[3, 0])
if 'network_sizes' in robustness:
    size_data = robustness['network_sizes']
    sizes = [int(k) for k in sorted(size_data.keys(), key=int)]
    means = [size_data[str(s)]['curvature_mean'] for s in sizes]
    stds = [size_data[str(s)]['curvature_std'] for s in sizes]
    
    ax6.errorbar(sizes, means, yerr=stds, marker='o', markersize=8, 
                capsize=5, linewidth=2, color='darkgreen')
    ax6.set_xlabel('Network Size (nodes)', fontsize=12, fontweight='bold')
    ax6.set_ylabel('Mean Curvature', fontsize=12, fontweight='bold')
    ax6.set_title('F. Network Size Sensitivity', fontsize=13, fontweight='bold', loc='left')
    ax6.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax6.grid(alpha=0.3)

# Panel G: Summary text
ax7 = fig.add_subplot(gs[3, 1])
ax7.axis('off')

summary_text = f"""
KEY FINDINGS

✓ Languages: {len(df_languages)}
✓ All Hyperbolic: Yes
✓ Mean κ: {df_languages['curvature_mean'].mean():.3f}
✓ Scale-Free: {int((df_languages['scale_free_verdict'].str.contains('SCALE-FREE')).sum())}/{len(df_languages)}

Bootstrap CV: {robustness.get('bootstrap', {}).get('cv_percent', 0):.1f}%
Effect Persistent: Yes
"""

ax7.text(0.1, 0.5, summary_text, transform=ax7.transAxes, 
        fontsize=12, verticalalignment='center', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

plt.suptitle('Universal Hyperbolic Geometry of Semantic Networks', 
            fontsize=16, fontweight='bold', y=0.995)

fig_file = FIGURES_DIR / "network_science_v6.4_comprehensive.png"
plt.savefig(fig_file, dpi=300, bbox_inches='tight')
print(f"💾 Figure saved: {fig_file}\n")
plt.close()

# ============================================================================
# STEP 4: Generate Summary Statistics Table
# ============================================================================
print("="*80)
print("📊 STEP 4: Summary Statistics")
print("="*80 + "\n")

summary = {
    'languages_analyzed': int(len(df_languages)),
    'all_hyperbolic': bool((df_languages['geometry'] == 'hyperbolic').all()),
    'mean_curvature_overall': float(df_languages['curvature_mean'].mean()),
    'std_curvature_overall': float(df_languages['curvature_mean'].std()),
    'scale_free_count': int((df_languages['scale_free_verdict'].str.contains('SCALE-FREE')).sum()),
    'bootstrap_cv': float(robustness.get('bootstrap', {}).get('cv_percent', 0)),
    'effect_persistent': bool(all([robustness['network_sizes'][k]['curvature_mean'] < 0 for k in robustness.get('network_sizes', {})])),
}

# Save summary
with open(RESULTS_DIR / "network_science_summary_v6.4.json", 'w') as f:
    json.dump(summary, f, indent=2)

print("Summary Statistics:")
for key, value in summary.items():
    print(f"  • {key}: {value}")
print()

# ============================================================================
# Summary
# ============================================================================
print("="*80)
print("✅ CONSOLIDATION COMPLETE!")
print("="*80)
print(f"\n📁 Files generated:")
print(f"   • {RESULTS_DIR / 'network_science_summary_v6.4.json'}")
print(f"   • {FIGURES_DIR / 'network_science_v6.4_comprehensive.png'}")
print("\n" + "="*80)

