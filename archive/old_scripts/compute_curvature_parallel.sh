#!/bin/bash

echo "═══════════════════════════════════════════════════════════════"
echo "   PARALLEL CURVATURE COMPUTATION (2 datasets)"
echo "═══════════════════════════════════════════════════════════════"
echo ""

cd /home/agourakis82/workspace/hyperbolic-semantic-networks

# WordNet N=2000 (background)
echo "🔄 Starting WordNet N=2000 curvature..."
nohup python code/analysis/unified_dataset_analysis.py \
  --dataset wordnet_N2000 \
  --edge-file data/processed/wordnet_N2000_edges.csv \
  --output-dir results/multi_dataset \
  > logs/wordnet_N2000_curvature.log 2>&1 &
WN_PID=$!
echo "   WordNet PID: $WN_PID"

# ConceptNet (background)
echo "🔄 Starting ConceptNet curvature..."
nohup python code/analysis/unified_dataset_analysis.py \
  --dataset conceptnet \
  --edge-file data/processed/conceptnet_en_edges.csv \
  --output-dir results/multi_dataset \
  > logs/conceptnet_curvature.log 2>&1 &
CN_PID=$!
echo "   ConceptNet PID: $CN_PID"

echo ""
echo "✅ Both jobs launched in parallel!"
echo ""
echo "Monitor progress:"
echo "  tail -f logs/wordnet_N2000_curvature.log"
echo "  tail -f logs/conceptnet_curvature.log"
echo ""
echo "Estimated time:"
echo "  WordNet N=2000: ~2-3 hours"
echo "  ConceptNet: ~30-45 minutes"
echo ""

