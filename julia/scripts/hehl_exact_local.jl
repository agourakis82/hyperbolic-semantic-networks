"""
HEHL EXACT LOCAL COMPUTATION

Computes exact Wasserstein distance on the LOCAL NEIGHBORHOOD structure
derived from Hehl's formula (arXiv:2407.08854v3, Theorem 4.2).

For an edge (u,v) in a k-regular graph with t common neighbors (triangles):

Local node structure:
- Node 0: u (source)
- Node 1: v (target)
- Nodes 2:(t+1): triangle nodes (common neighbors, t of them)
- Nodes (t+2):(t+2+n_exc-1): exclusive N(u) nodes (n_exc = k-1-t)
- Nodes (t+2+n_exc):(t+2+2*n_exc-1): exclusive N(v) nodes (n_exc = k-1-t)

Probability measures:
- μ_u: mass α at u, mass (1-α)/k at each neighbor (t triangles + n_exc exclusive)
- μ_v: mass α at v, mass (1-α)/k at each neighbor (t triangles + n_exc exclusive)

Distance structure:
- d(u,v) = 1
- d(u, triangle) = 1, d(v, triangle) = 1
- d(triangle_i, triangle_j) = 2 (via u or v)
- d(u, exc_u) = 1, d(v, exc_v) = 1
- d(u, exc_v) = 2 (via v), d(v, exc_u) = 2 (via u)
- d(exc_u, triangle) = 2 (via u)
- d(exc_v, triangle) = 2 (via v)
- d(exc_u, exc_v) = 3 (exc_u → u → v → exc_v) OR 1 if direct edge exists!

The key is the random bipartite graph between exc_u and exc_v.
"""

using LinearAlgebra
using Statistics
using Random
using JSON
using Printf
using Distributions
using JuMP
using HiGHS

"""
    build_local_distance_matrix(t::Int, n_exc::Int, edges_exc::Set{Tuple{Int,Int}})

Build distance matrix for local neighborhood.

Node indexing:
- 1: u
- 2: v
- 3:(t+2): triangle nodes
- (t+3):(t+2+n_exc): exclusive N(u)
- (t+3+n_exc):(t+2+2*n_exc): exclusive N(v)
"""
function build_local_distance_matrix(t::Int, n_exc::Int, 
                                      edges_exc::Set{Tuple{Int,Int}})
    n_nodes = 2 + t + 2*n_exc
    D = fill(10.0, n_nodes, n_nodes)  # Default large distance
    
    # Self distances
    for i in 1:n_nodes
        D[i,i] = 0.0
    end
    
    # u (1) - v (2)
    D[1,2] = 1.0
    D[2,1] = 1.0
    
    # Triangle nodes (indices 3:(t+2))
    for i in 3:(2+t)
        # u - triangle
        D[1,i] = 1.0
        D[i,1] = 1.0
        
        # v - triangle
        D[2,i] = 1.0
        D[i,2] = 1.0
        
        # Triangle - triangle
        for j in 3:(2+t)
            if i != j
                D[i,j] = 2.0  # Via u or v
            end
        end
    end
    
    # Exclusive N(u) nodes (indices (t+3):(t+2+n_exc))
    exc_u_start = t + 3
    exc_u_end = t + 2 + n_exc
    
    # Exclusive N(v) nodes
    exc_v_start = t + 3 + n_exc
    exc_v_end = t + 2 + 2*n_exc
    
    for i in exc_u_start:exc_u_end
        idx_u = i - exc_u_start + 1  # 1-indexed within exclusive u
        
        # u - exc_u
        D[1,i] = 1.0
        D[i,1] = 1.0
        
        # v - exc_u (via u)
        D[2,i] = 2.0
        D[i,2] = 2.0
        
        # exc_u - triangle
        for j in 3:(2+t)
            D[i,j] = 2.0  # exc_u → u → triangle
            D[j,i] = 2.0
        end
        
        # exc_u - exc_v
        for j in exc_v_start:exc_v_end
            idx_v = j - exc_v_start + 1
            if (idx_u, idx_v) in edges_exc
                D[i,j] = 1.0  # Direct edge!
                D[j,i] = 1.0
            else
                D[i,j] = 3.0  # exc_u → u → v → exc_v
                D[j,i] = 3.0
            end
        end
    end
    
    for i in exc_v_start:exc_v_end
        # v - exc_v
        D[2,i] = 1.0
        D[i,2] = 1.0
        
        # u - exc_v (via v)
        D[1,i] = 2.0
        D[i,1] = 2.0
        
        # exc_v - triangle
        for j in 3:(2+t)
            D[i,j] = 2.0  # exc_v → v → triangle
            D[j,i] = 2.0
        end
    end
    
    return D
end

"""
    build_local_measures(t::Int, n_exc::Int, alpha::Float64, k::Int)

Build probability measures μ_u and μ_v for local neighborhood.
"""
function build_local_measures(t::Int, n_exc::Int, alpha::Float64, k::Int)
    n_nodes = 2 + t + 2*n_exc
    
    mu_u = zeros(n_nodes)
    mu_v = zeros(n_nodes)
    
    # μ_u: mass α at u
    mu_u[1] = alpha
    
    # μ_u: mass (1-α)/k at each neighbor (t triangles + n_exc exclusive)
    mass_per_neighbor = (1 - alpha) / k
    
    # Triangle nodes get mass
    for i in 3:(2+t)
        mu_u[i] = mass_per_neighbor
    end
    
    # Exclusive N(u) nodes get mass
    exc_u_start = t + 3
    exc_u_end = t + 2 + n_exc
    for i in exc_u_start:exc_u_end
        mu_u[i] = mass_per_neighbor
    end
    
    # μ_v: mass α at v
    mu_v[2] = alpha
    
    # μ_v: mass at neighbors
    for i in 3:(2+t)
        mu_v[i] = mass_per_neighbor
    end
    
    exc_v_start = t + 3 + n_exc
    exc_v_end = t + 2 + 2*n_exc
    for i in exc_v_start:exc_v_end
        mu_v[i] = mass_per_neighbor
    end
    
    return mu_u, mu_v
end

"""
    solve_wasserstein_exact(mu, nu, D) -> Float64

Solve Wasserstein-1 exactly via LP.
"""
function solve_wasserstein_exact(mu::Vector{Float64}, nu::Vector{Float64}, 
                                  D::Matrix{Float64})::Float64
    n = length(mu)
    
    model = Model(HiGHS.Optimizer)
    set_silent(model)
    
    @variable(model, gamma[1:n, 1:n] >= 0)
    
    @constraint(model, source[i=1:n], sum(gamma[i,j] for j in 1:n) == mu[i])
    @constraint(model, target[j=1:n], sum(gamma[i,j] for i in 1:n) == nu[j])
    
    @objective(model, Min, sum(D[i,j] * gamma[i,j] for i in 1:n, j in 1:n))
    
    optimize!(model)
    
    if termination_status(model) != OPTIMAL && termination_status(model) != LOCALLY_SOLVED
        @warn "LP not optimal: $(termination_status(model))"
        return NaN
    end
    
    return objective_value(model)
end

"""
    sample_random_edges(n_exc::Int, p_edge::Float64) -> Set{Tuple{Int,Int}}

Sample random bipartite edges between exclusive neighborhoods.
"""
function sample_random_edges(n_exc::Int, p_edge::Float64; 
                              rng::AbstractRNG=Random.GLOBAL_RNG)
    edges = Set{Tuple{Int,Int}}()
    
    for i in 1:n_exc, j in 1:n_exc
        if rand(rng) < p_edge
            push!(edges, (i, j))
        end
    end
    
    return edges
end

"""
    compute_exact_local_curvature(k::Int, t::Int, alpha::Float64, p_edge::Float64;
                                   n_samples::Int=100)

Compute expected ORC for local neighborhood with exact Wasserstein LPs.
"""
function compute_exact_local_curvature(k::Int, t::Int, alpha::Float64, p_edge::Float64;
                                        n_samples::Int=100,
                                        rng::AbstractRNG=Random.GLOBAL_RNG)
    n_exc = max(0, k - 1 - t)
    
    W1_samples = Float64[]
    
    for _ in 1:n_samples
        # Sample random edges between exclusive neighborhoods
        edges_exc = sample_random_edges(n_exc, p_edge; rng=rng)
        
        # Build distance matrix
        D = build_local_distance_matrix(t, n_exc, edges_exc)
        
        # Build measures
        mu_u, mu_v = build_local_measures(t, n_exc, alpha, k)
        
        # Solve Wasserstein
        W1 = solve_wasserstein_exact(mu_u, mu_v, D)
        
        if !isnan(W1)
            push!(W1_samples, W1)
        end
    end
    
    if length(W1_samples) == 0
        return NaN, NaN
    end
    
    # Curvature: κ = 1 - W1 (since d(u,v) = 1)
    kappa_mean = 1.0 - mean(W1_samples)
    kappa_std = std(W1_samples)
    
    return kappa_mean, kappa_std
end

"""
    ensemble_curvature(k::Int, eta::Float64, alpha::Float64=0.5;
                       n_trials::Int=1000, n_wasserstein_samples::Int=50)

Compute ensemble-averaged curvature by sampling t ~ Poisson(eta).
"""
function ensemble_curvature(k::Int, eta::Float64, alpha::Float64=0.5;
                             n_trials::Int=1000, 
                             n_wasserstein_samples::Int=50,
                             rng::AbstractRNG=Random.GLOBAL_RNG)
    curvatures = Float64[]
    
    p_edge = min(eta / k, 1.0)
    
    for trial in 1:n_trials
        # Sample triangles
        t = rand(rng, Poisson(eta))
        t = min(max(t, 0), k - 1)
        
        # Compute curvature for this local structure
        kappa, _ = compute_exact_local_curvature(k, t, alpha, p_edge;
                                                  n_samples=n_wasserstein_samples,
                                                  rng=rng)
        
        if !isnan(kappa)
            push!(curvatures, kappa)
        end
        
        if trial % 100 == 0
            @info "  Progress: $trial/$n_trials"
        end
    end
    
    return mean(curvatures), std(curvatures)
end

"""
    load_n1000_data()
"""
function load_n1000_data()
    data_path = joinpath(@__DIR__, "..", "..", "results", "experiments", 
                         "phase_transition_exact_n1000.json")
    
    if !isfile(data_path)
        @warn "N=1000 data not found at $data_path"
        return nothing
    end
    
    data = JSON.parsefile(data_path)
    return data["results"]
end

"""
    run_exact_comparison()
"""
function run_exact_comparison()
    @info "="^70
    @info "HEHL EXACT LOCAL COMPUTATION (LP-based)"
    @info "="^70
    
    emp_data = load_n1000_data()
    
    if emp_data === nothing
        @error "Cannot load empirical data"
        return nothing
    end
    
    alpha = 0.5
    comparisons = Dict[]
    
    @info "\nComputing exact local curvatures (this will take time)..."
    @printf("%-4s %6s %10s %10s %10s %10s\n", 
            "k", "η", "κ_emp", "κ_exact", "std", "error")
    
    for emp_point in emp_data
        k = emp_point["k_target"]
        eta = emp_point["ratio"]
        kappa_emp = emp_point["kappa_mean"]
        
        @info "\nComputing for k=$k, η=$eta..."
        
        # Exact computation (fewer trials for speed)
        kappa_exact, kappa_std = ensemble_curvature(k, eta, alpha;
                                                     n_trials=200,
                                                     n_wasserstein_samples=20)
        
        push!(comparisons, Dict(
            "k" => k,
            "eta" => eta,
            "kappa_empirical" => kappa_emp,
            "kappa_exact" => kappa_exact,
            "kappa_std" => kappa_std,
            "error" => abs(kappa_emp - kappa_exact)
        ))
        
        @printf("%4d %6.3f %+.6f %+.6f %10.6f %10.6f\n",
                k, eta, kappa_emp, kappa_exact, kappa_std, abs(kappa_emp - kappa_exact))
    end
    
    # Summary
    mse = mean([c["error"]^2 for c in comparisons])
    mae = mean([c["error"] for c in comparisons])
    
    @info "\n" * "="^70
    @info "SUMMARY"
    @info "="^70
    @info "MSE: $(round(mse, digits=6))"
    @info "MAE: $(round(mae, digits=6))"
    
    # Save results
    output = Dict(
        "alpha" => alpha,
        "comparisons" => comparisons,
        "mse" => mse,
        "mae" => mae,
        "method" => "hehl_exact_local_wasserstein",
        "notes" => "Full LP on local neighborhood structure per Hehl Thm 4.2"
    )
    
    output_path = joinpath(@__DIR__, "..", "..", "results", "experiments",
                           "hehl_exact_local.json")
    mkpath(dirname(output_path))
    
    open(output_path, "w") do f
        JSON.print(f, output, 2)
    end
    
    @info "\nResults saved to: $output_path"
    
    return output
end

if abspath(PROGRAM_FILE) == @__FILE__
    run_exact_comparison()
end
