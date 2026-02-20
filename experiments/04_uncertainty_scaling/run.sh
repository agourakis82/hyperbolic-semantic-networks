#!/usr/bin/env bash
# Run the Uncertainty Scaling experiment
# Usage: bash experiments/04_uncertainty_scaling/run.sh [--rebuild]
#
# Outputs:
#   results/sounio/uncertainty_scaling.csv  (data)
#   results/sounio/uncertainty_scaling.log  (build log)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SOUNIO_DIR="${HOME}/work/sounio"
SOUC="${SOUNIO_DIR}/target/release/souc"
EXPERIMENT="${SCRIPT_DIR}/uncertainty_scaling.sio"
RESULTS_DIR="${REPO_DIR}/results/sounio"
OUTPUT_CSV="${RESULTS_DIR}/uncertainty_scaling.csv"
BUILD_LOG="${RESULTS_DIR}/uncertainty_scaling.log"

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
echo "[run.sh] Uncertainty analysis: 5 seeds x 11 k-values = 55 computations"
echo

start_time=$(date +%s)
SOUNIO_SELFHOST_DRIVER_REQUIRE_OUTPUT=0 \
    "${SOUC}" run "${EXPERIMENT}" 2>"${BUILD_LOG}" | tee "${OUTPUT_CSV}"
end_time=$(date +%s)

echo
echo "[run.sh] Done in $((end_time - start_time)) seconds."
echo "[run.sh] Results: ${OUTPUT_CSV}"

# ── Uncertainty summary ──────────────────────────────────────────────────

echo
echo "=== Uncertainty Scaling Summary ==="
grep -v '^#' "${OUTPUT_CSV}" | grep -v '^N,' | awk -F',' '
{
    region = ($3 < 2.0) ? "Hyp " : ($3 > 3.5) ? "Sph " : "Trans"
    printf "  k=%-2s  ratio=%5.2f  [%s]  kappa=%+.4f  intra_std=%.4f  inter_std=%.6f  H=%.3f bits\n",
           $2, $3, region, $4, $5, $6, $10
}' || true

echo
echo "Expected: H=0 at extremes (all seeds agree), H>0 near transition (disagreement)"
echo "Expected: inter_std peaks near k_crit ≈ 7.07 (k^2/N ≈ 2.5)"
