#!/usr/bin/env python3
"""
Simple direct build for Greek and Portuguese networks
"""
import gzip
import json
import networkx as nx
import pandas as pd
from pathlib import Path
from collections import Counter
from tqdm import tqdm

def build_network(lang_code, lang_name, min_weight=2.0, n_nodes=500):
    print(f"\n{'='*70}")
    print(f"BUILDING {lang_name.upper()} NETWORK")
    print(f"{'='*70}\n")
    
    input_file = 'data/raw/conceptnet/conceptnet-assertions-5.7.0.csv.gz'
    
    # Parse
    print(f"Parsing ConceptNet for language '{lang_code}'...")
    edges_filtered = []
    node_freq = Counter()
    
    with gzip.open(input_file, 'rt', encoding='utf-8') as f:
        for i, line in enumerate(tqdm(f, desc=f"{lang_name}", unit=" lines")):
            if i == 0:
                continue
            
            try:
                parts = line.strip().split('\t')
                if len(parts) < 5:
                    continue
                
                rel = parts[1]
                start_uri = parts[2]
                end_uri = parts[3]
                
                # Weight
                try:
                    edge_data = json.loads(parts[4])
                    weight = edge_data.get('weight', 1.0)
                except:
                    weight = 1.0
                
                # Filter by language
                if f'/c/{lang_code}/' in start_uri and f'/c/{lang_code}/' in end_uri and weight >= min_weight:
                    start_concept = start_uri.split('/')[3] if len(start_uri.split('/')) >= 4 else None
                    end_concept = end_uri.split('/')[3] if len(end_uri.split('/')) >= 4 else None
                    
                    if start_concept and end_concept:
                        edges_filtered.append({
                            'source': start_concept,
                            'target': end_concept,
                            'relation': rel,
                            'weight': weight
                        })
                        node_freq[start_concept] += 1
                        node_freq[end_concept] += 1
            except:
                continue
    
    print(f"\nParsed {len(edges_filtered):,} edges")
    print(f"Unique nodes: {len(node_freq):,}")
    
    # Select top nodes
    top_nodes = [node for node, freq in node_freq.most_common(n_nodes)]
    print(f"\nTop {n_nodes} nodes: {top_nodes[:10]}")
    
    # Filter edges
    edges_final = [e for e in edges_filtered 
                   if e['source'] in top_nodes and e['target'] in top_nodes]
    print(f"Edges in final network: {len(edges_final):,}")
    
    # Build graph
    G = nx.DiGraph()
    for e in edges_final:
        G.add_edge(e['source'], e['target'], weight=e['weight'], relation=e['relation'])
    
    # LCC
    wcc = list(nx.weakly_connected_components(G))
    lcc = max(wcc, key=len)
    G_lcc = G.subgraph(lcc).copy()
    
    print(f"\nNetwork Stats (LCC):")
    print(f"  Nodes: {G_lcc.number_of_nodes():,}")
    print(f"  Edges: {G_lcc.number_of_edges():,}")
    print(f"  Density: {nx.density(G_lcc):.6f}")
    
    # Save
    edges_save = []
    for u, v, d in G_lcc.edges(data=True):
        edges_save.append({
            'source': u,
            'target': v,
            'weight': d['weight'],
            'relation': d.get('relation', 'unknown')
        })
    
    df = pd.DataFrame(edges_save)
    output_dir = Path('data/processed')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f'conceptnet_{lang_code}_edges.csv'
    
    df.to_csv(output_file, index=False)
    print(f"\n✅ Saved to: {output_file}")
    
    # Metadata
    metadata = {
        'dataset': 'ConceptNet',
        'language': lang_code,
        'n_nodes': G_lcc.number_of_nodes(),
        'n_edges': G_lcc.number_of_edges(),
        'density': nx.density(G_lcc)
    }
    
    with open(output_dir / f'conceptnet_{lang_code}_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ {lang_name.upper()} NETWORK COMPLETE!\n")
    return output_file

# Build both
build_network('el', 'Greek', min_weight=1.5, n_nodes=500)
build_network('pt', 'Portuguese', min_weight=2.0, n_nodes=500)

