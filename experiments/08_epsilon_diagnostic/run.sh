#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

SOUC="${HOME}/work/sounio/target/release/souc"
if [ ! -x "$SOUC" ]; then
    echo "[run.sh] ERROR: souc not found at $SOUC"
    exit 1
fi

OUTDIR="results/sounio"
mkdir -p "$OUTDIR"

echo "[run.sh] === Epsilon Diagnostic (N=20) ==="
echo "[run.sh] Sweeping epsilon={0.5, 0.1, 0.05, 0.01} at k={3, 7, 10, 14, 18}"

SECONDS=0
export SOUNIO_SELFHOST_DRIVER_REQUIRE_OUTPUT=0
"$SOUC" run experiments/08_epsilon_diagnostic/epsilon_diagnostic.sio \
    | tee "$OUTDIR/epsilon_diagnostic.csv"

echo ""
echo "[run.sh] Done in $SECONDS seconds."
echo "[run.sh] Results: $OUTDIR/epsilon_diagnostic.csv"
