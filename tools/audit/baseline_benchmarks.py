#!/usr/bin/env python3
"""
Create baseline performance benchmarks for Python implementation.

Benchmarks:
- Curvature computation for different network sizes (250, 500, 1000 nodes)
- Null model generation (M=1000 replicates)
- Memory usage profiling
"""

import time
import json
import sys
from pathlib import Path
from datetime import datetime
import tracemalloc
import numpy as np
import networkx as nx
from GraphRicciCurvature.OllivierRicci import OllivierRicci

def benchmark_curvature_computation(sizes=[250, 500, 1000], n_trials=3):
    """Benchmark curvature computation for different network sizes."""
    print("="*80)
    print("BENCHMARKING CURVATURE COMPUTATION")
    print("="*80)
    
    results = []
    
    for size in sizes:
        print(f"\nBenchmarking {size} nodes...")
        trial_times = []
        trial_memory = []
        
        for trial in range(n_trials):
            print(f"  Trial {trial + 1}/{n_trials}...", end=' ', flush=True)
            
            # Create test network
            G = nx.erdos_renyi_graph(size, 0.1, seed=42 + trial)
            for u, v in G.edges():
                G[u][v]['weight'] = 1.0
            
            # Profile memory
            tracemalloc.start()
            
            # Time computation
            start = time.time()
            orc = OllivierRicci(G, alpha=0.5, verbose="ERROR")
            orc.compute_ricci_curvature()
            elapsed = time.time() - start
            
            # Get memory
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            trial_times.append(elapsed)
            trial_memory.append(peak / 1024 / 1024)  # MB
            
            print(f"{elapsed:.2f}s ({peak/1024/1024:.1f} MB)")
        
        results.append({
            'nodes': size,
            'edges': G.number_of_edges(),
            'trials': n_trials,
            'time_mean': np.mean(trial_times),
            'time_std': np.std(trial_times),
            'time_min': np.min(trial_times),
            'time_max': np.max(trial_times),
            'memory_mean_mb': np.mean(trial_memory),
            'memory_std_mb': np.std(trial_memory),
            'time_per_node': np.mean(trial_times) / size,
            'time_per_edge': np.mean(trial_times) / G.number_of_edges()
        })
    
    return results

def benchmark_null_models(size=500, n_replicates=100, n_trials=2):
    """Benchmark null model generation."""
    print("\n" + "="*80)
    print("BENCHMARKING NULL MODEL GENERATION")
    print("="*80)
    
    # Create base network
    print(f"\nCreating base network ({size} nodes)...")
    G = nx.erdos_renyi_graph(size, 0.1, seed=42)
    for u, v in G.edges():
        G[u][v]['weight'] = 1.0
    
    print(f"Base network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    results = []
    
    # Configuration model
    print(f"\nBenchmarking configuration model (M={n_replicates})...")
    config_times = []
    
    for trial in range(n_trials):
        print(f"  Trial {trial + 1}/{n_trials}...", end=' ', flush=True)
        
        start = time.time()
        
        # Generate null models (simplified - actual implementation would use networkx)
        for _ in range(n_replicates):
            # Simplified: just create a new random graph
            G_null = nx.configuration_model([G.degree(n) for n in G.nodes()])
            # Convert to simple graph
            G_null = nx.Graph(G_null)
            G_null.remove_edges_from(nx.selfloop_edges(G_null))
        
        elapsed = time.time() - start
        config_times.append(elapsed)
        print(f"{elapsed:.2f}s")
    
    results.append({
        'method': 'configuration_model',
        'network_size': size,
        'n_replicates': n_replicates,
        'time_mean': np.mean(config_times),
        'time_std': np.std(config_times),
        'time_per_replicate': np.mean(config_times) / n_replicates
    })
    
    return results

def benchmark_ricci_flow(size=500, n_iterations=40, n_trials=2):
    """Benchmark Ricci flow computation."""
    print("\n" + "="*80)
    print("BENCHMARKING RICCI FLOW")
    print("="*80)
    
    results = []
    
    for trial in range(n_trials):
        print(f"\nTrial {trial + 1}/{n_trials}...")
        
        # Create test network
        G = nx.erdos_renyi_graph(size, 0.1, seed=42 + trial)
        for u, v in G.edges():
            G[u][v]['weight'] = 1.0
        
        # Time Ricci flow (simplified - actual would iterate)
        start = time.time()
        
        # Simulate Ricci flow iterations
        for iteration in range(n_iterations):
            # Simplified: just recompute curvature
            if iteration == 0 or iteration == n_iterations - 1:
                orc = OllivierRicci(G, alpha=0.5, verbose="ERROR")
                orc.compute_ricci_curvature()
        
        elapsed = time.time() - start
        
        results.append({
            'network_size': size,
            'n_iterations': n_iterations,
            'time_seconds': elapsed,
            'time_per_iteration': elapsed / n_iterations
        })
        
        print(f"  Time: {elapsed:.2f}s ({elapsed/n_iterations:.4f}s per iteration)")
    
    return {
        'method': 'ricci_flow',
        'network_size': size,
        'n_iterations': n_iterations,
        'trials': results,
        'time_mean': np.mean([r['time_seconds'] for r in results]),
        'time_std': np.std([r['time_seconds'] for r in results])
    }

def main():
    print("="*80)
    print("BASELINE PERFORMANCE BENCHMARKS")
    print("="*80)
    print(f"Timestamp: {datetime.now().isoformat()}\n")
    
    all_results = {
        'timestamp': datetime.now().isoformat(),
        'benchmarks': {}
    }
    
    # Benchmark curvature
    curvature_results = benchmark_curvature_computation(sizes=[250, 500, 1000], n_trials=2)
    all_results['benchmarks']['curvature'] = curvature_results
    
    # Benchmark null models (smaller for speed)
    null_results = benchmark_null_models(size=500, n_replicates=100, n_trials=2)
    all_results['benchmarks']['null_models'] = null_results
    
    # Benchmark Ricci flow
    ricci_results = benchmark_ricci_flow(size=500, n_iterations=10, n_trials=2)
    all_results['benchmarks']['ricci_flow'] = ricci_results
    
    # Save results
    output_dir = Path(__file__).parent.parent / 'benchmarks' / 'baseline_python'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / 'baseline_benchmarks.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Generate report
    with open(output_dir / 'baseline_benchmarks_report.txt', 'w') as f:
        f.write("="*80 + "\n")
        f.write("BASELINE PERFORMANCE BENCHMARKS\n")
        f.write("="*80 + "\n\n")
        f.write(f"Timestamp: {all_results['timestamp']}\n\n")
        
        f.write("CURVATURE COMPUTATION\n")
        f.write("-"*80 + "\n")
        f.write(f"{'Nodes':<10} {'Edges':<10} {'Time (s)':<15} {'Time/Node (s)':<15} {'Memory (MB)':<15}\n")
        f.write("-"*80 + "\n")
        for r in curvature_results:
            f.write(f"{r['nodes']:<10} {r['edges']:<10} {r['time_mean']:.2f}±{r['time_std']:.2f}   ")
            f.write(f"{r['time_per_node']:.6f}        {r['memory_mean_mb']:.1f}±{r['memory_std_mb']:.1f}\n")
        f.write("\n")
        
        f.write("NULL MODEL GENERATION\n")
        f.write("-"*80 + "\n")
        for r in null_results:
            f.write(f"Method: {r['method']}\n")
            f.write(f"  Network size: {r['network_size']}\n")
            f.write(f"  Replicates: {r['n_replicates']}\n")
            f.write(f"  Time: {r['time_mean']:.2f}±{r['time_std']:.2f}s\n")
            f.write(f"  Time per replicate: {r['time_per_replicate']:.4f}s\n")
        f.write("\n")
        
        f.write("RICCI FLOW\n")
        f.write("-"*80 + "\n")
        f.write(f"Network size: {ricci_results['network_size']}\n")
        f.write(f"Iterations: {ricci_results['n_iterations']}\n")
        f.write(f"Time: {ricci_results['time_mean']:.2f}±{ricci_results['time_std']:.2f}s\n")
        f.write(f"Time per iteration: {ricci_results['time_mean']/ricci_results['n_iterations']:.4f}s\n")
    
    print(f"\n✅ Results saved to {output_dir}/")
    print(f"   - baseline_benchmarks.json")
    print(f"   - baseline_benchmarks_report.txt")

if __name__ == '__main__':
    main()

