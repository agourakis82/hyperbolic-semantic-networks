"""Compute CPC 2026 trajectory statistics and validate abstract-facing claims."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from common import (
    CPC_RESULTS_DIR,
    DEFAULT_SEED,
    ENTROPY_PRODUCTION_CSV,
    EXAMPLE_TRAJECTORIES_PARQUET,
    REGIME_CONFIGS,
    REGIME_SUMMARY_CSV,
    STATISTICAL_SUMMARY_JSON,
    STEPWISE_SUMMARY_CSV,
    TRAJECTORY_STATS_PARQUET,
    graph_eta,
    infer_critical_eta,
    load_node_metrics,
    load_phase_transition_reference,
    load_swow_en_graph,
    save_json,
    seed_everything,
    summarize_ci,
    to_step_matrix,
    trajectory_path,
)


def cohens_d(x: np.ndarray, y: np.ndarray) -> float:
    """Compute Cohen's d for two independent samples."""

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    pooled = np.sqrt(((len(x) - 1) * x.var(ddof=1) + (len(y) - 1) * y.var(ddof=1)) / (len(x) + len(y) - 2))
    if pooled == 0.0:
        return 0.0
    return float((y.mean() - x.mean()) / pooled)


def bootstrap_statistic(
    x: np.ndarray,
    y: np.ndarray | None,
    statistic,
    n_bootstrap: int = 1_000,
    seed: int = DEFAULT_SEED,
) -> np.ndarray:
    """Bootstrap a scalar statistic over one or two samples."""

    rng = np.random.default_rng(seed)
    draws = np.empty(n_bootstrap, dtype=float)
    for idx in range(n_bootstrap):
        x_sample = x[rng.integers(0, len(x), size=len(x))]
        if y is None:
            draws[idx] = statistic(x_sample)
        else:
            y_sample = y[rng.integers(0, len(y), size=len(y))]
            draws[idx] = statistic(x_sample, y_sample)
    return draws


def dfa_hurst(series: np.ndarray) -> float:
    """Estimate the Hurst exponent via detrended fluctuation analysis."""

    x = np.asarray(series, dtype=float)
    if np.allclose(x, x[0]):
        return 0.5

    profile = np.cumsum(x - x.mean())
    n_points = len(profile)
    scales = np.unique(np.floor(np.logspace(np.log10(4), np.log10(n_points // 4), num=8)).astype(int))
    fluctuation = []
    valid_scales = []
    grid_cache: dict[int, np.ndarray] = {}

    for scale in scales:
        n_segments = n_points // scale
        if n_segments < 2:
            continue
        trimmed = profile[: n_segments * scale].reshape(n_segments, scale)
        grid = grid_cache.setdefault(scale, np.arange(scale, dtype=float))
        rms_values = []
        for segment in trimmed:
            slope, intercept = np.polyfit(grid, segment, 1)
            trend = slope * grid + intercept
            rms = np.sqrt(np.mean((segment - trend) ** 2))
            if rms > 0.0:
                rms_values.append(rms)
        if rms_values:
            valid_scales.append(scale)
            fluctuation.append(float(np.mean(rms_values)))

    if len(valid_scales) < 2:
        return float("nan")
    slope, _ = np.polyfit(np.log(valid_scales), np.log(fluctuation), 1)
    return float(slope)


def dfa_hurst_matrix(matrix: np.ndarray) -> np.ndarray:
    """Estimate Hurst exponents for many trajectories at once via vectorized DFA."""

    values = np.asarray(matrix, dtype=float)
    if values.ndim == 1:
        return np.array([dfa_hurst(values)], dtype=float)

    n_trajectories, n_points = values.shape
    if n_points < 8:
        return np.full(n_trajectories, np.nan, dtype=float)

    profile = np.cumsum(values - values.mean(axis=1, keepdims=True), axis=1)
    constant_mask = np.all(np.isclose(values, values[:, :1]), axis=1)

    scales = np.unique(np.floor(np.logspace(np.log10(4), np.log10(n_points // 4), num=8)).astype(int))
    fluctuation_columns: list[np.ndarray] = []
    valid_scales: list[int] = []

    for scale in scales:
        n_segments = n_points // scale
        if n_segments < 2:
            continue
        segments = profile[:, : n_segments * scale].reshape(n_trajectories, n_segments, scale)
        x = np.arange(scale, dtype=float)
        x_mean = float(x.mean())
        x_centered = x - x_mean
        denominator = float(np.sum(x_centered**2))

        segment_means = segments.mean(axis=2, keepdims=True)
        slopes = np.sum((segments - segment_means) * x_centered[None, None, :], axis=2) / denominator
        intercepts = segment_means.squeeze(axis=2) - slopes * x_mean
        trends = slopes[:, :, None] * x[None, None, :] + intercepts[:, :, None]
        residuals = segments - trends
        rms = np.sqrt(np.mean(residuals**2, axis=2))
        fluctuation_columns.append(np.clip(rms.mean(axis=1), 1e-12, None))
        valid_scales.append(scale)

    if len(valid_scales) < 2:
        hurst = np.full(n_trajectories, np.nan, dtype=float)
        hurst[constant_mask] = 0.5
        return hurst

    log_scales = np.log(np.asarray(valid_scales, dtype=float))
    log_fluctuation = np.log(np.stack(fluctuation_columns, axis=1))

    x_mean = float(log_scales.mean())
    x_centered = log_scales - x_mean
    denominator = float(np.sum(x_centered**2))
    y_mean = log_fluctuation.mean(axis=1, keepdims=True)
    slopes = np.sum((log_fluctuation - y_mean) * x_centered[None, :], axis=1) / denominator
    slopes[constant_mask] = 0.5
    return slopes


def summarize_regime(
    regime: str,
    frame: pd.DataFrame,
    high_entropy_threshold: float,
    n_bootstrap: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute per-trajectory and per-step summaries for one regime."""

    c_ent = to_step_matrix(frame, "C_ent")
    entropy = to_step_matrix(frame, "entropy")
    kappa = to_step_matrix(frame, "kappa")

    c_ent_variance = c_ent.var(axis=1, ddof=1)
    residence_steps = (entropy >= high_entropy_threshold).sum(axis=1)
    residence_fraction = residence_steps / entropy.shape[1]
    entropy_production = np.concatenate(
        [np.zeros((entropy.shape[0], 1), dtype=float), np.abs(np.diff(entropy, axis=1))],
        axis=1,
    )
    entropy_production_rate = entropy_production[:, 1:].mean(axis=1)
    hurst_exponents = dfa_hurst_matrix(c_ent)

    stats_frame = pd.DataFrame(
        {
            "regime": regime,
            "trajectory_id": np.arange(c_ent.shape[0], dtype=np.int32),
            "c_ent_variance": c_ent_variance,
            "residence_steps_high_entropy": residence_steps.astype(np.int32),
            "residence_fraction_high_entropy": residence_fraction,
            "entropy_production_rate": entropy_production_rate,
            "hurst_exponent": hurst_exponents,
            "mean_C_ent": c_ent.mean(axis=1),
            "mean_entropy": entropy.mean(axis=1),
            "mean_kappa": kappa.mean(axis=1),
        }
    )

    production_frame = pd.DataFrame(
        {
            "regime": regime,
            "step": np.arange(c_ent.shape[1], dtype=np.int16),
            "mean_entropy_production": entropy_production.mean(axis=0),
        }
    )

    return stats_frame, production_frame


def pick_example_trajectories(frame: pd.DataFrame, stats_frame: pd.DataFrame, n_examples: int = 5) -> pd.DataFrame:
    """Select representative trajectories spanning the C_ent variance distribution."""

    quantiles = np.quantile(stats_frame["c_ent_variance"], np.linspace(0.1, 0.9, n_examples))
    selected: list[int] = []
    for quantile in quantiles:
        remaining = stats_frame.loc[~stats_frame["trajectory_id"].isin(selected)].copy()
        remaining["distance"] = (remaining["c_ent_variance"] - quantile).abs()
        selected.append(int(remaining.sort_values("distance").iloc[0]["trajectory_id"]))

    return frame.loc[frame["trajectory_id"].isin(selected)].copy()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bootstrap", type=int, default=1_000, help="Bootstrap resamples for confidence intervals.")
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Analyze whatever artifacts are present and print a compact summary.",
    )
    return parser.parse_args()


def main() -> None:
    """Run CPC 2026 statistical analysis."""

    args = parse_args()
    seed_everything(DEFAULT_SEED)

    ensure_dir = CPC_RESULTS_DIR
    ensure_dir.mkdir(parents=True, exist_ok=True)

    node_metrics = load_node_metrics()
    high_entropy_threshold = float(node_metrics["entropy"].quantile(0.9))
    phase_reference = load_phase_transition_reference()
    critical_eta = infer_critical_eta(phase_reference)
    graph = load_swow_en_graph()

    trajectory_stats_frames: list[pd.DataFrame] = []
    production_frames: list[pd.DataFrame] = []
    example_frames: list[pd.DataFrame] = []

    regime_summary_rows = []
    per_regime_summary: dict[str, dict[str, float | list[float]]] = {}

    for offset, regime_cfg in enumerate(REGIME_CONFIGS):
        regime = regime_cfg.name
        frame = pd.read_parquet(trajectory_path(regime))
        stats_frame, production_frame = summarize_regime(
            regime=regime,
            frame=frame,
            high_entropy_threshold=high_entropy_threshold,
            n_bootstrap=args.bootstrap,
        )
        trajectory_stats_frames.append(stats_frame)
        production_frames.append(production_frame)
        example = pick_example_trajectories(frame, stats_frame, n_examples=5)
        example["regime"] = regime
        example_frames.append(example)

        variance_ci = summarize_ci(
            bootstrap_statistic(
                stats_frame["c_ent_variance"].to_numpy(),
                None,
                lambda sample: float(sample.mean()),
                n_bootstrap=args.bootstrap,
                seed=DEFAULT_SEED + offset,
            )
        )
        residence_ci = summarize_ci(
            bootstrap_statistic(
                stats_frame["residence_fraction_high_entropy"].to_numpy(),
                None,
                lambda sample: float(sample.mean()),
                n_bootstrap=args.bootstrap,
                seed=DEFAULT_SEED + 100 + offset,
            )
        )
        production_ci = summarize_ci(
            bootstrap_statistic(
                stats_frame["entropy_production_rate"].to_numpy(),
                None,
                lambda sample: float(sample.mean()),
                n_bootstrap=args.bootstrap,
                seed=DEFAULT_SEED + 200 + offset,
            )
        )
        hurst_ci = summarize_ci(
            bootstrap_statistic(
                stats_frame["hurst_exponent"].dropna().to_numpy(),
                None,
                lambda sample: float(sample.mean()),
                n_bootstrap=args.bootstrap,
                seed=DEFAULT_SEED + 300 + offset,
            )
        )

        per_regime_summary[regime] = {
            "n_trajectories": int(len(stats_frame)),
            "mean_c_ent_variance": float(stats_frame["c_ent_variance"].mean()),
            "ci_c_ent_variance": [variance_ci[0], variance_ci[1]],
            "mean_residence_fraction_high_entropy": float(stats_frame["residence_fraction_high_entropy"].mean()),
            "ci_residence_fraction_high_entropy": [residence_ci[0], residence_ci[1]],
            "mean_entropy_production_rate": float(stats_frame["entropy_production_rate"].mean()),
            "ci_entropy_production_rate": [production_ci[0], production_ci[1]],
            "mean_hurst_exponent": float(stats_frame["hurst_exponent"].mean()),
            "ci_hurst_exponent": [hurst_ci[0], hurst_ci[1]],
        }

        regime_summary_rows.append(
            {
                "regime": regime,
                "mean_c_ent_variance": per_regime_summary[regime]["mean_c_ent_variance"],
                "mean_residence_fraction_high_entropy": per_regime_summary[regime]["mean_residence_fraction_high_entropy"],
                "mean_entropy_production_rate": per_regime_summary[regime]["mean_entropy_production_rate"],
                "mean_hurst_exponent": per_regime_summary[regime]["mean_hurst_exponent"],
            }
        )

    trajectory_stats = pd.concat(trajectory_stats_frames, ignore_index=True)
    production_series = pd.concat(production_frames, ignore_index=True)
    example_trajectories = pd.concat(example_frames, ignore_index=True)
    regime_summary_df = pd.DataFrame(regime_summary_rows)

    normative = trajectory_stats.loc[trajectory_stats["regime"] == "normative"]
    anxious = trajectory_stats.loc[trajectory_stats["regime"] == "anxious"]

    variance_d = cohens_d(
        normative["c_ent_variance"].to_numpy(),
        anxious["c_ent_variance"].to_numpy(),
    )
    variance_d_ci = summarize_ci(
        bootstrap_statistic(
            normative["c_ent_variance"].to_numpy(),
            anxious["c_ent_variance"].to_numpy(),
            cohens_d,
            n_bootstrap=args.bootstrap,
            seed=DEFAULT_SEED + 900,
        )
    )
    variance_test = stats.ttest_ind(
        normative["c_ent_variance"].to_numpy(),
        anxious["c_ent_variance"].to_numpy(),
        equal_var=False,
    )

    residence_increase = (
        anxious["residence_fraction_high_entropy"].mean() / normative["residence_fraction_high_entropy"].mean() - 1.0
    ) * 100.0
    residence_diff_ci = summarize_ci(
        bootstrap_statistic(
            normative["residence_fraction_high_entropy"].to_numpy(),
            anxious["residence_fraction_high_entropy"].to_numpy(),
            lambda x, y: float((y.mean() / x.mean() - 1.0) * 100.0),
            n_bootstrap=args.bootstrap,
            seed=DEFAULT_SEED + 901,
        )
    )
    residence_test = stats.mannwhitneyu(
        normative["residence_fraction_high_entropy"].to_numpy(),
        anxious["residence_fraction_high_entropy"].to_numpy(),
        alternative="two-sided",
    )

    summary_payload = {
        "seed": DEFAULT_SEED,
        "high_entropy_threshold": high_entropy_threshold,
        "n_bootstrap": args.bootstrap,
        "per_regime": per_regime_summary,
        "comparisons": {
            "normative_vs_anxious_c_ent_variance": {
                "cohens_d": variance_d,
                "ci": [variance_d_ci[0], variance_d_ci[1]],
                "p_value": float(variance_test.pvalue),
                "normative_mean": float(normative["c_ent_variance"].mean()),
                "anxious_mean": float(anxious["c_ent_variance"].mean()),
            },
            "normative_vs_anxious_high_entropy_residence": {
                "percent_increase": float(residence_increase),
                "ci": [residence_diff_ci[0], residence_diff_ci[1]],
                "p_value": float(residence_test.pvalue),
                "normative_mean": float(normative["residence_fraction_high_entropy"].mean()),
                "anxious_mean": float(anxious["residence_fraction_high_entropy"].mean()),
            },
        },
        "phase_transition_reference": {
            "eta_critical_reference": critical_eta["eta_critical"],
            "eta_critical_method": critical_eta["method"],
            "swow_eta": graph_eta(graph),
            "swow_mean_kappa": float(node_metrics["kappa"].mean()),
            "swow_position": "subcritical_hyperbolic" if graph_eta(graph) < critical_eta["eta_critical"] else "near_or_above_transition",
        },
        "abstract_claim_check": {
            "cohens_d_claim": {"claimed": 1.84, "observed": variance_d},
            "residence_time_claim_percent": {"claimed": 47.0, "observed": float(residence_increase)},
            "hurst_pathology_direction": {
                "claimed": "pathological_regimes_lower_than_normative",
                "observed": {
                    regime: per_regime_summary[regime]["mean_hurst_exponent"] for regime in per_regime_summary
                },
            },
        },
    }

    trajectory_stats.to_parquet(TRAJECTORY_STATS_PARQUET, index=False)
    production_series.to_csv(ENTROPY_PRODUCTION_CSV, index=False)
    regime_summary_df.to_csv(REGIME_SUMMARY_CSV, index=False)
    example_trajectories.to_parquet(EXAMPLE_TRAJECTORIES_PARQUET, index=False)
    save_json(STATISTICAL_SUMMARY_JSON, summary_payload)

    if args.smoke_test:
        print(
            pd.DataFrame(
                {
                    "metric": ["cohens_d", "residence_percent_increase", "eta_critical_reference", "swow_eta"],
                    "value": [
                        variance_d,
                        residence_increase,
                        critical_eta["eta_critical"],
                        graph_eta(graph),
                    ],
                }
            ).to_string(index=False)
        )
        return

    print(
        f"Saved trajectory statistics to {TRAJECTORY_STATS_PARQUET} and summary JSON to {STATISTICAL_SUMMARY_JSON}."
    )


if __name__ == "__main__":
    main()
