#!/usr/bin/env python3
"""
SYSTEMATIC LITERATURE SEARCH - Pre-submission validation
Find ALL related work before claiming novelty
"""

import json
from datetime import datetime
from pathlib import Path

print("="*70)
print("📚 SYSTEMATIC LITERATURE SEARCH")
print("="*70)
print()

# ============================================================================
# SEARCH PROTOCOL
# ============================================================================

SEARCH_QUERIES = [
    {
        'id': 'Q1',
        'query': '"Ricci curvature" AND "semantic network"',
        'rationale': 'Direct overlap - most critical!',
        'databases': ['Google Scholar', 'Web of Science', 'Scopus'],
        'expected_n': '0-10',
        'priority': 'CRITICAL'
    },
    {
        'id': 'Q2',
        'query': '"Ollivier-Ricci" AND "language"',
        'rationale': 'OR curvature applied to linguistic data',
        'databases': ['Google Scholar', 'arXiv'],
        'expected_n': '0-20',
        'priority': 'CRITICAL'
    },
    {
        'id': 'Q3',
        'query': '"geometric" AND "word association" AND "network"',
        'rationale': 'Geometric analysis of word networks',
        'databases': ['Google Scholar', 'PubMed'],
        'expected_n': '10-50',
        'priority': 'HIGH'
    },
    {
        'id': 'Q4',
        'query': '"clustering coefficient" AND "curvature" AND "psychopathology"',
        'rationale': 'Clustering-curvature in disorders',
        'databases': ['PubMed', 'PsyArXiv'],
        'expected_n': '0-10',
        'priority': 'CRITICAL'
    },
    {
        'id': 'Q5',
        'query': '"hyperbolic geometry" AND "semantic"',
        'rationale': 'Hyperbolic geometry in semantic networks',
        'databases': ['Google Scholar', 'arXiv'],
        'expected_n': '10-30',
        'priority': 'HIGH'
    },
    {
        'id': 'Q6',
        'query': '"network geometry" AND ("mental disorder" OR "psychopathology")',
        'rationale': 'Geometric network analysis in psychiatry',
        'databases': ['PubMed', 'bioRxiv'],
        'expected_n': '20-50',
        'priority': 'HIGH'
    },
    {
        'id': 'Q7',
        'query': '"speech graph" AND ("curvature" OR "geometry")',
        'rationale': 'Geometric analysis of speech graphs',
        'databases': ['Google Scholar', 'PubMed'],
        'expected_n': '0-5',
        'priority': 'CRITICAL'
    },
    {
        'id': 'Q8',
        'query': '"semantic fluency" AND "network topology" AND "schizophrenia"',
        'rationale': 'Topology of semantic networks in disorders',
        'databases': ['PubMed'],
        'expected_n': '20-50',
        'priority': 'HIGH'
    },
]

# ============================================================================
# KEY PAPERS TO READ (IDENTIFIED)
# ============================================================================

KEY_PAPERS = {
    'Kenett': [
        'Kenett et al. (2011) - Global and local features Hebrew lexicon',
        'Kenett et al. (2014) - Creative semantic networks',
        'Kenett et al. (2016) - Asperger associative mind',
        'Kenett et al. (2018) - Schizophrenia semantic networks',
    ],
    'Siew': [
        'Siew et al. (2019) - Cognitive network science review (READ ALL REFS!)',
        'Siew (empirical papers on disorders)',
    ],
    'Mota': [
        'Mota et al. (2012) - Speech graphs in psychosis',
        'Mota et al. (2014, 2017) - Follow-up work',
    ],
    'Network_Geometry': [
        'Krioukov et al. (2010) - Hyperbolic geometry of complex networks',
        'Bianconi papers on network geometry',
        'Ni et al. (2015, 2019) - Ricci curvature applications',
    ],
}

# ============================================================================
# SCREENING CRITERIA
# ============================================================================

INCLUSION_CRITERIA = {
    'Must have ONE of:': [
        'Ricci curvature OR geometric analysis',
        'Semantic networks OR word associations',
        'Psychiatric disorders + network analysis',
        'Clustering-curvature relationship',
    ],
    'Relevance levels:': {
        'HIGH': 'Direct overlap (curvature + semantics + disorders)',
        'MEDIUM': 'Two of three components',
        'LOW': 'One component only',
    }
}

# ============================================================================
# OUTPUT STRUCTURE
# ============================================================================

search_protocol = {
    'date_created': datetime.now().isoformat(),
    'purpose': 'Pre-submission validation - find ALL related work',
    'timeline': '4 weeks (Week 1: Literature review)',
    'search_queries': SEARCH_QUERIES,
    'key_papers_identified': KEY_PAPERS,
    'screening_criteria': INCLUSION_CRITERIA,
    'deliverables': [
        'Complete bibliography (50-100 papers)',
        'Categorized by relevance',
        'Read 20-30 most relevant',
        'Literature matrix (papers × our contributions)',
        'Gap analysis (what we did that others didn\'t)',
        'Positioning statement',
    ]
}

# Save protocol
Path('data').mkdir(exist_ok=True)
with open('data/literature_search_protocol.json', 'w') as f:
    json.dump(search_protocol, f, indent=2)

print("✅ Saved search protocol: data/literature_search_protocol.json")
print()

# Display summary
print("="*70)
print("SEARCH PROTOCOL SUMMARY")
print("="*70)
print()
print(f"Total queries: {len(SEARCH_QUERIES)}")
print(f"  CRITICAL priority: {sum(1 for q in SEARCH_QUERIES if q['priority'] == 'CRITICAL')}")
print(f"  HIGH priority: {sum(1 for q in SEARCH_QUERIES if q['priority'] == 'HIGH')}")
print()

print("Queries to execute:")
for q in SEARCH_QUERIES:
    print(f"\n[{q['id']}] {q['priority']}")
    print(f"  Query: {q['query']}")
    print(f"  Expected: {q['expected_n']} papers")
    print(f"  Databases: {', '.join(q['databases'])}")

print()
print("="*70)
print("Key Papers to Read:")
print("="*70)
for category, papers in KEY_PAPERS.items():
    print(f"\n{category}:")
    for p in papers:
        print(f"  • {p}")

print()
print("="*70)
print("✅ SEARCH PROTOCOL READY!")
print("="*70)
print()
print("🎯 NEXT STEPS:")
print("  1. Execute searches (Google Scholar, PubMed, arXiv)")
print("  2. Screen results (title + abstract)")
print("  3. Download full texts (~20-30 papers)")
print("  4. Deep read + extract findings")
print("  5. Create literature matrix")
print("  6. Identify genuine gaps")
print()
print("ETA Week 1: 7 days for complete literature review")

