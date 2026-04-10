#!/usr/bin/env python3
"""
Script para gerar PDF do manuscrito
Alternativas se Pandoc falhar:
1. Usar pandoc com opções simplificadas
2. Converter Markdown → HTML → PDF (via weasyprint)
3. Usar LaTeX diretamente
"""

import subprocess
from pathlib import Path

manuscript = Path('manuscript/main.md')
output = Path('submission/nature-communications-v2.0-final/manuscript/main.pdf')

# Tentativa 1: Pandoc simples (sem citeproc)
print("Tentativa 1: Pandoc simples...")
try:
    cmd = [
        'pandoc',
        str(manuscript),
        '-o', str(output),
        '--pdf-engine=pdflatex',
        '-V', 'geometry:margin=1in',
        '-V', 'fontsize=11pt',
    ]
    subprocess.run(cmd, check=True, timeout=120)
    print(f"✅ PDF gerado: {output}")
except Exception as e:
    print(f"❌ Erro: {e}")
    print("\n💡 Alternativas:")
    print("   1. Instalar pandoc mais recente: sudo apt install pandoc")
    print("   2. Usar conversão online: https://www.markdowntopdf.com/")
    print("   3. Usar LaTeX diretamente (criar .tex manualmente)")
