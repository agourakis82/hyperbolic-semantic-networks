#!/usr/bin/env bash
# run.sh — Phase 2 epistemic ORC experiment runner
#
# Usage:
#   bash experiments/02_exact_w1/run.sh
#
# Output:
#   logs/02_exact_w1.log   (stderr)
#   stdout: EpistemicKappa results for K4, n=20, n=100 k=14, n=100 k=16
#
# Note: Tests 3 and 4 (N=100) are slow on the interpreter.
#   Run on gpu-appliance-l4 for reasonable throughput:
#   ssh gpu-appliance-l4 "bash ~/work/hyperbolic-semantic-networks/experiments/02_exact_w1/run.sh"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SOUNIO_DIR="${HOME}/work/sounio-lang"
SOUC="${SOUNIO_DIR}/artifacts/omega/souc-bin/souc-linux-x86_64-gpu"
LOG_DIR="${REPO_DIR}/logs"

if [[ ! -x "${SOUC}" ]]; then
    echo "ERROR: souc not found at ${SOUC}" >&2
    echo "Clone the compiler: git clone https://github.com/sounio-lang/sounio ${SOUNIO_DIR}" >&2
    exit 1
fi

mkdir -p "${LOG_DIR}"
LOG_FILE="${LOG_DIR}/02_exact_w1.log"
SIO="${SCRIPT_DIR}/epistemic_orc.sio"

echo "souc: ${SOUC}"
"${SOUC}" --version
echo "Running: ${SIO}"
echo ""

"${SOUC}" run "${SIO}" 2>"${LOG_FILE}"
echo ""
echo "Log: ${LOG_FILE}"
