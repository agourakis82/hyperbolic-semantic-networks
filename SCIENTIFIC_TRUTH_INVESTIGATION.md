# 🔬 INVESTIGAÇÃO CIENTÍFICA COMPLETA - Sem Atalhos
**Princípio:** Descobrir a VERDADE, não publicar rápido  
**Método:** Systematic hypothesis testing até causa raiz  
**Timeline:** O que for necessário

---

## 🎯 PERGUNTA CENTRAL

**Por que configuration null tem κ = -0.24 (mais hyperbolic) quando real tem κ = -0.07?**

**Hipóteses a testar sistematicamente:**

### **H1: Clustering Effect**
- Real network: C = 0.166 (semantic clusters)
- Config null: C ≈ 0.001 (randomized)
- **Hypothesis:** High clustering → LESS hyperbolic (more spherical locally)
- **Test:** Compute κ vs. C correlation

### **H2: Degree Heterogeneity**
- Configuration model may amplify degree effects
- Hub nodes in random topology → extreme divergence
- **Test:** Compare degree distributions real vs. null

### **H3: Connected Component Size**
- Real: 422 nodes LCC (from 443)
- Null: varies per realization
- **Test:** Does LCC size affect curvature?

### **H4: Weight Distribution Effect**
- Real: Specific weight pattern from semantics
- Null: Random shuffle
- **Already tested:** Persists in unweighted → NOT the cause

### **H5: Literature Precedent**
- Maybe this IS expected behavior?
- Config models in other domains?
- **Test:** Deep literature review

---

## 🔍 PLANNED TESTS (Sequential)


