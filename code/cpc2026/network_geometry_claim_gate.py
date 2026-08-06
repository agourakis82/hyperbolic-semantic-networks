"""Claim-discipline gate for CPC 2026 depression ORC network-geometry claims.

This gate intentionally does not validate a clinical biomarker, biomarker
candidate, or clinical context of use. It audits the existing CPC depression
ORC artifacts and emits a narrow, conference-safe claim: the current artifacts
support exploratory descriptive ORC / entropic-curvature summaries for
depression semantic-network characterization.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import re
from pathlib import Path
import subprocess
from statistics import mean

from common import (
    CLINICAL_DEPRESSION_SUMMARY_JSON,
    CPC_RESULTS_DIR,
    DEPRESSION_SEVERITIES,
    REPO_ROOT,
    RESULTS_DIR,
    ensure_directory,
    load_json,
    save_json,
)


OUT_JSON = CPC_RESULTS_DIR / "depression_orc_network_geometry_scope_gate.json"
OUT_MD = REPO_ROOT / "submission" / "cpc2026" / "depression_orc_network_geometry_claim.md"
EPISTEMIC_ORC_JSON = CPC_RESULTS_DIR / "depression_epistemic_orc.json"
CROSS_DOMAIN_JSON = CPC_RESULTS_DIR / "cross_domain_orc_summary.json"
KEC_CORRELATIONS_JSON = RESULTS_DIR / "depression_kec_correlations.json"

CLAIM_DOCS = (
    REPO_ROOT / "code" / "cpc2026" / "README.md",
    REPO_ROOT / "submission" / "cpc2026" / "README.md",
    OUT_MD,
)

FORBIDDEN_PATTERNS = (
    (r"\bvalidated clinical biomarker\b", "validated_clinical_biomarker"),
    (r"\bbiomarker-candidate\b", "biomarker_candidate_claim"),
    (r"\bdiagnostic biomarker\b", "diagnostic_biomarker"),
    (r"\bdiagnos(?:e|is|tic)\b", "diagnostic_claim"),
    (r"\bclinical utility\b", "clinical_utility_claim"),
    (r"\bpatient-level prediction\b", "patient_level_prediction_claim"),
)


def _severity_order(values: dict[str, float]) -> list[float]:
    return [float(values[sev]) for sev in DEPRESSION_SEVERITIES]


def _is_monotonic(xs: list[float]) -> bool:
    return all(a <= b for a, b in zip(xs, xs[1:])) or all(a >= b for a, b in zip(xs, xs[1:]))


def _fmt_float(value: float, digits: int = 4) -> str:
    return f"{value:.{digits}g}"


def _write_claim_markdown(report: dict) -> None:
    ensure_directory(OUT_MD.parent)
    per = report["per_severity"]
    evidence = report["evidence"]
    OUT_MD.write_text(
        "\n".join(
            [
                "# Depression Ollivier-Ricci Curvature Exploratory Network Geometry Scope Gate",
                "",
                "## Conference-Safe Claim",
                "",
                (
                    "This artifact is a repository-backed scope gate, not a clinical "
                    "or statistical results claim. It records that the current CPC "
                    "2026 Ollivier-Ricci curvature and entropic-curvature outputs are "
                    "graph-level exploratory aggregates and defines the next "
                    "falsification-oriented experiments."
                ),
                "",
                "## Executable Hooks",
                "",
                "- Python gate: `code/cpc2026/network_geometry_claim_gate.py`",
                "- Sounio spine: `experiments/sounio_cpc2026/depression_orc_claim.sio`",
                "- Integrated gate: `code/cpc2026/sounio_claim_gate.py`",
                "- Machine-readable status: `results/cpc2026/depression_orc_network_geometry_scope_gate.json` and `results/cpc2026/sounio_depression_orc_claim_gate.json`",
                "",
                "## Scope Observations",
                "",
                f"- Source groups are four severity-labelled semantic networks treated here as nominal graph labels: `{', '.join(sorted(DEPRESSION_SEVERITIES))}`",
                f"- Graph size by source group (`N` nodes, `E` edges): `{evidence['graph_size_by_group']}`",
                "- Numeric ORC/C_ent tables and bootstrap metadata remain in the machine-readable JSON artifacts.",
                "- This memo intentionally does not interpret ORC/C_ent intervals, contrasts, or signs as graph-construction, cohort, clinical, or patient-level uncertainty.",
                "- External-facing interpretation is blocked until null models, resampling units, and size controls are specified.",
                "",
                "## Required Boundaries",
                "",
                "- This is an exploratory network-geometry scope gate, not a biomarker-candidate claim or validated clinical biomarker.",
                "- This does not claim diagnosis, clinical utility, patient-level prediction, or treatment selection.",
                "- Severity labels are nominal graph labels in this memo; no monotonic severity trend is claimed.",
                "- Context of use: exploratory research and conference hypothesis generation, not clinical decision-making.",
                "- The observations are suitable for audit-trail bookkeeping and next-experiment design only.",
                "- External validation would require independent cohorts, preregistered endpoints, patient-level performance metrics, and a defined context of use.",
                "- Monotonicity assumption: not established; the current group means are non-monotonic and require formal trend testing before any ordered-severity claim.",
                "",
                "## Limitations",
                "",
                "- Target external cohort: TBD; no access agreement or validation cohort is claimed here. A future cohort must specify language, diagnostic ascertainment, age range, and comorbidity exclusions before confirmatory analysis.",
                "- No degree-preserving, permutation, or other null-model comparison is included in this artifact.",
                "- Negative ORC values are not interpreted against a meaningful semantic-graph null model in this memo.",
                "- Current ORC and C_ent summaries are graph-level aggregate metrics, not patient-level measurements.",
                "- Pairwise C_ent contrasts are recorded internally but are not interpreted as inferential effect sizes here.",
                "- Preregistered margins remain undefined; future continuous severity models and future binary endpoint models require separately justified thresholds.",
                "",
                "## Next Falsifiable Experiments",
                "",
                "- H1 null-model test: for each source graph, compare observed mean ORC against at least 100 degree-preserving random graphs; only proceed if preregistered z-score or empirical-p thresholds are met after size/density checks.",
                "- H2 size-control test: repeat ORC/C_ent estimates on size-matched subgraphs or include graph size and density as covariates before interpreting between-group differences.",
                "- H3 individual-level test: if per-subject graphs become available, evaluate whether ORC/C_ent features improve a preregistered severity or outcome model beyond graph size/density baselines.",
                "- Context-of-use gate: choose screening, prognosis, monitoring, or response modeling before any marker or biomarker language is allowed.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _scan_claim_docs() -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for path in CLAIM_DOCS:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern, name in FORBIDDEN_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                line_start = text.rfind("\n", 0, match.start()) + 1
                line_end = text.find("\n", match.end())
                if line_end == -1:
                    line_end = len(text)
                context_start = text.rfind("\n", 0, max(0, line_start - 1)) + 1
                context_end = text.find("\n", line_end + 1)
                if context_end == -1:
                    context_end = len(text)
                context = text[context_start:context_end].lower()
                if any(token in context for token in ("not", "no ", "without", "does not", "reject", "avoid", "forbidden")):
                    continue
                hits.append({"file": str(path.relative_to(REPO_ROOT)), "name": name, "pattern": pattern})
    return hits


def _git_commit_hash() -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0:
            return proc.stdout.strip()
    except Exception:
        pass
    return "unknown"


def build_report() -> dict:
    clinical = load_json(CLINICAL_DEPRESSION_SUMMARY_JSON)
    epistemic = load_json(EPISTEMIC_ORC_JSON)
    cross = load_json(CROSS_DOMAIN_JSON)
    kec = load_json(KEC_CORRELATIONS_JSON) if KEC_CORRELATIONS_JSON.exists() else {}

    missing = [
        sev
        for sev in DEPRESSION_SEVERITIES
        if sev not in clinical.get("per_severity", {}) or sev not in epistemic.get("per_severity", {})
    ]
    clinical_per = clinical.get("per_severity", {})
    epi_per = epistemic.get("per_severity", {})
    pairwise = clinical.get("pairwise_cohens_d", {})

    kappa_by_sev = {sev: float(epi_per[sev]["kappa_mean"]) for sev in DEPRESSION_SEVERITIES if sev in epi_per}
    c_ent_by_sev = {sev: float(clinical_per[sev]["C_ent_mean"]) for sev in DEPRESSION_SEVERITIES if sev in clinical_per}
    ci_negative = {
        sev: float(epi_per[sev]["ci_hi"]) < 0.0 and float(epi_per[sev]["ci_lo"]) < 0.0
        for sev in DEPRESSION_SEVERITIES
        if sev in epi_per
    }
    kappa_ci_by_sev = {
        sev: [
            round(float(epi_per[sev]["ci_lo"]), 3),
            round(float(epi_per[sev]["ci_hi"]), 3),
        ]
        for sev in DEPRESSION_SEVERITIES
        if sev in epi_per
    }
    graph_size_by_sev = {
        sev: {
            "N": int(epi_per[sev]["N"]),
            "E": int(epi_per[sev]["E"]),
        }
        for sev in sorted(DEPRESSION_SEVERITIES)
        if sev in epi_per
    }
    depression_cross = [
        row for row in cross.get("networks", []) if str(row.get("network", "")).startswith("Depression-")
    ]
    max_abs_d = max((abs(float(v["cohens_d"])) for v in pairwise.values()), default=0.0)

    kappa_values = _severity_order(kappa_by_sev) if len(kappa_by_sev) == len(DEPRESSION_SEVERITIES) else []
    c_ent_values = _severity_order(c_ent_by_sev) if len(c_ent_by_sev) == len(DEPRESSION_SEVERITIES) else []

    requirements = {
        "all_severity_levels_present": not missing,
        "all_epistemic_ci_negative": len(ci_negative) == 4 and all(ci_negative.values()),
        "cross_domain_has_four_depression_networks": len(depression_cross) == 4,
            "pairwise_C_ent_effects_are_small_descriptive_not_marker_validation_level": max_abs_d < 0.25,
        "severity_aggregate_is_not_overstated_as_monotonic": bool(kappa_values) and not _is_monotonic(kappa_values),
    }

    report = {
        "schema": "cpc2026.depression_orc_network_geometry_scope_gate.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit_hash": _git_commit_hash(),
        "status": "PASS_EXPLORATORY_NETWORK_GEOMETRY_SCOPE_GATE_ONLY",
        "requirements": requirements,
        "failed_requirements": [name for name, ok in requirements.items() if not ok],
        "per_severity": {
            "kappa_mean_by_severity": kappa_by_sev,
            "C_ent_mean_by_severity": c_ent_by_sev,
            "kappa_sequence_monotonic": _is_monotonic(kappa_values) if kappa_values else None,
            "C_ent_sequence_monotonic": _is_monotonic(c_ent_values) if c_ent_values else None,
        },
        "evidence": {
            "negative_ci_count": sum(1 for ok in ci_negative.values() if ok),
            "ci_negative_by_severity": ci_negative,
            "kappa_95ci_by_severity": kappa_ci_by_sev,
            "graph_size_by_group": graph_size_by_sev,
            "bootstrap_protocol": f"bootstrap mean ORC over graph nodes, n_boot={int(epistemic.get('n_bootstrap', 0))}; source seed recorded in depression_epistemic_orc.json",
            "null_model_comparison_available": False,
            "cross_domain_depression_count": len(depression_cross),
            "cross_domain_total_network_count": int(cross.get("count", len(cross.get("networks", [])))),
            "max_abs_pairwise_C_ent_d": max_abs_d,
            "small_effect_threshold_for_C_ent_d": 0.2,
            "kec_curvature_spearman_rho": kec.get("curvature", {}).get("spearman_rho"),
            "kec_curvature_spearman_p": kec.get("curvature", {}).get("spearman_p"),
            "kec_KEC_spectral_spearman_rho": kec.get("KEC_spectral", {}).get("spearman_rho"),
            "kec_KEC_spectral_spearman_p": kec.get("KEC_spectral", {}).get("spearman_p"),
        },
        "accepted_claim": (
            "The current CPC 2026 artifact is an exploratory network-geometry scope gate "
            "that authorizes null-model, size-control, and per-subject follow-up experiments only."
        ),
        "claim_level": "exploratory_network_geometry_scope_gate",
        "context_of_use": "exploratory research and conference hypothesis generation; not for clinical decision-making",
        "target_external_cohort": "TBD; no access agreement or validation cohort is claimed",
        "monotonicity_assumption": "not established; current group means are non-monotonic and require formal trend testing before any ordered-severity claim",
        "preregistered_margins": "undefined; example planning thresholds such as |r| >= 0.30 for severity association or AUC >= 0.65 for individual-level endpoints require domain justification before confirmatory use",
        "forbidden_claims": [
            "biomarker-candidate",
            "validated clinical biomarker",
            "diagnostic biomarker",
            "clinical utility",
            "patient-level prediction",
            "treatment selection",
        ],
        "boundaries": [
            "conference_hypothesis_framing_not_clinical_validation",
            "exploratory_network_geometry_scope_gate_not_biomarker_candidate",
            "exploratory_network_geometry_scope_gate_not_diagnostic_biomarker",
            "no_patient_level_prediction_or_treatment_selection_claim",
            "severity_aggregate_is_non_monotonic_in_current_four_network_evidence",
            "clinical_context_of_use_not_defined",
            "requires_independent_external_validation_before_clinical_biomarker_language",
        ],
    }
    if report["failed_requirements"]:
        report["status"] = "FAIL"
    return report


def main() -> int:
    global OUT_JSON, OUT_MD

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-json", default=str(OUT_JSON))
    parser.add_argument("--out-md", default=str(OUT_MD))
    args = parser.parse_args()

    OUT_JSON = Path(args.out_json)
    OUT_MD = Path(args.out_md)

    report = build_report()
    _write_claim_markdown(report)
    forbidden_hits = _scan_claim_docs()
    report["claim_doc"] = str(OUT_MD.relative_to(REPO_ROOT))
    report["forbidden_hits"] = forbidden_hits
    if forbidden_hits:
        report["status"] = "FAIL"

    save_json(OUT_JSON, report)
    print(
        "network_geometry_claim_gate: "
        f"{report['status']} negative_ci={report['evidence']['negative_ci_count']}/4 "
        f"max_abs_d={report['evidence']['max_abs_pairwise_C_ent_d']:.6g} "
        f"out={OUT_JSON}"
    )
    return 0 if report["status"] == "PASS_EXPLORATORY_NETWORK_GEOMETRY_SCOPE_GATE_ONLY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
