"""Generate regime-specific O-SSM input sequences on SWOW-EN.

The regime kernel matches the CPC Markov-chain baseline so the O-SSM can be
compared against the existing quantitative results on aligned input walks.
"""

from __future__ import annotations

import argparse
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
    CPC_DATA_DIR,
    DEFAULT_SEED,
    REGIME_CONFIGS,
    ensure_directory,
    load_node_metrics,
    load_swow_en_graph,
    save_json,
    seed_everything,
    trajectory_input_tensor_path,
    trajectory_node_index_path,
    trajectory_path,
)
from trajectory_simulator import simulate_markov_regime  # noqa: E402
from ossm_bridge.node_features import (  # noqa: E402
    FEATURE_COLUMNS,
    NODE_FEATURES_CSV,
    NODE_FEATURES_NPY,
    save_node_features,
)


TRAJECTORY_INPUT_METADATA_JSON = CPC_DATA_DIR / "trajectory_input_metadata.json"


def _load_or_build_node_features() -> tuple[pd.DataFrame, np.ndarray]:
    """Load cached node features, building them if needed."""

    if not NODE_FEATURES_CSV.exists() or not NODE_FEATURES_NPY.exists():
        save_node_features()
    table = pd.read_csv(NODE_FEATURES_CSV).sort_values("node_index", ignore_index=True)
    matrix = np.load(NODE_FEATURES_NPY)
    return table, matrix


def _node_matrix_from_frame(frame: pd.DataFrame, node_to_index: dict[str, int]) -> np.ndarray:
    """Convert a long CPC trajectory frame into a trajectory x step node matrix."""

    ordered = frame.sort_values(["trajectory_id", "step"], kind="mergesort").reset_index(drop=True)
    n_trajectories = int(ordered["trajectory_id"].max()) + 1
    trajectory_length = int(ordered["step"].max()) + 1
    node_indices = ordered["node"].astype(str).map(node_to_index).to_numpy(dtype=np.int32)
    return node_indices.reshape(n_trajectories, trajectory_length)


def _load_or_simulate_regime(
    regime_name: str,
    seed: int,
    n_trajectories: int,
    trajectory_length: int,
    force_resimulate: bool,
) -> pd.DataFrame:
    """Load cached CPC trajectories or simulate them with the validated kernel."""

    parquet_path = trajectory_path(regime_name)
    if parquet_path.exists() and not force_resimulate:
        frame = pd.read_parquet(parquet_path)
        expected_rows = n_trajectories * trajectory_length
        if len(frame) == expected_rows:
            return frame

    graph = load_swow_en_graph()
    metrics = load_node_metrics()
    regime = next(config for config in REGIME_CONFIGS if config.name == regime_name)
    frame, _ = simulate_markov_regime(
        graph,
        metrics,
        regime=regime,
        n_trajectories=n_trajectories,
        trajectory_length=trajectory_length,
        seed=seed,
    )
    ensure_directory(parquet_path.parent)
    frame.to_parquet(parquet_path, index=False)
    return frame


def generate_input_tensors(
    n_trajectories: int,
    trajectory_length: int,
    force_resimulate: bool = False,
) -> dict[str, Any]:
    """Generate regime-wise node-index and feature tensors."""

    node_table, feature_matrix = _load_or_build_node_features()
    node_to_index = dict(zip(node_table["node"], node_table["node_index"], strict=True))

    outputs: dict[str, Any] = {
        "seed": DEFAULT_SEED,
        "n_trajectories": n_trajectories,
        "trajectory_length": trajectory_length,
        "feature_columns": list(FEATURE_COLUMNS),
        "regimes": {},
    }

    ensure_directory(CPC_DATA_DIR)
    for offset, regime in enumerate(REGIME_CONFIGS):
        frame = _load_or_simulate_regime(
            regime_name=regime.name,
            seed=DEFAULT_SEED + 100 * offset,
            n_trajectories=n_trajectories,
            trajectory_length=trajectory_length,
            force_resimulate=force_resimulate,
        )
        node_matrix = _node_matrix_from_frame(frame, node_to_index)
        input_tensor = feature_matrix[node_matrix]

        np.save(trajectory_node_index_path(regime.name), node_matrix)
        np.save(trajectory_input_tensor_path(regime.name), input_tensor.astype(np.float32))

        outputs["regimes"][regime.name] = {
            "node_index_path": str(trajectory_node_index_path(regime.name)),
            "input_tensor_path": str(trajectory_input_tensor_path(regime.name)),
            "shape": [int(dim) for dim in input_tensor.shape],
            "seed": DEFAULT_SEED + 100 * offset,
        }

    save_json(TRAJECTORY_INPUT_METADATA_JSON, outputs)
    return outputs


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-trajectories", type=int, default=10_000, help="Trajectories per regime.")
    parser.add_argument("--trajectory-length", type=int, default=500, help="Steps per trajectory.")
    parser.add_argument(
        "--force-resimulate",
        action="store_true",
        help="Ignore cached CPC parquet trajectories and regenerate them.",
    )
    parser.add_argument("--smoke-test", action="store_true", help="Run with smaller tensors for a fast check.")
    return parser


def main() -> None:
    """CLI entry point with a small smoke configuration when requested."""

    parser = _build_parser()
    args = parser.parse_args()

    seed_everything(DEFAULT_SEED)
    n_trajectories = 32 if args.smoke_test else args.n_trajectories
    trajectory_length = 16 if args.smoke_test else args.trajectory_length
    outputs = generate_input_tensors(
        n_trajectories=n_trajectories,
        trajectory_length=trajectory_length,
        force_resimulate=args.force_resimulate,
    )

    for regime, payload in outputs["regimes"].items():
        shape = payload["shape"]
        if len(shape) != 3 or shape[2] != 8:
            raise SystemExit(f"{regime} tensor has unexpected shape: {shape}")

    print(
        "Saved O-SSM input tensors for "
        f"{len(outputs['regimes'])} regimes ({n_trajectories} trajectories x {trajectory_length} steps)."
    )


if __name__ == "__main__":
    main()
