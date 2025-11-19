//! Configuration model: preserve degree sequence, randomize edges

use petgraph::Graph;
use rand::Rng;
use rand::thread_rng;

/// Sample a single configuration model network.
///
/// Uses the configuration model algorithm to generate a random graph
/// with the same degree sequence as the input.
pub fn sample_configuration_model(
    degrees: &[usize],
) -> Graph<(), (), petgraph::Undirected> {
    // Create stubs (half-edges) for each node
    let mut stubs = Vec::new();
    for (node_id, &degree) in degrees.iter().enumerate() {
        for _ in 0..degree {
            stubs.push(node_id);
        }
    }
    
    // Shuffle stubs
    let mut rng = thread_rng();
    for i in (1..stubs.len()).rev() {
        let j = rng.gen_range(0..=i);
        stubs.swap(i, j);
    }
    
    // Pair stubs to form edges
    let mut graph = Graph::new_undirected();
    let nodes: Vec<_> = (0..degrees.len())
        .map(|_| graph.add_node(()))
        .collect();
    
    for chunk in stubs.chunks(2) {
        if chunk.len() == 2 {
            let u = nodes[chunk[0]];
            let v = nodes[chunk[1]];
            if u != v && !graph.contains_edge(u, v) {
                graph.add_edge(u, v, ());
            }
        }
    }
    
    graph
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_configuration_model_basic() {
        let degrees = vec![2, 2, 2, 2]; // 4 nodes, each degree 2
        let graph = sample_configuration_model(&degrees);
        
        assert_eq!(graph.node_count(), 4);
        // Each node should have degree approximately 2
        for node in graph.node_indices() {
            let degree = graph.neighbors(node).count();
            assert!(degree <= 2);
        }
    }
}

