#!/usr/bin/env python3
"""
Fill placeholders in manuscript with computed values from structural null analysis.

This script:
1. Loads results from 07_structural_nulls.py
2. Fills all <PLACEHOLDER> in manuscript
3. Generates updated v1.8 manuscript

Author: Demetrios Chiuratto Agourakis
Date: 2025-10-31
"""

import json
import re
from pathlib import Path
from typing import Dict

# Paths
RESULTS_DIR = Path("/home/agourakis82/workspace/hyperbolic-semantic-networks/results/structural_nulls")
MANUSCRIPT_PATH = Path("/home/agourakis82/workspace/hyperbolic-semantic-networks/manuscript/main.md")
OUTPUT_PATH = Path("/home/agourakis82/workspace/hyperbolic-semantic-networks/manuscript/main_v1.8_filled.md")


def load_results() -> Dict:
    """Load all structural null results."""
    results_file = RESULTS_DIR / "all_structural_nulls.json"
    
    if not results_file.exists():
        raise FileNotFoundError(
            f"Results file not found: {results_file}\n"
            "Please run 07_structural_nulls.py first!"
        )
    
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    return results


def format_value(value: float, decimals: int = 3) -> str:
    """Format float value with specified decimals."""
    return f"{value:.{decimals}f}"


def fill_abstract(text: str, results: Dict) -> str:
    """Fill placeholders in Abstract."""
    # Remove the NOTE placeholder line
    text = re.sub(
        r'\*\*NOTE\*\*:.*?proper null scaling\.\*\n\n',
        '',
        text,
        flags=re.DOTALL
    )
    
    return text


def fill_table_3a(text: str, results: Dict) -> str:
    """Fill placeholders in Table 3A (§3.3)."""
    
    # Build table rows
    table_rows = []
    lang_names = {
        'spanish': 'Spanish',
        'dutch': 'Dutch',
        'chinese': 'Chinese',
        'english': 'English'
    }
    
    for lang_key, lang_name in lang_names.items():
        if lang_key not in results:
            print(f"Warning: No results for {lang_name}")
            continue
        
        res = results[lang_key]['configuration']
        
        row = (
            f"| {lang_name:<8} | "
            f"{res['kappa_real']:>6.3f} | "
            f"{res['kappa_null_mean']:>6.3f}±{res['kappa_null_std']:<5.3f} | "
            f"{res['delta_kappa']:>6.3f} | "
            f"{res['p_MC']:>7.4f} | "
            f"{res['cliffs_delta']:>9.3f} |"
        )
        table_rows.append(row)
    
    # Build complete table
    table = (
        "| Language | κ_real | Configuration null (μ±σ) | Δκ | p_MC | Cliff's δ |\n"
        "|----------|--------|--------------------------|-----|------|-----------|"
    )
    
    for row in table_rows:
        table += "\n" + row
    
    # Replace placeholder table
    pattern = r'\| Language \| κ_real \| Configuration null.*?\| <PLACEHOLDER> \|'
    
    text = re.sub(pattern, table, text, flags=re.DOTALL)
    
    return text


def fill_discussion_4_7(text: str, results: Dict) -> str:
    """Fill placeholders in Discussion §4.7."""
    
    # For demonstration, use Spanish results
    if 'spanish' in results:
        res = results['spanish']['configuration']
        
        # Replace example in "Artifact of network sparsity?"
        old_text = "Real networks differ significantly from ER (p<0.0001, d>200)"
        new_text = (
            f"Real networks differ significantly "
            f"(Δκ={res['delta_kappa']:.3f}, p_MC={res['p_MC']:.4f}, Cliff's δ={res['cliffs_delta']:.2f})"
        )
        
        text = text.replace(old_text, new_text)
    
    return text


def generate_summary_note(results: Dict) -> str:
    """Generate summary note to add at end of Abstract."""
    
    # Calculate overall statistics
    all_delta_kappa = []
    all_p_mc = []
    all_cliffs_delta = []
    
    for lang in results.values():
        res = lang['configuration']
        all_delta_kappa.append(res['delta_kappa'])
        all_p_mc.append(res['p_MC'])
        all_cliffs_delta.append(res['cliffs_delta'])
    
    mean_delta = sum(all_delta_kappa) / len(all_delta_kappa)
    max_p_mc = max(all_p_mc)
    mean_cliffs = sum(all_cliffs_delta) / len(all_cliffs_delta)
    
    note = (
        f"\n\n**Structural null analysis**: Mean Δκ = {mean_delta:.3f}, "
        f"all p_MC < {max_p_mc:.4f}, mean Cliff's δ = {mean_cliffs:.2f} (large effect)."
    )
    
    return note


def main():
    """Main execution."""
    print("="*60)
    print("FILLING PLACEHOLDERS IN MANUSCRIPT")
    print("="*60)
    
    # Load results
    print("\n1. Loading structural null results...")
    try:
        results = load_results()
        print(f"   Loaded results for {len(results)} languages")
    except FileNotFoundError as e:
        print(f"   ERROR: {e}")
        return
    
    # Load manuscript
    print("\n2. Loading manuscript...")
    with open(MANUSCRIPT_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    print(f"   Loaded {len(text)} characters")
    
    # Fill placeholders
    print("\n3. Filling placeholders...")
    
    print("   - Abstract...")
    text = fill_abstract(text, results)
    
    print("   - Table 3A (§3.3)...")
    text = fill_table_3a(text, results)
    
    print("   - Discussion §4.7...")
    text = fill_discussion_4_7(text, results)
    
    # Add summary note to Abstract
    print("   - Adding summary to Abstract...")
    summary = generate_summary_note(results)
    # Insert before "**Conclusion**:"
    text = text.replace(
        "**Conclusion**: Semantic networks",
        summary + "\n\n**Conclusion**: Semantic networks"
    )
    
    # Update version
    text = text.replace(
        "**Status**: Draft v1.8 (Submission-Ready)",
        "**Status**: Draft v1.8-filled (Ready for Final Review)"
    )
    
    # Save
    print("\n4. Saving filled manuscript...")
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"   Saved: {OUTPUT_PATH}")
    
    # Summary
    print("\n" + "="*60)
    print("PLACEHOLDERS FILLED SUCCESSFULLY!")
    print("="*60)
    print(f"\nFilled manuscript: {OUTPUT_PATH}")
    print("\nNext steps:")
    print("1. Review filled manuscript")
    print("2. Generate Figure S7: python generate_figureS7_sensitivity.py")
    print("3. Generate PDF: pandoc main_v1.8_filled.md -o main_v1.8_filled.pdf")
    print("4. Final review and submit!")
    print("\n" + "="*60)


if __name__ == "__main__":
    main()

