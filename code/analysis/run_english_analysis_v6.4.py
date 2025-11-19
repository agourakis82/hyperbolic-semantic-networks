"""
English Analysis - v6.4.0

Resolve problema de field size com múltiplas estratégias:
1. Chunked reading
2. Smaller sample (250 nodes)
3. R1 file (smaller)
"""
import pandas as pd
import networkx as nx
import numpy as np
from pathlib import Path
import json
from GraphRicciCurvature.OllivierRicci import OllivierRicci
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("ENGLISH ANALYSIS - v6.4.0")
print("=" * 70)

ALPHA = 0.5
result = {}

# Strategy 1: Try R1 file (smaller)
print(f"\n{'=' * 70}")
print("STRATEGY 1: R1 file (smaller dataset)")
print(f"{'=' * 70}")

try:
    import csv
    csv.field_size_limit(10**7)
    
    filepath_r1 = 'data/en/raw/strength.SWOW-EN.R1.20180827.csv'
    print(f"Loading: {filepath_r1}")
    
    df_en = pd.read_csv(filepath_r1, sep=None, engine='python')
    print(f"✓ Loaded {len(df_en):,} rows")
    
    # Build network
    N_EDGES_BUILD = 10000
    df_build = df_en.head(N_EDGES_BUILD)
    G_full = nx.from_pandas_edgelist(df_build, source='cue', target='response', create_using=nx.Graph())
    
    # Get largest connected component
    if not nx.is_connected(G_full):
        largest_cc = max(nx.connected_components(G_full), key=len)
        G_full = G_full.subgraph(largest_cc).copy()
    
    # Sample 500 nodes
    N_NODES_SAMPLE = 500
    if G_full.number_of_nodes() > N_NODES_SAMPLE:
        import random
        random.seed(42)
        start_node = random.choice(list(G_full.nodes()))
        sampled_nodes = {start_node}
        current_nodes = [start_node]
        
        while len(sampled_nodes) < N_NODES_SAMPLE and current_nodes:
            current = current_nodes.pop(0)
            neighbors = list(G_full.neighbors(current))
            for neighbor in neighbors:
                if neighbor not in sampled_nodes:
                    sampled_nodes.add(neighbor)
                    current_nodes.append(neighbor)
                    if len(sampled_nodes) >= N_NODES_SAMPLE:
                        break
        
        G_en = G_full.subgraph(sampled_nodes).copy()
    else:
        G_en = G_full
    
    print(f"Network: {G_en.number_of_nodes()} nodes, {G_en.number_of_edges()} edges")
    
    # Compute OR curvature
    print("Computing Ollivier-Ricci curvature...")
    orc_en = OllivierRicci(G_en, alpha=ALPHA, verbose="ERROR")
    orc_en.compute_ricci_curvature()
    G_en_orc = orc_en.G
    
    curvatures = [G_en_orc[u][v]['ricciCurvature'] for u, v in G_en_orc.edges()]
    mean_curv = np.mean(curvatures)
    std_curv = np.std(curvatures)
    min_curv = np.min(curvatures)
    max_curv = np.max(curvatures)
    median_curv = np.median(curvatures)
    
    print(f"\n✓ Results:")
    print(f"  Mean: {mean_curv:.6f}")
    print(f"  Median: {median_curv:.6f}")
    print(f"  Std: {std_curv:.6f}")
    print(f"  Range: [{min_curv:.3f}, {max_curv:.3f}]")
    
    # Interpretation
    if mean_curv < -0.1:
        geometry = "hyperbolic"
        print(f"  ⭐ Geometry: HYPERBOLIC")
    elif mean_curv > 0.1:
        geometry = "spherical"
        print(f"  ○ Geometry: SPHERICAL")
    else:
        geometry = "euclidean"
        print(f"  ▢ Geometry: EUCLIDEAN")
    
    # Validate range
    if -1 <= min_curv and max_curv <= 1:
        print(f"  ✅ Values in expected range [-1, 1]")
        valid = True
    else:
        print(f"  ⚠️  Values outside expected range!")
        valid = False
    
    result = {
        'strategy': 'R1_file',
        'n_nodes': G_en.number_of_nodes(),
        'n_edges': G_en.number_of_edges(),
        'curvature_mean': float(mean_curv),
        'curvature_median': float(median_curv),
        'curvature_std': float(std_curv),
        'curvature_min': float(min_curv),
        'curvature_max': float(max_curv),
        'geometry': geometry,
        'valid_range': valid,
        'success': True
    }
    
    print(f"\n✅ STRATEGY 1 SUCCESSFUL!")
    
except Exception as e:
    print(f"❌ Strategy 1 failed: {e}")
    result = {'strategy': 'R1_file', 'error': str(e), 'success': False}

# If strategy 1 failed, try strategy 2
if not result.get('success', False):
    print(f"\n{'=' * 70}")
    print("STRATEGY 2: Smaller sample (250 nodes)")
    print(f"{'=' * 70}")
    
    try:
        filepath_r123 = 'data/en/raw/strength.SWOW-EN.R123.20180827.csv'
        
        # Try reading in chunks
        print(f"Reading file in chunks...")
        chunks = []
        for i, chunk in enumerate(pd.read_csv(filepath_r123, sep=None, engine='python', chunksize=5000)):
            chunks.append(chunk)
            if i >= 1:  # Only read 10k rows
                break
        
        df_en = pd.concat(chunks, ignore_index=True)
        print(f"✓ Loaded {len(df_en):,} rows")
        
        # Build smaller network (250 nodes)
        G_full = nx.from_pandas_edgelist(df_en, source='cue', target='response', create_using=nx.Graph())
        
        if not nx.is_connected(G_full):
            largest_cc = max(nx.connected_components(G_full), key=len)
            G_full = G_full.subgraph(largest_cc).copy()
        
        N_NODES_SAMPLE = 250  # Smaller
        if G_full.number_of_nodes() > N_NODES_SAMPLE:
            import random
            random.seed(42)
            start_node = random.choice(list(G_full.nodes()))
            sampled_nodes = {start_node}
            current_nodes = [start_node]
            
            while len(sampled_nodes) < N_NODES_SAMPLE and current_nodes:
                current = current_nodes.pop(0)
                neighbors = list(G_full.neighbors(current))
                for neighbor in neighbors:
                    if neighbor not in sampled_nodes:
                        sampled_nodes.add(neighbor)
                        current_nodes.append(neighbor)
                        if len(sampled_nodes) >= N_NODES_SAMPLE:
                            break
            
            G_en = G_full.subgraph(sampled_nodes).copy()
        else:
            G_en = G_full
        
        print(f"Network: {G_en.number_of_nodes()} nodes, {G_en.number_of_edges()} edges")
        
        # Compute curvature
        print("Computing Ollivier-Ricci curvature...")
        orc_en = OllivierRicci(G_en, alpha=ALPHA, verbose="ERROR")
        orc_en.compute_ricci_curvature()
        G_en_orc = orc_en.G
        
        curvatures = [G_en_orc[u][v]['ricciCurvature'] for u, v in G_en_orc.edges()]
        mean_curv = np.mean(curvatures)
        
        print(f"\n✓ Mean curvature: {mean_curv:.6f}")
        
        result = {
            'strategy': 'smaller_sample_250',
            'n_nodes': G_en.number_of_nodes(),
            'n_edges': G_en.number_of_edges(),
            'curvature_mean': float(mean_curv),
            'geometry': 'hyperbolic' if mean_curv < -0.1 else 'euclidean',
            'success': True
        }
        
        print(f"\n✅ STRATEGY 2 SUCCESSFUL!")
        
    except Exception as e:
        print(f"❌ Strategy 2 failed: {e}")
        result = {'strategy': 'smaller_sample', 'error': str(e), 'success': False}

# Summary
print(f"\n{'=' * 70}")
print("ENGLISH ANALYSIS SUMMARY")
print(f"{'=' * 70}")

if result.get('success', False):
    print(f"\n✅ SUCCESS with strategy: {result['strategy']}")
    print(f"  Nodes: {result['n_nodes']}")
    print(f"  Edges: {result['n_edges']}")
    print(f"  Mean curvature: {result['curvature_mean']:.6f}")
    print(f"  Geometry: {result['geometry'].upper()}")
    
    # Compare with other languages
    other_langs = {
        'es': -0.104,
        'nl': -0.172,
        'zh': -0.189
    }
    
    print(f"\n  Comparison with other languages:")
    for lang, curv in other_langs.items():
        print(f"    {lang.upper()}: {curv:.3f}")
    print(f"    EN: {result['curvature_mean']:.3f}")
    
    all_means = list(other_langs.values()) + [result['curvature_mean']]
    overall_mean = np.mean(all_means)
    print(f"\n  Overall mean (4 languages): {overall_mean:.6f}")
    
    if result['geometry'] == 'hyperbolic':
        print(f"\n  ⭐⭐⭐ UNIVERSALITY: 4/4 languages HYPERBOLIC!")
    else:
        print(f"\n  ⚠️  English shows different geometry")
else:
    print(f"\n❌ FAILED: Could not analyze English")
    print(f"  Reason: {result.get('error', 'unknown')}")
    print(f"\n  → Proceeding with 3 languages (ES, NL, ZH)")

# Save
output_path = 'results/english_analysis_v6.4.json'
Path('results').mkdir(exist_ok=True)
with open(output_path, 'w') as f:
    json.dump(result, f, indent=2)

print(f"\nResults saved to: {output_path}")

print(f"{'=' * 70}\n")

