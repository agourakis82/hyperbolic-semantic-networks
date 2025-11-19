#!/usr/bin/env python3
"""
Preprocess SWOW datasets to generate edge lists for network analysis.

Reads SWOW CSV files (cue, R1, R2, R3) and generates:
- Weighted directed graphs (cue → response associations)
- Top N nodes by frequency (default: 500)
- Edge list CSV: source,target,weight

Author: Demetrios Chiuratto Agourakis
Date: 2025-10-31
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


def preprocess_swow_en(file_path: Path, top_n: int = 500) -> pd.DataFrame:
    """Preprocess English SWOW data."""
    logger.info(f"Loading: {file_path}")
    
    # English format: cue, R1, R2, R3 columns
    df = pd.read_csv(file_path, low_memory=False)
    
    # Count word frequencies (cues + responses)
    word_counts = defaultdict(int)
    
    # Count cues
    cue_counts = df['cue'].value_counts().to_dict()
    for cue, count in cue_counts.items():
        if pd.notna(cue):
            word_counts[cue.lower().strip()] += count
    
    # Count responses (R1, R2, R3)
    for col in ['R1', 'R2', 'R3']:
        if col in df.columns:
            resp_counts = df[col].value_counts().to_dict()
            for resp, count in resp_counts.items():
                if pd.notna(resp):
                    word_counts[resp.lower().strip()] += count
    
    # Get top N words
    top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    top_words_set = {w for w, _ in top_words}
    
    logger.info(f"Selected top {len(top_words_set)} words")
    
    # Build edge list: cue -> response (weighted by frequency)
    edge_dict = defaultdict(float)
    
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing edges"):
        cue = row['cue']
        if pd.isna(cue) or cue.lower().strip() not in top_words_set:
            continue
        
        cue_clean = cue.lower().strip()
        
        # Process responses (R1 weighted more than R2, R2 more than R3)
        for i, col in enumerate(['R1', 'R2', 'R3'], 1):
            if col not in df.columns:
                continue
            resp = row[col]
            if pd.isna(resp):
                continue
            
            resp_clean = resp.lower().strip()
            if resp_clean not in top_words_set:
                continue
            
            # Weight: R1=3.0, R2=2.0, R3=1.0 (can be adjusted)
            weight = 4.0 - i
            edge_dict[(cue_clean, resp_clean)] += weight
    
    # Convert to DataFrame
    edges = []
    for (source, target), weight in edge_dict.items():
        edges.append({'source': source, 'target': target, 'weight': weight})
    
    df_edges = pd.DataFrame(edges)
    logger.info(f"Generated {len(df_edges)} edges")
    
    return df_edges


def preprocess_swow_rp(file_path: Path, top_n: int = 500) -> pd.DataFrame:
    """Preprocess Rioplatense Spanish SWOW data."""
    logger.info(f"Loading: {file_path}")
    
    # Spanish format: cue, R1, R2, R3 columns
    df = pd.read_csv(file_path, low_memory=False)
    
    # Same processing as English
    word_counts = defaultdict(int)
    
    # Count cues
    if 'cue' in df.columns:
        cue_counts = df['cue'].value_counts().to_dict()
        for cue, count in cue_counts.items():
            if pd.notna(cue):
                word_counts[str(cue).lower().strip()] += count
    
    # Count responses
    for col in ['R1', 'R2', 'R3']:
        if col in df.columns:
            resp_counts = df[col].value_counts().to_dict()
            for resp, count in resp_counts.items():
                if pd.notna(resp):
                    word_counts[str(resp).lower().strip()] += count
    
    # Get top N words
    top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    top_words_set = {w for w, _ in top_words}
    
    logger.info(f"Selected top {len(top_words_set)} words")
    
    # Build edge list
    edge_dict = defaultdict(float)
    
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing edges"):
        if 'cue' not in df.columns:
            continue
        cue = row['cue']
        if pd.isna(cue) or str(cue).lower().strip() not in top_words_set:
            continue
        
        cue_clean = str(cue).lower().strip()
        
        for i, col in enumerate(['R1', 'R2', 'R3'], 1):
            if col not in df.columns:
                continue
            resp = row[col]
            if pd.isna(resp):
                continue
            
            resp_clean = str(resp).lower().strip()
            if resp_clean not in top_words_set:
                continue
            
            weight = 4.0 - i
            edge_dict[(cue_clean, resp_clean)] += weight
    
    edges = []
    for (source, target), weight in edge_dict.items():
        edges.append({'source': source, 'target': target, 'weight': weight})
    
    df_edges = pd.DataFrame(edges)
    logger.info(f"Generated {len(df_edges)} edges")
    
    return df_edges


def preprocess_swow_nl(file_path: Path, top_n: int = 500) -> pd.DataFrame:
    """Preprocess Dutch SWOW data - already in edge format."""
    logger.info(f"Loading: {file_path}")
    
    # Dutch is already preprocessed in format: cue,response,lang,weight
    df = pd.read_csv(file_path, low_memory=False)
    
    # Rename columns
    df = df.rename(columns={'cue': 'source', 'response': 'target'})
    
    # Get top N nodes by frequency
    word_counts = defaultdict(int)
    for word in list(df['source']) + list(df['target']):
        if pd.notna(word):
            word_counts[str(word).lower().strip()] += 1
    
    top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    top_words_set = {w for w, _ in top_words}
    
    logger.info(f"Selected top {len(top_words_set)} words")
    
    # Filter to top N
    df = df[df['source'].apply(lambda x: str(x).lower().strip() in top_words_set) & 
            df['target'].apply(lambda x: str(x).lower().strip() in top_words_set)]
    
    df['source'] = df['source'].apply(lambda x: str(x).lower().strip())
    df['target'] = df['target'].apply(lambda x: str(x).lower().strip())
    
    # Keep only source, target, weight
    df_edges = df[['source', 'target', 'weight']].copy()
    
    logger.info(f"Generated {len(df_edges)} edges")
    
    return df_edges


def preprocess_swow_zh(file_path: Path, top_n: int = 500) -> pd.DataFrame:
    """Preprocess Chinese SWOW data (SWOW-ZH format)."""
    logger.info(f"Loading: {file_path}")
    
    # Chinese format: sequenceNumber,...,cue,R1Raw,R2Raw,R3Raw,R1,R2,R3
    df = pd.read_csv(file_path, low_memory=False)
    
    # Count word frequencies (cues + responses)
    word_counts = defaultdict(int)
    
    # Count cues
    cue_counts = df['cue'].value_counts().to_dict()
    for cue, count in cue_counts.items():
        if pd.notna(cue):
            word_counts[str(cue).strip()] += count
    
    # Count responses (R1, R2, R3 - use cleaned versions)
    for col in ['R1', 'R2', 'R3']:
        if col in df.columns:
            resp_counts = df[col].value_counts().to_dict()
            for resp, count in resp_counts.items():
                if pd.notna(resp):
                    word_counts[str(resp).strip()] += count
    
    # Get top N words
    top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    top_words_set = {w for w, _ in top_words}
    
    logger.info(f"Selected top {len(top_words_set)} words")
    
    # Build edge list
    edge_dict = defaultdict(float)
    
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing edges"):
        cue = row['cue']
        if pd.isna(cue) or str(cue).strip() not in top_words_set:
            continue
        
        cue_clean = str(cue).strip()
        
        # Process responses (R1 weighted more than R2, R2 more than R3)
        for i, col in enumerate(['R1', 'R2', 'R3'], 1):
            if col not in df.columns:
                continue
            resp = row[col]
            if pd.isna(resp):
                continue
            
            resp_clean = str(resp).strip()
            if resp_clean not in top_words_set:
                continue
            
            weight = 4.0 - i  # R1=3.0, R2=2.0, R3=1.0
            edge_dict[(cue_clean, resp_clean)] += weight
    
    edges = []
    for (source, target), weight in edge_dict.items():
        edges.append({'source': source, 'target': target, 'weight': weight})
    
    df_edges = pd.DataFrame(edges)
    logger.info(f"Generated {len(df_edges)} edges")
    
    return df_edges


def main():
    """Main execution."""
    # Input directories
    RAW_DIR = Path("/home/agourakis82/workspace/hyperbolic-semantic-networks/data/raw")
    OUTPUT_DIR = Path("/home/agourakis82/workspace/pcs-meta-repo/data/processed")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    TOP_N = 500  # Number of nodes to keep
    
    # Language configurations
    languages = {
        'english': {
            'file': RAW_DIR / 'SWOW-EN.R100.20180827.csv',
            'func': preprocess_swow_en
        },
        'spanish': {
            'file': RAW_DIR / 'SWOWRP.R70.20220426.csv',
            'func': preprocess_swow_rp
        },
        'dutch': {
            'file': RAW_DIR / 'swow_nl.csv',
            'func': preprocess_swow_nl
        },
        'chinese': {
            'file': RAW_DIR / 'SWOW-ZH24' / 'SWOWZH.R55.20230424.csv',
            'func': preprocess_swow_zh
        }
    }
    
    logger.info("="*60)
    logger.info("SWOW DATA PREPROCESSING")
    logger.info("="*60)
    logger.info(f"Output directory: {OUTPUT_DIR}")
    logger.info(f"Top N nodes: {TOP_N}")
    logger.info("="*60)
    
    # Process each language
    for lang, config in languages.items():
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing {lang.upper()}")
        logger.info(f"{'='*60}")
        
        if not config['file'].exists():
            logger.error(f"File not found: {config['file']}")
            continue
        
        try:
            df_edges = config['func'](config['file'], top_n=TOP_N)
            
            # Save edge list
            output_file = OUTPUT_DIR / f"{lang}_edges.csv"
            df_edges.to_csv(output_file, index=False)
            logger.info(f"Saved: {output_file}")
            logger.info(f"  Edges: {len(df_edges)}")
            logger.info(f"  Unique nodes: {len(set(df_edges['source']) | set(df_edges['target']))}")
            
        except Exception as e:
            logger.error(f"Error processing {lang}: {e}", exc_info=True)
    
    logger.info("\n" + "="*60)
    logger.info("PREPROCESSING COMPLETE!")
    logger.info("="*60)


if __name__ == "__main__":
    main()


