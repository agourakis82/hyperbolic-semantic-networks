"""
Pytest configuration and shared fixtures.
"""

import pytest
import networkx as nx
import numpy as np


@pytest.fixture
def simple_graph():
    """Create a simple test graph."""
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0)])
    return G


@pytest.fixture
def weighted_graph():
    """Create a weighted test graph."""
    G = nx.Graph()
    G.add_edge(0, 1, weight=0.8)
    G.add_edge(1, 2, weight=0.6)
    G.add_edge(2, 3, weight=0.9)
    G.add_edge(3, 0, weight=0.7)
    return G


@pytest.fixture
def triangle_graph():
    """Create a triangle graph (K3)."""
    return nx.complete_graph(3)


@pytest.fixture
def star_graph():
    """Create a star graph (hub and spokes)."""
    return nx.star_graph(5)


@pytest.fixture
def semantic_network_sample():
    """Create a sample semantic network."""
    G = nx.Graph()
    edges = [
        ('cat', 'animal', 0.9),
        ('dog', 'animal', 0.8),
        ('fish', 'animal', 0.7),
        ('cat', 'pet', 0.85),
        ('dog', 'pet', 0.9),
    ]
    for source, target, weight in edges:
        G.add_edge(source, target, weight=weight)
    return G


@pytest.fixture
def random_seed():
    """Set random seed for reproducibility."""
    np.random.seed(42)
    return 42
