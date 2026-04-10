"""Compute entropic curvature on depression speech networks for clinical validation."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from common import (
    CLINICAL_DEPRESSION_METRICS_PARQUET,
    CLINICAL_DEPRESSION_SUMMARY_JSON,
    DEFAULT_SEED,
    DEPRESSION_EDGE_DIR,
    DEPRESSION_ORC_DIR,
    DEPRESSION_SEVERITIES,
    build_weighted_graph,
    derive_exact_node_kappa,
    ensure_directory,
    graph_eta,
    load_edgelist,
    load_json,
    save_json,
    seed_everything,
)
from entropic_curvature import compute_local_entropy


def load_depression_network(severity: str) -> tuple[object, dict]:
    """Load a depression speech network and its pre-computed ORC artifact."""

    edge_path = DEPRESSION_EDGE_DIR / f"depression_{severity}_edges.csv"
    orc_path = DEPRESSION_ORC_DIR / f"depression_{severity}_exact_lp.json"

    edges_df = load_edgelist(edge_path)
    graph = build_weighted_graph(edges_df, largest_component=True)
    artifact = load_json(orc_path)

    if "per_edge_curvatures" not in artifact:
        raise ValueError(f"ORC artifact for {severity} missing per_edge_curvatures")

    return graph, artifact


def compute_depression_metrics(severity: str) -> pd.DataFrame:
    """Compute per-node entropic curvature for one depression severity level."""

    graph, artifact = load_depression_network(severity)
    entropy_df = compute_local_entropy(graph)
    kappa_df = derive_exact_node_kappa(graph, artifact=artifact)

    metrics = entropy_df.merge(kappa_df, on="node", how="left")
    metrics["C_ent"] = metrics["kappa"] * (1.0 - metrics["entropy_norm"])
    metrics["severity"] = severity
    metrics["eta"] = graph_eta(graph)
    metrics["N"] = graph.number_of_nodes()
    metrics["E"] = graph.number_of_edges()

    return metrics.sort_values("node", ignore_index=True)


def cohens_d(x: np.ndarray, y: np.ndarray) -> float:
    """Cohen's d for two independent samples."""

    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    pooled = np.sqrt(
        ((len(x) - 1) * x.var(ddof=1) + (len(y) - 1) * y.var(ddof=1))
        / (len(x) + len(y) - 2)
    )
    return 0.0 if pooled == 0.0 else float((y.mean() - x.mean()) / pooled)


def main() -> None:
    seed_everything(DEFAULT_SEED)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args()

    all_metrics = []
    per_severity = {}

    for severity in DEPRESSION_SEVERITIES:
        print(f"Computing C_ent for depression_{severity}...")
        df = compute_depression_metrics(severity)
        all_metrics.append(df)

        per_severity[severity] = {
            "N": int(df["N"].iloc[0]),
            "E": int(df["E"].iloc[0]),
            "eta": float(df["eta"].iloc[0]),
            "kappa_mean": float(df["kappa"].mean()),
            "kappa_std": float(df["kappa"].std()),
            "kappa_median": float(df["kappa"].median()),
            "entropy_mean": float(df["entropy"].mean()),
            "entropy_norm_mean": float(df["entropy_norm"].mean()),
            "C_ent_mean": float(df["C_ent"].mean()),
            "C_ent_std": float(df["C_ent"].std()),
            "C_ent_median": float(df["C_ent"].median()),
        }
        print(
            f"  N={per_severity[severity]['N']}, "
            f"kappa={per_severity[severity]['kappa_mean']:.4f}, "
            f"C_ent={per_severity[severity]['C_ent_mean']:.4f}"
        )

    combined = pd.concat(all_metrics, ignore_index=True)

    # Pairwise Cohen's d for C_ent between severity levels
    pairwise = {}
    for i, s1 in enumerate(DEPRESSION_SEVERITIES):
        for s2 in DEPRESSION_SEVERITIES[i + 1 :]:
            x = combined.loc[combined["severity"] == s1, "C_ent"].to_numpy()
            y = combined.loc[combined["severity"] == s2, "C_ent"].to_numpy()
            d = cohens_d(x, y)
            pairwise[f"{s1}_vs_{s2}"] = {
                "cohens_d": d,
                "n1": len(x),
                "n2": len(y),
                "mean1": float(x.mean()),
                "mean2": float(y.mean()),
            }

    summary = {
        "per_severity": per_severity,
        "pairwise_cohens_d": pairwise,
    }

    ensure_directory(CLINICAL_DEPRESSION_METRICS_PARQUET.parent)
    combined.to_parquet(CLINICAL_DEPRESSION_METRICS_PARQUET, index=False)
    save_json(CLINICAL_DEPRESSION_SUMMARY_JSON, summary)

    if args.smoke_test:
        for sev in DEPRESSION_SEVERITIES:
            s = per_severity[sev]
            print(f"  {sev}: N={s['N']}, kappa={s['kappa_mean']:.4f}, C_ent={s['C_ent_mean']:.4f}")
        return

    print(f"\nSaved {len(combined)} node metrics to {CLINICAL_DEPRESSION_METRICS_PARQUET}")
    print(f"Saved summary to {CLINICAL_DEPRESSION_SUMMARY_JSON}")
    print("\nPairwise C_ent effect sizes:")
    for pair, info in pairwise.items():
        print(f"  {pair}: d={info['cohens_d']:.3f}")


if __name__ == "__main__":
    main()
