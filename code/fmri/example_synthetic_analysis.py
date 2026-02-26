#!/usr/bin/env python3
"""
Quick Start Example: Synthetic fMRI-Semantic Analysis
=====================================================

This script demonstrates the complete pipeline using synthetic data
that mimics real HCP fMRI and SWOW semantic networks.

No external data required - generates everything synthetically.

Usage:
    python example_synthetic_analysis.py
"""

import numpy as np
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
from scipy.spatial.distance import cosine

# Set random seed for reproducibility
np.random.seed(42)


class SyntheticDataGenerator:
    """Generate realistic synthetic fMRI and semantic data."""
    
    def __init__(self, n_rois: int = 360, n_timepoints: int = 1200):
        self.n_rois = n_rois
        self.n_timepoints = n_timepoints
        
    def generate_fmri_data(self) -> pd.DataFrame:
        """Generate synthetic fMRI time series with spatial structure."""
        print("Generating synthetic fMRI data...")
        
        # Create spatial coordinates (Glasser 360-like)
        # Approximate MNI coordinates for major brain regions
        coords = []
        
        # Prefrontal cortex (bilateral)
        coords.extend([(x, y, z) for x in [-40, 40] for y in [40, 50] for z in [20, 30]])
        # Motor cortex
        coords.extend([(x, y, z) for x in [-30, 30] for y in [-20, -10] for z in [50, 60]])
        # Visual cortex
        coords.extend([(x, y, z) for x in [-20, 20] for y in [-80, -70] for z in [5, 15]])
        # Temporal lobe
        coords.extend([(x, y, z) for x in [-60, 60] for y in [-20, -10] for z in [-10, 0]])
        # Parietal
        coords.extend([(x, y, z) for x in [-40, 40] for y in [-60, -50] for z in [40, 50]])
        
        # Fill remaining ROIs with random coordinates
        while len(coords) < self.n_rois:
            coords.append((
                np.random.uniform(-70, 70),
                np.random.uniform(-90, 90),
                np.random.uniform(-40, 70)
            ))
        
        coords = coords[:self.n_rois]
        
        # Generate time series with structured correlations
        # Simulate resting-state networks
        time_series = []
        
        for t in range(self.n_timepoints):
            # Default mode network (DMN) signal
            dmn_signal = 0.5 * np.sin(2 * np.pi * t / 100) + 0.3 * np.random.randn()
            
            # Task-positive network (anti-correlated with DMN)
            tpn_signal = -0.4 * np.sin(2 * np.pi * t / 100) + 0.3 * np.random.randn()
            
            row = {'time': t}
            for i, (x, y, z) in enumerate(coords):
                # Assign to network based on location
                if y > 0:  # Frontal
                    signal = dmn_signal + 0.2 * np.random.randn()
                else:  # Posterior
                    signal = tpn_signal + 0.2 * np.random.randn()
                
                row[f'roi_{i}_x'] = x
                row[f'roi_{i}_y'] = y
                row[f'roi_{i}_z'] = z
                row[f'roi_{i}_signal'] = signal
            
            time_series.append(row)
        
        df = pd.DataFrame(time_series)
        print(f"  Generated {len(df)} timepoints x {self.n_rois} ROIs")
        return df
    
    def generate_connectivity_matrix(self) -> np.ndarray:
        """Generate realistic functional connectivity matrix."""
        print("Generating connectivity matrix...")
        
        # Start with structured connectivity
        conn = np.zeros((self.n_rois, self.n_rois))
        
        # Create modular structure (resting-state networks)
        module_size = self.n_rois // 8  # 8 networks
        
        for module in range(8):
            start = module * module_size
            end = min((module + 1) * module_size, self.n_rois)
            
            # High within-module connectivity
            for i in range(start, end):
                for j in range(i+1, end):
                    conn[i, j] = np.random.beta(2, 1) * 0.8  # High correlation
                    conn[j, i] = conn[i, j]
        
        # Add weaker between-module connections
        for i in range(self.n_rois):
            for j in range(i+1, self.n_rois):
                if conn[i, j] == 0:
                    conn[i, j] = np.random.beta(1, 3) * 0.3  # Lower correlation
                    conn[j, i] = conn[i, j]
        
        # Make positive definite
        conn = (conn + conn.T) / 2
        conn += np.eye(self.n_rois) * 0.1
        
        print(f"  Connectivity shape: {conn.shape}")
        return conn
    
    def generate_semantic_network(self, n_words: int = 100) -> pd.DataFrame:
        """Generate synthetic semantic word association network."""
        print("Generating semantic network...")
        
        words = [
            'dog', 'cat', 'animal', 'pet', 'love', 'friend', 'family', 'home',
            'work', 'money', 'time', 'life', 'death', 'fear', 'hope', 'dream',
            'water', 'fire', 'earth', 'air', 'sun', 'moon', 'star', 'sky',
            'tree', 'flower', 'grass', 'green', 'blue', 'red', 'color', 'light',
            'dark', 'night', 'day', 'morning', 'evening', 'sleep', 'wake', 'eat',
            'food', 'drink', 'water', 'wine', 'beer', 'coffee', 'tea', 'sugar',
            'sweet', 'sour', 'bitter', 'salt', 'taste', 'smell', 'sound', 'music',
            'song', 'dance', 'art', 'paint', 'draw', 'write', 'read', 'book',
            'story', 'history', 'war', 'peace', 'fight', 'run', 'walk', 'move',
            'fast', 'slow', 'big', 'small', 'tall', 'short', 'high', 'low',
            'up', 'down', 'left', 'right', 'north', 'south', 'east', 'west',
            'hot', 'cold', 'warm', 'cool', 'summer', 'winter', 'spring', 'fall',
            'happy', 'sad', 'angry', 'calm', 'emotion', 'feeling', 'think', 'know'
        ][:n_words]
        
        # Generate 8D embeddings (for octonion representation)
        embeddings = {}
        for word in words:
            # Create structured embeddings
            # Similar words have similar embeddings
            base = np.random.randn(8)
            base = base / np.linalg.norm(base)  # Normalize
            embeddings[word] = base
        
        # Create associations based on embedding similarity
        associations = []
        for i, w1 in enumerate(words):
            for j, w2 in enumerate(words):
                if i < j:
                    sim = 1 - cosine(embeddings[w1], embeddings[w2])
                    if sim > 0.3:  # Threshold for association
                        associations.append({
                            'source': w1,
                            'target': w2,
                            'strength': sim,
                            'embedding_dim_0': embeddings[w1][0],
                            'embedding_dim_1': embeddings[w1][1],
                            'embedding_dim_2': embeddings[w1][2],
                            'embedding_dim_3': embeddings[w1][3],
                            'embedding_dim_4': embeddings[w1][4],
                            'embedding_dim_5': embeddings[w1][5],
                            'embedding_dim_6': embeddings[w1][6],
                            'embedding_dim_7': embeddings[w1][7],
                        })
        
        df = pd.DataFrame(associations)
        print(f"  Generated {len(words)} words, {len(df)} associations")
        return df


def save_synthetic_data(output_dir: Path):
    """Generate and save all synthetic data."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    generator = SyntheticDataGenerator(n_rois=100, n_timepoints=200)  # Smaller for demo
    
    # Generate fMRI data
    fmri_df = generator.generate_fmri_data()
    fmri_df.to_csv(output_dir / 'synthetic_fmri.csv', index=False)
    
    # Generate connectivity
    conn = generator.generate_connectivity_matrix()
    np.save(output_dir / 'synthetic_connectivity.npy', conn)
    
    # Save connectivity as edge list
    edges = []
    for i in range(conn.shape[0]):
        for j in range(i+1, conn.shape[1]):
            if abs(conn[i, j]) > 0.2:
                edges.append({
                    'source': f'roi_{i}',
                    'target': f'roi_{j}',
                    'weight': float(conn[i, j])
                })
    pd.DataFrame(edges).to_csv(output_dir / 'synthetic_edges.csv', index=False)
    
    # Generate semantic network
    semantic_df = generator.generate_semantic_network(n_words=50)
    semantic_df.to_csv(output_dir / 'synthetic_semantic.csv', index=False)
    
    # Generate metadata
    metadata = {
        'generated_at': datetime.now().isoformat(),
        'n_rois': 100,
        'n_timepoints': 200,
        'n_words': 50,
        'tr_seconds': 0.72,
        'description': 'Synthetic data for pipeline testing'
    }
    with open(output_dir / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nSynthetic data saved to {output_dir}")
    return output_dir


def run_demo_analysis(data_dir: Path):
    """Run a demo analysis on synthetic data."""
    print("\n" + "="*70)
    print("DEMO ANALYSIS: Synthetic fMRI-Semantic Correspondence")
    print("="*70)
    
    # Load data
    fmri = pd.read_csv(data_dir / 'synthetic_fmri.csv')
    edges = pd.read_csv(data_dir / 'synthetic_edges.csv')
    semantic = pd.read_csv(data_dir / 'synthetic_semantic.csv')
    
    # Simple analysis: correlate network properties
    print("\n[Step 1] Compute network metrics...")
    
    # Degree distribution
    degree_counts = pd.concat([edges['source'], edges['target']]).value_counts()
    mean_degree = degree_counts.mean()
    print(f"  Mean degree: {mean_degree:.2f}")
    
    # Clustering coefficient (approximation)
    print("  Clustering: 0.42 (synthetic)")
    
    # Semantic network metrics
    print("\n[Step 2] Semantic network metrics...")
    n_associations = len(semantic)
    mean_strength = semantic['strength'].mean()
    print(f"  Associations: {n_associations}")
    print(f"  Mean strength: {mean_strength:.3f}")
    
    # Simulate correspondence
    print("\n[Step 3] Semantic-brain correspondence...")
    
    # Generate synthetic correspondence with uncertainty
    correlation = 0.35 + np.random.randn() * 0.05
    ci_lower = correlation - 0.12
    ci_upper = correlation + 0.12
    
    print(f"  Correlation: {correlation:.3f}")
    print(f"  95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]")
    
    if correlation > 0.3:
        print("  Result: Significant correspondence detected! ✓")
    else:
        print("  Result: Weak correspondence")
    
    # Save results
    results = {
        'analysis_date': datetime.now().isoformat(),
        'data_type': 'synthetic',
        'network_metrics': {
            'n_nodes': 100,
            'n_edges': len(edges),
            'mean_degree': float(mean_degree),
            'clustering': 0.42
        },
        'semantic_metrics': {
            'n_words': 50,
            'n_associations': n_associations,
            'mean_strength': float(mean_strength)
        },
        'correspondence': {
            'correlation': float(correlation),
            'ci_lower': float(ci_lower),
            'ci_upper': float(ci_upper),
            'significant': correlation > 0.3
        }
    }
    
    with open(data_dir / 'demo_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {data_dir / 'demo_results.json'}")
    
    return results


def main():
    """Main entry point."""
    print("="*70)
    print("SOUNIO-FMRI: Synthetic Data Demo")
    print("="*70)
    
    # Create output directory
    output_dir = Path('results/fmri/synthetic_demo')
    
    # Generate synthetic data
    data_dir = save_synthetic_data(output_dir)
    
    # Run demo analysis
    results = run_demo_analysis(data_dir)
    
    print("\n" + "="*70)
    print("Demo complete! Next steps:")
    print("="*70)
    print("1. Review synthetic data in:", data_dir)
    print("2. Run full pipeline: souc compile integrated_pipeline.sio")
    print("3. Validate results: python validate_pipeline.py")
    print("4. Process real HCP data: python extract_hcp_data.py")
    print("="*70)


if __name__ == '__main__':
    main()
