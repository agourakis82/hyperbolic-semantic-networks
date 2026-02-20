#!/usr/bin/env bash
# Run the Forman-Ricci vs Ollivier-Ricci Comparison experiment
# Usage: bash experiments/03_forman_ricci/run.sh [--rebuild]
#
# Outputs:
#   results/sounio/forman_comparison.csv  (data)
#   results/sounio/forman_comparison.log  (build log)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SOUNIO_DIR="${HOME}/work/sounio"
SOUC="${SOUNIO_DIR}/target/release/souc"
EXPERIMENT="${SCRIPT_DIR}/forman_comparison.sio"
RESULTS_DIR="${REPO_DIR}/results/sounio"
OUTPUT_CSV="${RESULTS_DIR}/forman_comparison.csv"
BUILD_LOG="${RESULTS_DIR}/forman_comparison.log"

# ── Build compiler ─────────────────────────────────────────────────────────

if [[ ! -f "${SOUC}" ]] || [[ "${1:-}" == "--rebuild" ]]; then
    echo "[run.sh] Building Sounio compiler (this may take a few minutes)..."
    (cd "${SOUNIO_DIR}" && cargo build -p souc --release) 2>&1 | tee "${BUILD_LOG}"
    echo "[run.sh] Compiler built: ${SOUC}"
else
    echo "[run.sh] Using existing compiler: ${SOUC}"
fi

# ── Results directory ──────────────────────────────────────────────────────

mkdir -p "${RESULTS_DIR}"

# ── Run experiment ─────────────────────────────────────────────────────────

echo "[run.sh] Running: ${EXPERIMENT}"
echo "[run.sh] Output : ${OUTPUT_CSV}"
echo "[run.sh] Comparing: Forman-Ricci (combinatorial) vs Ollivier-Ricci (optimal transport)"
echo

start_time=$(date +%s)
SOUNIO_SELFHOST_DRIVER_REQUIRE_OUTPUT=0 \
    "${SOUC}" run "${EXPERIMENT}" 2>"${BUILD_LOG}" | tee "${OUTPUT_CSV}"
end_time=$(date +%s)

echo
echo "[run.sh] Done in $((end_time - start_time)) seconds."
echo "[run.sh] Results: ${OUTPUT_CSV}"

# ── Comparison summary ────────────────────────────────────────────────────

echo
echo "=== Curvature Comparison ==="
grep -v '^#' "${OUTPUT_CSV}" | grep -v '^N,' | awk -F',' '
{
    f_sign = ($4 < -0.5) ? "Hyp" : ($4 > 0.5) ? "Sph" : "Euc"
    o_sign = ($6 < -0.05) ? "Hyp" : ($6 > 0.05) ? "Sph" : "Euc"
    agree = ($11 == 1) ? "YES" : "NO"
    printf "  k=%-2s  Forman=%+7.2f (%s)  Ollivier=%+.4f (%s)  agree=%s\n",
           $2, $4, f_sign, $6, o_sign, agree
}' || true
