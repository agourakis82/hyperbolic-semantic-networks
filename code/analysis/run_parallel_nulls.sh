#!/bin/bash
# Run Structural Null Analysis in Parallel (8 processes)
# 4 languages × 2 null types = 8 parallel jobs

set -e

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DATA_DIR="${SCRIPT_DIR}/../../data/processed"
OUTPUT_DIR="${SCRIPT_DIR}/../../results/structural_nulls"
LOG_DIR="/tmp/structural_nulls_logs"

mkdir -p "${OUTPUT_DIR}" "${LOG_DIR}"

echo "═══════════════════════════════════════════════════════════════"
echo "🚀 STRUCTURAL NULL ANALYSIS - PARALLEL EXECUTION"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📊 Configuration:"
echo "   - Languages: Spanish, English, Dutch, Chinese"
echo "   - Null types: Configuration, Triadic"
echo "   - Total jobs: 8 (running in parallel)"
echo "   - Replicates per job: M=1000"
echo "   - Alpha (idleness): 0.5"
echo ""
echo "⏰ Estimated time: 2-4 hours (with 8-core parallelization)"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Array of jobs (language, null_type, seed)
declare -a JOBS=(
    "spanish configuration 123"
    "spanish triadic 124"
    "english configuration 125"
    "english triadic 126"
    "dutch configuration 127"
    "dutch triadic 128"
    "chinese configuration 129"
    "chinese triadic 130"
)

# Launch all jobs in background
PIDS=()
for job in "${JOBS[@]}"; do
    read -r lang null_type seed <<< "${job}"
    
    edge_file="${DATA_DIR}/${lang}_edges.csv"
    log_file="${LOG_DIR}/${lang}_${null_type}.log"
    
    echo "🚀 Launching: ${lang} - ${null_type} (seed=${seed})"
    
    python3 "${SCRIPT_DIR}/07_structural_nulls_single_lang.py" \
        --language "${lang}" \
        --null-type "${null_type}" \
        --edge-file "${edge_file}" \
        --output-dir "${OUTPUT_DIR}" \
        --M 1000 \
        --alpha 0.5 \
        --seed "${seed}" \
        > "${log_file}" 2>&1 &
    
    PIDS+=($!)
    echo "   → PID: ${!}, Log: ${log_file}"
done

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ All 8 jobs launched!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "PIDs: ${PIDS[@]}"
echo ""
echo "📝 Monitor logs:"
echo "   tail -f ${LOG_DIR}/*.log"
echo ""
echo "📊 Check progress:"
echo "   watch -n 30 'ls -lh ${OUTPUT_DIR}/*.json'"
echo ""
echo "⏳ Waiting for all jobs to complete..."
echo ""

# Wait for all jobs and track completion
COMPLETED=0
TOTAL=${#PIDS[@]}

while [ ${COMPLETED} -lt ${TOTAL} ]; do
    sleep 60  # Check every minute
    
    COMPLETED=0
    for pid in "${PIDS[@]}"; do
        if ! ps -p ${pid} > /dev/null 2>&1; then
            ((COMPLETED++))
        fi
    done
    
    echo "⏰ $(date '+%H:%M:%S') - Progress: ${COMPLETED}/${TOTAL} jobs completed"
    
    # Show brief status from logs
    echo "   Recent activity:"
    for job in "${JOBS[@]}"; do
        read -r lang null_type _ <<< "${job}"
        log_file="${LOG_DIR}/${lang}_${null_type}.log"
        
        if [ -f "${log_file}" ]; then
            last_line=$(tail -n 1 "${log_file}" 2>/dev/null | grep -oP '(\d+/\d+)' || echo "initializing...")
            echo "      ${lang}-${null_type}: ${last_line}"
        fi
    done
    echo ""
done

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ ALL JOBS COMPLETED!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📊 Results:"
ls -lh "${OUTPUT_DIR}"/*.json
echo ""
echo "📈 Summary:"
for job in "${JOBS[@]}"; do
    read -r lang null_type _ <<< "${job}"
    result_file="${OUTPUT_DIR}/${lang}_${null_type}_nulls.json"
    
    if [ -f "${result_file}" ]; then
        echo "   ${lang}-${null_type}:"
        cat "${result_file}" | jq -r '"      Δκ = \(.delta_kappa), p_MC = \(.p_MC), Cliff δ = \(.cliff_delta)"'
    else
        echo "   ${lang}-${null_type}: ⚠️  FAILED (check log: ${LOG_DIR}/${lang}_${null_type}.log)"
    fi
done
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🎉 ANALYSIS COMPLETE!"
echo "═══════════════════════════════════════════════════════════════"

