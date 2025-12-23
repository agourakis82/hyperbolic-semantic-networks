//! Sinkhorn algorithm for entropy-regularized optimal transport

/// Run Sinkhorn iterations to compute optimal transport matrix.
///
/// Returns the transport matrix P (n×n, flattened row-major).
/// Implements early stopping based on convergence criterion.
pub fn sinkhorn_iteration(
    mu: &[f64],
    nu: &[f64],
    cost_matrix: &[f64],
    n: usize,
    epsilon: f64,
    max_iterations: usize,
) -> Vec<f64> {
    sinkhorn_iteration_with_convergence(mu, nu, cost_matrix, n, epsilon, max_iterations, 1e-6)
}

/// Run Sinkhorn iterations with configurable convergence threshold.
///
/// # Arguments
/// * `mu`, `nu` - Probability measures
/// * `cost_matrix` - Cost matrix (flattened)
/// * `n` - Size of measures
/// * `epsilon` - Entropy regularization
/// * `max_iterations` - Maximum iterations
/// * `convergence_threshold` - Stop when ||u_new - u_old||_1 < threshold
///
/// # Returns
/// Transport matrix P (n×n, flattened row-major)
pub fn sinkhorn_iteration_with_convergence(
    mu: &[f64],
    nu: &[f64],
    cost_matrix: &[f64],
    n: usize,
    epsilon: f64,
    max_iterations: usize,
    convergence_threshold: f64,
) -> Vec<f64> {
    // Initialize: K = exp(-C / epsilon)
    let mut k = vec![0.0; n * n];
    for i in 0..n {
        for j in 0..n {
            k[i * n + j] = (-cost_matrix[i * n + j] / epsilon).exp();
        }
    }

    // Initialize u and v (scaling vectors)
    let mut u = vec![1.0; n];
    let mut v = vec![1.0; n];
    let mut u_old = vec![1.0; n];

    // Sinkhorn iterations with convergence check
    for iteration in 0..max_iterations {
        // Save old u for convergence check
        u_old.copy_from_slice(&u);

        // Update u: u = mu / (K * v)
        for i in 0..n {
            let mut kv_sum = 0.0;
            for j in 0..n {
                kv_sum += k[i * n + j] * v[j];
            }
            if kv_sum > 1e-10 {
                u[i] = mu[i] / kv_sum;
            }
        }

        // Update v: v = nu / (K^T * u)
        for j in 0..n {
            let mut ktu_sum = 0.0;
            for i in 0..n {
                ktu_sum += k[i * n + j] * u[i];
            }
            if ktu_sum > 1e-10 {
                v[j] = nu[j] / ktu_sum;
            }
        }

        // Check convergence every 10 iterations (to reduce overhead)
        if iteration % 10 == 0 && iteration > 0 {
            let l1_diff: f64 = u.iter()
                .zip(u_old.iter())
                .map(|(a, b)| (a - b).abs())
                .sum();

            if l1_diff < convergence_threshold {
                // Converged early
                break;
            }
        }
    }

    // Compute transport matrix: P = diag(u) * K * diag(v)
    let mut transport = vec![0.0; n * n];
    for i in 0..n {
        for j in 0..n {
            transport[i * n + j] = u[i] * k[i * n + j] * v[j];
        }
    }

    transport
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sinkhorn_convergence() {
        let mu = vec![0.5, 0.5];
        let nu = vec![0.5, 0.5];
        let cost = vec![0.0, 1.0, 1.0, 0.0];

        let transport = sinkhorn_iteration(&mu, &nu, &cost, 2, 0.01, 100);

        // For identical measures, transport should be close to identity
        assert!((transport[0] - 0.5).abs() < 0.1);
        assert!((transport[3] - 0.5).abs() < 0.1);
    }

    #[test]
    fn test_sinkhorn_early_convergence() {
        let mu = vec![0.5, 0.5];
        let nu = vec![0.5, 0.5];
        let cost = vec![0.0, 1.0, 1.0, 0.0];

        // Should converge in much less than 1000 iterations
        let transport = sinkhorn_iteration_with_convergence(
            &mu, &nu, &cost, 2, 0.01, 1000, 1e-6
        );

        // Verify correctness
        assert!((transport[0] - 0.5).abs() < 0.1);
        assert!((transport[3] - 0.5).abs() < 0.1);
    }

    #[test]
    fn test_sinkhorn_marginal_constraints() {
        let mu = vec![0.3, 0.7];
        let nu = vec![0.4, 0.6];
        let cost = vec![0.0, 1.0, 1.0, 0.0];

        let transport = sinkhorn_iteration(&mu, &nu, &cost, 2, 0.1, 500);

        // Verify marginal constraints: sum over rows should match mu
        let row_sum_0 = transport[0] + transport[1];
        let row_sum_1 = transport[2] + transport[3];
        assert!((row_sum_0 - mu[0]).abs() < 0.05);
        assert!((row_sum_1 - mu[1]).abs() < 0.05);

        // Verify marginal constraints: sum over cols should match nu
        let col_sum_0 = transport[0] + transport[2];
        let col_sum_1 = transport[1] + transport[3];
        assert!((col_sum_0 - nu[0]).abs() < 0.05);
        assert!((col_sum_1 - nu[1]).abs() < 0.05);
    }
}

