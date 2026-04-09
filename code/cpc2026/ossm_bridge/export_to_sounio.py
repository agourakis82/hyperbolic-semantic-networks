"""Export SWOW O-SSM inputs to a compact CSV package for canonical Sounio.

The Python side keeps dense `.npy` tensors for analysis, but the Sounio side is
better served by compact row-wise CSV matrices of node indices plus a separate
node-feature table. This avoids a prohibitively large flat stepwise CSV while
remaining easy to parse with `read_file(...)` and string splitting in Sounio.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
CPC_DIR = SCRIPT_DIR.parent
if str(CPC_DIR) not in sys.path:
    sys.path.append(str(CPC_DIR))

from common import (  # noqa: E402
    CPC_SOUNIO_INPUT_DIR,
    DEFAULT_SEED,
    REGIME_CONFIGS,
    SOUNIO_INPUT_MANIFEST_JSON,
    ensure_directory,
    save_json,
    trajectory_node_index_path,
    trajectory_sounio_csv_path,
)
from ossm_bridge.node_features import FEATURE_COLUMNS, NODE_FEATURES_CSV, NODE_FEATURES_METADATA_JSON  # noqa: E402
from ossm_bridge.trajectory_generator import TRAJECTORY_INPUT_METADATA_JSON, generate_input_tensors  # noqa: E402


def _write_rowwise_node_csv(path: Path, node_matrix: np.ndarray) -> None:
    """Write one trajectory per CSV row: trajectory_id,n0,n1,...,nT."""

    ensure_directory(path.parent)
    header = ["trajectory_id", *[f"step_{idx}" for idx in range(node_matrix.shape[1])]]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        for trajectory_id, row in enumerate(node_matrix):
            writer.writerow([trajectory_id, *row.tolist()])


def _parity_csv_path(regime: str) -> Path:
    """Return the compact parity CSV path used by the canonical Sounio runner."""

    return CPC_SOUNIO_INPUT_DIR / f"trajectories_{regime}_nodes_parity.csv"


def export_sounio_package() -> dict[str, Any]:
    """Export node features and node-index trajectories for Sounio."""

    if not NODE_FEATURES_CSV.exists():
        raise FileNotFoundError(f"Missing node feature table at {NODE_FEATURES_CSV}.")
    if not TRAJECTORY_INPUT_METADATA_JSON.exists():
        generate_input_tensors(n_trajectories=10_000, trajectory_length=500)

    ensure_directory(CPC_SOUNIO_INPUT_DIR)

    node_features = pd.read_csv(NODE_FEATURES_CSV)
    feature_export = node_features.loc[:, ["node_index", "node", *FEATURE_COLUMNS]]
    feature_export_path = CPC_SOUNIO_INPUT_DIR / "node_features.csv"
    feature_export.to_csv(feature_export_path, index=False)

    regimes: dict[str, Any] = {}
    parity_defaults = {"max_trajectories": 64, "max_steps": 64}
    for regime in REGIME_CONFIGS:
        node_path = trajectory_node_index_path(regime.name)
        if not node_path.exists():
            raise FileNotFoundError(f"Missing trajectory node matrix for {regime.name} at {node_path}.")
        node_matrix = np.load(node_path)
        csv_path = trajectory_sounio_csv_path(regime.name)
        _write_rowwise_node_csv(csv_path, node_matrix)
        parity_matrix = node_matrix[: parity_defaults["max_trajectories"], : parity_defaults["max_steps"]]
        parity_path = _parity_csv_path(regime.name)
        _write_rowwise_node_csv(parity_path, parity_matrix)
        regimes[regime.name] = {
            "node_csv": str(csv_path),
            "shape": [int(dim) for dim in node_matrix.shape],
            "parity_node_csv": str(parity_path),
            "parity_shape": [int(dim) for dim in parity_matrix.shape],
        }

    manifest = {
        "seed": DEFAULT_SEED,
        "format": "rowwise_node_indices_csv_plus_feature_lookup",
        "feature_file": str(feature_export_path),
        "feature_columns": list(FEATURE_COLUMNS),
        "node_feature_metadata": str(NODE_FEATURES_METADATA_JSON),
        "trajectory_generation_metadata": str(TRAJECTORY_INPUT_METADATA_JSON),
        "parity_defaults": parity_defaults,
        "regimes": regimes,
        "notes": [
            "Each trajectory CSV row contains one trajectory_id followed by 500 node indices.",
            "Sounio should load node_features.csv once, then look up the 8D vector for each node index.",
            "The *_parity.csv files provide a bounded 64 x 64 subset for executable Sounio parity runs.",
            "Dense .npy tensors remain in data/cpc2026/ for Python-side analysis.",
        ],
    }
    save_json(SOUNIO_INPUT_MANIFEST_JSON, manifest)
    return manifest


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Export only if the small smoke tensors are already present.",
    )
    return parser


def main() -> None:
    """CLI entry point for the Sounio export bundle."""

    parser = _build_parser()
    parser.parse_args()
    manifest = export_sounio_package()
    print(
        "Exported compact Sounio input package "
        f"for {len(manifest['regimes'])} regimes to {CPC_SOUNIO_INPUT_DIR}."
    )


if __name__ == "__main__":
    main()
