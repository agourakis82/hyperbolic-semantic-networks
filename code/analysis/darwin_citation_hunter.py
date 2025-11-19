#!/usr/bin/env python3
"""
DARWIN CITATION HUNTER - Automated Literature Search
Find all critical citations for Nature-tier manuscript
"""

import json
from dataclasses import dataclass
from typing import List, Dict
import time

print("="*70)
print("🤖 DARWIN CITATION HUNTER SYSTEM")
print("="*70)
print()

@dataclass
class Citation:
    """Citation entry"""
    id: str
    priority: str  # 'CRITICAL', 'HIGH', 'MODERATE'
    authors: str
    year: str
    title: str
    journal: str
    volume: str
    pages: str
    doi: str
    status: str  # 'HAVE', 'NEED', 'SEARCHING', 'FOUND'
    used_for: str
    where_to_cite: str

# ============================================================================
# CRITICAL CITATIONS DATABASE
# ============================================================================

CRITICAL_CITATIONS = [
    Citation(
        id="dedeyne2019",
        priority="CRITICAL",
        authors="De Deyne, S., Navarro, D. J., Perfors, A., Brysbaert, M., & Storms, G.",
        year="2019",
        title="The Small World of Words English word association norms for over 12,000 cue words",
        journal="Behavior Research Methods",
        volume="51",
        pages="987-1006",
        doi="10.3758/s13428-018-1115-7",
        status="HAVE",
        used_for="SWOW database, healthy baseline",
        where_to_cite="Methods, Results"
    ),
    
    Citation(
        id="nettekoven2023",
        priority="CRITICAL",
        authors="Nettekoven, C., et al.",
        year="2023",
        title="[NEED TO EXTRACT FROM PDF]",
        journal="[TBD]",
        volume="",
        pages="",
        doi="",
        status="NEED",
        used_for="FEP data (PMC10031728)",
        where_to_cite="Results (FEP)"
    ),
    
    Citation(
        id="heladepdet2023",
        priority="CRITICAL",
        authors="Priyadarshana, H., et al.",
        year="2023",
        title="[NEED TO FIND]",
        journal="[TBD]",
        volume="",
        pages="",
        doi="",
        status="NEED",
        used_for="HelaDepDet depression dataset",
        where_to_cite="Methods (Data)"
    ),
    
    Citation(
        id="mcnamara2005",
        priority="CRITICAL",
        authors="McNamara, T. P.",
        year="2005",
        title="Semantic Priming: Perspectives from Memory and Word Recognition",
        journal="Psychology Press",
        volume="",
        pages="",
        doi="",
        status="NEED",
        used_for="Semantic priming window (justifies window=5)",
        where_to_cite="Methods (Window Justification)"
    ),
    
    Citation(
        id="mota2012",
        priority="CRITICAL",
        authors="Mota, N. B., Vasconcelos, N. A., Lemos, N., Pieretti, A. C., Kinouchi, O., Cecchi, G. A., Copelli, M., & Ribeiro, S.",
        year="2012",
        title="Speech graphs provide a quantitative measure of thought disorder in psychosis",
        journal="PLoS ONE",
        volume="7",
        pages="e34928",
        doi="10.1371/journal.pone.0034928",
        status="NEED",
        used_for="Speech graph methodology, window-based construction",
        where_to_cite="Methods, Discussion"
    ),
    
    Citation(
        id="siew2019",
        priority="CRITICAL",
        authors="Siew, C. S., Wulff, D. U., Beckage, N. M., & Kenett, Y. N.",
        year="2019",
        title="Cognitive network science: A review of research on cognition through the lens of network representations, processes, and dynamics",
        journal="Complexity",
        volume="2019",
        pages="2108423",
        doi="10.1155/2019/2108423",
        status="NEED",
        used_for="Cognitive network science framework",
        where_to_cite="Introduction, Methods, Discussion"
    ),
    
    Citation(
        id="ollivier2009",
        priority="CRITICAL",
        authors="Ollivier, Y.",
        year="2009",
        title="Ricci curvature of Markov chains on metric spaces",
        journal="Journal of Functional Analysis",
        volume="256",
        pages="810-864",
        doi="10.1016/j.jfa.2008.11.001",
        status="NEED",
        used_for="Ollivier-Ricci curvature definition",
        where_to_cite="Methods (Curvature)"
    ),
    
    Citation(
        id="ni2015",
        priority="CRITICAL",
        authors="Ni, C. C., Lin, Y. Y., Gao, J., Gu, X. D., & Saucan, E.",
        year="2015",
        title="Ricci curvature of the Internet topology",
        journal="IEEE INFOCOM",
        volume="",
        pages="2758-2766",
        doi="10.1109/INFOCOM.2015.7218668",
        status="NEED",
        used_for="OR curvature in networks, alpha parameter",
        where_to_cite="Methods"
    ),
    
    Citation(
        id="heaps1978",
        priority="CRITICAL",
        authors="Heaps, H. S.",
        year="1978",
        title="Information Retrieval: Computational and Theoretical Aspects",
        journal="Academic Press",
        volume="",
        pages="",
        doi="",
        status="NEED",
        used_for="Heaps' Law (vocabulary growth)",
        where_to_cite="Methods (Sample Size), Discussion"
    ),
    
    Citation(
        id="efron1994",
        priority="CRITICAL",
        authors="Efron, B., & Tibshirani, R. J.",
        year="1994",
        title="An Introduction to the Bootstrap",
        journal="Chapman and Hall/CRC",
        volume="",
        pages="",
        doi="10.1201/9780429246593",
        status="NEED",
        used_for="Bootstrap methodology",
        where_to_cite="Methods (Validation)"
    ),
    
    Citation(
        id="borenstein2009",
        priority="CRITICAL",
        authors="Borenstein, M., Hedges, L. V., Higgins, J. P., & Rothstein, H. R.",
        year="2009",
        title="Introduction to Meta-Analysis",
        journal="John Wiley & Sons",
        volume="",
        pages="",
        doi="10.1002/9780470743386",
        status="NEED",
        used_for="Meta-analysis methodology",
        where_to_cite="Methods (Meta-Analysis)"
    ),
    
    Citation(
        id="higgins2003",
        priority="CRITICAL",
        authors="Higgins, J. P., Thompson, S. G., Deeks, J. J., & Altman, D. G.",
        year="2003",
        title="Measuring inconsistency in meta-analyses",
        journal="BMJ",
        volume="327",
        pages="557-560",
        doi="10.1136/bmj.327.7414.557",
        status="NEED",
        used_for="I² statistic",
        where_to_cite="Methods, Results"
    ),
    
    Citation(
        id="kapur2003",
        priority="CRITICAL",
        authors="Kapur, S.",
        year="2003",
        title="Psychosis as a state of aberrant salience",
        journal="American Journal of Psychiatry",
        volume="160",
        pages="13-23",
        doi="10.1176/appi.ajp.160.1.13",
        status="NEED",
        used_for="Aberrant salience theory (explains FEP hyperconnectivity)",
        where_to_cite="Discussion (FEP)"
    ),
    
    Citation(
        id="chung1997",
        priority="CRITICAL",
        authors="Chung, F. R.",
        year="1997",
        title="Spectral Graph Theory",
        journal="American Mathematical Society",
        volume="",
        pages="",
        doi="",
        status="NEED",
        used_for="Spectral entropy theoretical foundation",
        where_to_cite="Methods (Entropy)"
    ),
    
    Citation(
        id="cohen1988",
        priority="CRITICAL",
        authors="Cohen, J.",
        year="1988",
        title="Statistical Power Analysis for the Behavioral Sciences",
        journal="Lawrence Erlbaum Associates",
        volume="",
        pages="",
        doi="",
        status="HAVE",
        used_for="Effect sizes, power analysis",
        where_to_cite="Methods, Results"
    ),
]

# ============================================================================
# SAVE CITATION DATABASE
# ============================================================================

citations_dict = {
    'total_citations': len(CRITICAL_CITATIONS),
    'critical_citations': len([c for c in CRITICAL_CITATIONS if c.priority == 'CRITICAL']),
    'have': len([c for c in CRITICAL_CITATIONS if c.status == 'HAVE']),
    'need': len([c for c in CRITICAL_CITATIONS if c.status == 'NEED']),
    'citations': [
        {
            'id': c.id,
            'priority': c.priority,
            'authors': c.authors,
            'year': c.year,
            'title': c.title,
            'journal': c.journal,
            'volume': c.volume,
            'pages': c.pages,
            'doi': c.doi,
            'status': c.status,
            'used_for': c.used_for,
            'where_to_cite': c.where_to_cite
        }
        for c in CRITICAL_CITATIONS
    ]
}

with open('data/citations_database.json', 'w') as f:
    json.dump(citations_dict, f, indent=2)

print("✅ Saved citation database: data/citations_database.json")
print()

# Summary
print("="*70)
print("CITATION DATABASE SUMMARY")
print("="*70)
print()
print(f"Total citations tracked: {citations_dict['total_citations']}")
print(f"  CRITICAL priority: {citations_dict['critical_citations']}")
print(f"  Have: {citations_dict['have']}")
print(f"  Need: {citations_dict['need']}")
print()

print("Citations NEED to find:")
for c in CRITICAL_CITATIONS:
    if c.status == 'NEED':
        print(f"  • [{c.id}] {c.authors} ({c.year})")
        print(f"    {c.title}")
        print()

print("="*70)
print("🎯 NEXT: Deploy search agents to find all missing citations")
print("="*70)

