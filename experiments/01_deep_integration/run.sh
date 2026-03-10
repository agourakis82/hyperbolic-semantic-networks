#!/usr/bin/env bash
# run.sh — Build and execute Phase 1 deep Sounio integration experiments
#
# Usage:
#   bash experiments/01_deep_integration/run.sh [EXPERIMENT]
#
# Arguments:
#   EXPERIMENT   One of: sparse_graph, bfs_dynamic, sinkhorn_adaptive,
#                        phase_transition_full (default)
#
# Output:
#   results/experiments/phase_transition_sounio_v1.csv  (phase transition data)
#   logs/01_deep_integration.log                        (stderr)
#
# Optional environment:
#   SOUNIO_TIMEOUT_SECONDS=240
#       Bound long-running sweeps while keeping partial CSV output.
#
# Compiler:
#   Uses /home/demetrios/work/sounio-lang/artifacts/omega/souc-bin/souc-linux-x86_64-gpu
#   (from the sounio-lang/sounio GitHub clone — stable beta.4 build)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SOUNIO_DIR="${HOME}/work/sounio-lang"
SOUC="${SOUNIO_DIR}/artifacts/omega/souc-bin/souc-linux-x86_64-gpu"
RESULTS_DIR="${REPO_DIR}/results/experiments"
LOG_DIR="${REPO_DIR}/logs"
EXPERIMENT="${1:-phase_transition_full}"

# ── Check compiler ──────────────────────────────────────────────────────────
if [[ ! -x "${SOUC}" ]]; then
    echo "ERROR: souc not found at ${SOUC}" >&2
    echo "Clone the compiler: git clone https://github.com/sounio-lang/sounio ${SOUNIO_DIR}" >&2
    exit 1
fi

echo "souc: ${SOUC}"
"${SOUC}" --version

# ── Prepare output dirs ──────────────────────────────────────────────────────
mkdir -p "${RESULTS_DIR}" "${LOG_DIR}"

# ── Select experiment file ───────────────────────────────────────────────────
case "${EXPERIMENT}" in
    sparse_graph)       SIO="${SCRIPT_DIR}/sparse_graph.sio" ;;
    bfs_dynamic)        SIO="${SCRIPT_DIR}/bfs_dynamic.sio" ;;
    sinkhorn_adaptive)  SIO="${SCRIPT_DIR}/sinkhorn_adaptive.sio" ;;
    phase_transition_full) SIO="${SCRIPT_DIR}/phase_transition_full.sio" ;;
    *)
        echo "ERROR: Unknown experiment '${EXPERIMENT}'" >&2
        echo "Valid: sparse_graph | bfs_dynamic | sinkhorn_adaptive | phase_transition_full" >&2
        exit 1
        ;;
esac

echo "Running: ${SIO}"

# ── Run ──────────────────────────────────────────────────────────────────────
OUTPUT_CSV="${RESULTS_DIR}/phase_transition_sounio_v1.csv"
LOG_FILE="${LOG_DIR}/01_deep_integration.log"
TIMEOUT_SECONDS="${SOUNIO_TIMEOUT_SECONDS:-}"

if [[ "${EXPERIMENT}" == "phase_transition_full" ]]; then
    echo "Writing CSV → ${OUTPUT_CSV}"
    if [[ -n "${TIMEOUT_SECONDS}" ]]; then
        echo "Bounding run with timeout ${TIMEOUT_SECONDS}s"
        timeout "${TIMEOUT_SECONDS}" "${SOUC}" run "${SIO}" 2>"${LOG_FILE}" | tee "${OUTPUT_CSV}"
    else
        "${SOUC}" run "${SIO}" 2>"${LOG_FILE}" | tee "${OUTPUT_CSV}"
    fi
    echo ""
    echo "Done. Results in: ${OUTPUT_CSV}"
    echo "Log: ${LOG_FILE}"
else
    # Validation experiments: print to stdout only
    "${SOUC}" run "${SIO}" 2>"${LOG_FILE}"
    echo ""
    echo "Log: ${LOG_FILE}"
fi
