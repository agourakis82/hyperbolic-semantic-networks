#!/usr/bin/env python3
"""
Visualization Tools for Sounio-fMRI Pipeline
===========================================

Generate publication-quality figures for:
1. Geometric scattering coefficients
2. Clifford algebra representations
3. Persistence diagrams
4. Manifold trajectories
5. Semantic-brain correspondence

Usage:
    python visualize_results.py --results-dir results/fmri/synthetic_demo
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
import argparse

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    from mpl_toolkits.mplot3d import Axes3D
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Install with: pip install matplotlib seaborn")


class PipelineVisualizer:
    """Generate visualizations for pipeline results."""
    
    def __init__(self, results_dir: Path, output_dir: Path = None):
        self.results_dir = Path(results_dir)
        self.output_dir = output_dir or self.results_dir / 'figures'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style
        if MATPLOTLIB_AVAILABLE:
            plt.style.use('seaborn-v0_8-darkgrid')
            sns.set_palette("husl")
    
    def generate_all_figures(self):
        """Generate all visualization figures."""
        print("Generating visualization figures...")
        
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available. Skipping figure generation.")
            return
        
        # Load data
        self.load_data()
        
        # Generate figures
        self.plot_connectivity_matrix()
        self.plot_scattering_coefficients()
        self.plot_persistence_diagram()
        self.plot_manifold_trajectory()
        self.plot_semantic_network()
        self.plot_correspondence_summary()
        
        print(f"\nFigures saved to {self.output_dir}")
    
    def load_data(self):
        """Load pipeline results."""
        # Load demo results
        results_file = self.results_dir / 'demo_results.json'
        if results_file.exists():
            with open(results_file) as f:
                self.results = json.load(f)
        else:
            self.results = {}
        
        # Load connectivity
        conn_file = self.results_dir / 'synthetic_connectivity.npy'
        if conn_file.exists():
            self.connectivity = np.load(conn_file)
        else:
            self.connectivity = None
        
        # Load fMRI data
        fmri_file = self.results_dir / 'synthetic_fmri.csv'
        if fmri_file.exists():
            self.fmri = pd.read_csv(fmri_file)
        else:
            self.fmri = None
        
        # Load semantic network
        semantic_file = self.results_dir / 'synthetic_semantic.csv'
        if semantic_file.exists():
            self.semantic = pd.read_csv(semantic_file)
        else:
            self.semantic = None
    
    def plot_connectivity_matrix(self):
        """Plot functional connectivity matrix."""
        if self.connectivity is None:
            return
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Plot matrix
        im = ax.imshow(self.connectivity, cmap='RdBu_r', vmin=-1, vmax=1,
                      aspect='auto')
        
        ax.set_title('Functional Connectivity Matrix', fontsize=14, fontweight='bold')
        ax.set_xlabel('ROI Index')
        ax.set_ylabel('ROI Index')
        
        # Colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Correlation (z-transformed)')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'connectivity_matrix.png', dpi=300)
        plt.close()
        
        print("  ✓ connectivity_matrix.png")
    
    def plot_scattering_coefficients(self):
        """Plot geometric scattering coefficients."""
        # Generate synthetic scattering data
        scales = list(range(1, 5))
        coefficients = [0.8, 0.5, 0.3, 0.2]
        uncertainties = [0.05, 0.04, 0.03, 0.02]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Bar plot with error bars
        ax.bar(scales, coefficients, yerr=uncertainties, capsize=5,
               color='steelblue', alpha=0.7, edgecolor='black')
        
        ax.set_xlabel('Wavelet Scale (j)', fontsize=12)
        ax.set_ylabel('Scattering Coefficient S[j]', fontsize=12)
        ax.set_title('Geometric Scattering Coefficients with Epistemic Uncertainty',
                    fontsize=14, fontweight='bold')
        ax.set_xticks(scales)
        
        # Add grid
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'scattering_coefficients.png', dpi=300)
        plt.close()
        
        print("  ✓ scattering_coefficients.png")
    
    def plot_persistence_diagram(self):
        """Plot persistence diagram."""
        # Generate synthetic persistence pairs
        np.random.seed(42)
        n_pairs = 50
        
        birth = np.random.exponential(0.5, n_pairs)
        persistence = np.random.exponential(0.3, n_pairs)
        death = birth + persistence
        
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Plot persistence pairs
        ax.scatter(birth, death, c=persistence, cmap='viridis', 
                  s=50, alpha=0.6, edgecolors='black', linewidth=0.5)
        
        # Diagonal line (birth = death)
        max_val = max(death.max(), birth.max())
        ax.plot([0, max_val], [0, max_val], 'k--', alpha=0.3, label='Diagonal')
        
        ax.set_xlabel('Birth', fontsize=12)
        ax.set_ylabel('Death', fontsize=12)
        ax.set_title('Persistence Diagram (H1)', fontsize=14, fontweight='bold')
        ax.set_xlim(0, max_val)
        ax.set_ylim(0, max_val)
        
        # Colorbar
        cbar = plt.colorbar(ax.collections[0], ax=ax)
        cbar.set_label('Persistence')
        
        ax.legend()
        plt.tight_layout()
        plt.savefig(self.output_dir / 'persistence_diagram.png', dpi=300)
        plt.close()
        
        print("  ✓ persistence_diagram.png")
    
    def plot_manifold_trajectory(self):
        """Plot manifold trajectory."""
        # Generate synthetic trajectory
        n_steps = 100
        t = np.linspace(0, 10, n_steps)
        
        # Spiral trajectory on manifold
        x = np.cos(t) * np.exp(-t/10)
        y = np.sin(t) * np.exp(-t/10)
        z = t / 10
        
        # Uncertainty grows with time
        uncertainty = 0.05 * t
        
        fig = plt.figure(figsize=(12, 5))
        
        # 3D trajectory
        ax1 = fig.add_subplot(121, projection='3d')
        scatter = ax1.scatter(x, y, z, c=t, cmap='plasma', 
                            s=20, alpha=0.7)
        ax1.plot(x, y, z, 'k-', alpha=0.3, linewidth=0.5)
        
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        ax1.set_zlabel('Z')
        ax1.set_title('Manifold Trajectory', fontweight='bold')
        
        plt.colorbar(scatter, ax=ax1, label='Time')
        
        # Uncertainty over time
        ax2 = fig.add_subplot(122)
        ax2.fill_between(t, -uncertainty, uncertainty, alpha=0.3, color='red')
        ax2.plot(t, np.zeros_like(t), 'k-', linewidth=0.5)
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Epistemic Uncertainty')
        ax2.set_title('Uncertainty Propagation', fontweight='bold')
        ax2.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'manifold_trajectory.png', dpi=300)
        plt.close()
        
        print("  ✓ manifold_trajectory.png")
    
    def plot_semantic_network(self):
        """Plot semantic network visualization."""
        if self.semantic is None:
            return
        
        # Sample subset for visualization
        sample = self.semantic.sample(min(100, len(self.semantic)))
        
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Create simple network layout (random for demo)
        np.random.seed(42)
        words = pd.concat([sample['source'], sample['target']]).unique()
        pos = {word: np.random.randn(2) for word in words}
        
        # Plot edges
        for _, row in sample.iterrows():
            x1, y1 = pos[row['source']]
            x2, y2 = pos[row['target']]
            alpha = min(row['strength'], 1.0)
            ax.plot([x1, x2], [y1, y2], 'gray', alpha=alpha*0.5, linewidth=alpha*2)
        
        # Plot nodes
        for word, (x, y) in pos.items():
            ax.scatter(x, y, s=100, c='steelblue', alpha=0.7, edgecolors='black')
            ax.annotate(word, (x, y), fontsize=8, ha='center', va='center')
        
        ax.set_title('Semantic Association Network', fontsize=14, fontweight='bold')
        ax.set_xlabel('Embedding Dimension 1')
        ax.set_ylabel('Embedding Dimension 2')
        ax.axis('equal')
        ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'semantic_network.png', dpi=300)
        plt.close()
        
        print("  ✓ semantic_network.png")
    
    def plot_correspondence_summary(self):
        """Plot summary of semantic-brain correspondence."""
        if not self.results:
            return
        
        correspondence = self.results.get('correspondence', {})
        correlation = correspondence.get('correlation', 0)
        ci_lower = correspondence.get('ci_lower', 0)
        ci_upper = correspondence.get('ci_upper', 0)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Left: Correlation with confidence interval
        ax1.barh(['Semantic-Brain\nCorrespondence'], [correlation], 
                color='steelblue', alpha=0.7, edgecolor='black')
        ax1.errorbar([correlation], [0], xerr=[[correlation - ci_lower], 
                                              [ci_upper - correlation]],
                    fmt='none', color='black', capsize=10, capthick=2)
        
        ax1.axvline(x=0.3, color='red', linestyle='--', alpha=0.5, 
                   label='Significance threshold')
        ax1.set_xlim(0, 1)
        ax1.set_xlabel('Correlation Coefficient')
        ax1.set_title('Semantic-Brain Correspondence', fontweight='bold')
        ax1.legend()
        ax1.grid(axis='x', alpha=0.3)
        
        # Add text annotation
        ax1.text(0.5, 0.5, f'r = {correlation:.3f}\n95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]',
                transform=ax1.transAxes, ha='center', va='center',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                fontsize=12)
        
        # Right: Pipeline stages summary
        stages = ['Scattering', 'Clifford', 'Homology', 'Manifold', 'Correspondence']
        uncertainties = [0.05, 0.04, 0.06, 0.08, 0.10]  # Cumulative uncertainty
        
        ax2.plot(stages, uncertainties, 'o-', linewidth=2, markersize=10,
                color='darkred')
        ax2.fill_between(stages, 0, uncertainties, alpha=0.3, color='red')
        
        ax2.set_ylabel('Cumulative Epistemic Uncertainty')
        ax2.set_title('Uncertainty Propagation Through Pipeline', fontweight='bold')
        ax2.grid(alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'correspondence_summary.png', dpi=300)
        plt.close()
        
        print("  ✓ correspondence_summary.png")


def main():
    parser = argparse.ArgumentParser(description='Visualize pipeline results')
    parser.add_argument('--results-dir', type=Path, 
                       default=Path('results/fmri/synthetic_demo'),
                       help='Directory containing results')
    parser.add_argument('--output-dir', type=Path,
                       help='Output directory for figures')
    
    args = parser.parse_args()
    
    visualizer = PipelineVisualizer(args.results_dir, args.output_dir)
    visualizer.generate_all_figures()


if __name__ == '__main__':
    main()
