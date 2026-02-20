#!/usr/bin/env bash
# Run the Configuration Null Model Ensemble experiment
# Usage: bash experiments/02_null_model/run.sh [--rebuild]
#
# Outputs:
#   results/sounio/configuration_null.csv  (data)
#   results/sounio/configuration_null.log  (build log)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SOUNIO_DIR="${HOME}/work/sounio"
SOUC="${SOUNIO_DIR}/target/release/souc"
EXPERIMENT="${SCRIPT_DIR}/configuration_null.sio"
RESULTS_DIR="${REPO_DIR}/results/sounio"
OUTPUT_CSV="${RESULTS_DIR}/configuration_null.csv"
BUILD_LOG="${RESULTS_DIR}/configuration_null.log"

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
echo "[run.sh] Null model ensemble: 5 seeds x 11 k-values = 55 computations"
echo

start_time=$(date +%s)
SOUNIO_SELFHOST_DRIVER_REQUIRE_OUTPUT=0 \
    "${SOUC}" run "${EXPERIMENT}" 2>"${BUILD_LOG}" | tee "${OUTPUT_CSV}"
end_time=$(date +%s)

echo
echo "[run.sh] Done in $((end_time - start_time)) seconds."
echo "[run.sh] Results: ${OUTPUT_CSV}"

# ── Ensemble summary ─────────────────────────────────────────────────────

echo
echo "=== Ensemble Summary (E rows) ==="
grep '^E,' "${OUTPUT_CSV}" | awk -F',' '
{
    printf "  k=%-2s  ratio=%5.2f  ensemble_mean=%+.6f  ensemble_std=%.6f  agreement=%.1f\n",
           $3, $5, $6, $7, $11
}' || true

echo
echo "Low ensemble_std → curvature is structurally invariant (degree-determined)"
echo "High agreement → phase transition prediction is robust across realizations"
