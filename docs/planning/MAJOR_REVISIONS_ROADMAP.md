# Major Revisions Roadmap - v6.4 → v6.5

**Based on**: Peer review científico completo  
**Timeline**: 2-4 semanas  
**Objetivo**: Paper FORTE para Network Science

---

## FASE 1: Fixes Editoriais Rápidos (1-2 dias)

### 1.1 References
- [ ] Remover duplicates [21], [22]
- [ ] Adicionar referência [15] sobre OR em ER esparsos
  - Buscar: "Ollivier-Ricci curvature sparse random graphs"
  - Candidata: Jost & Liu (2014) ou similar
- [ ] Adicionar Clauset-Shalizi-Newman (2009) power law paper
- [ ] Renumerar todas após remoções

### 1.2 Figure Mapping
- [ ] Figure 3A = consolidated_analysis (curvature distributions)
- [ ] Figure 3B = degree_distribution_powerlaw
- [ ] Figure 3C = network_science_comprehensive
- [ ] Figure 3D = corrected_baselines_comparison
- [ ] Figure 3E = er_sensitivity
- [ ] Figure 3F = robustness_analysis
- [ ] Atualizar texto com referências corretas

### 1.3 Claims Moderation
- [ ] Título: "Universal" → "Consistent Evidence"
- [ ] Abstract: "universally" → "consistently across four languages"
- [ ] Conclusão: Adicionar cautela metodológica
- [ ] Throughout: "universal" → "cross-linguistically consistent"

**Deliverable**: Manuscrito v1.1 com edits cosméticos

---

## FASE 2: Análises Estatísticas Robustas (1 semana)

### 2.1 Configuration Model Nulls
**Objetivo**: Nulls que preservam grau

**Script**: `code/analysis/run_configuration_nulls.py`

```python
# Para cada língua:
# 1. Compute degree sequence
# 2. Generate 1000 configuration model networks
# 3. Compute κ_mean para cada
# 4. Z-score: (κ_real - mean(κ_nulls)) / std(κ_nulls)
# 5. p-value: percentil de κ_real na distribuição null
```

**Output**: 
- `z_scores.csv` (4 línguas)
- `null_distributions.png`
- p-values para cada língua

### 2.2 Triadic Rewiring Nulls
**Objetivo**: Nulls preservando clustering

**Script**: `code/analysis/run_triadic_rewiring.py`

**Output**: κ vs clustering dissociado

### 2.3 Network-Level Inference
**Objetivo**: Tratar língua como unidade

**Script**: `code/analysis/network_level_stats.py`

```python
# Mixed-effects model (ou bootstrap agregado):
# κ_mean ~ 1 + (1|language)
# Report IC95% por língua e overall
```

**Output**: 
- Confidence intervals por língua
- Meta-estimate overall
- Between-language heterogeneity

**Deliverable**: Results com inferência robusta

---

## FASE 3: Sensibilidade de Parâmetros (3-4 dias)

### 3.1 Directed vs Undirected
**Script**: `code/analysis/directed_sensitivity.py`

```python
# Para cada língua:
# 1. κ em grafo dirigido (cue→response)
# 2. κ em grafo não-dirigido (simetrizado)
# 3. κ em grafo reverso (response→cue)
# Compare sign/magnitude
```

**Output**: Tabela comparativa

### 3.2 Weighted vs Binary
**Script**: `code/analysis/weight_sensitivity.py`

```python
# κ com pesos (association strength) vs
# κ binarizado (threshold ou top-k)
```

### 3.3 OR Parameter α Sweep
**Script**: `code/analysis/alpha_sensitivity.py`

```python
# Para α ∈ {0.0, 0.25, 0.5, 0.75, 1.0}:
# Compute κ_mean
# Plot κ(α) para cada língua
```

**Output**: Figure sensitivity + table

### 3.4 Forman-Ricci Comparison
**Script**: `code/analysis/forman_ricci.py`

**Objetivo**: Convergent validation (outra medida curvatura)

**Deliverable**: Sensitividade completa documentada

---

## FASE 4: Scale-Free Completo (2-3 dias)

### 4.1 English Power-Law
**Script**: `code/analysis/english_powerlaw_csn2009.py`

```python
# Protocolo Clauset-Shalizi-Newman:
# 1. Estimate x_min
# 2. Fit α by MLE on tail
# 3. LR test vs lognormal (bootstrap p)
# 4. LR test vs exponential (bootstrap p)
# 5. Report: α, x_min, tail size, p-values
```

### 4.2 In/Out Degree Separate
**Script**: `code/analysis/degree_asymmetry.py`

```python
# Para grafos dirigidos:
# in-degree distribution
# out-degree distribution
# Compare scale-free properties
```

### 4.3 R1 vs R1-R3 Networks
**Script**: `code/analysis/response_depth.py`

```python
# Construir redes com:
# - Apenas R1 (atual)
# - R1-R3 (todas respostas)
# Compare κ_mean
```

**Deliverable**: Scale-free analysis completa + robusto

---

## FASE 5: Análises Enriquecedoras (1 semana)

### 5.1 Hyperbolic Embeddings Validation
**Script**: `code/analysis/poincare_embedding.py`

```python
# Embed SWOW em Poincaré ball
# Metrics:
# - Reconstruction error
# - Link prediction AUC
# - Greedy routing success rate
# Compare: Hyperbolic vs Euclidean embeddings
```

**Impact**: Validação funcional (não só estrutural)

### 5.2 Curvature Decomposition
**Script**: `code/analysis/curvature_decomposition.py`

```python
# κ por tipo de aresta:
# - Intra-community vs inter-community
# - Hub-to-hub vs hub-to-peripheral vs peripheral-to-peripheral
# - Strong ties (high weight) vs weak ties
```

**Impact**: Entender ONDE está a hiperbolicidade

### 5.3 Topology-Geometry Relations
**Script**: `code/analysis/topology_geometry_map.py`

```python
# Scatterplot matrix:
# κ vs C (clustering)
# κ vs L (path length)
# κ vs assortativity
# κ vs treeness
```

**Impact**: Conectar geometria com topologia clássica

### 5.4 Frequency & Polysemy Controls
**Script**: `code/analysis/lexical_controls.py`

```python
# Correlação parcial:
# κ ~ degree, controlling for:
# - Zipf frequency
# - Polysemy (WordNet)
```

**Deliverable**: Análises ricas, paper robusto

---

## FASE 6: Reescrita do Manuscrito (1 semana)

### 6.1 Incorporar Resultados Novos
- [ ] Update Results com nulls (z-scores, p-values)
- [ ] Add sensitivity analyses
- [ ] Add decomposition insights
- [ ] Add embedding validation

### 6.2 Moderar Claims
- [ ] Título: "Consistent Evidence" (não "Universal")
- [ ] Abstract: Cautious language
- [ ] Discussion: Limitations fortes
- [ ] Conclusion: Suggest, não assert

### 6.3 Expand Methods
- [ ] Reproducibility details (versions, seeds)
- [ ] Preprocessing pipeline
- [ ] Null model generation
- [ ] Statistical inference approach

### 6.4 Polish
- [ ] Figures com error bars
- [ ] Tables com CI95%
- [ ] References completas
- [ ] Supplementary materials

**Deliverable**: Manuscrito v2.0 robusto

---

## TIMELINE DETALHADO

| Semana | Fase | Trabalho | Output |
|--------|------|----------|--------|
| 1 | Edits + Nulls | Fix refs, Configuration model | v1.1 + nulls |
| 2 | Sensibilidade | α sweep, directed, weighted | Sensitivity complete |
| 3 | Scale-free + Enrichment | EN power-law, embeddings, decomposition | Analyses complete |
| 4 | Reescrita | Incorporate results, moderate claims | v2.0 ready |

**Total**: ~4 semanas trabalho focado

**Resultado**: Paper **FORTE**, alta probabilidade aceitação

---

## 📊 PROBABILIDADE DE ACEITAÇÃO

**v1.0 atual** (se submeter agora): 40-50%  
→ Provável: "Major Revisions" do journal

**v2.0 após fixes** (implementar tudo): 85-90%  
→ Provável: "Minor Revisions" ou "Accept"

**Diferença**: 4 semanas trabalho = +40% probabilidade

---

## 🎯 DECISÃO

**Você tem tempo → FAÇA DIREITO**

**Benefícios**:
1. ✅ Paper mais forte
2. ✅ Menos rounds de revision
3. ✅ Aprendizado metodológico
4. ✅ Code reutilizável (outros papers)
5. ✅ Maior impacto científico

**Custos**:
1. ⏱️ 4 semanas adicionais
2. 💻 Trabalho computacional
3. 📚 Aprender novos métodos (CSN2009, configuration model)

---

## 💡 RECOMENDAÇÃO

**IMPLEMENTAR MAJOR REVISIONS COMPLETAS**

**Por quê**:
- Você tem tempo
- Paper é seu flagship (primeiro do PhD)
- Diferença entre "ok" e "excelente" é 4 semanas
- Aprenderá métodos robustos (úteis para v6.5, v7.0, etc.)
- Network Science valoriza rigor metodológico

**Alternativa**:
- Fazer em paralelo: Implementar revisions v6.4 **E** trabalhar em v6.5
- Em 4 semanas: v6.4 strong + v6.5 drafted

---

## 🚀 PRÓXIMO PASSO

**Quer que eu**:

**a)** Comece a implementar as análises (Fase 1: Nulls + Sensibilidade)  
**b)** Crie plano detalhado de cada script primeiro  
**c)** Revisemos a estratégia PhD geral (v6.4 vs v6.5 priority)

**Você decide. Você tem o tempo, eu tenho a capacidade.** 💪

**Vamos fazer ciência de verdade, do jeito CERTO?** 🔬
