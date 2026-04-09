"""Reference O-SSM simulator for CPC 2026 cognitive trajectories.

This Python implementation mirrors the intended canonical Sounio architecture:

    h_{t+1}^{(i)} = sigma(A_i * h_t^{(i)} * B_i + C_i * x_t + residual * h_t^{(i)})

with 4 octonionic hidden units, regime-specific temperature / initial-state /
valence-gate settings, and a scalar readout that produces a state-conditioned
entropic-curvature signal. It exists because the canonical Sounio repo has the
necessary octonion primitives but not a recoverable full O-SSM benchmark stack.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.append(str(SCRIPT_DIR))

from common import (  # noqa: E402
    CPC_RESULTS_DIR,
    DEFAULT_SEED,
    REGIME_CONFIGS,
    ensure_directory,
    load_node_metrics,
    save_json,
    trajectory_input_tensor_path,
    trajectory_node_index_path,
)
from ossm_bridge.node_features import NODE_FEATURES_CSV, NODE_FEATURES_METADATA_JSON  # noqa: E402


OSSM_SUMMARY_JSON = CPC_RESULTS_DIR / "ossm_simulation_summary.json"
OSSM_TRAJECTORY_SUMMARY_PARQUET = CPC_RESULTS_DIR / "ossm_trajectory_statistics.parquet"


@dataclass(frozen=True)
class OssmRegimeConfig:
    """Regime-specific configuration for the reference O-SSM."""

    name: str
    temperature: float
    initial_state_mode: str
    valence_gate: float


OSSM_REGIMES: tuple[OssmRegimeConfig, ...] = (
    OssmRegimeConfig("normative", temperature=0.5, initial_state_mode="balanced", valence_gate=1.0),
    OssmRegimeConfig("anxious", temperature=2.0, initial_state_mode="negative_attractor", valence_gate=2.0),
    OssmRegimeConfig("ruminative", temperature=0.3, initial_state_mode="rigid", valence_gate=1.5),
    OssmRegimeConfig("psychotic", temperature=5.0, initial_state_mode="dispersed", valence_gate=0.5),
)


def oct_mul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Broadcasted octonion multiplication over the last axis."""

    a0, a1, a2, a3, a4, a5, a6, a7 = np.moveaxis(a, -1, 0)
    b0, b1, b2, b3, b4, b5, b6, b7 = np.moveaxis(b, -1, 0)
    return np.stack(
        [
            a0 * b0 - a1 * b1 - a2 * b2 - a3 * b3 - a4 * b4 - a5 * b5 - a6 * b6 - a7 * b7,
            a0 * b1 + a1 * b0 + a2 * b3 - a3 * b2 + a4 * b5 - a5 * b4 - a6 * b7 + a7 * b6,
            a0 * b2 - a1 * b3 + a2 * b0 + a3 * b1 + a4 * b6 + a5 * b7 - a6 * b4 - a7 * b5,
            a0 * b3 + a1 * b2 - a2 * b1 + a3 * b0 + a4 * b7 - a5 * b6 + a6 * b5 - a7 * b4,
            a0 * b4 - a1 * b5 - a2 * b6 - a3 * b7 + a4 * b0 + a5 * b1 + a6 * b2 + a7 * b3,
            a0 * b5 + a1 * b4 - a2 * b7 + a3 * b6 - a4 * b1 + a5 * b0 - a6 * b3 + a7 * b2,
            a0 * b6 + a1 * b7 + a2 * b4 - a3 * b5 - a4 * b2 + a5 * b3 + a6 * b0 - a7 * b1,
            a0 * b7 - a1 * b6 + a2 * b5 + a3 * b4 - a4 * b3 - a5 * b2 + a6 * b1 + a7 * b0,
        ],
        axis=-1,
    )


def oct_associator(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    """Broadcasted octonion associator [a, b, c] = (ab)c - a(bc)."""

    return oct_mul(oct_mul(a, b), c) - oct_mul(a, oct_mul(b, c))


def oct_softsign(values: np.ndarray, temperature: float) -> np.ndarray:
    """Stable component-wise activation used by the deterministic O-SSM."""

    scaled = values / max(temperature, 1e-6)
    return scaled / (1.0 + np.abs(scaled))


def hidden_entropy(hidden: np.ndarray) -> np.ndarray:
    """Normalized Shannon entropy of component magnitudes across the 32D hidden state."""

    magnitudes = np.abs(hidden).reshape(hidden.shape[0], -1)
    totals = magnitudes.sum(axis=1, keepdims=True)
    probabilities = np.divide(
        magnitudes,
        totals,
        out=np.full_like(magnitudes, 1.0 / magnitudes.shape[1]),
        where=totals > 0.0,
    )
    entropy = -np.sum(np.where(probabilities > 0.0, probabilities * np.log(probabilities), 0.0), axis=1)
    return entropy / np.log(probabilities.shape[1])


def _base_parameters() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Deterministic structured octonionic parameters for the no-training reference."""

    A = np.array(
        [
            [0.82, 0.14, 0.04, 0.00, 0.05, 0.02, 0.00, 0.01],
            [0.78, 0.00, 0.16, 0.06, 0.00, 0.03, 0.02, 0.00],
            [0.80, 0.03, 0.00, 0.18, 0.04, 0.00, 0.02, 0.01],
            [0.76, 0.05, 0.04, 0.00, 0.14, 0.02, 0.03, 0.02],
        ],
        dtype=np.float32,
    )
    B = np.array(
        [
            [0.91, 0.03, 0.02, 0.00, 0.00, 0.01, 0.00, 0.00],
            [0.89, 0.00, 0.04, 0.02, 0.00, 0.00, 0.01, 0.00],
            [0.90, 0.01, 0.00, 0.05, 0.02, 0.00, 0.00, 0.01],
            [0.88, 0.02, 0.01, 0.00, 0.04, 0.01, 0.00, 0.00],
        ],
        dtype=np.float32,
    )
    C = np.array(
        [
            [0.45, 0.08, 0.03, 0.12, 0.04, 0.04, 0.02, 0.01],
            [0.42, 0.02, 0.09, 0.08, 0.03, 0.04, 0.04, 0.02],
            [0.40, 0.03, 0.02, 0.14, 0.05, 0.02, 0.04, 0.03],
            [0.44, 0.05, 0.04, 0.04, 0.11, 0.03, 0.03, 0.02],
        ],
        dtype=np.float32,
    )
    D = np.array(
        [
            [0.55, 0.10, 0.04, 0.18, 0.02, 0.01, 0.00, 0.00],
            [0.50, 0.02, 0.12, 0.14, 0.03, 0.01, 0.01, 0.00],
            [0.53, 0.03, 0.02, 0.20, 0.02, 0.00, 0.01, 0.01],
            [0.48, 0.04, 0.03, 0.10, 0.11, 0.01, 0.00, 0.02],
        ],
        dtype=np.float32,
    )
    return A, B, C, D


def initialize_hidden_state(
    regime: OssmRegimeConfig,
    batch_size: int,
    hidden_dim: int,
    seed: int,
) -> np.ndarray:
    """Construct the regime-specific octonionic initial hidden state."""

    rng = np.random.default_rng(seed)
    hidden = np.zeros((batch_size, hidden_dim, 8), dtype=np.float32)

    if regime.initial_state_mode == "balanced":
        hidden[:] = np.array(
            [
                [0.28, 0.08, 0.08, 0.04, 0.04, 0.02, 0.02, 0.01],
                [0.24, 0.02, 0.09, 0.06, 0.04, 0.03, 0.02, 0.01],
                [0.26, 0.03, 0.04, 0.09, 0.03, 0.02, 0.03, 0.01],
                [0.25, 0.04, 0.03, 0.03, 0.09, 0.02, 0.02, 0.02],
            ],
            dtype=np.float32,
        )
    elif regime.initial_state_mode == "negative_attractor":
        hidden[:] = np.array(
            [
                [-0.12, 0.02, 0.04, -0.28, 0.02, 0.00, 0.00, 0.00],
                [-0.10, 0.01, 0.03, -0.24, 0.01, 0.00, 0.01, 0.00],
                [-0.11, 0.02, 0.02, -0.26, 0.01, 0.01, 0.00, 0.00],
                [-0.09, 0.01, 0.02, -0.22, 0.02, 0.00, 0.00, 0.01],
            ],
            dtype=np.float32,
        )
    elif regime.initial_state_mode == "rigid":
        hidden[:] = np.array(
            [
                [0.35, 0.10, 0.08, 0.03, 0.00, 0.00, 0.00, 0.00],
                [0.31, 0.06, 0.09, 0.02, 0.00, 0.00, 0.00, 0.00],
                [0.29, 0.08, 0.06, 0.04, 0.00, 0.00, 0.00, 0.00],
                [0.33, 0.07, 0.07, 0.03, 0.00, 0.00, 0.00, 0.00],
            ],
            dtype=np.float32,
        )
    else:
        hidden = rng.normal(loc=0.0, scale=0.12, size=(batch_size, hidden_dim, 8)).astype(np.float32)

    return hidden


def run_regime_reference(
    regime: OssmRegimeConfig,
    node_table: pd.DataFrame,
    chunk_size: int,
    sample_trajectories: int,
    max_trajectories: int | None = None,
    max_steps: int | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Run the reference O-SSM for one regime and write per-step CSV output."""

    A, B, C, D = _base_parameters()
    input_tensor = np.load(trajectory_input_tensor_path(regime.name), mmap_mode="r")
    node_indices = np.load(trajectory_node_index_path(regime.name), mmap_mode="r")

    n_trajectories, trajectory_length, _ = input_tensor.shape
    if max_trajectories is not None:
        n_trajectories = min(n_trajectories, max_trajectories)
    if max_steps is not None:
        trajectory_length = min(trajectory_length, max_steps)
    node_labels = node_table["node"].to_numpy()
    raw_c_ent = node_table["C_ent"].to_numpy(dtype=np.float32)
    raw_entropy = node_table["entropy"].to_numpy(dtype=np.float32)

    output_csv = CPC_RESULTS_DIR / f"ossm_trajectories_{regime.name}.csv"
    sample_parquet = CPC_RESULTS_DIR / f"ossm_state_samples_{regime.name}.parquet"
    ensure_directory(output_csv.parent)
    output_csv.write_text(
        "trajectory_id,step,visited_node,C_ent,C_ent_readout,h_norm,h_entropy,h_associator_norm\n",
        encoding="utf-8",
    )

    summary_rows: list[pd.DataFrame] = []
    sample_rows: list[pd.DataFrame] = []
    coupling = 0.18
    residual = 0.22

    for start in range(0, n_trajectories, chunk_size):
        stop = min(start + chunk_size, n_trajectories)
        features = np.asarray(input_tensor[start:stop, :trajectory_length], dtype=np.float32)
        chunk_nodes = np.asarray(node_indices[start:stop, :trajectory_length], dtype=np.int32)
        batch_size = stop - start
        hidden = initialize_hidden_state(regime, batch_size, hidden_dim=4, seed=DEFAULT_SEED + start)

        h_norm_series = np.empty((batch_size, trajectory_length), dtype=np.float32)
        h_entropy_series = np.empty((batch_size, trajectory_length), dtype=np.float32)
        assoc_series = np.empty((batch_size, trajectory_length), dtype=np.float32)
        readout_series = np.empty((batch_size, trajectory_length), dtype=np.float32)
        raw_c_ent_series = raw_c_ent[chunk_nodes]
        raw_entropy_series = raw_entropy[chunk_nodes]

        for step in range(trajectory_length):
            x_t = features[:, step, :].copy()
            x_t[:, 3] *= regime.valence_gate
            prev_hidden = hidden
            mixed_hidden = hidden + coupling * hidden.mean(axis=1, keepdims=True)
            preactivation = oct_mul(oct_mul(A[None, :, :], mixed_hidden), B[None, :, :])
            preactivation += oct_mul(C[None, :, :], x_t[:, None, :])
            preactivation += residual * hidden
            hidden = oct_softsign(preactivation, regime.temperature)

            assoc = oct_associator(hidden, x_t[:, None, :], prev_hidden)
            assoc_norm = np.linalg.norm(assoc, axis=2).mean(axis=1)
            state_norm = np.linalg.norm(hidden.reshape(batch_size, -1), axis=1)
            state_entropy = hidden_entropy(hidden)

            read_oct = oct_mul(hidden, D[None, :, :])
            read_signal = read_oct[..., 0].mean(axis=1) + 0.25 * read_oct[..., 3].mean(axis=1)
            readout = raw_c_ent_series[:, step]
            readout += 0.18 * np.tanh(read_signal)
            readout += 0.08 * assoc_norm * np.sign(x_t[:, 3])
            readout -= 0.05 * (state_entropy - 0.5)
            readout = np.clip(readout, -1.0, 1.0)

            h_norm_series[:, step] = state_norm
            h_entropy_series[:, step] = state_entropy
            assoc_series[:, step] = assoc_norm.astype(np.float32)
            readout_series[:, step] = readout.astype(np.float32)

            if start < sample_trajectories:
                sample_stop = min(stop, sample_trajectories)
                sample_hidden = hidden[: sample_stop - start]
                sample_frame = pd.DataFrame(
                    {
                        "trajectory_id": np.repeat(np.arange(start, sample_stop), 1),
                        "step": step,
                    }
                )
                for unit in range(4):
                    for component in range(8):
                        sample_frame[f"h{unit}_{component}"] = sample_hidden[:, unit, component]
                sample_frame["C_ent_readout"] = readout_series[: sample_stop - start, step]
                sample_frame["h_associator_norm"] = assoc_series[: sample_stop - start, step]
                sample_rows.append(sample_frame)

        frame = pd.DataFrame(
            {
                "trajectory_id": np.repeat(np.arange(start, stop, dtype=np.int32), trajectory_length),
                "step": np.tile(np.arange(trajectory_length, dtype=np.int16), batch_size),
                "visited_node": node_labels[chunk_nodes.reshape(-1)],
                "C_ent": raw_c_ent_series.reshape(-1),
                "C_ent_readout": readout_series.reshape(-1),
                "h_norm": h_norm_series.reshape(-1),
                "h_entropy": h_entropy_series.reshape(-1),
                "h_associator_norm": assoc_series.reshape(-1),
            }
        )
        frame.to_csv(output_csv, mode="a", header=False, index=False, float_format="%.6f")

        summary_rows.append(
            pd.DataFrame(
                {
                    "regime": regime.name,
                    "trajectory_id": np.arange(start, stop, dtype=np.int32),
                    "c_ent_variance": readout_series.var(axis=1, ddof=1).astype(np.float32),
                    "mean_c_ent_readout": readout_series.mean(axis=1).astype(np.float32),
                    "mean_h_norm": h_norm_series.mean(axis=1).astype(np.float32),
                    "mean_h_entropy": h_entropy_series.mean(axis=1).astype(np.float32),
                    "mean_associator_norm": assoc_series.mean(axis=1).astype(np.float32),
                    "mean_input_entropy": raw_entropy_series.mean(axis=1).astype(np.float32),
                }
            )
        )

    summary = pd.concat(summary_rows, ignore_index=True)
    summary.to_parquet(CPC_RESULTS_DIR / f"ossm_trajectory_summary_{regime.name}.parquet", index=False)
    if sample_rows:
        pd.concat(sample_rows, ignore_index=True).to_parquet(sample_parquet, index=False)

    payload = {
        "output_csv": str(output_csv),
        "summary_parquet": str(CPC_RESULTS_DIR / f"ossm_trajectory_summary_{regime.name}.parquet"),
        "sample_parquet": str(sample_parquet),
        "n_trajectories": int(n_trajectories),
        "trajectory_length": int(trajectory_length),
        "chunk_size": int(chunk_size),
    }
    return summary, payload


def simulate_reference_ossm(
    chunk_size: int = 512,
    sample_trajectories: int = 64,
    max_trajectories: int | None = None,
    max_steps: int | None = None,
) -> dict[str, Any]:
    """Run all regimes and save a combined summary payload."""

    node_table = pd.read_csv(NODE_FEATURES_CSV)
    summaries: list[pd.DataFrame] = []
    payload: dict[str, Any] = {
        "seed": DEFAULT_SEED,
        "max_trajectories": max_trajectories,
        "max_steps": max_steps,
        "regimes": {},
    }

    for regime in OSSM_REGIMES:
        summary, regime_payload = run_regime_reference(
            regime=regime,
            node_table=node_table,
            chunk_size=chunk_size,
            sample_trajectories=sample_trajectories,
            max_trajectories=max_trajectories,
            max_steps=max_steps,
        )
        summaries.append(summary)
        payload["regimes"][regime.name] = regime_payload

    combined = pd.concat(summaries, ignore_index=True)
    combined.to_parquet(OSSM_TRAJECTORY_SUMMARY_PARQUET, index=False)
    payload["combined_summary_parquet"] = str(OSSM_TRAJECTORY_SUMMARY_PARQUET)
    save_json(OSSM_SUMMARY_JSON, payload)
    return payload


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunk-size", type=int, default=512, help="Trajectories processed per chunk.")
    parser.add_argument(
        "--sample-trajectories",
        type=int,
        default=64,
        help="Number of trajectories per regime for hidden-state sample exports.",
    )
    parser.add_argument(
        "--max-trajectories",
        type=int,
        default=None,
        help="Optional cap on trajectories per regime (useful for smoke and parity runs).",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=None,
        help="Optional cap on steps per trajectory (useful for smoke and parity runs).",
    )
    parser.add_argument("--smoke-test", action="store_true", help="Run on 64 trajectories x 32 steps.")
    return parser


def main() -> None:
    """CLI entry point."""

    parser = _build_parser()
    args = parser.parse_args()

    if args.smoke_test:
        args.chunk_size = min(args.chunk_size, 64)
        args.sample_trajectories = min(args.sample_trajectories, 8)
        args.max_trajectories = 64 if args.max_trajectories is None else min(args.max_trajectories, 64)
        args.max_steps = 32 if args.max_steps is None else min(args.max_steps, 32)

    payload = simulate_reference_ossm(
        chunk_size=args.chunk_size,
        sample_trajectories=args.sample_trajectories,
        max_trajectories=args.max_trajectories,
        max_steps=args.max_steps,
    )
    print(
        "Saved reference O-SSM outputs for "
        f"{len(payload['regimes'])} regimes to {CPC_RESULTS_DIR}."
    )


if __name__ == "__main__":
    main()
