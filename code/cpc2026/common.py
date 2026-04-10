"""Shared helpers for the CPC 2026 semantic-manifold pipeline.

This module centralizes graph loading, exact-ORC artifact access, JSON/parquet
serialization, and path management so the CPC scripts stay flat and readable.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
import random
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np
import pandas as pd

try:
    from GraphRicciCurvature.OllivierRicci import OllivierRicci
except Exception:  # pragma: no cover - optional dependency at runtime
    OllivierRicci = None  # type: ignore[assignment]


REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
RESULTS_DIR = REPO_ROOT / "results"
FIGURES_DIR = REPO_ROOT / "figures"
SUBMISSION_DIR = REPO_ROOT / "submission"

CPC_CODE_DIR = Path(__file__).resolve().parent
CPC_DATA_DIR = DATA_DIR / "cpc2026"
CPC_RESULTS_DIR = RESULTS_DIR / "cpc2026"
CPC_FIGURES_DIR = FIGURES_DIR / "cpc2026"
CPC_SUBMISSION_DIR = SUBMISSION_DIR / "cpc2026"
CPC_SOUNIO_INPUT_DIR = CPC_DATA_DIR / "sounio_input"

SWOW_FINAL_CSV = PROCESSED_DATA_DIR / "english_edges_FINAL.csv"
SWOW_VALENCE_CSV = PROCESSED_DATA_DIR / "swow_en_valence.csv"
SWOW_EXACT_ORC_JSON = RESULTS_DIR / "unified" / "swow_en_exact_lp.json"
PHASE_TRANSITION_REFERENCE_JSON = RESULTS_DIR / "experiments" / "phase_transition_pure_julia.json"

NODE_METRICS_PARQUET = CPC_RESULTS_DIR / "node_metrics.parquet"
NODE_METRICS_QC_JSON = CPC_RESULTS_DIR / "node_metrics_qc.json"
VALENCE_COVERAGE_JSON = CPC_RESULTS_DIR / "valence_coverage.json"
SIMULATION_METADATA_JSON = CPC_RESULTS_DIR / "simulation_metadata.json"
STEPWISE_SUMMARY_CSV = CPC_RESULTS_DIR / "trajectory_stepwise_summary.csv"
TRAJECTORY_STATS_PARQUET = CPC_RESULTS_DIR / "trajectory_statistics.parquet"
STATISTICAL_SUMMARY_JSON = CPC_RESULTS_DIR / "statistical_summary.json"
POINCARE_EMBEDDING_PARQUET = CPC_RESULTS_DIR / "poincare_embedding.parquet"
LANGEVIN_EXAMPLES_PARQUET = CPC_RESULTS_DIR / "trajectories_langevin_examples.parquet"
HYBRID_EXAMPLES_PARQUET = CPC_RESULTS_DIR / "trajectories_hybrid_examples.parquet"
EXAMPLE_TRAJECTORIES_PARQUET = CPC_RESULTS_DIR / "example_trajectories.parquet"
ENTROPY_PRODUCTION_CSV = CPC_RESULTS_DIR / "entropy_production_time_series.csv"
REGIME_SUMMARY_CSV = CPC_RESULTS_DIR / "regime_summary.csv"
NODE_FEATURES_CSV = CPC_DATA_DIR / "swow_en_node_features.csv"
NODE_FEATURES_NPY = CPC_DATA_DIR / "swow_en_node_features.npy"
NODE_FEATURES_METADATA_JSON = CPC_DATA_DIR / "node_feature_metadata.json"
SOUNIO_INPUT_MANIFEST_JSON = CPC_SOUNIO_INPUT_DIR / "manifest.json"

CLINICAL_DEPRESSION_SUMMARY_JSON = CPC_RESULTS_DIR / "clinical_depression_summary.json"
CLINICAL_DEPRESSION_METRICS_PARQUET = CPC_RESULTS_DIR / "clinical_depression_node_metrics.parquet"
CROSS_DOMAIN_ORC_SUMMARY_CSV = CPC_RESULTS_DIR / "cross_domain_orc_summary.csv"
CROSS_DOMAIN_ORC_SUMMARY_JSON = CPC_RESULTS_DIR / "cross_domain_orc_summary.json"

DEPRESSION_EDGE_DIR = PROCESSED_DATA_DIR / "depression_networks_optimal"
DEPRESSION_ORC_DIR = RESULTS_DIR / "unified"
DEPRESSION_SEVERITIES = ("minimum", "mild", "moderate", "severe")

DEFAULT_SEED = 20260409


@dataclass(frozen=True)
class RegimeConfig:
    """Configuration for a cognitive trajectory regime."""

    name: str
    temperature: float
    valence_bias: float
    description: str

    @property
    def negative_bias_strength(self) -> float:
        return abs(min(self.valence_bias, 0.0))

    @property
    def beta(self) -> float:
        return 1.0 / self.temperature


REGIME_CONFIGS: tuple[RegimeConfig, ...] = (
    RegimeConfig(
        name="normative",
        temperature=0.5,
        valence_bias=0.0,
        description="Low-temperature, balanced exploration with entropy penalty.",
    ),
    RegimeConfig(
        name="anxious",
        temperature=2.0,
        valence_bias=-1.0,
        description="High-temperature exploration with negative-valence priming.",
    ),
    RegimeConfig(
        name="ruminative",
        temperature=0.3,
        valence_bias=-0.5,
        description="Low-temperature trapping with mild negative-valence priming.",
    ),
    RegimeConfig(
        name="psychotic",
        temperature=5.0,
        valence_bias=0.0,
        description="Maximum stochasticity via uniform neighbor sampling.",
    ),
)


def ensure_directory(path: Path) -> Path:
    """Create a directory if it does not already exist."""

    path.mkdir(parents=True, exist_ok=True)
    return path


def json_default(value: Any) -> Any:
    """Convert NumPy and dataclass values to JSON-serializable objects."""

    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    raise TypeError(f"Object of type {type(value)!r} is not JSON serializable")


def save_json(path: Path, payload: dict[str, Any]) -> Path:
    """Write a JSON file with stable formatting."""

    ensure_directory(path.parent)
    path.write_text(json.dumps(payload, indent=2, default=json_default) + "\n", encoding="utf-8")
    return path


def load_json(path: Path) -> dict[str, Any]:
    """Load a UTF-8 encoded JSON file."""

    return json.loads(path.read_text(encoding="utf-8"))


def seed_everything(seed: int = DEFAULT_SEED) -> np.random.Generator:
    """Seed Python and NumPy RNGs and return a fresh generator."""

    random.seed(seed)
    np.random.seed(seed)
    return np.random.default_rng(seed)


def normalize_token(token: Any) -> str:
    """Normalize lexical tokens for exact lemma matching."""

    if token is None:
        return ""
    if isinstance(token, float) and math.isnan(token):
        return ""
    return str(token).strip().lower()


def load_edgelist(path: Path) -> pd.DataFrame:
    """Load a generic source/target/weight edge list CSV."""

    df = pd.read_csv(path)
    required = {"source", "target", "weight"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in {path.name}: {sorted(missing)}")
    return df


def load_swow_en_edgelist(path: Path = SWOW_FINAL_CSV) -> pd.DataFrame:
    """Load the validated SWOW-EN edge list used in the exact-LP pipeline."""

    return load_edgelist(path)


def build_weighted_graph(edgelist: pd.DataFrame, largest_component: bool = True) -> nx.Graph:
    """Build an undirected weighted graph from the SWOW-EN edge list."""

    graph = nx.Graph()
    for row in edgelist.itertuples(index=False):
        source = str(row.source)
        target = str(row.target)
        weight = float(row.weight)
        if source == target:
            continue
        if graph.has_edge(source, target):
            graph[source][target]["weight"] += weight
        else:
            graph.add_edge(source, target, weight=weight)

    if largest_component:
        largest_nodes = max(nx.connected_components(graph), key=len)
        graph = graph.subgraph(sorted(largest_nodes)).copy()

    return graph


def load_swow_en_graph(largest_component: bool = True) -> nx.Graph:
    """Load the validated SWOW-EN graph as a NetworkX graph."""

    return build_weighted_graph(load_swow_en_edgelist(), largest_component=largest_component)


def graph_eta(graph: nx.Graph) -> float:
    """Compute the density proxy eta = <k>^2 / N."""

    n_nodes = graph.number_of_nodes()
    mean_degree = (2.0 * graph.number_of_edges()) / n_nodes
    return float((mean_degree**2) / n_nodes)


def graph_summary(graph: nx.Graph) -> dict[str, Any]:
    """Return basic graph diagnostics for logging and JSON summaries."""

    weights = np.fromiter((data["weight"] for _, _, data in graph.edges(data=True)), dtype=float)
    return {
        "n_nodes": graph.number_of_nodes(),
        "n_edges": graph.number_of_edges(),
        "mean_degree": float(np.mean([degree for _, degree in graph.degree()])),
        "eta": graph_eta(graph),
        "weight_min": float(weights.min()) if len(weights) else 0.0,
        "weight_max": float(weights.max()) if len(weights) else 0.0,
        "is_connected": nx.is_connected(graph),
    }


def expected_exact_edge_order(graph: nx.Graph) -> list[tuple[str, str]]:
    """Reconstruct the edge order used by the validated Julia artifact.

    The validated Julia pipeline builds the largest connected component with
    lexicographically sorted node labels before collecting `edges(g_lcc)`.
    For a simple undirected graph, that yields the same lexicographic ordering
    by `(u, v)` over sorted endpoint labels.
    """

    return sorted((min(u, v), max(u, v)) for u, v in graph.edges())


def load_exact_orc_artifact(path: Path = SWOW_EXACT_ORC_JSON) -> dict[str, Any]:
    """Load the validated exact-LP SWOW-EN ORC artifact."""

    if not path.exists():
        raise FileNotFoundError(
            f"Exact ORC artifact not found at {path}. Run julia/scripts/unified_semantic_orc.jl first."
        )
    artifact = load_json(path)
    if "per_edge_curvatures" not in artifact:
        raise ValueError(f"Artifact at {path} does not contain `per_edge_curvatures`.")
    return artifact


def derive_exact_node_kappa(graph: nx.Graph, artifact: dict[str, Any] | None = None) -> pd.DataFrame:
    """Derive per-node mean curvature from the exact-LP edge artifact."""

    artifact = artifact or load_exact_orc_artifact()
    edge_curvatures = np.asarray(artifact["per_edge_curvatures"], dtype=float)
    ordered_edges = expected_exact_edge_order(graph)

    if len(ordered_edges) != len(edge_curvatures):
        raise ValueError(
            "Exact artifact edge count does not match reconstructed graph edge count: "
            f"{len(edge_curvatures)} vs {len(ordered_edges)}."
        )

    node_values: dict[str, list[float]] = {node: [] for node in graph.nodes()}
    for (source, target), kappa in zip(ordered_edges, edge_curvatures, strict=True):
        node_values[source].append(float(kappa))
        node_values[target].append(float(kappa))

    return pd.DataFrame(
        {
            "node": list(node_values.keys()),
            "kappa": [float(np.mean(values)) if values else 0.0 for values in node_values.values()],
        }
    ).sort_values("node", ignore_index=True)


def compute_graphricci_node_kappa(graph: nx.Graph, alpha: float = 0.5) -> pd.DataFrame:
    """Compute per-node ORC with GraphRicciCurvature as a Python fallback."""

    if OllivierRicci is None:
        raise ImportError("GraphRicciCurvature is not installed in the current environment.")

    orc = OllivierRicci(graph.copy(), alpha=alpha, verbose="ERROR", proc=1)
    orc.compute_ricci_curvature()

    node_values: dict[str, list[float]] = {node: [] for node in orc.G.nodes()}
    for source, target, data in orc.G.edges(data=True):
        kappa = float(data.get("ricciCurvature", 0.0))
        node_values[str(source)].append(kappa)
        node_values[str(target)].append(kappa)

    return pd.DataFrame(
        {
            "node": list(node_values.keys()),
            "kappa_graphricci": [float(np.mean(values)) if values else 0.0 for values in node_values.values()],
        }
    ).sort_values("node", ignore_index=True)


def load_node_metrics(path: Path = NODE_METRICS_PARQUET) -> pd.DataFrame:
    """Load the CPC node-metrics parquet artifact."""

    if not path.exists():
        raise FileNotFoundError(f"Node metrics not found at {path}. Run entropic_curvature.py first.")
    return pd.read_parquet(path)


def load_poincare_embedding(path: Path = POINCARE_EMBEDDING_PARQUET) -> pd.DataFrame:
    """Load the cached CPC Poincare embedding."""

    if not path.exists():
        raise FileNotFoundError(
            f"Poincare embedding not found at {path}. Run trajectory_simulator.py first."
        )
    return pd.read_parquet(path)


def load_valence_data(path: Path = SWOW_VALENCE_CSV) -> pd.DataFrame:
    """Load merged SWOW-EN valence annotations."""

    if not path.exists():
        raise FileNotFoundError(f"Valence table not found at {path}. Run valence_loader.py first.")
    return pd.read_csv(path)


def trajectory_path(regime: str) -> Path:
    """Return the standard parquet path for one regime's trajectories."""

    return CPC_RESULTS_DIR / f"trajectories_{regime}.parquet"


def trajectory_input_tensor_path(regime: str) -> Path:
    """Return the standard numpy tensor path for one regime's O-SSM inputs."""

    return CPC_DATA_DIR / f"trajectories_{regime}_input.npy"


def trajectory_node_index_path(regime: str) -> Path:
    """Return the numpy path for node-index trajectories."""

    return CPC_DATA_DIR / f"trajectories_{regime}_nodes.npy"


def trajectory_sounio_csv_path(regime: str) -> Path:
    """Return the compact row-wise CSV path exported for Sounio."""

    return CPC_SOUNIO_INPUT_DIR / f"trajectories_{regime}_nodes.csv"


def load_phase_transition_reference(path: Path = PHASE_TRANSITION_REFERENCE_JSON) -> pd.DataFrame:
    """Load the validated random-regular phase-transition reference curve."""

    payload = load_json(path)
    rows = []
    for row in payload.get("results", []):
        rows.append(
            {
                "N": int(row["N"]),
                "k_target": int(row["k_target"]),
                "k_actual": float(row["k_actual"]),
                "eta": float(row["ratio"]),
                "kappa_mean": float(row["kappa_mean"]),
                "kappa_std": float(row["kappa_std"]),
                "geometry": str(row["geometry"]),
            }
        )
    return pd.DataFrame(rows).sort_values("eta", ignore_index=True)


def infer_critical_eta(phase_df: pd.DataFrame) -> dict[str, float]:
    """Estimate the zero-crossing of mean curvature from the reference curve."""

    if phase_df.empty:
        raise ValueError("Phase-transition dataframe is empty.")

    eta = phase_df["eta"].to_numpy(dtype=float)
    kappa = phase_df["kappa_mean"].to_numpy(dtype=float)

    for idx in range(len(kappa) - 1):
        left = kappa[idx]
        right = kappa[idx + 1]
        if left == 0.0:
            return {"eta_critical": float(eta[idx]), "method": "exact_zero"}
        if left < 0.0 <= right or left <= 0.0 < right:
            slope = (right - left) / (eta[idx + 1] - eta[idx])
            crossing = eta[idx] - left / slope
            return {"eta_critical": float(crossing), "method": "linear_interpolation"}

    best_idx = int(np.argmin(np.abs(kappa)))
    return {"eta_critical": float(eta[best_idx]), "method": "minimum_absolute_curvature"}


def to_step_matrix(frame: pd.DataFrame, column: str) -> np.ndarray:
    """Convert a long trajectory dataframe column into trajectory x step matrix."""

    ordered = frame.sort_values(["trajectory_id", "step"], kind="mergesort")
    n_trajectories = int(ordered["trajectory_id"].max()) + 1
    trajectory_length = int(ordered["step"].max()) + 1
    values = ordered[column].to_numpy()
    return values.reshape(n_trajectories, trajectory_length)


def summarize_ci(samples: np.ndarray, confidence: float = 0.95) -> tuple[float, float]:
    """Return a percentile confidence interval for a 1D sample."""

    alpha = (1.0 - confidence) / 2.0
    lower = float(np.quantile(samples, alpha))
    upper = float(np.quantile(samples, 1.0 - alpha))
    return lower, upper


def softmax(scores: np.ndarray) -> np.ndarray:
    """Numerically stable softmax."""

    shifted = scores - float(np.max(scores))
    weights = np.exp(shifted)
    total = float(weights.sum())
    if total == 0.0:
        return np.full(len(scores), 1.0 / len(scores))
    return weights / total


def center_and_scale(values: np.ndarray) -> np.ndarray:
    """Z-score a vector, guarding against zero variance."""

    mean = float(values.mean())
    std = float(values.std(ddof=0))
    if std == 0.0:
        return np.zeros_like(values, dtype=float)
    return (values - mean) / std


def disk_project(points: np.ndarray, max_radius: float = 0.98) -> np.ndarray:
    """Project 2D coordinates back inside the Poincare disk."""

    radii = np.linalg.norm(points, axis=1)
    mask = radii >= max_radius
    if np.any(mask):
        points = points.copy()
        points[mask] = (points[mask] / radii[mask, None]) * max_radius
    return points


def nearest_node_indices(points: np.ndarray, coordinates: np.ndarray) -> np.ndarray:
    """Find the nearest node index for each 2D point."""

    squared = ((points[:, None, :] - coordinates[None, :, :]) ** 2).sum(axis=2)
    return np.argmin(squared, axis=1).astype(np.int32)


def smoke_summary() -> dict[str, Any]:
    """Return a tiny smoke summary for CLI entry points."""

    graph = load_swow_en_graph()
    artifact = load_exact_orc_artifact()
    return {
        "graph": graph_summary(graph),
        "artifact_edge_count": len(artifact["per_edge_curvatures"]),
        "regimes": [cfg.name for cfg in REGIME_CONFIGS],
    }


if __name__ == "__main__":
    print(json.dumps(smoke_summary(), indent=2, default=json_default))
