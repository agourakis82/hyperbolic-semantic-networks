"""Run the CPC 2026 network-geometry claim audit through a Sounio spine."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys

from common import CPC_RESULTS_DIR, REPO_ROOT, ensure_directory, load_json, save_json


SOUNIO_CLAIM_SOURCE = REPO_ROOT / "experiments" / "sounio_cpc2026" / "depression_orc_claim.sio"
PYTHON_GATE_JSON = CPC_RESULTS_DIR / "depression_orc_network_geometry_scope_gate.json"
OUT_JSON = CPC_RESULTS_DIR / "sounio_depression_orc_claim_gate.json"


def resolve_souc() -> Path:
    env = os.environ.get("SOUC")
    candidates = []
    if env:
        candidates.append(Path(env))
    candidates.extend(
        [
            REPO_ROOT / "bin" / "souc",
            Path("/workspace/sounio/bin/souc"),
            Path("/usr/local/bin/souc"),
        ]
    )
    for path in candidates:
        if path.is_file() and os.access(path, os.X_OK):
            return path
    raise FileNotFoundError(
        "Could not find Sounio compiler. Set SOUC=/path/to/souc or mount /workspace/sounio/bin/souc."
    )


def git_commit_hash() -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else "unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-json", default=str(OUT_JSON))
    parser.add_argument("--souc", default="")
    args = parser.parse_args()

    out_json = Path(args.out_json)

    py_gate = subprocess.run(
        [sys.executable, str(REPO_ROOT / "code" / "cpc2026" / "network_geometry_claim_gate.py")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if py_gate.returncode != 0:
        print(py_gate.stdout, end="")
        print(py_gate.stderr, end="", file=sys.stderr)
        return py_gate.returncode

    souc = Path(args.souc) if args.souc else resolve_souc()
    proc = subprocess.run(
        [str(souc), "run", str(SOUNIO_CLAIM_SOURCE.relative_to(REPO_ROOT))],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    stdout = proc.stdout
    python_report = load_json(PYTHON_GATE_JSON)
    required_tokens = [
        "SOUNIO_CPC2026_NETWORK_GEOMETRY_CLAIM_PASS",
        "claim_level=exploratory_network_geometry_scope_gate",
        "context_of_use=exploratory_research_only",
        "target_external_cohort=TBD",
        "biomarker_candidate_language=false",
        "diagnostic_language=false",
        "clinical_utility=false",
        "patient_level_prediction=false",
        "requires_external_validation=true",
    ]
    missing = [token for token in required_tokens if token not in stdout]
    status = "PASS_SOUNIO_CLAIM_SPINE_READY"
    reasons: list[str] = []
    if proc.returncode != 0:
        status = "FAIL"
        reasons.append("sounio_run_failed")
    if missing:
        status = "FAIL"
        reasons.append("sounio_required_tokens_missing")
    if python_report.get("status") != "PASS_EXPLORATORY_NETWORK_GEOMETRY_SCOPE_GATE_ONLY":
        status = "FAIL"
        reasons.append("python_network_geometry_scope_gate_not_pass")

    report = {
        "schema": "cpc2026.sounio_depression_orc_claim_gate.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit_hash": git_commit_hash(),
        "status": status,
        "reasons": reasons,
        "souc": str(souc),
        "sounio_source": str(SOUNIO_CLAIM_SOURCE.relative_to(REPO_ROOT)),
        "python_gate": str(PYTHON_GATE_JSON.relative_to(REPO_ROOT)),
        "python_gate_status": python_report.get("status"),
        "claim_level": "exploratory_network_geometry_scope_gate",
        "context_of_use": python_report.get("context_of_use"),
        "target_external_cohort": python_report.get("target_external_cohort"),
        "monotonicity_assumption": python_report.get("monotonicity_assumption"),
        "preregistered_margins": python_report.get("preregistered_margins"),
        "sounio_returncode": proc.returncode,
        "sounio_stdout": stdout.splitlines(),
        "sounio_stderr": proc.stderr.splitlines()[:32],
        "required_tokens": required_tokens,
        "missing_tokens": missing,
        "boundaries": [
            "sounio_spine_validates_claim_level_not_orc_recomputation",
            "exploratory_network_geometry_scope_gate_not_biomarker_candidate",
            "biomarker_candidate_language_false_until_context_of_use_validation",
            "diagnostic_language_false_until_external_validation",
            "clinical_utility_false_until_context_of_use_validation",
        ],
    }
    ensure_directory(out_json.parent)
    save_json(out_json, report)
    print(
        "sounio_claim_gate: "
        f"{status} source={SOUNIO_CLAIM_SOURCE.relative_to(REPO_ROOT)} out={out_json}"
    )
    return 0 if status == "PASS_SOUNIO_CLAIM_SPINE_READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
