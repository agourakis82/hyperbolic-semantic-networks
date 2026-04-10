#!/bin/bash
# COMPUTE ALL REAL - Parallel execution no WSL (5860)
# Configuration nulls M=1000 + Clustering moderation + Bootstrap
# Tempo estimado REAL: 20-30 horas wallclock

set -e

cd /home/agourakis82/workspace/hyperbolic-semantic-networks

echo "=================================================================="
echo "COMPUTAÇÃO COMPLETA - TODOS OS MISSING RESULTS"
echo "=================================================================="
echo ""
echo "🎯 O QUE SERÁ COMPUTADO:"
echo "  1. Configuration Nulls M=1000 (3 languages)"
echo "  2. Clustering Moderation Validation (9 synthetic models)"
echo "  3. Bootstrap Analysis N=50"
echo ""
echo "⏱️  TEMPO ESTIMADO REAL:"
echo "  - Config nulls: 15-20 horas (paralelo)"
echo "  - Clustering: 4-6 horas"
echo "  - Bootstrap: 2-3 horas"
echo "  - TOTAL: ~24-30 horas wallclock"
echo ""
echo "=================================================================="
echo ""

mkdir -p results/final_validation
mkdir -p logs/final_validation

# JOB 1: Spanish Configuration Nulls M=1000
echo "🚀 Starting: Spanish Configuration Nulls M=1000..."
nohup python code/analysis/07_structural_nulls_single_lang.py \
  --language spanish \
  --null-type configuration \
  --edge-file data/processed/spanish_edges_FINAL.csv \
  --output-dir results/final_validation \
  --M 1000 \
  --alpha 0.5 \
  --seed 42 \
  > logs/final_validation/spanish_config_M1000.log 2>&1 &

SPANISH_PID=$!
echo "   PID: $SPANISH_PID"
sleep 3

# JOB 2: English Configuration Nulls M=1000
echo "🚀 Starting: English Configuration Nulls M=1000..."
nohup python code/analysis/07_structural_nulls_single_lang.py \
  --language english \
  --null-type configuration \
  --edge-file data/processed/english_edges_FINAL.csv \
  --output-dir results/final_validation \
  --M 1000 \
  --alpha 0.5 \
  --seed 43 \
  > logs/final_validation/english_config_M1000.log 2>&1 &

ENGLISH_PID=$!
echo "   PID: $ENGLISH_PID"
sleep 3

# JOB 3: Chinese Configuration Nulls M=1000
echo "🚀 Starting: Chinese Configuration Nulls M=1000..."
nohup python code/analysis/07_structural_nulls_single_lang.py \
  --language chinese \
  --null-type configuration \
  --edge-file data/processed/chinese_edges_FINAL.csv \
  --output-dir results/final_validation \
  --M 1000 \
  --alpha 0.5 \
  --seed 44 \
  > logs/final_validation/chinese_config_M1000.log 2>&1 &

CHINESE_PID=$!
echo "   PID: $CHINESE_PID"
sleep 3

echo ""
echo "=================================================================="
echo "✅ CONFIG NULLS STARTED (3 jobs paralelos)"
echo "=================================================================="
echo ""
echo "PIDs: $SPANISH_PID (spanish), $ENGLISH_PID (english), $CHINESE_PID (chinese)"
echo ""
echo "Monitor:"
echo "  tail -f logs/final_validation/spanish_config_M1000.log"
echo ""
echo "Check progress:"
echo "  grep 'it/s' logs/final_validation/*.log | tail -3"
echo ""
echo "Kill all:"
echo "  kill $SPANISH_PID $ENGLISH_PID $CHINESE_PID"
echo ""
echo "=================================================================="
echo ""
echo "⏰ Estes jobs vão rodar por 15-20 HORAS"
echo "   Você pode fechar o terminal (nohup mantém rodando)"
echo "   Verificar progresso amanhã: grep 'configuration:' logs/final_validation/*.log"
echo ""
echo "=================================================================="

