#!/usr/bin/env python3
"""
Count all analyzed networks in the project.
"""

import json
from pathlib import Path

print("="*70)
print("NETWORK INVENTORY")
print("="*70)

# 1. SWOW Association Networks
print("\n1. SWOW ASSOCIATION NETWORKS:")
print("-" * 70)

swow_networks = ['spanish', 'english', 'chinese', 'dutch']
swow_valid = []

for lang in swow_networks:
    edge_file_options = [
        f'data/processed/{lang}_edges_FINAL.csv',
        f'data/processed/{lang}_edges.csv'
    ]

    exists = any(Path(f).exists() for f in edge_file_options)
    symbol = "✅" if exists else "❌"
    print(f"  {symbol} {lang.capitalize()}")

    if exists:
        swow_valid.append(lang)

print(f"\n  Total SWOW networks: {len(swow_valid)}/4")

# Check which have curvature results
print("\n  Curvature results available:")
curvature_file = 'results/FINAL_CURVATURE_CORRECTED_PREPROCESSING.json'
if Path(curvature_file).exists():
    with open(curvature_file) as f:
        curvature_data = json.load(f)
    for lang in swow_valid:
        if lang in curvature_data:
            kappa = curvature_data[lang]['kappa_mean']
            print(f"    ✅ {lang.capitalize()}: κ = {kappa:.3f}")
        else:
            print(f"    ❌ {lang.capitalize()}: No curvature data")

# 2. WordNet
print("\n2. WORDNET TAXONOMY:")
print("-" * 70)

wordnet_files = [
    ('WordNet N=500', 'data/processed/wordnet_metadata.json'),
    ('WordNet N=2000', 'data/processed/wordnet_N2000_metadata.json')
]

wordnet_count = 0
for name, path in wordnet_files:
    if Path(path).exists():
        print(f"  ✅ {name}")
        wordnet_count += 1
    else:
        print(f"  ❌ {name}")

print(f"\n  Total WordNet networks: {wordnet_count}")

# 3. BabelNet
print("\n3. BABELNET TAXONOMIES:")
print("-" * 70)

babelnet_langs = ['ru', 'ar']
babelnet_count = 0

for lang in babelnet_langs:
    path = f'data/processed/babelnet_{lang}_metadata.json'
    if Path(path).exists():
        with open(path) as f:
            meta = json.load(f)
        print(f"  ✅ {lang.upper()}: N={meta.get('n_nodes_lcc', '?')}")
        babelnet_count += 1
    else:
        print(f"  ❌ {lang.upper()}")

print(f"\n  Total BabelNet networks: {babelnet_count}")

# 4. ConceptNet
print("\n4. CONCEPTNET KNOWLEDGE GRAPHS:")
print("-" * 70)

conceptnet_langs = ['en', 'pt', 'ru', 'ar', 'el']
conceptnet_count = 0

for lang in conceptnet_langs:
    path = f'data/processed/conceptnet_{lang}_metadata.json'
    if Path(path).exists():
        with open(path) as f:
            meta = json.load(f)
        n_nodes = meta.get('n_nodes_lcc', meta.get('n_nodes_total', '?'))
        print(f"  ✅ {lang.upper()}: N={n_nodes}")
        conceptnet_count += 1
    else:
        print(f"  ❌ {lang.upper()}")

print(f"\n  Total ConceptNet networks: {conceptnet_count}")

# SUMMARY
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

total = len(swow_valid) + wordnet_count + babelnet_count + conceptnet_count

print(f"\n  Association networks (SWOW): {len(swow_valid)}")
print(f"  Taxonomies (WordNet): {wordnet_count}")
print(f"  Taxonomies (BabelNet): {babelnet_count}")
print(f"  Knowledge graphs (ConceptNet): {conceptnet_count}")
print(f"\n  TOTAL NETWORKS: {total}")

print("\n" + "="*70)
print("MANUSCRIPT CLAIM VERIFICATION")
print("="*70)

print("\nManuscript says: 'N=5 association networks'")
print(f"Actual count: N={len(swow_valid)} SWOW networks")

if len(swow_valid) == 5:
    print("✅ MATCHES")
elif len(swow_valid) == 4:
    print("⚠️  DISCREPANCY: Found 4, not 5")
    print("   Possible explanations:")
    print("   1. Dutch should be excluded (spherical, not hyperbolic)")
    print("   2. A fifth language was analyzed but data not in repository")
    print("   3. Manuscript count includes a different preprocessing")
elif len(swow_valid) == 3:
    print("⚠️  DISCREPANCY: Found 3, not 5")
    print("   If Dutch excluded: ES, EN, ZH (3 hyperbolic networks)")
