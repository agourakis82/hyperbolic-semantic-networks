#!/usr/bin/env python3
"""
STRATEGY A: Manual Deep Read of PMC10031728
Extract and map clustering values to clinical groups
"""

import fitz  # PyMuPDF
import re
import json
from pathlib import Path

pdf_path = "/mnt/c/Users/demet/Downloads/Artigos Semantic Networks/PMC10031728.pdf"

print("="*70)
print("STRATEGY A: MANUAL DEEP READ - PMC10031728")
print("="*70)
print()

# Extract full text
doc = fitz.open(pdf_path)
full_text = ""
page_texts = []

for page_num, page in enumerate(doc, 1):
    page_text = page.get_text()
    page_texts.append({
        'page': page_num,
        'text': page_text
    })
    full_text += f"\n\n=== PAGE {page_num} ===\n\n" + page_text

doc.close()

print(f"📄 Extracted {len(page_texts)} pages")
print()

# Save full text for manual review
with open('data/manual_extraction/PMC10031728_full_text.txt', 'w', encoding='utf-8') as f:
    f.write(full_text)

print("✅ Full text saved to: data/manual_extraction/PMC10031728_full_text.txt")
print()

# ============================================================================
# PHASE A1: Find all clustering mentions with extended context
# ============================================================================

print("="*70)
print("PHASE A1: FINDING ALL CLUSTERING MENTIONS")
print("="*70)
print()

# Known clustering values
known_values = [0.14, 0.12, 0.10, 0.08, 0.07, 0.04]

clustering_contexts = []

# Search for each known value with extensive context
for value in known_values:
    # Try different formats
    patterns = [
        rf'{value:.2f}',
        rf'{value:.3f}',
        rf'{int(value*100)}',  # percentage
    ]
    
    for pattern in patterns:
        for match in re.finditer(re.escape(pattern), full_text):
            start = max(0, match.start() - 500)
            end = min(len(full_text), match.end() + 500)
            context = full_text[start:end]
            
            # Find page number
            page_num = None
            cumulative_len = 0
            for p in page_texts:
                cumulative_len += len(p['text']) + 50  # Account for page markers
                if match.start() < cumulative_len:
                    page_num = p['page']
                    break
            
            clustering_contexts.append({
                'value': value,
                'match_position': match.start(),
                'page': page_num,
                'context': context,
                'pattern': pattern
            })

# Remove duplicates (same value + similar position)
unique_contexts = []
seen = set()
for ctx in clustering_contexts:
    key = (ctx['value'], ctx['page'])
    if key not in seen:
        seen.add(key)
        unique_contexts.append(ctx)

print(f"Found {len(unique_contexts)} unique clustering mentions")
print()

# ============================================================================
# PHASE A2: Identify clinical groups for each value
# ============================================================================

print("="*70)
print("PHASE A2: IDENTIFYING CLINICAL GROUPS")
print("="*70)
print()

# Group keywords
group_keywords = {
    'FEP': ['fep', 'first episode psychosis', 'first-episode psychosis', 'fep patient'],
    'CHR-P': ['chr-p', 'chr participant', 'clinical high risk', 'chr group'],
    'Control': ['control', 'healthy control', 'control group', 'controls', 'healthy participant'],
    'General': ['general population', 'online', 'general cohort']
}

# Analyze each context
results = []
for ctx in unique_contexts:
    context_lower = ctx['context'].lower()
    
    # Identify group
    identified_group = 'Unknown'
    group_mentions = []
    
    for group, keywords in group_keywords.items():
        for keyword in keywords:
            if keyword in context_lower:
                group_mentions.append(group)
                break
    
    # Take most specific group
    if 'FEP' in group_mentions:
        identified_group = 'FEP'
    elif 'CHR-P' in group_mentions:
        identified_group = 'CHR-P'
    elif 'Control' in group_mentions:
        identified_group = 'Control'
    elif 'General' in group_mentions:
        identified_group = 'General'
    
    result = {
        'value': ctx['value'],
        'group': identified_group,
        'page': ctx['page'],
        'context_snippet': ctx['context'][:300] + '...',
        'all_group_mentions': group_mentions
    }
    
    results.append(result)
    
    print(f"Value: {ctx['value']:.2f}")
    print(f"  Group: {identified_group}")
    print(f"  Page: {ctx['page']}")
    print(f"  Group mentions: {group_mentions}")
    print(f"  Context: {ctx['context'][:150]}...")
    print()

# ============================================================================
# PHASE A3: Look for tables and figures
# ============================================================================

print("="*70)
print("PHASE A3: SEARCHING FOR TABLES AND FIGURES")
print("="*70)
print()

# Find table mentions
table_mentions = []
for match in re.finditer(r'table\s+\d+', full_text, re.IGNORECASE):
    start = max(0, match.start() - 200)
    end = min(len(full_text), match.end() + 300)
    context = full_text[start:end]
    
    table_mentions.append({
        'table': match.group(0),
        'context': context
    })

print(f"Found {len(table_mentions)} table mentions")
for tm in table_mentions[:10]:
    print(f"\n{tm['table']}:")
    print(f"  {tm['context'][:200]}...")

# Find figure mentions
figure_mentions = []
for match in re.finditer(r'figure\s+\d+', full_text, re.IGNORECASE):
    start = max(0, match.start() - 200)
    end = min(len(full_text), match.end() + 300)
    context = full_text[start:end]
    
    figure_mentions.append({
        'figure': match.group(0),
        'context': context
    })

print(f"\nFound {len(figure_mentions)} figure mentions")
for fm in figure_mentions[:5]:
    print(f"\n{fm['figure']}:")
    print(f"  {fm['context'][:200]}...")

# ============================================================================
# PHASE A4: Extract sample sizes and statistical tests
# ============================================================================

print("\n" + "="*70)
print("PHASE A4: EXTRACTING SAMPLE SIZES AND STATISTICS")
print("="*70)
print()

# Sample sizes
n_patterns = [
    r'n\s*=\s*(\d+)',
    r'N\s*=\s*(\d+)',
    r'(\d+)\s+(?:patients?|participants?|subjects?|controls?)',
]

sample_sizes = []
for pattern in n_patterns:
    for match in re.finditer(pattern, full_text, re.IGNORECASE):
        try:
            n = int(match.group(1))
            if 5 <= n <= 1000:
                start = max(0, match.start() - 100)
                end = min(len(full_text), match.end() + 100)
                context = full_text[start:end]
                
                sample_sizes.append({
                    'n': n,
                    'context': context.replace('\n', ' ')[:200]
                })
        except:
            pass

# Remove duplicates
unique_n = []
seen_n = set()
for ss in sample_sizes:
    if ss['n'] not in seen_n:
        seen_n.add(ss['n'])
        unique_n.append(ss)

print(f"Sample sizes found: {len(unique_n)}")
for ss in sorted(unique_n, key=lambda x: x['n'], reverse=True)[:10]:
    print(f"  n={ss['n']}: {ss['context'][:150]}...")

# ============================================================================
# Save results
# ============================================================================

print("\n" + "="*70)
print("SAVING RESULTS")
print("="*70)
print()

output = {
    'paper_id': 'PMC10031728',
    'clustering_values': results,
    'table_mentions': table_mentions,
    'figure_mentions': figure_mentions,
    'sample_sizes': unique_n,
    'summary': {
        'n_clustering_values': len(results),
        'groups_identified': {
            'FEP': len([r for r in results if r['group'] == 'FEP']),
            'CHR-P': len([r for r in results if r['group'] == 'CHR-P']),
            'Control': len([r for r in results if r['group'] == 'Control']),
            'General': len([r for r in results if r['group'] == 'General']),
            'Unknown': len([r for r in results if r['group'] == 'Unknown']),
        }
    }
}

with open('data/manual_extraction/PMC10031728_manual_analysis.json', 'w') as f:
    json.dump(output, f, indent=2)

print("✅ Results saved to: data/manual_extraction/PMC10031728_manual_analysis.json")
print()

print("="*70)
print("SUMMARY")
print("="*70)
print()
print(f"Clustering values analyzed: {len(results)}")
print(f"Groups identified:")
for group, count in output['summary']['groups_identified'].items():
    print(f"  {group}: {count}")
print()
print(f"Tables found: {len(table_mentions)}")
print(f"Figures found: {len(figure_mentions)}")
print(f"Sample sizes found: {len(unique_n)}")
print()

print("="*70)
print("✅ STRATEGY A: MANUAL DEEP READ COMPLETE")
print("="*70)

