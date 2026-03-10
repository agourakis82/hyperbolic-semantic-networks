#!/usr/bin/env bash
# run.sh — Phase 7: Deep Hypercomplex ORC (d=32, 64) orchestrator
#
# Usage:
#   bash experiments/07_deep_hypercomplex/run.sh [target]
#
# Targets:
#   test_epsilon_d32          — epsilon sensitivity diagnostic for d=32
#   hypercomplex_orc_d32      — k-regular N=100 sweep at d=32
#   hypercomplex_orc_d64      — k-regular N=100 sweep at d=64
#   hypercomplex_semantic_d32 — 8 semantic networks at d=32
#
# Environment:
#   SOUC              — path to Sounio compiler (default: auto-detect)
#   SOUNIO_TIMEOUT    — optional timeout in seconds

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Auto-detect Sounio compiler (same as Phase 6)
if [[ -z "${SOUC:-}" ]]; then
    if [[ -f "${HOME}/work/sounio-lang/artifacts/omega/souc-bin/souc-linux-x86_64-gpu" ]]; then
        SOUC="${HOME}/work/sounio-lang/artifacts/omega/souc-bin/souc-linux-x86_64-gpu"
    elif [[ -f "${HOME}/work/sounio/artifacts/omega/souc-bin/souc-linux-x86_64" ]]; then
        SOUC="${HOME}/work/sounio/artifacts/omega/souc-bin/souc-linux-x86_64"
    else
        echo "ERROR: Sounio compiler not found. Set SOUC env var." >&2
        exit 1
    fi
fi

echo "=== Phase 7: Deep Hypercomplex ORC (d=32, 64) ==="
echo "Compiler: ${SOUC}"
echo "Working dir: ${SCRIPT_DIR}"
echo ""

TARGET="${1:-test_epsilon_d32}"
SIO_FILE="${SCRIPT_DIR}/${TARGET}.sio"

if [[ ! -f "${SIO_FILE}" ]]; then
    echo "ERROR: ${SIO_FILE} not found" >&2
    echo "Available targets:" >&2
    ls "${SCRIPT_DIR}"/*.sio 2>/dev/null | sed 's|.*/||;s|\.sio$||' | sed 's/^/  /' >&2
    exit 1
fi

mkdir -p "${REPO_ROOT}/results/experiments"

echo "Running: ${TARGET}.sio"
echo "---"

if [[ -n "${SOUNIO_TIMEOUT:-}" ]]; then
    timeout "${SOUNIO_TIMEOUT}" "${SOUC}" run "${SIO_FILE}" 2>&1
else
    "${SOUC}" run "${SIO_FILE}" 2>&1
fi

echo ""
echo "=== Phase 7 complete ==="
