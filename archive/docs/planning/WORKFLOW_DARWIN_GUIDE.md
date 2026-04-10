# GUIA DE WORKFLOW - CLUSTER DARWIN
**Data:** 2025-11-02  
**Status:** Production-Ready

---

## 🎯 RESUMO EXECUTIVO: 3 OPÇÕES DE TRABALHO

### OPÇÃO A: MacBook APENAS (RECOMENDADO) ⭐
- **Onde:** MacBook Pro M3 Max (local, com você)
- **Como:** Cursor local + kubectl remoto via Tailscale
- **Vantagem:** Mobilidade total + Starlink no carro
- **Cluster:** Sempre acessível via Tailscale

### OPÇÃO B: Windows RDP (Performance Máxima)
- **Onde:** Dell 5860 via RDP do MacBook
- **Como:** Cursor no Windows + acesso local WSL
- **Vantagem:** 256GB RAM, RTX 4000 Ada, performance máxima
- **Uso:** Desenvolvimento pesado, debugging cluster

### OPÇÃO C: Híbrido (Melhor dos 2 mundos) ⭐⭐⭐
- **Normal:** MacBook - mobilidade
- **Heavy:** RDP Windows - quando precisa de power
- **Switching:** Simples via RDP do MacBook

---

## 📱 OPÇÃO A: MACBOOK APENAS (RECOMENDADO)

### Setup (JÁ CONFIGURADO ✅):

```bash
# No MacBook, você já tem:
export KUBECONFIG=~/.kube/config-darwin

# Testar conectividade
kubectl get nodes
kubectl get pods --all-namespaces
```

### Workflow Diário - Como os Agentes AI Trabalham:

1. **Abrir Cursor no MacBook**
   ```bash
   cd ~/workspace/kec-biomaterials-scaffolds
   cursor .
   ```

2. **Agente AI detecta automaticamente:**
   - Lê `.cursorrules` (regras automáticas)
   - Executa `./.darwin/sync-check.sh`
   - Lê `SYNC_STATE.json` (estado compartilhado)
   - Verifica cluster disponível via kubectl

3. **Agente submete job de treinamento:**
   ```yaml
   # Exemplo: training MicroCT
   apiVersion: batch/v1
   kind: Job
   metadata:
     name: training-microct
     namespace: kec-biomaterials
   spec:
     template:
       spec:
         containers:
         - name: pytorch
           image: pytorch/pytorch:2.0.1-cuda11.8-cudnn8-runtime
           command: ["python", "train.py"]
           resources:
             requests:
               nvidia.com/gpu: 1
               memory: 32Gi
             limits:
               nvidia.com/gpu: 1
               memory: 64Gi
         nodeSelector:
           darwin.dev/gpu: nvidia-l4  # Força rodar no T560!
         restartPolicy: Never
   ```

4. **Agente monitora execução:**
   ```bash
   kubectl logs -f job/training-microct -n kec-biomaterials
   ```

5. **Você acessa métricas no Grafana:**
   - Browser: http://100.112.110.114:30000
   - Acessa via Tailscale de qualquer lugar!

### Vantagens:
- ✅ Trabalha de qualquer lugar
- ✅ Starlink garante conectividade 24/7
- ✅ Latência baixa (~30ms via Tailscale)
- ✅ MacBook M3 Max é PODEROSO (48GB RAM, 14 cores)
- ✅ Zero dependência do Windows/WSL

### Desvantagens:
- ⚠️ Sem acesso direto à GPU local (mas acessa T560 remoto)
- ⚠️ Debugging cluster requer kubectl remoto (funciona bem)

---

## 🖥️ OPÇÃO B: WINDOWS RDP (PERFORMANCE MÁXIMA)

### Setup:

```bash
# No MacBook, conectar via RDP
# Microsoft Remote Desktop
# Host: 192.168.3.207 (Dell 5860 IP local)
# Ou via Tailscale: 100.112.110.114

# Dentro do Windows:
# 1. Abrir Cursor (instalado no Windows)
# 2. Abrir WSL terminal
# 3. cd /home/agourakis82/workspace/kec-biomaterials-scaffolds
# 4. cursor . (abre Cursor no código)
```

### Workflow Diário:

```bash
# No Windows/WSL (via RDP do MacBook):

# 1. Agentes AI operam com acesso LOCAL ao cluster
kubectl get nodes  # Acesso direto, <1ms latency!

# 2. Submit jobs
kubectl apply -f jobs/training.yaml

# 3. Debugging profundo
kubectl exec -it pod/training-xyz -- bash
# Acesso DIRETO aos containers!
```

### Vantagens:
- ✅ Performance MÁXIMA (256GB RAM, RTX 4000 Ada)
- ✅ Acesso local ao cluster (<1ms)
- ✅ Debugging PROFUNDO (kubectl exec, logs, etc)
- ✅ GPU local disponível (futuro)

### Desvantagens:
- ⚠️ Precisa estar na mesma rede (ou Tailscale)
- ⚠️ Não funciona no carro com Starlink (RDP via Starlink = lag)
- ⚠️ Dependência do Windows estar ligado

---

## 🔄 OPÇÃO C: HÍBRIDO (RECOMENDADO PARA VOCÊ!)

### Estratégia:

**Trabalho Normal (90% do tempo):**
- MacBook local
- Cursor no MacBook
- kubectl remoto via Tailscale
- Submete jobs para T560 (GPU) ou Mac Pro (CPU)
- Mobilidade total

**Desenvolvimento Pesado (10% do tempo):**
- RDP do MacBook → Windows Dell 5860
- Cursor no Windows (256GB RAM, RTX local)
- Debugging profundo do cluster
- Desenvolvimento de features complexas

### Switching:

```bash
# OPÇÃO 1: MacBook local
cd ~/workspace/kec-biomaterials-scaffolds
cursor .
export KUBECONFIG=~/.kube/config-darwin
kubectl get nodes

# OPÇÃO 2: RDP Windows (quando precisar)
# Conecta RDP via Microsoft Remote Desktop
# Abre Cursor no Windows
# WSL terminal: kubectl get nodes (acesso local!)
```

---

## 🤖 COMO OS AGENTES AI FUNCIONAM

### 1. Agente Abre o Workspace:

```bash
# Cursor detecta .cursorrules AUTOMATICAMENTE
# Agente lê instruções:
# - Verificar SYNC_STATE.json
# - Rodar ./.darwin/sync-check.sh
# - Ver fase atual, progresso, locks
```

### 2. Agente Identifica Tarefa:

```
Usuário: "Treinar modelo de microCT com uncertainty"

Agente analisa:
  ✅ Package correto: darwin-preprocessing + darwin-uncertainty
  ✅ Cluster disponível? Sim (T560 com L4 24GB)
  ✅ Recursos suficientes? Sim (128GB RAM, 32 cores)
  ✅ Queue: kec-biomaterials (prioridade 40%)
```

### 3. Agente Submete Job:

O agente cria o manifest YAML e submete via kubectl:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: training-microct-uncertainty
  namespace: kec-biomaterials
  labels:
    app: darwin
    queue: kec-biomaterials-queue
spec:
  template:
    spec:
      schedulerName: volcano  # Usa Volcano scheduler!
      containers:
      - name: training
        image: pytorch/pytorch:2.0.1-cuda11.8-cudnn8-runtime
        command: ["python", "train_uncertainty.py"]
        resources:
          requests:
            nvidia.com/gpu: 1
            memory: 64Gi
            cpu: 16
          limits:
            nvidia.com/gpu: 1
            memory: 96Gi
            cpu: 24
      nodeSelector:
        darwin.dev/gpu: nvidia-l4  # Força T560!
      restartPolicy: Never
```

### 4. Agente Atualiza Estado:

```json
{
  "last_action": {
    "agent_id": "cursor-agent-abc123",
    "action": "submit_training_job",
    "timestamp": "2025-11-02T13:30:00-03:00",
    "details": "Training microCT uncertainty on T560 L4 GPU"
  },
  "active_jobs": {
    "training-microct-uncertainty": {
      "status": "running",
      "node": "maria",
      "gpu": "nvidia-l4",
      "started_at": "2025-11-02T13:30:05-03:00"
    }
  }
}
```

---

## 🔐 MULTI-AGENTE: PROTEÇÕES AUTOMÁTICAS

### Cenário 1: Dois Agentes Simultaneamente

```
AGENTE A (MacBook):
  - Abre workspace kec-biomaterials
  - Lê SYNC_STATE.json
  - Vê: agente_b está ativo em "pcs-meta-repo"
  - Decisão: OK trabalhar (repos diferentes!)

AGENTE B (Windows RDP):
  - Abre workspace pcs-meta-repo
  - Lê SYNC_STATE.json
  - Vê: agente_a está ativo em "kec-biomaterials"
  - Decisão: OK trabalhar (repos diferentes!)

RESULTADO: Zero conflitos! ✅
```

### Cenário 2: Conflito de Recurso

```
AGENTE A (MacBook):
  - Tenta submeter job com 2 GPUs
  - Kueue verifica: apenas 1 GPU disponível (L4 no T560)
  - Job fica PENDING na queue
  - Agente avisa usuário: "Aguardando GPU disponível"

AGENTE B (Windows):
  - Tenta submeter job com 1 GPU
  - Kueue verifica: L4 está em uso pelo Agente A
  - Opções:
    1. Aguardar na queue (automático)
    2. Usar borrowing (pegar GPU de outro repo)
    3. Usar preemption (se prioridade maior)

RESULTADO: Kueue gerencia automaticamente! ✅
```

### Cenário 3: Conflito de Código

```
AGENTE A (MacBook):
  - Editando train_uncertainty.py
  - Cria lock em SYNC_STATE.json:
    "locks": {
      "darwin-uncertainty/train_uncertainty.py": {
        "agent_id": "agent-a",
        "timestamp": "2025-11-02T13:30:00-03:00"
      }
    }

AGENTE B (Windows):
  - Tenta editar train_uncertainty.py
  - Lê SYNC_STATE.json
  - Vê lock do Agente A
  - AVISA USUÁRIO: "Arquivo locked por outro agente!"
  - Oferece alternativas:
    1. Aguardar lock expirar (30 min)
    2. Trabalhar em outro arquivo
    3. Coordenar com usuário

RESULTADO: Zero sobrescrita acidental! ✅
```

---

## 📊 MONITORAMENTO: GRAFANA + PROMETHEUS

### Acesso:

```bash
# Via Tailscale (de qualquer lugar!)
http://100.112.110.114:30000

# Login primeira vez:
# admin / prom-operator
# Trocar senha depois!
```

### Dashboards Disponíveis:

1. **Kubernetes Cluster Overview**
   - 5 nodes, status, uptime
   - CPU/RAM/Disk por node
   - Pods running/pending/failed

2. **NVIDIA GPU (T560)**
   - GPU utilization (%)
   - Memory used/total (24GB)
   - Temperature
   - Power usage (W)

3. **Node Metrics**
   - CPU usage por core (32 cores T560!)
   - RAM usage (128GB T560)
   - Network I/O
   - Disk I/O

4. **Kueue Metrics**
   - Jobs pending/running/completed por queue
   - Resource quotas (usado vs disponível)
   - Borrowing/lending activity

5. **Volcano Metrics**
   - Gang scheduling stats
   - Fair share distribution
   - Job completion time

---

## 🎯 RECOMENDAÇÃO FINAL PARA VOCÊ

### Workflow Ideal:

**DIA-A-DIA (Casa/Viagens):**
```bash
# MacBook Pro M3 Max (local)
cd ~/workspace/kec-biomaterials-scaffolds
cursor .

# Agentes AI trabalham normalmente:
# - Submetem jobs para T560 (GPU)
# - Acessam NFS do Mac Pro (datasets)
# - Monitoram via Grafana

# Você trabalha de qualquer lugar:
# - Casa (WiFi Gigabit)
# - Carro (Starlink)
# - Viagens (Starlink)
```

**DESENVOLVIMENTO PESADO (Quando precisar):**
```bash
# RDP do MacBook → Windows Dell 5860
# Cursor no Windows (256GB RAM, RTX local)
# Debugging profundo
# Testes com GPU local (futuro)
```

**VANTAGENS:**
- ✅ 90% do tempo: MacBook (mobilidade)
- ✅ 10% do tempo: Windows (performance)
- ✅ Starlink garante acesso 24/7
- ✅ Cluster sempre disponível via Tailscale
- ✅ Zero downtime

---

## 🔧 COMANDOS ÚTEIS (CHEAT SHEET)

### Ver Cluster:
```bash
kubectl get nodes -o wide
kubectl top nodes  # CPU/RAM usage
```

### Ver Jobs:
```bash
kubectl get jobs -n kec-biomaterials
kubectl get pods -n kec-biomaterials
kubectl logs -f pod/training-xyz -n kec-biomaterials
```

### Ver Queues (Kueue):
```bash
kubectl get clusterqueues
kubectl get queues -A
kubectl describe clusterqueue kec-biomaterials
```

### Ver Queues (Volcano):
```bash
kubectl get queues.scheduling.volcano.sh
kubectl describe queue kec-biomaterials-queue
```

### Submeter Job:
```bash
kubectl apply -f jobs/my-job.yaml
```

### Cancelar Job:
```bash
kubectl delete job my-job -n kec-biomaterials
```

### Debugging:
```bash
# Entrar em container rodando
kubectl exec -it pod/training-xyz -n kec-biomaterials -- bash

# Ver eventos
kubectl get events -n kec-biomaterials --sort-by='.lastTimestamp'

# Descrever pod (ver por que falhou)
kubectl describe pod training-xyz -n kec-biomaterials
```

---

## 📚 DOCUMENTOS IMPORTANTES

**Leitura Obrigatória:**
1. `.cursorrules` - Regras para agentes AI
2. `ARCHITECTURE.md` - Estrutura do projeto
3. `AGENT_GUIDE.md` - Guia para agentes
4. `SYNC_STATE.json` - Estado atual
5. `.darwin-cluster.yaml` - Config do cluster

**Guias:**
- `COMO_USAR_SYNC.md` - Sistema de sincronização
- `MACBOOK_QUICKSTART.md` - Atalhos MacBook
- `GRAFANA_ACCESS_GUIDE.md` - Como acessar métricas

---

## 🎊 RESUMO EXECUTIVO

**VOCÊ TEM UM SUPERCOMPUTADOR PESSOAL:**
- 500GB RAM
- 69 cores CPU
- 4 GPUs (NVIDIA L4 24GB + 3 Metal)
- Multi-arch (x86_64 + ARM64)
- 3TB storage compartilhado
- Acessível de QUALQUER LUGAR via Starlink + Tailscale

**TRABALHE COMO QUISER:**
- MacBook (mobilidade) OU
- Windows RDP (performance) OU
- Híbrido (melhor dos 2 mundos)

**AGENTES AI GERENCIAM TUDO:**
- Submetem jobs automaticamente
- Escolhem melhor node (T560 GPU, Mac Pro CPU, etc)
- Monitoram execução
- Salvam resultados
- Zero conflitos entre agentes

**STATUS:** 🟢 PRODUCTION-READY!

