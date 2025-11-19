#!/usr/bin/env python3
"""
Build WordNet semantic network from hierarchical relations
Focus on English, top 500-1000 most frequent synsets
"""

import json
import logging
import networkx as nx
import pandas as pd
from pathlib import Path
from collections import Counter
from nltk.corpus import wordnet as wn

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def build_wordnet_network(n_nodes=500):
    """Build WordNet network from hierarchical relations using BFS from root"""
    
    logger.info("="*70)
    logger.info(f"BUILDING WORDNET NETWORK (n={n_nodes})")
    logger.info("="*70)
    logger.info("")
    
    # Start from root concept and do BFS to get connected subgraph
    logger.info("Finding root concepts...")
    root_synsets = []
    for s in wn.all_synsets('n'):
        if not s.hypernyms():  # No hypernyms = root
            root_synsets.append(s)
    
    logger.info(f"  Found {len(root_synsets)} root synsets")
    logger.info(f"  Examples: {[s.name() for s in root_synsets[:5]]}")
    logger.info("")
    
    # BFS from largest root to get connected n_nodes
    logger.info("Performing BFS to select connected nodes...")
    selected_synsets = set()
    queue = [root_synsets[0]]  # Start from first root (entity.n.01)
    visited = set()
    
    while queue and len(selected_synsets) < n_nodes:
        current = queue.pop(0)
        if current in visited:
            continue
        
        visited.add(current)
        selected_synsets.add(current)
        
        # Add children (hyponyms) to queue
        for hypo in current.hyponyms():
            if hypo not in visited and len(selected_synsets) < n_nodes:
                queue.append(hypo)
    
    top_synsets = list(selected_synsets)
    logger.info(f"  Selected {len(top_synsets)} synsets via BFS")
    logger.info(f"  Examples: {[s.name() for s in top_synsets[:10]]}")
    logger.info("")
    
    # Build directed network
    logger.info("Building network from relations...")
    G = nx.DiGraph()
    
    # Add nodes
    for s in top_synsets:
        G.add_node(s.name(), 
                  definition=s.definition(),
                  lemmas=','.join([l.name() for l in s.lemmas()]))
    
    # Add edges from relations
    edge_count = 0
    
    # Hypernym relations (is-a: dog -> mammal)
    for s in top_synsets:
        for hyper in s.hypernyms():
            if hyper.name() in G.nodes():
                G.add_edge(s.name(), hyper.name(), 
                          relation='hypernym', weight=1.0)
                edge_count += 1
    
    # Hyponym relations (has-subtype: mammal -> dog)
    for s in top_synsets:
        for hypo in s.hyponyms():
            if hypo.name() in G.nodes():
                G.add_edge(s.name(), hypo.name(),
                          relation='hyponym', weight=1.0)
                edge_count += 1
    
    # Meronym relations (has-part: car -> wheel)
    for s in top_synsets:
        for mero in s.part_meronyms() + s.substance_meronyms():
            if mero.name() in G.nodes():
                G.add_edge(s.name(), mero.name(),
                          relation='meronym', weight=1.0)
                edge_count += 1
    
    # Holonym relations (part-of: wheel -> car)
    for s in top_synsets:
        for holo in s.part_holonyms() + s.substance_holonyms():
            if holo.name() in G.nodes():
                G.add_edge(s.name(), holo.name(),
                          relation='holonym', weight=1.0)
                edge_count += 1
    
    logger.info(f"  Total edges added: {edge_count:,}")
    logger.info("")
    
    # Network stats
    logger.info("Network Statistics:")
    logger.info(f"  Nodes: {G.number_of_nodes():,}")
    logger.info(f"  Edges: {G.number_of_edges():,}")
    logger.info(f"  Density: {nx.density(G):.6f}")
    
    # Connectivity
    if G.number_of_edges() > 0:
        wcc = list(nx.weakly_connected_components(G))
        lcc = max(wcc, key=len)
        logger.info(f"  Largest connected component: {len(lcc)}/{G.number_of_nodes()} nodes")
        
        # Extract LCC
        G_lcc = G.subgraph(lcc).copy()
        logger.info(f"  LCC edges: {G_lcc.number_of_edges():,}")
        logger.info(f"  LCC density: {nx.density(G_lcc):.6f}")
    else:
        logger.warning("  No edges! Network is empty.")
        G_lcc = G
    
    logger.info("")
    
    # Save edge list
    logger.info("Saving edge list...")
    edges = []
    for u, v, d in G_lcc.edges(data=True):
        edges.append({
            'source': u,
            'target': v,
            'weight': d.get('weight', 1.0),
            'relation': d.get('relation', 'unknown')
        })
    
    df = pd.DataFrame(edges)
    
    output_dir = Path('data/processed')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'wordnet_edges.csv'
    
    df.to_csv(output_file, index=False)
    logger.info(f"  ✅ Saved to: {output_file}")
    logger.info(f"  Total edges: {len(df):,}")
    logger.info("")
    
    # Save metadata
    metadata = {
        'dataset': 'WordNet',
        'type': 'hierarchical_taxonomy',
        'n_nodes_total': G.number_of_nodes(),
        'n_edges_total': G.number_of_edges(),
        'n_nodes_lcc': G_lcc.number_of_nodes(),
        'n_edges_lcc': G_lcc.number_of_edges(),
        'density': nx.density(G_lcc),
        'relations': ['hypernym', 'hyponym', 'meronym', 'holonym']
    }
    
    with open(output_dir / 'wordnet_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info("="*70)
    logger.info("✅ WORDNET NETWORK CONSTRUCTION COMPLETE")
    logger.info("="*70)
    
    return output_file


if __name__ == '__main__':
    build_wordnet_network(n_nodes=500)

