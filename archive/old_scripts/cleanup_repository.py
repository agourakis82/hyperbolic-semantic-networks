#!/usr/bin/env python3
"""
Script para limpeza completa e reorganização do repositório
Criado: 2025-11-08
Autor: AI Assistant + Dr. Agourakis
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).parent.parent

# Arquivos que devem permanecer na raiz
ESSENTIAL_FILES = {
    "README.md", "CHANGELOG.md", "LICENSE", "CITATION.cff", 
    ".zenodo.json", ".gitignore", ".cursorrules"
}

# Estrutura de organização
ORGANIZATION = {
    "config/": [
        "*.yml", "*.yaml", "*.conf", "*.cfg", "*.ini",
        "babelnet_conf.yml", "kubernetes_nulls_job.yaml"
    ],
    "scripts/": [
        "*.sh", "COMANDOS_RAPIDOS.sh"
    ],
    "submission/": [
        "*.pdf", "*.zip", "RESPONSE_TO_REVIEWERS.pdf",
        "RESPONSE_TO_REVIEWER_CORRECTED.pdf",
        "hyperbolic-semantic-networks-v1.8.12-submission.zip"
    ],
    "k8s/": [
        "kubernetes_nulls_job.yaml"
    ],
    "archive/": [
        "zenodo-release-v1.8.12"
    ]
}


def organize_root_files(dry_run: bool = False):
    """Organiza arquivos da raiz para pastas apropriadas."""
    root_files = list(ROOT.glob("*"))
    moved = []
    
    print("="*60)
    print("LIMPEZA E REORGANIZAÇÃO DO REPOSITÓRIO")
    print("="*60)
    print(f"Modo: {'DRY RUN' if dry_run else 'EXECUÇÃO REAL'}\n")
    
    for file_path in root_files:
        if file_path.is_dir():
            # Pastas que devem permanecer
            if file_path.name in [".git", ".github", "code", "data", "docs", 
                                  "figures", "manuscript", "results", "scripts",
                                  "submission", "supplementary", "tools", "archive",
                                  "k8s", "logs", "config"]:
                continue
            
            # Mover pastas temporárias/obsoletas
            if file_path.name.startswith("zenodo-release"):
                target = ROOT / "archive" / file_path.name
                if not dry_run:
                    target.parent.mkdir(exist_ok=True)
                    if target.exists():
                        shutil.rmtree(target)
                    shutil.move(str(file_path), str(target))
                moved.append(("archive", file_path.name))
                print(f"{'[DRY] ' if dry_run else ''}→ archive/{file_path.name}/")
            continue
        
        # Arquivos
        filename = file_path.name
        
        # Manter arquivos essenciais
        if filename in ESSENTIAL_FILES or filename.startswith("."):
            continue
        
        # Organizar por tipo
        moved_file = False
        
        # PDFs → submission/
        if filename.endswith(".pdf"):
            target = ROOT / "submission" / filename
            if not dry_run:
                target.parent.mkdir(exist_ok=True)
                shutil.move(str(file_path), str(target))
            moved.append(("submission", filename))
            print(f"{'[DRY] ' if dry_run else ''}→ submission/{filename}")
            moved_file = True
        
        # ZIPs → submission/
        elif filename.endswith(".zip"):
            target = ROOT / "submission" / filename
            if not dry_run:
                target.parent.mkdir(exist_ok=True)
                shutil.move(str(file_path), str(target))
            moved.append(("submission", filename))
            print(f"{'[DRY] ' if dry_run else ''}→ submission/{filename}")
            moved_file = True
        
        # Scripts shell → scripts/
        elif filename.endswith(".sh"):
            target = ROOT / "scripts" / filename
            if not dry_run:
                target.parent.mkdir(exist_ok=True)
                shutil.move(str(file_path), str(target))
            moved.append(("scripts", filename))
            print(f"{'[DRY] ' if dry_run else ''}→ scripts/{filename}")
            moved_file = True
        
        # Configs → config/
        elif filename.endswith((".yml", ".yaml", ".conf", ".cfg", ".ini")):
            target = ROOT / "config" / filename
            if not dry_run:
                target.parent.mkdir(exist_ok=True)
                shutil.move(str(file_path), str(target))
            moved.append(("config", filename))
            print(f"{'[DRY] ' if dry_run else ''}→ config/{filename}")
            moved_file = True
        
        # Markdowns que não são essenciais
        elif filename.endswith(".md") and filename not in ESSENTIAL_FILES:
            # Já foram organizados pelo script anterior
            continue
        
        if not moved_file and filename not in ESSENTIAL_FILES:
            print(f"⚠️  Não categorizado: {filename}")
    
    print(f"\n{'[DRY] ' if dry_run else ''}Total movido: {len(moved)} arquivos/pastas")
    return moved


def consolidate_docs_structure(dry_run: bool = False):
    """Consolida estrutura de docs/ removendo subpastas desnecessárias."""
    docs_path = ROOT / "docs"
    
    # Subpastas que devem ser mantidas
    keep_subdirs = {
        "session_reports", "planning", "research_reports", 
        "integration", "literature", "manuscript_versions", "guides"
    }
    
    # Mover conteúdo de subpastas confusas
    if (docs_path / "reports").exists():
        reports_path = docs_path / "reports"
        for subdir in reports_path.iterdir():
            if subdir.is_dir():
                # Mover para categoria apropriada
                if "research" in subdir.name.lower():
                    target = docs_path / "research_reports" / subdir.name
                elif "session" in subdir.name.lower():
                    target = docs_path / "session_reports" / subdir.name
                elif "investigation" in subdir.name.lower():
                    target = docs_path / "research_reports" / subdir.name
                else:
                    target = docs_path / "research_reports" / subdir.name
                
                if not dry_run:
                    target.parent.mkdir(exist_ok=True)
                    if target.exists():
                        shutil.rmtree(target)
                    shutil.move(str(subdir), str(target))
                print(f"{'[DRY] ' if dry_run else ''}→ docs/research_reports/{subdir.name}/")
    
    # Limpar subpastas vazias
    if not dry_run:
        for subdir in docs_path.iterdir():
            if subdir.is_dir() and subdir.name not in keep_subdirs:
                try:
                    if not any(subdir.iterdir()):
                        subdir.rmdir()
                        print(f"✓ Removida pasta vazia: docs/{subdir.name}/")
                except:
                    pass


if __name__ == "__main__":
    import sys
    
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    
    moved = organize_root_files(dry_run=dry_run)
    consolidate_docs_structure(dry_run=dry_run)
    
    if dry_run:
        print("\n⚠️  MODO DRY RUN - Nenhum arquivo foi movido")
        print("Execute sem --dry-run para aplicar as mudanças")

