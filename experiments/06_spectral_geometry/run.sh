#!/usr/bin/env bash
# Run the Spectral Geometry experiment
# Usage: bash experiments/06_spectral_geometry/run.sh [--rebuild]
#
# Outputs:
#   results/sounio/spectral_phase_transition.csv  (data)
#   results/sounio/spectral_phase_transition.log  (build log)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SOUNIO_DIR="${HOME}/work/sounio"
SOUC="${SOUNIO_DIR}/target/release/souc"
EXPERIMENT="${SCRIPT_DIR}/spectral_phase_transition.sio"
RESULTS_DIR="${REPO_DIR}/results/sounio"
OUTPUT_CSV="${RESULTS_DIR}/spectral_phase_transition.csv"
BUILD_LOG="${RESULTS_DIR}/spectral_phase_transition.log"

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
echo "[run.sh] Phase A: N=20, 11 k-values, spectral + curvature"
echo "[run.sh] Phase B: N=50, 8 k-values, spectral only"
echo

start_time=$(date +%s)
SOUNIO_SELFHOST_DRIVER_REQUIRE_OUTPUT=0 \
    "${SOUC}" run "${EXPERIMENT}" 2>"${BUILD_LOG}" | tee "${OUTPUT_CSV}"
end_time=$(date +%s)

echo
echo "[run.sh] Done in $((end_time - start_time)) seconds."
echo "[run.sh] Results: ${OUTPUT_CSV}"

# ── Summary ────────────────────────────────────────────────────────────────

echo
echo "=== Spectral Geometry Summary ==="
grep -v '^#' "${OUTPUT_CSV}" | grep -v '^N,' | grep -v '^$' | awk -F',' '
{
    region = ($3 < 2.0) ? "Hyp " : ($3 > 3.5) ? "Sph " : "Trns"
    printf "  N=%-2s k=%-2s ratio=%5.2f [%s]  lambda2=%6.3f  gap/k=%.3f  friedman=%.3f  kappa=%+.4f\n",
           $1, $2, $3, region, $4, $6, $9, $12
}' || true

echo
echo "Expected: norm_gap increases monotonically with k (more connected = larger gap)"
echo "Expected: Friedman ratio near 1.0 for k >= 3 (validates random regular model)"
echo "Expected: Phase transition visible in both spectral gap and curvature at k^2/N = 2.5"
