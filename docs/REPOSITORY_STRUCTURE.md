# 📁 Estrutura do Repositório

**Última atualização**: 2025-11-08  
**Versão**: v2.0

---

## 🎯 Visão Geral

Este repositório segue uma estrutura limpa e profissional, adequada para publicação científica de alto nível.

```
hyperbolic-semantic-networks/
├── README.md                    # Visão geral do projeto
├── CHANGELOG.md                 # Histórico de versões
├── LICENSE                      # Licença (CC BY 4.0)
├── CITATION.cff                 # Metadados de citação
├── .zenodo.json                 # Configuração Zenodo
├── CHECKLIST_Nature_Submission.md  # Checklist de submissão
│
├── code/                        # Código de análise
│   ├── analysis/                # Scripts de análise Python
│   └── figures/                 # Scripts de geração de figuras
│
├── data/                        # Dados
│   ├── raw/                     # Dados brutos (instruções de download)
│   └── processed/               # Dados processados
│
├── manuscript/                  # Manuscrito principal
│   ├── main.md                  # Manuscrito completo
│   ├── figures/                 # Figuras de publicação (300 DPI)
│   └── references.bib          # Referências bibliográficas
│
├── results/                     # Resultados computados
│   ├── curvature/               # Métricas de curvatura
│   ├── null_models/             # Resultados de modelos nulos
│   └── phase_diagram/           # Diagrama de fase
│
├── figures/                     # Figuras geradas
│
├── submission/                  # Materiais de submissão
│   ├── cover_letter.md          # Carta de apresentação
│   ├── *.pdf                    # PDFs de resposta a revisores
│   └── *.zip                    # Pacotes de submissão
│
├── supplementary/              # Materiais suplementares
│
├── docs/                        # Documentação organizada
│   ├── INDEX.md                 # Índice mestre
│   ├── session_reports/         # Relatórios de sessões (24 arquivos)
│   ├── planning/                # Planos e estratégias (38 arquivos)
│   ├── research_reports/        # Relatórios de pesquisa (34 arquivos)
│   ├── integration/             # Planos de integração (10 arquivos)
│   ├── literature/              # Achados da literatura (6 arquivos)
│   ├── manuscript_versions/     # Versões do manuscrito (16 arquivos)
│   └── guides/                  # Guias de uso (4 arquivos)
│
├── config/                      # Arquivos de configuração
│   ├── babelnet_conf.yml        # Configuração BabelNet
│   └── kubernetes_nulls_job.yaml # Job Kubernetes
│
├── scripts/                     # Scripts utilitários
│   ├── organize_repository.py   # Organização de arquivos
│   └── cleanup_repository.py    # Limpeza do repositório
│
├── archive/                     # Arquivos arquivados (31 arquivos)
│
├── k8s/                         # Configurações Kubernetes
├── logs/                        # Logs de execução
├── tools/                       # Ferramentas auxiliares
│
└── .github/                     # GitHub Actions
    └── workflows/                # CI/CD pipelines
```

---

## 📋 Arquivos na Raiz

Apenas arquivos essenciais permanecem na raiz:

- ✅ `README.md` - Documentação principal
- ✅ `CHANGELOG.md` - Histórico de versões
- ✅ `LICENSE` - Licença do projeto
- ✅ `CITATION.cff` - Metadados de citação
- ✅ `.zenodo.json` - Configuração Zenodo
- ✅ `CHECKLIST_Nature_Submission.md` - Checklist de submissão
- ✅ `NEXT_STEPS.md` - Próximos passos

---

## 📚 Documentação

Toda a documentação está organizada em `docs/`:

- **`docs/INDEX.md`** - Índice mestre com navegação completa
- **`docs/session_reports/`** - Relatórios de sessões de trabalho
- **`docs/planning/`** - Planos, estratégias e checklists
- **`docs/research_reports/`** - Relatórios de pesquisa e análises
- **`docs/integration/`** - Planos de integração e iterações
- **`docs/literature/`** - Achados da literatura e revisões
- **`docs/manuscript_versions/`** - Versões do manuscrito
- **`docs/guides/`** - Guias de uso e quickstarts

---

## 🔧 Scripts de Manutenção

### Organizar arquivos markdown

```bash
python3 scripts/organize_repository.py
```

### Limpar e reorganizar repositório

```bash
python3 scripts/cleanup_repository.py
```

### Modo dry-run (ver sem executar)

```bash
python3 scripts/organize_repository.py --dry-run
python3 scripts/cleanup_repository.py --dry-run
```

---

## 📊 Estatísticas

- **Total de arquivos organizados**: 160+ arquivos markdown
- **Arquivos na raiz**: 7 (apenas essenciais)
- **Categorias de documentação**: 8
- **Estrutura**: Limpa e profissional

---

## ✅ Princípios de Organização

1. **Raiz limpa**: Apenas arquivos essenciais
2. **Categorização clara**: Cada tipo de arquivo em sua pasta
3. **Documentação centralizada**: Tudo em `docs/` com índice
4. **Configurações separadas**: Arquivos de config em `config/`
5. **Scripts utilitários**: Em `scripts/`
6. **Arquivos temporários**: Em `archive/`

---

**Última atualização**: 2025-11-08

