"""Generate O-SSM-focused figures for the CPC 2026 extension."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from common import CPC_FIGURES_DIR, CPC_RESULTS_DIR, ensure_directory


OSSMMAP = {
    "normative": "#2A6F97",
    "anxious": "#C44536",
    "ruminative": "#6D597A",
    "psychotic": "#D4A373",
}


def _save_figure(figure: plt.Figure, stem: str) -> None:
    """Write both PDF and PNG versions of a figure."""

    ensure_directory(CPC_FIGURES_DIR)
    figure.savefig(CPC_FIGURES_DIR / f"{stem}.pdf", bbox_inches="tight")
    figure.savefig(CPC_FIGURES_DIR / f"{stem}.png", dpi=300, bbox_inches="tight")
    plt.close(figure)


def _configure_style() -> None:
    """Use a clean publication-oriented matplotlib style."""

    sns.set_theme(style="whitegrid")
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "#FCFBF7",
            "axes.edgecolor": "#333333",
            "axes.labelsize": 11,
            "axes.titlesize": 13,
            "font.size": 10,
            "grid.alpha": 0.18,
            "grid.linestyle": "--",
            "legend.frameon": False,
        }
    )


def plot_associator() -> None:
    """Plot mean associator norm over time by regime."""

    stepwise = pd.read_csv(CPC_RESULTS_DIR / "ossm_stepwise_summary.csv")
    stepwise["associator_smooth"] = (
        stepwise.groupby("regime")["mean_associator_norm"].transform(lambda s: s.rolling(15, min_periods=1).mean())
    )

    figure, axis = plt.subplots(figsize=(8.4, 4.8))
    for regime, frame in stepwise.groupby("regime"):
        axis.plot(
            frame["step"],
            frame["associator_smooth"],
            color=OSSMMAP[regime],
            linewidth=2.1,
            label=regime.title(),
        )
    axis.set_title("Associator Norm Across Cognitive Regimes")
    axis.set_xlabel("Step")
    axis.set_ylabel("Mean associator norm")
    axis.legend(ncol=2)
    _save_figure(figure, "fig_ossm_associator")


def plot_subspace_occupancy() -> None:
    """Plot quaternionic subspace occupancy heatmap."""

    occupancy = pd.read_csv(CPC_RESULTS_DIR / "ossm_subspace_occupancy.csv")
    matrix = occupancy.pivot(index="subspace", columns="regime", values="occupancy")
    ordered_columns = [name for name in ["normative", "anxious", "ruminative", "psychotic"] if name in matrix.columns]
    matrix = matrix.loc[:, ordered_columns]

    figure, axis = plt.subplots(figsize=(6.8, 4.6))
    sns.heatmap(matrix, cmap="YlOrBr", annot=True, fmt=".2f", cbar_kws={"label": "Occupancy"}, ax=axis)
    axis.set_title("Quaternionic Subspace Occupancy")
    axis.set_xlabel("Regime")
    axis.set_ylabel("Fano-plane quaternionic subspace")
    _save_figure(figure, "fig_ossm_subspace_occupancy")


def plot_vs_markov() -> None:
    """Plot effect sizes for Markov versus O-SSM metrics."""

    frame = pd.read_csv(CPC_RESULTS_DIR / "ossm_cross_model_comparison.csv")
    melted = frame.melt(
        id_vars=["metric"],
        value_vars=["markov_d", "ossm_d"],
        var_name="model",
        value_name="cohens_d",
    )
    melted["model"] = melted["model"].map({"markov_d": "Markov", "ossm_d": "O-SSM"})

    figure, axis = plt.subplots(figsize=(8.6, 4.8))
    sns.barplot(data=melted, x="metric", y="cohens_d", hue="model", palette=["#8C8C8C", "#1F6F8B"], ax=axis)
    axis.axhline(0.0, color="#333333", linewidth=1.0)
    axis.set_title("Normative vs Anxious Effect Sizes")
    axis.set_xlabel("")
    axis.set_ylabel("Cohen's d")
    axis.tick_params(axis="x", rotation=15)
    _save_figure(figure, "fig_ossm_vs_markov")


def plot_phase_portrait() -> None:
    """Project sampled hidden states to 2D with PCA and plot regime basins."""

    frames = []
    for regime in ["normative", "anxious", "ruminative", "psychotic"]:
        path = CPC_RESULTS_DIR / f"ossm_state_samples_{regime}.parquet"
        if not path.exists():
            continue
        frame = pd.read_parquet(path)
        frame["regime"] = regime
        frames.append(frame)

    if not frames:
        raise FileNotFoundError("Missing O-SSM state sample parquets.")

    combined = pd.concat(frames, ignore_index=True)
    hidden_columns = [column for column in combined.columns if column.startswith("h")]
    sample = combined.loc[:, ["regime", "trajectory_id", "step", *hidden_columns]].copy()
    sample = sample.groupby("regime", group_keys=False).head(2_000).reset_index(drop=True)

    values = sample.loc[:, hidden_columns].to_numpy(dtype=float)
    centered = values - values.mean(axis=0, keepdims=True)
    _, _, vt = np.linalg.svd(centered, full_matrices=False)
    components = centered @ vt[:2].T
    sample["pc1"] = components[:, 0]
    sample["pc2"] = components[:, 1]

    figure, axis = plt.subplots(figsize=(6.6, 6.0))
    for regime, frame in sample.groupby("regime"):
        axis.scatter(
            frame["pc1"],
            frame["pc2"],
            s=10,
            alpha=0.28,
            color=OSSMMAP[regime],
            label=regime.title(),
        )
    axis.set_title("O-SSM Hidden-State Phase Portrait")
    axis.set_xlabel("PC1")
    axis.set_ylabel("PC2")
    axis.legend()
    _save_figure(figure, "fig_ossm_phase_portrait")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke-test", action="store_true", help="Run and print the figure directory.")
    return parser.parse_args()


def main() -> None:
    """Generate all O-SSM figures."""

    parse_args()
    _configure_style()
    plot_associator()
    plot_subspace_occupancy()
    plot_vs_markov()
    plot_phase_portrait()
    print(f"Saved O-SSM figures to {CPC_FIGURES_DIR}.")


if __name__ == "__main__":
    main()
