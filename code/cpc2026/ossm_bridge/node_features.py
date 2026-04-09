"""Build 8D SWOW-EN node features for the cognitive O-SSM bridge.

Each node is mapped to a reviewer-friendly octonionic input vector:

    [kappa, entropy_norm, c_ent_norm, valence, poincare_x, poincare_y,
     log_degree_norm, eta_local_norm]

The CPC pipeline already materializes the required node metrics, valence
annotations, and a 2D Poincare embedding for the 438-node SWOW-EN largest
connected component. This script consolidates those artifacts and adds the only
missing graph-derived term: a local density proxy eta_local.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any

import networkx as nx
import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
CPC_DIR = SCRIPT_DIR.parent
if str(CPC_DIR) not in sys.path:
    sys.path.append(str(CPC_DIR))

from common import (  # noqa: E402
    DEFAULT_SEED,
    NODE_FEATURES_CSV,
    NODE_FEATURES_METADATA_JSON,
    NODE_FEATURES_NPY,
    ensure_directory,
    load_node_metrics,
    load_poincare_embedding,
    load_swow_en_graph,
    load_valence_data,
    save_json,
    seed_everything,
)
from trajectory_simulator import compute_poincare_embedding  # noqa: E402


FEATURE_COLUMNS: tuple[str, ...] = (
    "feature_kappa",
    "feature_entropy_norm",
    "feature_c_ent",
    "feature_valence",
    "feature_poincare_x",
    "feature_poincare_y",
    "feature_log_degree",
    "feature_eta_local",
)


def _symmetric_unit_scale(values: np.ndarray) -> tuple[np.ndarray, float]:
    """Scale a vector to [-1, 1] using its maximum absolute value."""

    max_abs = float(np.max(np.abs(values))) if len(values) else 1.0
    if max_abs == 0.0:
        return np.zeros_like(values, dtype=np.float32), 1.0
    scaled = np.clip(values / max_abs, -1.0, 1.0)
    return scaled.astype(np.float32), max_abs


def _minmax_unit_scale(values: np.ndarray) -> tuple[np.ndarray, dict[str, float]]:
    """Scale a vector to [-1, 1] using min-max normalization."""

    lower = float(values.min()) if len(values) else 0.0
    upper = float(values.max()) if len(values) else 0.0
    if upper == lower:
        return np.zeros_like(values, dtype=np.float32), {"min": lower, "max": upper}
    scaled = 2.0 * ((values - lower) / (upper - lower)) - 1.0
    return np.clip(scaled, -1.0, 1.0).astype(np.float32), {"min": lower, "max": upper}


def compute_local_eta(graph: nx.Graph) -> pd.DataFrame:
    """Compute a local density proxy for each node's 1-hop induced neighborhood."""

    rows: list[dict[str, float | str]] = []
    for node in sorted(graph.nodes()):
        local_nodes = {node, *graph.neighbors(node)}
        subgraph = graph.subgraph(local_nodes)
        n_local = subgraph.number_of_nodes()
        if n_local == 0:
            eta_local = 0.0
            mean_degree_local = 0.0
            local_edges = 0
        else:
            degrees = np.array([degree for _, degree in subgraph.degree()], dtype=float)
            mean_degree_local = float(degrees.mean()) if len(degrees) else 0.0
            local_edges = subgraph.number_of_edges()
            eta_local = float((mean_degree_local**2) / n_local)

        rows.append(
            {
                "node": node,
                "n_local": n_local,
                "local_edges": local_edges,
                "mean_degree_local": mean_degree_local,
                "eta_local_raw": eta_local,
            }
        )
    return pd.DataFrame(rows).sort_values("node", ignore_index=True)


def _load_or_compute_embedding(graph: nx.Graph) -> pd.DataFrame:
    """Load the CPC Poincare embedding, computing it if necessary."""

    try:
        return load_poincare_embedding().sort_values("node", ignore_index=True)
    except FileNotFoundError:
        return compute_poincare_embedding(graph).sort_values("node", ignore_index=True)


def build_node_feature_table() -> tuple[pd.DataFrame, np.ndarray, dict[str, Any]]:
    """Merge CPC node artifacts into a normalized 8D feature table."""

    graph = load_swow_en_graph()
    metrics = load_node_metrics().sort_values("node", ignore_index=True)
    valence = load_valence_data().sort_values("node", ignore_index=True)
    embedding = _load_or_compute_embedding(graph)
    local_eta = compute_local_eta(graph)

    merged = (
        metrics.merge(
            valence.loc[:, ["node", "valence_centered", "arousal_raw", "dominance_raw"]],
            on="node",
            how="left",
        )
        .merge(embedding.loc[:, ["node", "x", "y", "radius", "embedding_engine"]], on="node", how="left")
        .merge(local_eta, on="node", how="left")
        .sort_values("node", ignore_index=True)
    )

    merged["node_index"] = np.arange(len(merged), dtype=np.int32)
    merged["valence_centered"] = merged["valence_centered"].fillna(0.0)
    merged["arousal_raw"] = merged["arousal_raw"].fillna(0.0)
    merged["dominance_raw"] = merged["dominance_raw"].fillna(0.0)

    merged["log_degree_raw"] = np.log(np.clip(merged["degree"].to_numpy(dtype=float), 1.0, None))

    c_ent_scaled, c_ent_scale = _symmetric_unit_scale(merged["C_ent"].to_numpy(dtype=float))
    log_degree_scaled, log_degree_meta = _minmax_unit_scale(merged["log_degree_raw"].to_numpy(dtype=float))
    eta_local_scaled, eta_local_meta = _minmax_unit_scale(merged["eta_local_raw"].to_numpy(dtype=float))

    merged["feature_kappa"] = np.clip(merged["kappa"].to_numpy(dtype=float), -1.0, 1.0).astype(np.float32)
    merged["feature_entropy_norm"] = np.clip(
        merged["entropy_norm"].to_numpy(dtype=float), -1.0, 1.0
    ).astype(np.float32)
    merged["feature_c_ent"] = c_ent_scaled
    merged["feature_valence"] = np.clip(
        merged["valence_centered"].to_numpy(dtype=float), -1.0, 1.0
    ).astype(np.float32)
    merged["feature_poincare_x"] = np.clip(merged["x"].to_numpy(dtype=float), -1.0, 1.0).astype(np.float32)
    merged["feature_poincare_y"] = np.clip(merged["y"].to_numpy(dtype=float), -1.0, 1.0).astype(np.float32)
    merged["feature_log_degree"] = log_degree_scaled
    merged["feature_eta_local"] = eta_local_scaled

    feature_matrix = merged.loc[:, FEATURE_COLUMNS].to_numpy(dtype=np.float32)

    metadata = {
        "seed": DEFAULT_SEED,
        "n_nodes": int(len(merged)),
        "feature_columns": list(FEATURE_COLUMNS),
        "vector_layout": [
            "kappa",
            "entropy_norm",
            "c_ent_scaled",
            "valence_centered",
            "poincare_x",
            "poincare_y",
            "log_degree_scaled",
            "eta_local_scaled",
        ],
        "normalization": {
            "kappa": "identity_clip[-1,1]",
            "entropy_norm": "identity_clip[-1,1]",
            "c_ent_scaled": {"method": "max_abs", "scale": c_ent_scale},
            "valence_centered": "identity_clip[-1,1]",
            "poincare_x": "identity_clip[-1,1]",
            "poincare_y": "identity_clip[-1,1]",
            "log_degree_scaled": {"method": "minmax_to_unit", **log_degree_meta},
            "eta_local_scaled": {"method": "minmax_to_unit", **eta_local_meta},
        },
        "poincare_embedding_engine": str(merged["embedding_engine"].iloc[0]),
        "raw_columns_retained": [
            "degree",
            "strength",
            "entropy",
            "entropy_norm",
            "kappa",
            "C_ent",
            "valence_centered",
            "arousal_raw",
            "dominance_raw",
            "x",
            "y",
            "radius",
            "log_degree_raw",
            "eta_local_raw",
        ],
    }
    return merged, feature_matrix, metadata


def save_node_features(output_csv: Path = NODE_FEATURES_CSV, output_npy: Path = NODE_FEATURES_NPY) -> dict[str, Any]:
    """Compute and persist node features plus metadata."""

    table, feature_matrix, metadata = build_node_feature_table()
    ensure_directory(output_csv.parent)
    table.to_csv(output_csv, index=False)
    np.save(output_npy, feature_matrix)
    save_json(NODE_FEATURES_METADATA_JSON, metadata)
    return {
        "csv": str(output_csv),
        "npy": str(output_npy),
        "metadata": str(NODE_FEATURES_METADATA_JSON),
        "shape": list(feature_matrix.shape),
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke-test", action="store_true", help="Run a minimal integrity check after writing.")
    return parser


def main() -> None:
    """CLI entry point with a minimal smoke test."""

    parser = _build_parser()
    args = parser.parse_args()

    seed_everything(DEFAULT_SEED)
    result = save_node_features()

    if args.smoke_test:
        feature_matrix = np.load(NODE_FEATURES_NPY)
        if feature_matrix.shape[1] != 8:
            raise SystemExit(f"Expected 8 feature columns, found {feature_matrix.shape[1]}.")
        if np.isnan(feature_matrix).any():
            raise SystemExit("Feature matrix contains NaNs.")

    print(
        "Saved SWOW node features for the O-SSM bridge "
        f"({result['shape'][0]} nodes x {result['shape'][1]} features)."
    )


if __name__ == "__main__":
    main()
