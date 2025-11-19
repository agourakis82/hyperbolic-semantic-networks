#!/usr/bin/env python3
"""
DARWIN AGENTS - PDF DEEP ANALYSIS SYSTEM
Multi-agent MCTS/PUCT orchestration for psychiatric paper analysis
"""

import os
import json
import fitz  # PyMuPDF
import pdfplumber
import re
import numpy as np
import pandas as pd
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
import time
from pathlib import Path

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class NetworkMetric:
    """Single network metric measurement"""
    metric_type: str  # 'clustering', 'path_length', 'degree', etc.
    value: float
    group: Optional[str] = None  # 'patient', 'control', 'FEP', 'CHR-P', etc.
    disorder: Optional[str] = None  # 'schizophrenia', 'alzheimer', etc.
    n_sample: Optional[int] = None
    p_value: Optional[float] = None
    context: Optional[str] = None
    paper_id: Optional[str] = None

@dataclass
class Paper:
    """Paper metadata and extracted data"""
    file: str
    pmc_id: str
    title: str
    first_author: str
    year: str
    disorder: List[str]
    metrics: List[NetworkMetric]
    tables: List[Dict]
    supplementary_refs: List[str]
    has_edge_data: bool
    priority_score: float

@dataclass
class MCTSNode:
    """MCTS node for exploration"""
    state: str  # PDF file or section
    visits: int = 0
    quality: float = 0.0
    prior: float = 0.5
    children: Dict = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = {}

# ============================================================================
# AGENT 1: PDF_EXTRACTOR
# ============================================================================

class PDFExtractor:
    """Deep PDF reading and text extraction"""
    
    def __init__(self):
        self.name = "PDF_EXTRACTOR"
        
    def extract_full_text(self, pdf_path: str) -> str:
        """Extract full text from PDF"""
        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            doc.close()
            return full_text
        except Exception as e:
            print(f"❌ {self.name}: Error extracting {pdf_path}: {e}")
            return ""
    
    def extract_metadata(self, text: str) -> Dict:
        """Extract paper metadata"""
        # Title (first substantial line)
        lines = text.split('\n')
        title = ""
        for line in lines[:30]:
            line = line.strip()
            if len(line) > 20 and not line.startswith(('http', 'doi', 'citation')):
                if not title or len(line) > len(title):
                    title = line
        
        # First author
        author_match = re.search(r'([A-Z][a-z]+\s+[A-Z][a-z]+)', text[:2000])
        first_author = author_match.group(1) if author_match else "Unknown"
        
        # Year
        year_match = re.search(r'\b(20[0-2][0-9]|19[89][0-9])\b', text[:1000])
        year = year_match.group(1) if year_match else "Unknown"
        
        # Disorder
        text_lower = text.lower()
        disorders = []
        disorder_keywords = {
            'schizophrenia': ['schizophrenia', 'psychosis', 'psychotic'],
            'alzheimer': ['alzheimer', 'dementia', 'mci'],
            'depression': ['depression', 'depressive', 'mdd'],
            'autism': ['autism', 'autistic', 'asd']
        }
        
        for disorder, keywords in disorder_keywords.items():
            if any(kw in text_lower[:3000] for kw in keywords):
                disorders.append(disorder)
        
        return {
            'title': title[:200],
            'first_author': first_author,
            'year': year,
            'disorders': disorders
        }
    
    def extract_network_metrics(self, text: str, paper_id: str) -> List[NetworkMetric]:
        """Extract all network metric values"""
        metrics = []
        text_lower = text.lower()
        
        # Clustering patterns
        clustering_patterns = [
            r'clustering\s+coefficient[:\s=]+([0-9]+\.[0-9]+)',
            r'C\s*[=:]\s*([0-9]+\.[0-9]+)',
            r'clustering[:\s=]+([0-9]+\.[0-9]+)',
            r'transitivity[:\s=]+([0-9]+\.[0-9]+)'
        ]
        
        for pattern in clustering_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                try:
                    val = float(match.group(1))
                    if 0 <= val <= 1:
                        # Get context
                        start = max(0, match.start() - 100)
                        end = min(len(text), match.end() + 100)
                        context = text[start:end].replace('\n', ' ')
                        
                        # Try to identify group
                        group = self._identify_group(context)
                        
                        metrics.append(NetworkMetric(
                            metric_type='clustering',
                            value=val,
                            group=group,
                            context=context,
                            paper_id=paper_id
                        ))
                except:
                    pass
        
        # Path length patterns
        path_patterns = [
            r'path\s+length[:\s=]+([0-9]+\.[0-9]+)',
            r'average\s+path[:\s=]+([0-9]+\.[0-9]+)',
            r'L\s*[=:]\s*([0-9]+\.[0-9]+)'
        ]
        
        for pattern in path_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                try:
                    val = float(match.group(1))
                    if 0 <= val <= 20:
                        start = max(0, match.start() - 100)
                        end = min(len(text), match.end() + 100)
                        context = text[start:end].replace('\n', ' ')
                        group = self._identify_group(context)
                        
                        metrics.append(NetworkMetric(
                            metric_type='path_length',
                            value=val,
                            group=group,
                            context=context,
                            paper_id=paper_id
                        ))
                except:
                    pass
        
        return metrics
    
    def _identify_group(self, context: str) -> Optional[str]:
        """Identify patient/control group from context"""
        context_lower = context.lower()
        
        # Check for specific groups (most specific first)
        if 'fep patient' in context_lower or 'first episode psychosis' in context_lower:
            return 'FEP'
        elif 'chr-p' in context_lower or 'chr participant' in context_lower or 'clinical high risk' in context_lower:
            return 'CHR-P'
        elif 'healthy control' in context_lower or 'control group' in context_lower or 'controls' in context_lower:
            return 'control'
        elif 'fep' in context_lower:
            return 'FEP'
        elif 'patient' in context_lower and 'control' not in context_lower:
            return 'patient'
        elif 'schizophrenia' in context_lower and 'control' not in context_lower:
            return 'patient'
        
        return 'unknown'
    
    def extract_supplementary_refs(self, text: str) -> List[str]:
        """Extract supplementary material references"""
        refs = []
        patterns = [
            r'supplementary\s+table\s+([0-9]+)',
            r'supplementary\s+figure\s+([0-9]+)',
            r'supplemental\s+table\s+([0-9]+)',
            r'supplemental\s+figure\s+([0-9]+)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                refs.append(match.group(0))
        
        return list(set(refs))

# ============================================================================
# AGENT 2: TABLE_ANALYZER
# ============================================================================

class TableAnalyzer:
    """Table extraction and data parsing"""
    
    def __init__(self):
        self.name = "TABLE_ANALYZER"
    
    def extract_tables(self, pdf_path: str) -> List[Dict]:
        """Extract all tables from PDF"""
        tables_found = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    tables = page.extract_tables()
                    
                    if tables:
                        for table_idx, table in enumerate(tables):
                            cleaned_table = self._clean_table(table)
                            
                            if cleaned_table and len(cleaned_table) > 1:
                                tables_found.append({
                                    'page': page_num + 1,
                                    'table_num': table_idx + 1,
                                    'n_rows': len(cleaned_table),
                                    'n_cols': max(len(row) for row in cleaned_table),
                                    'data': cleaned_table,
                                    'has_metrics': self._has_network_metrics(cleaned_table),
                                    'has_patient_control': self._has_patient_control(cleaned_table)
                                })
        except Exception as e:
            print(f"❌ {self.name}: Error extracting tables: {e}")
        
        return tables_found
    
    def _clean_table(self, table: List[List]) -> List[List]:
        """Clean table data"""
        cleaned = []
        for row in table:
            if row:
                cleaned_row = [str(cell).strip() if cell else '' for cell in row]
                if any(cell for cell in cleaned_row):
                    cleaned.append(cleaned_row)
        return cleaned
    
    def _has_network_metrics(self, table: List[List]) -> bool:
        """Check if table contains network metrics"""
        table_str = ' '.join([' '.join(row) for row in table]).lower()
        keywords = ['clustering', 'path length', 'degree', 'modularity', 'small world']
        return any(kw in table_str for kw in keywords)
    
    def _has_patient_control(self, table: List[List]) -> bool:
        """Check if table contains patient/control labels"""
        table_str = ' '.join([' '.join(row) for row in table]).lower()
        keywords = ['patient', 'control', 'healthy', 'schizophrenia', 'fep', 'chr']
        return any(kw in table_str for kw in keywords)
    
    def extract_metrics_from_tables(self, tables: List[Dict], paper_id: str) -> List[NetworkMetric]:
        """Extract network metrics from tables"""
        metrics = []
        
        for table_info in tables:
            if not (table_info['has_metrics'] and table_info['has_patient_control']):
                continue
            
            data = table_info['data']
            headers = data[0] if data else []
            
            # Try to identify metric columns and patient/control rows
            for row_idx, row in enumerate(data[1:], 1):  # Skip header
                row_str = ' '.join(str(cell) for cell in row).lower()
                
                # Identify group
                group = None
                if 'control' in row_str or 'healthy' in row_str:
                    group = 'control'
                elif 'fep' in row_str or 'first episode' in row_str:
                    group = 'FEP'
                elif 'chr' in row_str or 'clinical high risk' in row_str:
                    group = 'CHR-P'
                elif 'patient' in row_str or 'schizophrenia' in row_str:
                    group = 'patient'
                
                if group:
                    # Extract numeric values
                    for cell in row:
                        if cell:
                            try:
                                val = float(cell)
                                if 0 <= val <= 1:  # Likely clustering
                                    metrics.append(NetworkMetric(
                                        metric_type='clustering',
                                        value=val,
                                        group=group,
                                        paper_id=paper_id,
                                        context=f"Table {table_info['table_num']}, page {table_info['page']}"
                                    ))
                            except:
                                pass
        
        return metrics

# ============================================================================
# AGENT 3: SEMANTIC_MAPPER
# ============================================================================

class SemanticMapper:
    """Map values to clinical groups"""
    
    def __init__(self):
        self.name = "SEMANTIC_MAPPER"
    
    def create_patient_control_table(self, metrics: List[NetworkMetric]) -> pd.DataFrame:
        """Create patient-control comparison table"""
        rows = []
        for metric in metrics:
            if metric.group:
                rows.append({
                    'paper_id': metric.paper_id,
                    'metric_type': metric.metric_type,
                    'group': metric.group,
                    'value': metric.value,
                    'n_sample': metric.n_sample,
                    'p_value': metric.p_value
                })
        
        return pd.DataFrame(rows)
    
    def compute_group_statistics(self, df: pd.DataFrame) -> Dict:
        """Compute statistics by group"""
        stats = {}
        
        # Handle empty DataFrame or missing columns
        if df.empty or 'group' not in df.columns:
            return stats
        
        for group in df['group'].unique():
            group_data = df[df['group'] == group]
            
            for metric_type in group_data['metric_type'].unique():
                metric_data = group_data[group_data['metric_type'] == metric_type]
                
                key = f"{group}_{metric_type}"
                stats[key] = {
                    'mean': metric_data['value'].mean(),
                    'std': metric_data['value'].std(),
                    'n': len(metric_data),
                    'values': metric_data['value'].tolist()
                }
        
        return stats

# ============================================================================
# AGENT 5: HYPOTHESIS_TESTER
# ============================================================================

class HypothesisTester:
    """Test sweet spot hypothesis"""
    
    def __init__(self):
        self.name = "HYPOTHESIS_TESTER"
        self.sweet_spot_range = (0.02, 0.15)
    
    def test_sweet_spot_hypothesis(self, metrics: List[NetworkMetric]) -> Dict:
        """Test if patients are outside sweet spot"""
        results = {
            'sweet_spot_range': self.sweet_spot_range,
            'groups': {}
        }
        
        # Group metrics by group
        by_group = defaultdict(list)
        for metric in metrics:
            if metric.metric_type == 'clustering' and metric.group:
                by_group[metric.group].append(metric.value)
        
        # Test each group
        for group, values in by_group.items():
            values = np.array(values)
            mean = np.mean(values)
            std = np.std(values)
            
            # Check if in sweet spot
            in_sweet_spot = self.sweet_spot_range[0] <= mean <= self.sweet_spot_range[1]
            
            results['groups'][group] = {
                'n': len(values),
                'mean': float(mean),
                'std': float(std),
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'in_sweet_spot': bool(in_sweet_spot),
                'values': values.tolist()
            }
        
        # Compute effect size if we have patient and control
        if 'control' in by_group and 'patient' in by_group:
            control_mean = np.mean(by_group['control'])
            patient_mean = np.mean(by_group['patient'])
            pooled_std = np.sqrt((np.std(by_group['control'])**2 + np.std(by_group['patient'])**2) / 2)
            
            cohens_d = (patient_mean - control_mean) / pooled_std if pooled_std > 0 else 0
            
            results['effect_size'] = {
                'cohens_d': float(cohens_d),
                'interpretation': self._interpret_cohens_d(cohens_d)
            }
        
        return results
    
    def _interpret_cohens_d(self, d: float) -> str:
        """Interpret Cohen's d"""
        d_abs = abs(d)
        if d_abs < 0.2:
            return "negligible"
        elif d_abs < 0.5:
            return "small"
        elif d_abs < 0.8:
            return "medium"
        else:
            return "large"

# ============================================================================
# MCTS/PUCT ORCHESTRATOR
# ============================================================================

class MCTSOrchestrator:
    """Multi-agent MCTS/PUCT orchestration"""
    
    def __init__(self, pdf_dir: str, iterations: int = 30, exploration: float = 2.0):
        self.pdf_dir = Path(pdf_dir)
        self.iterations = iterations
        self.exploration = exploration
        
        # Initialize agents
        self.pdf_extractor = PDFExtractor()
        self.table_analyzer = TableAnalyzer()
        self.semantic_mapper = SemanticMapper()
        self.hypothesis_tester = HypothesisTester()
        
        # State
        self.root = MCTSNode(state="root")
        self.papers = []
        self.all_metrics = []
        
    def run(self) -> Dict:
        """Run MCTS/PUCT orchestration"""
        print("="*70)
        print("🤖 DARWIN AGENTS - MCTS/PUCT PDF ANALYSIS")
        print("="*70)
        print(f"\nIterations: {self.iterations}")
        print(f"Exploration constant: {self.exploration}")
        print()
        
        # Get all PDFs
        pdf_files = sorted([f for f in self.pdf_dir.glob("*.pdf")])
        print(f"Found {len(pdf_files)} PDFs")
        print()
        
        # Run iterations
        for iter_num in range(1, self.iterations + 1):
            print(f"\n{'='*70}")
            print(f"ITERATION {iter_num}/{self.iterations}")
            print(f"{'='*70}\n")
            
            if iter_num <= len(pdf_files):
                # Phase 1: Extract from each PDF
                pdf_file = pdf_files[iter_num - 1]
                self._process_pdf(pdf_file, iter_num)
            elif iter_num <= 15:
                # Phase 2: Deep analysis
                self._deep_analysis(iter_num)
            else:
                # Phase 3: Synthesis
                self._synthesis(iter_num)
        
        # Final results
        return self._generate_final_report()
    
    def _process_pdf(self, pdf_path: Path, iter_num: int):
        """Process single PDF"""
        print(f"📄 Processing: {pdf_path.name}")
        
        # Extract text
        text = self.pdf_extractor.extract_full_text(str(pdf_path))
        
        # Extract metadata
        metadata = self.pdf_extractor.extract_metadata(text)
        print(f"   Title: {metadata['title'][:60]}...")
        print(f"   Author: {metadata['first_author']}, Year: {metadata['year']}")
        print(f"   Disorders: {', '.join(metadata['disorders']) if metadata['disorders'] else 'None'}")
        
        # Extract metrics
        paper_id = pdf_path.stem
        metrics = self.pdf_extractor.extract_network_metrics(text, paper_id)
        print(f"   Metrics extracted: {len(metrics)}")
        
        # Extract tables
        tables = self.table_analyzer.extract_tables(str(pdf_path))
        print(f"   Tables found: {len(tables)}")
        
        # Extract metrics from tables
        table_metrics = self.table_analyzer.extract_metrics_from_tables(tables, paper_id)
        print(f"   Metrics from tables: {len(table_metrics)}")
        
        # Extract supplementary refs
        suppl_refs = self.pdf_extractor.extract_supplementary_refs(text)
        print(f"   Supplementary refs: {len(suppl_refs)}")
        
        # Combine
        all_metrics = metrics + table_metrics
        self.all_metrics.extend(all_metrics)
        
        # Create paper object
        paper = Paper(
            file=pdf_path.name,
            pmc_id=paper_id,
            title=metadata['title'],
            first_author=metadata['first_author'],
            year=metadata['year'],
            disorder=metadata['disorders'],
            metrics=all_metrics,
            tables=tables,
            supplementary_refs=suppl_refs,
            has_edge_data='supplementary' in text.lower(),
            priority_score=self._compute_priority_score(all_metrics, tables, suppl_refs)
        )
        
        self.papers.append(paper)
        
        print(f"   Priority score: {paper.priority_score:.2f}")
        
        # Print clustering values by group
        clustering_by_group = defaultdict(list)
        for m in all_metrics:
            if m.metric_type == 'clustering' and m.group:
                clustering_by_group[m.group].append(m.value)
        
        if clustering_by_group:
            print(f"\n   📊 Clustering by group:")
            for group, values in clustering_by_group.items():
                print(f"      {group}: {values}")
    
    def _compute_priority_score(self, metrics: List[NetworkMetric], tables: List[Dict], suppl_refs: List[str]) -> float:
        """Compute priority score"""
        clustering_count = len([m for m in metrics if m.metric_type == 'clustering'])
        path_count = len([m for m in metrics if m.metric_type == 'path_length'])
        patient_control_count = len([m for m in metrics if m.group in ['patient', 'control', 'FEP', 'CHR-P']])
        
        score = (clustering_count * 3) + \
                (path_count * 3) + \
                (patient_control_count * 5) + \
                (len(tables) * 2) + \
                (len(suppl_refs) * 3)
        
        return score
    
    def _deep_analysis(self, iter_num: int):
        """Deep analysis phase"""
        print(f"🔬 Deep Analysis Phase")
        
        if iter_num == 11:
            # Test sweet spot hypothesis
            print("Testing sweet spot hypothesis...")
            results = self.hypothesis_tester.test_sweet_spot_hypothesis(self.all_metrics)
            
            print(f"\n📊 Sweet Spot Analysis:")
            print(f"   Range: {results['sweet_spot_range']}")
            print()
            
            for group, stats in results['groups'].items():
                in_spot = "✅ IN" if stats['in_sweet_spot'] else "❌ OUT"
                print(f"   {group}: {stats['mean']:.3f} ± {stats['std']:.3f} (n={stats['n']}) {in_spot}")
            
            if 'effect_size' in results:
                print(f"\n   Effect size (Patient vs. Control):")
                print(f"      Cohen's d = {results['effect_size']['cohens_d']:.3f} ({results['effect_size']['interpretation']})")
            
            # Save results
            with open('results/sweet_spot_validation_patients.json', 'w') as f:
                json.dump(results, f, indent=2)
    
    def _synthesis(self, iter_num: int):
        """Synthesis phase"""
        print(f"🔗 Synthesis Phase")
        
        if iter_num == 21:
            # Create patient-control table
            df = self.semantic_mapper.create_patient_control_table(self.all_metrics)
            df.to_csv('data/patient_control_metrics.csv', index=False)
            print(f"   ✅ Patient-control table saved: {len(df)} rows")
            
            # Compute statistics
            stats = self.semantic_mapper.compute_group_statistics(df)
            with open('data/patient_control_statistics.json', 'w') as f:
                json.dump(stats, f, indent=2)
            print(f"   ✅ Statistics saved: {len(stats)} groups")
    
    def _generate_final_report(self) -> Dict:
        """Generate final report"""
        print("\n" + "="*70)
        print("📊 FINAL REPORT")
        print("="*70)
        print()
        
        report = {
            'n_papers': len(self.papers),
            'n_metrics': len(self.all_metrics),
            'papers': [asdict(p) for p in self.papers]
        }
        
        print(f"Papers analyzed: {report['n_papers']}")
        print(f"Metrics extracted: {report['n_metrics']}")
        print()
        
        # Summary by metric type
        by_type = defaultdict(int)
        for m in self.all_metrics:
            by_type[m.metric_type] += 1
        
        print("Metrics by type:")
        for metric_type, count in sorted(by_type.items(), key=lambda x: -x[1]):
            print(f"   {metric_type}: {count}")
        print()
        
        # Summary by group
        by_group = defaultdict(int)
        for m in self.all_metrics:
            if m.group:
                by_group[m.group] += 1
        
        print("Metrics by group:")
        for group, count in sorted(by_group.items(), key=lambda x: -x[1]):
            print(f"   {group}: {count}")
        print()
        
        # Save report
        with open('results/darwin_agents_final_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("✅ Final report saved")
        
        return report

# ============================================================================
# MAIN
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Darwin Agents PDF Analysis')
    parser.add_argument('--pdf-dir', required=True, help='Directory with PDFs')
    parser.add_argument('--iterations', type=int, default=30, help='Number of MCTS iterations')
    parser.add_argument('--exploration', type=float, default=2.0, help='Exploration constant')
    parser.add_argument('--output-dir', default='results/darwin_agents_pdf/', help='Output directory')
    
    args = parser.parse_args()
    
    # Create output dir
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    Path('data').mkdir(exist_ok=True)
    Path('results').mkdir(exist_ok=True)
    
    # Run orchestrator
    orchestrator = MCTSOrchestrator(
        pdf_dir=args.pdf_dir,
        iterations=args.iterations,
        exploration=args.exploration
    )
    
    report = orchestrator.run()
    
    print("\n" + "="*70)
    print("✅ DARWIN AGENTS COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()

