#!/usr/bin/env python3
"""
Build ConceptNet semantic network
Focus on English, high-quality relations, top nodes
"""

import gzip
import json
import logging
import networkx as nx
import pandas as pd
from pathlib import Path
from collections import Counter
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_conceptnet_uri(uri):
    """Parse ConceptNet URI to extract concept and language"""
    parts = uri.split('/')
    if len(parts) >= 4:
        lang = parts[2]
        concept = parts[3]
        return lang, concept
    return None, None


def build_conceptnet_network(language='en', min_weight=2.0, n_nodes=500):
    """Build ConceptNet network for a specific language"""
    
    logger.info("="*70)
    logger.info(f"BUILDING CONCEPTNET NETWORK (lang={language}, n={n_nodes})")
    logger.info("="*70)
    logger.info("")
    
    # Load ConceptNet assertions
    input_file = 'data/raw/conceptnet/conceptnet-assertions-5.7.0.csv.gz'
    logger.info(f"Loading ConceptNet from: {input_file}")
    
    # Parse file
    logger.info("Parsing edges (this may take a few minutes)...")
    edges_filtered = []
    node_freq = Counter()
    
    with gzip.open(input_file, 'rt', encoding='utf-8') as f:
        for i, line in enumerate(tqdm(f, desc="Parsing", unit=" lines")):
            if i == 0:
                continue  # Skip header
            
            try:
                parts = line.strip().split('\t')
                if len(parts) < 5:
                    continue
                
                rel = parts[1]
                start_uri = parts[2]
                end_uri = parts[3]
                
                # Parse weight (column 4 is JSON with weight)
                try:
                    edge_data = json.loads(parts[4])
                    weight = edge_data.get('weight', 1.0)
                except:
                    weight = 1.0
                
                # Filter by language
                lang_start, concept_start = parse_conceptnet_uri(start_uri)
                lang_end, concept_end = parse_conceptnet_uri(end_uri)
                
                if lang_start == language and lang_end == language and weight >= min_weight:
                    edges_filtered.append({
                        'source': concept_start,
                        'target': concept_end,
                        'relation': rel,
                        'weight': weight
                    })
                    node_freq[concept_start] += 1
                    node_freq[concept_end] += 1
            
            except Exception as e:
                continue
    
    logger.info(f"  Parsed {len(edges_filtered):,} edges (weight >= {min_weight})")
    logger.info(f"  Unique nodes: {len(node_freq):,}")
    logger.info("")
    
    # Select top N nodes by frequency
    logger.info(f"Selecting top {n_nodes} most frequent nodes...")
    top_nodes = [node for node, freq in node_freq.most_common(n_nodes)]
    logger.info(f"  Top nodes: {top_nodes[:10]}")
    logger.info("")
    
    # Filter edges to top nodes
    logger.info("Filtering edges to top nodes...")
    edges_final = [e for e in edges_filtered 
                   if e['source'] in top_nodes and e['target'] in top_nodes]
    logger.info(f"  Edges in final network: {len(edges_final):,}")
    logger.info("")
    
    # Build graph
    logger.info("Building NetworkX graph...")
    G = nx.DiGraph()
    
    for e in edges_final:
        G.add_edge(e['source'], e['target'],
                  weight=e['weight'],
                  relation=e['relation'])
    
    # Get LCC
    logger.info("Extracting largest connected component...")
    wcc = list(nx.weakly_connected_components(G))
    lcc = max(wcc, key=len)
    G_lcc = G.subgraph(lcc).copy()
    
    logger.info("Network Statistics:")
    logger.info(f"  Nodes (LCC): {G_lcc.number_of_nodes():,}")
    logger.info(f"  Edges (LCC): {G_lcc.number_of_edges():,}")
    logger.info(f"  Density: {nx.density(G_lcc):.6f}")
    logger.info(f"  Mean degree: {2*G_lcc.number_of_edges()/G_lcc.number_of_nodes():.2f}")
    logger.info("")
    
    # Save edge list
    logger.info("Saving edge list...")
    edges_save = []
    for u, v, d in G_lcc.edges(data=True):
        edges_save.append({
            'source': u,
            'target': v,
            'weight': d.get('weight', 1.0),
            'relation': d.get('relation', 'unknown')
        })
    
    df = pd.DataFrame(edges_save)
    
    output_dir = Path('data/processed')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f'conceptnet_{language}_edges.csv'
    
    df.to_csv(output_file, index=False)
    logger.info(f"  ✅ Saved to: {output_file}")
    logger.info(f"  Total edges: {len(df):,}")
    logger.info("")
    
    # Save metadata
    metadata = {
        'dataset': 'ConceptNet',
        'version': '5.7.0',
        'language': language,
        'type': 'knowledge_graph',
        'min_weight': min_weight,
        'n_nodes': G_lcc.number_of_nodes(),
        'n_edges': G_lcc.number_of_edges(),
        'density': nx.density(G_lcc),
        'mean_degree': 2*G_lcc.number_of_edges()/G_lcc.number_of_nodes()
    }
    
    with open(output_dir / f'conceptnet_{language}_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info("="*70)
    logger.info("✅ CONCEPTNET NETWORK CONSTRUCTION COMPLETE")
    logger.info("="*70)
    
    return output_file


if __name__ == '__main__':
    build_conceptnet_network(language='en', min_weight=2.0, n_nodes=500)

