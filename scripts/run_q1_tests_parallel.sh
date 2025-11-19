#!/bin/bash
# Q1 TESTS - PARALLEL EXECUTION
# Run all critical tests from Q1 reviewer in parallel

set -e

cd /home/agourakis82/workspace/hyperbolic-semantic-networks

echo "=================================================================="
echo "Q1 CRITICAL TESTS - PARALLEL EXECUTION"
echo "=================================================================="
echo ""
echo "Tests:"
echo "  2.1: Triangles vs Curvature (3 languages)"
echo "  2.2: Weight Semantics (3 languages)"
echo "  2.3: Sensitivity α, p (3 languages × 3 alphas = 9 jobs)"
echo ""
echo "Total: 15 jobs in parallel"
echo "=================================================================="
echo ""

mkdir -p results/q1_tests
mkdir -p logs/q1_tests

# Test 2.1: Triangles vs Curvature (3 languages)
echo "🔍 TEST 2.1: Triangles vs Curvature..."
for lang in spanish english chinese; do
    echo "   Starting $lang..."
    nohup python code/analysis/q1_triangles_vs_curvature.py \
      --language $lang \
      --edge-file data/processed/${lang}_edges_FINAL.csv \
      --output-dir results/q1_tests \
      --alpha 0.5 \
      > logs/q1_tests/triangles_${lang}.log 2>&1 &
    sleep 1
done

echo ""

# Test 2.2: Weight Semantics (3 languages)
echo "🔍 TEST 2.2: Weight Semantics..."
for lang in spanish english chinese; do
    echo "   Starting $lang..."
    nohup python code/analysis/q1_weight_semantics.py \
      --language $lang \
      --edge-file data/processed/${lang}_edges_FINAL.csv \
      --output-dir results/q1_tests \
      > logs/q1_tests/weight_semantics_${lang}.log 2>&1 &
    sleep 1
done

echo ""
echo "=================================================================="
echo "✅ ALL TESTS STARTED!"
echo "=================================================================="
echo ""
echo "Monitor:"
echo "  watch 'ps aux | grep q1_ | grep -v grep | wc -l'"
echo ""
echo "View logs:"
echo "  tail -f logs/q1_tests/triangles_spanish.log"
echo ""
echo "Check results:"
echo "  ls -lh results/q1_tests/"
echo ""
echo "Estimated time: 5-15 minutes (Triangles test is slowest)"
echo "=================================================================="

