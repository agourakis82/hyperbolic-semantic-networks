#!/usr/bin/env bash
# Run the Hypercomplex Curvature Embedding experiment
# Usage: bash experiments/05_hypercomplex/run.sh [--rebuild]
#
# Outputs:
#   results/sounio/hypercomplex_curvature.csv  (data)
#   results/sounio/hypercomplex_curvature.log  (build log)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SOUNIO_DIR="${HOME}/work/sounio"
SOUC="${SOUNIO_DIR}/target/release/souc"
EXPERIMENT="${SCRIPT_DIR}/hypercomplex_curvature.sio"
RESULTS_DIR="${REPO_DIR}/results/sounio"
OUTPUT_CSV="${RESULTS_DIR}/hypercomplex_curvature.csv"
BUILD_LOG="${RESULTS_DIR}/hypercomplex_curvature.log"

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
echo "[run.sh] Phase A: N=20, 11 k-values × 4 curvature methods (hop, S³, S⁷, S¹⁵)"
echo "[run.sh] Phase B: N=50, 8 k-values × 4 curvature methods"
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
echo "=== Hypercomplex Curvature Summary ==="
grep -v '^#' "${OUTPUT_CSV}" | grep -v '^N,' | awk -F',' '
{
    region = ($3 < 2.0) ? "Hyp " : ($3 > 3.5) ? "Sph " : "Trns"
    printf "  N=%-2s k=%-2s ratio=%5.2f [%s]  hop=%+.4f  quat=%+.4f  oct=%+.4f  sed=%+.4f\n",
           $1, $2, $3, region, $4, $5, $6, $7
}' || true

echo
echo "Expected: All methods detect phase transition (hop kappa crosses zero near k_crit)"
echo "Expected: Embedding curvatures track hop-count but with continuous (smoother) values"
