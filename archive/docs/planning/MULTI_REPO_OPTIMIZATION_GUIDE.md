# GUIA DE OTIMIZAÇÃO MULTI-REPO - CLUSTER DARWIN
**Data:** 2025-11-02 11:40:00 -03  
**Status:** Como otimizar os 4 repos no cluster  
**Repos:** kec-biomaterials, pcs-meta-repo, chiuratto-AI, hyperbolic-semantic-network

---

## 🎯 ESTRATÉGIA: OTIMIZAÇÕES SÃO GLOBAIS!

**IMPORTANTE:** As otimizações feitas HOJE beneficiam **TODOS OS 4 REPOS!**

### Por quê?

1. **Otimizações de Hardware (T560, Dell):**
   - ZFS tuning → Todos os repos usam
   - GPU MPS → Todos os repos podem usar
   - Kernel tuning → Global para todo o cluster
   - 100GbE (amanhã) → Todos os repos se beneficiam

2. **Otimizações de Kubernetes:**
   - PriorityClasses → Disponíveis para todos os repos
   - StorageClasses → Todos podem usar (nvme-fast, hdd-bulk, nfs-shared)
   - PersistentVolumes → Compartilhados entre repos (via PVCs)

3. **Networking:**
   - Mellanox 100GbE → Acelera TODOS os jobs
   - RDMA → Todos os repos se beneficiam

**CONCLUSÃO:** Otimizações são **CLUSTER-WIDE**, não repo-specific! ✅

---

## 📊 COMO CADA REPO USA OS RECURSOS

### Repo 1: kec-biomaterials (ESTE!) - 40% recursos
**ClusterQueue:** kec-biomaterials (já configurado)  
**Volcano Queue:** kec-biomaterials-queue (fair share: 40%)

**Recursos Alocados:**
- GPU: 1x L4 (ou borrowing até 2x)
- RAM: 40-256Gi (nominal 64Gi, borrowing até 192Gi)
- CPU: 8-32 cores (nominal 8, borrowing até 24)
- Storage: Pode usar qualquer PV (nvme-fast, hdd-bulk, nfs-shared)

**Workloads Típicos:**
- Training microCT: GPU L4 + 64Gi RAM + nvme-fast
- Preprocessing: CPU only + 32Gi RAM + nfs-shared
- Inference: GPU L4 + 16Gi RAM + nvme-fast

**Como usar:**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: training-microct
  namespace: kec-biomaterials  # Namespace do repo
  labels:
    kueue.x-k8s.io/queue-name: kec-biomaterials  # ClusterQueue
spec:
  template:
    spec:
      schedulerName: volcano  # Usa Volcano
      priorityClassName: high-priority  # Usa prioridades globais!
      nodeSelector:
        darwin.dev/gpu: nvidia-l4  # Força T560
      containers:
      - name: training
        image: pytorch/pytorch:2.0.1-cuda11.8-cudnn8-runtime
        resources:
          requests:
            nvidia.com/gpu: 1
            memory: 64Gi
            cpu: 16
          limits:
            nvidia.com/gpu: 1
            memory: 96Gi
            cpu: 24
        volumeMounts:
        - name: datasets
          mountPath: /data
        - name: models
          mountPath: /models
      volumes:
      - name: datasets
        persistentVolumeClaim:
          claimName: datasets-pvc  # Usa PV nvme-fast!
      - name: models
        persistentVolumeClaim:
          claimName: models-pvc
      restartPolicy: Never
---
# PVC para datasets (usa t560-nvme-fast automaticamente!)
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: datasets-pvc
  namespace: kec-biomaterials
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: t560-nvme-fast  # StorageClass global!
  resources:
    requests:
      storage: 500Gi
---
# PVC para models
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: models-pvc
  namespace: kec-biomaterials
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: t560-nvme-fast
  resources:
    requests:
      storage: 200Gi
```

---

### Repo 2: pcs-meta-repo - 20% recursos
**ClusterQueue:** pcs-meta-repo (já configurado)  
**Volcano Queue:** pcs-meta-queue (fair share: 20%)

**Recursos Alocados:**
- GPU: 1x (borrowing possível)
- RAM: 32-128Gi
- CPU: 4-16 cores
- Storage: Mesmos PVs globais!

**Workloads Típicos:**
- Meta-learning: GPU + 64Gi RAM
- Data processing: CPU + 16Gi RAM
- Analysis: CPU + 8Gi RAM

**Como usar:**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: meta-training
  namespace: pcs-meta-repo  # Namespace diferente!
  labels:
    kueue.x-k8s.io/queue-name: pcs-meta-repo
spec:
  template:
    spec:
      schedulerName: volcano
      priorityClassName: normal-priority  # Mesmas prioridades!
      nodeSelector:
        darwin.dev/gpu: nvidia-l4
      containers:
      - name: training
        image: pytorch/pytorch:2.0.1-cuda11.8-cudnn8-runtime
        resources:
          requests:
            nvidia.com/gpu: 1
            memory: 32Gi
            cpu: 8
        volumeMounts:
        - name: datasets
          mountPath: /data
      volumes:
      - name: datasets
        persistentVolumeClaim:
          claimName: datasets-pvc  # PVC do pcs-meta-repo
      restartPolicy: Never
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: datasets-pvc
  namespace: pcs-meta-repo  # Namespace diferente, mas usa MESMO PV!
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: t560-nvme-fast  # StorageClass global!
  resources:
    requests:
      storage: 300Gi
```

---

### Repo 3: chiuratto-AI - 20% recursos
**ClusterQueue:** chiuratto-ai  
**Volcano Queue:** chiuratto-ai-queue (fair share: 20%)

**Workloads Típicos:**
- AI training: GPU + 32Gi RAM
- NLP processing: CPU ARM64 (MacBook!) + 16Gi RAM
- Inference: GPU + 8Gi RAM

**Exemplo ARM64 (MacBook M3 Max):**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: nlp-processing
  namespace: chiuratto-ai
  labels:
    kueue.x-k8s.io/queue-name: chiuratto-ai
spec:
  template:
    spec:
      schedulerName: volcano
      priorityClassName: normal-priority
      nodeSelector:
        darwin.dev/device: macbook-m3-max  # Força MacBook!
        kubernetes.io/arch: arm64  # ARM64 específico
      containers:
      - name: nlp
        image: arm64v8/python:3.11-slim  # Imagem ARM64!
        command: ["python", "process_nlp.py"]
        resources:
          requests:
            memory: 16Gi
            cpu: 8
          limits:
            memory: 24Gi
            cpu: 12
      restartPolicy: Never
```

---

### Repo 4: hyperbolic-semantic-network - 20% recursos
**ClusterQueue:** hyperbolic-semantic  
**Volcano Queue:** hyperbolic-queue (fair share: 20%)

**Workloads Típicos:**
- Graph processing: CPU x86_64 (Mac Pro ou Dell)
- Semantic analysis: CPU ARM64 (iMac M3)
- Bulk data: NFS shared

**Exemplo NFS (Mac Pro - acesso local ao Pegasus!):**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: graph-indexing
  namespace: hyperbolic-semantic
  labels:
    kueue.x-k8s.io/queue-name: hyperbolic-semantic
spec:
  template:
    spec:
      schedulerName: volcano
      priorityClassName: normal-priority
      nodeSelector:
        darwin.dev/nfs-server: "true"  # Força Mac Pro (acesso local!)
      containers:
      - name: indexing
        image: python:3.11-slim
        command: ["python", "index_graphs.py"]
        resources:
          requests:
            memory: 24Gi
            cpu: 6
        volumeMounts:
        - name: datasets
          mountPath: /data
      volumes:
      - name: datasets
        persistentVolumeClaim:
          claimName: datasets-nfs-pvc
      restartPolicy: Never
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: datasets-nfs-pvc
  namespace: hyperbolic-semantic
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: nfs-shared  # NFS do Mac Pro!
  resources:
    requests:
      storage: 1000Gi
```

---

## 🔄 BORROWING/LENDING ENTRE REPOS (Kueue Cohort)

### Como Funciona:

**Cohort:** darwin-research (todos os 4 repos compartilham!)

**Cenário 1: kec-biomaterials precisa de 2 GPUs**
```
kec-biomaterials:
  - Nominal: 1 GPU
  - Borrowing limit: +1 GPU
  
Kueue verifica:
  ✅ pcs-meta-repo: Ocioso (0 GPUs em uso)
  ✅ chiuratto-ai: Ocioso (0 GPUs em uso)
  
Kueue empresta:
  ✅ kec-biomaterials PEGA emprestado de outro repo
  ✅ Job com 2 GPUs RODA!
  
Quando pcs-meta-repo precisar:
  ⚠️ kec-biomaterials DEVOLVE (preemption se necessário)
```

**Exemplo Job com Borrowing:**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: training-dual-gpu
  namespace: kec-biomaterials
  labels:
    kueue.x-k8s.io/queue-name: kec-biomaterials
spec:
  template:
    spec:
      schedulerName: volcano
      priorityClassName: high-priority  # Maior prioridade = menos chance de preemption
      containers:
      - name: training
        resources:
          requests:
            nvidia.com/gpu: 2  # Pede 2 GPUs (1 nominal + 1 borrowing)!
            memory: 96Gi
            cpu: 24
```

---

## 📁 ESTRUTURA DE NAMESPACES E STORAGE

### Cada Repo tem:

```
Repo: kec-biomaterials
  Namespace: kec-biomaterials
  ClusterQueue: kec-biomaterials
  Volcano Queue: kec-biomaterials-queue
  
  PVCs (Private):
    - datasets-pvc (usa PV global t560-datasets-nvme)
    - models-pvc (usa PV global t560-models-nvme)
    - results-pvc (usa PV global t560-hdd-archives)
  
  Jobs:
    - Submit para namespace kec-biomaterials
    - Automaticamente usa ClusterQueue kec-biomaterials
    - Pode usar QUALQUER StorageClass global
    - Pode usar QUALQUER PriorityClass global
```

```
Repo: pcs-meta-repo
  Namespace: pcs-meta-repo
  ClusterQueue: pcs-meta-repo
  Volcano Queue: pcs-meta-queue
  
  PVCs (Private):
    - datasets-pvc (DIFERENTE do kec-biomaterials!)
    - models-pvc (namespace isolado)
  
  Jobs:
    - Submit para namespace pcs-meta-repo
    - Usa ClusterQueue pcs-meta-repo
    - Compartilha MESMOS PVs físicos (mas PVCs isolados)
```

**Isolamento:** Namespaces separam os repos  
**Compartilhamento:** PVs, StorageClasses, PriorityClasses são globais!

---

## 🚀 WORKFLOW PARA CADA REPO

### Passo 1: Criar Namespace (se não existe)

```bash
# Já criados via setup anterior:
kubectl get namespaces | grep -E "kec-biomaterials|pcs-meta-repo|chiuratto-ai|hyperbolic-semantic"
```

### Passo 2: Criar PVCs no Namespace do Repo

```bash
# Exemplo: pcs-meta-repo
cat << EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: datasets-pvc
  namespace: pcs-meta-repo
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: t560-nvme-fast  # Usa StorageClass global!
  resources:
    requests:
      storage: 300Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: models-pvc
  namespace: pcs-meta-repo
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: t560-nvme-fast
  resources:
    requests:
      storage: 100Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: results-pvc
  namespace: pcs-meta-repo
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: t560-hdd-bulk  # Results em HDD (bulk storage)
  resources:
    requests:
      storage: 500Gi
EOF
```

### Passo 3: Submeter Jobs

```bash
# Jobs automaticamente usam:
# ✅ ClusterQueue do repo (via namespace)
# ✅ Volcano Queue do repo (via scheduler)
# ✅ PriorityClasses globais (critical/high/normal/low)
# ✅ StorageClasses globais (nvme-fast/hdd-bulk/nfs-shared)
# ✅ Node Affinity para hardware correto
# ✅ Borrowing/Lending automático (Kueue Cohort!)
```

---

## 🎯 OTIMIZAÇÕES ESPECÍFICAS POR REPO

### kec-biomaterials (VOCÊ - Q1 Papers!)
**Prioridade:** CRÍTICA (deadlines Q1!)  
**Recursos:** 40% (maior fatia)

**Otimizações Específicas:**
1. **PriorityClass: critical-priority** para jobs de deadline
2. **Storage nvme-fast** para datasets ativos
3. **Node Affinity: T560 L4** para training pesado
4. **Borrowing:** Pode pegar até 100% GPU se outros ociosos!

```yaml
# Job exemplo com MÁXIMA PRIORIDADE
apiVersion: batch/v1
kind: Job
metadata:
  name: training-q1-paper-deadline
  namespace: kec-biomaterials
  labels:
    kueue.x-k8s.io/queue-name: kec-biomaterials
spec:
  template:
    spec:
      schedulerName: volcano
      priorityClassName: critical-priority  # MÁXIMA PRIORIDADE!
      nodeSelector:
        darwin.dev/gpu: nvidia-l4
      containers:
      - name: training
        image: pytorch/pytorch:2.0.1-cuda11.8-cudnn8-runtime
        resources:
          requests:
            nvidia.com/gpu: 1
            memory: 64Gi
            cpu: 16
```

---

### pcs-meta-repo (Meta-Learning)
**Prioridade:** MÉDIA  
**Recursos:** 20%

**Otimizações Específicas:**
1. **PriorityClass: normal-priority** (maioria dos jobs)
2. **Storage:** Mix nvme-fast (active) + hdd-bulk (archives)
3. **Node Affinity:** T560 L4 (se disponível) ou Mac Pro (CPU)
4. **Borrowing:** Pode pegar de outros se ociosos

**Workload ARM64 (se aplicável):**
```yaml
# Se tiver preprocessing que rode em ARM64
nodeSelector:
  darwin.dev/device: macbook-m3-max
  kubernetes.io/arch: arm64
```

---

### chiuratto-AI (NLP + AI)
**Prioridade:** MÉDIA  
**Recursos:** 20%

**Otimizações Específicas:**
1. **NLP em ARM64:** MacBook M3 Max (ótimo para NLP!)
2. **Training:** T560 L4 (se precisar GPU)
3. **Inference:** iMac M3 ou MacBook (Metal GPU)

**Exemplo NLP ARM64:**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: nlp-bert-training
  namespace: chiuratto-ai
spec:
  template:
    spec:
      schedulerName: volcano
      nodeSelector:
        darwin.dev/device: macbook-m3-max  # 48GB RAM, Metal GPU!
        kubernetes.io/arch: arm64
      containers:
      - name: nlp
        image: arm64v8/python:3.11-slim
        command: ["python", "train_bert.py"]
        resources:
          requests:
            memory: 32Gi  # MacBook tem 42Gi disponível
            cpu: 10
```

---

### hyperbolic-semantic-network (Graph Processing)
**Prioridade:** MÉDIA  
**Recursos:** 20%

**Otimizações Específicas:**
1. **NFS Shared:** Ideal para graphs grandes (acesso compartilhado)
2. **Mac Pro:** Jobs I/O-heavy rodam no Mac Pro (acesso local NFS!)
3. **CPU only:** Não usa GPU (libera para outros repos)

**Exemplo Graph Processing:**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: graph-indexing
  namespace: hyperbolic-semantic
spec:
  template:
    spec:
      schedulerName: volcano
      priorityClassName: low-priority  # Exploratório
      nodeSelector:
        darwin.dev/nfs-server: "true"  # Mac Pro (Thunderbolt local!)
      containers:
      - name: indexing
        image: python:3.11-slim
        resources:
          requests:
            memory: 24Gi
            cpu: 6
        volumeMounts:
        - name: graphs
          mountPath: /data/graphs
      volumes:
      - name: graphs
        persistentVolumeClaim:
          claimName: graphs-nfs-pvc
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: graphs-nfs-pvc
  namespace: hyperbolic-semantic
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: nfs-shared  # NFS do Pegasus R4!
  resources:
    requests:
      storage: 1500Gi
```

---

## 🎯 TEMPLATES DE JOBS POR TIPO

### Template 1: GPU Training (x86_64)
```yaml
# Para: kec-biomaterials, pcs-meta-repo, chiuratto-ai
apiVersion: batch/v1
kind: Job
metadata:
  name: gpu-training
  namespace: <SEU-REPO>
  labels:
    kueue.x-k8s.io/queue-name: <SEU-REPO>
spec:
  template:
    spec:
      schedulerName: volcano
      priorityClassName: high-priority
      nodeSelector:
        darwin.dev/gpu: nvidia-l4
        kubernetes.io/arch: amd64
      containers:
      - name: training
        image: pytorch/pytorch:2.0.1-cuda11.8-cudnn8-runtime
        resources:
          requests:
            nvidia.com/gpu: 1
            memory: 64Gi
            cpu: 16
```

### Template 2: CPU Preprocessing (ARM64)
```yaml
# Para: Qualquer repo (libera x86 para GPU!)
apiVersion: batch/v1
kind: Job
metadata:
  name: preprocessing-arm
  namespace: <SEU-REPO>
spec:
  template:
    spec:
      schedulerName: volcano
      priorityClassName: normal-priority
      nodeSelector:
        darwin.dev/device: macbook-m3-max
        kubernetes.io/arch: arm64
      containers:
      - name: preprocessing
        image: arm64v8/python:3.11-slim
        resources:
          requests:
            memory: 32Gi
            cpu: 12
```

### Template 3: NFS Heavy I/O (x86_64)
```yaml
# Para: Workloads I/O intensivos
apiVersion: batch/v1
kind: Job
metadata:
  name: data-indexing
  namespace: <SEU-REPO>
spec:
  template:
    spec:
      schedulerName: volcano
      nodeSelector:
        darwin.dev/nfs-server: "true"  # Mac Pro (Thunderbolt local!)
      containers:
      - name: indexing
        image: python:3.11-slim
        resources:
          requests:
            memory: 40Gi
            cpu: 8
        volumeMounts:
        - name: data
          mountPath: /data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: nfs-pvc
```

---

## 🤖 COMO OS AGENTES AI USAM O CLUSTER

### Workflow Automático:

```
USUÁRIO (em qualquer repo):
  "Treinar modelo X no dataset Y"

AGENTE AI:
  1. Lê .cursorrules (regras do repo)
  2. Identifica namespace correto (via repo name)
  3. Verifica ClusterQueue disponível
  4. Escolhe hardware:
     - GPU? → T560 L4
     - CPU x86? → Mac Pro ou Dell
     - ARM64? → MacBook M3 Max ou iMac M3
     - I/O heavy? → Mac Pro (NFS local)
  5. Escolhe storage:
     - Active datasets → nvme-fast
     - Archives → hdd-bulk
     - Shared → nfs-shared
  6. Escolhe prioridade:
     - Deadline Q1? → critical-priority
     - Active dev? → high-priority
     - Normal? → normal-priority
     - Exploratory? → low-priority
  7. CRIA manifest YAML automaticamente
  8. SUBMETE via kubectl
  9. MONITORA execução
  10. SALVA resultados

KUEUE:
  - Aloca recursos conforme quota do repo
  - Empresta de outros repos se ociosos (borrowing!)
  - Preempta jobs baixa prioridade se necessário

VOLCANO:
  - Fair share entre repos (40/20/20/20)
  - Gang scheduling (jobs multi-pod)
  - GPU topology awareness
```

---

## 📊 COMO VERIFICAR RECURSOS DISPONÍVEIS

### Ver recursos por repo:
```bash
# Kec-biomaterials
kubectl describe clusterqueue kec-biomaterials

# Pcs-meta-repo
kubectl describe clusterqueue pcs-meta-repo

# Chiuratto-AI
kubectl describe clusterqueue chiuratto-ai

# Hyperbolic
kubectl describe clusterqueue hyperbolic-semantic
```

### Ver jobs rodando:
```bash
# Por namespace (repo)
kubectl get jobs -n kec-biomaterials
kubectl get jobs -n pcs-meta-repo
kubectl get jobs -n chiuratto-ai
kubectl get jobs -n hyperbolic-semantic

# Todos os repos
kubectl get jobs -A
```

### Ver quotas:
```bash
kubectl get resourcequotas -A
```

### Ver borrowing/lending:
```bash
# Via Kueue
kubectl get clusterqueues -o yaml | grep -A 10 "borrowingLimit\|lendingLimit"
```

---

## 🎯 RECOMENDAÇÕES POR REPO

### kec-biomaterials (VOCÊ):
- ✅ Use **critical-priority** para deadlines Q1
- ✅ Use **nvme-fast** para datasets ativos
- ✅ Force **T560 L4** para training GPU
- ✅ Borrow agressivamente (você tem prioridade!)

### pcs-meta-repo:
- ✅ Use **normal-priority** (maioria)
- ✅ Mix **nvme-fast** + **hdd-bulk**
- ✅ Considere **ARM64** para preprocessing

### chiuratto-AI:
- ✅ Use **ARM64** (MacBook/iMac) para NLP!
- ✅ Metal GPU para inference
- ✅ CUDA GPU (T560) só se necessário

### hyperbolic-semantic:
- ✅ Use **nfs-shared** (graphs grandes)
- ✅ Force **Mac Pro** para I/O heavy
- ✅ **low-priority** para exploratório

---

## 🔧 SCRIPTS DE SETUP PARA OUTROS REPOS

### Script: Criar PVCs em qualquer repo

```bash
#!/bin/bash
# create-repo-pvcs.sh
# Usage: ./create-repo-pvcs.sh <namespace> <datasets-size> <models-size> <results-size>

NAMESPACE=$1
DATASETS_SIZE=$2
MODELS_SIZE=$3
RESULTS_SIZE=$4

kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: datasets-pvc
  namespace: $NAMESPACE
spec:
  accessModes: [ReadWriteMany]
  storageClassName: t560-nvme-fast
  resources:
    requests:
      storage: ${DATASETS_SIZE}Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: models-pvc
  namespace: $NAMESPACE
spec:
  accessModes: [ReadWriteMany]
  storageClassName: t560-nvme-fast
  resources:
    requests:
      storage: ${MODELS_SIZE}Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: results-pvc
  namespace: $NAMESPACE
spec:
  accessModes: [ReadWriteMany]
  storageClassName: t560-hdd-bulk
  resources:
    requests:
      storage: ${RESULTS_SIZE}Gi
EOF

# Exemplo:
# ./create-repo-pvcs.sh pcs-meta-repo 300 100 500
# ./create-repo-pvcs.sh chiuratto-ai 200 50 300
# ./create-repo-pvcs.sh hyperbolic-semantic 1000 50 1000
```

---

## 📈 MONITORAMENTO MULTI-REPO

### Grafana Dashboards:

**Dashboard Principal:** Darwin Cluster Overview
- Vê TODOS os repos
- Jobs por queue
- Recursos por namespace
- GPU utilization (todos os repos juntos)

**Filtrar por repo:**
```promql
# Jobs do kec-biomaterials
sum by (namespace) (kube_pod_info{namespace="kec-biomaterials"})

# GPU usage do pcs-meta-repo
DCGM_FI_DEV_GPU_UTIL{namespace="pcs-meta-repo"}
```

---

## 🎊 RESUMO EXECUTIVO

### O QUE É GLOBAL (Todos os repos usam):
✅ Hardware (T560, Dell, Mac Pro, iMac, MacBook)  
✅ Networking (100GbE amanhã!)  
✅ Storage Físico (47TB ZFS + NFS)  
✅ GPU (L4 24GB via Kueue borrowing)  
✅ PriorityClasses (critical/high/normal/low)  
✅ StorageClasses (nvme-fast/hdd-bulk/nfs-shared)  
✅ Monitoring (Grafana/Prometheus)  
✅ Otimizações (ZFS, MPS, Kernel, etc)

### O QUE É POR REPO (Isolado):
✅ Namespace (kec-biomaterials, pcs-meta-repo, etc)  
✅ ClusterQueue (quotas específicas)  
✅ Volcano Queue (fair share)  
✅ PVCs (cada repo tem seus próprios)  
✅ Jobs (submetidos no namespace do repo)

### BENEFÍCIO:
- ✅ **Otimizações de HOJE beneficiam TODOS os 4 repos!**
- ✅ **100GbE AMANHÃ beneficia TODOS os 4 repos!**
- ✅ **Zero trabalho duplicado!**
- ✅ **Cada repo usa via namespace próprio!**

---

## 🚀 PRÓXIMOS PASSOS PARA VOCÊ

1. **Abrir outros repos no Cursor:**
   ```bash
   cd ~/workspace/pcs-meta-repo
   cursor .
   # Agente AI detecta namespace "pcs-meta-repo" automaticamente!
   ```

2. **Criar PVCs em cada repo:**
   ```bash
   ./create-repo-pvcs.sh pcs-meta-repo 300 100 500
   ./create-repo-pvcs.sh chiuratto-ai 200 50 300
   ./create-repo-pvcs.sh hyperbolic-semantic 1000 50 1000
   ```

3. **Submeter jobs:**
   - Agentes AI fazem isso automaticamente!
   - Ou manual: `kubectl apply -f job.yaml`

4. **Monitorar:**
   - Grafana: http://100.112.110.114:30000
   - kubectl: `kubectl get jobs -A`

---

**RESULTADO:** Todos os 4 repos otimizados COM ZERO TRABALHO EXTRA! 🎊

