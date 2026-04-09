"""Simulate CPC 2026 cognitive trajectories on the validated SWOW-EN graph."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

try:
    from gensim.models.poincare import PoincareModel
except Exception:  # pragma: no cover - optional dependency at runtime
    PoincareModel = None  # type: ignore[assignment]

from common import (
    CPC_RESULTS_DIR,
    DEFAULT_SEED,
    HYBRID_EXAMPLES_PARQUET,
    LANGEVIN_EXAMPLES_PARQUET,
    POINCARE_EMBEDDING_PARQUET,
    REGIME_CONFIGS,
    SIMULATION_METADATA_JSON,
    STEPWISE_SUMMARY_CSV,
    SWOW_VALENCE_CSV,
    RegimeConfig,
    disk_project,
    ensure_directory,
    load_node_metrics,
    load_swow_en_graph,
    load_valence_data,
    nearest_node_indices,
    save_json,
    seed_everything,
    softmax,
    trajectory_path,
)


def compute_poincare_embedding(
    graph,
    output_path: Path = POINCARE_EMBEDDING_PARQUET,
    seed: int = DEFAULT_SEED,
    force: bool = False,
) -> pd.DataFrame:
    """Compute a 2D Poincare embedding, with a deterministic spring-layout fallback."""

    if output_path.exists() and not force:
        return pd.read_parquet(output_path)

    nodes = sorted(graph.nodes())
    engine = "spring_layout_fallback"
    coordinates: np.ndarray

    try:
        if PoincareModel is None:
            raise ImportError("gensim is not available")
        relations = [(source, target) for source, target in graph.edges()]
        relations += [(target, source) for source, target in graph.edges()]
        model = PoincareModel(relations, size=2, alpha=0.05, negative=5, burn_in=10, seed=seed)
        model.train(epochs=50)
        coordinates = np.vstack([model.kv.get_vector(node) for node in nodes]).astype(float)
        radii = np.linalg.norm(coordinates, axis=1)
        if np.any(radii >= 0.999):
            coordinates = disk_project(coordinates, max_radius=0.95)
        engine = "gensim_poincare"
    except Exception:
        layout = nx.spring_layout(graph, seed=seed, weight="weight", dim=2)
        coordinates = np.vstack([layout[node] for node in nodes]).astype(float)
        radii = np.linalg.norm(coordinates, axis=1)
        max_radius = float(radii.max()) if float(radii.max()) > 0 else 1.0
        coordinates = coordinates / max_radius
        coordinates = np.tanh(1.1 * coordinates)
        coordinates = disk_project(coordinates, max_radius=0.95)

    embedding = pd.DataFrame(
        {
            "node": nodes,
            "x": coordinates[:, 0],
            "y": coordinates[:, 1],
            "radius": np.linalg.norm(coordinates, axis=1),
            "embedding_engine": engine,
        }
    )
    ensure_directory(output_path.parent)
    embedding.to_parquet(output_path, index=False)
    return embedding


def prepare_model_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, int], list[str], list[np.ndarray]]:
    """Load graph, metrics, and valence tables in a shared node order."""

    graph = load_swow_en_graph()
    metrics = load_node_metrics().sort_values("node", ignore_index=True)
    valence = load_valence_data(SWOW_VALENCE_CSV).sort_values("node", ignore_index=True)
    merged = metrics.merge(valence.loc[:, ["node", "valence_centered"]], on="node", how="left")
    merged["valence_centered"] = merged["valence_centered"].fillna(0.0)

    nodes = merged["node"].tolist()
    node_to_index = {node: idx for idx, node in enumerate(nodes)}
    adjacency = [np.array([node_to_index[nbr] for nbr in sorted(graph.neighbors(node))], dtype=np.int32) for node in nodes]
    return metrics, valence, merged, node_to_index, nodes, adjacency


def build_transition_tables(
    graph,
    merged: pd.DataFrame,
    nodes: list[str],
    adjacency: list[np.ndarray],
    regime: RegimeConfig,
) -> list[np.ndarray]:
    """Build neighbor transition probabilities for a single regime."""

    entropy_norm = merged["entropy_norm"].to_numpy(dtype=float)
    valence = merged["valence_centered"].to_numpy(dtype=float)
    probabilities: list[np.ndarray] = []

    for node, neighbor_indices in zip(nodes, adjacency, strict=True):
        if len(neighbor_indices) == 0:
            probabilities.append(np.array([1.0], dtype=float))
            continue
        if regime.name == "psychotic":
            probabilities.append(np.full(len(neighbor_indices), 1.0 / len(neighbor_indices), dtype=float))
            continue

        weights = np.array([graph[node][nodes[idx]]["weight"] for idx in neighbor_indices], dtype=float)
        scores = regime.beta * np.log(np.clip(weights, 1e-12, None))
        scores -= regime.beta * entropy_norm[neighbor_indices]
        if regime.negative_bias_strength > 0.0:
            scores += regime.beta * regime.negative_bias_strength * (-valence[neighbor_indices])
        probabilities.append(softmax(scores))

    return probabilities


def flatten_trajectories(
    regime: str,
    trajectory_nodes: np.ndarray,
    node_names: list[str],
    metrics: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Convert trajectory node indices into long-form parquet-ready dataframes."""

    n_trajectories, trajectory_length = trajectory_nodes.shape
    flat_indices = trajectory_nodes.reshape(-1)
    metric_lookup = metrics.set_index("node")
    ordered_metrics = metric_lookup.loc[node_names]

    frame = pd.DataFrame(
        {
            "trajectory_id": np.repeat(np.arange(n_trajectories, dtype=np.int32), trajectory_length),
            "step": np.tile(np.arange(trajectory_length, dtype=np.int16), n_trajectories),
            "node": pd.Categorical.from_codes(flat_indices, categories=node_names),
            "C_ent": ordered_metrics["C_ent"].to_numpy(dtype=np.float32)[flat_indices],
            "entropy": ordered_metrics["entropy"].to_numpy(dtype=np.float32)[flat_indices],
            "kappa": ordered_metrics["kappa"].to_numpy(dtype=np.float32)[flat_indices],
        }
    )

    stepwise = pd.DataFrame(
        {
            "regime": regime,
            "step": np.arange(trajectory_length, dtype=np.int16),
            "mean_C_ent": ordered_metrics["C_ent"].to_numpy(dtype=np.float32)[trajectory_nodes].mean(axis=0),
            "mean_entropy": ordered_metrics["entropy"].to_numpy(dtype=np.float32)[trajectory_nodes].mean(axis=0),
            "mean_kappa": ordered_metrics["kappa"].to_numpy(dtype=np.float32)[trajectory_nodes].mean(axis=0),
        }
    )
    return frame, stepwise


def simulate_markov_regime(
    graph,
    metrics: pd.DataFrame,
    regime: RegimeConfig,
    n_trajectories: int,
    trajectory_length: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Simulate graph-constrained trajectories for one regime."""

    _, _, merged, _, nodes, adjacency = prepare_model_inputs()
    probabilities = build_transition_tables(graph, merged, nodes, adjacency, regime)
    rng = np.random.default_rng(seed)

    trajectory_nodes = np.empty((n_trajectories, trajectory_length), dtype=np.int32)
    trajectory_nodes[:, 0] = rng.integers(0, len(nodes), size=n_trajectories, dtype=np.int32)

    for step in range(1, trajectory_length):
        previous = trajectory_nodes[:, step - 1]
        next_nodes = np.empty_like(previous)
        for current in np.unique(previous):
            mask = previous == current
            neighbors = adjacency[int(current)]
            if len(neighbors) == 0:
                next_nodes[mask] = int(current)
                continue
            next_nodes[mask] = rng.choice(neighbors, size=int(mask.sum()), p=probabilities[int(current)])
        trajectory_nodes[:, step] = next_nodes

    return flatten_trajectories(regime.name, trajectory_nodes, nodes, metrics)


def simulate_langevin_like(
    embedding: pd.DataFrame,
    metrics: pd.DataFrame,
    n_trajectories: int = 200,
    trajectory_length: int = 500,
    seed: int = DEFAULT_SEED + 701,
    sigma: float = 0.08,
    drift_strength: float = 0.16,
) -> pd.DataFrame:
    """Generate exploratory Langevin-like trajectories on the embedding."""

    nodes = metrics["node"].tolist()
    coordinates = embedding.set_index("node").loc[nodes, ["x", "y"]].to_numpy(dtype=float)
    c_ent = metrics["C_ent"].to_numpy(dtype=float)
    c_ent = (c_ent - c_ent.mean()) / (c_ent.std(ddof=0) or 1.0)

    rng = np.random.default_rng(seed)
    start = rng.integers(0, len(nodes), size=n_trajectories, dtype=np.int32)
    positions = coordinates[start].copy()
    trajectory_nodes = np.empty((n_trajectories, trajectory_length), dtype=np.int32)
    trajectory_nodes[:, 0] = start

    for step in range(1, trajectory_length):
        current = trajectory_nodes[:, step - 1]
        local_targets = coordinates[current] * (1.0 + 0.25 * c_ent[current, None])
        drift = drift_strength * (local_targets - positions)
        noise = rng.normal(loc=0.0, scale=sigma, size=positions.shape)
        positions = disk_project(positions + drift + noise, max_radius=0.97)
        snapped = nearest_node_indices(positions, coordinates)
        trajectory_nodes[:, step] = snapped

    frame, _ = flatten_trajectories("langevin", trajectory_nodes, nodes, metrics)
    return frame


def simulate_hybrid_trajectories(
    embedding: pd.DataFrame,
    graph,
    metrics: pd.DataFrame,
    regime: RegimeConfig,
    n_trajectories: int = 200,
    trajectory_length: int = 500,
    seed: int = DEFAULT_SEED + 1701,
) -> pd.DataFrame:
    """Generate exploratory hybrid trajectories that mix graph jumps and disk drift."""

    _, _, merged, _, nodes, adjacency = prepare_model_inputs()
    probabilities = build_transition_tables(graph, merged, nodes, adjacency, regime)
    coordinates = embedding.set_index("node").loc[nodes, ["x", "y"]].to_numpy(dtype=float)

    rng = np.random.default_rng(seed)
    trajectory_nodes = np.empty((n_trajectories, trajectory_length), dtype=np.int32)
    trajectory_nodes[:, 0] = rng.integers(0, len(nodes), size=n_trajectories, dtype=np.int32)
    positions = coordinates[trajectory_nodes[:, 0]].copy()

    for step in range(1, trajectory_length):
        previous = trajectory_nodes[:, step - 1]
        next_nodes = np.empty_like(previous)
        for current in np.unique(previous):
            mask = previous == current
            neighbors = adjacency[int(current)]
            if len(neighbors) == 0:
                next_nodes[mask] = int(current)
                continue
            next_nodes[mask] = rng.choice(neighbors, size=int(mask.sum()), p=probabilities[int(current)])
        positions = disk_project(0.5 * positions + 0.5 * coordinates[next_nodes] + rng.normal(0.0, 0.03, positions.shape))
        trajectory_nodes[:, step] = nearest_node_indices(positions, coordinates)

    frame, _ = flatten_trajectories("hybrid", trajectory_nodes, nodes, metrics)
    return frame


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-trajectories", type=int, default=10_000, help="Number of trajectories per regime.")
    parser.add_argument("--trajectory-length", type=int, default=500, help="Number of steps per trajectory.")
    parser.add_argument(
        "--include-exploratory-engines",
        action="store_true",
        help="Also save small exploratory Langevin-like and hybrid trajectory examples.",
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Run a small simulation (100 trajectories x 50 steps) and print a short summary.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the CPC 2026 trajectory simulations."""

    args = parse_args()
    seed_everything(DEFAULT_SEED)
    graph = load_swow_en_graph()
    metrics = load_node_metrics()
    _ = load_valence_data()

    n_trajectories = 100 if args.smoke_test else args.n_trajectories
    trajectory_length = 50 if args.smoke_test else args.trajectory_length

    ensure_directory(CPC_RESULTS_DIR)
    embedding = compute_poincare_embedding(graph)

    stepwise_frames: list[pd.DataFrame] = []
    metadata = {
        "seed": DEFAULT_SEED,
        "n_trajectories_per_regime": n_trajectories,
        "trajectory_length": trajectory_length,
        "regimes": [asdict(cfg) for cfg in REGIME_CONFIGS],
        "embedding_path": str(POINCARE_EMBEDDING_PARQUET),
    }

    for offset, regime in enumerate(REGIME_CONFIGS):
        frame, stepwise = simulate_markov_regime(
            graph=graph,
            metrics=metrics,
            regime=regime,
            n_trajectories=n_trajectories,
            trajectory_length=trajectory_length,
            seed=DEFAULT_SEED + 100 * offset,
        )
        output_path = trajectory_path(regime.name)
        frame.to_parquet(output_path, index=False)
        stepwise_frames.append(stepwise)

    pd.concat(stepwise_frames, ignore_index=True).to_csv(STEPWISE_SUMMARY_CSV, index=False)

    if args.include_exploratory_engines or args.smoke_test:
        simulate_langevin_like(
            embedding=embedding,
            metrics=metrics,
            n_trajectories=min(200, n_trajectories),
            trajectory_length=trajectory_length,
        ).to_parquet(LANGEVIN_EXAMPLES_PARQUET, index=False)
        simulate_hybrid_trajectories(
            embedding=embedding,
            graph=graph,
            metrics=metrics,
            regime=REGIME_CONFIGS[0],
            n_trajectories=min(200, n_trajectories),
            trajectory_length=trajectory_length,
        ).to_parquet(HYBRID_EXAMPLES_PARQUET, index=False)
        metadata["exploratory_engines_saved"] = True
    else:
        metadata["exploratory_engines_saved"] = False

    save_json(SIMULATION_METADATA_JSON, metadata)

    if args.smoke_test:
        print(json.dumps({"saved_regimes": [cfg.name for cfg in REGIME_CONFIGS], **metadata}, indent=2))
        return

    print(
        f"Saved regime trajectories to {CPC_RESULTS_DIR} "
        f"({n_trajectories} trajectories x {trajectory_length} steps per regime)."
    )


if __name__ == "__main__":
    main()
