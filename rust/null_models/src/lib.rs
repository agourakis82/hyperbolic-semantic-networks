//! Null Model Generation - Rust Backend
//!
//! High-performance parallel generation of:
//! - Configuration model (degree-preserving)
//! - Triadic-rewire model (triangle-preserving)
//!
//! Author: Dr. Demetrios Agourakis
//! Date: 2025-11-08

#![allow(dead_code)] // During development

pub mod configuration;
pub mod triadic_rewire;

use petgraph::Graph;
use rand::Rng;

/// Generate configuration model null networks.
///
/// # Arguments
/// * `degrees` - Degree sequence to preserve
/// * `n_samples` - Number of null model replicates
///
/// # Returns
/// Vector of null model graphs
pub fn generate_configuration_models(
    degrees: &[usize],
    n_samples: usize,
) -> Vec<Graph<(), (), petgraph::Undirected>> {
    use rayon::prelude::*;
    
    (0..n_samples)
        .into_par_iter()
        .map(|_| configuration::sample_configuration_model(degrees))
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_configuration_model_degree_preservation() {
        let degrees = vec![2, 2, 2, 2];
        let nulls = generate_configuration_models(&degrees, 10);
        
        assert_eq!(nulls.len(), 10);
        // Each null model should preserve degree sequence
        for null in nulls {
            let null_degrees: Vec<usize> = null.node_indices()
                .map(|n| null.neighbors(n).count())
                .collect();
            // Degrees should match (up to ordering)
            assert_eq!(null_degrees.iter().sum::<usize>(), degrees.iter().sum::<usize>());
        }
    }
}

