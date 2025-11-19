//! Wasserstein-1 distance computation using Sinkhorn algorithm

use crate::sinkhorn::sinkhorn_iteration;

/// Compute Wasserstein-1 distance between two probability measures.
///
/// Uses the Sinkhorn algorithm for entropy-regularized optimal transport.
pub fn wasserstein1_distance(
    mu: &[f64],
    nu: &[f64],
    cost_matrix: &[f64],
    n: usize,
    epsilon: f64,
    max_iterations: usize,
) -> f64 {
    // Validate inputs
    assert_eq!(mu.len(), n, "mu must have length n");
    assert_eq!(nu.len(), n, "nu must have length n");
    assert_eq!(cost_matrix.len(), n * n, "cost_matrix must be n×n");
    
    // Normalize measures (ensure they sum to 1.0)
    let mu_sum: f64 = mu.iter().sum();
    let nu_sum: f64 = nu.iter().sum();
    
    let mu_normalized: Vec<f64> = mu.iter().map(|&x| x / mu_sum).collect();
    let nu_normalized: Vec<f64> = nu.iter().map(|&x| x / nu_sum).collect();
    
    // Run Sinkhorn algorithm
    let transport_matrix = sinkhorn_iteration(
        &mu_normalized,
        &nu_normalized,
        cost_matrix,
        n,
        epsilon,
        max_iterations,
    );
    
    // Compute Wasserstein-1 distance: sum of transport * cost
    let mut w1 = 0.0;
    for i in 0..n {
        for j in 0..n {
            w1 += transport_matrix[i * n + j] * cost_matrix[i * n + j];
        }
    }
    
    w1
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_wasserstein1_identical() {
        let mu = vec![0.5, 0.5];
        let nu = vec![0.5, 0.5];
        let cost = vec![0.0, 1.0, 1.0, 0.0];
        
        let result = wasserstein1_distance(&mu, &nu, &cost, 2, 0.01, 100);
        assert!((result - 0.0).abs() < 1e-4);
    }

    #[test]
    fn test_wasserstein1_different() {
        let mu = vec![1.0, 0.0];
        let nu = vec![0.0, 1.0];
        let cost = vec![0.0, 1.0, 1.0, 0.0];
        
        let result = wasserstein1_distance(&mu, &nu, &cost, 2, 0.01, 100);
        assert!((result - 1.0).abs() < 1e-4);
    }
}

