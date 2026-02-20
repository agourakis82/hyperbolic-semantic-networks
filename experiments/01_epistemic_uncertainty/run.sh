#!/usr/bin/env bash
# Run the Sounio phase transition experiment
# Usage: bash experiments/01_epistemic_uncertainty/run.sh [--rebuild]
#
# Outputs results to:
#   results/sounio/phase_transition_sounio.csv  (data)
#   results/sounio/phase_transition_sounio.log  (build log)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SOUNIO_DIR="${HOME}/work/sounio"
SOUC="${SOUNIO_DIR}/target/release/souc"
EXPERIMENT="${SCRIPT_DIR}/phase_transition.sio"
RESULTS_DIR="${REPO_DIR}/results/sounio"
OUTPUT_CSV="${RESULTS_DIR}/phase_transition_sounio.csv"
BUILD_LOG="${RESULTS_DIR}/phase_transition_sounio.log"

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
echo

start_time=$(date +%s)
# SOUNIO_SELFHOST_DRIVER_REQUIRE_OUTPUT=0 disables the release-mode check
# that requires a TTY when piping stdout. Diagnostics go to log; CSV to stdout.
SOUNIO_SELFHOST_DRIVER_REQUIRE_OUTPUT=0 \
    "${SOUC}" run "${EXPERIMENT}" 2>"${BUILD_LOG}" | tee "${OUTPUT_CSV}"
end_time=$(date +%s)

echo
echo "[run.sh] Done in $((end_time - start_time)) seconds."
echo "[run.sh] Results: ${OUTPUT_CSV}"

# ── Quick summary ──────────────────────────────────────────────────────────
# Columns: N,k,ratio,kappa_mean,kappa_std,std_err_mean,n_edges,pred,obs
#          $1 $2    $3         $4        $5           $6      $7   $8  $9

echo
echo "=== Quick validation (compare to Julia reference) ==="
echo "Julia reference (N=200): k=3→κ≈-0.303  k=22→κ≈-0.013  k=40→κ≈+0.073"
echo "Sounio results (N=20, k_crit≈7.07):"
grep -v '^#' "${OUTPUT_CSV}" | grep -v '^N,' | awk -F',' '
  $2 == "3"  { printf "  k=3  ratio=%.4f kappa=%+.6f pred=%s obs=%s\n", $3, $4, $8, $9 }
  $2 == "7"  { printf "  k=7  ratio=%.4f kappa=%+.6f pred=%s obs=%s\n", $3, $4, $8, $9 }
  $2 == "14" { printf "  k=14 ratio=%.4f kappa=%+.6f pred=%s obs=%s\n", $3, $4, $8, $9 }
' || true

echo
echo "Legend: pred/obs: 0=Hyperbolic 1=Euclidean 2=Spherical"
echo "Expected: k=3→Hyperbolic (κ<-0.05), k≈7→Transition, k=14→Spherical (κ>+0.05)"
