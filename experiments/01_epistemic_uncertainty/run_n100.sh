#!/usr/bin/env bash
# Run the Sounio N=100 validation experiment
# Usage: bash experiments/01_epistemic_uncertainty/run_n100.sh
#
# Validates against Julia reference values (N=200):
#   k=3  → κ ≈ -0.303
#   k=22 → κ ≈ -0.013
#   k=40 → κ ≈ +0.073

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SOUNIO_DIR="${HOME}/work/sounio"
SOUC="${SOUNIO_DIR}/target/release/souc"
EXPERIMENT="${SCRIPT_DIR}/phase_transition_n100.sio"
RESULTS_DIR="${REPO_DIR}/results/sounio"
OUTPUT_CSV="${RESULTS_DIR}/phase_transition_n100.csv"
BUILD_LOG="${RESULTS_DIR}/phase_transition_n100.log"

# ── Verify compiler ────────────────────────────────────────────────────────

if [[ ! -f "${SOUC}" ]]; then
    echo "[run_n100.sh] ERROR: Sounio compiler not found at ${SOUC}"
    echo "[run_n100.sh] Build it with: cd ${SOUNIO_DIR} && cargo build -p souc --release"
    exit 1
fi

echo "[run_n100.sh] Using compiler: ${SOUC}"

# ── Results directory ──────────────────────────────────────────────────────

mkdir -p "${RESULTS_DIR}"

# ── Run experiment ─────────────────────────────────────────────────────────

echo "[run_n100.sh] Running: ${EXPERIMENT}"
echo "[run_n100.sh] Output : ${OUTPUT_CSV}"
echo "[run_n100.sh] WARNING: N=100 will take significantly longer than N=20 (~5-10 minutes)"
echo

start_time=$(date +%s)
SOUNIO_SELFHOST_DRIVER_REQUIRE_OUTPUT=0 \
    "${SOUC}" run "${EXPERIMENT}" 2>"${BUILD_LOG}" | tee "${OUTPUT_CSV}"
end_time=$(date +%s)

echo
echo "[run_n100.sh] Done in $((end_time - start_time)) seconds."
echo "[run_n100.sh] Results: ${OUTPUT_CSV}"

# ── Validation against Julia reference ────────────────────────────────────

echo
echo "=== Validation against Julia reference (N=200) ==="
echo "Julia reference: k=3→κ≈-0.303  k=22→κ≈-0.013  k=40→κ≈+0.073"
echo "Sounio results (N=100):"
grep -v '^#' "${OUTPUT_CSV}" | grep -v '^N,' | awk -F',' '
  $2 == "3"  { printf "  k=3  ratio=%.4f kappa=%+.6f (Julia: -0.303, diff: %+.3f)\n", $3, $4, $4 + 0.303 }
  $2 == "20" { printf "  k=20 ratio=%.4f kappa=%+.6f (Julia k=22: -0.013, approx)\n", $3, $4 }
  $2 == "40" { printf "  k=40 ratio=%.4f kappa=%+.6f (Julia: +0.073, diff: %+.3f)\n", $3, $4, $4 - 0.073 }
' || true

echo
echo "Expected behavior:"
echo "  - k=3  should be strongly negative (hyperbolic), close to -0.303"
echo "  - k=20 should be near zero (transition zone)"
echo "  - k=40 should be positive (spherical), close to +0.073"
echo
echo "Acceptable tolerance: ±0.05 (5% difference due to N=100 vs N=200)"

