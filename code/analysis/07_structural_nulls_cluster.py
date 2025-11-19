#!/usr/bin/env python3
"""
Cluster-compatible wrapper for structural nulls analysis.

This version reads paths from environment variables for K8s deployment.

Author: Demetrios Chiuratto Agourakis
Date: 2025-11-03
"""

import os
import sys
from pathlib import Path

# Get paths from environment (with defaults)
DATA_DIR = Path(os.environ.get('DATA_DIR', '/data/processed'))
OUTPUT_DIR = Path(os.environ.get('OUTPUT_DIR', '/results/structural_nulls'))

print(f"📂 Configuration:")
print(f"   DATA_DIR: {DATA_DIR}")
print(f"   OUTPUT_DIR: {OUTPUT_DIR}")
print()

# Import and patch the original module
sys.path.append(str(Path(__file__).parent))
import importlib.util

# Load 07_structural_nulls.py
spec = importlib.util.spec_from_file_location(
    "structural_nulls", 
    Path(__file__).parent / "07_structural_nulls.py"
)
structural_nulls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(structural_nulls)  # Execute module to load functions

def patched_main():
    """Patched main that uses env vars."""
    import numpy as np
    from pathlib import Path
    import json
    
    # Override paths
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    LANGUAGES = ['spanish', 'english', 'dutch', 'chinese']
    NULL_TYPES = ['configuration']  # Only configuration model (faster, sufficient for publication)
    M = int(os.environ.get('M_REPLICATES', '1000'))
    ALPHA = float(os.environ.get('ALPHA_IDLENESS', '0.5'))
    SEED = int(os.environ.get('SEED', '123'))
    
    np.random.seed(SEED)
    
    print("="*60)
    print("STRUCTURAL NULL MODEL ANALYSIS")
    print("="*60)
    print(f"Languages: {LANGUAGES}")
    print(f"Null types: {NULL_TYPES}")
    print(f"Replicates: M={M}")
    print(f"Idleness: α={ALPHA}")
    print(f"Seed: {SEED}")
    print("="*60)
    
    all_results = {}
    
    # Process each language
    for lang in LANGUAGES:
        print(f"\n{'='*60}")
        print(f"Processing {lang.upper()}")
        print(f"{'='*60}")
        
        # Load real network
        try:
            G_real = structural_nulls.load_real_network(lang, DATA_DIR)
        except FileNotFoundError as e:
            print(f"ERROR: Skipping {lang}: {e}")
            continue
        
        lang_results = {}
        
        # Run both null types
        for null_type in NULL_TYPES:
            results = structural_nulls.run_null_analysis(
                lang, G_real, null_type, M=M, alpha=ALPHA
            )
            lang_results[null_type] = results
            
            # Save individual result
            output_file = OUTPUT_DIR / f"{lang}_{null_type}_nulls.json"
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Saved: {output_file}")
        
        all_results[lang] = lang_results
    
    # Save combined results
    combined_file = OUTPUT_DIR / "all_structural_nulls.json"
    with open(combined_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\nSaved combined results: {combined_file}")
    
    # Generate summary table
    print("\n" + "="*80)
    print("SUMMARY TABLE (Configuration Model)")
    print("="*80)
    print(f"{'Language':<10} {'κ_real':<10} {'κ_null (μ±σ)':<20} {'Δκ':<10} {'p_MC':<10} {'Cliff δ':<10}")
    print("-"*80)
    
    for lang in LANGUAGES:
        if lang not in all_results:
            continue
        res = all_results[lang]['configuration']
        print(f"{lang.capitalize():<10} "
              f"{res['kappa_real']:<10.4f} "
              f"{res['kappa_null_mean']:>6.4f}±{res['kappa_null_std']:<6.4f} "
              f"{res['delta_kappa']:<10.4f} "
              f"{res['p_MC']:<10.4f} "
              f"{res['cliffs_delta']:<10.4f}")
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print(f"Results saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    patched_main()

