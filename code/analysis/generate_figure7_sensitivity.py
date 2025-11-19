#!/usr/bin/env python3
"""
Generate Figure 7: Sensitivity Analysis Heatmaps

Creates 3-panel heatmap showing robustness of hyperbolic geometry
across parameter variations:
- Panel A: Network size (250-1000 nodes)
- Panel B: Edge threshold (0.1-0.25)
- Panel C: Alpha parameter (0.1-1.0)
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Paths
RESULTS_DIR = Path('/home/agourakis82/workspace/pcs-meta-repo/results/v64_revisions_20251031_065340')
OUTPUT_DIR = Path(__file__).parent.parent.parent / 'manuscript' / 'figures'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load sensitivity analysis results
with open(RESULTS_DIR / 'sensitivity_analysis.json') as f:
    data = json.load(f)

# Configuration
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("RdBu_r")

# Create figure
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

languages = ['spanish', 'dutch', 'chinese', 'english']
param_configs = {
    'n_nodes': {
        'title': 'A) Network Size Sensitivity',
        'xlabel': 'Number of Nodes',
        'ylabel': 'Language',
        'values': [250, 500, 750, 1000]
    },
    'edge_threshold': {
        'title': 'B) Edge Threshold Sensitivity',
        'xlabel': 'Minimum Edge Weight',
        'ylabel': 'Language',
        'values': [0.1, 0.15, 0.2, 0.25]
    },
    'alpha_param': {
        'title': 'C) OR Curvature α Parameter',
        'xlabel': 'Alpha (α)',
        'ylabel': 'Language',
        'values': [0.1, 0.25, 0.5, 0.75, 1.0]
    }
}

# Generate each panel
for idx, (param_name, config) in enumerate(param_configs.items()):
    ax = axes[idx]
    
    # Extract data for heatmap
    sweep_data = data['parameter_sweeps'][param_name]
    param_values = sweep_data['param_values']
    
    # Build matrix: languages × param_values
    matrix = np.zeros((len(languages), len(param_values)))
    
    for i, lang in enumerate(languages):
        lang_results = sweep_data['results_by_language'][lang]
        for j, result in enumerate(lang_results):
            matrix[i, j] = result['curvature']
    
    # Create heatmap
    im = ax.imshow(matrix, cmap='RdBu_r', aspect='auto', 
                   vmin=-0.25, vmax=-0.10, origin='lower')
    
    # Labels
    ax.set_title(config['title'], fontsize=12, fontweight='bold')
    ax.set_xlabel(config['xlabel'], fontsize=10)
    ax.set_ylabel(config['ylabel'], fontsize=10)
    
    # Tick labels
    ax.set_yticks(range(len(languages)))
    ax.set_yticklabels([l.title() for l in languages], fontsize=9)
    ax.set_xticks(range(len(param_values)))
    ax.set_xticklabels([f'{v:.2f}' if isinstance(v, float) else str(v) 
                        for v in param_values], fontsize=9, rotation=45)
    
    # Annotate with values
    for i in range(len(languages)):
        for j in range(len(param_values)):
            text = ax.text(j, i, f'{matrix[i, j]:.3f}',
                          ha="center", va="center", color="black", fontsize=7)
    
    # Colorbar (only on last panel)
    if idx == 2:
        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Mean Curvature (κ)', rotation=270, labelpad=15, fontsize=10)

# Overall title
fig.suptitle('Figure 7: Parameter Sensitivity Analysis - Robustness of Hyperbolic Geometry',
             fontsize=14, fontweight='bold', y=1.02)

# Add caption text
caption = (
    "Heatmaps showing mean Ollivier-Ricci curvature (κ) across parameter variations. "
    "All configurations yield negative curvature (hyperbolic), demonstrating robustness "
    "(Overall CV = 11.5%). Darker red indicates more negative curvature."
)
fig.text(0.5, -0.05, caption, ha='center', fontsize=9, style='italic', wrap=True)

plt.tight_layout()

# Save
output_file = OUTPUT_DIR / 'figure7_sensitivity_heatmaps.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
print(f'✅ Figure 7 saved: {output_file}')
print(f'   Size: {output_file.stat().st_size / 1024:.1f} KB')
print(f'   Resolution: 300 DPI')

# Also save as PDF (vector)
output_pdf = OUTPUT_DIR / 'figure7_sensitivity_heatmaps.pdf'
plt.savefig(output_pdf, bbox_inches='tight', facecolor='white')
print(f'✅ PDF saved: {output_pdf}')

# Summary statistics
print('\n📊 Summary Statistics:')
for param_name in param_configs.keys():
    rob = data['robustness_summary'][param_name]
    print(f'  {param_name}: CV = {rob["cv_percent"]:.1f}%, All negative = {rob["all_negative"]}')

overall = data['robustness_summary']['overall']
print(f'\n  Overall: CV = {overall["mean_cv"]:.1f}%, Robust = {overall["robust"]}')

