DS#!/usr/bin/env python3
"""
Compute power-law exponent for degree distributions.
Simple fitting without powerlaw library.
"""

import networkx as nx
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import linregress
import json
from pathlib import Path

def power_law(x, alpha, c):
    """Power-law function: P(k) = c * k^(-alpha)"""
    return c * x**(-alpha)

def fit_power_law_loglog(degrees):
    """Fit power-law using log-log linear regression."""
    # Remove zeros
    degrees_nonzero = [d for d in degrees if d > 0]

    if len(degrees_nonzero) == 0:
        return None, None, None

    # Count frequency
    unique, counts = np.unique(degrees_nonzero, return_counts=True)
    prob = counts / len(degrees_nonzero)

    # Log-log regression (only for k >= 2 to avoid noise at low k)
    mask = unique >= 2
    if mask.sum() < 3:
        mask = unique >= 1

    x_log = np.log10(unique[mask])
    y_log = np.log10(prob[mask])

    # Linear regression in log-log space
    slope, intercept, r_value, p_value, std_err = linregress(x_log, y_log)

    # Power-law exponent is -slope
    alpha = -slope
    r_squared = r_value**2

    return alpha, r_squared, std_err

def analyze_network(edge_file):
    """Load network and compute power-law exponent."""
    df = pd.read_csv(edge_file)

    # Build graph
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row['source'], row['target'], weight=row['weight'])

    # Get LCC
    if not nx.is_connected(G):
        Gcc = max(nx.connected_components(G), key=len)
        G = G.subgraph(Gcc).copy()

    # Get degrees
    degrees = [d for _, d in G.degree()]

    # Fit power-law
    alpha, r2, stderr = fit_power_law_loglog(degrees)

    return {
        'n_nodes': G.number_of_nodes(),
        'n_edges': G.number_of_edges(),
        'degree_mean': np.mean(degrees),
        'degree_std': np.std(degrees),
        'degree_min': min(degrees),
        'degree_max': max(degrees),
        'alpha': alpha,
        'r_squared': r2,
        'stderr': stderr
    }

def main():
    networks = {
        'spanish': 'data/processed/spanish_edges_FINAL.csv',
        'english': 'data/processed/english_edges_FINAL.csv',
        'chinese': 'data/processed/chinese_edges_FINAL.csv',
        'dutch': 'data/processed/dutch_edges.csv'
    }

    results = {}

    print("="*70)
    print("POWER-LAW DEGREE DISTRIBUTION ANALYSIS")
    print("="*70)
    print()

    for lang, edge_file in networks.items():
        print(f"{lang.upper()}:")
        metrics = analyze_network(edge_file)
        results[lang] = metrics

        print(f"  N = {metrics['n_nodes']}, E = {metrics['n_edges']}")
        print(f"  ⟨k⟩ = {metrics['degree_mean']:.2f} ± {metrics['degree_std']:.2f}")
        print(f"  k ∈ [{metrics['degree_min']}, {metrics['degree_max']}]")

        if metrics['alpha'] is not None:
            print(f"  α = {metrics['alpha']:.2f} ± {metrics['stderr']:.2f}")
            print(f"  R² = {metrics['r_squared']:.3f}")

            # Check if scale-free (α ∈ [2, 3] for typical scale-free)
            if 1.5 <= metrics['alpha'] <= 3.0:
                print(f"  ✅ Scale-free regime (α ∈ [1.5, 3.0])")
            elif metrics['alpha'] < 1.5:
                print(f"  ⚠️  Very weak power-law (α < 1.5)")
            else:
                print(f"  ⚠️  Steep power-law (α > 3.0)")
        else:
            print(f"  ❌ Could not fit power-law")

        print()

    # Save results
    output_file = 'results/powerlaw_degree_distributions.json'
    Path('results').mkdir(exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to {output_file}")

    # Check if any network has α ≈ 1.90
    print("\n" + "="*70)
    print("CHECKING FOR α ≈ 1.90")
    print("="*70)

    found_match = False
    for lang, metrics in results.items():
        if metrics['alpha'] is not None:
            if abs(metrics['alpha'] - 1.90) < 0.3:
                print(f"✅ {lang.upper()}: α = {metrics['alpha']:.2f} ≈ 1.90")
                found_match = True
            else:
                print(f"⚠️  {lang.upper()}: α = {metrics['alpha']:.2f} (not ≈ 1.90)")

    if not found_match:
        print("\n❌ No network has α ≈ 1.90")
        print("The manuscript claim may refer to a different dataset or preprocessing.")

if __name__ == '__main__':
    main()
