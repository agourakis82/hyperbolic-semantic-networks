#!/usr/bin/env python3
"""
Regenerate the 7-graph versions of Figure 1 and Figure 4.

Source data: results/phase_diagram_metrics_7graph.csv
  columns: label, category, family, clustering, sigma_k, kappa_mean
  4 SWOW association networks + 3 taxonomy lexicons (NO ConceptNet).

Figure 1 - Clustering-Curvature Map:
  scatter of weighted clustering C (x) vs mean Ollivier-Ricci curvature kappa_mean (y).
  Association graphs = filled circles; taxonomy = open triangles. Each point labeled.
  Shaded moderate-clustering band C in [0.026, 0.037] (the SWOW band).
  A light descriptive smooth is overlaid and labeled descriptive (n=7, not inferential).

Figure 4 - Phase Diagram:
  (C, sigma_k) plane, points colored by kappa_mean on a diverging colormap (0 = white).
  Association vs taxonomy markers, labeled. Hyperbolic vs Euclidean regions annotated.

Outputs (NEW files, do not overwrite the existing 8-graph PNGs):
  submission/nature-communications-v2.0-final/figures/figure1_clustering_curvature_7graph.png
  submission/nature-communications-v2.0-final/figures/figure4_phase_diagram_7graph.png
"""

from __future__ import annotations

import os
from pathlib import Path

# Force a headless backend before importing pyplot.
os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = ROOT / "results" / "phase_diagram_metrics_7graph.csv"
OUT_DIR = ROOT / "submission" / "nature-communications-v2.0-final" / "figures"

# Publication style.
plt.rcParams.update(
    {
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    }
)

# Moderate-clustering "sweet spot" band occupied by the four SWOW networks.
SWEET_MIN, SWEET_MAX = 0.026, 0.037

PALETTE = {"Association": "#1f77b4", "Taxonomy": "#ff7f0e"}
MARKERS = {"Association": "o", "Taxonomy": "^"}


def load_metrics() -> pd.DataFrame:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Missing metrics file: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    required = {"label", "category", "clustering", "sigma_k", "kappa_mean"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {sorted(missing)}")
    return df.sort_values("clustering").reset_index(drop=True)


def _scatter_by_category(ax, df: pd.DataFrame, x: str, y: str, **kwargs) -> None:
    """Filled circles for Association, open triangles for Taxonomy."""
    seen = set()
    for _, row in df.iterrows():
        cat = row["category"]
        label = cat if cat not in seen else None
        seen.add(cat)
        if cat == "Taxonomy":
            face = "none"
            edge = PALETTE.get(cat, "#7f7f7f")
        else:
            face = PALETTE.get(cat, "#7f7f7f")
            edge = "black"
        ax.scatter(
            row[x],
            row[y],
            s=130,
            facecolor=face,
            edgecolor=edge,
            linewidth=1.4,
            marker=MARKERS.get(cat, "o"),
            label=label,
            zorder=5,
            **kwargs,
        )


def generate_figure1(df: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(7.6, 5.8))

    # Shade the moderate-clustering region (the SWOW band).
    ax.axvspan(
        SWEET_MIN,
        SWEET_MAX,
        color="#b3e5fc",
        alpha=0.40,
        zorder=0,
        label=fr"Moderate-clustering band ($C\approx{SWEET_MIN:.3f}$–${SWEET_MAX:.3f}$)",
    )

    # Descriptive smooth (degree-2 polynomial) over the observed C range.
    # Labelled descriptive (n=7), NOT inferential -- the robust claim is categorical.
    C = df["clustering"].to_numpy(dtype=float)
    K = df["kappa_mean"].to_numpy(dtype=float)
    order = np.argsort(C)
    Cs, Ks = C[order], K[order]
    try:
        coeffs = np.polyfit(Cs, Ks, deg=2)
        xs = np.linspace(Cs.min(), Cs.max(), 200)
        ys = np.polyval(coeffs, xs)
        ax.plot(
            xs,
            ys,
            color="#555555",
            linestyle="-",
            linewidth=1.6,
            alpha=0.7,
            zorder=2,
            label="Descriptive smooth (n=7, not inferential)",
        )
    except Exception as exc:  # pragma: no cover - guard against degenerate fit
        print(f"[figure1] skipping descriptive smooth: {exc}")

    _scatter_by_category(ax, df, "clustering", "kappa_mean")

    # Label every point.
    for _, row in df.iterrows():
        ax.annotate(
            row["label"],
            (row["clustering"], row["kappa_mean"]),
            textcoords="offset points",
            xytext=(6, 6),
            ha="left",
            va="bottom",
            fontsize=9,
            rotation=12,
            alpha=0.9,
        )

    ax.axhline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.6)
    ax.set_xlabel(r"Weighted clustering coefficient ($C$)", fontweight="bold")
    ax.set_ylabel(r"Mean Ollivier–Ricci curvature ($\bar{\kappa}$)", fontweight="bold")
    ax.set_title("Clustering–Curvature Map Across Networks", fontweight="bold", pad=12)
    ax.grid(True, which="both", linestyle=":", alpha=0.4)

    # Linear x-axis: BabelNet (AR) has C = 0 exactly, which a log scale would drop.
    ax.set_xlim(left=-0.002)
    # Extra headroom below so the bottom SWOW cluster has room for labels.
    ymin = float(K.min())
    ax.set_ylim(bottom=ymin - 0.045, top=0.03)

    # Re-label legend entries so the marker shape is self-documenting.
    handles, labels = ax.get_legend_handles_labels()
    rename = {
        "Association": "Association (filled circles)",
        "Taxonomy": "Taxonomy (open triangles)",
    }
    labels = [rename.get(lab, lab) for lab in labels]
    if handles:
        ax.legend(
            handles,
            labels,
            loc="center left",
            bbox_to_anchor=(0.015, 0.42),
            frameon=True,
            fancybox=True,
        )

    fig.tight_layout()
    out_path = OUT_DIR / "figure1_clustering_curvature_7graph.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out_path


def generate_figure4(df: pd.DataFrame) -> Path:
    cmap = plt.get_cmap("coolwarm")
    # Symmetric limits keep 0 at white (diverging). Do NOT autoscale: all kappa<0.
    vmin, vmax = -0.3, 0.3
    norm = plt.Normalize(vmin=vmin, vmax=vmax)

    fig, ax = plt.subplots(figsize=(7.4, 5.9))

    seen = set()
    for _, row in df.iterrows():
        cat = row["category"]
        label = cat if cat not in seen else None
        seen.add(cat)
        ax.scatter(
            row["clustering"],
            row["sigma_k"],
            c=[row["kappa_mean"]],
            cmap=cmap,
            norm=norm,
            marker=MARKERS.get(cat, "o"),
            edgecolor="black",
            linewidth=0.8,
            s=150,
            label=label,
            zorder=5,
        )

    # Label every point.
    for _, row in df.iterrows():
        ax.annotate(
            row["label"],
            (row["clustering"], row["sigma_k"]),
            textcoords="offset points",
            xytext=(0, 9),
            ha="center",
            fontsize=9,
            zorder=6,
        )

    ax.set_xlabel(r"Weighted clustering coefficient ($C$)", fontweight="bold")
    ax.set_ylabel(r"Degree heterogeneity ($\sigma_k$)", fontweight="bold")
    ax.set_title("Phase Diagram of Network Geometry", fontweight="bold", pad=12)
    ax.set_xlim(left=-0.003)
    ax.set_ylim(bottom=0)
    ax.grid(True, linestyle=":", alpha=0.35)

    # Annotate the populated regimes. All 7 networks have kappa < 0, so the
    # data live in the hyperbolic (strongly negative) and Euclidean (~0) zones.
    ymax = ax.get_ylim()[1]
    ax.text(
        SWEET_MIN + 0.0015,
        ymax * 0.12,
        "Hyperbolic\ncorridor",
        color="#2166ac",
        fontsize=11,
        ha="left",
        va="bottom",
        fontweight="semibold",
    )
    ax.text(
        0.0005,
        ymax * 0.92,
        "Euclidean\nboundary",
        color="#4d4d4d",
        fontsize=11,
        ha="left",
        va="top",
        fontweight="semibold",
    )

    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    if by_label:
        legend = ax.legend(
            by_label.values(), by_label.keys(), loc="upper center", frameon=True
        )
        legend.get_frame().set_alpha(0.9)

    cbar = fig.colorbar(
        plt.cm.ScalarMappable(cmap=cmap, norm=norm), ax=ax, pad=0.02
    )
    cbar.set_label(r"Mean Ollivier–Ricci curvature ($\bar{\kappa}$)", fontweight="bold")

    fig.tight_layout()
    out_path = OUT_DIR / "figure4_phase_diagram_7graph.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out_path


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_metrics()
    print(f"Loaded {len(df)} networks from {CSV_PATH}")
    print(df[["label", "category", "clustering", "sigma_k", "kappa_mean"]].to_string(index=False))

    f1 = generate_figure1(df)
    print(f"Figure 1 saved: {f1}")
    f4 = generate_figure4(df)
    print(f"Figure 4 saved: {f4}")


if __name__ == "__main__":
    main()
