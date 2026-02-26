"""
HEHL FORMULA ASSIGNMENT COST SIMULATION

Simulates local neighborhoods on k-regular graphs using Hehl's explicit formula:
    κ_α(u,v) = 1 - (α/k)(k + 1 - W*)

where W* = inf_φ Σ d(z, φ(z)) is the optimal assignment cost between exclusive 
neighborhoods R_u = N(u) \\ (triangles ∪ {v}) and R_v = N(v) \\ (triangles ∪ {u}).

For the local limit (Galton-Watson tree + Poisson(η) excess edges):
    - t ~ Poisson(η) common neighbors (triangles)
    - |R_u| = |R_v| = k - 1 - t (exclusive neighborhood sizes)
    - Random bipartite graph between R_u and R_v with edge prob ~ η/k
    - Distance d = 1 if edge exists, d = 2 otherwise (tree-like)

Usage:
    julia hehl_assignment_simulation.jl
"""

using LinearAlgebra
using Statistics
using Random
using JSON
using Printf
using Hungarian  # For optimal assignment
using Distributions  # For Poisson sampling

# Install dependencies if needed
import Pkg
let deps = Pkg.project().dependencies
    if !haskey(deps, "Hungarian")
        Pkg.add("Hungarian")
    end
    if !haskey(deps, "Distributions")
        Pkg.add("Distributions")
    end
end

# ─────────────────────────────────────────────────────────────────
# Core: Optimal Assignment on Exclusive Neighborhoods
# ─────────────────────────────────────────────────────────────────

"""
    compute_assignment_cost(k::Int, t::Int, eta::Float64; n_samples::Int=1000)

Compute expected optimal assignment cost W* for given:
    - k: degree (regular)
    - t: number of common neighbors (triangles)  
    - eta: density parameter ⟨k⟩²/N
    
Returns mean and std of W* over n_samples random bipartite graphs.
"""
function compute_assignment_cost(k::Int, t::Int, eta::Float64; 
                                  n_samples::Int=1000, rng::AbstractRNG=Random.GLOBAL_RNG)
    @assert t <= k - 1 "t=$t cannot exceed k-1=$k"
    
    size_r = k - 1 - t  # Size of exclusive neighborhoods
    
    if size_r <= 0
        # No exclusive vertices to match
        return 0.0, 0.0
    end
    
    # Edge probability in bipartite graph (from local limit)
    # In GW tree with Poisson(η) excess, edges form with prob related to η/k
    p_edge = min(eta / k, 1.0)
    
    costs = Float64[]
    
    for _ in 1:n_samples
        # Build random bipartite adjacency between R_u and R_v
        # Cost matrix: d = 1 if edge, d = 2 otherwise (tree-like distances)
        cost_matrix = fill(2.0, size_r, size_r)
        
        for i in 1:size_r, j in 1:size_r
            if rand(rng) < p_edge
                cost_matrix[i, j] = 1.0  # Direct edge
            end
        end
        
        # Solve optimal assignment using Hungarian algorithm
        # Hungarian.jl solves: min Σ C[i, assignment[i]]
        assignment, cost = Hungarian.hungarian(cost_matrix)
        
        push!(costs, cost)
    end
    
    return mean(costs), std(costs)
end

"""
    sample_triangles(k::Int, eta::Float64) -> Int

Sample number of common neighbors t ~ Poisson(η), truncated to [0, k-1].
"""
function sample_triangles(k::Int, eta::Float64; rng::AbstractRNG=Random.GLOBAL_RNG)
    t = rand(rng, Poisson(eta))
    return min(max(t, 0), k - 1)  # Truncate to valid range
end

"""
    hehl_curvature(k::Int, eta::Float64, alpha::Float64; 
                   n_trials::Int=1000, n_assignment_samples::Int=100)

Compute expected ORC via Hehl formula:
    E[κ] ≈ 1 - (α/k)(k + 1 - E[W*])
    
where E[W*] is averaged over:
    1. t ~ Poisson(η) triangle sampling
    2. Random bipartite graph on exclusive neighborhoods
    3. Optimal assignment cost
"""
function hehl_curvature(k::Int, eta::Float64, alpha::Float64;
                        n_trials::Int=1000, n_assignment_samples::Int=100,
                        rng::AbstractRNG=Random.GLOBAL_RNG)
    
    curvatures = Float64[]
    
    for _ in 1:n_trials
        # Sample triangles
        t = sample_triangles(k, eta; rng=rng)
        
        # Compute expected assignment cost for this t
        W_star_mean, _ = compute_assignment_cost(k, t, eta; 
                                                  n_samples=n_assignment_samples,
                                                  rng=rng)
        
        # Hehl formula: κ = 1 - (α/k)(k + 1 - W*)
        kappa = 1.0 - (alpha / k) * (k + 1 - W_star_mean)
        
        push!(curvatures, kappa)
    end
    
    return mean(curvatures), std(curvatures)
end

# ─────────────────────────────────────────────────────────────────
# Self-Consistent Equation Derivation
# ─────────────────────────────────────────────────────────────────

"""
    fit_critical_eta(k_values::Vector{Int}, eta_range::AbstractRange, 
                     alpha::Float64=0.5; n_trials::Int=500)

For each k, find η_c(k) where Hehl-predicted κ crosses zero.
Returns fitted η_c values and suggests η_c^∞ limit.
"""
function fit_critical_eta(k_values::Vector{Int}, eta_range::AbstractRange,
                          alpha::Float64=0.5; n_trials::Int=500)
    
    results = Dict[]
    
    for k in k_values
        @info "Computing for k=$k..."
        
        eta_critical = nothing
        kappa_prev = nothing
        
        for eta in eta_range
            kappa_mean, kappa_std = hehl_curvature(k, eta, alpha; 
                                                   n_trials=n_trials,
                                                   n_assignment_samples=50)
            
            # Check for sign change
            if kappa_prev !== nothing && kappa_prev < 0 && kappa_mean > 0
                # Linear interpolation for finer estimate
                eta_critical = eta_prev + (eta - eta_prev) * (-kappa_prev) / (kappa_mean - kappa_prev)
                @info "  Sign change at η≈$(round(eta_critical, digits=3))"
                break
            end
            
            kappa_prev = kappa_mean
            eta_prev = eta
        end
        
        if eta_critical !== nothing
            push!(results, Dict(
                "k" => k,
                "eta_critical" => eta_critical,
                "alpha" => alpha
            ))
        end
    end
    
    return results
end

# ─────────────────────────────────────────────────────────────────
# Compare to N=1000 data
# ─────────────────────────────────────────────────────────────────

"""
    load_n1000_data() -> Vector{Dict}
    
Load the empirical N=1000 phase transition data.
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
    compare_to_empirical(alpha::Float64=0.5; n_trials::Int=500)

Compare Hehl-predicted curvature to empirical N=1000 data.
"""
function compare_to_empirical(alpha::Float64=0.5; n_trials::Int=500)
    emp_data = load_n1000_data()
    
    if emp_data === nothing
        @error "Cannot load empirical data"
        return nothing
    end
    
    comparisons = Dict[]
    
    for emp_point in emp_data
        k = emp_point["k_target"]
        eta_emp = emp_point["ratio"]
        kappa_emp = emp_point["kappa_mean"]
        
        # Hehl prediction
        kappa_hehl, kappa_std = hehl_curvature(k, eta_emp, alpha;
                                               n_trials=n_trials,
                                               n_assignment_samples=50)
        
        push!(comparisons, Dict(
            "k" => k,
            "eta" => eta_emp,
            "kappa_empirical" => kappa_emp,
            "kappa_hehl" => kappa_hehl,
            "kappa_hehl_std" => kappa_std,
            "error" => abs(kappa_emp - kappa_hehl)
        ))
        
        @printf("k=%2d η=%.3f: κ_emp=%+.4f  κ_hehl=%+.4f±%.4f  err=%.4f\n",
                k, eta_emp, kappa_emp, kappa_hehl, kappa_std, abs(kappa_emp - kappa_hehl))
    end
    
    return comparisons
end

# ─────────────────────────────────────────────────────────────────
# Extract Self-Consistent Equation Numerically
# ─────────────────────────────────────────────────────────────────

"""
    extract_mean_field_equation(k::Int, eta_range::AbstractRange;
                                 alpha::Float64=0.5, n_trials::Int=1000)
    
For fixed k, compute E[κ(η)] curve and fit functional form.
The goal is to find η_c such that E[κ(η_c)] = 0.
"""
function extract_mean_field_equation(k::Int, eta_range::AbstractRange;
                                      alpha::Float64=0.5, n_trials::Int=1000)
    
    curve_points = Dict[]
    
    for eta in eta_range
        kappa_mean, kappa_std = hehl_curvature(k, eta, alpha; 
                                               n_trials=n_trials,
                                               n_assignment_samples=100)
        
        push!(curve_points, Dict(
            "eta" => eta,
            "kappa_mean" => kappa_mean,
            "kappa_std" => kappa_std,
            "k" => k,
            "alpha" => alpha
        ))
        
        @printf("k=%d, η=%.3f: E[κ] = %+.4f ± %.4f\n", k, eta, kappa_mean, kappa_std)
    end
    
    return curve_points
end

# ─────────────────────────────────────────────────────────────────
# Main Entry Points
# ─────────────────────────────────────────────────────────────────

function run_full_analysis()
    @info "="^70
    @info "HEHL FORMULA ASSIGNMENT COST SIMULATION"
    @info "="^70
    
    alpha = 0.5
    
    # Part 1: Compare to N=1000 empirical data
    @info "\n" * "─"^70
    @info "PART 1: Comparing Hehl predictions to N=1000 empirical data"
    @info "─"^70
    
    comparisons = compare_to_empirical(alpha; n_trials=500)
    
    if comparisons !== nothing
        mse = mean([c["error"]^2 for c in comparisons])
        mae = mean([c["error"] for c in comparisons])
        @info "\nFit quality: MSE=$(round(mse, digits=6)), MAE=$(round(mae, digits=6))"
    end
    
    # Part 2: Extract E[κ(η)] curves for different k
    @info "\n" * "─"^70
    @info "PART 2: Extracting E[κ(η)] curves (mean-field equation)"
    @info "─"^70
    
    eta_range = 0.5:0.25:8.0
    k_values = [10, 20, 30, 50]
    
    all_curves = Dict()
    
    for k in k_values
        @info "\nComputing curve for k=$k..."
        curve = extract_mean_field_equation(k, eta_range; alpha=alpha, n_trials=500)
        all_curves["k=$k"] = curve
        
        # Find sign change (critical eta)
        for i in 2:length(curve)
            if curve[i-1]["kappa_mean"] < 0 && curve[i]["kappa_mean"] > 0
                eta_c = curve[i-1]["eta"] + 
                        (curve[i]["eta"] - curve[i-1]["eta"]) * 
                        (-curve[i-1]["kappa_mean"]) / 
                        (curve[i]["kappa_mean"] - curve[i-1]["kappa_mean"])
                @info "  Critical η_c ≈ $(round(eta_c, digits=3)) for k=$k"
                break
            end
        end
    end
    
    # Part 3: Large-k limit (approaching η_c^∞)
    @info "\n" * "─"^70
    @info "PART 3: Large-k limit analysis (extracting η_c^∞)"
    @info "─"^70
    
    large_k_values = [20, 30, 40, 50, 60]
    eta_fine = 2.0:0.1:5.0
    
    critical_etas = Float64[]
    
    for k in large_k_values
        @info "Analyzing k=$k for critical point..."
        curve = extract_mean_field_equation(k, eta_fine; alpha=alpha, n_trials=300)
        
        # Find sign change
        for i in 2:length(curve)
            if curve[i-1]["kappa_mean"] < 0 && curve[i]["kappa_mean"] > 0
                eta_c = curve[i-1]["eta"] + 
                        (curve[i]["eta"] - curve[i-1]["eta"]) * 
                        (-curve[i-1]["kappa_mean"]) / 
                        (curve[i]["kappa_mean"] - curve[i-1]["kappa_mean"])
                push!(critical_etas, eta_c)
                @info "  η_c(k=$k) ≈ $(round(eta_c, digits=3))"
                break
            end
        end
    end
    
    if length(critical_etas) >= 2
        # Extrapolate to k→∞
        # Assume η_c(k) = η_c^∞ - a/k + o(1/k)
        # Use last two points for estimate
        eta_inf_estimate = 2 * critical_etas[end] - critical_etas[end-1]
        @info "\n" * "="^70
        @info "ESTIMATED η_c^∞ ≈ $(round(eta_inf_estimate, digits=3))"
        @info "="^70
    end
    
    # Save all results
    output = Dict(
        "alpha" => alpha,
        "comparisons_to_n1000" => comparisons,
        "mean_field_curves" => all_curves,
        "critical_etas" => Dict(zip(string.(large_k_values), critical_etas)),
        "eta_c_infinity_estimate" => length(critical_etas) >= 2 ? 
            2 * critical_etas[end] - critical_etas[end-1] : nothing,
        "method" => "hehl_assignment_simulation",
        "description" => "Mean-field prediction using Hehl formula + optimal assignment"
    )
    
    output_path = joinpath(@__DIR__, "..", "..", "results", "experiments",
                           "hehl_meanfield_analysis.json")
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
    run_full_analysis()
end
