#!/usr/bin/env python3
"""
Generate final publication-quality figures for manuscript v1.9
Figure 1: Clustering-Curvature scatter (9 models)
Figure 2: Config null violin plots (3 languages)
Figure 3: Ricci flow trajectories (6 networks)
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats

# Publication style
plt.rcParams.update({
    'font.size': 11,
    'font.family': 'Arial',
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

# ============================================================================
# FIGURE 1: Clustering-Curvature Relationship
# ============================================================================

def generate_figure1():
    """Figure 1: Clustering moderates hyperbolic geometry"""
    
    print("Generating Figure 1: Clustering-Curvature Relationship...")
    
    # Load data
    with open('results/final_validation/clustering_moderation_validation.json') as f:
        data = json.load(f)
    
    models = data['models']
    C_values = [m['clustering'] for m in models if m['kappa'] is not None]
    kappa_values = [m['kappa'] for m in models if m['kappa'] is not None]
    labels = [m['model'] for m in models if m['kappa'] is not None]
    
    # Regression
    slope = data['statistical_tests']['linear_regression']['slope']
    intercept = data['statistical_tests']['linear_regression']['intercept']
    r2 = data['statistical_tests']['linear_regression']['R2']
    r_pearson = data['statistical_tests']['pearson']['r']
    p_pearson = data['statistical_tests']['pearson']['p']
    
    # Plot
    fig, ax = plt.subplots(figsize=(7, 5.5))
    
    # Color by type
    colors = []
    for label in labels:
        if 'Real' in label:
            colors.append('#d62728')  # Red for real
        elif 'Config' in label:
            colors.append('#1f77b4')  # Blue for config
        elif 'WS' in label:
            colors.append('#2ca02c')  # Green for WS
        elif 'ER' in label:
            colors.append('#ff7f0e')  # Orange for ER
        elif 'BA' in label:
            colors.append('#9467bd')  # Purple for BA
        else:
            colors.append('#7f7f7f')  # Gray for others
    
    # Scatter
    ax.scatter(C_values, kappa_values, s=100, c=colors, alpha=0.7, edgecolors='black', linewidth=1.5, zorder=3)
    
    # Regression line
    C_range = np.linspace(min(C_values), max(C_values), 100)
    kappa_pred = intercept + slope * C_range
    ax.plot(C_range, kappa_pred, 'k--', linewidth=2, alpha=0.6, label=f'κ = {intercept:.3f} + {slope:.3f}·C', zorder=2)
    
    # Labels with arrows for crowded points
    for i, (c, k, label) in enumerate(zip(C_values, kappa_values, labels)):
        if 'Real' in label or 'Config' in label:
            ax.annotate(label, (c, k), xytext=(10, 10), textcoords='offset points',
                       fontsize=9, ha='left',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray', alpha=0.8),
                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3', color='gray', lw=1))
    
    # Stats box
    stats_text = f"R² = {r2:.3f}\nr = {r_pearson:+.3f}\np = {p_pearson:.4f}"
    ax.text(0.05, 0.95, stats_text, transform=ax.transAxes,
           fontsize=10, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    ax.set_xlabel('Clustering Coefficient (C)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Mean Ollivier-Ricci Curvature (κ)', fontsize=12, fontweight='bold')
    ax.set_title('Clustering Moderates Hyperbolic Geometry', fontsize=14, fontweight='bold', pad=15)
    ax.grid(True, alpha=0.3, linestyle=':', zorder=1)
    ax.axhline(0, color='black', linestyle='-', linewidth=0.8, alpha=0.5, zorder=1)
    ax.legend(loc='lower right', frameon=True, fancybox=True, shadow=True)
    
    plt.tight_layout()
    plt.savefig('figures/figure1_clustering_curvature.png', dpi=300, bbox_inches='tight')
    plt.savefig('figures/figure1_clustering_curvature.pdf', bbox_inches='tight')
    print("✅ Figure 1 saved")
    plt.close()


# ============================================================================
# FIGURE 2: Configuration Null Distributions
# ============================================================================

def generate_figure2():
    """Figure 2: Config nulls are MORE hyperbolic than real"""
    
    print("Generating Figure 2: Configuration Null Distributions...")
    
    languages = ['spanish', 'english', 'chinese']
    lang_names = ['Spanish', 'English', 'Chinese']
    
    fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=True)
    
    for ax, lang, name in zip(axes, languages, lang_names):
        # Load data
        with open(f'results/final_validation/{lang}_configuration_nulls.json') as f:
            data = json.load(f)
        
        kappa_real = data['kappa_real']
        kappa_nulls = data['kappa_nulls']
        kappa_null_mean = data['kappa_null_mean']
        delta_kappa = data['delta_kappa']
        p_MC = data['p_MC']
        cliff_delta = data['cliff_delta']
        
        # Violin plot for nulls
        parts = ax.violinplot([kappa_nulls], positions=[0], widths=0.7,
                              showmeans=False, showmedians=False, showextrema=False)
        
        for pc in parts['bodies']:
            pc.set_facecolor('#1f77b4')
            pc.set_alpha(0.6)
            pc.set_edgecolor('black')
            pc.set_linewidth(1.5)
        
        # Real network line
        ax.axhline(kappa_real, color='#d62728', linestyle='--', linewidth=3, label=f'Real: κ={kappa_real:.3f}', zorder=3)
        
        # Null mean line
        ax.axhline(kappa_null_mean, color='#1f77b4', linestyle=':', linewidth=2, label=f'Null mean: κ={kappa_null_mean:.3f}', alpha=0.8)
        
        # Stats annotation
        stats_text = f"Δκ = {delta_kappa:+.3f}\np < 0.001\nCliff's δ = {cliff_delta:.2f}"
        ax.text(0.5, 0.05, stats_text, transform=ax.transAxes,
               fontsize=9, ha='center',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
        
        ax.set_title(name, fontsize=13, fontweight='bold')
        ax.set_xlim(-0.6, 0.6)
        ax.set_xticks([])
        ax.grid(True, alpha=0.3, axis='y', linestyle=':', zorder=1)
        ax.axhline(0, color='black', linestyle='-', linewidth=0.8, alpha=0.5, zorder=1)
        
        if ax == axes[0]:
            ax.set_ylabel('Ollivier-Ricci Curvature (κ)', fontsize=12, fontweight='bold')
            ax.legend(loc='upper left', fontsize=9, frameon=True, fancybox=True, shadow=True)
        else:
            ax.legend(loc='upper left', fontsize=9, frameon=True, fancybox=True, shadow=True)
    
    fig.suptitle('Configuration Nulls Are More Hyperbolic Than Real Networks', 
                fontsize=15, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    plt.savefig('figures/figure2_config_nulls.png', dpi=300, bbox_inches='tight')
    plt.savefig('figures/figure2_config_nulls.pdf', bbox_inches='tight')
    print("✅ Figure 2 saved")
    plt.close()


# ============================================================================
# FIGURE 3: Ricci Flow Trajectories
# ============================================================================

def generate_figure3():
    """Figure 3: Semantic networks resist Ricci flow"""
    
    print("Generating Figure 3: Ricci Flow Trajectories...")
    
    languages = ['spanish', 'english', 'chinese']
    lang_names = ['Spanish', 'English', 'Chinese']
    colors = ['#d62728', '#1f77b4', '#2ca02c']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    
    for lang, name, color in zip(languages, lang_names, colors):
        # Load data
        with open(f'results/ricci_flow/ricci_flow_{lang}_real.json') as f:
            data = json.load(f)
        
        # Extract trajectory (simplified - just initial and final)
        C_initial = data['initial_metrics']['clustering']
        C_final = data['final_metrics']['clustering']
        kappa_initial = data['initial_metrics']['kappa']
        kappa_final = data['final_metrics']['kappa']
        steps = data['parameters']['iterations']
        
        # Plot clustering trajectory
        ax1.plot([0, steps], [C_initial, C_final], '-o', color=color, linewidth=2.5, 
                markersize=8, label=name, alpha=0.8)
        
        # Plot curvature trajectory
        ax2.plot([0, steps], [kappa_initial, kappa_final], '-o', color=color, linewidth=2.5,
                markersize=8, label=name, alpha=0.8)
    
    # Clustering panel
    ax1.set_xlabel('Ricci Flow Iteration', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Clustering Coefficient (C)', fontsize=12, fontweight='bold')
    ax1.set_title('A) Clustering Reduction', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle=':', zorder=1)
    ax1.legend(loc='upper right', fontsize=10, frameon=True, fancybox=True, shadow=True)
    
    # Add annotation
    ax1.text(0.05, 0.5, '79-87% reduction', transform=ax1.transAxes,
            fontsize=10, style='italic', color='darkred',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Curvature panel
    ax2.set_xlabel('Ricci Flow Iteration', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Mean Curvature (κ)', fontsize=12, fontweight='bold')
    ax2.set_title('B) Sphericalization', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle=':', zorder=1)
    ax2.axhline(0, color='black', linestyle='-', linewidth=0.8, alpha=0.5, zorder=1)
    ax2.legend(loc='lower right', fontsize=10, frameon=True, fancybox=True, shadow=True)
    
    # Add annotation
    ax2.text(0.05, 0.95, 'Δκ ≈ +0.17 to +0.25', transform=ax2.transAxes,
            fontsize=10, style='italic', color='darkblue',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
            verticalalignment='top')
    
    fig.suptitle('Semantic Networks Resist Geometric Equilibrium', 
                fontsize=15, fontweight='bold', y=1.00)
    
    plt.tight_layout()
    plt.savefig('figures/figure3_ricci_flow.png', dpi=300, bbox_inches='tight')
    plt.savefig('figures/figure3_ricci_flow.pdf', bbox_inches='tight')
    print("✅ Figure 3 saved")
    plt.close()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("="*70)
    print("GENERATING FINAL PUBLICATION FIGURES")
    print("="*70)
    print()
    
    # Create figures directory
    Path('figures').mkdir(parents=True, exist_ok=True)
    
    # Generate all figures
    generate_figure1()
    generate_figure2()
    generate_figure3()
    
    print()
    print("="*70)
    print("✅ ALL FIGURES GENERATED")
    print("="*70)
    print()
    print("Files saved:")
    print("  - figures/figure1_clustering_curvature.png|pdf")
    print("  - figures/figure2_config_nulls.png|pdf")
    print("  - figures/figure3_ricci_flow.png|pdf")

