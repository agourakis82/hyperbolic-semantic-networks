#!/usr/bin/env python3
"""
EXPERIMENT: Find the Missing α = 1.90

HYPOTHESIS: The α=1.90 refers to IN-DEGREE or OUT-DEGREE distribution
in the original DIRECTED association networks, not the undirected version.

Free association is fundamentally DIRECTED:
  CUE → RESPONSE

We've been analyzing the undirected projection, which may have different scaling.
"""

import pandas as pd
import networkx as nx
import numpy as np
from scipy.stats import linregress
import json
from pathlib import Path

def fit_powerlaw_loglog(degrees):
    """Fit power-law using log-log linear regression."""
    if len(degrees) == 0:
        return None, None, None

    # Count frequency
    unique, counts = np.unique(degrees, return_counts=True)
    prob = counts / len(degrees)

    # Remove k=0
    mask = unique > 0
    unique = unique[mask]
    prob = prob[mask]

    # Further filter: k >= 2 for stable fit
    mask = unique >= 2
    if mask.sum() < 3:
        mask = unique >= 1

    x_log = np.log10(unique[mask])
    y_log = np.log10(prob[mask])

    # Linear regression
    slope, intercept, r_value, p_value, std_err = linregress(x_log, y_log)

    alpha = -slope
    r_squared = r_value**2

    return alpha, r_squared, std_err

def analyze_directed_network(edge_file, source_col, target_col):
    """Analyze directed network and compute in/out degree distributions."""

    df = pd.read_csv(edge_file)

    # Build DIRECTED graph
    G = nx.DiGraph()

    for _, row in df.iterrows():
        source = row[source_col]
        target = row[target_col]
        G.add_edge(source, target)

    # Get LCC (treat as undirected for connectivity)
    G_undirected = G.to_undirected()
    if not nx.is_connected(G_undirected):
        Gcc = max(nx.connected_components(G_undirected), key=len)
        G = G.subgraph(Gcc).copy()

    # Compute degree distributions
    in_degrees = [d for _, d in G.in_degree()]
    out_degrees = [d for _, d in G.out_degree()]
    total_degrees = [G.in_degree(n) + G.out_degree(n) for n in G.nodes()]

    # Fit power-laws
    alpha_in, r2_in, stderr_in = fit_powerlaw_loglog(in_degrees)
    alpha_out, r2_out, stderr_out = fit_powerlaw_loglog(out_degrees)
    alpha_total, r2_total, stderr_total = fit_powerlaw_loglog(total_degrees)

    return {
        'n_nodes': G.number_of_nodes(),
        'n_edges': G.number_of_edges(),
        'in_degree': {
            'mean': np.mean(in_degrees),
            'std': np.std(in_degrees),
            'min': min(in_degrees),
            'max': max(in_degrees),
            'alpha': alpha_in,
            'r_squared': r2_in,
            'stderr': stderr_in
        },
        'out_degree': {
            'mean': np.mean(out_degrees),
            'std': np.std(out_degrees),
            'min': min(out_degrees),
            'max': max(out_degrees),
            'alpha': alpha_out,
            'r_squared': r2_out,
            'stderr': stderr_out
        },
        'total_degree': {
            'mean': np.mean(total_degrees),
            'std': np.std(total_degrees),
            'min': min(total_degrees),
            'max': max(total_degrees),
            'alpha': alpha_total,
            'r_squared': r2_total,
            'stderr': stderr_total
        }
    }

def main():
    print("="*70)
    print("DIRECTED DEGREE DISTRIBUTION EXPERIMENT")
    print("="*70)
    print("\nSearching for α = 1.90 in directed SWOW networks...")
    print()

    # Check if we have the raw SWOW data
    raw_files = {
        'spanish': {
            'path': 'data/es/raw/strength.SWOWRP.R123.20220426.csv',
            'source': 'cue',
            'target': 'response'
        },
        'chinese': {
            'path': 'data/zh/raw/SWOW-ZH24/strength.SWOWZH.R123.20230423.csv',
            'source': 'cue',
            'target': 'response'
        },
        'dutch': {
            'path': 'data/nl/raw/associationData.csv',
            'source': 'cue',
            'target': 'asso1'  # Use first association column
        }
    }

    results = {}

    for lang, config in raw_files.items():
        path = Path(config['path'])

        if not path.exists():
            print(f"❌ {lang.upper()}: File not found: {path}")
            continue

        print(f"\n{'='*70}")
        print(f"{lang.upper()}")
        print(f"{'='*70}")

        try:
            # Sample first 10000 edges for speed
            print(f"Loading {path}...")
            import csv
            csv.field_size_limit(10**7)

            df = pd.read_csv(path, sep=None, engine='python', nrows=10000)

            print(f"Analyzing directed network...")
            stats = analyze_directed_network(
                path,
                config['source'],
                config['target']
            )

            results[lang] = stats

            print(f"\nNetwork: N={stats['n_nodes']}, E={stats['n_edges']}")
            print()

            # Print in-degree
            alpha_in = stats['in_degree']['alpha']
            r2_in = stats['in_degree']['r_squared']
            if alpha_in:
                match_in = "✅ MATCH!" if abs(alpha_in - 1.90) < 0.3 else ""
                print(f"IN-DEGREE:")
                print(f"  ⟨k_in⟩  = {stats['in_degree']['mean']:.2f} ± {stats['in_degree']['std']:.2f}")
                print(f"  α_in    = {alpha_in:.2f} ± {stats['in_degree']['stderr']:.2f}")
                print(f"  R²      = {r2_in:.3f}")
                print(f"  {match_in}")

            # Print out-degree
            alpha_out = stats['out_degree']['alpha']
            r2_out = stats['out_degree']['r_squared']
            if alpha_out:
                match_out = "✅ MATCH!" if abs(alpha_out - 1.90) < 0.3 else ""
                print(f"\nOUT-DEGREE:")
                print(f"  ⟨k_out⟩ = {stats['out_degree']['mean']:.2f} ± {stats['out_degree']['std']:.2f}")
                print(f"  α_out   = {alpha_out:.2f} ± {stats['out_degree']['stderr']:.2f}")
                print(f"  R²      = {r2_out:.3f}")
                print(f"  {match_out}")

            # Print total (undirected)
            alpha_total = stats['total_degree']['alpha']
            r2_total = stats['total_degree']['r_squared']
            if alpha_total:
                match_total = "✅ MATCH!" if abs(alpha_total - 1.90) < 0.3 else ""
                print(f"\nTOTAL DEGREE (undirected):")
                print(f"  ⟨k_tot⟩ = {stats['total_degree']['mean']:.2f} ± {stats['total_degree']['std']:.2f}")
                print(f"  α_tot   = {alpha_total:.2f} ± {stats['total_degree']['stderr']:.2f}")
                print(f"  R²      = {r2_total:.3f}")
                print(f"  {match_total}")

        except Exception as e:
            print(f"❌ Error: {e}")
            continue

    # Save results
    if results:
        output_dir = Path('results/experiments')
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / 'directed_powerlaw_experiment.json'
        with open(output_file, 'w') as f:
            json.dump({
                'experiment': 'directed_powerlaw',
                'hypothesis': 'α=1.90 appears in in-degree or out-degree',
                'results': results
            }, f, indent=2)

        print(f"\n{'='*70}")
        print("RESULTS SAVED")
        print(f"{'='*70}")
        print(f"File: {output_file}")

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")

    found_match = False

    for lang, stats in results.items():
        print(f"\n{lang.upper()}:")

        alpha_in = stats['in_degree']['alpha']
        alpha_out = stats['out_degree']['alpha']
        alpha_total = stats['total_degree']['alpha']

        if alpha_in and abs(alpha_in - 1.90) < 0.3:
            print(f"  ✅ IN-DEGREE: α = {alpha_in:.2f} ≈ 1.90")
            found_match = True
        elif alpha_in:
            print(f"  ⚠️  IN-DEGREE: α = {alpha_in:.2f}")

        if alpha_out and abs(alpha_out - 1.90) < 0.3:
            print(f"  ✅ OUT-DEGREE: α = {alpha_out:.2f} ≈ 1.90")
            found_match = True
        elif alpha_out:
            print(f"  ⚠️  OUT-DEGREE: α = {alpha_out:.2f}")

        if alpha_total and abs(alpha_total - 1.90) < 0.3:
            print(f"  ✅ TOTAL: α = {alpha_total:.2f} ≈ 1.90")
            found_match = True
        elif alpha_total:
            print(f"  ⚠️  TOTAL: α = {alpha_total:.2f}")

    print()

    if found_match:
        print("🎉 SUCCESS: Found α ≈ 1.90 in directed degree distributions!")
    else:
        print("❌ α = 1.90 not found in directed analysis either.")
        print("\nPossible remaining explanations:")
        print("  1. Different sample/preprocessing in manuscript")
        print("  2. Entire network (not N=500 sample)")
        print("  3. Different fitting method (MLE vs log-log)")
        print("  4. Typo in manuscript (should be α ≈ 2.9)")

if __name__ == '__main__':
    main()
