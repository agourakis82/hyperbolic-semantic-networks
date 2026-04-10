# 🚀 PLANO DE MIGRAÇÃO: Python → Julia/Rust

**Data**: 2025-11-08  
**Status**: Planejamento Inicial  
**Escopo**: Migração completa da codebase (~64 arquivos Python, ~16,516 linhas)

---

## 📊 ANÁLISE DA CODEBASE ATUAL

### Estatísticas
- **Arquivos Python**: 64
- **Linhas de código**: ~16,516
- **Principais módulos**:
  - Curvatura Ollivier-Ricci
  - Preprocessamento de redes
  - Análises estatísticas (bootstrap, null models)
  - Geração de figuras
  - Ricci flow
  - Validação de robustez

### Dependências Críticas
```python
# Bibliotecas principais
- networkx          # Grafos
- numpy             # Computação numérica
- pandas            # Manipulação de dados
- GraphRicciCurvature  # Curvatura Ollivier-Ricci
- scipy             # Estatísticas
- sklearn            # Machine learning
- gudhi              # Topologia persistente
- plotly/matplotlib  # Visualização
```

---

## 🎯 DECISÃO: JULIA vs RUST

### **Recomendação: JULIA** ✅

**Razões:**
1. **Ecossistema científico maduro**: Similar ao Python, mas 10-100x mais rápido
2. **Bibliotecas equivalentes**: LightGraphs.jl, DataFrames.jl, Plots.jl
3. **Curvatura Ollivier-Ricci**: Pode implementar ou usar bibliotecas existentes
4. **Prototipagem rápida**: Mantém produtividade científica
5. **Interoperabilidade**: Pode chamar Python/Rust se necessário
6. **JIT compilation**: Performance próxima de C/Rust para código científico

**Rust seria melhor se:**
- Fosse um sistema de produção crítico
- Precisasse de controle de memória extremo
- Fosse biblioteca de baixo nível
- Mas para análise científica, Julia é mais adequada

---

## 📋 PLANO DE MIGRAÇÃO

### FASE 1: Preparação e Estrutura (1-2 semanas)

#### 1.1 Estrutura de Projeto Julia
```
hyperbolic-semantic-networks/
├── Project.toml              # Dependências Julia
├── Manifest.toml            # Lock de versões
├── README.md
│
├── src/
│   ├── HyperbolicSemanticNetworks.jl  # Módulo principal
│   ├── preprocessing/
│   │   ├── swow.jl
│   │   ├── conceptnet.jl
│   │   └── taxonomies.jl
│   ├── curvature/
│   │   ├── ollivier_ricci.jl
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
├── scripts/
│   ├── run_full_pipeline.jl
│   └── generate_figures.jl
│
└── data/                     # Mantém estrutura atual
```

#### 1.2 Dependências Julia (Project.toml)
```toml
[deps]
# Grafos
LightGraphs = "~1.3"
MetaGraphs = "~0.6"
GraphPlot = "~0.4"

# Dados
DataFrames = "~1.3"
CSV = "~0.10"
JSON = "~0.21"

# Computação numérica
LinearAlgebra = ""
Statistics = ""
Distributions = "~0.25"
Random = ""

# Visualização
Plots = "~1.29"
PlotlyJS = "~0.18"
StatsPlots = "~0.15"

# Otimização/ML
Optim = "~1.6"
Clustering = "~0.14"

# Topologia
# (Implementar ou usar wrapper para gudhi)

# Utilitários
ProgressMeter = "~1.7"
ArgParse = "~2.0"
```

---

### FASE 2: Implementação Core (4-6 semanas)

#### 2.1 Módulo de Preprocessamento
**Prioridade**: ALTA
- [ ] `preprocessing/swow.jl` - Carregar e processar SWOW
- [ ] `preprocessing/conceptnet.jl` - Carregar ConceptNet
- [ ] `preprocessing/taxonomies.jl` - WordNet/BabelNet
- [ ] Testes de equivalência com Python

#### 2.2 Módulo de Curvatura
**Prioridade**: CRÍTICA
- [ ] `curvature/ollivier_ricci.jl` - Implementação Ollivier-Ricci
  - Otimal transport (Sinkhorn)
  - Idleness parameter α
  - Edge curvature computation
- [ ] Validação contra GraphRicciCurvature (Python)
- [ ] Benchmarks de performance

#### 2.3 Módulo de Análise
**Prioridade**: ALTA
- [ ] `analysis/null_models.jl`
  - Configuration model
  - Triadic-rewire
- [ ] `analysis/bootstrap.jl`
  - Bootstrap resampling
  - Confidence intervals
- [ ] `analysis/ricci_flow.jl`
  - Discrete Ricci flow
  - Convergence criteria

#### 2.4 Módulo de Visualização
**Prioridade**: MÉDIA
- [ ] `visualization/figures.jl`
  - Clustering-curvature plots
  - Phase diagrams
  - Null model comparisons
- [ ] `visualization/phase_diagram.jl`

---

### FASE 3: Validação e Testes (2-3 semanas)

#### 3.1 Testes de Equivalência
- [ ] Comparar resultados com Python (mesmos dados)
- [ ] Verificar métricas (κ, C, σ_k)
- [ ] Validar figuras (mesma aparência)

#### 3.2 Benchmarks de Performance
- [ ] Tempo de execução vs Python
- [ ] Uso de memória
- [ ] Escalabilidade (250-1000 nós)

#### 3.3 Testes Unitários
- [ ] Cobertura > 80%
- [ ] Testes de edge cases
- [ ] Validação de inputs

---

### FASE 4: Documentação e Integração (1-2 semanas)

#### 4.1 Documentação
- [ ] README atualizado
- [ ] Documentação inline (DocStrings)
- [ ] Exemplos de uso
- [ ] Guia de migração

#### 4.2 Integração com Pipeline
- [ ] Scripts de reprodução
- [ ] CI/CD (GitHub Actions)
- [ ] Docker container (opcional)

---

## 🔧 IMPLEMENTAÇÃO: Módulos Críticos

### 1. Ollivier-Ricci Curvature (Julia)

```julia
# src/curvature/ollivier_ricci.jl
module OllivierRicci

using LightGraphs
using LinearAlgebra
using SparseArrays
using Optim

"""
Compute Ollivier-Ricci curvature for an edge (u, v).

κ(u,v) = 1 - W₁(μ_u, μ_v) / d(u,v)

where:
- μ_u = α·δ_u + (1-α)·Σ(w_uz / Σw_uz')·δ_z
- W₁ is Wasserstein-1 distance (optimal transport)
- α is idleness parameter (default 0.5)
"""
function compute_edge_curvature(
    G::AbstractGraph,
    u::Int,
    v::Int,
    α::Float64 = 0.5,
    weights::Dict{Tuple{Int,Int},Float64} = Dict()
)::Float64
    # 1. Build probability measures μ_u, μ_v
    μ_u = build_probability_measure(G, u, α, weights)
    μ_v = build_probability_measure(G, v, α, weights)
    
    # 2. Compute Wasserstein-1 distance
    W1 = wasserstein1_distance(G, μ_u, μ_v, weights)
    
    # 3. Edge distance
    d_uv = has_edge(G, u, v) ? get_weight(G, u, v, weights) : 1.0
    
    # 4. Curvature
    κ = 1.0 - W1 / d_uv
    return κ
end

"""
Build probability measure for node u.

μ_u = α·δ_u + (1-α)·Σ(w_uz / Σw_uz')·δ_z
"""
function build_probability_measure(
    G::AbstractGraph,
    u::Int,
    α::Float64,
    weights::Dict{Tuple{Int,Int},Float64}
)::Dict{Int,Float64}
    μ = Dict{Int,Float64}()
    
    # Idleness component
    μ[u] = α
    
    # Neighbor component
    neighbors = neighbors(G, u)
    if length(neighbors) > 0
        total_weight = sum(get_weight(G, u, z, weights) for z in neighbors)
        if total_weight > 0
            for z in neighbors
                w_uz = get_weight(G, u, z, weights)
                μ[z] = (1 - α) * w_uz / total_weight
            end
        end
    end
    
    return μ
end

"""
Compute Wasserstein-1 distance using Sinkhorn algorithm.
"""
function wasserstein1_distance(
    G::AbstractGraph,
    μ::Dict{Int,Float64},
    ν::Dict{Int,Float64},
    weights::Dict{Tuple{Int,Int},Float64},
    ε::Float64 = 0.01,
    max_iter::Int = 100
)::Float64
    # Sinkhorn algorithm implementation
    # (Simplified - full implementation needed)
    # ...
end

"""
Compute curvature for all edges in graph.
"""
function compute_graph_curvature(
    G::AbstractGraph,
    α::Float64 = 0.5,
    weights::Dict{Tuple{Int,Int},Float64} = Dict()
)::Dict{Tuple{Int,Int},Float64}
    curvatures = Dict{Tuple{Int,Int},Float64}()
    
    for edge in edges(G)
        u, v = src(edge), dst(edge)
        κ = compute_edge_curvature(G, u, v, α, weights)
        curvatures[(u, v)] = κ
    end
    
    return curvatures
end

end # module
```

### 2. Null Models (Julia)

```julia
# src/analysis/null_models.jl
module NullModels

using LightGraphs
using Random
using Statistics

"""
Configuration model: preserve degree sequence, randomize edges.
"""
function configuration_model(
    G::AbstractGraph,
    n_samples::Int = 1000
)::Vector{AbstractGraph}
    degrees = degree(G)
    samples = Vector{AbstractGraph}()
    
    for _ in 1:n_samples
        G_null = sample_configuration_model(degrees)
        push!(samples, G_null)
    end
    
    return samples
end

"""
Triadic-rewire: preserve triangle counts, randomize other edges.
"""
function triadic_rewire(
    G::AbstractGraph,
    n_samples::Int = 1000
)::Vector{AbstractGraph}
    triangles = count_triangles(G)
    samples = Vector{AbstractGraph}()
    
    for _ in 1:n_samples
        G_null = sample_triadic_rewire(G, triangles)
        push!(samples, G_null)
    end
    
    return samples
end

end # module
```

---

## 📈 BENEFÍCIOS ESPERADOS

### Performance
- **10-100x mais rápido** que Python para computação numérica
- **Menor uso de memória** (tipagem estática)
- **Paralelização nativa** (Threads.jl, Distributed.jl)

### Qualidade de Código
- **Type safety** (menos bugs)
- **Múltiplo dispatch** (código mais limpo)
- **Package manager** robusto (Pkg.jl)

### Reprodutibilidade
- **Manifest.toml** locka todas as versões
- **Ambiente isolado** por projeto
- **CI/CD** mais confiável

---

## ⚠️  RISCOS E MITIGAÇÕES

### Risco 1: Biblioteca de Curvatura
**Problema**: GraphRicciCurvature não existe em Julia  
**Mitigação**: 
- Implementar Ollivier-Ricci do zero
- Validar contra Python
- Benchmarks de correção

### Risco 2: Tempo de Migração
**Problema**: 4-6 semanas pode atrasar submissão  
**Mitigação**:
- Manter Python funcionando em paralelo
- Migração incremental (módulo por módulo)
- Priorizar módulos críticos

### Risco 3: Curva de Aprendizado
**Problema**: Julia tem sintaxe diferente  
**Mitigação**:
- Documentação extensa
- Exemplos de migração
- Pair programming se necessário

---

## 🎯 PRÓXIMOS PASSOS IMEDIATOS

1. **Decisão Final**: Julia ou Rust? (Recomendação: Julia)
2. **Setup Inicial**:
   ```bash
   # Instalar Julia
   # Criar projeto
   julia --project=. -e 'using Pkg; Pkg.activate(".")'
   ```
3. **Protótipo**: Implementar Ollivier-Ricci básico
4. **Validação**: Comparar com Python (mesmos dados)
5. **Planejamento**: Timeline detalhado

---

## 📚 RECURSOS

### Julia
- [Julia Documentation](https://docs.julialang.org/)
- [LightGraphs.jl](https://github.com/JuliaGraphs/LightGraphs.jl)
- [DataFrames.jl](https://dataframes.juliadata.org/)
- [Plots.jl](http://docs.juliaplots.org/)

### Migração
- [From Python to Julia](https://docs.julialang.org/en/v1/manual/noteworthy-differences/)
- [Julia for Data Science](https://juliahpc.github.io/JuliaHPC_tutorial/)

---

**Status**: Planejamento completo  
**Próxima ação**: Decisão final (Julia vs Rust) e setup inicial

