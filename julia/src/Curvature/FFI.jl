"""
FFI.jl - Foreign Function Interface to Rust backend

Provides Julia bindings to Rust curvature computation library.
"""

module FFI

using Libdl
using LinearAlgebra

# Load Rust library
const LIB_CURVATURE = Ref{String}()

function init_rust_library()
    """Initialize Rust library path."""
    # Try to find the compiled library
    lib_paths = [
        joinpath(@__DIR__, "..", "..", "..", "rust", "target", "release", "libhyperbolic_curvature.so"),
        joinpath(@__DIR__, "..", "..", "..", "rust", "target", "release", "libhyperbolic_curvature.dylib"),
        joinpath(@__DIR__, "..", "..", "..", "rust", "target", "release", "hyperbolic_curvature.dll"),
    ]
    
    for path in lib_paths
        if isfile(path)
            LIB_CURVATURE[] = path
            return true
        end
    end
    
    @warn "Rust library not found. Using simplified implementation."
    return false
end

"""
Call Rust Wasserstein-1 distance computation.

# Arguments
- `mu`: First probability measure (Vector{Float64})
- `nu`: Second probability measure (Vector{Float64})
- `cost_matrix`: Cost matrix (flattened, row-major, Vector{Float64})
- `epsilon`: Entropy regularization parameter
- `max_iterations`: Maximum Sinkhorn iterations

# Returns
- Wasserstein-1 distance value
"""
function wasserstein1_rust(
    mu::Vector{Float64},
    nu::Vector{Float64},
    cost_matrix::Vector{Float64},
    epsilon::Float64 = 0.01,
    max_iterations::Int = 100
)::Float64
    # Initialize library if not already done
    if isempty(LIB_CURVATURE) || (LIB_CURVATURE[] != "" && !isfile(LIB_CURVATURE[]))
        init_rust_library()
    end
    
    if isempty(LIB_CURVATURE) || !isfile(LIB_CURVATURE[])
        # Fallback to Julia implementation
        return wasserstein1_julia(mu, nu, cost_matrix, epsilon, max_iterations)
    end
    
    n = length(mu)
    @assert length(nu) == n "mu and nu must have same length"
    @assert length(cost_matrix) == n * n "cost_matrix must be n×n"
    
    # Call Rust function
    ccall(
        (:compute_wasserstein1, LIB_CURVATURE[]),
        Float64,
        (Ptr{Float64}, Ptr{Float64}, Ptr{Float64}, Csize_t, Float64, Csize_t),
        mu, nu, cost_matrix, n, epsilon, max_iterations
    )
end

"""
Julia fallback implementation of Wasserstein-1.
"""
function wasserstein1_julia(
    mu::Vector{Float64},
    nu::Vector{Float64},
    cost_matrix::Vector{Float64},
    epsilon::Float64,
    max_iterations::Int
)::Float64
    n = length(mu)
    C = reshape(cost_matrix, n, n)
    mu_norm = mu / sum(mu)
    nu_norm = nu / sum(nu)

    K = exp.(-C / epsilon)
    u = ones(n)
    v = ones(n)
    tol = 1e-6

    for iter in 1:max_iterations
        u_old = copy(u)
        u = mu_norm ./ (K * v)
        v = nu_norm ./ (K' * u)
        if iter % 10 == 0 && norm(u - u_old, 1) < tol
            break
        end
    end

    P = Diagonal(u) * K * Diagonal(v)
    return sum(P .* C)
end

# Export functions
export wasserstein1_rust, init_rust_library

end # module FFI
