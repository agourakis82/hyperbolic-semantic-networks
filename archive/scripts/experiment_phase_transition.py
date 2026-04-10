#!/usr/bin/env python3
"""
EXPERIMENT: Phase Transition from Hyperbolic to Spherical Geometry

HYPOTHESIS: The transition occurs when ⟨k⟩² ≈ N

This will create synthetic networks with controlled sparsity and measure curvature
to verify the exact transition point.

PREDICTION:
- ⟨k⟩²/N << 1: κ < 0 (hyperbolic)
- ⟨k⟩²/N ≈ 1:  κ ≈ 0 (transition)
- ⟨k⟩²/N >> 1: κ > 0 (spherical)
"""

import networkx as nx
import numpy as np
import json
from pathlib import Path
import matplotlib.pyplot as plt
from tqdm import tqdm

# Try to import GraphRicciCurvature
try:
    from GraphRicciCurvature.OllivierRicci import OllivierRicci
    HAS_CURVATURE = True
except ImportError:
    print("⚠️  GraphRicciCurvature not available")
    print("   Install: pip install GraphRicciCurvature")
    HAS_CURVATURE = False

def create_configuration_model(N, k_sequence):
    """Create random graph with given degree sequence (configuration model)."""
    # Ensure sum of degrees is even
    if sum(k_sequence) % 2 != 0:
        k_sequence[-1] += 1

    # Create graph
    G = nx.configuration_model(k_sequence, create_using=nx.Graph())

    # Remove self-loops and multiple edges
    G = nx.Graph(G)
    G.remove_edges_from(nx.selfloop_edges(G))

    # Get LCC
    if not nx.is_connected(G):
        Gcc = max(nx.connected_components(G), key=len)
        G = G.subgraph(Gcc).copy()

    return G

def create_random_regular(N, k):
    """Create random k-regular graph."""
    if N * k % 2 != 0:
        k += 1

    try:
        G = nx.random_regular_graph(k, N)
        return G
    except:
        # Fallback to configuration model
        k_sequence = [k] * N
        return create_configuration_model(N, k_sequence)

def compute_curvature_stats(G, alpha=0.5):
    """Compute Ollivier-Ricci curvature statistics for graph."""
    if not HAS_CURVATURE:
        return None

    # Compute curvature
    orc = OllivierRicci(G, alpha=alpha, verbose="ERROR")
    orc.compute_ricci_curvature()

    # Extract curvatures
    curvatures = [orc.G[u][v]['ricciCurvature'] for u, v in orc.G.edges()]

    if len(curvatures) == 0:
        return None

    return {
        'kappa_mean': np.mean(curvatures),
        'kappa_std': np.std(curvatures),
        'kappa_median': np.median(curvatures),
        'kappa_min': np.min(curvatures),
        'kappa_max': np.max(curvatures),
        'n_edges': len(curvatures)
    }

def run_phase_transition_experiment():
    """
    Run systematic experiment varying ⟨k⟩ at fixed N.

    Test values:
    - N = 500 (like our SWOW networks)
    - ⟨k⟩ ∈ [2, 4, 6, 8, 10, 15, 20, 30, 40, 50, 60]

    Critical prediction: Transition near √N ≈ 22
    """

    if not HAS_CURVATURE:
        print("Cannot run experiment without GraphRicciCurvature library")
        print("\nTo install:")
        print("  pip install GraphRicciCurvature")
        return

    N = 500
    k_values = [2, 3, 4, 6, 8, 10, 15, 20, 25, 30, 40, 50, 60]

    # Critical threshold: √N
    k_critical = int(np.sqrt(N))

    print("="*70)
    print("PHASE TRANSITION EXPERIMENT")
    print("="*70)
    print(f"\nFixed network size: N = {N}")
    print(f"Varying average degree: ⟨k⟩ ∈ {k_values}")
    print(f"\nCritical prediction: Transition near ⟨k⟩ ≈ √N = {k_critical}")
    print(f"  (where ⟨k⟩²/N ≈ 1)")
    print()

    results = []

    for k in k_values:
        print(f"\n{'='*70}")
        print(f"Testing ⟨k⟩ = {k}")
        print(f"{'='*70}")

        # Compute critical ratio
        ratio = k**2 / N
        print(f"  ⟨k⟩²/N = {k}²/{N} = {ratio:.3f}")

        # Predict geometry
        if ratio < 0.5:
            predicted = "HYPERBOLIC (κ < 0)"
        elif ratio < 2.0:
            predicted = "TRANSITION (κ ≈ 0)"
        else:
            predicted = "SPHERICAL (κ > 0)"

        print(f"  Predicted: {predicted}")

        # Create random regular graph
        print(f"  Creating random {k}-regular graph...")
        G = create_random_regular(N, k)

        n_actual = G.number_of_nodes()
        e_actual = G.number_of_edges()
        k_actual = 2 * e_actual / n_actual

        print(f"  Created: N={n_actual}, E={e_actual}, ⟨k⟩={k_actual:.2f}")

        # Compute curvature
        print(f"  Computing Ollivier-Ricci curvature...")
        curvature_stats = compute_curvature_stats(G, alpha=0.5)

        if curvature_stats is None:
            print("  ❌ Failed to compute curvature")
            continue

        kappa = curvature_stats['kappa_mean']
        kappa_std = curvature_stats['kappa_std']

        # Determine actual geometry
        if kappa < -0.05:
            actual = "HYPERBOLIC"
            symbol = "🔴"
        elif kappa > 0.05:
            actual = "SPHERICAL"
            symbol = "🔵"
        else:
            actual = "EUCLIDEAN/TRANSITION"
            symbol = "⚪"

        print(f"  Result: κ = {kappa:.4f} ± {kappa_std:.4f}")
        print(f"  {symbol} {actual}")

        # Check prediction
        match = (
            (ratio < 0.5 and kappa < -0.05) or
            (ratio > 2.0 and kappa > 0.05) or
            (0.5 <= ratio <= 2.0 and abs(kappa) <= 0.05)
        )

        if match:
            print(f"  ✅ Prediction CORRECT")
        else:
            print(f"  ⚠️  Prediction MISMATCH")

        # Store results
        results.append({
            'k_target': k,
            'k_actual': k_actual,
            'N': n_actual,
            'E': e_actual,
            'ratio': ratio,
            'kappa_mean': kappa,
            'kappa_std': kappa_std,
            'kappa_median': curvature_stats['kappa_median'],
            'kappa_min': curvature_stats['kappa_min'],
            'kappa_max': curvature_stats['kappa_max'],
            'geometry': actual,
            'prediction_match': match
        })

    # Save results
    output_dir = Path('results/experiments')
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / 'phase_transition_experiment.json'
    with open(output_file, 'w') as f:
        json.dump({
            'experiment': 'phase_transition',
            'hypothesis': 'Transition at k²/N ≈ 1',
            'N_fixed': N,
            'k_critical': k_critical,
            'results': results
        }, f, indent=2)

    print(f"\n{'='*70}")
    print("RESULTS SAVED")
    print(f"{'='*70}")
    print(f"File: {output_file}")

    # Analysis
    print(f"\n{'='*70}")
    print("ANALYSIS")
    print(f"{'='*70}")

    # Count geometries
    n_hyperbolic = sum(1 for r in results if r['kappa_mean'] < -0.05)
    n_euclidean = sum(1 for r in results if abs(r['kappa_mean']) <= 0.05)
    n_spherical = sum(1 for r in results if r['kappa_mean'] > 0.05)

    print(f"\nGeometry distribution:")
    print(f"  Hyperbolic: {n_hyperbolic}/{len(results)}")
    print(f"  Euclidean:  {n_euclidean}/{len(results)}")
    print(f"  Spherical:  {n_spherical}/{len(results)}")

    # Find transition point
    print(f"\nFinding transition point...")

    # Sort by k
    sorted_results = sorted(results, key=lambda r: r['k_actual'])

    # Find where κ crosses zero
    transition_k = None
    for i in range(len(sorted_results) - 1):
        k1 = sorted_results[i]['k_actual']
        k2 = sorted_results[i+1]['k_actual']
        kappa1 = sorted_results[i]['kappa_mean']
        kappa2 = sorted_results[i+1]['kappa_mean']

        if kappa1 < 0 and kappa2 > 0:
            # Linear interpolation
            transition_k = k1 + (k2 - k1) * abs(kappa1) / (abs(kappa1) + abs(kappa2))
            print(f"  Transition between ⟨k⟩={k1:.1f} and ⟨k⟩={k2:.1f}")
            print(f"  Estimated: ⟨k⟩ ≈ {transition_k:.1f}")
            break

    if transition_k:
        transition_ratio = transition_k**2 / N
        print(f"  Ratio at transition: ⟨k⟩²/N ≈ {transition_ratio:.2f}")

        if 0.5 <= transition_ratio <= 2.0:
            print(f"  ✅ HYPOTHESIS CONFIRMED: Transition near ⟨k⟩²/N ≈ 1")
        else:
            print(f"  ⚠️  HYPOTHESIS NEEDS REVISION")

    # Accuracy
    n_correct = sum(1 for r in results if r['prediction_match'])
    accuracy = n_correct / len(results) * 100

    print(f"\nPrediction accuracy: {n_correct}/{len(results)} ({accuracy:.1f}%)")

    # Create plot
    print(f"\nGenerating plot...")
    create_phase_diagram(results, N, k_critical, output_dir)

    return results

def create_phase_diagram(results, N, k_critical, output_dir):
    """Create phase diagram plot."""

    k_values = [r['k_actual'] for r in results]
    kappa_values = [r['kappa_mean'] for r in results]
    kappa_std = [r['kappa_std'] for r in results]
    ratios = [r['ratio'] for r in results]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

    # Plot 1: κ vs ⟨k⟩
    colors = ['red' if k < 0 else 'blue' if k > 0 else 'gray' for k in kappa_values]

    ax1.errorbar(k_values, kappa_values, yerr=kappa_std,
                 fmt='o', capsize=5, capthick=2, markersize=8,
                 ecolor='gray', alpha=0.7)
    ax1.scatter(k_values, kappa_values, c=colors, s=100, zorder=3, alpha=0.8)

    ax1.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax1.axvline(x=k_critical, color='green', linestyle='--', linewidth=2,
                label=f'√N = {k_critical}')

    ax1.set_xlabel('Average Degree ⟨k⟩', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Ollivier-Ricci Curvature κ', fontsize=12, fontweight='bold')
    ax1.set_title(f'Phase Transition: Hyperbolic → Spherical (N={N})',
                  fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # Add regime labels
    ax1.text(3, -0.3, 'HYPERBOLIC\nκ < 0', fontsize=10, ha='center',
             bbox=dict(boxstyle='round', facecolor='red', alpha=0.2))
    ax1.text(50, 0.3, 'SPHERICAL\nκ > 0', fontsize=10, ha='center',
             bbox=dict(boxstyle='round', facecolor='blue', alpha=0.2))

    # Plot 2: κ vs ⟨k⟩²/N
    ax2.errorbar(ratios, kappa_values, yerr=kappa_std,
                 fmt='o', capsize=5, capthick=2, markersize=8,
                 ecolor='gray', alpha=0.7)
    ax2.scatter(ratios, kappa_values, c=colors, s=100, zorder=3, alpha=0.8)

    ax2.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax2.axvline(x=1.0, color='green', linestyle='--', linewidth=2,
                label='⟨k⟩²/N = 1')

    ax2.set_xlabel('Sparsity Ratio ⟨k⟩²/N', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Ollivier-Ricci Curvature κ', fontsize=12, fontweight='bold')
    ax2.set_title('Phase Diagram: Critical Ratio', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_xscale('log')

    # Add regime labels
    ax2.text(0.1, -0.3, 'HYPERBOLIC\n⟨k⟩²/N << 1', fontsize=10, ha='center',
             bbox=dict(boxstyle='round', facecolor='red', alpha=0.2))
    ax2.text(10, 0.3, 'SPHERICAL\n⟨k⟩²/N >> 1', fontsize=10, ha='center',
             bbox=dict(boxstyle='round', facecolor='blue', alpha=0.2))

    plt.tight_layout()

    plot_file = output_dir / 'phase_transition_diagram.png'
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    print(f"  Plot saved: {plot_file}")

    plt.close()

if __name__ == '__main__':
    print(__doc__)

    if HAS_CURVATURE:
        results = run_phase_transition_experiment()
    else:
        print("\n⚠️  GraphRicciCurvature library not available")
        print("\nThis experiment requires curvature computation.")
        print("Install with: pip install GraphRicciCurvature")
        print("\nSkipping experiment.")
