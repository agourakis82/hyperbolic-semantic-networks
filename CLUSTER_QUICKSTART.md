# QUICKSTART - HYPERBOLIC SEMANTIC NO CLUSTER DARWIN
**Repo:** hyperbolic-semantic-network  
**Namespace:** hyperbolic-semantic  
**ClusterQueue:** hyperbolic-semantic (20% recursos)  
**Volcano Queue:** hyperbolic-queue

---

## 🚀 COMO SUBMETER JOBS

### Template Básico (CPU):
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: meu-job
  namespace: hyperbolic-semantic  # SEU NAMESPACE!
  labels:
    kueue.x-k8s.io/queue-name: hyperbolic-semantic
spec:
  template:
    spec:
      priorityClassName: normal-priority
      nodeSelector:
        darwin.dev/device: t560  # ou macpro-worker
      containers:
      - name: trabalho
        image: python:3.11-slim
        command: ["python", "script.py"]
        resources:
          requests:
            memory: 16Gi
            cpu: 8
      restartPolicy: Never
```

### Template NFS (Mac Pro - I/O Heavy!)
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: graph-indexing
  namespace: hyperbolic-semantic
spec:
  template:
    spec:
      nodeSelector:
        darwin.dev/nfs-server: "true"  # Mac Pro (Thunderbolt local!)
      containers:
      - name: indexing
        image: python:3.11-slim
        command: ["python", "index_graphs.py"]
        resources:
          requests:
            memory: 24Gi
            cpu: 6
        volumeMounts:
        - name: graphs
          mountPath: /data
      volumes:
      - name: graphs
        persistentVolumeClaim:
          claimName: graphs-nfs-pvc
      restartPolicy: Never
```

---

## 💾 STORAGE (3 Tiers - NFS Ideal para Graphs!)

### Tier 3: NFS Shared (Mac Pro) - 3TB @ 500 MB/s ⭐
```yaml
storageClassName: nfs-shared  # IDEAL para graphs grandes compartilhados!
```

### Tier 1: NVMe Fast - 3.6TB @ 7000 MB/s
```yaml
storageClassName: t560-nvme-fast  # Para processamento ativo
```

### Tier 2: HDD Bulk - 7.2TB @ 500 MB/s
```yaml
storageClassName: t560-hdd-bulk  # Para archives
```

---

## 📚 DOCUMENTAÇÃO COMPLETA

1. **WORKFLOW_DARWIN_GUIDE.md** - Como trabalhar
2. **MULTI_REPO_OPTIMIZATION_GUIDE.md** - Detalhes multi-repo
3. **CLUSTER_RESOURCES_REAL.md** - Recursos (100GbE + 47TB!)

---

## 🎯 RECURSOS ALOCADOS

- **RAM:** 20-128Gi (nominal 20Gi, borrowing até 96Gi)
- **CPU:** 4-16 cores
- **NFS Access:** 3TB Pegasus R4 (ideal para graphs!)
- **Fair Share:** 20%

---

**Grafana:** http://100.112.110.114:30000

