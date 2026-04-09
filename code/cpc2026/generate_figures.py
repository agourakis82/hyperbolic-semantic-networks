"""Generate publication figures for the CPC 2026 semantic-manifold analysis."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
import pandas as pd
import seaborn as sns

from common import (
    CPC_FIGURES_DIR,
    ENTROPY_PRODUCTION_CSV,
    EXAMPLE_TRAJECTORIES_PARQUET,
    POINCARE_EMBEDDING_PARQUET,
    REGIME_CONFIGS,
    STATISTICAL_SUMMARY_JSON,
    TRAJECTORY_STATS_PARQUET,
    ensure_directory,
    load_node_metrics,
    load_phase_transition_reference,
)


REGIME_ORDER = [config.name for config in REGIME_CONFIGS]
REGIME_LABELS = {
    "normative": "Normative",
    "anxious": "Anxious",
    "ruminative": "Ruminative",
    "psychotic": "Psychotic",
}
REGIME_COLORS = {
    "normative": "#2D6A4F",
    "anxious": "#B02E0C",
    "ruminative": "#7A5C61",
    "psychotic": "#355070",
}


def setup_style() -> None:
    """Apply a clean, journal-style plotting theme."""

    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams.update(
        {
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titlesize": 16,
            "axes.labelsize": 13,
            "legend.frameon": False,
            "figure.dpi": 150,
            "savefig.bbox": "tight",
        }
    )


def save_figure(fig: plt.Figure, stem: str) -> None:
    """Save one figure as vector PDF and 300 DPI PNG."""

    ensure_directory(CPC_FIGURES_DIR)
    pdf_path = CPC_FIGURES_DIR / f"{stem}.pdf"
    png_path = CPC_FIGURES_DIR / f"{stem}.png"
    fig.savefig(pdf_path)
    fig.savefig(png_path, dpi=300)
    plt.close(fig)


def load_summary() -> dict:
    """Load the statistical summary JSON."""

    return json.loads(Path(STATISTICAL_SUMMARY_JSON).read_text(encoding="utf-8"))


def figure_cent_distributions(trajectory_stats: pd.DataFrame, summary: dict) -> None:
    """Figure 1: trajectory-level C_ent variance distributions by regime."""

    fig, ax = plt.subplots(figsize=(10, 6))
    plot_frame = trajectory_stats.copy()
    plot_frame["regime_label"] = plot_frame["regime"].map(REGIME_LABELS)

    sns.violinplot(
        data=plot_frame,
        x="regime_label",
        y="c_ent_variance",
        hue="regime_label",
        order=[REGIME_LABELS[regime] for regime in REGIME_ORDER],
        palette=[REGIME_COLORS[regime] for regime in REGIME_ORDER],
        inner=None,
        cut=0,
        legend=False,
        ax=ax,
    )
    sns.boxplot(
        data=plot_frame,
        x="regime_label",
        y="c_ent_variance",
        order=[REGIME_LABELS[regime] for regime in REGIME_ORDER],
        width=0.18,
        showcaps=False,
        boxprops={"facecolor": "white", "zorder": 3},
        whiskerprops={"linewidth": 0},
        showfliers=False,
        ax=ax,
    )

    d_value = summary["comparisons"]["normative_vs_anxious_c_ent_variance"]["cohens_d"]
    ax.set_title("Trajectory-level entropic-curvature variance across regimes")
    ax.set_xlabel("")
    ax.set_ylabel("Variance of $C_{ent}$ along trajectory")
    ax.text(0.03, 0.97, f"Cohen's d (anxious vs normative) = {d_value:.2f}", transform=ax.transAxes, va="top")
    save_figure(fig, "fig1_cent_distributions")


def figure_phase_diagram(summary: dict) -> None:
    """Figure 2: validated phase diagram with SWOW-EN overlay."""

    phase_reference = load_phase_transition_reference()
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(phase_reference["eta"], phase_reference["kappa_mean"], marker="o", linewidth=2.2, color="#3A506B")
    ax.axhline(0.0, color="black", linewidth=1, linestyle="--")

    critical_eta = summary["phase_transition_reference"]["eta_critical_reference"]
    swow_eta = summary["phase_transition_reference"]["swow_eta"]
    swow_kappa = summary["phase_transition_reference"]["swow_mean_kappa"]

    ax.axvline(critical_eta, color="#BC6C25", linestyle="--", linewidth=1.4, label=f"Reference $\\eta_c$ = {critical_eta:.2f}")
    ax.scatter([swow_eta], [swow_kappa], s=120, color="#D62828", zorder=5, label="SWOW-EN")

    ax.set_xscale("log")
    ax.set_xlabel(r"$\langle k \rangle^2 / N$")
    ax.set_ylabel(r"Mean Ollivier-Ricci curvature $\bar{\kappa}$")
    ax.set_title("Reference phase transition with SWOW-EN overlay")
    ax.legend(loc="best")
    save_figure(fig, "fig2_phase_diagram")


def _heatmap_field(node_metrics: pd.DataFrame, embedding: pd.DataFrame, grid_size: int = 120) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Create a smooth disk heatmap for C_ent."""

    merged = embedding.merge(node_metrics.loc[:, ["node", "C_ent"]], on="node", how="left")
    x = np.linspace(-1.0, 1.0, grid_size)
    y = np.linspace(-1.0, 1.0, grid_size)
    xx, yy = np.meshgrid(x, y)
    field = np.full_like(xx, np.nan, dtype=float)

    coords = merged.loc[:, ["x", "y"]].to_numpy(dtype=float)
    values = merged["C_ent"].to_numpy(dtype=float)
    sigma = 0.10

    for i in range(grid_size):
        for j in range(grid_size):
            point = np.array([xx[i, j], yy[i, j]])
            if np.linalg.norm(point) > 1.0:
                continue
            distances = np.sum((coords - point) ** 2, axis=1)
            kernel = np.exp(-distances / (2.0 * sigma**2))
            field[i, j] = float(np.sum(kernel * values) / np.sum(kernel))

    return xx, yy, field


def figure_trajectory_poincare(example_trajectories: pd.DataFrame, node_metrics: pd.DataFrame, embedding: pd.DataFrame) -> None:
    """Figure 3: representative trajectories on the Poincare disk."""

    merged = example_trajectories.merge(embedding.loc[:, ["node", "x", "y"]], on="node", how="left")
    xx, yy, field = _heatmap_field(node_metrics, embedding)

    fig, axes = plt.subplots(2, 2, figsize=(12, 12), sharex=True, sharey=True)
    axes = axes.ravel()

    for axis, regime in zip(axes, REGIME_ORDER, strict=True):
        regime_frame = merged.loc[merged["regime"] == regime]
        axis.contourf(xx, yy, field, levels=20, cmap="RdBu_r", alpha=0.75)
        axis.add_patch(Circle((0, 0), 1.0, fill=False, linewidth=1.2, color="black"))
        for trajectory_id, group in regime_frame.groupby("trajectory_id"):
            axis.plot(group["x"], group["y"], color=REGIME_COLORS[regime], linewidth=1.6, alpha=0.9)
            axis.scatter(group["x"].iloc[0], group["y"].iloc[0], color="white", edgecolor=REGIME_COLORS[regime], s=25)
        axis.set_title(REGIME_LABELS[regime])
        axis.set_aspect("equal")
        axis.set_xlim(-1.02, 1.02)
        axis.set_ylim(-1.02, 1.02)
        axis.set_xticks([])
        axis.set_yticks([])

    fig.suptitle("Representative semantic trajectories on the Poincare disk", y=0.92)
    save_figure(fig, "fig3_trajectory_poincare")


def figure_hurst_comparison(trajectory_stats: pd.DataFrame) -> None:
    """Figure 4: Hurst exponent comparison across regimes."""

    fig, ax = plt.subplots(figsize=(10, 6))
    plot_frame = trajectory_stats.copy()
    plot_frame["regime_label"] = plot_frame["regime"].map(REGIME_LABELS)

    sns.boxplot(
        data=plot_frame,
        x="regime_label",
        y="hurst_exponent",
        hue="regime_label",
        order=[REGIME_LABELS[regime] for regime in REGIME_ORDER],
        palette=[REGIME_COLORS[regime] for regime in REGIME_ORDER],
        legend=False,
        ax=ax,
    )
    ax.axhline(0.5, linestyle="--", color="black", linewidth=1, label="H = 0.5")
    ax.axhline(1.0, linestyle=":", color="#7F5539", linewidth=1, label="H = 1.0")
    ax.set_xlabel("")
    ax.set_ylabel("Hurst exponent (DFA)")
    ax.set_title("Long-range dependence of entropic-curvature time series")
    ax.legend(loc="upper right")
    save_figure(fig, "fig4_hurst_comparison")


def figure_residence_time(trajectory_stats: pd.DataFrame) -> None:
    """Figure 5: mean residence time in high-entropy hubs by regime."""

    grouped = (
        trajectory_stats.groupby("regime", sort=False)["residence_fraction_high_entropy"]
        .agg(["mean", "sem"])
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.bar(
        [REGIME_LABELS[regime] for regime in grouped["regime"]],
        grouped["mean"],
        yerr=1.96 * grouped["sem"],
        color=[REGIME_COLORS[regime] for regime in grouped["regime"]],
        capsize=5,
    )
    ax.set_ylabel("Residence fraction in top-10% entropy hubs")
    ax.set_xlabel("")
    ax.set_title("Residence time in high-entropy hubs")
    save_figure(fig, "fig5_residence_time")


def figure_entropy_production(entropy_production: pd.DataFrame) -> None:
    """Supplementary figure: mean entropy-production rate by step."""

    fig, ax = plt.subplots(figsize=(10, 6))
    for regime in REGIME_ORDER:
        regime_frame = entropy_production.loc[entropy_production["regime"] == regime]
        ax.plot(
            regime_frame["step"],
            regime_frame["mean_entropy_production"],
            color=REGIME_COLORS[regime],
            linewidth=2.0,
            label=REGIME_LABELS[regime],
        )
    ax.set_xlabel("Step")
    ax.set_ylabel("Mean |Δ entropy| per step")
    ax.set_title("Entropy production rate across simulated trajectories")
    ax.legend(loc="upper right")
    save_figure(fig, "fig_supp_entropy_production")


def main() -> None:
    """Generate the CPC 2026 figure set from saved analysis artifacts."""

    setup_style()
    summary = load_summary()
    trajectory_stats = pd.read_parquet(TRAJECTORY_STATS_PARQUET)
    example_trajectories = pd.read_parquet(EXAMPLE_TRAJECTORIES_PARQUET)
    node_metrics = load_node_metrics()
    embedding = pd.read_parquet(POINCARE_EMBEDDING_PARQUET)
    entropy_production = pd.read_csv(ENTROPY_PRODUCTION_CSV)

    figure_cent_distributions(trajectory_stats, summary)
    figure_phase_diagram(summary)
    figure_trajectory_poincare(example_trajectories, node_metrics, embedding)
    figure_hurst_comparison(trajectory_stats)
    figure_residence_time(trajectory_stats)
    figure_entropy_production(entropy_production)

    print(f"Saved CPC 2026 figures to {CPC_FIGURES_DIR}.")


if __name__ == "__main__":
    main()
