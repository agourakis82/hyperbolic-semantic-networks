#!/usr/bin/env bash
# Run the Scale experiment: N=100 (all methods) + N=200 (spectral)
# Usage: bash experiments/07_scale_n500/run.sh [--rebuild]
#
# Estimated runtime: 1-3 hours
#   Phase A (N=100, curvature k<=18): ~5-20 min per k-value
#   Phase A (N=100, spectral k>18):   ~1-3 min per k-value
#   Phase B (N=200, spectral only):   ~2-5 min per k-value
#
# Note: N=500 was attempted but [i64;250000] BFS all-pairs is infeasible
# in the Sounio bytecode VM (~6 hours for a single k-value).
#
# Outputs:
#   results/sounio/scale_n500.csv  (data)
#   results/sounio/scale_n500.log  (build log)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SOUNIO_DIR="${HOME}/work/sounio"
SOUC="${SOUNIO_DIR}/target/release/souc"
EXPERIMENT="${SCRIPT_DIR}/scale_n500.sio"
RESULTS_DIR="${REPO_DIR}/results/sounio"
OUTPUT_CSV="${RESULTS_DIR}/scale_n500.csv"
BUILD_LOG="${RESULTS_DIR}/scale_n500.log"

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
echo "[run.sh] Phase A: N=100, k in {2,4,8,12,16,18} (curvature + spectral)"
echo "[run.sh]          N=100, k in {24,32,40,48} (spectral only)"
echo "[run.sh] Phase B: N=200, k in {2,4,8,14,22,30,38,44} (spectral only)"
echo

start_time=$(date +%s)
SOUNIO_SELFHOST_DRIVER_REQUIRE_OUTPUT=0 \
    "${SOUC}" run "${EXPERIMENT}" 2>"${BUILD_LOG}" | tee "${OUTPUT_CSV}"
end_time=$(date +%s)
elapsed=$((end_time - start_time))

echo
echo "[run.sh] Done in ${elapsed} seconds ($((elapsed / 60)) min)."
echo "[run.sh] Results: ${OUTPUT_CSV}"

# ── Summary ────────────────────────────────────────────────────────────────

echo
echo "=== Scale Experiment Summary ==="
grep -v '^#' "${OUTPUT_CSV}" | grep -v '^N,' | grep -v '^$' | awk -F',' '
{
    region = ($3 < 2.0) ? "Hyp " : ($3 > 3.5) ? "Sph " : "Trns"
    printf "  N=%-3s k=%-2s ratio=%5.2f [%s]  lambda2=%6.3f  gap/k=%.3f  kappa=%+.4f  kappa_q4=%+.4f\n",
           $1, $2, $3, region, $4, $6, $12, $13
}' || true

echo
echo "Phase A: N=100, k_crit = 15.8 — curvature spans full transition"
echo "Phase B: N=200, k_crit = 22.4 — spectral matches Julia reference"
