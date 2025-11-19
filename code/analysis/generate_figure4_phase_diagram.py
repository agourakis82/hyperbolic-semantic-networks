#!/usr/bin/env python3
"""Generate Figure 4: Phase diagram of network geometry."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "processed"
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "figures"
OUTPUT_FIG_DIR = ROOT / "submission" / "nature-communications-v2.0" / "figures"


def load_json(path: Path) -> Dict[str, Any]:
    with path.open() as f:
        return json.load(f)


def compute_network_metrics(edge_file: Path) -> Dict[str, float]:
    df = pd.read_csv(edge_file)

    weight_column = "weight" if "weight" in df.columns else None

    G_dir = nx.DiGraph()
    for row in df.itertuples(index=False):
        source = getattr(row, "source")
        target = getattr(row, "target")
        weight = getattr(row, "weight", 1.0)
        G_dir.add_edge(source, target, weight=weight)

    G = G_dir.to_undirected()
    if not nx.is_connected(G):
        largest = max(nx.connected_components(G), key=len)
        G = G.subgraph(largest).copy()

    c_weighted = nx.average_clustering(G, weight=weight_column)
    degrees = np.array([deg for _, deg in G.degree()], dtype=float)
    sigma_k = float(np.std(degrees, ddof=0))

    return {
        "n_nodes": G.number_of_nodes(),
        "n_edges": G.number_of_edges(),
        "clustering": float(c_weighted),
        "sigma_k": sigma_k,
    }


def get_kappa_mean(source: Dict[str, Any]) -> float:
    kind = source.get("kind")
    path = ROOT / source["path"]

    data = load_json(path)

    if kind == "swow_final":
        entry = data[source["key"]]
        return float(entry["kappa_mean"])
    if kind == "curvature_nested":
        return float(data["curvature"]["kappa_mean"])
    if kind == "curvature_root":
        return float(data["kappa_mean"])

    raise ValueError(f"Unknown curvature source type: {kind}")


NETWORKS: List[Dict[str, Any]] = [
    {
        "label": "SWOW (ES)",
        "category": "Association",
        "edge_file": DATA_DIR / "spanish_edges_FINAL.csv",
        "curvature": {
            "kind": "swow_final",
            "path": "results/FINAL_CURVATURE_CORRECTED_PREPROCESSING.json",
            "key": "spanish",
        },
    },
    {
        "label": "SWOW (EN)",
        "category": "Association",
        "edge_file": DATA_DIR / "english_edges_FINAL.csv",
        "curvature": {
            "kind": "swow_final",
            "path": "results/FINAL_CURVATURE_CORRECTED_PREPROCESSING.json",
            "key": "english",
        },
    },
    {
        "label": "SWOW (ZH)",
        "category": "Association",
        "edge_file": DATA_DIR / "chinese_edges_FINAL.csv",
        "curvature": {
            "kind": "swow_final",
            "path": "results/FINAL_CURVATURE_CORRECTED_PREPROCESSING.json",
            "key": "chinese",
        },
    },
    {
        "label": "ConceptNet (EN)",
        "category": "Association",
        "edge_file": DATA_DIR / "conceptnet_en_edges.csv",
        "curvature": {
            "kind": "curvature_nested",
            "path": "results/multi_dataset/conceptnet_curvature_results.json",
        },
    },
    {
        "label": "ConceptNet (PT)",
        "category": "Association",
        "edge_file": DATA_DIR / "conceptnet_pt_edges.csv",
        "curvature": {
            "kind": "curvature_root",
            "path": "results/conceptnet_pt_curvature.json",
        },
    },
    {
        "label": "WordNet (EN)",
        "category": "Taxonomy",
        "edge_file": DATA_DIR / "wordnet_edges.csv",
        "curvature": {
            "kind": "curvature_nested",
            "path": "results/multi_dataset/wordnet_curvature_results.json",
        },
    },
    {
        "label": "BabelNet (RU)",
        "category": "Taxonomy",
        "edge_file": DATA_DIR / "babelnet_ru_edges.csv",
        "curvature": {
            "kind": "curvature_root",
            "path": "results/babelnet_ru_curvature.json",
        },
    },
    {
        "label": "BabelNet (AR)",
        "category": "Taxonomy",
        "edge_file": DATA_DIR / "babelnet_ar_edges.csv",
        "curvature": {
            "kind": "curvature_root",
            "path": "results/babelnet_ar_curvature.json",
        },
    },
]


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FIG_DIR.mkdir(parents=True, exist_ok=True)

    records: List[Dict[str, Any]] = []

    for entry in NETWORKS:
        metrics = compute_network_metrics(entry["edge_file"])
        kappa_mean = get_kappa_mean(entry["curvature"])

        record = {
            "label": entry["label"],
            "category": entry["category"],
            "n_nodes": metrics["n_nodes"],
            "n_edges": metrics["n_edges"],
            "clustering": metrics["clustering"],
            "sigma_k": metrics["sigma_k"],
            "kappa_mean": kappa_mean,
        }
        records.append(record)

    df = pd.DataFrame(records)
    df.sort_values("clustering", inplace=True)

    # Save data snapshot for reproducibility
    df.to_csv(RESULTS_DIR / "phase_diagram_metrics.csv", index=False)

    # Plotting
    markers = {"Association": "o", "Taxonomy": "^", "Dense": "s"}
    cmap = plt.get_cmap("coolwarm")
    vmin, vmax = -0.3, 0.3

    fig, ax = plt.subplots(figsize=(7.2, 5.8))

    # Highlight the "hyperbolic sweet spot"
    ax.axvspan(0.02, 0.15, color="#f0f0f0", alpha=0.6, label="Hyperbolic sweet spot")

    for category, subset in df.groupby("category"):
        ax.scatter(
            subset["clustering"],
            subset["sigma_k"],
            c=subset["kappa_mean"],
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            marker=markers.get(category, "o"),
            edgecolor="black",
            linewidth=0.6,
            s=120,
            label=category,
        )

    # Annotate key points
    for _, row in df.iterrows():
        ax.annotate(
            row["label"],
            (row["clustering"], row["sigma_k"]),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=9,
        )

    ax.set_xlabel("Mean clustering coefficient (C)", fontweight="bold")
    ax.set_ylabel("Degree heterogeneity (σₖ)", fontweight="bold")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

    ax.text(0.155, ax.get_ylim()[1] * 0.9, "Spherical", color="#b2182b", fontsize=10,
            ha="left", fontweight="semibold")
    ax.text(0.001, ax.get_ylim()[1] * 0.85, "Euclidean", color="#4d4d4d", fontsize=10,
            ha="left", fontweight="semibold")
    ax.text(0.025, ax.get_ylim()[1] * 0.1, "Hyperbolic", color="#2166ac", fontsize=10,
            ha="left", fontweight="semibold")

    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    legend = ax.legend(by_label.values(), by_label.keys(), loc="upper left", frameon=True)
    legend.get_frame().set_alpha(0.9)

    cbar = fig.colorbar(
        plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax)),
        ax=ax,
        pad=0.02,
    )
    cbar.set_label("Mean Ollivier–Ricci curvature (κ̄)", fontweight="bold")

    fig.tight_layout()

    for out_dir in [FIGURES_DIR, OUTPUT_FIG_DIR]:
        (out_dir / "figure4_phase_diagram.png").parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_dir / "figure4_phase_diagram.png", dpi=300, bbox_inches="tight")
        fig.savefig(out_dir / "figure4_phase_diagram.pdf", bbox_inches="tight")

    print("✅ Figure 4 saved to:")
    print(f"   - {FIGURES_DIR / 'figure4_phase_diagram.png'}")
    print(f"   - {OUTPUT_FIG_DIR / 'figure4_phase_diagram.png'}")


if __name__ == "__main__":
    main()

