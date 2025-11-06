#!/usr/bin/env python3
"""
Prepare semantic networks from SWOW data for all 4 languages.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def process_language(lang_code: str, strength_file: Path, n_nodes: int = 500):
    """Process one language."""
    logger.info(f"{'='*60}")
    logger.info(f"Processing {lang_code.upper()}")
    logger.info(f"{'='*60}")
    
    # Load strength file
    logger.info(f"Loading: {strength_file}")
    df = pd.read_csv(strength_file, encoding='utf-8', on_bad_lines='skip')
    logger.info(f"  Loaded {len(df)} associations")
    
    # Get top N frequent cues
    cue_freq = df['cue'].value_counts()
    top_cues = cue_freq.head(n_nodes).index.tolist()
    logger.info(f"  Selected top {len(top_cues)} cues")
    
    # Filter to top cues and responses
    df_filtered = df[df['cue'].isin(top_cues)].copy()
    df_filtered = df_filtered[df_filtered['response'].isin(top_cues)]
    
    # Group by cue-response pairs
    edges = df_filtered.groupby(['cue', 'response']).size().reset_index(name='weight')
    
    # Normalize weights to [0,1]
    if len(edges) > 0:
        edges['weight'] = edges['weight'] / edges['weight'].max()
    
    # Rename columns
    edges = edges.rename(columns={'cue': 'source', 'response': 'target'})
    
    logger.info(f"  Network: {len(top_cues)} nodes, {len(edges)} edges")
    
    return edges

def main():
    RAW_DIR = Path("/home/agourakis82/workspace/hyperbolic-semantic-networks/data/raw")
    PROC_DIR = Path("/home/agourakis82/workspace/hyperbolic-semantic-networks/data/processed")
    PROC_DIR.mkdir(parents=True, exist_ok=True)
    
    # Language configurations
    languages = {
        'spanish': RAW_DIR / 'strength.SWOW-ES.R1.csv',
        'dutch': RAW_DIR / 'strength.SWOW-NL.R1.csv',
        'chinese': RAW_DIR / 'strength.SWOW-ZH.R1.csv',
        'english': RAW_DIR / 'strength.SWOW-EN.R1.20180827.csv'
    }
    
    logger.info("="*60)
    logger.info("SWOW NETWORK PREPARATION - 4 LANGUAGES")
    logger.info("="*60)
    
    for lang_name, strength_file in languages.items():
        if not strength_file.exists():
            logger.warning(f"SKIP {lang_name}: File not found: {strength_file}")
            continue
        
        try:
            edges = process_language(lang_name, strength_file, n_nodes=500)
            
            # Save
            output_file = PROC_DIR / f"{lang_name}_edges.csv"
            edges.to_csv(output_file, index=False)
            logger.info(f"  ✅ Saved: {output_file}\n")
            
        except Exception as e:
            logger.error(f"ERROR processing {lang_name}: {e}\n")
            continue
    
    logger.info("="*60)
    logger.info("PREPROCESSING COMPLETE!")
    logger.info("="*60)
    logger.info(f"Networks saved to: {PROC_DIR}")
    
    # Summary
    edge_files = list(PROC_DIR.glob("*_edges.csv"))
    logger.info(f"\nCreated {len(edge_files)} networks:")
    for f in sorted(edge_files):
        df = pd.read_csv(f)
        logger.info(f"  {f.name}: {len(df)} edges")

if __name__ == "__main__":
    main()
