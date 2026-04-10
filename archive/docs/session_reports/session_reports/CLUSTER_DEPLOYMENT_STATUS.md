# 🚀 CLUSTER DEPLOYMENT - Minor Revisions Distributed Processing
**Cluster:** Darwin (maria node - T560)  
**Resources:** 32 cores, 251GB RAM, 100Gbps Mellanox  
**Jobs Deployed:** 3 configuration nulls (M=1000 each)  
**Expected Speedup:** 3x (parallel) + faster CPU = ~2h instead of 18h

---

## 📊 JOBS DEPLOYED

### **1. spanish-config-null-corrected**
- Namespace: pcs-meta-repo
- Resources: 8-12 cores, 32-48GB RAM
- Task: Configuration null M=1000
- Input: spanish_edges_FINAL.csv (583 edges)
- Output: results/nulls_corrected/spanish_configuration_nulls.json
- ETA: ~2 hours (from 6h local)

### **2. english-config-null-corrected**
- Namespace: pcs-meta-repo
- Resources: 8-12 cores, 32-48GB RAM
- Task: Configuration null M=1000
- Input: english_edges_FINAL.csv (661 edges)
- Output: results/nulls_corrected/english_configuration_nulls.json
- ETA: ~2 hours

### **3. chinese-config-null-corrected**
- Namespace: pcs-meta-repo
- Resources: 8-12 cores, 32-48GB RAM
- Task: Configuration null M=1000
- Input: chinese_edges_FINAL.csv (768 edges)
- Output: results/nulls_corrected/chinese_configuration_nulls.json
- ETA: ~2 hours

---

## ⏰ TIMELINE

```
Hour 0:     Deploy to cluster ✅
Hour 0.5:   Pods pulling images + pip install
Hour 1:     Nulls start computing
Hour 2-3:   Nulls running (monitor progress)
Hour 3:     ✅ All 3 nulls complete (vs. 6h local)
Hour 3.5:   Bootstrap job deploy
Hour 4:     Bootstrap complete
Hour 4.5:   Sensitivity + degree dist (quick, can run local)
Hour 5:     Update all tables
Hour 6:     Generate final v1.8.15 PDFs
DONE:       ✅ Ready for submission
```

**Total Time:** 6 hours (vs. 18h local)  
**Speedup:** 3x

---

## 📋 MONITORING COMMANDS

```bash
# Check job status
kubectl get jobs -n pcs-meta-repo | grep config-null

# Check pod status
kubectl get pods -n pcs-meta-repo | grep config-null

# View logs (Spanish example)
kubectl logs -n pcs-meta-repo -l job-name=spanish-config-null-corrected -f

# Check progress
kubectl logs -n pcs-meta-repo -l job-name=spanish-config-null-corrected --tail=50 | grep "Progress"
```

---

## 🎯 EXPECTED OUTPUTS

After ~3 hours:

```
results/nulls_corrected/
├── spanish_configuration_nulls.json
├── english_configuration_nulls.json
└── chinese_configuration_nulls.json
```

Each containing:
- kappa_real: corrected value
- kappa_null_mean: μ_null
- delta_kappa: Δκ
- p_value: p_MC
- cliffs_delta: |δ|

---

**CLUSTER JOBS RUNNING - MONITOR PROGRESS** 🚀⚡


