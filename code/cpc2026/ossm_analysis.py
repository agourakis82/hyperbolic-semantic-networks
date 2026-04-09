"""Analyze O-SSM cognitive dynamics and compare them against the Markov baseline."""

from __future__ import annotations

import argparse
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from analysis import bootstrap_statistic, cohens_d, dfa_hurst_matrix
from common import (
    CPC_RESULTS_DIR,
    DEFAULT_SEED,
    REGIME_CONFIGS,
    STATISTICAL_SUMMARY_JSON,
    TRAJECTORY_STATS_PARQUET,
    load_node_metrics,
    save_json,
    seed_everything,
    summarize_ci,
)


OSSM_TRAJECTORY_STATS_PARQUET = CPC_RESULTS_DIR / "ossm_trajectory_statistics.parquet"
OSSM_STATISTICAL_SUMMARY_JSON = CPC_RESULTS_DIR / "ossm_statistical_summary.json"
OSSM_STEPWISE_SUMMARY_CSV = CPC_RESULTS_DIR / "ossm_stepwise_summary.csv"
OSSM_REGIME_SUMMARY_CSV = CPC_RESULTS_DIR / "ossm_regime_summary.csv"
OSSM_SUBSPACE_OCCUPANCY_CSV = CPC_RESULTS_DIR / "ossm_subspace_occupancy.csv"
OSSM_ATTRACTOR_SUMMARY_CSV = CPC_RESULTS_DIR / "ossm_attractor_summary.csv"
OSSM_CROSS_MODEL_CSV = CPC_RESULTS_DIR / "ossm_cross_model_comparison.csv"

HIDDEN_COMPONENT_COLUMNS: tuple[str, ...] = tuple(
    f"h{unit}_{component}" for unit in range(4) for component in range(8)
)
FANO_TRIPLES: tuple[tuple[str, tuple[int, int, int]], ...] = (
    ("H123", (1, 2, 3)),
    ("H145", (1, 4, 5)),
    ("H167", (1, 6, 7)),
    ("H246", (2, 4, 6)),
    ("H257", (2, 5, 7)),
    ("H347", (3, 4, 7)),
    ("H356", (3, 5, 6)),
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bootstrap", type=int, default=1_000, help="Bootstrap resamples for confidence intervals.")
    parser.add_argument("--smoke-test", action="store_true", help="Print a compact summary after writing outputs.")
    return parser.parse_args()


def _comparison_stats(
    baseline: pd.Series,
    candidate: pd.Series,
    n_bootstrap: int,
    seed_offset: int,
) -> dict[str, float | list[float]]:
    """Compute a concise comparison payload for two regimes."""

    x = baseline.to_numpy(dtype=float)
    y = candidate.to_numpy(dtype=float)
    effect = cohens_d(x, y)
    ci_low, ci_high = summarize_ci(
        bootstrap_statistic(x, y, cohens_d, n_bootstrap=n_bootstrap, seed=DEFAULT_SEED + seed_offset)
    )
    p_value = float(stats.ttest_ind(x, y, equal_var=False).pvalue)
    return {
        "cohens_d": float(effect),
        "ci": [ci_low, ci_high],
        "p_value": p_value,
        "baseline_mean": float(x.mean()),
        "candidate_mean": float(y.mean()),
    }


def _load_stepwise_ossm(regime: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load one regime's O-SSM CSV and derive trajectory-level matrices."""

    path = CPC_RESULTS_DIR / f"ossm_trajectories_{regime}.csv"
    frame = pd.read_csv(
        path,
        dtype={
            "trajectory_id": "int32",
            "step": "int16",
            "visited_node": "string",
            "C_ent": "float32",
            "C_ent_readout": "float32",
            "h_norm": "float32",
            "h_entropy": "float32",
            "h_associator_norm": "float32",
        },
    )

    n_trajectories = int(frame["trajectory_id"].max()) + 1
    trajectory_length = int(frame["step"].max()) + 1
    node_entropy = load_node_metrics().set_index("node")["entropy"].to_dict()
    visited_entropy = (
        frame["visited_node"].astype("string").map(node_entropy).fillna(0.0).to_numpy(dtype=np.float32)
    )

    payload = {
        "path": str(path),
        "n_trajectories": n_trajectories,
        "trajectory_length": trajectory_length,
        "c_ent_readout": frame["C_ent_readout"].to_numpy(dtype=np.float32).reshape(n_trajectories, trajectory_length),
        "h_norm": frame["h_norm"].to_numpy(dtype=np.float32).reshape(n_trajectories, trajectory_length),
        "h_entropy": frame["h_entropy"].to_numpy(dtype=np.float32).reshape(n_trajectories, trajectory_length),
        "h_associator_norm": frame["h_associator_norm"]
        .to_numpy(dtype=np.float32)
        .reshape(n_trajectories, trajectory_length),
        "visited_entropy": visited_entropy.reshape(n_trajectories, trajectory_length),
        "visited_nodes": frame["visited_node"].astype("string").to_numpy().reshape(n_trajectories, trajectory_length),
    }
    return frame, payload


def _load_hidden_samples(regime: str) -> np.ndarray:
    """Load sampled hidden states exported by the reference simulator."""

    path = CPC_RESULTS_DIR / f"ossm_state_samples_{regime}.parquet"
    if not path.exists():
        return np.empty((0, 0, 32), dtype=np.float32)

    frame = pd.read_parquet(path).sort_values(["trajectory_id", "step"], kind="mergesort")
    n_trajectories = int(frame["trajectory_id"].max()) + 1
    trajectory_length = int(frame["step"].max()) + 1
    return frame.loc[:, HIDDEN_COMPONENT_COLUMNS].to_numpy(dtype=np.float32).reshape(
        n_trajectories, trajectory_length, 32
    )


def _subspace_occupancy(hidden_samples: np.ndarray) -> np.ndarray:
    """Estimate occupancy across the seven canonical quaternionic subspaces."""

    if hidden_samples.size == 0:
        return np.zeros(len(FANO_TRIPLES), dtype=float)

    hidden = hidden_samples.reshape(hidden_samples.shape[0], hidden_samples.shape[1], 4, 8)
    squared = hidden**2
    energies = []
    for _, (i, j, k) in FANO_TRIPLES:
        energy = squared[..., 0].sum(axis=2)
        energy += squared[..., i].sum(axis=2)
        energy += squared[..., j].sum(axis=2)
        energy += squared[..., k].sum(axis=2)
        energies.append(energy)
    labels = np.stack(energies, axis=-1).argmax(axis=-1).reshape(-1)
    counts = np.bincount(labels, minlength=len(FANO_TRIPLES)).astype(float)
    return counts / counts.sum()


def _attractor_summary(hidden_samples: np.ndarray) -> dict[str, float]:
    """Approximate recurrence, fixed-point, and short-cycle tendencies."""

    if hidden_samples.size == 0:
        return {
            "recurrence_rate": 0.0,
            "fixed_point_fraction": 0.0,
            "limit_cycle_fraction": 0.0,
            "threshold": 0.0,
        }

    series = hidden_samples[:, ::5, :]
    diffs = np.linalg.norm(np.diff(series, axis=1), axis=2)
    threshold = float(np.quantile(diffs, 0.10))
    if threshold <= 0.0:
        threshold = 1e-6

    fixed_point = (diffs < threshold).mean(axis=1)
    if series.shape[1] >= 3:
        cycle_dist = np.linalg.norm(series[:, 2:, :] - series[:, :-2, :], axis=2)
        cycle_fraction = ((cycle_dist < threshold) & (diffs[:, 1:] >= threshold)).mean(axis=1)
    else:
        cycle_fraction = np.zeros(series.shape[0], dtype=float)

    recurrence = []
    for trajectory in series:
        distance = np.linalg.norm(trajectory[:, None, :] - trajectory[None, :, :], axis=2)
        mask = ~np.eye(distance.shape[0], dtype=bool)
        recurrence.append(float((distance[mask] < threshold).mean()))

    return {
        "recurrence_rate": float(np.mean(recurrence)),
        "fixed_point_fraction": float(fixed_point.mean()),
        "limit_cycle_fraction": float(cycle_fraction.mean()),
        "threshold": threshold,
    }


def _trajectory_summary(
    regime: str,
    payload: dict[str, Any],
    high_entropy_threshold: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute per-trajectory and per-step O-SSM summaries."""

    c_ent = payload["c_ent_readout"]
    h_norm = payload["h_norm"]
    h_entropy = payload["h_entropy"]
    associator = payload["h_associator_norm"]
    visited_entropy = payload["visited_entropy"]

    c_ent_variance = c_ent.var(axis=1, ddof=1)
    residence_fraction = (visited_entropy >= high_entropy_threshold).sum(axis=1) / visited_entropy.shape[1]
    hidden_entropy_production = np.abs(np.diff(h_entropy, axis=1)).mean(axis=1)
    hurst = dfa_hurst_matrix(c_ent)

    summary = pd.DataFrame(
        {
            "regime": regime,
            "trajectory_id": np.arange(c_ent.shape[0], dtype=np.int32),
            "c_ent_variance": c_ent_variance,
            "residence_fraction_high_entropy": residence_fraction,
            "hidden_entropy_production_rate": hidden_entropy_production,
            "hurst_exponent": hurst,
            "mean_c_ent_readout": c_ent.mean(axis=1),
            "mean_h_norm": h_norm.mean(axis=1),
            "mean_h_entropy": h_entropy.mean(axis=1),
            "mean_associator_norm": associator.mean(axis=1),
        }
    )

    stepwise = pd.DataFrame(
        {
            "regime": regime,
            "step": np.arange(c_ent.shape[1], dtype=np.int16),
            "mean_c_ent_readout": c_ent.mean(axis=0),
            "mean_h_norm": h_norm.mean(axis=0),
            "mean_h_entropy": h_entropy.mean(axis=0),
            "mean_associator_norm": associator.mean(axis=0),
        }
    )
    return summary, stepwise


def main() -> None:
    """Run O-SSM analysis and write the comparison artifacts."""

    args = parse_args()
    seed_everything(DEFAULT_SEED)

    node_metrics = load_node_metrics()
    high_entropy_threshold = float(node_metrics["entropy"].quantile(0.9))
    baseline_stats = pd.read_parquet(TRAJECTORY_STATS_PARQUET)
    trajectory_frames: list[pd.DataFrame] = []
    stepwise_frames: list[pd.DataFrame] = []
    regime_rows: list[dict[str, Any]] = []
    occupancy_rows: list[dict[str, Any]] = []
    attractor_rows: list[dict[str, Any]] = []
    summary_payload: dict[str, Any] = {
        "seed": DEFAULT_SEED,
        "high_entropy_threshold": high_entropy_threshold,
        "per_regime": {},
        "comparisons": {},
        "cross_model": {},
    }

    for offset, regime_cfg in enumerate(REGIME_CONFIGS):
        regime = regime_cfg.name
        _, payload = _load_stepwise_ossm(regime)
        summary, stepwise = _trajectory_summary(regime, payload, high_entropy_threshold)
        hidden_samples = _load_hidden_samples(regime)
        occupancy = _subspace_occupancy(hidden_samples)
        attractor = _attractor_summary(hidden_samples)

        trajectory_frames.append(summary)
        stepwise_frames.append(stepwise)

        variance_ci = summarize_ci(
            bootstrap_statistic(
                summary["c_ent_variance"].to_numpy(),
                None,
                lambda sample: float(sample.mean()),
                n_bootstrap=args.bootstrap,
                seed=DEFAULT_SEED + offset,
            )
        )
        residence_ci = summarize_ci(
            bootstrap_statistic(
                summary["residence_fraction_high_entropy"].to_numpy(),
                None,
                lambda sample: float(sample.mean()),
                n_bootstrap=args.bootstrap,
                seed=DEFAULT_SEED + 100 + offset,
            )
        )
        entropy_ci = summarize_ci(
            bootstrap_statistic(
                summary["hidden_entropy_production_rate"].to_numpy(),
                None,
                lambda sample: float(sample.mean()),
                n_bootstrap=args.bootstrap,
                seed=DEFAULT_SEED + 200 + offset,
            )
        )
        hurst_ci = summarize_ci(
            bootstrap_statistic(
                summary["hurst_exponent"].dropna().to_numpy(),
                None,
                lambda sample: float(sample.mean()),
                n_bootstrap=args.bootstrap,
                seed=DEFAULT_SEED + 300 + offset,
            )
        )
        assoc_ci = summarize_ci(
            bootstrap_statistic(
                summary["mean_associator_norm"].to_numpy(),
                None,
                lambda sample: float(sample.mean()),
                n_bootstrap=args.bootstrap,
                seed=DEFAULT_SEED + 400 + offset,
            )
        )
        hidden_ci = summarize_ci(
            bootstrap_statistic(
                summary["mean_h_entropy"].to_numpy(),
                None,
                lambda sample: float(sample.mean()),
                n_bootstrap=args.bootstrap,
                seed=DEFAULT_SEED + 500 + offset,
            )
        )

        occupancy_payload = {label: float(value) for (label, _), value in zip(FANO_TRIPLES, occupancy, strict=True)}
        per_regime_payload = {
            "n_trajectories": int(len(summary)),
            "mean_c_ent_variance": float(summary["c_ent_variance"].mean()),
            "ci_c_ent_variance": [variance_ci[0], variance_ci[1]],
            "mean_residence_fraction_high_entropy": float(summary["residence_fraction_high_entropy"].mean()),
            "ci_residence_fraction_high_entropy": [residence_ci[0], residence_ci[1]],
            "mean_hidden_entropy_production_rate": float(summary["hidden_entropy_production_rate"].mean()),
            "ci_hidden_entropy_production_rate": [entropy_ci[0], entropy_ci[1]],
            "mean_hurst_exponent": float(summary["hurst_exponent"].mean()),
            "ci_hurst_exponent": [hurst_ci[0], hurst_ci[1]],
            "mean_associator_norm": float(summary["mean_associator_norm"].mean()),
            "ci_mean_associator_norm": [assoc_ci[0], assoc_ci[1]],
            "mean_h_entropy": float(summary["mean_h_entropy"].mean()),
            "ci_mean_h_entropy": [hidden_ci[0], hidden_ci[1]],
            "subspace_occupancy": occupancy_payload,
            "attractor_summary": attractor,
        }
        summary_payload["per_regime"][regime] = per_regime_payload

        regime_rows.append(
            {
                "regime": regime,
                "mean_c_ent_variance": per_regime_payload["mean_c_ent_variance"],
                "mean_residence_fraction_high_entropy": per_regime_payload["mean_residence_fraction_high_entropy"],
                "mean_hidden_entropy_production_rate": per_regime_payload["mean_hidden_entropy_production_rate"],
                "mean_hurst_exponent": per_regime_payload["mean_hurst_exponent"],
                "mean_associator_norm": per_regime_payload["mean_associator_norm"],
                "mean_h_entropy": per_regime_payload["mean_h_entropy"],
            }
        )
        for label, value in occupancy_payload.items():
            occupancy_rows.append({"regime": regime, "subspace": label, "occupancy": value})
        attractor_rows.append({"regime": regime, **attractor})

    trajectory_stats = pd.concat(trajectory_frames, ignore_index=True)
    stepwise_summary = pd.concat(stepwise_frames, ignore_index=True)
    regime_summary = pd.DataFrame(regime_rows)
    occupancy_summary = pd.DataFrame(occupancy_rows)
    attractor_summary = pd.DataFrame(attractor_rows)

    normative_ossm = trajectory_stats.loc[trajectory_stats["regime"] == "normative"]
    anxious_ossm = trajectory_stats.loc[trajectory_stats["regime"] == "anxious"]
    normative_markov = baseline_stats.loc[baseline_stats["regime"] == "normative"]
    anxious_markov = baseline_stats.loc[baseline_stats["regime"] == "anxious"]

    ossm_comparisons = {
        "normative_vs_anxious_c_ent_variance": _comparison_stats(
            normative_ossm["c_ent_variance"], anxious_ossm["c_ent_variance"], args.bootstrap, 900
        ),
        "normative_vs_anxious_hurst_exponent": _comparison_stats(
            normative_ossm["hurst_exponent"], anxious_ossm["hurst_exponent"], args.bootstrap, 901
        ),
        "normative_vs_anxious_residence_fraction_high_entropy": _comparison_stats(
            normative_ossm["residence_fraction_high_entropy"],
            anxious_ossm["residence_fraction_high_entropy"],
            args.bootstrap,
            902,
        ),
        "normative_vs_anxious_hidden_entropy_production_rate": _comparison_stats(
            normative_ossm["hidden_entropy_production_rate"],
            anxious_ossm["hidden_entropy_production_rate"],
            args.bootstrap,
            903,
        ),
        "normative_vs_anxious_mean_associator_norm": _comparison_stats(
            normative_ossm["mean_associator_norm"], anxious_ossm["mean_associator_norm"], args.bootstrap, 904
        ),
    }
    summary_payload["comparisons"] = ossm_comparisons

    cross_model_rows = [
        {
            "metric": "C_ent variance",
            "markov_metric": "c_ent_variance",
            "ossm_metric": "c_ent_variance",
            "markov_d": float(cohens_d(normative_markov["c_ent_variance"], anxious_markov["c_ent_variance"])),
            "ossm_d": float(cohens_d(normative_ossm["c_ent_variance"], anxious_ossm["c_ent_variance"])),
            "markov_normative_mean": float(normative_markov["c_ent_variance"].mean()),
            "markov_anxious_mean": float(anxious_markov["c_ent_variance"].mean()),
            "ossm_normative_mean": float(normative_ossm["c_ent_variance"].mean()),
            "ossm_anxious_mean": float(anxious_ossm["c_ent_variance"].mean()),
            "note": "Directly comparable trajectory-level C_ent variance.",
        },
        {
            "metric": "Hurst exponent",
            "markov_metric": "hurst_exponent",
            "ossm_metric": "hurst_exponent",
            "markov_d": float(cohens_d(normative_markov["hurst_exponent"], anxious_markov["hurst_exponent"])),
            "ossm_d": float(cohens_d(normative_ossm["hurst_exponent"], anxious_ossm["hurst_exponent"])),
            "markov_normative_mean": float(normative_markov["hurst_exponent"].mean()),
            "markov_anxious_mean": float(anxious_markov["hurst_exponent"].mean()),
            "ossm_normative_mean": float(normative_ossm["hurst_exponent"].mean()),
            "ossm_anxious_mean": float(anxious_ossm["hurst_exponent"].mean()),
            "note": "Directly comparable DFA on the model output series.",
        },
        {
            "metric": "Residence in high-entropy hubs",
            "markov_metric": "residence_fraction_high_entropy",
            "ossm_metric": "residence_fraction_high_entropy",
            "markov_d": float(
                cohens_d(
                    normative_markov["residence_fraction_high_entropy"],
                    anxious_markov["residence_fraction_high_entropy"],
                )
            ),
            "ossm_d": float(
                cohens_d(
                    normative_ossm["residence_fraction_high_entropy"],
                    anxious_ossm["residence_fraction_high_entropy"],
                )
            ),
            "markov_normative_mean": float(normative_markov["residence_fraction_high_entropy"].mean()),
            "markov_anxious_mean": float(anxious_markov["residence_fraction_high_entropy"].mean()),
            "ossm_normative_mean": float(normative_ossm["residence_fraction_high_entropy"].mean()),
            "ossm_anxious_mean": float(anxious_ossm["residence_fraction_high_entropy"].mean()),
            "note": "Inherited from the input walk under the current no-training O-SSM setup.",
        },
        {
            "metric": "Entropy production",
            "markov_metric": "entropy_production_rate",
            "ossm_metric": "hidden_entropy_production_rate",
            "markov_d": float(
                cohens_d(normative_markov["entropy_production_rate"], anxious_markov["entropy_production_rate"])
            ),
            "ossm_d": float(
                cohens_d(
                    normative_ossm["hidden_entropy_production_rate"],
                    anxious_ossm["hidden_entropy_production_rate"],
                )
            ),
            "markov_normative_mean": float(normative_markov["entropy_production_rate"].mean()),
            "markov_anxious_mean": float(anxious_markov["entropy_production_rate"].mean()),
            "ossm_normative_mean": float(normative_ossm["hidden_entropy_production_rate"].mean()),
            "ossm_anxious_mean": float(anxious_ossm["hidden_entropy_production_rate"].mean()),
            "note": "Markov uses visited-node entropy; O-SSM uses hidden-state entropy.",
        },
    ]
    cross_model = pd.DataFrame(cross_model_rows)
    summary_payload["cross_model"] = {
        row["metric"]: {"markov_d": row["markov_d"], "ossm_d": row["ossm_d"], "note": row["note"]}
        for row in cross_model_rows
    }
    summary_payload["baseline_markov_summary_path"] = str(STATISTICAL_SUMMARY_JSON)

    trajectory_stats.to_parquet(OSSM_TRAJECTORY_STATS_PARQUET, index=False)
    stepwise_summary.to_csv(OSSM_STEPWISE_SUMMARY_CSV, index=False)
    regime_summary.to_csv(OSSM_REGIME_SUMMARY_CSV, index=False)
    occupancy_summary.to_csv(OSSM_SUBSPACE_OCCUPANCY_CSV, index=False)
    attractor_summary.to_csv(OSSM_ATTRACTOR_SUMMARY_CSV, index=False)
    cross_model.to_csv(OSSM_CROSS_MODEL_CSV, index=False)
    save_json(OSSM_STATISTICAL_SUMMARY_JSON, summary_payload)

    if args.smoke_test:
        print(regime_summary.to_string(index=False))
        return

    print(
        "Saved O-SSM statistics to "
        f"{OSSM_TRAJECTORY_STATS_PARQUET} and comparison summary to {OSSM_STATISTICAL_SUMMARY_JSON}."
    )


if __name__ == "__main__":
    main()
