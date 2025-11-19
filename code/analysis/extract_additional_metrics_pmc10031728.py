#!/usr/bin/env python3
"""
OPTION 2: Extract Additional Network Metrics from PMC10031728
Search for pathology in path length, modularity, degree, etc.
"""

import fitz  # PyMuPDF
import re
import json
import numpy as np
from collections import defaultdict

pdf_path = "/mnt/c/Users/demet/Downloads/Artigos Semantic Networks/PMC10031728.pdf"

print("="*70)
print("OPTION 2: EXTRACTING ADDITIONAL NETWORK METRICS")
print("="*70)
print()

# Load full text
doc = fitz.open(pdf_path)
full_text = ""
for page in doc:
    full_text += page.get_text()
doc.close()

print(f"📄 Loaded full text ({len(full_text)} chars)")
print()

# ============================================================================
# METRIC 1: PATH LENGTH
# ============================================================================

print("="*70)
print("METRIC 1: PATH LENGTH")
print("="*70)
print()

path_length_patterns = [
    r'path\s+length[:\s=]+([0-9]+\.[0-9]+)',
    r'average\s+path[:\s=]+([0-9]+\.[0-9]+)',
    r'mean\s+path[:\s=]+([0-9]+\.[0-9]+)',
    r'L\s*[=:]\s*([0-9]+\.[0-9]+)',
    r'shortest\s+path[:\s=]+([0-9]+\.[0-9]+)',
    r'geodesic[:\s=]+([0-9]+\.[0-9]+)'
]

path_length_values = []
for pattern in path_length_patterns:
    for match in re.finditer(pattern, full_text, re.IGNORECASE):
        try:
            val = float(match.group(1))
            if 0.5 <= val <= 20:  # Reasonable path length range
                start = max(0, match.start() - 300)
                end = min(len(full_text), match.end() + 300)
                context = full_text[start:end].replace('\n', ' ')
                
                # Identify group
                context_lower = context.lower()
                if 'fep' in context_lower and 'control' not in context_lower:
                    group = 'FEP'
                elif 'chr-p' in context_lower or 'chr participant' in context_lower:
                    group = 'CHR-P'
                elif 'control' in context_lower or 'healthy' in context_lower:
                    group = 'Control'
                elif 'general' in context_lower:
                    group = 'General'
                else:
                    group = 'Unknown'
                
                path_length_values.append({
                    'value': val,
                    'group': group,
                    'context': context[:200]
                })
        except:
            pass

print(f"Found {len(path_length_values)} path length values")
for plv in path_length_values[:20]:
    print(f"  {plv['value']:.2f} ({plv['group']}): {plv['context'][:100]}...")
print()

# ============================================================================
# METRIC 2: DEGREE / CONNECTIVITY
# ============================================================================

print("="*70)
print("METRIC 2: DEGREE / CONNECTIVITY")
print("="*70)
print()

degree_patterns = [
    r'degree[:\s=]+([0-9]+\.[0-9]+)',
    r'connectivity[:\s=]+([0-9]+\.[0-9]+)',
    r'k\s*[=:]\s*([0-9]+\.[0-9]+)',
    r'average\s+degree[:\s=]+([0-9]+\.[0-9]+)',
    r'mean\s+degree[:\s=]+([0-9]+\.[0-9]+)'
]

degree_values = []
for pattern in degree_patterns:
    for match in re.finditer(pattern, full_text, re.IGNORECASE):
        try:
            val = float(match.group(1))
            if 0.5 <= val <= 100:  # Reasonable degree range
                start = max(0, match.start() - 300)
                end = min(len(full_text), match.end() + 300)
                context = full_text[start:end].replace('\n', ' ')
                
                context_lower = context.lower()
                if 'fep' in context_lower and 'control' not in context_lower:
                    group = 'FEP'
                elif 'chr-p' in context_lower:
                    group = 'CHR-P'
                elif 'control' in context_lower or 'healthy' in context_lower:
                    group = 'Control'
                elif 'general' in context_lower:
                    group = 'General'
                else:
                    group = 'Unknown'
                
                degree_values.append({
                    'value': val,
                    'group': group,
                    'context': context[:200]
                })
        except:
            pass

print(f"Found {len(degree_values)} degree values")
for dv in degree_values[:20]:
    print(f"  {dv['value']:.2f} ({dv['group']}): {dv['context'][:100]}...")
print()

# ============================================================================
# METRIC 3: MODULARITY / COMMUNITY STRUCTURE
# ============================================================================

print("="*70)
print("METRIC 3: MODULARITY / COMMUNITY")
print("="*70)
print()

modularity_patterns = [
    r'modularity[:\s=]+([0-9]+\.[0-9]+)',
    r'Q\s*[=:]\s*([0-9]+\.[0-9]+)',
    r'community[:\s=]+([0-9]+)',
    r'module[:\s=]+([0-9]+)'
]

modularity_values = []
for pattern in modularity_patterns:
    for match in re.finditer(pattern, full_text, re.IGNORECASE):
        try:
            val = float(match.group(1))
            if 0 <= val <= 1:  # Modularity range
                start = max(0, match.start() - 300)
                end = min(len(full_text), match.end() + 300)
                context = full_text[start:end].replace('\n', ' ')
                
                context_lower = context.lower()
                if 'fep' in context_lower and 'control' not in context_lower:
                    group = 'FEP'
                elif 'chr-p' in context_lower:
                    group = 'CHR-P'
                elif 'control' in context_lower or 'healthy' in context_lower:
                    group = 'Control'
                elif 'general' in context_lower:
                    group = 'General'
                else:
                    group = 'Unknown'
                
                modularity_values.append({
                    'value': val,
                    'group': group,
                    'context': context[:200]
                })
        except:
            pass

print(f"Found {len(modularity_values)} modularity values")
for mv in modularity_values[:20]:
    print(f"  {mv['value']:.2f} ({mv['group']}): {mv['context'][:100]}...")
print()

# ============================================================================
# METRIC 4: CONNECTED COMPONENTS (FRAGMENTATION)
# ============================================================================

print("="*70)
print("METRIC 4: CONNECTED COMPONENTS (FRAGMENTATION)")
print("="*70)
print()

# This metric is explicitly mentioned in the paper
cc_patterns = [
    r'connected\s+component[s]?[:\s=]+([0-9]+)',
    r'number\s+of\s+connected\s+component[s]?[:\s=]+([0-9]+)',
    r'CC\s+Number[:\s=]+([0-9]+)',
    r'mean\s+connected\s+component\s+size[:\s=]+([0-9]+\.[0-9]+)',
    r'median\s+connected\s+component\s+size[:\s=]+([0-9]+\.[0-9]+)',
    r'fragmentation[:\s=]+([0-9]+\.[0-9]+)'
]

cc_values = []
for pattern in cc_patterns:
    for match in re.finditer(pattern, full_text, re.IGNORECASE):
        try:
            val = float(match.group(1))
            start = max(0, match.start() - 400)
            end = min(len(full_text), match.end() + 400)
            context = full_text[start:end].replace('\n', ' ')
            
            context_lower = context.lower()
            
            # More careful group identification
            if 'fep patient' in context_lower:
                group = 'FEP'
            elif 'chr-p participant' in context_lower or 'chr-p' in context_lower:
                group = 'CHR-P'
            elif 'healthy control' in context_lower or 'control group' in context_lower:
                group = 'Control'
            elif 'general population' in context_lower or 'online' in context_lower:
                group = 'General'
            elif 'fep' in context_lower:
                group = 'FEP'
            elif 'control' in context_lower:
                group = 'Control'
            else:
                group = 'Unknown'
            
            cc_values.append({
                'metric': 'connected_components',
                'value': val,
                'group': group,
                'context': context[:250]
            })
        except:
            pass

print(f"Found {len(cc_values)} connected component values")
for ccv in cc_values[:30]:
    print(f"  {ccv['value']:.2f} ({ccv['group']}): {ccv['context'][:120]}...")
print()

# ============================================================================
# METRIC 5: NODES AND EDGES (NETWORK SIZE)
# ============================================================================

print("="*70)
print("METRIC 5: NODES AND EDGES (NETWORK SIZE)")
print("="*70)
print()

nodes_edges_patterns = [
    r'([0-9]+\.[0-9]+)\s*±\s*([0-9]+\.[0-9]+)\s+nodes?',
    r'([0-9]+\.[0-9]+)\s*±\s*([0-9]+\.[0-9]+)\s+edges?',
    r'nodes?[:\s=]+([0-9]+\.[0-9]+)',
    r'edges?[:\s=]+([0-9]+\.[0-9]+)'
]

size_values = []
for pattern in nodes_edges_patterns:
    for match in re.finditer(pattern, full_text, re.IGNORECASE):
        try:
            if '±' in match.group(0):
                mean_val = float(match.group(1))
                std_val = float(match.group(2))
                val = mean_val
            else:
                val = float(match.group(1))
            
            start = max(0, match.start() - 300)
            end = min(len(full_text), match.end() + 300)
            context = full_text[start:end].replace('\n', ' ')
            
            context_lower = context.lower()
            if 'fep' in context_lower and 'control' not in context_lower:
                group = 'FEP'
            elif 'chr-p' in context_lower:
                group = 'CHR-P'
            elif 'control' in context_lower or 'healthy' in context_lower:
                group = 'Control'
            elif 'general' in context_lower:
                group = 'General'
            else:
                group = 'Unknown'
            
            metric_type = 'nodes' if 'node' in match.group(0).lower() else 'edges'
            
            size_values.append({
                'metric': metric_type,
                'value': val,
                'group': group,
                'context': context[:200]
            })
        except:
            pass

print(f"Found {len(size_values)} network size values")
for sv in size_values[:30]:
    print(f"  {sv['metric']}: {sv['value']:.2f} ({sv['group']}): {sv['context'][:100]}...")
print()

# ============================================================================
# SAVE ALL RESULTS
# ============================================================================

print("="*70)
print("CONSOLIDATING RESULTS")
print("="*70)
print()

all_metrics = {
    'paper_id': 'PMC10031728',
    'path_length': path_length_values,
    'degree': degree_values,
    'modularity': modularity_values,
    'connected_components': cc_values,
    'network_size': size_values
}

with open('data/manual_extraction/PMC10031728_additional_metrics.json', 'w') as f:
    json.dump(all_metrics, f, indent=2)

print("✅ Results saved to: data/manual_extraction/PMC10031728_additional_metrics.json")
print()

# ============================================================================
# SUMMARY BY METRIC TYPE
# ============================================================================

print("="*70)
print("SUMMARY BY METRIC TYPE")
print("="*70)
print()

print(f"Path Length: {len(path_length_values)} values")
print(f"Degree: {len(degree_values)} values")
print(f"Modularity: {len(modularity_values)} values")
print(f"Connected Components: {len(cc_values)} values")
print(f"Network Size: {len(size_values)} values")
print()

# Check which metrics have patient vs. control data
print("="*70)
print("PATIENT VS. CONTROL COMPARISONS AVAILABLE:")
print("="*70)
print()

for metric_name, metric_data in [
    ('Path Length', path_length_values),
    ('Degree', degree_values),
    ('Modularity', modularity_values),
    ('Connected Components', cc_values),
    ('Network Size', size_values)
]:
    groups = [m['group'] for m in metric_data]
    has_fep = 'FEP' in groups
    has_control = 'Control' in groups
    has_chrp = 'CHR-P' in groups
    
    status = "✅" if (has_fep and has_control) else "⚠️"
    print(f"{status} {metric_name}:")
    print(f"   FEP: {has_fep}, Control: {has_control}, CHR-P: {has_chrp}")
    print()

print("="*70)
print("✅ ADDITIONAL METRICS EXTRACTION COMPLETE")
print("="*70)

