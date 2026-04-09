"""Compute node-level entropic curvature on the validated SWOW-EN graph."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from common import (
    DEFAULT_SEED,
    NODE_METRICS_PARQUET,
    NODE_METRICS_QC_JSON,
    compute_graphricci_node_kappa,
    derive_exact_node_kappa,
    ensure_directory,
    graph_summary,
    load_exact_orc_artifact,
    load_swow_en_graph,
    save_json,
    seed_everything,
)


def compute_local_entropy(graph) -> pd.DataFrame:
    """Compute local Shannon transition entropy for every graph node."""

    rows = []
    for node in sorted(graph.nodes()):
        neighbors = sorted(graph.neighbors(node))
        degree = len(neighbors)
        strength = float(sum(graph[node][neighbor]["weight"] for neighbor in neighbors))
        if degree == 0 or strength == 0.0:
            entropy = 0.0
        else:
            weights = np.array([graph[node][neighbor]["weight"] for neighbor in neighbors], dtype=float)
            probabilities = weights / weights.sum()
            entropy = float(-(probabilities * np.log(probabilities)).sum())
        entropy_norm = 0.0 if degree <= 1 else float(entropy / np.log(degree))
        rows.append(
            {
                "node": node,
                "degree": degree,
                "strength": strength,
                "entropy": entropy,
                "entropy_norm": entropy_norm,
            }
        )
    return pd.DataFrame(rows)


def compute_node_metrics(validate_python_fallback: bool = True) -> tuple[pd.DataFrame, dict[str, float | str | bool]]:
    """Compute entropic curvature metrics from the exact-LP SWOW-EN artifact."""

    graph = load_swow_en_graph()
    entropy_df = compute_local_entropy(graph)
    exact_artifact = load_exact_orc_artifact()
    kappa_df = derive_exact_node_kappa(graph, artifact=exact_artifact)

    metrics = entropy_df.merge(kappa_df, on="node", how="left")
    metrics["C_ent"] = metrics["kappa"] * (1.0 - metrics["entropy_norm"])
    metrics = metrics.sort_values("node", ignore_index=True)

    qc_payload: dict[str, float | str | bool] = {
        "graph_n_nodes": graph.number_of_nodes(),
        "graph_n_edges": graph.number_of_edges(),
        "artifact_kappa_mean": float(exact_artifact["kappa_mean"]),
        "artifact_kappa_std": float(exact_artifact["kappa_std"]),
        "node_kappa_mean": float(metrics["kappa"].mean()),
        "node_c_ent_mean": float(metrics["C_ent"].mean()),
        "exact_artifact_used": True,
    }
    qc_payload.update(graph_summary(graph))

    if validate_python_fallback:
        try:
            fallback_df = compute_graphricci_node_kappa(graph)
            merged = metrics.merge(fallback_df, on="node", how="left")
            correlation = merged["kappa"].corr(merged["kappa_graphricci"])
            mad = (merged["kappa"] - merged["kappa_graphricci"]).abs().mean()
            qc_payload["graphricci_validation_available"] = True
            qc_payload["graphricci_node_correlation"] = float(correlation)
            qc_payload["graphricci_mean_absolute_difference"] = float(mad)
        except Exception as exc:  # pragma: no cover - environment dependent
            qc_payload["graphricci_validation_available"] = False
            qc_payload["graphricci_validation_error"] = str(exc)

    return metrics, qc_payload


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=NODE_METRICS_PARQUET,
        type=Path,
        help="Output parquet path for node-level entropic curvature metrics.",
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Compute metrics and print the first few rows instead of a long summary.",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for node-level entropic curvature computation."""

    seed_everything(DEFAULT_SEED)
    args = parse_args()
    output_path = args.output
    metrics, qc_payload = compute_node_metrics()

    ensure_directory(output_path.parent)
    metrics.to_parquet(output_path, index=False)
    save_json(NODE_METRICS_QC_JSON, qc_payload)

    if args.smoke_test:
        print(metrics.loc[:, ["node", "degree", "kappa", "entropy", "C_ent"]].head(8).to_string(index=False))
        return

    print(
        f"Saved {len(metrics)} node metrics to {output_path}. "
        f"Mean kappa={metrics['kappa'].mean():.4f}, mean C_ent={metrics['C_ent'].mean():.4f}."
    )


if __name__ == "__main__":
    main()
