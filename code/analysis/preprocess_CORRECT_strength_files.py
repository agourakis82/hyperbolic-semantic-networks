#!/usr/bin/env python3
"""
CORRECT SWOW Preprocessing - Using strength.*.R1.csv files
===========================================================
Uses the CORRECT files mentioned in DATA_DOWNLOAD.md:
- strength.SWOW-EN.R1.20180827.csv
- strength.SWOWRP.R1.20220426.csv  
- strength.SWOWZH.R1.20230423.csv
- strength.SWOW-NL.R1.csv (need to find/extract)

Format of strength files:
cue,response,R1
- R1 is the strength/weight of the association (0-1 normalized)
"""

import pandas as pd
import networkx as nx
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def preprocess_strength_file(file_path: Path, language: str, top_n: int = 500, 
                              strength_threshold: float = 0.06) -> pd.DataFrame:
    """
    Process SWOW strength file (cue, response, R1 format).
    
    Args:
        file_path: Path to strength.*.R1.csv file
        language: Language name for logging
        top_n: Number of top nodes to keep
        strength_threshold: Minimum R1.Strength value (default 0.06)
    
    Returns:
        DataFrame with source, target, weight columns
    """
    logger.info(f"[{language}] Loading: {file_path}")
    
    # Read strength file (auto-detect separator)
    # Try TAB first (English/Spanish), then COMMA (Chinese)
    try:
        df = pd.read_csv(file_path, sep='\t', quoting=1, on_bad_lines='skip')
        if 'cue,response' in str(df.columns):  # Column names merged = wrong separator
            df = pd.read_csv(file_path, sep=',', on_bad_lines='skip')
    except:
        df = pd.read_csv(file_path, sep=',', on_bad_lines='skip')
    
    logger.info(f"[{language}] Loaded {len(df)} associations")
    logger.info(f"[{language}] Columns: {list(df.columns)}")
    
    # Expected columns: cue, response, R1
    if 'cue' not in df.columns or 'response' not in df.columns:
        logger.error(f"[{language}] Missing required columns!")
        return pd.DataFrame()
    
    # Use R1.Strength (normalized) column - THIS IS KEY!
    if 'R1.Strength' not in df.columns:
        logger.error(f"[{language}] Missing R1.Strength column!")
        return pd.DataFrame()
    
    weight_col = 'R1.Strength'
    logger.info(f"[{language}] Using {weight_col} with threshold {strength_threshold}")
    
    # Filter by strength threshold
    df = df[df[weight_col] >= strength_threshold].copy()
    logger.info(f"[{language}] {len(df)} associations after threshold")
    
    # Normalize text (lowercase, strip)
    df['cue_clean'] = df['cue'].astype(str).str.lower().str.strip()
    df['resp_clean'] = df['response'].astype(str).str.lower().str.strip()
    
    # Count word frequencies (cues + responses)
    from collections import Counter
    word_counts = Counter()
    word_counts.update(df['cue_clean'])
    word_counts.update(df['resp_clean'])
    
    # Get top N words
    top_words = set([word for word, _ in word_counts.most_common(top_n)])
    logger.info(f"[{language}] Selected top {len(top_words)} words from {len(word_counts)} unique")
    
    # Filter to top words only
    df_filtered = df[
        (df['cue_clean'].isin(top_words)) & 
        (df['resp_clean'].isin(top_words)) &
        (df['cue_clean'] != df['resp_clean'])  # No self-loops
    ].copy()
    
    # Create edge list
    df_edges = df_filtered[['cue_clean', 'resp_clean', weight_col]].copy()
    df_edges.columns = ['source', 'target', 'weight']
    
    # Remove duplicates (keep max weight if any)
    df_edges = df_edges.groupby(['source', 'target'])['weight'].max().reset_index()
    
    logger.info(f"[{language}] Generated {len(df_edges)} unique edges")
    
    return df_edges

def compute_network_stats(df_edges: pd.DataFrame, language: str):
    """Compute and log network statistics."""
    G = nx.DiGraph()
    for _, row in df_edges.iterrows():
        G.add_edge(row['source'], row['target'], weight=row['weight'])
    
    G_undir = G.to_undirected()
    
    logger.info(f"✅ [{language}]")
    logger.info(f"   Nodes: {G_undir.number_of_nodes()}")
    logger.info(f"   Edges: {G_undir.number_of_edges()}")
    logger.info(f"   Mean degree: {2*G_undir.number_of_edges()/G_undir.number_of_nodes():.2f}")
    logger.info(f"   Weight range: [{df_edges['weight'].min():.3f}, {df_edges['weight'].max():.3f}]")

def main():
    output_dir = Path("data/processed")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    print("="*80)
    print("🔬 CORRECT SWOW Preprocessing - Using strength.*.R1.csv Files")
    print("="*80)
    print()
    print("Target edge counts (from Table 1):")
    print("  Spanish: 776 edges")
    print("  English: 815 edges")
    print("  Dutch: 817 edges")
    print("  Chinese: 799 edges")
    print()
    print("="*80)
    print()
    
    # Process English
    logger.info("PROCESSING ENGLISH...")
    df_en = preprocess_strength_file(
        Path("data/raw/strength.SWOW-EN.R1.20180827.csv"),
        language="English",
        top_n=500,
        strength_threshold=0.06
    )
    if len(df_en) > 0:
        output_path = output_dir / "english_edges_CORRECT.csv"
        df_en.to_csv(output_path, index=False)
        compute_network_stats(df_en, "English")
        logger.info(f"   Saved: {output_path}")
    print()
    
    # Process Spanish
    logger.info("PROCESSING SPANISH...")
    df_es = preprocess_strength_file(
        Path("data/raw/strength.SWOWRP.R1.20220426.csv"),
        language="Spanish",
        top_n=500,
        strength_threshold=0.06
    )
    if len(df_es) > 0:
        output_path = output_dir / "spanish_edges_CORRECT.csv"
        df_es.to_csv(output_path, index=False)
        compute_network_stats(df_es, "Spanish")
        logger.info(f"   Saved: {output_path}")
    print()
    
    # Process Chinese
    logger.info("PROCESSING CHINESE...")
    df_zh = preprocess_strength_file(
        Path("data/raw/SWOW-ZH24/strength.SWOWZH.R1.20230423.csv"),
        language="Chinese",
        top_n=500,
        strength_threshold=0.06
    )
    if len(df_zh) > 0:
        output_path = output_dir / "chinese_edges_CORRECT.csv"
        df_zh.to_csv(output_path, index=False)
        compute_network_stats(df_zh, "Chinese")
        logger.info(f"   Saved: {output_path}")
    print()
    
    # Dutch - need to find/extract
    logger.warning("DUTCH: Need to locate strength.SWOW-NL.R1.csv (check ZIP files)")
    print()
    
    print("="*80)
    print("✅ PREPROCESSING COMPLETE (3/4 languages)")
    print("="*80)
    print()
    print("Next: Compare edge counts to Table 1 targets")
    print()

if __name__ == '__main__':
    main()

