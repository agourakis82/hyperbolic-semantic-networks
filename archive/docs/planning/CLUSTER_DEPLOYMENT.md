# 🚀 Darwin Cluster Deployment - Hyperbolic Semantic Networks

**Status:** ✅ Pronto para deploy  
**Date:** 2025-11-03  
**Coordination:** Kueue multi-repo (4 repos simultâneos)

---

## 📊 Infraestrutura Existente

### Namespace & Kueue
```bash
Namespace: hyperbolic-semantic (criado 2025-11-02)
LocalQueue: hyperbolic-semantic
ClusterQueue: hyperbolic-semantic (cohort: darwin-research)
```

### Recursos Alocados
```yaml
Nominal:
  CPU: 18 cores
  Memory: 150Gi
  GPU: 1x nvidia-l4

Borrowing (quando outros repos idle):
  CPU: até 36 cores
  Memory: até 300Gi
  GPU: até 1
```

### ResourceFlavors
- `x86-nvidia-l4` (T560 - L4 24GB)
- `arm64-metal` (MacBook M3 MAX - MPS)
- `x86-cpu-only` (5860 - RTX 4000)

---

## 🎯 Workload: Structural Nulls Analysis

### Dados
**Source:** `/home/agourakis82/workspace/pcs-meta-repo/data/processed/`

```
spanish_edges.csv  (237K)
dutch_edges.csv    (289K)
chinese_edges.csv  (184K)
english_edges.csv  (256K)
```

**Total:** 4 languages, 500 nodes each, ~776 edges

### Job Specification

**Manifest:** `/home/agourakis82/darwin-cluster/kubernetes/projects/hyperbolic-semantic-nulls.yml`

```yaml
Resources:
  CPU: 4 cores (request), 8 cores (limit)
  Memory: 8Gi (request), 16Gi (limit)
  GPU: 0 (graph analysis, CPU-only)

Compute:
  M = 1000 replicates (configuration + triadic)
  4 languages × 2 null types × 1000 replicates
  Expected runtime: 2-4 hours

Storage:
  PVC: hyperbolic-data (10Gi, ReadWriteOnce)
  PVC: hyperbolic-results (5Gi, ReadWriteMany)
  StorageClass: local-path (KIND default)
```

### Script Modificado

**Original:** `code/analysis/07_structural_nulls.py` (hardcoded paths)  
**Cluster:** `code/analysis/07_structural_nulls_cluster.py` (env vars)

**Mudanças:**
- Lê `DATA_DIR` de env var (default: `/data/processed`)
- Lê `OUTPUT_DIR` de env var (default: `/results/structural_nulls`)
- Compatível com ConfigMap Kubernetes

---

## 🚀 Deploy

### One-Click Deploy

```bash
/home/agourakis82/darwin-cluster/scripts/hyperbolic-deploy.sh
```

**O que faz:**
1. ✓ Verifica namespace `hyperbolic-semantic`
2. ✓ Aplica manifests K8s (PVCs + ConfigMap + Job)
3. ✓ Aguarda PVCs serem bound
4. ✓ Copia dados SWOW para PVC via pod temporário
5. ✓ Monitora admissão Kueue
6. ✓ Mostra status do job

### Manual Deploy (passo a passo)

```bash
# 1. Apply manifests
kubectl apply -f /home/agourakis82/darwin-cluster/kubernetes/projects/hyperbolic-semantic-nulls.yml

# 2. Wait for PVCs
kubectl wait --for=condition=bound pvc/hyperbolic-data -n hyperbolic-semantic --timeout=60s
kubectl wait --for=condition=bound pvc/hyperbolic-results -n hyperbolic-semantic --timeout=60s

# 3. Copy data to PVC
kubectl run data-loader -n hyperbolic-semantic --image=busybox:latest --restart=Never \
  --overrides='{"spec":{"volumes":[{"name":"data","persistentVolumeClaim":{"claimName":"hyperbolic-data"}}],"containers":[{"name":"loader","image":"busybox","command":["sleep","3600"],"volumeMounts":[{"name":"data","mountPath":"/data"}]}]}}'

kubectl wait --for=condition=ready pod/data-loader -n hyperbolic-semantic --timeout=60s

kubectl exec -n hyperbolic-semantic data-loader -- mkdir -p /data/processed

for file in spanish_edges.csv dutch_edges.csv chinese_edges.csv english_edges.csv; do
  kubectl cp /home/agourakis82/workspace/pcs-meta-repo/data/processed/$file \
    hyperbolic-semantic/data-loader:/data/processed/$file
done

kubectl delete pod data-loader -n hyperbolic-semantic

# 4. Job starts automatically (Kueue admission)
```

---

## 📊 Monitoring

### Check Job Status
```bash
# Job progress
kubectl get jobs -n hyperbolic-semantic -w

# Pods
kubectl get pods -n hyperbolic-semantic

# Logs (real-time)
kubectl logs -n hyperbolic-semantic -l app=hyperbolic-semantic -f
```

### Check Kueue Coordination
```bash
# Workload admission status
kubectl get workload -n hyperbolic-semantic

# LocalQueue status
kubectl describe localqueue hyperbolic-semantic -n hyperbolic-semantic

# ClusterQueue (cross-repo)
kubectl describe clusterqueue hyperbolic-semantic
```

### Check Other Repos (Coordination)
```bash
# See what other repos are doing
~/.darwin-global/darwin-omniscient-agent.sh

# All running jobs across repos
kubectl get jobs -A | grep Running

# GPU usage (if borrowing)
kubectl describe node maria | grep nvidia.com/gpu
```

---

## 📥 Retrieve Results

### Option 1: Via kubectl cp
```bash
# List results
kubectl exec -n hyperbolic-semantic <pod-name> -- ls -lh /results/structural_nulls/

# Copy back to local
kubectl cp hyperbolic-semantic/<pod-name>:/results/structural_nulls/all_structural_nulls.json \
  /home/agourakis82/workspace/hyperbolic-semantic-networks/results/structural_nulls/all_structural_nulls.json
```

### Option 2: Via PVC mount
```bash
# Create read pod
kubectl run results-reader -n hyperbolic-semantic --image=busybox:latest --restart=Never \
  --overrides='{"spec":{"volumes":[{"name":"results","persistentVolumeClaim":{"claimName":"hyperbolic-results"}}],"containers":[{"name":"reader","image":"busybox","command":["sleep","3600"],"volumeMounts":[{"name":"results","mountPath":"/results"}]}]}}'

# Copy all results
kubectl cp hyperbolic-semantic/results-reader:/results/structural_nulls/ \
  /home/agourakis82/workspace/hyperbolic-semantic-networks/results/structural_nulls/

# Cleanup
kubectl delete pod results-reader -n hyperbolic-semantic
```

---

## 🎯 After Completion

### 1. Verify Results
```bash
cd /home/agourakis82/workspace/hyperbolic-semantic-networks/results/structural_nulls

ls -lh
# Expected:
#   spanish_configuration_nulls.json
#   spanish_triadic_nulls.json
#   dutch_configuration_nulls.json
#   dutch_triadic_nulls.json
#   chinese_configuration_nulls.json
#   chinese_triadic_nulls.json
#   english_configuration_nulls.json
#   english_triadic_nulls.json
#   all_structural_nulls.json  ← Main results
```

### 2. Fill Manuscript Placeholders
```bash
cd /home/agourakis82/workspace/hyperbolic-semantic-networks/code/analysis
python 08_fill_placeholders.py
```

### 3. Generate Final PDF
```bash
cd /home/agourakis82/workspace/hyperbolic-semantic-networks/manuscript
pandoc main_v1.8_filled.md -o main_v1.8_FINAL.pdf \
  --pdf-engine=xelatex \
  -V geometry:margin=1in
```

### 4. Commit & Push
```bash
cd /home/agourakis82/workspace/hyperbolic-semantic-networks

git add results/structural_nulls/*.json
git add manuscript/main_v1.8_filled.md
git add manuscript/main_v1.8_FINAL.pdf
git add code/analysis/07_structural_nulls_cluster.py

git commit -m "feat: complete structural null analysis on Darwin Cluster

- Deployed to Kueue-managed hyperbolic-semantic namespace
- Generated M=1000 nulls (configuration + triadic) for 4 languages
- Computed Δκ, p_MC, Cliff's δ
- Filled manuscript v1.8 placeholders
- SUBMISSION READY for Network Science journal"

git push origin main
```

---

## ⚠️ Troubleshooting

### Job Not Starting
```bash
# Check Kueue admission
kubectl describe workload -n hyperbolic-semantic

# Check resource availability
kubectl describe clusterqueue hyperbolic-semantic

# Check if other repos are using resources
kubectl get jobs -A | grep Running
```

### Out of Resources
```bash
# Kueue will automatically:
# - Borrow from idle repos (up to 36 CPU, 300Gi RAM)
# - Preempt lower-priority jobs if needed

# Manual check:
kubectl describe clusterqueue hyperbolic-semantic | grep -A 10 "Flavors Usage"
```

### Data Not Found in Container
```bash
# Verify PVC has data
kubectl exec -n hyperbolic-semantic <pod-name> -- ls -lh /data/processed/

# If empty, re-run data copy step from deployment
```

### Job Failed
```bash
# Check logs
kubectl logs -n hyperbolic-semantic <pod-name>

# Describe pod (events)
kubectl describe pod -n hyperbolic-semantic <pod-name>

# Delete and re-deploy
kubectl delete job structural-nulls-analysis -n hyperbolic-semantic
kubectl apply -f /home/agourakis82/darwin-cluster/kubernetes/projects/hyperbolic-semantic-nulls.yml
```

---

## 📚 References

- **Multi-Repo Guide:** `/home/agourakis82/darwin-cluster/MULTI_REPO_OPTIMIZATION_GUIDE.md`
- **Cluster Quickstart:** `/home/agourakis82/darwin-cluster/CLUSTER_QUICKSTART.md`
- **Darwin Workflow:** `/home/agourakis82/darwin-cluster/WORKFLOW_DARWIN_GUIDE.md`
- **Grafana:** http://100.112.110.114:30000

---

**Ready to deploy? Run:**
```bash
/home/agourakis82/darwin-cluster/scripts/hyperbolic-deploy.sh
```

🚀 **Good luck! This is PhD-quality work!**

