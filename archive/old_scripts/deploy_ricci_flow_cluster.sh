#!/bin/bash
# DEPLOY RICCI FLOW - DARWIN CLUSTER
# Deploy 6 parallel jobs for Ricci flow analysis

set -e

echo "=================================================================="
echo "RICCI FLOW DEPLOYMENT - DARWIN CLUSTER"
echo "=================================================================="
echo ""
echo "🎯 OBJETIVO: Testar equilíbrio de Ricci flow em redes semânticas"
echo ""
echo "📦 JOBS:"
echo "   1. Spanish Real (Maria/T560)"
echo "   2. Spanish Config (Maria/T560)"
echo "   3. English Real (Dell 5860)"
echo "   4. English Config (Dell 5860)"
echo "   5. Chinese Real (Maria/T560)"
echo "   6. Chinese Config (Dell 5860)"
echo ""
echo "⏱️  TEMPO ESTIMADO: 12-24 horas (paralelo)"
echo ""
echo "=================================================================="
echo ""

# Check cluster connectivity
echo "🔍 Verificando conectividade com cluster..."
if ! kubectl cluster-info &>/dev/null; then
    echo "❌ ERRO: Cluster não acessível!"
    echo "   Verifique KUBECONFIG e Tailscale"
    exit 1
fi

echo "✅ Cluster acessível"
echo ""

# Check nodes
echo "📊 Nodes disponíveis:"
kubectl get nodes -o wide
echo ""

# Create namespace if doesn't exist
echo "📦 Criando namespace hyperbolic-semantic..."
kubectl create namespace hyperbolic-semantic --dry-run=client -o yaml | kubectl apply -f -
echo ""

# Check if workspace path exists on nodes
echo "🔍 Verificando workspace path..."
echo "   Path: /home/agourakis82/workspace/hyperbolic-semantic-networks"
echo ""

# Deploy jobs
echo "🚀 Deploying Ricci flow jobs..."
echo ""

kubectl apply -f k8s/ricci-flow-deployment.yaml

echo ""
echo "✅ Jobs deployed successfully!"
echo ""

# Monitor status
echo "=================================================================="
echo "📊 JOB STATUS:"
echo "=================================================================="
kubectl get jobs -n hyperbolic-semantic -l app=ricci-flow
echo ""

echo "=================================================================="
echo "📊 POD STATUS:"
echo "=================================================================="
kubectl get pods -n hyperbolic-semantic -l app=ricci-flow
echo ""

echo "=================================================================="
echo "📝 MONITORING COMMANDS:"
echo "=================================================================="
echo ""
echo "# Ver status de todos os jobs:"
echo "kubectl get jobs -n hyperbolic-semantic -l app=ricci-flow"
echo ""
echo "# Ver logs de um job específico:"
echo "kubectl logs -f job/ricci-flow-spanish-real -n hyperbolic-semantic"
echo ""
echo "# Ver todos os logs em paralelo (multiple terminals):"
echo "for job in spanish-real spanish-config english-real english-config chinese-real chinese-config; do"
echo "  kubectl logs -f job/ricci-flow-\$job -n hyperbolic-semantic &"
echo "done"
echo ""
echo "# Ver resultados (quando completos):"
echo "ls -lh results/ricci_flow/"
echo ""
echo "=================================================================="
echo "⏱️  ESTIMATIVA: 12-24 horas"
echo "=================================================================="
echo ""
echo "Jobs rodando! Use os comandos acima para monitorar." echo ""
echo "🎯 PRÓXIMO: Aguardar conclusão e analisar resultados"

