"""
HEHL FAST APPROXIMATION

Simplified analytical approximation of Hehl's formula for mean-field analysis.

Key approximation: Instead of solving full Wasserstein LPs, we use the 
expected transport cost structure:

For local neighborhood with t triangles and (k-1-t) exclusive nodes per side:

Wasserstein cost W₁ ≈ α·1 + (1-α)·[(t/k)·0 + ((k-1-t)/k)·E[d_exc]]

where:
- α·1: mass at u → v (cost 1)
- (t/k)·0: triangle mass can match at cost 0
- ((k-1-t)/k)·E[d_exc]: exclusive nodes match at expected distance

Expected distance for exclusive nodes:
E[d_exc] = 3 - p_match·(2 - 1) = 3 - p_match

where p_match = probability that a random pair (z_u, z_v) has direct edge.

In local limit: p_match ≈ η/k (density parameter / degree)

So: E[d_exc] ≈ 3 - η/k

This gives:
W₁ ≈ α + (1-α)·((k-1-t)/k)·(3 - η/k)

and curvature:
κ ≈ 1 - W₁
"""

using Statistics
using Random
using JSON
using Printf
using Distributions

"""
    fast_hehl_curvature(k::Int, eta::Float64, t::Int, alpha::Float64=0.5)

Fast analytical approximation of ORC using simplified Hehl structure.
"""
function fast_hehl_curvature(k::Int, eta::Float64, t::Int, alpha::Float64=0.5)
    # Number of exclusive nodes per side
    n_exc = max(0, k - 1 - t)
    
    # Probability of direct edge between exclusive neighborhoods
    p_match = min(eta / k, 1.0)
    
    # Expected distance for exclusive node pairs
    # d = 3 if no edge (u -> exc_u -> ... -> exc_v -> v path)
    # d = 1 if edge (direct shortcut)
    # But this is simplified - actual path might be shorter
    # Heuristic: E[d_exc] = 3 - 2*p_match (ranges from 3 to 1)
    E_d_exc = 3.0 - 2.0 * p_match
    
    # Wasserstein cost components:
    # 1. Mass α at u -> v: cost 1
    cost_idle = alpha * 1.0
    
    # 2. Triangle mass: cost 0 (can stay)
    cost_tri = 0.0
    
    # 3. Exclusive node mass: expected distance
    # Fraction of mass at exclusive nodes: (1-α) * (n_exc/k)
    frac_exc = (1 - alpha) * (n_exc / k)
    cost_exc = frac_exc * E_d_exc
    
    # Total Wasserstein
    W1 = cost_idle + cost_tri + cost_exc
    
    # Curvature
    kappa = 1.0 - W1
    
    return kappa
end

"""
    sample_hehl_curvature(k::Int, eta::Float64, alpha::Float64=0.5; n_samples::Int=1000)

Sample ORC by sampling t ~ Poisson(eta) and computing fast approximation.
"""
function sample_hehl_curvature(k::Int, eta::Float64, alpha::Float64=0.5; 
                                n_samples::Int=1000,
                                rng::AbstractRNG=Random.GLOBAL_RNG)
    curvatures = Float64[]
    
    for _ in 1:n_samples
        t = rand(rng, Poisson(eta))
        t = min(max(t, 0), k - 1)
        
        kappa = fast_hehl_curvature(k, eta, t, alpha)
        push!(curvatures, kappa)
    end
    
    return mean(curvatures), std(curvatures)
end

"""
    load_n1000_data() -> Vector{Dict}
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
    run_fast_comparison()

Fast comparison using analytical approximation.
"""
function run_fast_comparison()
    @info "="^70
    @info "HEHL FAST APPROXIMATION (Analytical)"
    @info "="^70
    
    emp_data = load_n1000_data()
    
    if emp_data === nothing
        @error "Cannot load empirical data"
        return nothing
    end
    
    alpha = 0.5
    comparisons = Dict[]
    
    @info "\nComparing fast Hehl approximation to N=1000 empirical data..."
    @printf("%-4s %6s %10s %10s %10s %10s\n", 
            "k", "η", "κ_emp", "κ_fast", "std", "error")
    
    for emp_point in emp_data
        k = emp_point["k_target"]
        eta = emp_point["ratio"]
        kappa_emp = emp_point["kappa_mean"]
        
        # Fast approximation
        kappa_fast, kappa_std = sample_hehl_curvature(k, eta, alpha; n_samples=1000)
        
        push!(comparisons, Dict(
            "k" => k,
            "eta" => eta,
            "kappa_empirical" => kappa_emp,
            "kappa_fast" => kappa_fast,
            "kappa_std" => kappa_std,
            "error" => abs(kappa_emp - kappa_fast)
        ))
        
        @printf("%4d %6.3f %+.6f %+.6f %10.6f %10.6f\n",
                k, eta, kappa_emp, kappa_fast, kappa_std, abs(kappa_emp - kappa_fast))
    end
    
    # Summary
    mse = mean([c["error"]^2 for c in comparisons])
    mae = mean([c["error"] for c in comparisons])
    
    @info "\n" * "="^70
    @info "SUMMARY"
    @info "="^70
    @info "MSE: $(round(mse, digits=6))"
    @info "MAE: $(round(mae, digits=6))"
    
    # Find sign changes
    emp_cross = nothing
    fast_cross = nothing
    
    for i in 2:length(comparisons)
        if comparisons[i-1]["kappa_empirical"] < 0 && comparisons[i]["kappa_empirical"] > 0
            eta_prev = comparisons[i-1]["eta"]
            eta_curr = comparisons[i]["eta"]
            kappa_prev = comparisons[i-1]["kappa_empirical"]
            kappa_curr = comparisons[i]["kappa_empirical"]
            emp_cross = eta_prev + (eta_curr - eta_prev) * (-kappa_prev) / (kappa_curr - kappa_prev)
        end
        
        if comparisons[i-1]["kappa_fast"] < 0 && comparisons[i]["kappa_fast"] > 0
            eta_prev = comparisons[i-1]["eta"]
            eta_curr = comparisons[i]["eta"]
            kappa_prev = comparisons[i-1]["kappa_fast"]
            kappa_curr = comparisons[i]["kappa_fast"]
            fast_cross = eta_prev + (eta_curr - eta_prev) * (-kappa_prev) / (kappa_curr - kappa_prev)
        end
    end
    
    if emp_cross !== nothing
        @info "Empirical η_c ≈ $(round(emp_cross, digits=3))"
    end
    
    if fast_cross !== nothing
        @info "Fast Hehl η_c ≈ $(round(fast_cross, digits=3))"
    else
        # All positive or all negative - find closest to zero
        closest_idx = argmin([abs(c["kappa_fast"]) for c in comparisons])
        closest_eta = comparisons[closest_idx]["eta"]
        closest_kappa = comparisons[closest_idx]["kappa_fast"]
        @info "Fast Hehl closest to zero: η=$(round(closest_eta, digits=3)), κ=$(round(closest_kappa, digits=4))"
    end
    
    # Extract mean-field curve for different k
    @info "\n" * "="^70
    @info "MEAN-FIELD CURVES (E[κ(η)] vs η)"
    @info "="^70
    
    eta_range = 0.5:0.5:10.0
    k_values = [10, 20, 30, 50, 100]
    
    mean_field_curves = Dict()
    
    for k in k_values
        curve = Dict[]
        for eta in eta_range
            kappa_mean, kappa_std = sample_hehl_curvature(k, eta, alpha; n_samples=500)
            push!(curve, Dict("eta" => eta, "kappa" => kappa_mean, "std" => kappa_std))
        end
        mean_field_curves["k=$k"] = curve
        
        # Find sign change
        for i in 2:length(curve)
            if curve[i-1]["kappa"] < 0 && curve[i]["kappa"] > 0
                eta_c = curve[i-1]["eta"] + (curve[i]["eta"] - curve[i-1]["eta"]) * 
                        (-curve[i-1]["kappa"]) / (curve[i]["kappa"] - curve[i-1]["kappa"])
                @info "k=$k: η_c ≈ $(round(eta_c, digits=2))"
                break
            end
        end
    end
    
    # Large-k extrapolation
    @info "\n" * "="^70
    @info "LARGE-k EXTRAPOLATION"
    @info "="^70
    
    large_k = [20, 30, 50, 100, 200]
    eta_c_values = Float64[]
    
    for k in large_k
        eta_fine = 1.0:0.2:8.0
        for eta in eta_fine
            kappa_mean, _ = sample_hehl_curvature(k, eta, alpha; n_samples=200)
            if kappa_mean > 0
                push!(eta_c_values, eta)
                @info "k=$k: η_c ≈ $eta"
                break
            end
        end
    end
    
    if length(eta_c_values) >= 2
        # Extrapolate to infinity (assume η_c(k) = η_c^∞ - a/k)
        eta_inf = 2 * eta_c_values[end] - eta_c_values[end-1]
        @info "\nEstimated η_c^∞ ≈ $(round(eta_inf, digits=2))"
    end
    
    # Save results
    output = Dict(
        "alpha" => alpha,
        "comparisons_to_n1000" => comparisons,
        "mse" => mse,
        "mae" => mae,
        "eta_c_empirical" => emp_cross,
        "eta_c_fast_hehl" => fast_cross,
        "mean_field_curves" => mean_field_curves,
        "method" => "fast_hehl_approximation",
        "formula" => "kappa ≈ 1 - [alpha + (1-alpha)*((k-1-t)/k)*(3-2*eta/k)]",
        "notes" => "Simplified analytical approximation, not exact LP solution"
    )
    
    output_path = joinpath(@__DIR__, "..", "..", "results", "experiments",
                           "hehl_fast_approximation.json")
    mkpath(dirname(output_path))
    
    open(output_path, "w") do f
        JSON.print(f, output, 2)
    end
    
    @info "\nResults saved to: $output_path"
    
    return output
end

if abspath(PROGRAM_FILE) == @__FILE__
    run_fast_comparison()
end
