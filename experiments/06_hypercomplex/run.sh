#!/usr/bin/env bash
# run.sh — Phase 6 Hypercomplex ORC orchestrator
#
# Usage:
#   bash experiments/06_hypercomplex/run.sh [hypercomplex_orc|hypercomplex_semantic_orc]
#
# Environment:
#   SOUC           — path to Sounio compiler (default: auto-detect)
#   SOUNIO_TIMEOUT — optional timeout in seconds

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Auto-detect Sounio compiler
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

echo "=== Phase 6: Hypercomplex ORC ==="
echo "Compiler: ${SOUC}"
echo "Working dir: ${SCRIPT_DIR}"
echo ""

TARGET="${1:-hypercomplex_orc}"
SIO_FILE="${SCRIPT_DIR}/${TARGET}.sio"

if [[ ! -f "${SIO_FILE}" ]]; then
    echo "ERROR: ${SIO_FILE} not found" >&2
    echo "Available targets:" >&2
    ls "${SCRIPT_DIR}"/*.sio 2>/dev/null | sed 's|.*/||;s|\.sio$||' | sed 's/^/  /' >&2
    exit 1
fi

# Ensure results directory exists
mkdir -p "${REPO_ROOT}/results/experiments"

# Run with optional timeout
echo "Running: ${TARGET}.sio"
echo "---"

if [[ -n "${SOUNIO_TIMEOUT:-}" ]]; then
    timeout "${SOUNIO_TIMEOUT}" "${SOUC}" run "${SIO_FILE}" 2>&1
else
    "${SOUC}" run "${SIO_FILE}" 2>&1
fi

echo ""
echo "=== Phase 6 complete ==="
