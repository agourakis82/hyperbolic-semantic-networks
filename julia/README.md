# Hyperbolic Semantic Networks - Julia Implementation

## 🚀 Status: EM MIGRAÇÃO (Python → Julia)

**Data**: 2025-11-08  
**Versão**: 0.1.0 (Inicial)

---

## 📋 Visão Geral

Esta é a implementação Julia da análise de geometria hiperbólica em redes semânticas. A migração de Python para Julia visa:

- **Performance**: 10-100x mais rápido para computação numérica
- **Type Safety**: Menos bugs, código mais robusto
- **Reprodutibilidade**: Manifest.toml locka todas as versões
- **Paralelização**: Threads nativas, Distributed.jl

---

## 🏗️ Estrutura

```
julia/
├── Project.toml          # Dependências
├── Manifest.toml         # Lock de versões (gerado)
├── README.md             # Este arquivo
│
├── src/
│   ├── HyperbolicSemanticNetworks.jl  # Módulo principal
│   ├── preprocessing/
│   │   ├── swow.jl
│   │   ├── conceptnet.jl
│   │   └── taxonomies.jl
│   ├── curvature/
│   │   ├── ollivier_ricci.jl  ✅ Implementado
│   │   └── forman.jl
│   ├── analysis/
│   │   ├── null_models.jl
│   │   ├── bootstrap.jl
│   │   └── ricci_flow.jl
│   ├── visualization/
│   │   ├── figures.jl
│   │   └── phase_diagram.jl
│   └── utils/
│       ├── metrics.jl
│       └── io.jl
│
├── test/
│   ├── test_preprocessing.jl
│   ├── test_curvature.jl
│   └── test_analysis.jl
│
└── scripts/
    ├── run_full_pipeline.jl
    └── generate_figures.jl
```

---

## 🚀 Setup

### 1. Instalar Julia
```bash
# Ubuntu/Debian
sudo apt install julia

# Ou baixar de: https://julialang.org/downloads/
```

### 2. Ativar Projeto
```julia
julia --project=.

# No REPL:
using Pkg
Pkg.activate(".")
Pkg.instantiate()  # Instala todas as dependências
```

### 3. Testar
```julia
using HyperbolicSemanticNetworks
# ...
```

---

## 📊 Progresso da Migração

### ✅ Completo
- [x] Estrutura de projeto criada
- [x] Project.toml com dependências
- [x] Módulo básico de curvatura Ollivier-Ricci

### 🚧 Em Progresso
- [ ] Preprocessamento (SWOW, ConceptNet, taxonomias)
- [ ] Validação de curvatura (comparar com Python)
- [ ] Null models (configuration, triadic-rewire)
- [ ] Bootstrap e análise estatística
- [ ] Ricci flow
- [ ] Visualização

### 📋 Planejado
- [ ] Testes unitários
- [ ] Benchmarks de performance
- [ ] Documentação completa
- [ ] Scripts de reprodução

---

## 🔧 Dependências Principais

- **LightGraphs.jl** - Grafos
- **DataFrames.jl** - Manipulação de dados
- **Plots.jl** - Visualização
- **Statistics.jl** - Estatísticas
- **Optim.jl** - Otimização (para Sinkhorn)

---

## 📚 Recursos

- [Julia Documentation](https://docs.julialang.org/)
- [LightGraphs.jl](https://github.com/JuliaGraphs/LightGraphs.jl)
- [Plano de Migração](../docs/planning/MIGRATION_PLAN_JULIA_RUST.md)

---

## ⚠️  Notas

- Esta é uma migração em progresso
- Código Python original permanece em `code/analysis/`
- Validação contínua contra resultados Python
- Performance esperada: 10-100x mais rápido

---

**Última atualização**: 2025-11-08
