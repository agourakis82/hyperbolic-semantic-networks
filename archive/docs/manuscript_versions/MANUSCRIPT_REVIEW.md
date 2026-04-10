# Manuscript Review - Checklist de Revisão

**File**: `manuscript/main.md` (389 linhas)  
**Status**: Draft v1.0, pronto para conversão LaTeX

---

## ESTRUTURA ATUAL

### Abstract (150 palavras) ✅
- Background claro
- Methods: 4 línguas, OR curvature, SWOW
- Results: κ = -0.166 ± 0.042, 100% hyperbolic
- Conclusion: Universal property
- **Status**: Conciso, completo

### Introduction ✅
- 1.1 Background (semantic networks)
- 1.2 Hyperbolic geometry (definição)
- 1.3 Ollivier-Ricci curvature (método)
- 1.4 Research questions (4 RQs claras)
- 1.5 Hypotheses (4 hipóteses testáveis)
- **Status**: Bem estruturada

### Methods ✅
- 2.1 Dataset SWOW
- 2.2 Network construction (500 nodes)
- 2.3 Curvature computation (GraphRicciCurvature)
- 2.4 Scale-free analysis (powerlaw)
- 2.5 Baselines (ER, BA, WS, Lattice)
- 2.6 Robustness (bootstrap, size)
- 2.7 Statistical analysis
- **Status**: Reproduzível, detalhado

### Results ✅
- 3.1 Universal hyperbolic (Table 1: 4 línguas)
- 3.2 Scale-free (Table 2: 3/4 línguas)
- 3.3 Baselines (comparação)
- 3.4 Robustness (CV=10.1%)
- 3.5 Distribution (bimodal/skewed)
- **Status**: Completo, dados claros

### Discussion ✅
- 4.1 Universal geometry (interpretação)
- 4.2 Scale-free link (mecanismo)
- 4.3 ER unexpected result (honesto!)
- 4.4 Robustness (limitations claras)
- 4.5 Cognitive implications
- 4.6 Prior work
- **Status**: Honesto, bem fundamentado

### Conclusion ✅
- Summary dos achados
- Significance statement
- Impact
- Next steps
- **Status**: Conciso, impactante

### References ✅
- 26 referências
- Mix clássicos + recentes
- **Status**: Adequado

---

## PONTOS FORTES

1. ✅ **Claim claro**: "Universal hyperbolic geometry"
2. ✅ **Evidência forte**: 4/4 línguas (100%)
3. ✅ **Robustness**: Bootstrap, network size, baselines
4. ✅ **Honestidade**: ER unexpected, English incomplete, limitations claras
5. ✅ **Reproducible**: Methods detalhados
6. ✅ **Impact**: Cognitive implications explícitas

---

## PONTOS A CONSIDERAR (Para Revisão)

### 1. Abstract - Word Count
**Atual**: "150 palavras" declarado  
**Real**: ~150 palavras (verificar contagem exata)  
**Network Science limit**: Tipicamente 150-200

**Ação**: ✅ OK se ≤200

### 2. Scale-Free - English Missing
**Atual**: English N/A para α (linha 175)  
**Issue**: 3/4 é bom, mas 4/4 seria melhor

**Opção A**: Deixar como está, acknowledge em discussion  
**Opção B**: Computar α para English (se dados disponíveis)

**Recomendação**: Opção A (honesto, 3/4 é forte)

### 3. ER Result - Unexpected
**Atual**: κ = -0.349 (unexpected negative)  
**Treatment**: Reportado honestamente, noted como "unexpected but validated"

**Ação**: ✅ Correto (honestidade é boa)

### 4. References - [15] Missing
**Atual**: "[15] [Future investigation needed]" (linha 342)

**Ação**: 
- **Opção A**: Remover citação [15] do texto (linha 198)
- **Opção B**: Encontrar referência apropriada

**Recomendação**: Opção A (simples)

### 5. Duplicates em References
**Linhas 354, 356**: "duplicate - already cited"

**Ação**: Remover duplicates, renumerar

---

## FIGURES NECESSÁRIAS (Verificar se Existem)

Mencionadas no texto:
- **Figure A**: Curvature distribution (linha 216) ✅ consolidated_analysis
- **Figure D**: Baseline comparison (linha 183) ✅ corrected_baselines
- **Figure F**: Network size sensitivity (linha 207) ✅ robustness_analysis

**Verificar**: Se 7 painéis mencionados existem nas 6 figuras disponíveis

**Figuras disponíveis**:
1. consolidated_analysis_v6.4.png
2. network_science_v6.4_comprehensive.png
3. degree_distribution_powerlaw_v6.4.png
4. corrected_baselines_comparison_v6.4.png
5. robustness_analysis_v6.4.png
6. er_sensitivity_v6.4.png

**Ação**: Mapear painéis para figuras, atualizar text

---

## PRÓXIMAS AÇÕES RECOMENDADAS

### Antes de Converter para LaTeX:

1. **Fix references**:
   - [ ] Remover [15] do texto OU adicionar referência real
   - [ ] Remover duplicates [21], [22]
   - [ ] Renumerar após remoções

2. **Verify figures**:
   - [ ] Mapear painéis para figuras disponíveis
   - [ ] Atualizar captions
   - [ ] Verificar all figures referenced

3. **Abstract**:
   - [ ] Count exact palavras
   - [ ] Verificar Network Science limit

4. **Optional improvements**:
   - [ ] Add English scale-free analysis (if possible)
   - [ ] Expand supplementary materials section
   - [ ] Add author contributions

---

## CONVERSÃO PARA LaTeX

**Template**: Network Science (Cambridge)  
**Download**: https://www.cambridge.org/core/journals/network-science/information/instructions-contributors

**Sections mapping**:
- Markdown sections → LaTeX sections
- Tables → tabular environment
- Figures → includegraphics

**Estimated time**: 2-3 horas

---

## CHECKLIST FINAL PRÉ-SUBMISSION

Manuscript:
- [ ] References completas (sem [15], sem duplicates)
- [ ] Figures todas referenciadas
- [ ] Abstract word count verificado
- [ ] Supplementary materials preparado
- [ ] Converted to LaTeX
- [ ] Compiled sem erros

Metadata:
- [x] Author info correto
- [x] ORCID correto
- [x] Affiliation completa
- [ ] DOI obtido do Zenodo

Repository:
- [x] GitHub repo criado
- [x] Código pushed
- [ ] Zenodo integration ON
- [ ] DOI test successful

---

**Quer que eu corrija algo específico antes do push?**

**Ou está OK e vamos para GitHub agora?**

