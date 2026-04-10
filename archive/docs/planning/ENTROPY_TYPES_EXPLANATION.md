# 📊 TIPOS DE ENTROPIA - SHANNON vs. ESPECTRAL

**Date:** 2025-11-06  
**Purpose:** Comparar diferentes medidas de entropia para KEC  
**Principle:** HONESTIDADE ABSOLUTA [[memory:10560840]]

---

## 🎯 **POR QUE TESTAR DIFERENTES ENTROPIAS?**

**Insight:** Cada tipo de entropia captura **aspectos diferentes** da rede!

- **Shannon (transition):** Disorder LOCAL (node-level)
- **Shannon (degree):** Heterogeneidade da distribuição
- **Espectral:** Disorder GLOBAL (estrutura completa)
- **Von Neumann:** Quantum-inspired (híbrido)

**Para pathology detection:**
- ✅ Queremos detectar GLOBAL fragmentation
- ✅ Espectral pode ser mais sensível!
- ✅ Vale testar empiricamente

---

## 📚 **DEFINIÇÕES TÉCNICAS:**

### **1. SHANNON ENTROPY (Transition)** - Original KEC

**Formula:**
```
H_transition = mean_over_nodes( -Σ p_i log(p_i) )

Onde p_i = probabilidade de transição para vizinho i
```

**O que mede:**
- Disorder nas transições de cada nó
- Node-level uncertainty
- **LOCAL property**

**Vantagens:**
- ✅ Captura local connectivity patterns
- ✅ Sensível a degree distribution
- ✅ Interpretável (information theory)

**Limitações:**
- ⚠️ Pode perder estrutura global
- ⚠️ Média sobre nós pode mascarar patterns

---

### **2. SHANNON ENTROPY (Degree Distribution)**

**Formula:**
```
H_degree = -Σ p(k) log(p(k))

Onde p(k) = fração de nós com degree k
```

**O que mede:**
- Heterogeneidade da distribuição de graus
- Quanto a rede é "desigual"
- **GLOBAL property** (distribution-level)

**Vantagens:**
- ✅ Captura heterogeneidade
- ✅ Sensível a hubs vs. periphery
- ✅ Simple, rápido

**Limitações:**
- ⚠️ Não captura clustering
- ⚠️ Não captura connectivity patterns

---

### **3. SPECTRAL ENTROPY** ⭐⭐⭐

**Formula:**
```
H_spectral = -Σ λ_i log(λ_i)

Onde λ_i são autovalores NORMALIZADOS do Laplaciano
```

**O que mede:**
- Disorder na estrutura GLOBAL
- Complexity espectral da rede
- **GLOBAL property** (matrix spectrum)

**Vantagens:**
- ✅ Captura estrutura global completa
- ✅ Sensível a connectivity, clustering, modularity
- ✅ Teória espectral de grafos (rigorosa)
- ✅ Detecta fragmentation (múltiplos componentes = autovalores específicos)

**Limitações:**
- ⚠️ Computacionalmente mais custosa (eigenvalues)
- ⚠️ Menos interpretável intuitivamente

---

### **4. VON NEUMANN ENTROPY**

**Formula:**
```
H_vn = -Tr(ρ log(ρ))

Onde ρ = L / Tr(L) (densidade normalizada)
```

**O que mede:**
- Quantum-inspired graph entropy
- Similar à espectral mas com normalização diferente
- **GLOBAL property**

**Vantagens:**
- ✅ Teoria da informação quântica
- ✅ Bem estudada matematicamente
- ✅ Captura global structure

---

## 🔬 **QUAL USAR PARA PSYCHOPATHOLOGY?**

### **Hypotheses:**

**H1: Spectral > Shannon (transition) para FRAGMENTATION**

**Reasoning:**
- Fragmentation = GLOBAL property (múltiplos componentes)
- Shannon (transition) = LOCAL (node-level)
- Spectral captura global structure melhor
- **Prediction:** ρ(Spectral, Severity) > ρ(Shannon, Severity)

---

**H2: Shannon (degree) detecta HUBS disruption**

**Reasoning:**
- Depression pode afetar distribuição de graus
- Loss of hubs = flatter distribution
- Shannon (degree) sensível a isso
- **Prediction:** ρ(Shannon_degree, Severity) significante

---

**H3: Von Neumann ~ Spectral**

**Reasoning:**
- Ambas baseadas em eigenvalues
- Normalizações diferentes
- Devem correlacionar fortemente
- **Prediction:** Resultados similares

---

## 📊 **EXPECTED RESULTS:**

### **For FEP vs. Control:**

**Shannon (transition):**
- Control: H ≈ 3.5-4.0 (moderate)
- FEP: H ≈ 4.5-5.5 (higher - more uncertainty)
- **Detection:** Moderate

**Spectral:**
- Control: H ≈ 4.0-5.0 (organized)
- FEP: H ≈ 6.0-8.0 (fragmented - distinct eigenvalue spectrum)
- **Detection:** ⭐⭐⭐ BEST (captures fragmentation!)

**Shannon (degree):**
- Control: H ≈ 3.0-4.0
- FEP: H ≈ 3.5-4.5
- **Detection:** Moderate

---

### **For Depression Severity:**

**Best case (Spectral):**
- Minimum: H_spec ≈ 4.5
- Mild: H_spec ≈ 5.5
- Moderate: H_spec ≈ 6.5
- Severe: H_spec ≈ 7.5
- **Correlation:** ρ > 0.80 (strong!)

---

## 🎯 **IMPLICATIONS FOR KEC:**

### **Original KEC (Shannon transition):**
```
KEC = (H_shannon + κ_z - C_z) / 3
```

### **KEC with Spectral Entropy:**
```
KEC_spectral = (H_spectral_z + κ_z - C_z) / 3
```

### **Hybrid KEC (Multi-entropy):**
```
KEC_hybrid = (H_shannon_z + H_spectral_z + κ_z - C_z) / 4
```

**Testing:**
- Which KEC version best correlates with severity?
- Which best discriminates patient vs. control?
- Which has largest effect size?

---

## 🚀 **NEXT STEPS:**

### **NOW (Running):**
- ✅ Compute all 4 entropy types
- ✅ For SWOW networks (baseline)
- ✅ For depression networks
- ✅ Compare correlations with severity

### **AFTER RESULTS:**
1. Identify best entropy for pathology
2. Recompute KEC with optimal entropy
3. Test on FEP data (PMC10031728)
4. Validate cross-disorder

---

## 📁 **FILES:**

- `ENTROPY_TYPES_EXPLANATION.md` - This document
- `code/analysis/entropy_comparison_shannon_vs_spectral.py` - Implementation
- `logs/entropy_comparison.log` - Results
- `results/entropy_comparison_*.{csv,json}` - Data

---

**EXCELENTE PERGUNTA! FAZENDO CIÊNCIA METODOLÓGICA RIGOROSA!** 🔬💪


