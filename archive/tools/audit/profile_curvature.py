#!/usr/bin/env python3
"""
Profile curvature computation to identify bottlenecks.

This script profiles compute_curvature_FINAL.py to identify:
- O(n³) operations
- Memory leaks
- Inefficient loops
- Time spent in each function
"""

import cProfile
import pstats
import io
import sys
from pathlib import Path
import time
import tracemalloc
import json
from datetime import datetime

# Add code directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'code' / 'analysis'))

def profile_curvature_computation():
    """Profile the curvature computation function."""
    
    # Import after path setup
    import pandas as pd
    import networkx as nx
    from GraphRicciCurvature.OllivierRicci import OllivierRicci
    import numpy as np
    
    # Create test data (small network for quick profiling)
    print("Creating test network...")
    n_nodes = 100
    G = nx.erdos_renyi_graph(n_nodes, 0.1, seed=42)
    
    # Add weights
    for u, v in G.edges():
        G[u][v]['weight'] = 1.0
    
    print(f"Test network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # Profile memory
    tracemalloc.start()
    
    # Profile execution
    profiler = cProfile.Profile()
    profiler.enable()
    
    start_time = time.time()
    
    # Compute curvature
    orc = OllivierRicci(G, alpha=0.5, verbose="ERROR")
    orc.compute_ricci_curvature()
    
    end_time = time.time()
    profiler.disable()
    
    # Get memory snapshot
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Get profiling stats
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s)
    ps.sort_stats('cumulative')
    ps.print_stats(30)  # Top 30 functions
    
    profile_output = s.getvalue()
    
    # Extract key metrics
    stats_dict = {}
    for stat in ps.stats:
        func_name = f"{stat[0]}:{stat[1]}({stat[2]})"
        call_count = ps.stats[stat][0]
        total_time = ps.stats[stat][2]
        cumulative_time = ps.stats[stat][3]
        
        stats_dict[func_name] = {
            'call_count': call_count,
            'total_time': total_time,
            'cumulative_time': cumulative_time
        }
    
    results = {
        'network_size': {
            'nodes': G.number_of_nodes(),
            'edges': G.number_of_edges()
        },
        'timing': {
            'total_time_seconds': end_time - start_time,
            'time_per_node': (end_time - start_time) / G.number_of_nodes(),
            'time_per_edge': (end_time - start_time) / G.number_of_edges()
        },
        'memory': {
            'peak_memory_mb': peak / 1024 / 1024,
            'current_memory_mb': current / 1024 / 1024
        },
        'top_functions': dict(sorted(
            stats_dict.items(),
            key=lambda x: x[1]['cumulative_time'],
            reverse=True
        )[:20]),
        'profile_output': profile_output,
        'timestamp': datetime.now().isoformat()
    }
    
    return results

def profile_multiple_sizes():
    """Profile curvature computation for multiple network sizes."""
    
    import networkx as nx
    from GraphRicciCurvature.OllivierRicci import OllivierRicci
    import time
    
    sizes = [50, 100, 200, 500]
    results = []
    
    for n in sizes:
        print(f"\nProfiling network size: {n} nodes")
        
        # Create test network
        G = nx.erdos_renyi_graph(n, 0.1, seed=42)
        for u, v in G.edges():
            G[u][v]['weight'] = 1.0
        
        # Time computation
        start = time.time()
        orc = OllivierRicci(G, alpha=0.5, verbose="ERROR")
        orc.compute_ricci_curvature()
        elapsed = time.time() - start
        
        results.append({
            'nodes': n,
            'edges': G.number_of_edges(),
            'time_seconds': elapsed,
            'time_per_node': elapsed / n,
            'time_per_edge': elapsed / G.number_of_edges()
        })
        
        print(f"  Time: {elapsed:.2f}s ({elapsed/n:.4f}s per node)")
    
    return results

if __name__ == '__main__':
    print("="*80)
    print("CURVATURE COMPUTATION PROFILING")
    print("="*80)
    
    # Single detailed profile
    print("\n1. Detailed profiling...")
    detailed_results = profile_curvature_computation()
    
    # Multiple sizes
    print("\n2. Scaling analysis...")
    scaling_results = profile_multiple_sizes()
    
    # Save results
    output_dir = Path(__file__).parent.parent / 'docs' / 'audit'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save detailed profile
    with open(output_dir / 'curvature_profile_detailed.json', 'w') as f:
        json.dump(detailed_results, f, indent=2)
    
    # Save scaling analysis
    with open(output_dir / 'curvature_scaling.json', 'w') as f:
        json.dump(scaling_results, f, indent=2)
    
    # Save human-readable profile
    with open(output_dir / 'curvature_profile.txt', 'w') as f:
        f.write("="*80 + "\n")
        f.write("CURVATURE COMPUTATION PROFILING REPORT\n")
        f.write("="*80 + "\n\n")
        f.write(f"Timestamp: {detailed_results['timestamp']}\n\n")
        f.write("TIMING METRICS\n")
        f.write("-"*80 + "\n")
        f.write(f"Total time: {detailed_results['timing']['total_time_seconds']:.2f}s\n")
        f.write(f"Time per node: {detailed_results['timing']['time_per_node']:.4f}s\n")
        f.write(f"Time per edge: {detailed_results['timing']['time_per_edge']:.4f}s\n\n")
        f.write("MEMORY METRICS\n")
        f.write("-"*80 + "\n")
        f.write(f"Peak memory: {detailed_results['memory']['peak_memory_mb']:.2f} MB\n")
        f.write(f"Current memory: {detailed_results['memory']['current_memory_mb']:.2f} MB\n\n")
        f.write("TOP FUNCTIONS BY CUMULATIVE TIME\n")
        f.write("-"*80 + "\n")
        for func, stats in list(detailed_results['top_functions'].items())[:10]:
            f.write(f"{func}\n")
            f.write(f"  Calls: {stats['call_count']}\n")
            f.write(f"  Total time: {stats['total_time']:.4f}s\n")
            f.write(f"  Cumulative time: {stats['cumulative_time']:.4f}s\n\n")
        f.write("FULL PROFILE OUTPUT\n")
        f.write("-"*80 + "\n")
        f.write(detailed_results['profile_output'])
        f.write("\n\nSCALING ANALYSIS\n")
        f.write("-"*80 + "\n")
        for r in scaling_results:
            f.write(f"Nodes: {r['nodes']}, Edges: {r['edges']}\n")
            f.write(f"  Time: {r['time_seconds']:.2f}s\n")
            f.write(f"  Time per node: {r['time_per_node']:.4f}s\n")
            f.write(f"  Time per edge: {r['time_per_edge']:.6f}s\n\n")
    
    print(f"\n✅ Results saved to {output_dir}/")
    print(f"   - curvature_profile_detailed.json")
    print(f"   - curvature_scaling.json")
    print(f"   - curvature_profile.txt")

