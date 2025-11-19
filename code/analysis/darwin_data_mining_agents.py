#!/usr/bin/env python3
"""
DARWIN DATA MINING AGENTS
Search for semantic network datasets in psychopathology
"""

import requests
import json
import time
from pathlib import Path
from typing import List, Dict
import re

# ============================================================================
# AGENT 1: ZENODO SCOUT
# ============================================================================

class ZenodoScout:
    """Search Zenodo for semantic network datasets"""
    
    def __init__(self):
        self.name = "ZENODO_SCOUT"
        self.base_url = "https://zenodo.org/api/records"
        
    def search(self, query: str, size: int = 20) -> List[Dict]:
        """Search Zenodo API"""
        print(f"\n{'='*70}")
        print(f"{self.name}: Searching Zenodo")
        print(f"{'='*70}\n")
        print(f"Query: {query}")
        print()
        
        params = {
            'q': query,
            'size': size,
            'type': 'dataset'
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                hits = data.get('hits', {}).get('hits', [])
                print(f"✅ Found {len(hits)} results")
                return hits
            else:
                print(f"❌ Error: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Exception: {e}")
            return []

# ============================================================================
# AGENT 2: OSF SCOUT
# ============================================================================

class OSFScout:
    """Search OSF for semantic network datasets"""
    
    def __init__(self):
        self.name = "OSF_SCOUT"
        self.base_url = "https://api.osf.io/v2/search"
        
    def search(self, query: str, size: int = 20) -> List[Dict]:
        """Search OSF API"""
        print(f"\n{'='*70}")
        print(f"{self.name}: Searching OSF")
        print(f"{'='*70}\n")
        print(f"Query: {query}")
        print()
        
        params = {
            'q': query,
            'filter[tags]': 'data',
            'page[size]': size
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                results = data.get('data', [])
                print(f"✅ Found {len(results)} results")
                return results
            else:
                print(f"❌ Error: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Exception: {e}")
            return []

# ============================================================================
# AGENT 3: KNOWN PAPERS SCOUT
# ============================================================================

class KnownPapersScout:
    """Search for known papers with supplementary data"""
    
    def __init__(self):
        self.name = "KNOWN_PAPERS_SCOUT"
        self.known_papers = [
            {
                'authors': 'Mota et al.',
                'year': 2012,
                'title': 'Speech graphs provide a quantitative measure of thought disorder in psychosis',
                'journal': 'PLOS ONE',
                'doi': '10.1371/journal.pone.0034928',
                'has_data': 'possibly in supplementary',
                'keywords': ['schizophrenia', 'speech graph', 'thought disorder']
            },
            {
                'authors': 'Kenett et al.',
                'year': 2016,
                'title': 'A semantic network cartography of the creative mind',
                'journal': 'Trends in Cognitive Sciences',
                'doi': '10.1016/j.tics.2016.10.004',
                'has_data': 'OSF repository possible',
                'keywords': ['semantic network', 'creativity']
            },
            {
                'authors': 'Siew et al.',
                'year': 2019,
                'title': 'Cognitive network science: A review of research on cognition through the lens of network representations, processes, and dynamics',
                'journal': 'Complexity',
                'doi': '10.1155/2019/2108423',
                'has_data': 'review paper, cites data sources',
                'keywords': ['semantic network', 'cognitive network']
            },
            {
                'authors': 'Hills et al.',
                'year': 2015,
                'title': 'Exploration versus exploitation in space, mind, and society',
                'journal': 'Trends in Cognitive Sciences',
                'doi': '10.1016/j.tics.2014.10.004',
                'has_data': 'fluency data possible',
                'keywords': ['semantic fluency', 'foraging']
            },
            {
                'authors': 'Nettekoven et al.',
                'year': 2023,
                'title': 'Semantic speech networks in psychosis',
                'journal': 'Schizophrenia Bulletin',
                'doi': '10.1093/schbul/sbac056',
                'pmc': 'PMC10031728',
                'has_data': 'supplementary tables mentioned',
                'keywords': ['FEP', 'semantic network', 'fragmentation']
            }
        ]
        
    def get_known_papers(self) -> List[Dict]:
        """Return list of known papers with potential data"""
        print(f"\n{'='*70}")
        print(f"{self.name}: Known Papers with Data")
        print(f"{'='*70}\n")
        
        for i, paper in enumerate(self.known_papers, 1):
            print(f"{i}. {paper['authors']} ({paper['year']})")
            print(f"   {paper['title'][:70]}...")
            print(f"   DOI: {paper['doi']}")
            if 'pmc' in paper:
                print(f"   PMC: {paper['pmc']}")
            print(f"   Data: {paper['has_data']}")
            print()
        
        return self.known_papers

# ============================================================================
# AGENT 4: PUBLIC DATASETS SCOUT
# ============================================================================

class PublicDatasetsScount:
    """Search for known public semantic network datasets"""
    
    def __init__(self):
        self.name = "PUBLIC_DATASETS_SCOUT"
        self.known_datasets = [
            {
                'name': 'SWOW (Small World of Words)',
                'url': 'https://smallworldofwords.org/',
                'description': 'Word association data for multiple languages',
                'has_patient_data': False,
                'languages': ['English', 'Spanish', 'Chinese', 'Dutch'],
                'n_participants': 90000,
                'format': 'CSV',
                'accessibility': 'Open access'
            },
            {
                'name': 'WordNet',
                'url': 'https://wordnet.princeton.edu/',
                'description': 'English lexical database',
                'has_patient_data': False,
                'languages': ['English'],
                'format': 'Database',
                'accessibility': 'Open access'
            },
            {
                'name': 'ConceptNet',
                'url': 'https://conceptnet.io/',
                'description': 'Multilingual semantic knowledge graph',
                'has_patient_data': False,
                'languages': ['Multiple'],
                'format': 'CSV/JSON',
                'accessibility': 'Open access'
            },
            {
                'name': 'Semantic Fluency Norms',
                'url': 'Various publications',
                'description': 'Category fluency norms (animals, fruits, etc.)',
                'has_patient_data': 'Sometimes (Alzheimer studies)',
                'languages': ['Multiple'],
                'format': 'CSV/Text',
                'accessibility': 'Open/Restricted'
            }
        ]
        
    def get_known_datasets(self) -> List[Dict]:
        """Return list of known public datasets"""
        print(f"\n{'='*70}")
        print(f"{self.name}: Known Public Datasets")
        print(f"{'='*70}\n")
        
        for i, dataset in enumerate(self.known_datasets, 1):
            print(f"{i}. {dataset['name']}")
            print(f"   URL: {dataset['url']}")
            print(f"   Description: {dataset['description']}")
            print(f"   Patient data: {dataset['has_patient_data']}")
            print(f"   Access: {dataset['accessibility']}")
            print()
        
        return self.known_datasets

# ============================================================================
# AGENT 5: SUPPLEMENTARY DATA FINDER
# ============================================================================

class SupplementaryDataFinder:
    """Find and download supplementary data from papers"""
    
    def __init__(self):
        self.name = "SUPPLEMENTARY_DATA_FINDER"
        
    def get_pmc_supplementary(self, pmc_id: str) -> Dict:
        """Get supplementary files from PMC"""
        print(f"\n{'='*70}")
        print(f"{self.name}: Searching PMC{pmc_id}")
        print(f"{'='*70}\n")
        
        base_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc_id}/"
        
        print(f"PMC URL: {base_url}")
        print(f"Check for supplementary files:")
        print(f"  - Supplementary tables (Excel, CSV)")
        print(f"  - Supplementary data files")
        print(f"  - Code/analysis scripts")
        print()
        
        return {
            'pmc_id': pmc_id,
            'url': base_url,
            'status': 'manual_check_required'
        }

# ============================================================================
# ORCHESTRATOR
# ============================================================================

class DataMiningOrchestrator:
    """Orchestrate all mining agents"""
    
    def __init__(self):
        self.zenodo = ZenodoScout()
        self.osf = OSFScout()
        self.known_papers = KnownPapersScout()
        self.public_datasets = PublicDatasetsScount()
        self.suppl_finder = SupplementaryDataFinder()
        
    def run_all_agents(self):
        """Run all data mining agents"""
        print("="*70)
        print("🤖 DARWIN DATA MINING AGENTS - ACTIVATION")
        print("="*70)
        print()
        
        results = {}
        
        # Search Zenodo
        queries = [
            "semantic network schizophrenia",
            "word association psychosis",
            "semantic fluency patient",
            "thought disorder network"
        ]
        
        results['zenodo'] = []
        for query in queries:
            hits = self.zenodo.search(query, size=10)
            results['zenodo'].extend(hits)
            time.sleep(1)  # Rate limiting
        
        # Search OSF
        results['osf'] = []
        for query in queries:
            hits = self.osf.search(query, size=10)
            results['osf'].extend(hits)
            time.sleep(1)
        
        # Get known papers
        results['known_papers'] = self.known_papers.get_known_papers()
        
        # Get public datasets
        results['public_datasets'] = self.public_datasets.get_known_datasets()
        
        # Check PMC supplementary
        results['pmc_supplementary'] = [
            self.suppl_finder.get_pmc_supplementary('10031728')
        ]
        
        # Save results
        output_dir = Path('data/external/data_mining_results')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / 'all_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"\nZenodo hits: {len(results['zenodo'])}")
        print(f"OSF hits: {len(results['osf'])}")
        print(f"Known papers: {len(results['known_papers'])}")
        print(f"Public datasets: {len(results['public_datasets'])}")
        print()
        print(f"✅ Results saved to: {output_dir / 'all_results.json'}")
        print()
        
        return results

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    orchestrator = DataMiningOrchestrator()
    results = orchestrator.run_all_agents()
    
    print("="*70)
    print("✅ DATA MINING COMPLETE")
    print("="*70)

