#!/usr/bin/env python3
"""
Visualização 3D de fluxo semântico
Criado: 2025-11-07 15:45:00 -03
Autor: AI Assistant + Dr. Agourakis

Descrição:
-----------
Pipeline experimental para mapear redes semântico-cognitivas em 3D,
integrando curvatura Ollivier, homologia persistente e um pseudo-Ricci
flow iterativo. O objetivo é produzir dashboards interativos (Plotly)
que acompanham a evolução da "resistência semântica" no tempo,
registrando métricas como entropia, coerência e small-worldness.

O módulo não substitui as análises principais do manuscrito; ele serve
como base para o suplemento digital planejado na Seção 4.5.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import networkx as nx
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from GraphRicciCurvature.OllivierRicci import OllivierRicci
from gudhi import RipsComplex
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors


@dataclass
class SnapshotState:
    step: int
    node_curvature: Dict[int, float]
    graph_metrics: Dict[str, float]


@dataclass
class FlowResults:
    history: List[SnapshotState]
    edge_history: List[Dict[Tuple[int, int], float]]


# ---------------------------------------------------------------------------
# Carga de dados e construção do grafo
# ---------------------------------------------------------------------------


def load_embeddings(path: Path) -> np.ndarray:
    """Carrega embeddings (N x D) em formato .npy ou .csv."""
    if path.suffix.lower() == ".npy":
        data = np.load(path)
    else:
        data = pd.read_csv(path).values
    if data.ndim != 2:
        raise ValueError(f"Embeddings devem ser 2D, obtido shape={data.shape}")
    return data.astype(np.float32)


def ensure_three_dimensions(data: np.ndarray) -> np.ndarray:
    """Reduz para 3D usando PCA caso o embedding tenha dimensão > 3."""
    if data.shape[1] <= 3:
        return data
    reducer = PCA(n_components=3, random_state=42)
    return reducer.fit_transform(data)


def build_knn_graph(
    embeddings: np.ndarray,
    k: int = 8,
    metric: str = "cosine",
) -> nx.Graph:
    """
    Constrói grafo k-NN ponderado.

    Peso = exp(-distância) para garantir positividade.
    """
    nbrs = NearestNeighbors(n_neighbors=k + 1, metric=metric)
    nbrs.fit(embeddings)
    distances, indices = nbrs.kneighbors(embeddings)

    G = nx.Graph()
    n = embeddings.shape[0]
    G.add_nodes_from(range(n))

    for i in range(n):
        for dist, j in zip(distances[i, 1:], indices[i, 1:]):
            weight = math.exp(-float(dist))
            if G.has_edge(i, j):
                if weight > G[i][j]["weight"]:
                    G[i][j]["weight"] = weight
            else:
                G.add_edge(i, j, weight=weight)

    if not nx.is_connected(G):
        largest = max(nx.connected_components(G), key=len)
        G = G.subgraph(largest).copy()
    return G


# ---------------------------------------------------------------------------
# Curvatura, métricas e pseudo-Ricci flow
# ---------------------------------------------------------------------------


def compute_ollivier_curvature(G: nx.Graph, alpha: float = 0.5) -> nx.Graph:
    orc = OllivierRicci(G, alpha=alpha, weight="weight", verbose="ERROR")
    orc.compute_ricci_curvature()
    return orc.G


def node_curvature_map(G: nx.Graph) -> Dict[int, float]:
    values = {}
    for node in G.nodes():
        curvs = [
            data.get("ricciCurvature", 0.0)
            for _, _, data in G.edges(node, data=True)
        ]
        values[node] = float(np.mean(curvs)) if curvs else 0.0
    return values


def graph_entropy(G: nx.Graph) -> float:
    strengths = np.array([G.degree(n, weight="weight") for n in G.nodes()])
    total = strengths.sum()
    if total == 0.0:
        return 0.0
    probs = strengths / total
    probs = np.clip(probs, 1e-12, 1.0)
    return float(-(probs * np.log(probs)).sum())


def coherence_phi(node_curvatures: Iterable[float]) -> float:
    curvs = np.array(list(node_curvatures))
    variance = np.var(curvs)
    return float(1.0 / (1.0 + variance))


def small_world_sigma(G: nx.Graph) -> float:
    if not nx.is_connected(G):
        largest = max(nx.connected_components(G), key=len)
        H = G.subgraph(largest).copy()
    else:
        H = G
    C = nx.average_clustering(H, weight="weight")
    try:
        L = nx.average_shortest_path_length(H, weight="weight")
    except nx.NetworkXError:
        L = float("inf")
    density = nx.density(H)
    if L == 0 or math.isinf(L):
        return 0.0
    return float((C / L) * (1.0 + density))


def compute_graph_metrics(G: nx.Graph, node_curvatures: Dict[int, float]) -> Dict[str, float]:
    curv_values = np.array(list(node_curvatures.values()))
    edges_curv = [
        data.get("ricciCurvature", 0.0)
        for _, _, data in G.edges(data=True)
    ]
    return {
        "mean_curvature": float(curv_values.mean()),
        "std_curvature": float(curv_values.std()),
        "edge_mean_curvature": float(np.mean(edges_curv)) if edges_curv else 0.0,
        "clustering": float(nx.average_clustering(G, weight="weight")),
        "entropy": graph_entropy(G),
        "coherence_phi": coherence_phi(curv_values),
        "small_world_sigma": small_world_sigma(G),
        "edge_weight_mean": float(np.mean([d["weight"] for _, _, d in G.edges(data=True)])),
    }


def run_pseudo_ricci_flow(
    G: nx.Graph,
    iterations: int = 6,
    step: float = 0.5,
    alpha: float = 0.5,
) -> FlowResults:
    working_graph = G.copy()
    history: List[SnapshotState] = []
    edge_history: List[Dict[Tuple[int, int], float]] = []

    for t in range(iterations + 1):
        working_graph = compute_ollivier_curvature(working_graph, alpha=alpha)
        node_curv = node_curvature_map(working_graph)
        metrics = compute_graph_metrics(working_graph, node_curv)

        history.append(SnapshotState(step=t, node_curvature=node_curv, graph_metrics=metrics))
        edge_history.append(
            {(u, v): working_graph[u][v]["weight"] for u, v in working_graph.edges()}
        )

        if t == iterations:
            break

        for u, v, data in working_graph.edges(data=True):
            kappa_uv = data.get("ricciCurvature", 0.0)
            weight = data.get("weight", 1.0)
            update_factor = 1.0 - step * kappa_uv
            update_factor = max(0.1, min(update_factor, 2.5))
            data["weight"] = float(weight * update_factor)

    return FlowResults(history=history, edge_history=edge_history)


# ---------------------------------------------------------------------------
# Homologia persistente
# ---------------------------------------------------------------------------


def compute_persistence(points: np.ndarray, max_dimension: int = 2):
    rips = RipsComplex(points=points)
    simplex_tree = rips.create_simplex_tree(max_dimension=max_dimension)
    diag = simplex_tree.persistence()
    return diag


def summarize_persistence(diagram) -> Dict[str, float]:
    summary = {"beta0": 0.0, "beta1": 0.0, "beta2": 0.0, "total_persistence": 0.0}
    total = 0.0
    for dim, (birth, death) in diagram:
        if math.isinf(death):
            death = birth + 1.0
        lifespan = max(0.0, death - birth)
        total += lifespan
        key = f"beta{dim}"
        if key in summary:
            summary[key] += 1.0
    summary["total_persistence"] = total
    return summary


# ---------------------------------------------------------------------------
# Visualização Plotly
# ---------------------------------------------------------------------------


def build_plotly_animation(
    embeddings: np.ndarray,
    flow: FlowResults,
    output_path: Path,
) -> None:
    nodes = sorted(flow.history[0].node_curvature.keys())
    coords = embeddings[nodes]

    traces_edges = []
    base_edges = flow.edge_history[0]
    for (u, v), weight in base_edges.items():
        traces_edges.append(go.Scatter3d(
            x=[coords[u][0], coords[v][0], None],
            y=[coords[u][1], coords[v][1], None],
            z=[coords[u][2], coords[v][2], None],
            mode="lines",
            line=dict(color="rgba(120,120,120,0.25)", width=1 + weight * 2),
            hoverinfo="none",
            showlegend=False,
        ))

    frames = []
    for snapshot in flow.history:
        colors = [snapshot.node_curvature[n] for n in nodes]
        frames.append(go.Frame(
            data=[
                go.Scatter3d(
                    x=coords[:, 0],
                    y=coords[:, 1],
                    z=coords[:, 2],
                    mode="markers",
                    marker=dict(
                        size=5,
                        color=colors,
                        colorscale="RdBu",
                        colorbar=dict(title="κ"),
                        cmin=min(colors),
                        cmax=max(colors),
                    ),
                    name=f"t={snapshot.step}",
                )
            ],
            name=f"t={snapshot.step}",
        ))

    initial_colors = [flow.history[0].node_curvature[n] for n in nodes]
    scatter_nodes = go.Scatter3d(
        x=coords[:, 0],
        y=coords[:, 1],
        z=coords[:, 2],
        mode="markers",
        marker=dict(
            size=5,
            color=initial_colors,
            colorscale="RdBu",
            colorbar=dict(title="κ"),
            cmin=min(initial_colors),
            cmax=max(initial_colors),
        ),
        name="t=0",
    )

    layout = go.Layout(
        scene=dict(
            xaxis=dict(title="Dim 1"),
            yaxis=dict(title="Dim 2"),
            zaxis=dict(title="Dim 3"),
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        title="Fluxo semântico 3D – curvatura em cores",
        updatemenus=[
            dict(
                type="buttons",
                buttons=[
                    dict(label="Play", method="animate", args=[None, {"frame": {"duration": 700, "redraw": True}}]),
                    dict(label="Pause", method="animate", args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}]),
                ],
            )
        ],
        sliders=[
            dict(
                steps=[
                    dict(method="animate", args=[[frame.name], {"mode": "immediate", "frame": {"duration": 0, "redraw": True}}],
                         label=frame.name)
                    for frame in frames
                ],
                transition={"duration": 200},
            )
        ],
    )

    fig = go.Figure(data=[scatter_nodes] + traces_edges, layout=layout, frames=frames)
    fig.write_html(str(output_path))


# ---------------------------------------------------------------------------
# Execução CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline de visualização semântica 3D com curvatura + homologia.")
    parser.add_argument("--embeddings", type=Path, required=True, help="Arquivo de embeddings (npy ou csv).")
    parser.add_argument("--output-dir", type=Path, required=True, help="Diretório para guardar resultados.")
    parser.add_argument("--k", type=int, default=8, help="Número de vizinhos no grafo k-NN.")
    parser.add_argument("--flow-iterations", type=int, default=6, help="Número de iterações do pseudo-Ricci flow.")
    parser.add_argument("--flow-step", type=float, default=0.5, help="Passo de atualização dos pesos.")
    parser.add_argument("--alpha", type=float, default=0.5, help="Parâmetro α da curvatura Ollivier.")
    parser.add_argument("--max-persistence-dim", type=int, default=2, help="Dimensão máxima para homologia persistente.")
    parser.add_argument("--export-dashboard", action="store_true", help="Gera HTML interativo com Plotly.")

    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    embeddings = load_embeddings(args.embeddings)
    embeddings_3d = ensure_three_dimensions(embeddings)

    graph = build_knn_graph(embeddings, k=args.k)
    flow = run_pseudo_ricci_flow(graph, iterations=args.flow_iterations, step=args.flow_step, alpha=args.alpha)

    diagram = compute_persistence(embeddings_3d, max_dimension=args.max_persistence_dim)
    persistence_summary = summarize_persistence(diagram)

    metrics_log = []
    for snapshot in flow.history:
        entry = {
            "step": snapshot.step,
            **snapshot.graph_metrics,
        }
        metrics_log.append(entry)

    payload = {
        "config": {
            "k": args.k,
            "flow_iterations": args.flow_iterations,
            "flow_step": args.flow_step,
            "alpha": args.alpha,
            "max_persistence_dim": args.max_persistence_dim,
        },
        "persistence_summary": persistence_summary,
        "metrics": metrics_log,
    }

    metrics_path = args.output_dir / "semantic_flow_metrics.json"
    metrics_path.write_text(json.dumps(payload, indent=2))

    if args.export_dashboard:
        dashboard_path = args.output_dir / "semantic_flow_dashboard.html"
        build_plotly_animation(ensure_three_dimensions(embeddings), flow, dashboard_path)

    print("✅ Pipeline concluído.")
    print(f"   Métricas salvas em: {metrics_path}")
    if args.export_dashboard:
        print(f"   Dashboard interativo: {dashboard_path}")


if __name__ == "__main__":
    main()



