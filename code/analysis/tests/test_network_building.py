"""
Tests for network building and preprocessing functions.
"""

import pytest
import networkx as nx
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestNetworkBuilding:
    """Test network construction from SWOW data."""

    def test_simple_network_creation(self):
        """Test creating a simple network from edge list."""
        edges = pd.DataFrame({
            'source': ['cat', 'dog', 'fish'],
            'target': ['animal', 'animal', 'animal'],
            'weight': [0.8, 0.9, 0.7]
        })

        G = nx.Graph()
        for _, row in edges.iterrows():
            G.add_edge(row['source'], row['target'], weight=row['weight'])

        assert G.number_of_nodes() == 4
        assert G.number_of_edges() == 3
        assert nx.is_connected(G)

    def test_directed_to_undirected_conversion(self):
        """Test converting directed to undirected graph."""
        G_dir = nx.DiGraph()
        G_dir.add_edge('a', 'b', weight=0.5)
        G_dir.add_edge('b', 'a', weight=0.3)

        G_undir = G_dir.to_undirected()

        assert G_undir.number_of_nodes() == 2
        assert G_undir.number_of_edges() == 1

    def test_largest_component_extraction(self):
        """Test extracting largest connected component."""
        G = nx.Graph()
        # Component 1
        G.add_edge(1, 2)
        G.add_edge(2, 3)
        # Component 2 (larger)
        G.add_edge(4, 5)
        G.add_edge(5, 6)
        G.add_edge(6, 7)

        if not nx.is_connected(G):
            largest_cc = max(nx.connected_components(G), key=len)
            G_lcc = G.subgraph(largest_cc).copy()

            assert G_lcc.number_of_nodes() == 4
            assert nx.is_connected(G_lcc)

    def test_weight_normalization(self):
        """Test edge weight normalization."""
        G = nx.Graph()
        G.add_edge('a', 'b', weight=100)
        G.add_edge('b', 'c', weight=200)

        weights = [G[u][v]['weight'] for u, v in G.edges()]
        max_weight = max(weights)

        for u, v in G.edges():
            G[u][v]['weight'] /= max_weight

        normalized_weights = [G[u][v]['weight'] for u, v in G.edges()]
        assert max(normalized_weights) == 1.0
        assert all(0 <= w <= 1 for w in normalized_weights)


class TestNetworkMetrics:
    """Test basic network metrics computation."""

    def test_degree_distribution(self):
        """Test degree computation."""
        G = nx.cycle_graph(5)
        degrees = [G.degree(n) for n in G.nodes()]

        assert all(d == 2 for d in degrees)  # Cycle graph has constant degree 2

    def test_clustering_coefficient(self):
        """Test clustering coefficient computation."""
        # Triangle
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (2, 0)])

        clustering = nx.average_clustering(G)
        assert clustering == 1.0  # Perfect triangle

    def test_triangle_count(self):
        """Test triangle counting."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (2, 0)])  # One triangle

        triangles = sum(nx.triangles(G).values()) // 3
        assert triangles == 1


class TestDataValidation:
    """Test data validation and error handling."""

    def test_empty_graph_handling(self):
        """Test handling of empty graphs."""
        G = nx.Graph()

        assert G.number_of_nodes() == 0
        assert G.number_of_edges() == 0

    def test_negative_weights_detection(self):
        """Test detection of negative weights."""
        G = nx.Graph()
        G.add_edge('a', 'b', weight=-0.5)

        weights = [G[u][v]['weight'] for u, v in G.edges()]
        has_negative = any(w < 0 for w in weights)

        assert has_negative is True

    def test_self_loop_detection(self):
        """Test detection of self-loops."""
        G = nx.Graph()
        G.add_edge(1, 1)  # Self-loop

        assert nx.number_of_selfloops(G) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
