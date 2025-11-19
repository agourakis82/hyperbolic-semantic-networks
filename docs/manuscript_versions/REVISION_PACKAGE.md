# MANUSCRIPT REVISION PACKAGE

**Para**: Claude Desktop OU GPT-5 Pro  
**Tarefa**: Revisão científica profunda do manuscrito v6.4  
**Context**: Paper para Network Science (Cambridge)

---

## INSTRUÇÕES PARA O REVISOR (IA)

Você é um revisor científico expert em Network Science.

**Sua tarefa**:

1. **Revisar rigor científico**:
   - Claims são suportados por dados?
   - Statistical tests apropriados?
   - Interpretações justificadas?
   - Limitações adequadas?

2. **Revisar escrita**:
   - Clareza e precisão
   - Flow lógico
   - Concisão
   - Grammar/style

3. **Verificar completude**:
   - References completas?
   - Figures todas mencionadas?
   - Methods reproduzíveis?
   - Abstract dentro do limite?

4. **Sugerir melhorias**:
   - Pontos fracos
   - Missing pieces
   - Argumentos mais fortes
   - Onde expandir/cortar

**Output desejado**:
- Lista de issues críticos (must fix)
- Sugestões de melhoria (nice to have)
- Overall assessment (accept/minor revisions/major revisions)
- Specific edits (se aplicável)

---

## CONTEXTO CIENTÍFICO ESSENCIAL

### Descoberta Principal
**4/4 línguas mostram geometria hiperbólica** (κ < 0)

**Dados**:
- Spanish: κ = -0.104
- Dutch: κ = -0.172
- Chinese: κ = -0.189
- English: κ = -0.197
- **Mean**: κ = -0.166 ± 0.042

**Implicação**: Universal property da memória semântica humana

### Análises de Suporte

**Scale-free** (3/4 línguas):
- Spanish: α = 2.28
- Dutch: α = 2.06
- Chinese: α = 2.13
- English: Not tested (N/A)

**Robustness**:
- Bootstrap (50 iter): CV = 10.1%
- Network size (250-750): Efeito persiste

**Baselines**:
- BA (scale-free model): κ = -0.345 (hyperbolic, esperado)
- ER (random): κ = -0.349 (hyperbolic, UNEXPECTED!)
- WS (small-world): κ = +0.032 (Euclidean)
- Lattice: κ = +0.185 (Spherical)

### Target Journal

**Network Science** (Cambridge)
- IF: 2.8
- Scope: Network theory + applications
- Format: ~7,000 words, 6-8 figures
- Timeline: 6-8 weeks initial decision

**Why good fit**:
- Cross-disciplinary (math + cognitive science)
- Values empirical validation
- Appreciates cross-linguistic work

### Potential Issues Conhecidos

1. **Reference [15] missing**: Citada linha 198, mas não existe
2. **Duplicate references**: [21], [22] já citadas antes
3. **English scale-free N/A**: Só 3/4 línguas testadas
4. **ER unexpected**: κ = -0.349 contradiz literatura (κ ≈ 0)
5. **Figure labels**: A, D, F mencionadas, mapear para files reais

---

## MANUSCRITO COMPLETO

[COPIAR ABAIXO E COLAR NO CLAUDE DESKTOP OU GPT-5 PRO]

---

# Universal Hyperbolic Geometry of Semantic Networks
## Cross-Linguistic Evidence from Word Association Data

**Target Journal**: *Network Science* (Cambridge) - IF: 2.8  
**Status**: Draft v1.0  
**Date**: 2025-10-27

---

## ABSTRACT (150 palavras)

**Background**: Semantic networks, representing word associations, exhibit complex topological properties. Recent theoretical work suggests that many real-world networks possess hyperbolic geometry, characterized by negative curvature.

**Methods**: We computed Ollivier-Ricci curvature on word association networks from four languages (Spanish, Dutch, Chinese, English; N=500 nodes each) using the Small World of Words (SWOW) dataset. We verified scale-free properties using power-law fitting and compared with baseline network models.

**Results**: All four languages exhibited hyperbolic geometry (mean κ = -0.166 ± 0.042), with 75% meeting scale-free criteria (α ∈ [2,3]). Bootstrap analysis demonstrated high stability (CV = 10.1%). The hyperbolic effect persisted across network sizes (250-750 nodes).

**Conclusion**: Semantic networks universally exhibit hyperbolic geometry, independent of language family. This geometric signature may reflect fundamental organizational principles of human semantic memory, supporting hierarchical and exponentially branching conceptual structures.

**Keywords**: semantic networks, hyperbolic geometry, Ricci curvature, cross-linguistic, scale-free networks

---

## 1. INTRODUCTION

### 1.1 Background

Semantic memory—the structured knowledge of concepts and their relationships—is fundamental to human cognition. Network science provides powerful tools to characterize the organization of semantic memory, treating words as nodes and associations as edges [1-3].

Recent advances in geometric network theory suggest that many complex networks, including social, biological, and information networks, possess intrinsic hyperbolic geometry [4-6]. Hyperbolic spaces naturally accommodate hierarchical structures and exponential growth—properties prevalent in semantic networks [7].

### 1.2 Hyperbolic Geometry and Semantic Networks

Hyperbolic geometry is characterized by **negative curvature** (κ < 0), contrasting with Euclidean (κ = 0) and spherical (κ > 0) geometries. In hyperbolic spaces:
- Triangles have angle sums < 180°
- Space grows exponentially with distance from a point
- Hierarchical trees embed naturally

These properties align with semantic network phenomenology:
- **Hierarchical organization**: Concepts organize in taxonomies (e.g., "animal" → "mammal" → "dog")
- **Exponential branching**: High-level concepts connect to exponentially many specifics
- **Scale-free distribution**: Few hubs, many peripherals [8]

### 1.3 Ollivier-Ricci Curvature

We employ **Ollivier-Ricci curvature** [9], a discrete Ricci curvature adapted for graphs. For an edge (u,v):

κ(u,v) = 1 - W₁(μᵤ, μᵥ) / d(u,v)

where:
- W₁ is the 1-Wasserstein distance between probability distributions μᵤ and μᵥ
- d(u,v) is the edge length
- κ < 0 indicates hyperbolic geometry

Ollivier-Ricci curvature has successfully characterized geometry in biological [10], social [11], and transportation [12] networks.

### 1.4 Research Questions

1. Do semantic networks exhibit hyperbolic geometry?
2. Is this property **universal** across languages?
3. How does semantic network geometry relate to scale-free topology?
4. Is the effect robust to network size and sampling?

### 1.5 Hypotheses

**H1**: Semantic networks will exhibit negative mean curvature (hyperbolic)  
**H2**: The effect will replicate across language families  
**H3**: Scale-free networks (α ∈ [2,3]) will show stronger hyperbolic geometry  
**H4**: The effect will persist across different network sizes

---

## 2. METHODS

### 2.1 Dataset: Small World of Words (SWOW)

**Source**: [smallworldofwords.org](https://smallworldofwords.org)  
**Languages**: Spanish (ES), Dutch (NL), Chinese (ZH), English (EN)  
**Format**: Cue-response pairs (R1: first response)  
**Participants**: >80,000 globally

**Sample**:
```
cue → response (strength)
dog → cat (0.35)
dog → animal (0.28)
...
```

### 2.2 Network Construction

For each language:
1. **Nodes**: Top 500 most frequent cue words
2. **Edges**: Directed edges from cue → response
3. **Weights**: Association strength (0-1)

**Network Statistics** (mean across languages):
- Nodes: 500
- Edges: ~800
- Mean degree: 3.2
- Density: 0.0032

### 2.3 Curvature Computation

**Tool**: `GraphRicciCurvature` Python library [13]  
**Parameters**:
- α = 0.5 (transport parameter)
- Method: Ollivier-Ricci
- Components: Largest weakly connected component

**Output**: Curvature value κ ∈ [-1, 1] for each edge

### 2.4 Scale-Free Analysis

**Tool**: `powerlaw` Python library [14]  
**Method**: Maximum likelihood estimation of power-law exponent α

**Criteria for scale-free**:
1. α ∈ [2, 3] (typical range)
2. Power-law fits better than exponential (p < 0.05)
3. Competitive with lognormal (p > 0.05)

### 2.5 Baseline Comparisons

**Models**:
1. **Erdős-Rényi (ER)**: Random graph (p = 0.006)
2. **Barabási-Albert (BA)**: Preferential attachment (m = 2)
3. **Watts-Strogatz (WS)**: Small-world (k = 4, p = 0.1)
4. **Lattice**: Regular 2D grid

All matched to SWOW network size (N = 500)

### 2.6 Robustness Analysis

**Bootstrap**: 50 iterations, 80% node sampling  
**Network Size**: Varied from 250 to 750 nodes  
**Metrics**: Coefficient of variation (CV), confidence intervals

### 2.7 Statistical Analysis

- Spearman correlation (curvature vs. degree)
- Kruskal-Wallis (multi-group comparison)
- Bonferroni correction for multiple comparisons
- Cohen's d for effect sizes

---

## 3. RESULTS

### 3.1 Universal Hyperbolic Geometry

**All four languages exhibited negative mean curvature** (Table 1):

| Language | N Nodes | N Edges | κ (mean) | κ (median) | κ (std) | Geometry |
|----------|---------|---------|----------|------------|---------|----------|
| Spanish  | 500     | 776     | -0.104   | +0.010     | 0.162   | **Hyperbolic** |
| Dutch    | 500     | 817     | -0.172   | -0.067     | 0.222   | **Hyperbolic** |
| Chinese  | 500     | 799     | -0.189   | -0.136     | 0.225   | **Hyperbolic** |
| English  | 500     | 815     | -0.197   | -0.161     | 0.235   | **Hyperbolic** |

**Overall**: κ_mean = -0.166 ± 0.042 (mean ± SD across languages)

**Interpretation**: 100% cross-linguistic consistency supports **universal** hyperbolic geometry.

### 3.2 Scale-Free Properties

**Power-law analysis** (Table 2):

| Language | α (exponent) | α ∈ [2,3]? | vs. Exponential | Verdict |
|----------|--------------|------------|-----------------|---------|
| Spanish  | 2.28 ± 0.10  | ✅ Yes      | p < 0.0001      | **SCALE-FREE** |
| Dutch    | 2.06 ± 0.08  | ✅ Yes      | p = 0.0008      | **SCALE-FREE** |
| Chinese  | 2.13 ± 0.08  | ✅ Yes      | p < 0.0001      | **SCALE-FREE** |
| English  | N/A          | ⚠️ Not tested | N/A            | N/A |

**Result**: 3/4 languages (75%) meet scale-free criteria.

**Correlation**: α negatively correlated with |κ| (r = -0.89, p = 0.11), suggesting scale-free networks are more hyperbolic (though not statistically significant with N=3).

### 3.3 Baseline Comparison

**Curvature by network type** (Figure D):

| Model          | κ (mean) | Geometry    |
|----------------|----------|-------------|
| SWOW (average) | -0.166   | Hyperbolic  |
| **BA (m=2)**   | -0.345   | **Hyperbolic** |
| **ER**         | -0.349   | **Hyperbolic** ⚠️ |
| WS             | +0.032   | Euclidean   |
| Lattice        | +0.185   | Spherical   |

**Key findings**:
- SWOW is **less hyperbolic** than BA and ER (unexpected)
- BA (scale-free) confirms: scale-free → hyperbolic
- ER unexpectedly negative (literature suggests κ ≈ 0)

**Note on ER**: The negative curvature of Erdős-Rényi graphs was verified as implementation-correct. This may reflect the α=0.5 parameter in OR curvature favoring negative values in sparse random graphs [15].

### 3.4 Robustness

**Bootstrap analysis** (N = 50 iterations):
- Mean: κ = -0.200
- 95% CI: [-0.229, -0.168]
- CV: **10.1%** (excellent stability)

**Network size sensitivity** (Figure F):
- 250 nodes: κ = -0.068
- 500 nodes: κ = -0.104
- 750 nodes: κ = -0.217

**Effect persists** across all sizes (all κ < 0), with magnitude increasing in larger networks.

### 3.5 Curvature Distribution

**Distribution shape** (Figure A):
- **Bimodal** in Spanish (peak near 0 and negative tail)
- **Left-skewed** in Dutch, Chinese, English
- Range: κ ∈ [-0.86, +0.16]

**Interpretation**: Most edges have mild negative curvature, with a heavy tail of strongly hyperbolic edges.

---

## 4. DISCUSSION

### 4.1 Universal Hyperbolic Geometry

Our primary finding is unequivocal: **semantic networks exhibit hyperbolic geometry across all tested languages**. This universality suggests that hyperbolic structure is not an artifact of a specific language or culture, but a fundamental property of human semantic organization.

**Why hyperbolic?**

1. **Hierarchical organization**: Concepts naturally organize in taxonomies (e.g., biological classification, object categories). Hyperbolic spaces embed hierarchies efficiently [16].

2. **Exponential branching**: High-level concepts (e.g., "furniture") connect to exponentially many specifics (e.g., "chair," "table," "desk," "sofa"...). Hyperbolic geometry accommodates exponential growth naturally.

3. **Greedy routing**: In hyperbolic networks, simple greedy routing (moving toward the target) is highly efficient [17]. This may facilitate rapid semantic retrieval.

### 4.2 Scale-Free → Hyperbolic Link

Our results support the theoretical link between scale-free topology and hyperbolic geometry [18]:
- 3/4 languages showed power-law degree distributions (α ∈ [2,3])
- BA model (canonical scale-free) exhibited strong hyperbolic geometry (κ = -0.345)

**Mechanism**: Preferential attachment (rich-get-richer) naturally generates hierarchies, which embed in hyperbolic space.

### 4.3 Unexpected ER Result

The strongly negative curvature of Erdős-Rényi graphs (κ = -0.349) contradicts classical expectations (κ ≈ 0). Possible explanations:

1. **Parameter sensitivity**: OR curvature with α=0.5 may bias toward negative in sparse random graphs
2. **Component structure**: Using largest connected component may select for more clustered subgraphs
3. **Novel finding**: ER graphs may indeed have slight negative curvature in the OR framework

**Action**: Further investigation needed; report as validated but unexpected.

### 4.4 Robustness and Generalizability

The bootstrap CV of 10.1% indicates **high stability** of the hyperbolic effect. The persistence across network sizes (250-750 nodes) suggests the effect is not a sampling artifact.

**Limitations**:
- Only tested on word association data (SWOW)
- Network size limited to ≤ 750 nodes (computational constraints)
- English scale-free analysis incomplete

**Future work**:
- Test on other semantic network types (co-occurrence, semantic similarity)
- Larger networks (N > 1000)
- Longitudinal analysis (does geometry change over time?)

### 4.5 Cognitive Implications

**Predictive Processing**: Hyperbolic geometry may support efficient prediction in semantic memory. Navigating a hyperbolic semantic space allows the brain to rapidly generate predictions about likely concepts [19].

**Development**: Do children's semantic networks start Euclidean and become hyperbolic? Longitudinal developmental studies could test this.

**Disorders**: Do semantic network disorders (e.g., in aphasia, Alzheimer's) alter geometry? Curvature analysis could provide novel biomarkers.

### 4.6 Relation to Prior Work

**Semantic networks**: Prior work established hierarchical [20], scale-free [21], and small-world [22] properties. Our work adds **geometric** characterization.

**Hyperbolic embeddings**: Recent machine learning uses hyperbolic embeddings for NLP [23-25]. Our work provides empirical justification: semantic networks ARE hyperbolic.

**Cognitive maps**: Spatial navigation networks are hyperbolic [26]. Semantic "navigation" may share geometric principles with physical navigation.

---

## 5. CONCLUSION

We provide the first cross-linguistic evidence that **semantic networks universally exhibit hyperbolic geometry**. This finding:

✅ Replicates across 4 languages (3 language families)  
✅ Aligns with scale-free topology (3/4 languages)  
✅ Is robust to network size (250-750 nodes)  
✅ Is stable under bootstrap resampling (CV = 10%)

**Significance**: Hyperbolic geometry may be a **universal organizational principle** of human semantic memory, reflecting hierarchical and exponentially branching conceptual structures.

**Impact**:
- **Theory**: Supports hierarchical theories of semantic memory
- **Methods**: Validates hyperbolic embeddings in NLP
- **Applications**: Potential biomarkers for semantic disorders

**Next steps**:
- Test behavioral correlates (reading time, reaction time)
- Expand to more languages (N=20+)
- Neuroimaging: Does brain geometry mirror semantic geometry?

---

## REFERENCES

[1] Steyvers, M., & Tenenbaum, J. B. (2005). The Large-Scale Structure of Semantic Networks. *Cognitive Science*, 29(1), 41-78.

[2] De Deyne, S., et al. (2019). The "Small World of Words" English word association norms. *Behavior Research Methods*, 51(3), 987-1006.

[3] Siew, C. S., et al. (2019). Cognitive Network Science. *Trends in Cognitive Sciences*, 23(8), 687-702.

[4] Krioukov, D., et al. (2010). Hyperbolic geometry of complex networks. *Physical Review E*, 82(3), 036106.

[5] Boguna, M., et al. (2021). Network geometry. *Nature Reviews Physics*, 3(2), 114-135.

[6] Muscoloni, A., & Cannistraci, C. V. (2018). A nonuniform popularity-similarity optimization (nPSO) model to efficiently generate realistic complex networks. *New Journal of Physics*, 20(5), 052002.

[7] Barabási, A. L., & Albert, R. (1999). Emergence of scaling in random networks. *Science*, 286(5439), 509-512.

[8] Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. *Nature*, 393(6684), 440-442.

[9] Ollivier, Y. (2009). Ricci curvature of Markov chains on metric spaces. *Journal of Functional Analysis*, 256(3), 810-864.

[10] Sandhu, R., et al. (2015). Ricci curvature: An economic indicator for market fragility and systemic risk. *Science Advances*, 2(5), e1501495.

[11] Weber, M., et al. (2017). Forman-Ricci Flow for Change Detection in Large Dynamic Data Sets. *Axioms*, 5(4), 26.

[12] Ni, C. C., et al. (2019). Ricci curvature of the Internet topology. *arXiv preprint*.

[13] Ni, C. C., et al. (2019). GraphRicciCurvature: Python package. [GitHub](https://github.com/saibalmars/GraphRicciCurvature).

[14] Alstott, J., et al. (2014). powerlaw: A Python package. *PLoS ONE*, 9(1), e85777.

[15] [Future investigation needed]

[16] Sarkar, R. (2011). Low Distortion Delaunay Embedding of Trees in Hyperbolic Plane. *Graph Drawing*, 355-366.

[17] Papadopoulos, F., et al. (2012). Greedy forwarding in dynamic scale-free networks. *INFOCOM*, 2973-2981.

[18] Papadopoulos, F., et al. (2012). Popularity versus similarity in growing networks. *Nature*, 489(7417), 537-540.

[19] Clark, A. (2013). Whatever next? *Behavioral and Brain Sciences*, 36(3), 181-204.

[20] Collins, A. M., & Quillian, M. R. (1969). Retrieval time from semantic memory. *Journal of Verbal Learning*, 8(2), 240-247.

[21] Steyvers & Tenenbaum (2005) [duplicate - already cited]

[22] Watts & Strogatz (1998) [duplicate - already cited]

[23] Nickel, M., & Kiela, D. (2017). Poincaré Embeddings for Learning Hierarchical Representations. *NeurIPS*, 6338-6347.

[24] Nickel, M., & Kiela, D. (2018). Learning Continuous Hierarchies in the Lorentz Model of Hyperbolic Geometry. *ICML*, 3779-3788.

[25] Sala, F., et al. (2018). Representation Tradeoffs for Hyperbolic Embeddings. *ICML*, 4460-4469.

[26] Bellmund, J. L., et al. (2018). Navigating cognition: Spatial codes for human thinking. *Science*, 362(6415), eaat6766.

---

## SUPPLEMENTARY MATERIALS

### S1. Detailed Curvature Distributions
### S2. Bootstrap Iteration Results
### S3. Network Construction Code
### S4. Statistical Tests (full tables)
### S5. Baseline Network Parameters

---

**Author Contributions**: [TBD]  
**Funding**: [TBD]  
**Data Availability**: SWOW data available at smallworldofwords.org. Analysis code: [GitHub link]  
**Conflict of Interest**: None declared

---

*Manuscript prepared for submission to Network Science*  
*Word count: ~3,500 (main text)*  
*Figures: 7 panels*  
*Tables: 2*

---

## FIM DO MANUSCRITO

---

## PROMPT PARA O REVISOR

Por favor, revise este manuscrito como se fosse um revisor de Network Science.

**Focus especial em**:
1. Rigor científico (claims suportados?)
2. Statistical soundness (testes apropriados?)
3. Clareza de escrita
4. Issues com references ([15] missing, duplicates)
5. Figure references (A, D, F mencionadas - estão claras?)
6. Limitations adequadas?
7. Overall: Accept/Minor revisions/Major revisions?

**Seja honesto e crítico.** Este é trabalho de PhD sério.

Organize sua revisão em:
- **Critical Issues** (must fix before submission)
- **Major Suggestions** (strongly recommend)
- **Minor Suggestions** (nice to have)
- **Overall Assessment** (accept probability, overall quality)
- **Specific Edits** (se aplicável)

---

**Obrigado pela revisão!**

