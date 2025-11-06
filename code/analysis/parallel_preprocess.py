#!/usr/bin/env python3
"""
Parallel preprocessing of all SWOW datasets.

Processes 4 languages in parallel using multiprocessing.

Author: Demetrios Chiuratto Agourakis
Date: 2025-10-31
"""

import sys
from pathlib import Path
from multiprocessing import Pool, cpu_count
import logging

# Add preprocess script to path
sys.path.append(str(Path(__file__).parent))
from preprocess_swow_to_edges import (
    preprocess_swow_en,
    preprocess_swow_rp,
    preprocess_swow_nl,
    preprocess_swow_zh
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(processName)s] - %(message)s')
logger = logging.getLogger(__name__)


def process_language(config):
    """Process a single language (parallel worker)."""
    lang, file_path, func, output_dir, top_n = config
    
    try:
        logger.info(f"Starting {lang}...")
        
        if not file_path.exists():
            logger.error(f"{lang}: File not found - {file_path}")
            return None
        
        # Process
        df_edges = func(file_path, top_n=top_n)
        
        # Save
        output_file = output_dir / f"{lang}_edges.csv"
        df_edges.to_csv(output_file, index=False)
        
        n_edges = len(df_edges)
        n_nodes = len(set(df_edges['source']) | set(df_edges['target']))
        
        logger.info(f"{lang}: COMPLETE - {n_edges} edges, {n_nodes} nodes → {output_file}")
        
        return {
            'language': lang,
            'edges': n_edges,
            'nodes': n_nodes,
            'file': str(output_file)
        }
        
    except Exception as e:
        logger.error(f"{lang}: ERROR - {e}", exc_info=True)
        return None


def main():
    """Main parallel execution."""
    RAW_DIR = Path("/home/agourakis82/workspace/hyperbolic-semantic-networks/data/raw")
    OUTPUT_DIR = Path("/home/agourakis82/workspace/pcs-meta-repo/data/processed")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    TOP_N = 500
    N_WORKERS = min(4, cpu_count())  # Max 4 workers (1 per language)
    
    # Language configurations
    configs = [
        ('english', RAW_DIR / 'SWOW-EN.R100.20180827.csv', preprocess_swow_en, OUTPUT_DIR, TOP_N),
        ('spanish', RAW_DIR / 'SWOWRP.R70.20220426.csv', preprocess_swow_rp, OUTPUT_DIR, TOP_N),
        # ('dutch', RAW_DIR / 'SWOW-NL...csv', preprocess_swow_nl, OUTPUT_DIR, TOP_N),
        # ('chinese', RAW_DIR / 'SWOW-ZH...csv', preprocess_swow_zh, OUTPUT_DIR, TOP_N),
    ]
    
    logger.info("="*60)
    logger.info("PARALLEL SWOW PREPROCESSING")
    logger.info("="*60)
    logger.info(f"Languages: {len(configs)}")
    logger.info(f"Workers: {N_WORKERS}")
    logger.info(f"Top N nodes: {TOP_N}")
    logger.info("="*60)
    
    # Process in parallel
    with Pool(processes=N_WORKERS) as pool:
        results = pool.map(process_language, configs)
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("PREPROCESSING COMPLETE!")
    logger.info("="*60)
    
    for result in results:
        if result:
            logger.info(f"✓ {result['language'].upper()}: {result['edges']} edges, {result['nodes']} nodes")
        else:
            logger.warning(f"✗ Processing failed")
    
    logger.info("="*60)
    logger.info(f"Output directory: {OUTPUT_DIR}")
    logger.info("\nReady for structural null analysis!")


if __name__ == "__main__":
    main()

