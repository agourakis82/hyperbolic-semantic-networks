#!/bin/bash
# RUN RICCI FLOW - PARALLEL EXECUTION (WSL)
# 6 jobs paralelos usando nohup

set -e

cd /home/agourakis82/workspace/hyperbolic-semantic-networks

echo "=================================================================="
echo "RICCI FLOW - PARALLEL EXECUTION (WSL)"
echo "=================================================================="
echo ""
echo "🎯 Running 6 jobs in parallel using nohup"
echo ""
echo "Jobs:"
echo "  1. Spanish Real"
echo "  2. Spanish Config"
echo "  3. English Real"
echo "  4. English Config"
echo "  5. Chinese Real"
echo "  6. Chinese Config"
echo ""
echo "⏱️  Tempo estimado: 12-24 horas (depende de convergência)"
echo ""
echo "=================================================================="
echo ""

# Create results directory
mkdir -p results/ricci_flow
mkdir -p logs/ricci_flow

# Job 1: Spanish Real
echo "🚀 Starting Job 1: Spanish Real..."
nohup python code/analysis/ricci_flow_real.py \
  --language spanish \
  --network-type real \
  --edge-file data/processed/spanish_edges_FINAL.csv \
  --output-dir results/ricci_flow \
  --iterations 200 \
  --step 0.5 \
  --alpha 0.5 \
  > logs/ricci_flow/spanish_real.log 2>&1 &

echo "   PID: $!"
SPANISH_REAL_PID=$!

sleep 2

# Job 2: Spanish Config
echo "🚀 Starting Job 2: Spanish Config..."
nohup python code/analysis/ricci_flow_real.py \
  --language spanish \
  --network-type config \
  --edge-file data/processed/spanish_edges_FINAL.csv \
  --output-dir results/ricci_flow \
  --iterations 200 \
  --step 0.5 \
  --alpha 0.5 \
  --seed 123 \
  > logs/ricci_flow/spanish_config.log 2>&1 &

echo "   PID: $!"
sleep 2

# Job 3: English Real
echo "🚀 Starting Job 3: English Real..."
nohup python code/analysis/ricci_flow_real.py \
  --language english \
  --network-type real \
  --edge-file data/processed/english_edges_FINAL.csv \
  --output-dir results/ricci_flow \
  --iterations 200 \
  --step 0.5 \
  --alpha 0.5 \
  > logs/ricci_flow/english_real.log 2>&1 &

echo "   PID: $!"
sleep 2

# Job 4: English Config
echo "🚀 Starting Job 4: English Config..."
nohup python code/analysis/ricci_flow_real.py \
  --language english \
  --network-type config \
  --edge-file data/processed/english_edges_FINAL.csv \
  --output-dir results/ricci_flow \
  --iterations 200 \
  --step 0.5 \
  --alpha 0.5 \
  --seed 456 \
  > logs/ricci_flow/english_config.log 2>&1 &

echo "   PID: $!"
sleep 2

# Job 5: Chinese Real
echo "🚀 Starting Job 5: Chinese Real..."
nohup python code/analysis/ricci_flow_real.py \
  --language chinese \
  --network-type real \
  --edge-file data/processed/chinese_edges_FINAL.csv \
  --output-dir results/ricci_flow \
  --iterations 200 \
  --step 0.5 \
  --alpha 0.5 \
  > logs/ricci_flow/chinese_real.log 2>&1 &

echo "   PID: $!"
sleep 2

# Job 6: Chinese Config
echo "🚀 Starting Job 6: Chinese Config..."
nohup python code/analysis/ricci_flow_real.py \
  --language chinese \
  --network-type config \
  --edge-file data/processed/chinese_edges_FINAL.csv \
  --output-dir results/ricci_flow \
  --iterations 200 \
  --step 0.5 \
  --alpha 0.5 \
  --seed 789 \
  > logs/ricci_flow/chinese_config.log 2>&1 &

echo "   PID: $!"
echo ""

echo "=================================================================="
echo "✅ ALL 6 JOBS STARTED!"
echo "=================================================================="
echo ""
echo "📁 Logs:"
echo "   tail -f logs/ricci_flow/spanish_real.log"
echo "   tail -f logs/ricci_flow/english_real.log"
echo "   tail -f logs/ricci_flow/chinese_real.log"
echo ""
echo "📊 Monitor all:"
echo "   watch 'ps aux | grep ricci_flow_real | grep -v grep'"
echo ""
echo "📈 Check results:"
echo "   ls -lh results/ricci_flow/"
echo ""
echo "⏹️  Kill all jobs:"
echo "   pkill -f ricci_flow_real"
echo ""
echo "=================================================================="

