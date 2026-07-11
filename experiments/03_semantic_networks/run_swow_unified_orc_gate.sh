#!/usr/bin/env bash
# Gate: Sounio SWOW unified ORC must match Julia exact-LP reference per language.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOUC_DEFAULT="/workspace/sounio/scripts/ci/souc-native-wrapper.sh"
if [[ -n "${SOUNIO_SOUC_BIN:-}" ]]; then
  SOUC="$SOUNIO_SOUC_BIN"
elif [[ -n "${SOUC:-}" && -x "${SOUC}" ]]; then
  SOUC="$SOUC"
elif [[ -x "$SOUC_DEFAULT" ]]; then
  SOUC="$SOUC_DEFAULT"
else
  echo "error: set SOUNIO_SOUC_BIN to souc-native-wrapper.sh" >&2
  exit 1
fi
OUT_DIR="$ROOT/results/sounio"
mkdir -p "$OUT_DIR"

cd "$ROOT"

LOG="$OUT_DIR/swow_unified_orc_gate.log"
echo "=== swow_unified_orc gate $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" | tee "$LOG"
echo "souc=$SOUC" | tee -a "$LOG"

if ! "$SOUC" run experiments/03_semantic_networks/swow_unified_orc.sio >"$OUT_DIR/swow_unified_orc.out" 2>&1; then
  echo "compile/run failed" | tee -a "$LOG"
  tail -40 "$OUT_DIR/swow_unified_orc.out" | tee -a "$LOG"
  exit 1
fi

cat "$OUT_DIR/swow_unified_orc.out" | tee -a "$LOG"

if ! grep -q 'SWOW_UNIFIED_ORC_PASS' "$OUT_DIR/swow_unified_orc.out"; then
  echo "FAIL: parity token missing" | tee -a "$LOG"
  exit 1
fi

python3 << 'PY' | tee -a "$LOG"
import json, re, pathlib
root = pathlib.Path("/workspace/hyperbolic-semantic-networks")
out = (root / "results/sounio/swow_unified_orc.out").read_text()
langs = ["en", "es", "zh", "nl"]
artifact = {
    "experiment": "swow_unified_orc_sounio",
    "solver": "sinkhorn_lse",
    "alpha": 0.5,
    "epsilon": 0.01,
    "max_iter": 1000,
    "graph": "largest_connected_component",
    "parity_tol": 0.0005,
    "reference_dir": "results/unified",
    "networks": {},
}
for lang in langs:
    ref = json.load(open(root / f"results/unified/swow_{lang}_exact_lp.json"))
    m = re.search(
        rf"swow_{lang}:.*?N=(\d+)\s+E=(\d+).*?kappa_u6=(-?\d+)\s+ref_u6=(-?\d+)\s+delta_u6=(-?\d+)",
        out,
        re.S,
    )
    if not m:
        raise SystemExit(f"missing output block for swow_{lang}")
    n, e, kappa_u6, ref_u6, delta_u6 = m.groups()
    kappa = int(kappa_u6) / 1_000_000.0
    ref_k = int(ref_u6) / 1_000_000.0
    delta = int(delta_u6) / 1_000_000.0
    artifact["networks"][f"swow_{lang}"] = {
        "N": int(n),
        "E": int(e),
        "kappa_mean_sounio": float(kappa),
        "kappa_mean_ref_lp": float(ref_k),
        "delta": float(delta),
        "ref_N": ref["N"],
        "ref_E": ref["E"],
        "N_match": int(n) == ref["N"],
        "E_match": int(e) == ref["E"],
        "parity_ok": abs(float(delta)) <= artifact["parity_tol"],
    }

out_path = root / "results/sounio/swow_unified_orc_parity.json"
out_path.write_text(json.dumps(artifact, indent=2) + "\n")
print(f"artifact={out_path}")
for lang in langs:
    row = artifact["networks"][f"swow_{lang}"]
    print(
        f"  swow_{lang}: kappa={row['kappa_mean_sounio']:+.6f} "
        f"ref={row['kappa_mean_ref_lp']:+.6f} delta={row['delta']:+.6f} "
        f"N={row['N']}/{row['ref_N']} E={row['E']}/{row['ref_E']}"
    )
if not all(r["parity_ok"] and r["N_match"] and r["E_match"] for r in artifact["networks"].values()):
    raise SystemExit("numeric parity check failed")
print("swow_unified_orc_gate: PASS")
PY

echo "swow_unified_orc_gate: PASS" | tee -a "$LOG"
