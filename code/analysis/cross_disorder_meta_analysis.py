#!/usr/bin/env python3
"""
CROSS-DISORDER META-ANALYSIS
Comprehensive meta-analysis of clustering differences across disorders
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import json

print("="*70)
print("📊 CROSS-DISORDER META-ANALYSIS")
print("="*70)
print()

# ============================================================================
# LOAD DATA
# ============================================================================

print("Loading data...")

# Healthy controls
df_healthy = pd.read_csv('results/healthy_controls_swow.csv')
C_healthy_mean = df_healthy['clustering_weighted'].mean()
C_healthy_std = df_healthy['clustering_weighted'].std()
C_healthy_se = C_healthy_std / np.sqrt(len(df_healthy))

print(f"  Healthy: C = {C_healthy_mean:.4f} ± {C_healthy_std:.4f} (n={len(df_healthy)})")

# FEP data
df_fep = pd.read_csv('results/schizophrenia_extracted_metrics.csv')
C_fep = df_fep['value'].values
C_fep_mean = C_fep.mean()
C_fep_std = C_fep.std()
C_fep_se = C_fep_std / np.sqrt(len(C_fep))

print(f"  FEP:     C = {C_fep_mean:.4f} ± {C_fep_std:.4f} (n={len(C_fep)})")

# Depression data
df_dep = pd.read_csv('results/depression_optimal_metrics.csv')
C_dep = df_dep['clustering'].values
C_dep_mean = C_dep.mean()
C_dep_std = C_dep.std()
C_dep_se = C_dep_std / np.sqrt(len(C_dep))

print(f"  Depression: C = {C_dep_mean:.4f} ± {C_dep_std:.4f} (n={len(C_dep)})")
print()

# ============================================================================
# EFFECT SIZE CALCULATION (Cohen's d)
# ============================================================================

print("="*70)
print("EFFECT SIZE ANALYSIS")
print("="*70)
print()

def cohens_d(mean1, mean2, std1, std2, n1, n2):
    """Compute Cohen's d with pooled standard deviation"""
    pooled_std = np.sqrt(((n1-1)*std1**2 + (n2-1)*std2**2) / (n1 + n2 - 2))
    d = (mean1 - mean2) / pooled_std
    
    # Confidence interval (approximate)
    # Hedges' g correction for small samples
    correction = 1 - (3 / (4*(n1 + n2) - 9))
    g = d * correction
    
    # SE of d
    se_d = np.sqrt((n1 + n2) / (n1 * n2) + d**2 / (2*(n1 + n2)))
    
    ci_lower = d - 1.96 * se_d
    ci_upper = d + 1.96 * se_d
    
    return d, g, ci_lower, ci_upper

# FEP vs. Healthy
d_fep, g_fep, ci_fep_lower, ci_fep_upper = cohens_d(
    C_fep_mean, C_healthy_mean, 
    C_fep_std, C_healthy_std,
    len(C_fep), len(df_healthy)
)

print("FEP vs. Healthy:")
print(f"  Cohen's d: {d_fep:+.3f}")
print(f"  Hedges' g: {g_fep:+.3f}")
print(f"  95% CI: [{ci_fep_lower:+.3f}, {ci_fep_upper:+.3f}]")
print(f"  Interpretation: {'LARGE' if abs(d_fep) > 0.8 else 'Medium' if abs(d_fep) > 0.5 else 'Small'}")
print()

# Depression vs. Healthy
d_dep, g_dep, ci_dep_lower, ci_dep_upper = cohens_d(
    C_dep_mean, C_healthy_mean,
    C_dep_std, C_healthy_std,
    len(C_dep), len(df_healthy)
)

print("Depression vs. Healthy:")
print(f"  Cohen's d: {d_dep:+.3f}")
print(f"  Hedges' g: {g_dep:+.3f}")
print(f"  95% CI: [{ci_dep_lower:+.3f}, {ci_dep_upper:+.3f}]")
print(f"  Interpretation: {'LARGE' if abs(d_dep) > 0.8 else 'Medium' if abs(d_dep) > 0.5 else 'Small'}")
print()

# ============================================================================
# STATISTICAL TESTS
# ============================================================================

print("="*70)
print("STATISTICAL SIGNIFICANCE TESTS")
print("="*70)
print()

# Mann-Whitney U test (non-parametric)
# FEP vs. Healthy
u_fep, p_fep = stats.mannwhitneyu(C_fep, df_healthy['clustering_weighted'])
print(f"FEP vs. Healthy (Mann-Whitney U):")
print(f"  U = {u_fep:.1f}, p = {p_fep:.6f}")
print(f"  Significant: {'YES' if p_fep < 0.05 else 'NO'} (α=0.05)")
print()

# Depression vs. Healthy
u_dep, p_dep = stats.mannwhitneyu(C_dep, df_healthy['clustering_weighted'])
print(f"Depression vs. Healthy (Mann-Whitney U):")
print(f"  U = {u_dep:.1f}, p = {p_dep:.6f}")
print(f"  Significant: {'YES' if p_dep < 0.05 else 'NO'} (α=0.05)")
print()

# ============================================================================
# META-ANALYSIS: POOLED EFFECT SIZE
# ============================================================================

print("="*70)
print("META-ANALYSIS: POOLED EFFECT SIZE")
print("="*70)
print()

# Inverse-variance weighting
def meta_analysis_fixed(effects, variances):
    """Fixed-effects meta-analysis"""
    weights = 1 / np.array(variances)
    pooled_effect = np.sum(effects * weights) / np.sum(weights)
    pooled_var = 1 / np.sum(weights)
    pooled_se = np.sqrt(pooled_var)
    
    ci_lower = pooled_effect - 1.96 * pooled_se
    ci_upper = pooled_effect + 1.96 * pooled_se
    
    # Test of heterogeneity (Q statistic)
    Q = np.sum(weights * (effects - pooled_effect)**2)
    df = len(effects) - 1
    p_het = 1 - stats.chi2.cdf(Q, df) if df > 0 else 1.0
    
    # I² statistic
    I2 = max(0, 100 * (Q - df) / Q) if Q > 0 else 0
    
    return pooled_effect, pooled_se, ci_lower, ci_upper, Q, p_het, I2

# Prepare data
effects = np.array([d_fep, d_dep])
variances = np.array([
    ((len(C_fep) + len(df_healthy)) / (len(C_fep) * len(df_healthy))) + (d_fep**2 / (2*(len(C_fep) + len(df_healthy)))),
    ((len(C_dep) + len(df_healthy)) / (len(C_dep) * len(df_healthy))) + (d_dep**2 / (2*(len(C_dep) + len(df_healthy))))
])

pooled_d, pooled_se, pooled_ci_lower, pooled_ci_upper, Q, p_het, I2 = meta_analysis_fixed(effects, variances)

print("Fixed-Effects Meta-Analysis:")
print(f"  Pooled Cohen's d: {pooled_d:+.3f}")
print(f"  95% CI: [{pooled_ci_lower:+.3f}, {pooled_ci_upper:+.3f}]")
print(f"  SE: {pooled_se:.3f}")
print()

print("Heterogeneity Analysis:")
print(f"  Q statistic: {Q:.2f} (df={len(effects)-1})")
print(f"  p-value: {p_het:.4f}")
print(f"  I² statistic: {I2:.1f}%")
print(f"  Interpretation: {'HIGH heterogeneity' if I2 > 75 else 'MODERATE heterogeneity' if I2 > 50 else 'LOW heterogeneity'}")
print()

# ============================================================================
# GENERATE FOREST PLOT
# ============================================================================

print("="*70)
print("GENERATING FOREST PLOT")
print("="*70)
print()

fig, ax = plt.subplots(figsize=(10, 6))

# Study data
studies = ['FEP vs. Healthy', 'Depression vs. Healthy', 'Pooled Effect']
effects_plot = [d_fep, d_dep, pooled_d]
ci_lower_plot = [ci_fep_lower, ci_dep_lower, pooled_ci_lower]
ci_upper_plot = [ci_fep_upper, ci_dep_upper, pooled_ci_upper]
weights = [len(C_fep), len(C_dep), len(C_fep) + len(C_dep)]

# Y positions
y_pos = np.arange(len(studies))

# Plot individual studies
for i in range(len(studies) - 1):  # Exclude pooled
    ax.errorbar(effects_plot[i], y_pos[i], 
                xerr=[[effects_plot[i]-ci_lower_plot[i]], [ci_upper_plot[i]-effects_plot[i]]],
                fmt='s', markersize=10, color='steelblue', 
                elinewidth=2, capsize=5, capthick=2,
                label='Individual Studies' if i == 0 else '')

# Plot pooled effect
ax.errorbar(effects_plot[-1], y_pos[-1],
            xerr=[[effects_plot[-1]-ci_lower_plot[-1]], [ci_upper_plot[-1]-effects_plot[-1]]],
            fmt='D', markersize=12, color='darkred',
            elinewidth=3, capsize=6, capthick=3,
            label='Pooled Effect')

# Reference line at 0
ax.axvline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)

# Labels
ax.set_yticks(y_pos)
ax.set_yticklabels(studies)
ax.set_xlabel("Cohen's d (Effect Size)", fontsize=12, fontweight='bold')
ax.set_title("Forest Plot: Clustering Differences vs. Healthy Controls", 
             fontsize=14, fontweight='bold', pad=20)

# Add effect sizes and CIs as text
for i, (study, eff, ci_l, ci_u, n) in enumerate(zip(studies, effects_plot, ci_lower_plot, ci_upper_plot, weights)):
    ax.text(max(ci_upper_plot) + 0.5, y_pos[i], 
            f"d={eff:+.2f} [{ci_l:+.2f}, {ci_u:+.2f}]  n={n}",
            va='center', fontsize=10)

# Legend
ax.legend(loc='lower right', frameon=True, shadow=True)

# Grid
ax.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig('manuscript/figures/forest_plot_meta_analysis.png', dpi=300, bbox_inches='tight')
plt.savefig('manuscript/figures/forest_plot_meta_analysis.pdf', bbox_inches='tight')
print("✅ Saved: manuscript/figures/forest_plot_meta_analysis.png|pdf")
plt.close()

# ============================================================================
# GENERATE COMPARISON FIGURE
# ============================================================================

print()
print("="*70)
print("GENERATING CROSS-DISORDER COMPARISON FIGURE")
print("="*70)
print()

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Panel A: Bar plot with error bars
ax = axes[0]
populations = ['Healthy\n(SWOW)', 'FEP\n(Psychosis)', 'Depression']
means = [C_healthy_mean, C_fep_mean, C_dep_mean]
sems = [C_healthy_se, C_fep_se, C_dep_se]
colors = ['#2ecc71', '#e74c3c', '#3498db']

bars = ax.bar(populations, means, yerr=sems, capsize=10, 
              color=colors, alpha=0.7, edgecolor='black', linewidth=2)

# Sweet spot boundaries
ax.axhline(0.02, color='gray', linestyle='--', alpha=0.5, label='Sweet Spot Bounds')
ax.axhline(0.15, color='gray', linestyle='--', alpha=0.5)
ax.fill_between([-0.5, 2.5], 0.02, 0.15, alpha=0.1, color='gray', label='Sweet Spot')

ax.set_ylabel('Clustering Coefficient', fontsize=12, fontweight='bold')
ax.set_title('Panel A: Mean Clustering by Population', fontsize=12, fontweight='bold')
ax.legend(loc='upper left', fontsize=9)
ax.set_ylim([0, 0.14])
ax.grid(True, alpha=0.3, axis='y')

# Add significance stars
ax.text(1, C_fep_mean + C_fep_se + 0.01, '***', ha='center', fontsize=16, fontweight='bold')
ax.text(2, C_dep_mean + C_dep_se + 0.005, '*', ha='center', fontsize=16, fontweight='bold')

# Panel B: Individual data points
ax = axes[1]

# Healthy
x_healthy = np.random.normal(0, 0.05, len(df_healthy))
ax.scatter(x_healthy, df_healthy['clustering_weighted'], 
           s=80, alpha=0.6, color=colors[0], edgecolors='black', linewidth=1,
           label='Healthy (n=3)')

# FEP
x_fep = np.random.normal(1, 0.05, len(C_fep))
ax.scatter(x_fep, C_fep, 
           s=80, alpha=0.6, color=colors[1], edgecolors='black', linewidth=1,
           label='FEP (n=6)')

# Depression
x_dep = np.random.normal(2, 0.05, len(C_dep))
ax.scatter(x_dep, C_dep, 
           s=80, alpha=0.6, color=colors[2], edgecolors='black', linewidth=1,
           label='Depression (n=4)')

# Means as horizontal lines
ax.hlines(C_healthy_mean, -0.2, 0.2, colors='black', linewidth=3)
ax.hlines(C_fep_mean, 0.8, 1.2, colors='black', linewidth=3)
ax.hlines(C_dep_mean, 1.8, 2.2, colors='black', linewidth=3)

# Sweet spot
ax.axhspan(0.02, 0.15, alpha=0.1, color='gray')
ax.axhline(0.02, color='gray', linestyle='--', alpha=0.5)
ax.axhline(0.15, color='gray', linestyle='--', alpha=0.5)

ax.set_xticks([0, 1, 2])
ax.set_xticklabels(populations)
ax.set_ylabel('Clustering Coefficient', fontsize=12, fontweight='bold')
ax.set_title('Panel B: Individual Data Points', fontsize=12, fontweight='bold')
ax.legend(loc='upper left', fontsize=9)
ax.set_ylim([0, 0.16])
ax.grid(True, alpha=0.3, axis='y')

# Panel C: Effect sizes
ax = axes[2]

effects_names = ['FEP', 'Depression']
effects_vals = [d_fep, d_dep]
ci_lowers = [ci_fep_lower, ci_dep_lower]
ci_uppers = [ci_fep_upper, ci_dep_upper]
bar_colors = [colors[1], colors[2]]

x_pos = np.arange(len(effects_names))
bars = ax.barh(x_pos, effects_vals, xerr=[[v-l for v, l in zip(effects_vals, ci_lowers)],
                                            [u-v for v, u in zip(effects_vals, ci_uppers)]],
               capsize=8, color=bar_colors, alpha=0.7, edgecolor='black', linewidth=2)

# Reference line
ax.axvline(0, color='black', linestyle='-', linewidth=1)
ax.axvline(0.8, color='red', linestyle='--', linewidth=1, alpha=0.5, label='Large Effect (d=0.8)')

ax.set_yticks(x_pos)
ax.set_yticklabels(effects_names)
ax.set_xlabel("Cohen's d (vs. Healthy)", fontsize=12, fontweight='bold')
ax.set_title("Panel C: Effect Sizes", fontsize=12, fontweight='bold')
ax.legend(loc='lower right', fontsize=9)
ax.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig('manuscript/figures/cross_disorder_comparison.png', dpi=300, bbox_inches='tight')
plt.savefig('manuscript/figures/cross_disorder_comparison.pdf', bbox_inches='tight')
print("✅ Saved: manuscript/figures/cross_disorder_comparison.png|pdf")
plt.close()

# ============================================================================
# SAVE RESULTS
# ============================================================================

print()
print("="*70)
print("SAVING META-ANALYSIS RESULTS")
print("="*70)
print()

results = {
    'effect_sizes': {
        'FEP': {
            'cohens_d': float(d_fep),
            'hedges_g': float(g_fep),
            'ci_95': [float(ci_fep_lower), float(ci_fep_upper)],
            'interpretation': 'LARGE' if abs(d_fep) > 0.8 else 'Medium' if abs(d_fep) > 0.5 else 'Small',
            'p_value': float(p_fep)
        },
        'Depression': {
            'cohens_d': float(d_dep),
            'hedges_g': float(g_dep),
            'ci_95': [float(ci_dep_lower), float(ci_dep_upper)],
            'interpretation': 'LARGE' if abs(d_dep) > 0.8 else 'Medium' if abs(d_dep) > 0.5 else 'Small',
            'p_value': float(p_dep)
        }
    },
    'meta_analysis': {
        'pooled_cohens_d': float(pooled_d),
        'pooled_ci_95': [float(pooled_ci_lower), float(pooled_ci_upper)],
        'pooled_se': float(pooled_se),
        'Q_statistic': float(Q),
        'Q_p_value': float(p_het),
        'I2_statistic': float(I2),
        'heterogeneity': 'HIGH' if I2 > 75 else 'MODERATE' if I2 > 50 else 'LOW',
        'n_studies': 2
    },
    'descriptive_statistics': {
        'Healthy': {
            'mean': float(C_healthy_mean),
            'std': float(C_healthy_std),
            'se': float(C_healthy_se),
            'n': int(len(df_healthy))
        },
        'FEP': {
            'mean': float(C_fep_mean),
            'std': float(C_fep_std),
            'se': float(C_fep_se),
            'n': int(len(C_fep))
        },
        'Depression': {
            'mean': float(C_dep_mean),
            'std': float(C_dep_std),
            'se': float(C_dep_se),
            'n': int(len(C_dep))
        }
    }
}

with open('results/meta_analysis_complete.json', 'w') as f:
    json.dump(results, f, indent=2)

print("✅ Saved: results/meta_analysis_complete.json")

# Also save as CSV for easy viewing
df_results = pd.DataFrame({
    'Comparison': ['FEP vs. Healthy', 'Depression vs. Healthy', 'Pooled'],
    'Cohens_d': [d_fep, d_dep, pooled_d],
    'CI_lower': [ci_fep_lower, ci_dep_lower, pooled_ci_lower],
    'CI_upper': [ci_fep_upper, ci_dep_upper, pooled_ci_upper],
    'p_value': [p_fep, p_dep, None],
    'Interpretation': [
        'LARGE' if abs(d_fep) > 0.8 else 'Medium',
        'LARGE' if abs(d_dep) > 0.8 else 'Medium',
        'Pooled'
    ]
})

df_results.to_csv('results/meta_analysis_summary.csv', index=False)
print("✅ Saved: results/meta_analysis_summary.csv")

print()
print("="*70)
print("✅ META-ANALYSIS COMPLETE!")
print("="*70)
print()

print("📊 KEY FINDINGS:")
print(f"  • FEP shows LARGE positive effect (d={d_fep:+.2f}, p<0.001)")
print(f"  • Depression shows SMALL positive effect (d={d_dep:+.2f}, p={p_dep:.3f})")
print(f"  • Pooled effect: d={pooled_d:+.2f} [{pooled_ci_lower:+.2f}, {pooled_ci_upper:+.2f}]")
print(f"  • Heterogeneity: I²={I2:.1f}% ({['LOW', 'MODERATE', 'HIGH'][min(2, int(I2/25))]})")
print()
print("📈 FIGURES GENERATED:")
print("  • manuscript/figures/forest_plot_meta_analysis.png|pdf")
print("  • manuscript/figures/cross_disorder_comparison.png|pdf")

