"""
Tests for curvature computation functions.
"""

import pytest
import networkx as nx
import numpy as np
from GraphRicciCurvature.OllivierRicci import OllivierRicci


class TestCurvatureComputation:
    """Test Ollivier-Ricci curvature computation."""

    def test_curvature_bounds(self):
        """Test that curvature values are in valid range [-1, 1]."""
        # Create simple graph
        G = nx.cycle_graph(5)

        orc = OllivierRicci(G, alpha=0.5, verbose="ERROR")
        orc.compute_ricci_curvature()
        G_orc = orc.G

        curvatures = [G_orc[u][v]['ricciCurvature'] for u, v in G_orc.edges()]

        # All curvatures should be in [-1, 1]
        assert all(-1 <= k <= 1 for k in curvatures)

    def test_positive_curvature_triangle(self):
        """Test that triangles have positive curvature."""
        # Complete triangle (K3)
        G = nx.complete_graph(3)

        orc = OllivierRicci(G, alpha=0.5, verbose="ERROR")
        orc.compute_ricci_curvature()
        G_orc = orc.G

        curvatures = [G_orc[u][v]['ricciCurvature'] for u, v in G_orc.edges()]
        mean_curvature = np.mean(curvatures)

        # Triangle should have positive curvature
        assert mean_curvature > 0

    def test_negative_curvature_bridge(self):
        """Test that bridge edges between clusters have negative curvature.

        Canonical example: the bridge of a dumbbell graph (two triangles
        joined by a single edge) has kappa = -1/3 with alpha=0.5.
        Note: trees are NOT generically negative under Ollivier curvature
        with idleness — a star with alpha=0.5 has mean kappa = +0.2,
        because each leaf's measure keeps mass on itself.
        """
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (2, 0),
                          (3, 4), (4, 5), (5, 3),
                          (2, 3)])  # bridge

        orc = OllivierRicci(G, alpha=0.5, verbose="ERROR")
        orc.compute_ricci_curvature()
        G_orc = orc.G

        bridge_kappa = G_orc[2][3]['ricciCurvature']
        assert bridge_kappa < 0
        assert abs(bridge_kappa - (-1.0 / 3.0)) < 1e-6

    def test_star_curvature_exact_value(self):
        """Regression test: star graph with alpha=0.5 has mean kappa = +0.2.

        The leaf measure mu_y = 0.5*d_leaf + 0.5*d_center keeps 0.1 of its
        mass on the leaf itself (distance 0); the remaining 0.4 travels
        distance 2, giving W1 = 0.8 and kappa = +0.2 per edge.
        """
        G = nx.star_graph(5)

        orc = OllivierRicci(G, alpha=0.5, verbose="ERROR")
        orc.compute_ricci_curvature()
        G_orc = orc.G

        curvatures = [G_orc[u][v]['ricciCurvature'] for u, v in G_orc.edges()]
        mean_curvature = np.mean(curvatures)

        assert abs(mean_curvature - 0.2) < 1e-6

    def test_alpha_parameter_effect(self):
        """Test that alpha parameter affects curvature.

        Uses a star: mean kappa is +0.2 at alpha=0.1 and +0.04 at
        alpha=0.9. A cycle is unsuitable here — it has kappa = 0 for
        every alpha.
        """
        G = nx.star_graph(5)

        orc1 = OllivierRicci(G, alpha=0.1, verbose="ERROR")
        orc1.compute_ricci_curvature()
        kappa1 = np.mean([orc1.G[u][v]['ricciCurvature']
                          for u, v in orc1.G.edges()])

        orc2 = OllivierRicci(G, alpha=0.9, verbose="ERROR")
        orc2.compute_ricci_curvature()
        kappa2 = np.mean([orc2.G[u][v]['ricciCurvature']
                          for u, v in orc2.G.edges()])

        # Different alpha should give different results
        assert abs(kappa1 - kappa2) > 0.01

    def test_curvature_statistics(self):
        """Test computing curvature statistics."""
        G = nx.karate_club_graph()

        orc = OllivierRicci(G, alpha=0.5, verbose="ERROR")
        orc.compute_ricci_curvature()
        G_orc = orc.G

        curvatures = [G_orc[u][v]['ricciCurvature'] for u, v in G_orc.edges()]

        stats = {
            'mean': np.mean(curvatures),
            'median': np.median(curvatures),
            'std': np.std(curvatures),
            'min': np.min(curvatures),
            'max': np.max(curvatures)
        }

        # Check all statistics are finite
        assert all(np.isfinite(v) for v in stats.values())
        # Check bounds
        assert -1 <= stats['min'] <= stats['max'] <= 1


class TestWeightedCurvature:
    """Test curvature computation on weighted graphs."""

    def test_weighted_graph_curvature(self):
        """Test curvature on weighted graph."""
        G = nx.Graph()
        G.add_edge(0, 1, weight=1.0)
        G.add_edge(1, 2, weight=2.0)
        G.add_edge(2, 0, weight=1.5)

        orc = OllivierRicci(G, alpha=0.5, verbose="ERROR")
        orc.compute_ricci_curvature()
        G_orc = orc.G

        curvatures = [G_orc[u][v]['ricciCurvature'] for u, v in G_orc.edges()]

        # Should compute successfully
        assert len(curvatures) == 3
        assert all(np.isfinite(k) for k in curvatures)

    def test_uniform_weights_vs_unweighted(self):
        """Test that uniform weights give similar results to unweighted."""
        G_unweighted = nx.cycle_graph(5)

        G_weighted = nx.cycle_graph(5)
        for u, v in G_weighted.edges():
            G_weighted[u][v]['weight'] = 1.0

        orc1 = OllivierRicci(G_unweighted, alpha=0.5, verbose="ERROR")
        orc1.compute_ricci_curvature()
        kappa1 = np.mean([orc1.G[u][v]['ricciCurvature']
                          for u, v in orc1.G.edges()])

        orc2 = OllivierRicci(G_weighted, alpha=0.5, verbose="ERROR")
        orc2.compute_ricci_curvature()
        kappa2 = np.mean([orc2.G[u][v]['ricciCurvature']
                          for u, v in orc2.G.edges()])

        # Should be very close
        assert abs(kappa1 - kappa2) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
