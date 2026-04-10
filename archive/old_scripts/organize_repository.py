#!/usr/bin/env python3
"""
Script para organizar arquivos markdown do repositório
Criado: 2025-11-08
Autor: AI Assistant + Dr. Agourakis
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

# Diretório raiz do projeto
ROOT = Path(__file__).parent.parent

# Categorias e padrões de arquivos
CATEGORIES = {
    "docs/session_reports": [
        "SESSION_", "FINAL_SESSION", "DAY1_", "DAY2_", "TONIGHT_", 
        "SESSAO_", "ULTRA_FINAL", "COMPLETE_SESSION", "STATUS_",
        "PROGRESSO_", "HONEST_STATUS", "WEEK1_"
    ],
    "docs/planning": [
        "PLAN", "STRATEGY", "ROADMAP", "CHECKLIST", "NEXT_STEPS",
        "DEPLOYMENT", "EXECUTION", "TIMELINE", "GUIDE"
    ],
    "docs/research_reports": [
        "REPORT", "ANALYSIS", "FINDINGS", "DISCOVERY", "INVESTIGATION",
        "VALIDATION", "COMPARISON", "METHODOLOGICAL", "META_ANALYSIS",
        "DATA_MINING", "EXTRACTION", "ENRICHMENT"
    ],
    "docs/integration": [
        "INTEGRATION", "Q1_", "Q2_", "Q3_", "Q4_", "Q5_", "Q6_",
        "Q7_", "Q8_", "Q9_", "Q10_", "Q11_", "Q12_", "Q13_", "Q14_",
        "MCTS_ITERATION", "ITERATION_", "MCTS_"
    ],
    "docs/literature": [
        "LITERATURE", "CRITICAL_LITERATURE", "GPT5_PRO", "CITATIONS",
        "PAPERS", "PUBMED", "GOLD_PAPERS"
    ],
    "docs/manuscript_versions": [
        "MANUSCRIPT_", "RESPONSE_TO_REVIEWER", "REVISION_PACKAGE",
        "CORRECTION_COMPLETE", "V1.", "V2."
    ],
    "docs/guides": [
        "HOW_TO", "QUICKSTART", "GUIDE", "INSTRUCTIONS", "TUTORIAL",
        "README_FIRST", "START_HERE", "COMO_USAR"
    ],
    "archive": [
        "FINAL_ACCEPTANCE", "FINAL_DECISION", "FINAL_STATUS",
        "REPOSITORY_CLEANUP", "OLD_", "DEPRECATED_"
    ]
}

# Arquivos que devem permanecer na raiz
KEEP_IN_ROOT = {
    "README.md", "CHANGELOG.md", "LICENSE", "CITATION.cff",
    "CHECKLIST_Nature_Submission.md",  # Checklist principal
    "NEXT_STEPS.md"  # Próximos passos atuais
}


def categorize_file(filename: str) -> Tuple[str, bool]:
    """
    Categoriza um arquivo baseado em seu nome.
    Retorna (categoria, deve_mover)
    """
    filename_upper = filename.upper()
    
    # Verifica se deve permanecer na raiz
    if filename in KEEP_IN_ROOT:
        return ("root", False)
    
    # Verifica cada categoria
    for category, patterns in CATEGORIES.items():
        for pattern in patterns:
            if pattern in filename_upper:
                return (category, True)
    
    # Se não se encaixa em nenhuma categoria, vai para archive
    return ("archive", True)


def organize_files(dry_run: bool = False) -> Dict[str, List[str]]:
    """
    Organiza arquivos markdown do repositório.
    """
    root_path = ROOT
    moved_files = {cat: [] for cat in CATEGORIES.keys()}
    moved_files["root"] = []
    moved_files["archive"] = []
    
    # Lista todos os arquivos .md na raiz
    md_files = list(root_path.glob("*.md"))
    
    print(f"Encontrados {len(md_files)} arquivos markdown na raiz")
    print(f"Modo: {'DRY RUN' if dry_run else 'EXECUÇÃO REAL'}\n")
    
    for md_file in md_files:
        category, should_move = categorize_file(md_file.name)
        
        if not should_move:
            moved_files["root"].append(md_file.name)
            print(f"✓ Mantido na raiz: {md_file.name}")
            continue
        
        target_dir = root_path / category
        target_path = target_dir / md_file.name
        
        # Evita sobrescrever se já existe
        if target_path.exists():
            counter = 1
            stem = md_file.stem
            suffix = md_file.suffix
            while target_path.exists():
                target_path = target_dir / f"{stem}_{counter}{suffix}"
                counter += 1
        
        if not dry_run:
            # Cria diretório se não existir
            target_dir.mkdir(parents=True, exist_ok=True)
            # Move arquivo
            shutil.move(str(md_file), str(target_path))
        
        moved_files[category].append(md_file.name)
        print(f"{'[DRY] ' if dry_run else ''}→ {category}/{md_file.name}")
    
    return moved_files


def print_summary(moved_files: Dict[str, List[str]]):
    """Imprime resumo da organização."""
    print("\n" + "="*60)
    print("RESUMO DA ORGANIZAÇÃO")
    print("="*60)
    
    for category, files in moved_files.items():
        if files:
            print(f"\n{category}: {len(files)} arquivos")
            if len(files) <= 5:
                for f in files:
                    print(f"  - {f}")
            else:
                for f in files[:3]:
                    print(f"  - {f}")
                print(f"  ... e mais {len(files) - 3} arquivos")
    
    total_moved = sum(len(files) for cat, files in moved_files.items() if cat != "root")
    print(f"\nTotal movido: {total_moved} arquivos")
    print(f"Total mantido na raiz: {len(moved_files['root'])} arquivos")


if __name__ == "__main__":
    import sys
    
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    
    print("="*60)
    print("ORGANIZAÇÃO DO REPOSITÓRIO")
    print("="*60)
    print()
    
    moved_files = organize_files(dry_run=dry_run)
    print_summary(moved_files)
    
    if dry_run:
        print("\n⚠️  MODO DRY RUN - Nenhum arquivo foi movido")
        print("Execute sem --dry-run para mover os arquivos")

