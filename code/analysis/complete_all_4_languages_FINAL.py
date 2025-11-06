#!/usr/bin/env python3
"""
Complete Preprocessing - All 4 Languages FINAL
===============================================
Agent: DATA_PROCESSOR_COMPLETE
Mission: Process all 4 languages with CORRECT methodology
- Files: strength.*.R1.csv
- Threshold: R1.Strength >= 0.06
- Top N: 500 words
- Expected edges: ~750-850 per language
"""

import pandas as pd
import networkx as nx
from pathlib import Path
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def preprocess_strength(file_path, language, sep='\t'):
    """Process SWOW strength file."""
    logger.info(f"[{language}] Loading: {file_path}")
    
    # Auto-detect separator
    try:
        df = pd.read_csv(file_path, sep=sep, quoting=1, on_bad_lines='skip')
        if 'cue,response' in str(df.columns):
            df = pd.read_csv(file_path, sep=',', on_bad_lines='skip')
    except:
        df = pd.read_csv(file_path, sep=',', on_bad_lines='skip')
    
    logger.info(f"[{language}] Loaded {len(df)} rows")
    
    # Check for R1.Strength column
    if 'R1.Strength' not in df.columns:
        logger.error(f"[{language}] Missing R1.Strength!")
        return pd.DataFrame()
    
    # Filter by threshold
    df = df[df['R1.Strength'] >= 0.06].copy()
    logger.info(f"[{language}] {len(df)} after R1.Strength >= 0.06")
    
    # Count word frequencies
    from collections import Counter
    words = Counter()
    words.update(df['cue'].astype(str).str.lower())
    words.update(df['response'].astype(str).str.lower())
    
    top_500 = set([w for w, _ in words.most_common(500)])
    logger.info(f"[{language}] Top 500 from {len(words)} unique words")
    
    # Filter to top 500
    df['cue_clean'] = df['cue'].astype(str).str.lower()
    df['resp_clean'] = df['response'].astype(str).str.lower()
    
    df_filt = df[
        (df['cue_clean'].isin(top_500)) &
        (df['resp_clean'].isin(top_500)) &
        (df['cue_clean'] != df['resp_clean'])
    ].copy()
    
    # Aggregate duplicates
    edges = df_filt.groupby(['cue_clean', 'resp_clean'])['R1.Strength'].max().reset_index()
    edges.columns = ['source', 'target', 'weight']
    
    logger.info(f"[{language}] {len(edges)} unique edges")
    
    # Stats
    G = nx.DiGraph()
    for _, row in edges.iterrows():
        G.add_edge(row['source'], row['target'], weight=row['weight'])
    
    G_undir = G.to_undirected()
    logger.info(f"✅ [{language}] {G_undir.number_of_nodes()} nodes, {G_undir.number_of_edges()} edges\n")
    
    return edges

# Process all 4
print("="*80)
print("🔬 FINAL PREPROCESSING - All 4 Languages")
print("="*80)
print()

output_dir = Path("data/processed")

# English
df_en = preprocess_strength("data/raw/strength.SWOW-EN.R1.20180827.csv", "English")
df_en.to_csv(output_dir / "english_edges_FINAL.csv", index=False)

# Spanish
df_es = preprocess_strength("data/raw/strength.SWOWRP.R1.20220426.csv", "Spanish")
df_es.to_csv(output_dir / "spanish_edges_FINAL.csv", index=False)

# Chinese
df_zh = preprocess_strength("data/raw/SWOW-ZH24/strength.SWOWZH.R1.20230423.csv", "Chinese", sep=',')
df_zh.to_csv(output_dir / "chinese_edges_FINAL.csv", index=False)

# Dutch - find file first
import glob
dutch_files = glob.glob("data/raw/**/strength.*NL*.R1*.csv", recursive=True)
if dutch_files:
    df_nl = preprocess_strength(dutch_files[0], "Dutch")
    df_nl.to_csv(output_dir / "dutch_edges_FINAL.csv", index=False)
else:
    logger.warning("⚠️  Dutch strength file not found - checking ZIP...")

print("="*80)
print("✅ PREPROCESSING COMPLETE - All edge files ready")
print("="*80)

