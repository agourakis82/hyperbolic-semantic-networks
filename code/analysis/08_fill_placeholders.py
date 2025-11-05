#!/usr/bin/env python3
"""
Fill placeholders in manuscript with computed structural null results.
Reads JSON files from results/structural_nulls/ and replaces {{PLACEHOLDERS}}.
"""

import json
import re
from pathlib import Path

# Paths
RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "structural_nulls"
MANUSCRIPT_PATH = Path(__file__).parent.parent.parent / "manuscript" / "main.md"

def load_null_results():
    """Load all completed null model JSON results."""
    results = {}
    
    for json_file in RESULTS_DIR.glob("*.json"):
        with open(json_file, 'r') as f:
            data = json.load(f)
            key = f"{data['language']}_{data['null_type']}"
            results[key] = data
    
    return results

def compute_aggregate_metrics(results):
    """Compute aggregate metrics across all results."""
    config_deltas = []
    triadic_deltas = []
    all_cliffs = []
    
    for key, data in results.items():
        if 'configuration' in key:
            config_deltas.append(data['delta_kappa'])
        elif 'triadic' in key:
            triadic_deltas.append(data['delta_kappa'])
        
        if 'cliffs_delta' in data:
            all_cliffs.append(abs(data['cliffs_delta']))
    
    return {
        'delta_mean_config': sum(config_deltas) / len(config_deltas) if config_deltas else 0,
        'delta_mean_triadic': sum(triadic_deltas) / len(triadic_deltas) if triadic_deltas else 0,
        'delta_min': min(config_deltas + triadic_deltas),
        'delta_max': max(config_deltas + triadic_deltas),
        'cliffs_min': min(all_cliffs) if all_cliffs else 0,
        'cliffs_max': max(all_cliffs) if all_cliffs else 0,
        'delta_mean': sum(config_deltas + triadic_deltas) / len(config_deltas + triadic_deltas),
    }

def format_value(value, decimals=3):
    """Format numerical value for manuscript."""
    if isinstance(value, float):
        if value < 0.001:
            return "<0.001"
        return f"{value:.{decimals}f}"
    return str(value)

def fill_placeholders(manuscript_text, results, aggregates):
    """Replace all {{PLACEHOLDERS}} with actual values."""
    replacements = {}
    
    # Individual language/null results
    for lang in ['spanish', 'english', 'dutch', 'chinese']:
        for null_type in ['configuration', 'triadic']:
            key = f"{lang}_{null_type}"
            if key in results:
                data = results[key]
                # Convert "configuration" → "CONFIG", "triadic" → "TRIADIC"
                null_abbrev = "CONFIG" if null_type == "configuration" else "TRIADIC"
                prefix = f"{lang.upper()}_{null_abbrev}"
                
                replacements[f"{prefix}_KAPPA"] = format_value(data['kappa_real'])
                replacements[f"{prefix}_DELTA"] = format_value(data['delta_kappa'])
                replacements[f"{prefix}_PMC"] = format_value(data['p_MC'])
                replacements[f"{prefix}_CLIFFS"] = format_value(data.get('cliffs_delta', 0))
    
    # Aggregate metrics
    replacements["DELTA_MEAN_CONFIG"] = format_value(aggregates['delta_mean_config'])
    replacements["DELTA_MEAN_TRIADIC"] = format_value(aggregates['delta_mean_triadic'])
    replacements["DELTA_MIN"] = format_value(aggregates['delta_min'])
    replacements["DELTA_MAX"] = format_value(aggregates['delta_max'])
    replacements["DELTA_MEAN"] = format_value(aggregates['delta_mean'])
    replacements["CLIFFS_MEAN_RANGE"] = f"{format_value(aggregates['cliffs_min'])}-{format_value(aggregates['cliffs_max'])}"
    
    # Perform replacements
    filled_text = manuscript_text
    for placeholder, value in replacements.items():
        pattern = f"{{{{{placeholder}}}}}"
        filled_text = filled_text.replace(pattern, value)
    
    # Check for remaining placeholders
    remaining = re.findall(r'\{\{([A-Z_]+)\}\}', filled_text)
    if remaining:
        print(f"⚠️  Warning: {len(remaining)} placeholders not filled:")
        for p in set(remaining):
            print(f"   - {{{{{p}}}}}")
    
    return filled_text

def main():
    print("=" * 60)
    print("FILL MANUSCRIPT PLACEHOLDERS - Structural Nulls v1.8")
    print("=" * 60)
    print()
    
    # Load results
    print("📂 Loading structural null results...")
    results = load_null_results()
    print(f"   ✅ Loaded {len(results)} result files")
    
    for key in sorted(results.keys()):
        data = results[key]
        print(f"      - {key:30s} | Δκ={data['delta_kappa']:.4f}, p_MC={data['p_MC']:.4f}")
    
    # Compute aggregates
    print()
    print("📊 Computing aggregate metrics...")
    aggregates = compute_aggregate_metrics(results)
    print(f"   ✅ Δκ_config_mean = {aggregates['delta_mean_config']:.4f}")
    print(f"   ✅ Δκ_triadic_mean = {aggregates['delta_mean_triadic']:.4f}")
    print(f"   ✅ Δκ range: [{aggregates['delta_min']:.4f}, {aggregates['delta_max']:.4f}]")
    
    # Load manuscript
    print()
    print("📝 Loading manuscript...")
    with open(MANUSCRIPT_PATH, 'r', encoding='utf-8') as f:
        manuscript_text = f.read()
    print(f"   ✅ Loaded {len(manuscript_text)} characters")
    
    # Count placeholders
    placeholders = re.findall(r'\{\{([A-Z_]+)\}\}', manuscript_text)
    print(f"   📌 Found {len(placeholders)} placeholders to fill")
    
    # Fill placeholders
    print()
    print("🔄 Filling placeholders...")
    filled_text = fill_placeholders(manuscript_text, results, aggregates)
    
    # Write output
    output_path = MANUSCRIPT_PATH.parent / "main_v1.8_filled.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(filled_text)
    
    print()
    print("=" * 60)
    print(f"✅ SUCCESS! Filled manuscript written to:")
    print(f"   {output_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
