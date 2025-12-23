//! Hyperbolic Curvature Computation - Rust Backend
//!
//! This crate provides high-performance implementations of:
//! - Wasserstein-1 distance computation
//! - Sinkhorn algorithm for optimal transport
//! - Ollivier-Ricci curvature core computations
//!
//! Author: Dr. Demetrios Agourakis
//! Date: 2025-11-08

#![allow(dead_code)] // During development

pub mod wasserstein;
pub mod sinkhorn;

use wasserstein::wasserstein1_distance;
use sinkhorn::sinkhorn_iteration;

#[cfg(feature = "logging")]
use log::{error, warn, info, debug};

/// Compute Wasserstein-1 distance between two probability measures.
///
/// # Arguments
/// * `mu` - First probability measure (must sum to 1.0)
/// * `nu` - Second probability measure (must sum to 1.0)
/// * `cost_matrix` - Cost matrix (flattened, row-major)
/// * `n` - Size of measures (mu.len() == nu.len() == n)
/// * `epsilon` - Entropy regularization parameter
/// * `max_iterations` - Maximum Sinkhorn iterations
///
/// # Returns
/// Wasserstein-1 distance value
#[no_mangle]
pub extern "C" fn compute_wasserstein1(
    mu: *const f64,
    nu: *const f64,
    cost_matrix: *const f64,
    n: usize,
    epsilon: f64,
    max_iterations: usize,
) -> f64 {
    // Validate input pointers
    if mu.is_null() || nu.is_null() || cost_matrix.is_null() {
        eprintln!("ERROR: Null pointer passed to compute_wasserstein1");
        return f64::NAN;
    }

    // Validate parameters
    if n == 0 {
        eprintln!("ERROR: n must be greater than 0");
        return f64::NAN;
    }

    if epsilon <= 0.0 || !epsilon.is_finite() {
        eprintln!("ERROR: epsilon must be positive and finite");
        return f64::NAN;
    }

    if max_iterations == 0 {
        eprintln!("ERROR: max_iterations must be greater than 0");
        return f64::NAN;
    }

    unsafe {
        let mu_slice = std::slice::from_raw_parts(mu, n);
        let nu_slice = std::slice::from_raw_parts(nu, n);
        let cost_slice = std::slice::from_raw_parts(cost_matrix, n * n);

        // Validate that all values are finite
        if !mu_slice.iter().all(|x| x.is_finite()) {
            eprintln!("ERROR: mu contains non-finite values");
            return f64::NAN;
        }

        if !nu_slice.iter().all(|x| x.is_finite()) {
            eprintln!("ERROR: nu contains non-finite values");
            return f64::NAN;
        }

        if !cost_slice.iter().all(|x| x.is_finite()) {
            eprintln!("ERROR: cost_matrix contains non-finite values");
            return f64::NAN;
        }

        wasserstein1_distance(mu_slice, nu_slice, cost_slice, n, epsilon, max_iterations)
    }
}

/// Free memory allocated by Rust (if any)
#[no_mangle]
pub extern "C" fn free_rust_memory(ptr: *mut std::ffi::c_void) {
    unsafe {
        if !ptr.is_null() {
            // Drop the allocation
            let _ = Box::from_raw(ptr);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_wasserstein1_simple() {
        let mu = vec![0.5, 0.5];
        let nu = vec![0.5, 0.5];
        let cost = vec![0.0, 1.0, 1.0, 0.0]; // 2x2 cost matrix
        
        let result = wasserstein1_distance(&mu, &nu, &cost, 2, 0.01, 100);
        assert!((result - 0.0).abs() < 1e-6);
    }
    
    #[test]
    fn test_ffi_wasserstein1() {
        let mu = vec![0.5, 0.5];
        let nu = vec![0.5, 0.5];
        let cost = vec![0.0, 1.0, 1.0, 0.0];

        let result = unsafe {
            compute_wasserstein1(
                mu.as_ptr(),
                nu.as_ptr(),
                cost.as_ptr(),
                2,
                0.01,
                100,
            )
        };

        assert!((result - 0.0).abs() < 1e-4);
    }

    #[test]
    fn test_ffi_null_pointer_validation() {
        let mu = vec![0.5, 0.5];
        let nu = vec![0.5, 0.5];

        let result = unsafe {
            compute_wasserstein1(
                std::ptr::null(),
                nu.as_ptr(),
                std::ptr::null(),
                2,
                0.01,
                100,
            )
        };

        assert!(result.is_nan());
    }

    #[test]
    fn test_ffi_invalid_parameters() {
        let mu = vec![0.5, 0.5];
        let nu = vec![0.5, 0.5];
        let cost = vec![0.0, 1.0, 1.0, 0.0];

        // Test n = 0
        let result = unsafe {
            compute_wasserstein1(
                mu.as_ptr(),
                nu.as_ptr(),
                cost.as_ptr(),
                0,
                0.01,
                100,
            )
        };
        assert!(result.is_nan());

        // Test epsilon <= 0
        let result = unsafe {
            compute_wasserstein1(
                mu.as_ptr(),
                nu.as_ptr(),
                cost.as_ptr(),
                2,
                0.0,
                100,
            )
        };
        assert!(result.is_nan());

        // Test max_iterations = 0
        let result = unsafe {
            compute_wasserstein1(
                mu.as_ptr(),
                nu.as_ptr(),
                cost.as_ptr(),
                2,
                0.01,
                0,
            )
        };
        assert!(result.is_nan());
    }
}
