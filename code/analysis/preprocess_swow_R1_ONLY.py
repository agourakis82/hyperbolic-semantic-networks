#!/usr/bin/env python3
"""
SWOW Preprocessing - R1 ONLY (First Response)
==============================================
Corrected preprocessing matching original analysis methodology.

KEY PARAMETERS (matching Table 1 original analysis):
- Use ONLY R1 (first response), not R1+R2+R3
- Top 500 most frequent words
- Result: ~750-850 edges per language (sparse networks)

Original edge counts from Table 1:
- Spanish: 776 edges
- English: 815 edges  
- Dutch: 817 edges
- Chinese: 799 edges

This script should reproduce similar edge counts.
"""

import pandas as pd
import networkx as nx
from pathlib import Path
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def preprocess_swow_generic(file_path: Path, cue_col: str, response_col: str, 
                             top_n: int = 500, language: str = "unknown") -> pd.DataFrame:
    """
    Generic SWOW preprocessor using ONLY FIRST RESPONSE (R1).
    
    Args:
        file_path: Path to SWOW CSV file
        cue_col: Name of cue column
        response_col: Name of R1 column
        top_n: Number of top frequent words to keep
        language: Language name for logging
    
    Returns:
        DataFrame with columns: source, target, weight
    """
    logger.info(f"[{language}] Loading: {file_path}")
    
    df = pd.read_csv(file_path, low_memory=False)
    logger.info(f"[{language}] Loaded {len(df)} rows")
    
    # Count word frequencies (cues + R1 responses only)
    word_counts = defaultdict(int)
    
    # Count cues
    if cue_col in df.columns:
        for cue in df[cue_col]:
            if pd.notna(cue):
                word_counts[str(cue).lower().strip()] += 1
    
    # Count R1 responses ONLY
    if response_col in df.columns:
        for resp in df[response_col]:
            if pd.notna(resp):
                word_counts[str(resp).lower().strip()] += 1
    
    # Get top N most frequent words
    top_words = set(sorted(word_counts, key=word_counts.get, reverse=True)[:top_n])
    logger.info(f"[{language}] Top {top_n} words selected from {len(word_counts)} unique words")
    
    # Build edge list (cue → R1 ONLY)
    edge_weights = defaultdict(int)
    
    for _, row in df.iterrows():
        cue = str(row[cue_col]).lower().strip() if pd.notna(row.get(cue_col)) else None
        resp = str(row[response_col]).lower().strip() if pd.notna(row.get(response_col)) else None
        
        if cue and resp and cue in top_words and resp in top_words and cue != resp:
            edge_weights[(cue, resp)] += 1
    
    # Convert to DataFrame
    edges = []
    for (source, target), weight in edge_weights.items():
        edges.append({'source': source, 'target': target, 'weight': float(weight)})
    
    df_edges = pd.DataFrame(edges)
    
    logger.info(f"[{language}] Generated {len(df_edges)} edges from {len(top_words)} nodes")
    logger.info(f"[{language}] Weight range: [{df_edges['weight'].min():.0f}, {df_edges['weight'].max():.0f}]")
    
    return df_edges

def preprocess_english(output_dir: Path):
    """English SWOW - R1 only"""
    file_path = Path("data/raw/SWOW-EN.R100.20180827.csv")
    df = preprocess_swow_generic(file_path, cue_col='cue', response_col='R1', language='English')
    
    output_path = output_dir / "english_edges_R1.csv"
    df.to_csv(output_path, index=False)
    logger.info(f"Saved: {output_path}")
    
    # Verify edge count
    G = nx.DiGraph()
    for _, row in df.iterrows():
        G.add_edge(row['source'], row['target'], weight=row['weight'])
    G_undir = G.to_undirected()
    logger.info(f"✅ English: {G_undir.number_of_nodes()} nodes, {G_undir.number_of_edges()} edges (target: ~815)")

def preprocess_spanish(output_dir: Path):
    """Spanish SWOW - R1 only"""
    file_path = Path("data/raw/SWOWRP.R70.20220426.csv")  # Rioplatense Spanish
    df = preprocess_swow_generic(file_path, cue_col='cue', response_col='R1', language='Spanish')
    
    output_path = output_dir / "spanish_edges_R1.csv"
    df.to_csv(output_path, index=False)
    logger.info(f"Saved: {output_path}")
    
    G = nx.DiGraph()
    for _, row in df.iterrows():
        G.add_edge(row['source'], row['target'], weight=row['weight'])
    G_undir = G.to_undirected()
    logger.info(f"✅ Spanish: {G_undir.number_of_nodes()} nodes, {G_undir.number_of_edges()} edges (target: ~776)")

def preprocess_dutch(output_dir: Path):
    """Dutch SWOW - R1 only"""
    logger.warning("[Dutch] ZIP extraction failed, skipping for now. Will process manually later.")
    logger.info("[Dutch] Target: 500 nodes, ~817 edges")
    return

def preprocess_chinese(output_dir: Path):
    """Chinese SWOW - R1 only"""
    file_path = Path("data/raw/SWOW-ZH24/SWOWZH.R55.20230424.csv")
    
    # Chinese uses 'word' for cue and 'R1' for response
    df_raw = pd.read_csv(file_path, low_memory=False)
    logger.info(f"[Chinese] Columns: {list(df_raw.columns)}")
    
    # Need to identify correct column names
    # Typical Chinese format: 'word' (cue), 'R1' (first response)
    cue_col = 'word' if 'word' in df_raw.columns else 'cue'
    resp_col = 'R1'
    
    df = preprocess_swow_generic(file_path, cue_col=cue_col, response_col=resp_col, language='Chinese')
    
    output_path = output_dir / "chinese_edges_R1.csv"
    df.to_csv(output_path, index=False)
    logger.info(f"Saved: {output_path}")
    
    G = nx.DiGraph()
    for _, row in df.iterrows():
        G.add_edge(row['source'], row['target'], weight=row['weight'])
    G_undir = G.to_undirected()
    logger.info(f"✅ Chinese: {G_undir.number_of_nodes()} nodes, {G_undir.number_of_edges()} edges (target: ~799)")

def main():
    output_dir = Path("data/processed")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    print("="*70)
    print("🔬 SWOW Preprocessing - R1 ONLY (Corrected Methodology)")
    print("="*70)
    print("Goal: Reproduce original analysis with ~750-850 edges per language")
    print()
    
    # Process all 4 languages
    preprocess_spanish(output_dir)
    print()
    preprocess_english(output_dir)
    print()
    preprocess_dutch(output_dir)
    print()
    preprocess_chinese(output_dir)
    print()
    
    print("="*70)
    print("✅ PREPROCESSING COMPLETE")
    print("="*70)
    print()
    print("Next steps:")
    print("1. Verify edge counts match Table 1 (~750-850 range)")
    print("2. Compute OR curvature on these networks")
    print("3. Update Table 1 with correct values")
    print("4. Resolve manuscript inconsistency")
    print()

if __name__ == '__main__':
    main()

