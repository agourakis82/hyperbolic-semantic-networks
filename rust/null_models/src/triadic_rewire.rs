//! Triadic-rewire: preserve triangle counts, randomize other edges

use petgraph::Graph;
use petgraph::graph::NodeIndex;
use petgraph::Undirected;
use rand::Rng;
use rand::thread_rng;
use std::collections::HashSet;

/// Sample a triadic-rewire null model.
///
/// Preserves triangle counts while randomizing edges.
/// Uses double-edge swap that avoids breaking triangles.
///
/// # Algorithm
/// 1. Identify all triangles in the graph
/// 2. Perform edge rewiring via double-edge swaps
/// 3. Only accept swaps that preserve triangle count
pub fn sample_triadic_rewire(
    graph: &Graph<(), (), petgraph::Undirected>,
) -> Graph<(), (), petgraph::Undirected> {
    let mut new_graph = graph.clone();
    let n = new_graph.node_count();
    let m = new_graph.edge_count();

    if n < 3 || m < 3 {
        // Too small to rewire meaningfully
        return new_graph;
    }

    // Count initial triangles
    let initial_triangle_count = count_triangles(&new_graph);

    let mut rng = thread_rng();
    let num_swaps = m * 10; // Attempt 10 swaps per edge

    for _ in 0..num_swaps {
        // Select two random edges
        let edges: Vec<_> = new_graph.edge_indices().collect();
        if edges.len() < 2 {
            continue;
        }

        let edge1_idx = rng.gen_range(0..edges.len());
        let mut edge2_idx = rng.gen_range(0..edges.len());
        while edge2_idx == edge1_idx {
            edge2_idx = rng.gen_range(0..edges.len());
        }

        let edge1 = new_graph.edge_endpoints(edges[edge1_idx]);
        let edge2 = new_graph.edge_endpoints(edges[edge2_idx]);

        if edge1.is_none() || edge2.is_none() {
            continue;
        }

        let (a, b) = edge1.unwrap();
        let (c, d) = edge2.unwrap();

        // Attempt swap: (a,b) and (c,d) → (a,c) and (b,d)
        // Only if no self-loops or multi-edges created
        if a != c && b != d && a != d && b != c
            && !new_graph.contains_edge(a, c)
            && !new_graph.contains_edge(b, d)
        {
            // Try the swap
            new_graph.remove_edge(edges[edge1_idx]);
            new_graph.remove_edge(edges[edge2_idx]);
            new_graph.add_edge(a, c, ());
            new_graph.add_edge(b, d, ());

            // Check if triangle count preserved
            let new_triangle_count = count_triangles(&new_graph);

            if new_triangle_count == initial_triangle_count {
                // Accept swap
                continue;
            } else {
                // Reject swap - revert
                new_graph.remove_edge(new_graph.find_edge(a, c).unwrap());
                new_graph.remove_edge(new_graph.find_edge(b, d).unwrap());
                new_graph.add_edge(a, b, ());
                new_graph.add_edge(c, d, ());
            }
        }
    }

    new_graph
}

/// Count triangles in an undirected graph.
///
/// Uses node iterator method: for each node, count common neighbors
/// of pairs of its neighbors.
fn count_triangles(graph: &Graph<(), (), Undirected>) -> usize {
    let mut triangle_count = 0;

    for node in graph.node_indices() {
        let neighbors: Vec<_> = graph.neighbors(node).collect();

        // For each pair of neighbors, check if they're connected
        for i in 0..neighbors.len() {
            for j in (i + 1)..neighbors.len() {
                if graph.contains_edge(neighbors[i], neighbors[j]) {
                    triangle_count += 1;
                }
            }
        }
    }

    // Each triangle is counted 3 times (once per vertex)
    triangle_count / 3
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_count_triangles() {
        let mut graph = Graph::new_undirected();
        let a = graph.add_node(());
        let b = graph.add_node(());
        let c = graph.add_node(());

        graph.add_edge(a, b, ());
        graph.add_edge(b, c, ());
        graph.add_edge(c, a, ()); // One triangle

        assert_eq!(count_triangles(&graph), 1);
    }

    #[test]
    fn test_triadic_rewire_preserves_triangles() {
        let mut graph = Graph::new_undirected();
        let a = graph.add_node(());
        let b = graph.add_node(());
        let c = graph.add_node(());
        let d = graph.add_node(());

        graph.add_edge(a, b, ());
        graph.add_edge(b, c, ());
        graph.add_edge(c, a, ()); // Triangle
        graph.add_edge(c, d, ());
        graph.add_edge(d, a, ());

        let initial_triangles = count_triangles(&graph);
        let rewired = sample_triadic_rewire(&graph);

        assert_eq!(rewired.node_count(), 4);
        assert_eq!(count_triangles(&rewired), initial_triangles);
    }

    #[test]
    fn test_triadic_rewire_preserves_edge_count() {
        let mut graph = Graph::new_undirected();
        let a = graph.add_node(());
        let b = graph.add_node(());
        let c = graph.add_node(());
        let d = graph.add_node(());

        graph.add_edge(a, b, ());
        graph.add_edge(b, c, ());
        graph.add_edge(c, d, ());
        graph.add_edge(d, a, ());

        let initial_edges = graph.edge_count();
        let rewired = sample_triadic_rewire(&graph);

        assert_eq!(rewired.edge_count(), initial_edges);
    }

    #[test]
    fn test_triadic_rewire_small_graph() {
        // Graph too small to rewire
        let mut graph = Graph::new_undirected();
        let a = graph.add_node(());
        let b = graph.add_node(());

        graph.add_edge(a, b, ());

        let rewired = sample_triadic_rewire(&graph);
        assert_eq!(rewired.edge_count(), 1);
    }
}

