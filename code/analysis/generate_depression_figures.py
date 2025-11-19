#!/usr/bin/env python3
"""
Generate Publication-Quality Figures for Depression Analysis
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Set publication style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("colorblind")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'sans-serif'

print("="*70)
print("GENERATING PUBLICATION FIGURES - DEPRESSION ANALYSIS")
print("="*70)
print()

# Create output directory
fig_dir = Path('manuscript/figures')
fig_dir.mkdir(parents=True, exist_ok=True)

# ============================================================================
# LOAD DATA
# ============================================================================

# KEC results
df_kec = pd.read_csv('results/depression_complete_kec.csv')

# Add severity order
severity_order = {'minimum': 0, 'mild': 1, 'moderate': 2, 'severe': 3}
df_kec['severity_num'] = df_kec['severity'].map(severity_order)
df_kec = df_kec.sort_values('severity_num')

print("Loaded KEC results:")
print(df_kec[['severity', 'clustering', 'curvature', 'H_spectral', 'KEC_spectral']])
print()

# ============================================================================
# FIGURE 1: KEC Components by Severity
# ============================================================================

print("Generating Figure 1: KEC Components by Severity")

fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('KEC Framework: Depression Severity Analysis', fontsize=14, fontweight='bold')

# Plot 1: Clustering
ax1 = axes[0, 0]
ax1.plot(df_kec['severity_num'], df_kec['clustering'], 'o-', linewidth=2, markersize=8)
ax1.axhspan(0.02, 0.15, alpha=0.2, color='green', label='Sweet Spot')
ax1.set_ylabel('Clustering Coefficient (C)', fontsize=11)
ax1.set_xticks(range(4))
ax1.set_xticklabels(['Minimum', 'Mild', 'Moderate', 'Severe'])
ax1.legend()
ax1.grid(alpha=0.3)
ax1.set_title('(A) Clustering (Local Geometry)', fontweight='bold')

# Plot 2: Curvature
ax2 = axes[0, 1]
ax2.plot(df_kec['severity_num'], df_kec['curvature'], 'o-', linewidth=2, markersize=8, color='orange')
ax2.axhline(0, linestyle='--', color='gray', alpha=0.5)
ax2.set_ylabel('Curvature (κ)', fontsize=11)
ax2.set_xticks(range(4))
ax2.set_xticklabels(['Minimum', 'Mild', 'Moderate', 'Severe'])
ax2.grid(alpha=0.3)
ax2.set_title('(B) Hyperbolic Curvature', fontweight='bold')

# Plot 3: Spectral Entropy
ax3 = axes[1, 0]
ax3.plot(df_kec['severity_num'], df_kec['H_spectral'], 'o-', linewidth=2, markersize=8, color='red')
ax3.set_ylabel('Spectral Entropy (H)', fontsize=11)
ax3.set_xlabel('Depression Severity', fontsize=11)
ax3.set_xticks(range(4))
ax3.set_xticklabels(['Minimum', 'Mild', 'Moderate', 'Severe'])
ax3.grid(alpha=0.3)
ax3.set_title('(C) Spectral Entropy (Global Disorder)', fontweight='bold')

# Plot 4: KEC Composite
ax4 = axes[1, 1]
ax4.plot(df_kec['severity_num'], df_kec['KEC_spectral'], 'o-', linewidth=2, markersize=8, color='purple')
ax4.set_ylabel('KEC Score', fontsize=11)
ax4.set_xlabel('Depression Severity', fontsize=11)
ax4.set_xticks(range(4))
ax4.set_xticklabels(['Minimum', 'Mild', 'Moderate', 'Severe'])
ax4.grid(alpha=0.3)
ax4.set_title('(D) KEC Composite Score', fontweight='bold')

plt.tight_layout()
plt.savefig(fig_dir / 'depression_kec_by_severity.png', dpi=300, bbox_inches='tight')
plt.savefig(fig_dir / 'depression_kec_by_severity.pdf', bbox_inches='tight')
print("✅ Saved: manuscript/figures/depression_kec_by_severity.{png,pdf}")

plt.close()

# ============================================================================
# FIGURE 2: Sweet Spot Validation
# ============================================================================

print("Generating Figure 2: Sweet Spot Validation Across Datasets")

fig, ax = plt.subplots(figsize=(10, 6))

# Load SWOW data (for comparison)
swow_clustering = {
    'Spanish': 0.203,
    'English': 0.195,
    'Chinese': 0.215
}

# FEP from PMC10031728
fep_clustering = 0.090

# Depression
depression_clustering = df_kec['clustering'].values

# Create plot
x_positions = []
clustering_values = []
labels = []
colors = []

# SWOW
for i, (lang, c) in enumerate(swow_clustering.items()):
    x_positions.append(i)
    clustering_values.append(c)
    labels.append(f'SWOW\n{lang}')
    colors.append('blue')

# FEP
x_positions.append(len(swow_clustering))
clustering_values.append(fep_clustering)
labels.append('FEP')
colors.append('red')

# Depression
for i, (sev, c) in enumerate(zip(df_kec['severity'], df_kec['clustering'])):
    x_positions.append(len(swow_clustering) + 1 + i)
    clustering_values.append(c)
    labels.append(f'MDD\n{sev.capitalize()}')
    colors.append('green')

# Plot
ax.bar(x_positions, clustering_values, color=colors, alpha=0.7, edgecolor='black')
ax.axhspan(0.02, 0.15, alpha=0.2, color='gray', label='Sweet Spot (0.02-0.15)')
ax.axhline(0.085, linestyle='--', color='black', alpha=0.5, label='Sweet Spot Center')

ax.set_ylabel('Clustering Coefficient (C)', fontsize=12)
ax.set_xlabel('Dataset / Disorder', fontsize=12)
ax.set_xticks(x_positions)
ax.set_xticklabels(labels, rotation=45, ha='right')
ax.legend(fontsize=10)
ax.grid(alpha=0.3, axis='y')
ax.set_title('Sweet Spot Validation: Healthy, FEP, and Depression Networks', fontsize=13, fontweight='bold')

plt.tight_layout()
plt.savefig(fig_dir / 'sweet_spot_validation_depression.png', dpi=300, bbox_inches='tight')
plt.savefig(fig_dir / 'sweet_spot_validation_depression.pdf', bbox_inches='tight')
print("✅ Saved: manuscript/figures/sweet_spot_validation_depression.{png,pdf}")

plt.close()

# ============================================================================
# FIGURE 3: KEC Scatter (Clustering vs. Spectral Entropy)
# ============================================================================

print("Generating Figure 3: KEC Scatter Plot")

fig, ax = plt.subplots(figsize=(8, 7))

# Plot depression points
scatter = ax.scatter(
    df_kec['clustering'], 
    df_kec['H_spectral'],
    c=df_kec['severity_num'],
    s=200,
    alpha=0.7,
    cmap='RdYlBu_r',
    edgecolors='black',
    linewidth=1.5
)

# Add labels
for _, row in df_kec.iterrows():
    ax.annotate(
        row['severity'].capitalize(),
        (row['clustering'], row['H_spectral']),
        xytext=(5, 5),
        textcoords='offset points',
        fontsize=9
    )

# Colorbar
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Severity Level', fontsize=11)
cbar.set_ticks([0, 1, 2, 3])
cbar.set_ticklabels(['Minimum', 'Mild', 'Moderate', 'Severe'])

ax.set_xlabel('Clustering Coefficient (C)', fontsize=12)
ax.set_ylabel('Spectral Entropy (H)', fontsize=12)
ax.set_title('KEC Space: Depression Severity Progression', fontsize=13, fontweight='bold')
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(fig_dir / 'kec_scatter_depression.png', dpi=300, bbox_inches='tight')
plt.savefig(fig_dir / 'kec_scatter_depression.pdf', bbox_inches='tight')
print("✅ Saved: manuscript/figures/kec_scatter_depression.{png,pdf}")

plt.close()

print()
print("="*70)
print("✅ ALL FIGURES GENERATED!")
print("="*70)
print()
print("Output directory: manuscript/figures/")
print("Files: 6 total (3 PNG + 3 PDF)")

