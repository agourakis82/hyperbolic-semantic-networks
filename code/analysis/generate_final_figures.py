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
    """Figure 1: Clustering–curvature map across association vs taxonomy networks"""
    print("Generating Figure 1: Clustering–Curvature Map...")

    metrics_path = Path('results/phase_diagram_metrics.csv')
    if not metrics_path.exists():
        raise FileNotFoundError(f"Missing metrics file: {metrics_path}")

    import pandas as pd
    metrics = pd.read_csv(metrics_path)

    fig, ax = plt.subplots(figsize=(7.5, 5.8))

    sweet_min, sweet_max = 0.023, 0.147
    ax.axvspan(sweet_min, sweet_max, color='#b3e5fc', alpha=0.35,
               label=r'"Sweet spot" $0.023 \leq C \leq 0.147$')

    palette = {'Association': '#1f77b4', 'Taxonomy': '#ff7f0e'}
    markers = {'Association': 'o', 'Taxonomy': '^'}

    for _, row in metrics.iterrows():
        category = row['category']
        handle_labels = ax.get_legend_handles_labels()[1]
        ax.scatter(
            row['clustering'],
            row['kappa_mean'],
            s=120,
            color=palette.get(category, '#7f7f7f'),
            marker=markers.get(category, 'o'),
            edgecolor='black',
            linewidth=1.2,
            label=category if category not in handle_labels else ""
        )
        ax.text(
            row['clustering'],
            row['kappa_mean'],
            row['label'],
            fontsize=9,
            ha='left',
            va='bottom',
            rotation=15,
            alpha=0.85
        )

    ax.set_xscale('log')
    ax.set_xlabel('Weighted clustering coefficient ($C$)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Mean Ollivier–Ricci curvature ($\\bar{\\kappa}$)', fontsize=12, fontweight='bold')
    ax.set_title('Clustering modula a geometria semântica', fontsize=14, fontweight='bold', pad=14)
    ax.axhline(0, color='black', linestyle='--', linewidth=0.8, alpha=0.6)
    ax.grid(True, which='both', linestyle=':', alpha=0.4)

    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(handles, labels, loc='lower left', frameon=True, fancybox=True, shadow=False)

    ax.text(0.65, 0.92, 'Associação = círculos\nTaxonomia = triângulos', transform=ax.transAxes,
            fontsize=9, bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

    plt.tight_layout()
    plt.savefig('figures/figure1_clustering_curvature.png', dpi=300, bbox_inches='tight')
    plt.savefig('figures/figure1_clustering_curvature.pdf', bbox_inches='tight')
    print('✅ Figure 1 saved')
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
    """Figure 3: Ricci flow trajectories for representative networks"""
    print("Generating Figure 3: Ricci Flow Trajectories...")

    datasets = [
        ('ricci_flow_spanish_real.json', 'SWOW (ES)', '#d62728'),
        ('ricci_flow_english_real.json', 'SWOW (EN)', '#1f77b4'),
        ('ricci_flow_english_config.json', 'Config null (EN)', '#9467bd'),
        ('ricci_flow_wordnet_real.json', 'WordNet (EN)', '#ff7f0e')
    ]

    base_path = Path('results/ricci_flow')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.4))

    for filename, label, color in datasets:
        path = base_path / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing Ricci flow result: {path}")
        with open(path) as f:
            data = json.load(f)

        trajectory = data.get('trajectory', [])
        if not trajectory:
            continue

        steps = [pt['step'] for pt in trajectory]
        clustering = [pt['clustering'] for pt in trajectory]
        kappa = [pt['kappa'] for pt in trajectory]

        ax1.plot(steps, clustering, color=color, linewidth=2.5, label=label)
        ax2.plot(steps, kappa, color=color, linewidth=2.5, label=label)

        ax1.scatter(steps[0], clustering[0], color=color, edgecolor='black', zorder=5)
        ax1.scatter(steps[-1], clustering[-1], color=color, edgecolor='black', zorder=5)
        ax2.scatter(steps[0], kappa[0], color=color, edgecolor='black', zorder=5)
        ax2.scatter(steps[-1], kappa[-1], color=color, edgecolor='black', zorder=5)

    ax1.set_xlabel('Iteração do Ricci flow', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Coeficiente de clustering ($C$)', fontsize=12, fontweight='bold')
    ax1.set_title('A) Clustering reduzido sob Ricci flow', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle=':')

    ax2.set_xlabel('Iteração do Ricci flow', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Curvatura média ($\\bar{\\kappa}$)', fontsize=12, fontweight='bold')
    ax2.set_title('B) Aproximação da geometria esférica', fontsize=13, fontweight='bold')
    ax2.axhline(0, color='black', linestyle='--', linewidth=0.8, alpha=0.6)
    ax2.grid(True, alpha=0.3, linestyle=':')

    legend = fig.legend(loc='upper center', ncol=2, frameon=True, fancybox=True, bbox_to_anchor=(0.5, 1.08))
    for text in legend.get_texts():
        text.set_fontsize(10)

    fig.suptitle('Redes semânticas resistem ao achatamento por Ricci flow', fontsize=15, fontweight='bold', y=1.04)
    plt.tight_layout()
    plt.savefig('figures/figure3_ricci_flow.png', dpi=300, bbox_inches='tight')
    plt.savefig('figures/figure3_ricci_flow.pdf', bbox_inches='tight')
    print('✅ Figure 3 saved')
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

