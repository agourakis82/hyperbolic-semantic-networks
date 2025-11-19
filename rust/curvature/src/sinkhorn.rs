//! Sinkhorn algorithm for entropy-regularized optimal transport

/// Run Sinkhorn iterations to compute optimal transport matrix.
///
/// Returns the transport matrix P (n×n, flattened row-major).
pub fn sinkhorn_iteration(
    mu: &[f64],
    nu: &[f64],
    cost_matrix: &[f64],
    n: usize,
    epsilon: f64,
    max_iterations: usize,
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
    
    // Sinkhorn iterations
    for _iteration in 0..max_iterations {
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
}

