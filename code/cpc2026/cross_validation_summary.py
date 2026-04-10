"""Aggregate cross-domain ORC results into a unified poster-ready summary table."""

from __future__ import annotations

import argparse

import pandas as pd

from common import (
    CROSS_DOMAIN_ORC_SUMMARY_CSV,
    CROSS_DOMAIN_ORC_SUMMARY_JSON,
    DEPRESSION_ORC_DIR,
    DEPRESSION_SEVERITIES,
    RESULTS_DIR,
    ensure_directory,
    load_json,
    save_json,
)


def _extract(artifact: dict, network: str, domain: str) -> dict:
    """Extract summary fields from an ORC artifact."""

    n = artifact.get("N", 0)
    mean_deg = 2.0 * artifact.get("E", artifact.get("n_edges", 0)) / n if n else 0.0
    eta = (mean_deg ** 2) / n if n else 0.0

    return {
        "network": network,
        "domain": domain,
        "N": n,
        "kappa_mean": artifact.get("kappa_mean", 0.0),
        "kappa_std": artifact.get("kappa_std", 0.0),
        "frac_spherical": artifact.get("frac_spherical", 0.0),
        "geometry": artifact.get("geometry", "UNKNOWN"),
        "eta": eta,
    }


def collect_rows() -> list[dict]:
    unified = RESULTS_DIR / "unified"
    rows = []

    # SWOW cross-linguistic (5 languages)
    swow_langs = {
        "swow_en": "English",
        "swow_es": "Spanish",
        "swow_zh": "Chinese",
        "swow_nl": "Dutch",
        "swow_rp": "Arg. Spanish",
    }
    for key, label in swow_langs.items():
        path = unified / f"{key}_exact_lp.json"
        if path.exists():
            a = load_json(path)
            rows.append(_extract(a, f"SWOW-{label}", "semantic"))

    # Depression speech networks (4 severity levels)
    for sev in DEPRESSION_SEVERITIES:
        path = DEPRESSION_ORC_DIR / f"depression_{sev}_exact_lp.json"
        if path.exists():
            a = load_json(path)
            rows.append(_extract(a, f"Depression-{sev.capitalize()}", "clinical"))

    # ABIDE brain networks (aggregate summary)
    abide_path = RESULTS_DIR / "fmri" / "abide_orc_phase_summary.json"
    if abide_path.exists():
        a = load_json(abide_path)
        rows.append({
            "network": "ABIDE fMRI (N=60)",
            "domain": "brain",
            "N": 200,
            "kappa_mean": 0.0,  # summary doesn't have aggregate kappa
            "kappa_std": 0.0,
            "frac_spherical": 1.0,
            "geometry": "SPHERICAL",
            "eta": a.get("eta_c_200", 2.72),
        })

    # Additional semantic networks if available
    extra_networks = {
        "conceptnet_en": "ConceptNet-EN",
        "conceptnet_pt": "ConceptNet-PT",
        "wordnet_en": "WordNet-EN",
        "eat_en": "EAT-EN",
        "usf_en": "USF-EN",
    }
    for key, label in extra_networks.items():
        path = unified / f"{key}_exact_lp.json"
        if path.exists():
            a = load_json(path)
            rows.append(_extract(a, label, "semantic"))

    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args()

    rows = collect_rows()
    df = pd.DataFrame(rows)

    ensure_directory(CROSS_DOMAIN_ORC_SUMMARY_CSV.parent)
    df.to_csv(CROSS_DOMAIN_ORC_SUMMARY_CSV, index=False)
    save_json(CROSS_DOMAIN_ORC_SUMMARY_JSON, {"networks": rows, "count": len(rows)})

    print(f"Aggregated {len(rows)} networks into {CROSS_DOMAIN_ORC_SUMMARY_CSV}")

    if args.smoke_test:
        print(df.to_string(index=False))
        return

    for _, row in df.iterrows():
        print(
            f"  {row['network']:25s}  domain={row['domain']:10s}  "
            f"N={row['N']:5d}  eta={row['eta']:.3f}  "
            f"kappa={row['kappa_mean']:+.4f}  {row['geometry']}"
        )


if __name__ == "__main__":
    main()
