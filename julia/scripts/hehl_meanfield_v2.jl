"""
HEHL MEAN-FIELD SIMULATION v2 (Corrected)

Correct implementation of Hehl's formula for ORC on k-regular graphs.

Key insight: The probability measures μ_u and μ_v have:
- Mass α at u and v (idleness)
- Mass (1-α)/k at each neighbor

For nodes with t common neighbors (triangles), the transport is:
- Mass at u → v: cost 1
- Mass at triangle nodes: can stay (cost 0) or move to other triangle (cost 0)
- Mass at exclusive N(u) → exclusive N(v): assignment problem with d=1 or 2

Hehl formula (Theorem 4.2, Eq 17):
    κ_α(u,v) = 1 - (α/k) * (k + 1 - W*)
    
where W* is the optimal assignment cost on the EXCLUSIVE neighborhoods.
"""

using LinearAlgebra
using Statistics
using Random
using JSON
using Printf
using Distributions
using JuMP
using HiGHS

# ─────────────────────────────────────────────────────────────────
# Correct: Full Wasserstein on Local Neighborhood Structure
# ─────────────────────────────────────────────────────────────────

"""
    compute_local_wasserstein(k::Int, t::Int, alpha::Float64, 
                              p_edge::Float64; n_samples::Int=100)

Compute expected Wasserstein distance for local neighborhood with:
- k: degree (regular)
- t: number of triangles (common neighbors)
- alpha: idleness parameter
- p_edge: probability of edge between exclusive neighborhoods

The local structure consists of:
- Nodes: u, v, t triangle nodes, (k-1-t) exclusive N(u) nodes, (k-1-t) exclusive N(v) nodes
- Distances: tree-like with shortcuts
"""
function compute_local_wasserstein(k::Int, t::Int, alpha::Float64, 
                                   p_edge::Float64; n_samples::Int=100,
                                   rng::AbstractRNG=Random.GLOBAL_RNG)
    
    # Local neighborhood structure:
    # 0: u (source)
    # 1: v (target)  
    # 2:(t+1): triangle nodes (t of them)
    # (t+2):(t+2+k-2-t): exclusive N(u) nodes (k-1-t of them)
    # ... followed by exclusive N(v) nodes
    
    n_tri = t
    n_exc = k - 1 - t  # exclusive nodes per side
    
    if n_exc < 0
        n_exc = 0
    end
    
    # Build local distance matrix for ALL nodes in the support
    # Node indexing:
    # 1: u
    # 2: v
    # 3:(2+t): triangle nodes (shared)
    # (3+t):(2+t+n_exc): exclusive N(u)
    # (3+t+n_exc):(2+t+2*n_exc): exclusive N(v)
    
    n_local = 2 + t + 2*n_exc
    
    W1_samples = Float64[]
    
    for _ in 1:n_samples
        # Distance matrix
        D = fill(4.0, n_local, n_local)  # Default large distance
        
        # Self distances
        for i in 1:n_local
            D[i,i] = 0.0
        end
        
        # u-v distance
        D[1,2] = 1.0
        D[2,1] = 1.0
        
        # Triangle nodes (indices 3:(2+t))
        for i in 3:(2+t)
            # Distance from u to triangle node
            D[1,i] = 1.0
            D[i,1] = 1.0
            
            # Distance from v to triangle node
            D[2,i] = 1.0
            D[i,2] = 1.0
            
            # Distance between triangle nodes
            for j in 3:(2+t)
                if i != j
                    D[i,j] = 2.0  # Through u or v
                end
            end
        end
        
        # Exclusive N(u) nodes (indices (3+t):(2+t+n_exc))
        exc_u_start = 3 + t
        exc_u_end = 2 + t + n_exc
        
        # Exclusive N(v) nodes
        exc_v_start = 3 + t + n_exc
        exc_v_end = 2 + t + 2*n_exc
        
        for i in exc_u_start:exc_u_end
            # Distance from u to exclusive N(u)
            D[1,i] = 1.0
            D[i,1] = 1.0
            
            # Distance from v to exclusive N(u) (via u)
            D[2,i] = 2.0
            D[i,2] = 2.0
            
            # Distance to triangle nodes
            for j in 3:(2+t)
                D[i,j] = 2.0  # exc N(u) -> u -> triangle
                D[j,i] = 2.0
            end
        end
        
        for i in exc_v_start:exc_v_end
            # Distance from v to exclusive N(v)
            D[2,i] = 1.0
            D[i,2] = 1.0
            
            # Distance from u to exclusive N(v) (via v)
            D[1,i] = 2.0
            D[i,1] = 2.0
            
            # Distance to triangle nodes
            for j in 3:(2+t)
                D[i,j] = 2.0  # exc N(v) -> v -> triangle
                D[j,i] = 2.0
            end
        end
        
        # Random edges between exclusive neighborhoods
        for i in exc_u_start:exc_u_end
            for j in exc_v_start:exc_v_end
                if rand(rng) < p_edge
                    D[i,j] = 1.0  # Direct edge shortcut!
                    D[j,i] = 1.0
                else
                    D[i,j] = 3.0  # exc N(u) -> u -> v -> exc N(v)
                    D[j,i] = 3.0
                end
            end
        end
        
        # Build probability measures μ_u and μ_v
        mu_u = zeros(n_local)
        mu_v = zeros(n_local)
        
        # μ_u: mass α at u, mass (1-α)/k at each neighbor
        mu_u[1] = alpha  # u itself
        
        # Mass at triangle nodes (shared neighbors)
        for i in 3:(2+t)
            mu_u[i] = (1 - alpha) / k
        end
        
        # Mass at exclusive N(u) nodes
        for i in exc_u_start:exc_u_end
            mu_u[i] = (1 - alpha) / k
        end
        
        # μ_v: mass α at v, mass (1-α)/k at each neighbor
        mu_v[2] = alpha  # v itself
        
        # Mass at triangle nodes (shared neighbors)
        for i in 3:(2+t)
            mu_v[i] = (1 - alpha) / k
        end
        
        # Mass at exclusive N(v) nodes
        for i in exc_v_start:exc_v_end
            mu_v[i] = (1 - alpha) / k
        end
        
        # Solve Wasserstein-1 via LP
        W1 = solve_wasserstein_lp(mu_u, mu_v, D)
        push!(W1_samples, W1)
    end
    
    return mean(W1_samples), std(W1_samples)
end

"""
    solve_wasserstein_lp(mu, nu, C) -> Float64

Solve Wasserstein-1 optimal transport via linear programming.
"""
function solve_wasserstein_lp(mu::Vector{Float64}, nu::Vector{Float64}, 
                               C::Matrix{Float64})::Float64
    n = length(mu)
    @assert length(nu) == n
    @assert size(C) == (n, n)
    
    model = Model(HiGHS.Optimizer)
    set_silent(model)
    
    @variable(model, gamma[1:n, 1:n] >= 0)
    
    # Marginal constraints
    @constraint(model, source[i=1:n], sum(gamma[i, j] for j in 1:n) == mu[i])
    @constraint(model, target[j=1:n], sum(gamma[i, j] for i in 1:n) == nu[j])
    
    # Minimize transport cost
    @objective(model, Min, sum(C[i, j] * gamma[i, j] for i in 1:n, j in 1:n))
    
    optimize!(model)
    
    if termination_status(model) != OPTIMAL
        @warn "LP not optimal: $(termination_status(model))"
        return NaN
    end
    
    return objective_value(model)
end

"""
    hehl_curvature_v2(k::Int, eta::Float64, alpha::Float64=0.5;
                      n_trials::Int=500)

Compute expected ORC using corrected local Wasserstein computation.
"""
function hehl_curvature_v2(k::Int, eta::Float64, alpha::Float64=0.5;
                           n_trials::Int=500,
                           rng::AbstractRNG=Random.GLOBAL_RNG)
    
    curvatures = Float64[]
    
    # Poisson parameter for triangles
    lambda = eta  # E[#triangles] ≈ η in local limit
    
    for _ in 1:n_trials
        # Sample number of triangles
        t = rand(rng, Poisson(lambda))
        t = min(max(t, 0), k-1)  # Truncate to valid range
        
        # Edge probability between exclusive neighborhoods
        p_edge = min(eta / k, 1.0)
        
        # Compute Wasserstein for this local structure
        W1_mean, _ = compute_local_wasserstein(k, t, alpha, p_edge; 
                                               n_samples=10, rng=rng)
        
        # ORC: κ = 1 - W1 / d(u,v) = 1 - W1 (since d(u,v)=1)
        kappa = 1.0 - W1_mean
        
        push!(curvatures, kappa)
    end
    
    return mean(curvatures), std(curvatures)
end

# ─────────────────────────────────────────────────────────────────
# Compare to empirical N=1000 data
# ─────────────────────────────────────────────────────────────────

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

function run_comparison()
    @info "="^70
    @info "HEHL MEAN-FIELD v2 (Corrected Local Wasserstein)"
    @info "="^70
    
    emp_data = load_n1000_data()
    
    if emp_data === nothing
        @error "Cannot load empirical data"
        return nothing
    end
    
    alpha = 0.5
    comparisons = Dict[]
    
    @info "\nComparing Hehl v2 predictions to N=1000 empirical data..."
    @printf("%-4s %6s %10s %10s %10s %10s\n", 
            "k", "η", "κ_emp", "κ_hehl", "std", "error")
    
    for emp_point in emp_data
        k = emp_point["k_target"]
        eta = emp_point["ratio"]
        kappa_emp = emp_point["kappa_mean"]
        
        # Hehl v2 prediction
        kappa_hehl, kappa_std = hehl_curvature_v2(k, eta, alpha; n_trials=200)
        
        push!(comparisons, Dict(
            "k" => k,
            "eta" => eta,
            "kappa_empirical" => kappa_emp,
            "kappa_hehl" => kappa_hehl,
            "kappa_hehl_std" => kappa_std,
            "error" => abs(kappa_emp - kappa_hehl)
        ))
        
        @printf("%4d %6.3f %+.6f %+.6f %10.6f %10.6f\n",
                k, eta, kappa_emp, kappa_hehl, kappa_std, abs(kappa_emp - kappa_hehl))
    end
    
    # Summary statistics
    mse = mean([c["error"]^2 for c in comparisons])
    mae = mean([c["error"] for c in comparisons])
    
    # Find where empirical and predicted cross zero
    emp_cross = nothing
    hehl_cross = nothing
    
    for i in 2:length(comparisons)
        # Empirical sign change
        if comparisons[i-1]["kappa_empirical"] < 0 && comparisons[i]["kappa_empirical"] > 0
            eta_prev = comparisons[i-1]["eta"]
            eta_curr = comparisons[i]["eta"]
            kappa_prev = comparisons[i-1]["kappa_empirical"]
            kappa_curr = comparisons[i]["kappa_empirical"]
            emp_cross = eta_prev + (eta_curr - eta_prev) * (-kappa_prev) / (kappa_curr - kappa_prev)
        end
        
        # Hehl sign change
        if comparisons[i-1]["kappa_hehl"] < 0 && comparisons[i]["kappa_hehl"] > 0
            eta_prev = comparisons[i-1]["eta"]
            eta_curr = comparisons[i]["eta"]
            kappa_prev = comparisons[i-1]["kappa_hehl"]
            kappa_curr = comparisons[i]["kappa_hehl"]
            hehl_cross = eta_prev + (eta_curr - eta_prev) * (-kappa_prev) / (kappa_curr - kappa_prev)
        end
    end
    
    @info "\n" * "="^70
    @info "SUMMARY"
    @info "="^70
    @info "MSE: $(round(mse, digits=6))"
    @info "MAE: $(round(mae, digits=6))"
    
    if emp_cross !== nothing
        @info "Empirical η_c ≈ $(round(emp_cross, digits=3))"
    end
    
    if hehl_cross !== nothing
        @info "Hehl η_c ≈ $(round(hehl_cross, digits=3))"
    end
    
    # Save results
    output = Dict(
        "alpha" => alpha,
        "comparisons" => comparisons,
        "mse" => mse,
        "mae" => mae,
        "eta_c_empirical" => emp_cross,
        "eta_c_hehl" => hehl_cross,
        "method" => "hehl_v2_local_wasserstein"
    )
    
    output_path = joinpath(@__DIR__, "..", "..", "results", "experiments",
                           "hehl_v2_comparison.json")
    mkpath(dirname(output_path))
    
    open(output_path, "w") do f
        JSON.print(f, output, 2)
    end
    
    @info "\nResults saved to: $output_path"
    
    return output
end

# ─────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────

if abspath(PROGRAM_FILE) == @__FILE__
    run_comparison()
end
