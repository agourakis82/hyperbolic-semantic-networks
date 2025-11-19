#!/usr/bin/env python3
"""
Extract semantic network from BabelNet for a given language

REQUIRES:
  - BabelNet API key configured in babelnet_conf.yml
  - pip install babelnet

USAGE:
  python extract_babelnet_network.py --language ru --n_nodes 500
  python extract_babelnet_network.py --language ar --n_nodes 500
"""
import argparse
import babelnet as bn
from babelnet.language import Language
import networkx as nx
import pandas as pd
from pathlib import Path
from collections import Counter
import json
import time
from tqdm import tqdm

# Language code mapping
LANG_MAP = {
    'ru': Language.RU,  # Russian
    'ar': Language.AR,  # Arabic
    'en': Language.EN,
    'es': Language.ES,
    'pt': Language.PT,
    'zh': Language.ZH
}

def get_top_concepts(language, n=500):
    """
    Get top N most common concepts for a language
    Using frequent words as seeds
    """
    # Top frequent words per language (manually curated)
    seeds = {
        'ru': ['дом', 'человек', 'время', 'рука', 'дело', 'жизнь', 'день', 'голова',
               'вопрос', 'город', 'место', 'работа', 'сторона', 'страна', 'мир',
               'вид', 'конец', 'слово', 'глаз', 'вода', 'комната', 'друг', 'отец',
               'мать', 'ребенок', 'книга', 'школа', 'война', 'земля', 'народ'],
        'ar': ['بيت', 'إنسان', 'وقت', 'يد', 'حياة', 'يوم', 'رأس', 'مدينة',
               'مكان', 'عمل', 'بلد', 'عالم', 'كلمة', 'عين', 'ماء', 'غرفة',
               'صديق', 'أب', 'أم', 'طفل', 'كتاب', 'مدرسة', 'حرب', 'أرض']
    }
    
    return seeds.get(language, [])[:50]  # Use top 50 as seeds

def extract_babelnet_network(language_code, n_nodes=500, max_queries=900):
    """
    Extract semantic network from BabelNet
    
    Args:
        language_code: 'ru' or 'ar'
        n_nodes: Target number of nodes
        max_queries: Max API queries (respect daily limit of 1000)
    """
    print("="*70)
    print(f"EXTRACTING BABELNET NETWORK - {language_code.upper()}")
    print("="*70)
    print()
    
    lang = LANG_MAP[language_code]
    print(f"Language: {language_code} ({lang})")
    print(f"Target nodes: {n_nodes}")
    print(f"Max queries: {max_queries}")
    print()
    
    # Get seed words
    seeds = get_top_concepts(language_code)
    print(f"Seed concepts: {len(seeds)}")
    print(f"  Samples: {seeds[:10]}")
    print()
    
    # Track synsets and edges
    all_synsets = {}
    edges = []
    query_count = 0
    
    print("Querying BabelNet (respecting rate limits)...")
    print("(This may take several hours due to rate limiting)")
    print()
    
    for seed in tqdm(seeds, desc="Seeds"):
        if query_count >= max_queries:
            print(f"\n⚠️ Reached query limit ({max_queries})")
            break
        
        try:
            # Get synsets for seed word
            synsets = bn.get_synsets(seed, from_langs=[lang])
            query_count += 1
            
            for synset in synsets[:3]:  # Top 3 synsets per seed
                synset_id = str(synset.id)
                
                if synset_id not in all_synsets:
                    all_synsets[synset_id] = {
                        'id': synset_id,
                        'lemmas': [seed],
                        'pos': str(synset.pos) if hasattr(synset, 'pos') else 'UNKNOWN'
                    }
                
                # Get edges (outgoing relations)
                if query_count < max_queries:
                    try:
                        # Query for edges
                        outgoing = synset.outgoing_edges()
                        query_count += 1
                        
                        for edge in outgoing[:10]:  # Top 10 edges
                            target_id = str(edge.id_target)
                            relation = str(edge.pointer.name)
                            
                            edges.append({
                                'source': synset_id,
                                'target': target_id,
                                'relation': relation
                            })
                            
                            # Track target synset
                            if target_id not in all_synsets:
                                all_synsets[target_id] = {
                                    'id': target_id,
                                    'lemmas': [],
                                    'pos': 'UNKNOWN'
                                }
                    except:
                        pass
            
            # Rate limit: 1 query/second to be safe
            time.sleep(1)
            
        except Exception as e:
            print(f"  Error with '{seed}': {e}")
            continue
    
    print()
    print(f"API queries used: {query_count}/{max_queries}")
    print(f"Synsets collected: {len(all_synsets):,}")
    print(f"Edges collected: {len(edges):,}")
    print()
    
    # Build graph
    G = nx.DiGraph()
    for e in edges:
        G.add_edge(e['source'], e['target'], relation=e['relation'])
    
    print(f"Graph stats (raw):")
    print(f"  Nodes: {G.number_of_nodes():,}")
    print(f"  Edges: {G.number_of_edges():,}")
    print()
    
    # LCC
    if G.number_of_nodes() > 0:
        wcc = list(nx.weakly_connected_components(G))
        lcc = max(wcc, key=len)
        G_lcc = G.subgraph(lcc).copy()
        
        print(f"Largest Connected Component:")
        print(f"  Nodes: {G_lcc.number_of_nodes():,}")
        print(f"  Edges: {G_lcc.number_of_edges():,}")
        print(f"  Density: {nx.density(G_lcc):.6f}")
        print()
        
        if G_lcc.number_of_nodes() >= 300:
            # Save
            edges_save = []
            for u, v, d in G_lcc.edges(data=True):
                edges_save.append({
                    'source': u,
                    'target': v,
                    'weight': 1.0,
                    'relation': d.get('relation', 'unknown')
                })
            
            df = pd.DataFrame(edges_save)
            output_dir = Path('data/processed')
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f'babelnet_{language_code}_edges.csv'
            
            df.to_csv(output_file, index=False)
            print(f"✅ Saved to: {output_file}")
            
            # Metadata
            metadata = {
                'dataset': 'BabelNet',
                'language': language_code,
                'source': 'BabelNet API v9',
                'api_queries': query_count,
                'n_nodes': G_lcc.number_of_nodes(),
                'n_edges': G_lcc.number_of_edges(),
                'density': nx.density(G_lcc)
            }
            
            with open(output_dir / f'babelnet_{language_code}_metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✅ {language_code.upper()} BABELNET NETWORK COMPLETE!")
            return output_file
        else:
            print(f"⚠️ LCC too small ({G_lcc.number_of_nodes()} < 300)")
            return None
    else:
        print("❌ No graph created")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--language', required=True, choices=['ru', 'ar'],
                        help='Language code: ru (Russian) or ar (Arabic)')
    parser.add_argument('--n_nodes', type=int, default=500,
                        help='Target number of nodes')
    parser.add_argument('--max_queries', type=int, default=900,
                        help='Max API queries (default 900 to stay under 1000/day limit)')
    
    args = parser.parse_args()
    
    extract_babelnet_network(args.language, args.n_nodes, args.max_queries)

