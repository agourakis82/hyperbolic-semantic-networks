# 🔥 RICCI FLOW - DEPLOYMENT PLAN (REAL!)

**Data:** 2025-11-05  
**Status:** ✅ READY TO DEPLOY  
**Tempo Estimado:** 12-24 horas (execução paralela no cluster)

---

## 🎯 **OBJETIVO:**

Testar se **redes semânticas estão em equilíbrio de Ricci flow** usando implementação REAL (não simplificada):

> Se networks estão em equilíbrio → **Language evolution = Geometric optimization**  
> → **NATURE-TIER FINDING!**

---

## 📦 **ARQUIVOS CRIADOS:**

### **1. Script Python REAL:**
`code/analysis/ricci_flow_real.py`
- ✅ Usa `GraphRicciCurvature.OllivierRicci.compute_ricci_flow()`
- ✅ Full Wasserstein distance computation
- ✅ 200 iterations, η=0.5, α=0.5
- ✅ Convergence detection (ΔC < 0.0001, Δκ < 0.001)
- ✅ Trajectory tracking (metrics at each step)
- ✅ Configuration null generation
- ✅ JSON output com todos resultados

### **2. Kubernetes Deployment:**
`k8s/ricci-flow-deployment.yaml`
- ✅ 6 Jobs (3 languages × 2 types)
- ✅ Node selectors corretos (Maria/T560 + Dell 5860)
- ✅ Resource limits (16-32Gi RAM, 4-8 CPUs)
- ✅ hostPath volumes para workspace
- ✅ Namespace: hyperbolic-semantic

### **3. Deploy Script:**
`scripts/deploy_ricci_flow_cluster.sh`
- ✅ Verifica cluster connectivity
- ✅ Cria namespace
- ✅ Deploy all 6 jobs
- ✅ Mostra status e monitoring commands

### **4. Monitor Script:**
`scripts/monitor_ricci_flow.sh`
- ✅ Real-time dashboard (auto-refresh 30s)
- ✅ Job status, pod status, results
- ✅ Ctrl+C para sair

---

## 🏗️ **DISTRIBUIÇÃO NO CLUSTER:**

### **T560 "Maria" (L4 24GB):**
- Job 1: Spanish Real
- Job 2: Spanish Config
- Job 5: Chinese Real

**Total:** 3 jobs simultâneos  
**RAM:** 48Gi (16Gi × 3)  
**CPU:** 12 cores (4 × 3)

### **Dell 5860 (RTX 4000 20GB):**
- Job 3: English Real
- Job 4: English Config
- Job 6: Chinese Config

**Total:** 3 jobs simultâneos  
**RAM:** 48Gi (16Gi × 3)  
**CPU:** 12 cores (4 × 3)

**Ambos os nós têm RAM e CPU suficientes!** ✅

---

## ⏱️ **TEMPO ESTIMADO:**

### **Por Network:**
- Nodes: ~400-500
- Edges: ~600-800
- OR Curvature computation: ~5-10 min/iteration
- 200 iterations: **~16-33 horas por job**

### **Com Convergence Early Stopping:**
- Se convergir em 50 steps: ~4-8 horas
- Se convergir em 100 steps: ~8-16 horas
- **Estimativa realista:** 8-12 horas por job

### **Wallclock Time (Paralelo):**
- 6 jobs rodando simultaneamente
- **Total:** 12-18 horas (tudo completo!)

---

## 🚀 **COMO EXECUTAR:**

### **1. Preparação (AGORA):**
```bash
cd /home/agourakis82/workspace/hyperbolic-semantic-networks

# Verificar cluster
kubectl get nodes

# Verificar workspace path existe
ls -la /home/agourakis82/workspace/hyperbolic-semantic-networks/data/processed/
```

### **2. Deploy (1 comando!):**
```bash
./scripts/deploy_ricci_flow_cluster.sh
```

### **3. Monitorar (em outra janela):**
```bash
./scripts/monitor_ricci_flow.sh
```

### **4. Logs Individuais:**
```bash
# Spanish real
kubectl logs -f job/ricci-flow-spanish-real -n hyperbolic-semantic

# English real
kubectl logs -f job/ricci-flow-english-real -n hyperbolic-semantic

# Chinese real
kubectl logs -f job/ricci-flow-chinese-real -n hyperbolic-semantic
```

---

## 📊 **O QUE ESPERAR:**

### **Hipótese A: Equilibrium (NATURE-TIER!)**
```
Real networks:
  ΔC < 0.02, Δκ < 0.05
  → Networks already at optimal geometry
  → Language evolution = Ricci flow optimization

Config nulls:
  ΔC > 0.10, Δκ > 0.10
  → Nulls FAR from equilibrium
  → Flow converges TOWARD real network geometry
```

### **Hipótese B: Near Equilibrium (HIGH IMPACT)**
```
Real networks:
  ΔC < 0.05, Δκ < 0.10
  → Networks approximate optimal geometry
  → Evolutionary pressure toward optimization

Config nulls:
  ΔC > 0.15, Δκ > 0.15
  → Strong convergence toward clustered state
```

### **Hipótese C: Not Equilibrium (Still Interesting)**
```
Real networks:
  ΔC > 0.10, Δκ > 0.15
  → Networks evolving toward different geometry
  → Discover optimal semantic network structure
```

**Qualquer resultado é publicável!**

---

## 📁 **OUTPUT ESPERADO:**

### **Arquivos Gerados:**
```
results/ricci_flow/
├── ricci_flow_spanish_real.json
├── ricci_flow_spanish_config.json
├── ricci_flow_english_real.json
├── ricci_flow_english_config.json
├── ricci_flow_chinese_real.json
└── ricci_flow_chinese_config.json
```

### **Conteúdo de cada JSON:**
```json
{
  "language": "spanish",
  "network_type": "real",
  "timestamp": "2025-11-05 19:30:00",
  "parameters": {
    "iterations": 200,
    "alpha": 0.5,
    "step": 0.5
  },
  "initial_metrics": {
    "n_nodes": 422,
    "n_edges": 571,
    "clustering": 0.168,
    "kappa": -0.116,
    "density": 0.006428
  },
  "final_metrics": {
    "clustering": 0.173,
    "kappa": -0.109,
    "density": 0.006428
  },
  "deltas": {
    "delta_C": +0.005,
    "delta_kappa": +0.007
  },
  "trajectory": [
    {"step": 0, "clustering": 0.168, "kappa": -0.116},
    {"step": 10, "clustering": 0.170, "kappa": -0.114},
    ...
  ],
  "convergence": {
    "converged": true,
    "steps_to_convergence": 47
  }
}
```

---

## 🎯 **ANÁLISE PÓS-EXECUÇÃO:**

### **Script de Análise:**
```bash
python code/analysis/analyze_ricci_flow_results.py
```

**Output:**
- Tabela comparativa (Real vs Config nulls)
- Gráficos de trajetória (C(t), κ(t))
- Teste estatístico (Real vs Config deltas)
- Verdict: Equilibrium, Near, ou Far

---

## ✅ **CHECKLIST PRÉ-DEPLOY:**

- [x] Script Python criado com REAL Ollivier-Ricci
- [x] Kubernetes manifests criados
- [x] Node selectors configurados
- [x] Deploy script criado
- [x] Monitor script criado
- [ ] Testar cluster connectivity
- [ ] Verificar workspace path nos nodes
- [ ] Criar namespace hyperbolic-semantic
- [ ] **DEPLOY!**

---

## 🚀 **READY TO LAUNCH!**

**Próximo comando:**
```bash
./scripts/deploy_ricci_flow_cluster.sh
```

**Então:**
```bash
./scripts/monitor_ricci_flow.sh  # Em outra janela
```

**Resultado esperado em:** 12-18 horas

**Se tudo der certo:** **NATURE-TIER PAPER!** 🏆

