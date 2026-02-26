"""
HEHL IMPROVED ANALYTICAL APPROXIMATION

Better analytical approximation using insights from Hehl's explicit formula.

Key insight from Hehl (Eq 17-19): The optimal assignment can be decomposed as:

W* = inf_φ Σ d(z, φ(z)) ≈ (matching on distance-1 edges) + 2×(remaining unmatched)

For the local structure with:
- t triangle nodes (can match at cost 0 or 2)
- n_exc = k-1-t exclusive nodes per side

The Wasserstein cost has the exact decomposition:

W₁ = α·1 + (1-α)/k × [triangle_transport + exclusive_transport]

where:
- triangle_transport = 0 (triangles can match to themselves at cost 0)
- exclusive_transport = optimal assignment on bipartite graph between exc_u and exc_v

For the exclusive part, the optimal assignment cost is:
E[assignment] = Σ_{matched edges} 1 + Σ_{unmatched} 2
              = |matched|×1 + (n_exc - |matched|)×2
              = 2×n_exc - |matched|

where |matched| is the size of the maximum matching in the random bipartite graph.

For a random bipartite graph with edge probability p = η/k:
E[|matched|] ≈ n_exc × (1 - exp(-η/k × n_exc))  [heuristic from random graph theory]

This gives:
E[assignment] ≈ 2×n_exc - n_exc×(1 - exp(-η/k × n_exc))
              = n_exc × (1 + exp(-η×n_exc/k))

Total Wasserstein:
W₁ ≈ α + (1-α)/k × [0 + n_exc × (1 + exp(-η×n_exc/k))]

Curvature:
κ ≈ 1 - W₁
"""

using Statistics
using Random
using JSON
using Printf
using Distributions

"""
    improved_hehl_curvature(k::Int, eta::Float64, t::Int, alpha::Float64=0.5)

Improved analytical approximation using matching-based heuristic.
"""
function improved_hehl_curvature(k::Int, eta::Float64, t::Int, alpha::Float64=0.5)
    # Number of exclusive nodes per side
    n_exc = max(0, k - 1 - t)
    
    if n_exc == 0
        # Only triangles - triangles can match at cost 0
        W1 = alpha * 1.0  # Only the idleness mass at u -> v
        return 1.0 - W1
    end
    
    # Edge probability in exclusive bipartite graph
    p_edge = eta / k
    
    # Expected maximum matching size in random bipartite graph
    # Heuristic: E[|M|] = n_exc * (1 - exp(-p_edge * n_exc))
    # This comes from the fact that each node has ~Poisson(p_edge * n_exc) neighbors
    # and the matching saturates with high probability when degree > 1
    expected_matching = n_exc * (1.0 - exp(-p_edge * n_exc))
    expected_matching = min(expected_matching, n_exc)  # Can't exceed n_exc
    
    # Expected assignment cost:
    # Matched edges: cost 1
    # Unmatched nodes: must go via u->v path, cost 3
    # Actually, unmatched exc_u -> exc_v costs 3 (exc_u -> u -> v -> exc_v)
    # But we need to transport mass (1-α)/k per exclusive node
    
    # Total mass at exclusive nodes per side: (1-α) * n_exc/k
    mass_exc = (1 - alpha) * n_exc / k
    
    # Fraction of exclusive mass that is matched (at cost 1)
    frac_matched = expected_matching / n_exc
    
    # Transport cost for exclusive nodes:
    # - Matched part: cost 1
    # - Unmatched part: cost 3 (via u-v path)
    cost_matched = mass_exc * frac_matched * 1.0
    cost_unmatched = mass_exc * (1 - frac_matched) * 3.0
    
    # Triangle mass transport: cost 0 (stays put)
    cost_triangles = 0.0
    
    # Idleness mass: α from u to v, cost 1
    cost_idle = alpha * 1.0
    
    # Total Wasserstein
    W1 = cost_idle + cost_triangles + cost_matched + cost_unmatched
    
    # Curvature
    kappa = 1.0 - W1
    
    return kappa
end

"""
    sample_improved_curvature(k::Int, eta::Float64, alpha::Float64=0.5; 
                               n_samples::Int=1000)

Sample curvature using improved analytical approximation.
"""
function sample_improved_curvature(k::Int, eta::Float64, alpha::Float64=0.5; 
                                    n_samples::Int=1000,
                                    rng::AbstractRNG=Random.GLOBAL_RNG)
    curvatures = Float64[]
    
    for _ in 1:n_samples
        t = rand(rng, Poisson(eta))
        t = min(max(t, 0), k - 1)
        
        kappa = improved_hehl_curvature(k, eta, t, alpha)
        push!(curvatures, kappa)
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
    run_improved_comparison()
"""
function run_improved_comparison()
    @info "="^70
    @info "HEHL IMPROVED ANALYTICAL APPROXIMATION"
    @info "="^70
    
    emp_data = load_n1000_data()
    
    if emp_data === nothing
        @error "Cannot load empirical data"
        return nothing
    end
    
    alpha = 0.5
    comparisons = Dict[]
    
    @info "\nComparing improved approximation to N=1000 empirical data..."
    @printf("%-4s %6s %10s %10s %10s %10s\n", 
            "k", "η", "κ_emp", "κ_imprvd", "std", "error")
    
    for emp_point in emp_data
        k = emp_point["k_target"]
        eta = emp_point["ratio"]
        kappa_emp = emp_point["kappa_mean"]
        
        # Improved approximation
        kappa_imprvd, kappa_std = sample_improved_curvature(k, eta, alpha; n_samples=1000)
        
        push!(comparisons, Dict(
            "k" => k,
            "eta" => eta,
            "kappa_empirical" => kappa_emp,
            "kappa_improved" => kappa_imprvd,
            "kappa_std" => kappa_std,
            "error" => abs(kappa_emp - kappa_imprvd)
        ))
        
        @printf("%4d %6.3f %+.6f %+.6f %10.6f %10.6f\n",
                k, eta, kappa_emp, kappa_imprvd, kappa_std, abs(kappa_emp - kappa_imprvd))
    end
    
    # Summary
    mse = mean([c["error"]^2 for c in comparisons])
    mae = mean([c["error"] for c in comparisons])
    
    # Find sign changes
    emp_cross = nothing
    imprvd_cross = nothing
    
    for i in 2:length(comparisons)
        if comparisons[i-1]["kappa_empirical"] < 0 && comparisons[i]["kappa_empirical"] > 0
            eta_prev = comparisons[i-1]["eta"]
            eta_curr = comparisons[i]["eta"]
            kappa_prev = comparisons[i-1]["kappa_empirical"]
            kappa_curr = comparisons[i]["kappa_empirical"]
            emp_cross = eta_prev + (eta_curr - eta_prev) * (-kappa_prev) / (kappa_curr - kappa_prev)
        end
        
        if comparisons[i-1]["kappa_improved"] < 0 && comparisons[i]["kappa_improved"] > 0
            eta_prev = comparisons[i-1]["eta"]
            eta_curr = comparisons[i]["eta"]
            kappa_prev = comparisons[i-1]["kappa_improved"]
            kappa_curr = comparisons[i]["kappa_improved"]
            imprvd_cross = eta_prev + (eta_curr - eta_prev) * (-kappa_prev) / (kappa_curr - kappa_prev)
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
    
    if imprvd_cross !== nothing
        @info "Improved η_c ≈ $(round(imprvd_cross, digits=3))"
    end
    
    # Extract mean-field curves
    @info "\n" * "="^70
    @info "MEAN-FIELD CURVES"
    @info "="^70
    
    eta_range = 0.5:0.5:10.0
    k_values = [10, 20, 30, 50, 100, 200]
    
    mean_field_curves = Dict()
    
    for k in k_values
        curve = Dict[]
        for eta in eta_range
            kappa_mean, kappa_std = sample_improved_curvature(k, eta, alpha; n_samples=500)
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
    
    # Self-consistent equation derivation
    @info "\n" * "="^70
    @info "SELF-CONSISTENT EQUATION (NUMERICAL)"
    @info "="^70
    
    # For large k, find η_c and extrapolate
    large_k = [50, 100, 150, 200, 300, 500]
    eta_c_values = Float64[]
    
    for k in large_k
        eta_fine = 1.0:0.1:8.0
        for eta in eta_fine
            kappa_mean, _ = sample_improved_curvature(k, eta, alpha; n_samples=200)
            if kappa_mean > 0
                push!(eta_c_values, eta)
                @info "k=$k: η_c ≈ $eta"
                break
            end
        end
    end
    
    if length(eta_c_values) >= 3
        # Fit η_c(k) = η_c^∞ - a/k
        # Use last two points for extrapolation
        eta_inf = 2 * eta_c_values[end] - eta_c_values[end-1]
        @info "\nEstimated η_c^∞ ≈ $(round(eta_inf, digits=2))"
        
        # Also fit a
        a = (eta_inf - eta_c_values[end]) * large_k[length(eta_c_values)]
        @info "Fitted: η_c(k) ≈ $(round(eta_inf, digits=2)) - $(round(a, digits=2))/k"
    end
    
    # Save results
    output = Dict(
        "alpha" => alpha,
        "comparisons_to_n1000" => comparisons,
        "mse" => mse,
        "mae" => mae,
        "eta_c_empirical" => emp_cross,
        "eta_c_improved" => imprvd_cross,
        "mean_field_curves" => mean_field_curves,
        "method" => "improved_analytical_approximation",
        "formula" => "E[|M|] = n_exc * (1 - exp(-eta*n_exc/k)); W1 = alpha + (1-alpha)/k * (2*n_exc - E[|M|])",
        "notes" => "Matching-based heuristic for exclusive neighborhood transport"
    )
    
    output_path = joinpath(@__DIR__, "..", "..", "results", "experiments",
                           "hehl_improved_analytical.json")
    mkpath(dirname(output_path))
    
    open(output_path, "w") do f
        JSON.print(f, output, 2)
    end
    
    @info "\nResults saved to: $output_path"
    
    return output
end

if abspath(PROGRAM_FILE) == @__FILE__
    run_improved_comparison()
end
