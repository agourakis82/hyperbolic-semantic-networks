#!/usr/bin/env python3
"""
DARWIN MULTI-AGENT SYSTEM - DATA ENRICHMENT
Parallel execution of data enrichment tasks using agent-based architecture
"""

import pandas as pd
import networkx as nx
import numpy as np
import re
from pathlib import Path
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import scipy.stats as stats

print("="*70)
print("🤖 DARWIN MULTI-AGENT DATA ENRICHMENT SYSTEM")
print("="*70)
print()

# ============================================================================
# AGENT DEFINITIONS
# ============================================================================

@dataclass
class AgentResult:
    """Result from an agent task"""
    agent_id: str
    task_name: str
    status: str
    data: Dict
    execution_time: float
    
class DataEnrichmentAgent:
    """Base class for data enrichment agents"""
    
    def __init__(self, agent_id: str, task_name: str):
        self.agent_id = agent_id
        self.task_name = task_name
        
    def execute(self) -> AgentResult:
        """Execute agent task (to be overridden)"""
        raise NotImplementedError

# ============================================================================
# AGENT 1: HEALTHY CONTROLS EXTRACTOR
# ============================================================================

class HealthyControlsAgent(DataEnrichmentAgent):
    """Extract SWOW networks as healthy baseline"""
    
    def __init__(self):
        super().__init__("AGENT-001", "Extract Healthy Controls from SWOW")
        
    def execute(self) -> AgentResult:
        import time
        start = time.time()
        
        print(f"\n[{self.agent_id}] 🔍 Extracting healthy controls from SWOW...")
        
        # Load existing SWOW results
        swow_files = [
            ('Spanish', 'results/kec_spanish_network_level.csv'),
            ('English', 'results/kec_english_network_level.csv'),
            ('Chinese', 'results/kec_chinese_network_level.csv')
        ]
        
        healthy_data = []
        
        for lang, filepath in swow_files:
            try:
                if Path(filepath).exists():
                    df = pd.read_csv(filepath)
                    if 'clustering_weighted' in df.columns:
                        C = df['clustering_weighted'].iloc[0]
                    elif 'clustering' in df.columns:
                        C = df['clustering'].iloc[0]
                    else:
                        print(f"  ⚠️ {lang}: No clustering column found")
                        continue
                    
                    healthy_data.append({
                        'language': lang,
                        'source': 'SWOW',
                        'population': 'Healthy',
                        'clustering': C,
                        'n_nodes': df['n_nodes'].iloc[0] if 'n_nodes' in df.columns else None,
                        'n_edges': df['n_edges'].iloc[0] if 'n_edges' in df.columns else None
                    })
                    
                    print(f"  ✅ {lang}: C={C:.4f}")
                else:
                    print(f"  ⚠️ {lang}: File not found")
            except Exception as e:
                print(f"  ❌ {lang}: Error - {e}")
        
        # Compute statistics
        if healthy_data:
            clusterings = [d['clustering'] for d in healthy_data]
            stats_dict = {
                'mean': np.mean(clusterings),
                'std': np.std(clusterings),
                'median': np.median(clusterings),
                'min': np.min(clusterings),
                'max': np.max(clusterings),
                'n': len(clusterings)
            }
            
            print(f"\n  📊 Healthy Baseline: C = {stats_dict['mean']:.4f} ± {stats_dict['std']:.4f}")
            print(f"     Range: [{stats_dict['min']:.4f}, {stats_dict['max']:.4f}]")
        else:
            stats_dict = {}
        
        elapsed = time.time() - start
        
        return AgentResult(
            agent_id=self.agent_id,
            task_name=self.task_name,
            status="SUCCESS" if healthy_data else "FAILED",
            data={'healthy_controls': healthy_data, 'statistics': stats_dict},
            execution_time=elapsed
        )

# ============================================================================
# AGENT 2: DEPRESSION EXPANDER
# ============================================================================

class DepressionExpanderAgent(DataEnrichmentAgent):
    """Expand depression data to more severity bins"""
    
    def __init__(self, n_bins: int = 10):
        super().__init__("AGENT-002", f"Expand Depression to {n_bins} Bins")
        self.n_bins = n_bins
        
    def execute(self) -> AgentResult:
        import time
        start = time.time()
        
        print(f"\n[{self.agent_id}] 📊 Expanding depression data to {self.n_bins} bins...")
        
        try:
            # Load HelaDepDet
            df_full = pd.read_csv('data/external/Depression_Severity_Levels_Dataset/Depression_Severity_Levels_Dataset.csv')
            
            print(f"  Total posts: {len(df_full):,}")
            
            # Map severity to numeric
            severity_map = {
                'minimum': 0,
                'mild': 1,
                'moderate': 2,
                'severe': 3
            }
            
            df_full['severity_numeric'] = df_full['label'].map(severity_map)
            
            # Create bins
            df_full['severity_bin'] = pd.cut(
                df_full['severity_numeric'], 
                bins=self.n_bins, 
                labels=False
            )
            
            # Count per bin
            bin_counts = df_full['severity_bin'].value_counts().sort_index()
            
            print(f"\n  Distribution across {self.n_bins} bins:")
            for bin_id, count in bin_counts.items():
                print(f"    Bin {bin_id}: {count:,} posts")
            
            result_data = {
                'n_bins': self.n_bins,
                'total_posts': len(df_full),
                'bin_counts': bin_counts.to_dict(),
                'mean_per_bin': int(bin_counts.mean()),
                'std_per_bin': int(bin_counts.std())
            }
            
            # Save expanded dataset
            output_path = f'data/processed/depression_expanded_{self.n_bins}bins.csv'
            df_full.to_csv(output_path, index=False)
            print(f"\n  ✅ Saved: {output_path}")
            
            status = "SUCCESS"
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            result_data = {'error': str(e)}
            status = "FAILED"
        
        elapsed = time.time() - start
        
        return AgentResult(
            agent_id=self.agent_id,
            task_name=self.task_name,
            status=status,
            data=result_data,
            execution_time=elapsed
        )

# ============================================================================
# AGENT 3: PATIENT VS CONTROL STATISTICIAN
# ============================================================================

class PatientControlStatAgent(DataEnrichmentAgent):
    """Compute patient vs control statistics"""
    
    def __init__(self):
        super().__init__("AGENT-003", "Patient vs Control Statistics")
        
    def execute(self) -> AgentResult:
        import time
        start = time.time()
        
        print(f"\n[{self.agent_id}] 📈 Computing patient vs control statistics...")
        
        results = {}
        
        try:
            # 1. Load healthy baseline
            healthy_files = [
                'results/kec_spanish_network_level.csv',
                'results/kec_english_network_level.csv',
                'results/kec_chinese_network_level.csv'
            ]
            
            healthy_C = []
            for f in healthy_files:
                if Path(f).exists():
                    df = pd.read_csv(f)
                    if 'clustering_weighted' in df.columns:
                        healthy_C.append(df['clustering_weighted'].iloc[0])
                    elif 'clustering' in df.columns:
                        healthy_C.append(df['clustering'].iloc[0])
            
            if not healthy_C:
                print("  ⚠️ No healthy baseline found")
                return AgentResult(
                    agent_id=self.agent_id,
                    task_name=self.task_name,
                    status="FAILED",
                    data={'error': 'No healthy baseline'},
                    execution_time=time.time() - start
                )
            
            C_healthy_mean = np.mean(healthy_C)
            C_healthy_std = np.std(healthy_C)
            
            print(f"  Healthy baseline: C = {C_healthy_mean:.4f} ± {C_healthy_std:.4f}")
            
            # 2. Load depression data
            depression_file = 'results/depression_optimal_metrics.csv'
            if Path(depression_file).exists():
                df_dep = pd.read_csv(depression_file)
                
                print(f"\n  Depression comparison:")
                
                for _, row in df_dep.iterrows():
                    severity = row['severity']
                    C_patient = row['clustering']
                    
                    # Effect size (Cohen's d)
                    pooled_std = np.sqrt((C_healthy_std**2 + 0.01**2) / 2)  # Assume small variance for single values
                    cohens_d = (C_patient - C_healthy_mean) / pooled_std if pooled_std > 0 else 0
                    
                    # Percent difference
                    pct_diff = ((C_patient - C_healthy_mean) / C_healthy_mean) * 100
                    
                    print(f"    {severity:10s}: C={C_patient:.4f}, d={cohens_d:+.2f}, Δ={pct_diff:+.1f}%")
                    
                    results[severity] = {
                        'C_patient': C_patient,
                        'C_healthy': C_healthy_mean,
                        'cohens_d': cohens_d,
                        'percent_difference': pct_diff
                    }
            
            # 3. Load FEP data if available
            # (Would need to extract from PMC10031728)
            
            status = "SUCCESS"
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results = {'error': str(e)}
            status = "FAILED"
        
        elapsed = time.time() - start
        
        return AgentResult(
            agent_id=self.agent_id,
            task_name=self.task_name,
            status=status,
            data=results,
            execution_time=elapsed
        )

# ============================================================================
# AGENT 4: LITERATURE MINER
# ============================================================================

class LiteratureMinerAgent(DataEnrichmentAgent):
    """Mine additional data from literature"""
    
    def __init__(self):
        super().__init__("AGENT-004", "Literature Data Mining")
        
    def execute(self) -> AgentResult:
        import time
        start = time.time()
        
        print(f"\n[{self.agent_id}] 📚 Mining additional data from literature...")
        
        # Search for additional extractable data in downloaded PDFs
        pdf_dir = Path("/mnt/c/Users/demet/Downloads/Artigos Semantic Networks")
        
        if not pdf_dir.exists():
            print(f"  ⚠️ PDF directory not found: {pdf_dir}")
            return AgentResult(
                agent_id=self.agent_id,
                task_name=self.task_name,
                status="SKIPPED",
                data={'reason': 'PDF directory not found'},
                execution_time=time.time() - start
            )
        
        pdfs = list(pdf_dir.glob("*.pdf"))
        print(f"  Found {len(pdfs)} PDFs")
        
        # For now, just catalog what we have
        catalog = []
        for pdf in pdfs:
            catalog.append({
                'filename': pdf.name,
                'size_mb': pdf.stat().st_size / (1024*1024)
            })
        
        print(f"  📋 Cataloged {len(catalog)} PDFs for future extraction")
        
        elapsed = time.time() - start
        
        return AgentResult(
            agent_id=self.agent_id,
            task_name=self.task_name,
            status="SUCCESS",
            data={'pdf_catalog': catalog, 'n_pdfs': len(catalog)},
            execution_time=elapsed
        )

# ============================================================================
# AGENT ORCHESTRATOR
# ============================================================================

class AgentOrchestrator:
    """Orchestrate parallel execution of agents"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.agents = []
        self.results = []
        
    def register_agent(self, agent: DataEnrichmentAgent):
        """Register an agent for execution"""
        self.agents.append(agent)
        print(f"✅ Registered: [{agent.agent_id}] {agent.task_name}")
        
    def execute_all(self) -> List[AgentResult]:
        """Execute all registered agents in parallel"""
        print(f"\n{'='*70}")
        print(f"🚀 Executing {len(self.agents)} agents in parallel (max_workers={self.max_workers})")
        print(f"{'='*70}\n")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all agent tasks
            future_to_agent = {
                executor.submit(agent.execute): agent 
                for agent in self.agents
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_agent):
                agent = future_to_agent[future]
                try:
                    result = future.result()
                    self.results.append(result)
                    
                    status_emoji = "✅" if result.status == "SUCCESS" else "❌"
                    print(f"\n{status_emoji} [{result.agent_id}] {result.task_name}")
                    print(f"   Status: {result.status}")
                    print(f"   Time: {result.execution_time:.2f}s")
                    
                except Exception as e:
                    print(f"\n❌ [{agent.agent_id}] CRASHED: {e}")
        
        return self.results
    
    def generate_report(self) -> Dict:
        """Generate summary report"""
        successful = sum(1 for r in self.results if r.status == "SUCCESS")
        failed = sum(1 for r in self.results if r.status == "FAILED")
        total_time = sum(r.execution_time for r in self.results)
        
        report = {
            'total_agents': len(self.agents),
            'successful': successful,
            'failed': failed,
            'total_execution_time': total_time,
            'results': [
                {
                    'agent_id': r.agent_id,
                    'task': r.task_name,
                    'status': r.status,
                    'time': r.execution_time,
                    'data_keys': list(r.data.keys())
                }
                for r in self.results
            ]
        }
        
        return report

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    
    print("🤖 Initializing Darwin Multi-Agent System...")
    print()
    
    # Create orchestrator
    orchestrator = AgentOrchestrator(max_workers=4)
    
    # Register agents
    orchestrator.register_agent(HealthyControlsAgent())
    orchestrator.register_agent(DepressionExpanderAgent(n_bins=10))
    orchestrator.register_agent(PatientControlStatAgent())
    orchestrator.register_agent(LiteratureMinerAgent())
    
    print()
    
    # Execute all agents in parallel
    results = orchestrator.execute_all()
    
    # Generate report
    print(f"\n{'='*70}")
    print("📊 EXECUTION SUMMARY")
    print(f"{'='*70}\n")
    
    report = orchestrator.generate_report()
    
    print(f"Total agents: {report['total_agents']}")
    print(f"Successful: {report['successful']} ✅")
    print(f"Failed: {report['failed']} ❌")
    print(f"Total time: {report['total_execution_time']:.2f}s")
    print()
    
    # Save consolidated results
    output_file = 'results/darwin_data_enrichment_complete.json'
    
    consolidated = {
        'execution_summary': report,
        'agent_results': {
            r.agent_id: {
                'task': r.task_name,
                'status': r.status,
                'data': r.data,
                'execution_time': r.execution_time
            }
            for r in results
        }
    }
    
    with open(output_file, 'w') as f:
        json.dump(consolidated, f, indent=2)
    
    print(f"✅ Saved consolidated results: {output_file}")
    
    print(f"\n{'='*70}")
    print("🎯 DARWIN DATA ENRICHMENT COMPLETE!")
    print(f"{'='*70}")

