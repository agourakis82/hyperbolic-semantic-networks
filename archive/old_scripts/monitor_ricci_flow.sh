#!/bin/bash
# MONITOR RICCI FLOW JOBS - Real-time dashboard
# Usage: ./monitor_ricci_flow.sh

NAMESPACE="hyperbolic-semantic"

while true; do
    clear
    echo "=================================================================="
    echo "RICCI FLOW - REAL-TIME MONITOR"
    echo "=================================================================="
    echo "$(date)"
    echo ""
    
    echo "📊 JOB STATUS:"
    echo "------------------------------------------------------------------"
    kubectl get jobs -n $NAMESPACE -l app=ricci-flow -o custom-columns=\
NAME:.metadata.name,\
COMPLETIONS:.status.succeeded/.spec.completions,\
DURATION:.status.startTime,\
AGE:.metadata.creationTimestamp
    
    echo ""
    echo "📦 POD STATUS:"
    echo "------------------------------------------------------------------"
    kubectl get pods -n $NAMESPACE -l app=ricci-flow -o custom-columns=\
NAME:.metadata.name,\
STATUS:.status.phase,\
NODE:.spec.nodeName,\
AGE:.metadata.creationTimestamp
    
    echo ""
    echo "💾 RESULTADOS (se disponíveis):"
    echo "------------------------------------------------------------------"
    if [ -d "results/ricci_flow" ]; then
        ls -lh results/ricci_flow/*.json 2>/dev/null | tail -10 || echo "   (nenhum resultado ainda)"
    else
        echo "   (diretório não criado ainda)"
    fi
    
    echo ""
    echo "=================================================================="
    echo "Atualizando em 30 segundos... (Ctrl+C para sair)"
    echo "=================================================================="
    
    sleep 30
done

