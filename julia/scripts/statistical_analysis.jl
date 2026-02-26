"""
STATISTICAL ANALYSIS for ORC Phase Transition Manuscript

Loads v2 computation results and produces:
1. 95% confidence intervals for mean curvature at each (k, N)
2. One-sample t-tests for H₀: κ̄ = 0 at transition points (k=14, k=16)
3. Heuristic fit: κ̄ ≈ (η − η_c)/(η + 1), with R² and fitted η_c
4. Finite-size scaling fit: η_c(N) = η_c^∞ − a/√N
5. LLY vs ORC comparison statistics

Usage:
    julia statistical_analysis.jl
"""

import Pkg
let deps = Pkg.project().dependencies
    for pkg in ["JSON", "Distributions", "Optim"]
        if !haskey(deps, pkg)
            Pkg.add(pkg)
        end
    end
end

using JSON
using Statistics
using Distributions
using Optim
using Printf

# ─────────────────────────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────────────────────────

results_dir = joinpath(@__DIR__, "..", "..", "results", "experiments")

function load_json(filename)
    filepath = joinpath(results_dir, filename)
    if !isfile(filepath)
        error("File not found: $filepath")
    end
    return JSON.parsefile(filepath)
end

# ─────────────────────────────────────────────────────────────────
# 1. Confidence intervals
# ─────────────────────────────────────────────────────────────────

"""
Compute 95% CI for mean using t-distribution.
Returns (mean, ci_lower, ci_upper, margin).
"""
function confidence_interval_95(values::Vector{Float64})
    n = length(values)
    if n < 2
        return (values[1], NaN, NaN, NaN)
    end
    m = mean(values)
    s = std(values)
    t_crit = quantile(TDist(n - 1), 0.975)
    margin = t_crit * s / sqrt(n)
    return (m, m - margin, m + margin, margin)
end

"""
One-sample t-test for H₀: μ = μ₀.
Returns (t_statistic, p_value, reject_at_005).
"""
function one_sample_ttest(values::Vector{Float64}; mu0::Float64=0.0)
    n = length(values)
    if n < 2
        return (NaN, NaN, false)
    end
    m = mean(values)
    s = std(values)
    t_stat = (m - mu0) / (s / sqrt(n))
    p_val = 2.0 * ccdf(TDist(n - 1), abs(t_stat))
    return (t_stat, p_val, p_val < 0.05)
end

# ─────────────────────────────────────────────────────────────────
# 2. Heuristic formula fit
# ─────────────────────────────────────────────────────────────────

"""
Fit κ̄ ≈ (η − η_c)/(η + 1) to data.
Returns (η_c, R²).
"""
function fit_heuristic(etas::Vector{Float64}, kappas::Vector{Float64})
    # Objective: minimize Σ (κᵢ - (ηᵢ - η_c)/(ηᵢ + 1))²
    function residual_sse(params)
        eta_c = params[1]
        return sum((kappas[i] - (etas[i] - eta_c) / (etas[i] + 1))^2 for i in 1:length(etas))
    end

    result = optimize(residual_sse, [2.0], BFGS())
    eta_c_fit = Optim.minimizer(result)[1]

    # Compute R²
    kappa_pred = [(eta - eta_c_fit) / (eta + 1) for eta in etas]
    ss_res = sum((kappas .- kappa_pred).^2)
    ss_tot = sum((kappas .- mean(kappas)).^2)
    r_squared = 1.0 - ss_res / ss_tot

    return (eta_c_fit, r_squared, kappa_pred)
end

# ─────────────────────────────────────────────────────────────────
# 3. Finite-size scaling fit
# ─────────────────────────────────────────────────────────────────

"""
Find η_c for a given N by linear interpolation of the sign change.
"""
function find_eta_c(results::Vector)
    sorted = sort(results, by=r -> r["ratio"])
    for i in 2:length(sorted)
        if sorted[i-1]["kappa_mean"] < 0 && sorted[i]["kappa_mean"] >= 0
            # Linear interpolation
            eta1 = sorted[i-1]["ratio"]
            eta2 = sorted[i]["ratio"]
            k1 = sorted[i-1]["kappa_mean"]
            k2 = sorted[i]["kappa_mean"]
            eta_c = eta1 + (0.0 - k1) * (eta2 - eta1) / (k2 - k1)
            return (eta_c, sorted[i-1]["k_target"], sorted[i]["k_target"])
        end
    end
    return (NaN, nothing, nothing)
end

"""
Fit η_c(N) = η_c^∞ − a/√N.
Returns (η_c_inf, a, R²).
"""
function fit_scaling(N_values::Vector{Float64}, eta_c_values::Vector{Float64})
    # Linear regression: η_c = η_c^∞ − a/√N
    # Rewrite as: η_c = η_c^∞ + (−a) × (1/√N)
    # This is y = β₀ + β₁ × x where x = 1/√N
    x = 1.0 ./ sqrt.(N_values)
    y = eta_c_values

    n = length(x)
    x_mean = mean(x)
    y_mean = mean(y)
    beta1 = sum((x .- x_mean) .* (y .- y_mean)) / sum((x .- x_mean).^2)
    beta0 = y_mean - beta1 * x_mean

    y_pred = beta0 .+ beta1 .* x
    ss_res = sum((y .- y_pred).^2)
    ss_tot = sum((y .- y_mean).^2)
    r_squared = ss_tot > 0 ? 1.0 - ss_res / ss_tot : NaN

    eta_c_inf = beta0
    a = -beta1  # η_c = η_c^∞ − a/√N, so β₁ = −a

    return (eta_c_inf, a, r_squared)
end

# ─────────────────────────────────────────────────────────────────
# Main analysis
# ─────────────────────────────────────────────────────────────────

function main()
    println("="^70)
    println("STATISTICAL ANALYSIS: ORC Phase Transition")
    println("="^70)

    # --- Load N=100 data ---
    n100_file = "phase_transition_exact_n100_v2.json"
    if !isfile(joinpath(results_dir, n100_file))
        println("WARNING: $n100_file not found, trying original...")
        n100_file = "phase_transition_exact_n100.json"
    end
    n100_data = load_json(n100_file)
    n100_results = n100_data["results"]

    println("\n--- 1. CONFIDENCE INTERVALS (N=100) ---")
    ci_results = []
    for r in sort(n100_results, by=r -> r["k_target"])
        k = r["k_target"]
        eta = r["ratio"]
        per_seed = haskey(r, "per_seed_kappa_means") ? Float64.(r["per_seed_kappa_means"]) : Float64[r["kappa_mean"]]

        m, ci_lo, ci_hi, margin = confidence_interval_95(per_seed)
        @printf("k=%2d  η=%.2f  κ̄=%+.6f  95%% CI: [%+.6f, %+.6f]  margin=%.6f  n=%d\n",
                k, eta, m, ci_lo, ci_hi, margin, length(per_seed))

        push!(ci_results, Dict(
            "k" => k, "eta" => eta, "kappa_mean" => m,
            "ci_lower" => ci_lo, "ci_upper" => ci_hi, "ci_margin" => margin,
            "n_seeds" => length(per_seed),
            "per_seed_means" => per_seed
        ))
    end

    # --- t-tests at transition points ---
    println("\n--- 2. T-TESTS AT TRANSITION POINTS ---")
    ttest_results = Dict()
    for k_target in [14, 16]
        r = filter(r -> r["k_target"] == k_target, n100_results)
        if isempty(r)
            println("k=$k_target not found in results")
            continue
        end
        r = r[1]
        per_seed = haskey(r, "per_seed_kappa_means") ? Float64.(r["per_seed_kappa_means"]) : Float64[r["kappa_mean"]]
        t_stat, p_val, reject = one_sample_ttest(per_seed)
        @printf("k=%d: t=%.4f, p=%.6f, reject H₀(κ̄=0) at α=0.05: %s\n",
                k_target, t_stat, p_val, reject ? "YES" : "NO")
        ttest_results["k=$k_target"] = Dict(
            "t_statistic" => t_stat, "p_value" => p_val,
            "reject_at_005" => reject, "n" => length(per_seed),
            "mean" => mean(per_seed), "std" => std(per_seed)
        )
    end

    # --- Heuristic formula fit ---
    println("\n--- 3. HEURISTIC FORMULA FIT ---")
    # Use only k >= 3 (k=2 is special: cycles with κ=0)
    fit_data = filter(r -> r["k_target"] >= 3, sort(n100_results, by=r -> r["k_target"]))
    etas = Float64[r["ratio"] for r in fit_data]
    kappas = Float64[r["kappa_mean"] for r in fit_data]

    eta_c_fit, r_squared, kappa_pred = fit_heuristic(etas, kappas)
    @printf("Fit: κ̄ ≈ (η − %.4f)/(η + 1)\n", eta_c_fit)
    @printf("R² = %.6f\n", r_squared)
    @printf("Recommendation: %s\n", r_squared > 0.95 ? "KEEP formula (good fit)" : "CONSIDER REMOVING (poor fit)")

    heuristic_result = Dict(
        "eta_c_fit" => eta_c_fit,
        "r_squared" => r_squared,
        "recommendation" => r_squared > 0.95 ? "keep" : "remove"
    )

    # --- LLY comparison ---
    println("\n--- 4. LLY vs ORC COMPARISON ---")
    lly_comparison = []
    has_lly = any(haskey(r, "lly_kappa_mean") for r in n100_results)
    if has_lly
        for r in sort(n100_results, by=r -> r["k_target"])
            if haskey(r, "lly_kappa_mean")
                diff = r["kappa_mean"] - r["lly_kappa_mean"]
                @printf("k=%2d  κ_ORC=%+.6f  κ_LLY=%+.6f  Δ=%+.6f\n",
                        r["k_target"], r["kappa_mean"], r["lly_kappa_mean"], diff)
                push!(lly_comparison, Dict(
                    "k" => r["k_target"],
                    "orc_mean" => r["kappa_mean"],
                    "lly_mean" => r["lly_kappa_mean"],
                    "difference" => diff
                ))
            end
        end
        diffs = [d["difference"] for d in lly_comparison]
        @printf("\nMean |ORC−LLY| = %.6f, Max |ORC−LLY| = %.6f\n",
                mean(abs.(diffs)), maximum(abs.(diffs)))
    else
        println("LLY data not available in results.")
    end

    # --- Multi-N scaling ---
    println("\n--- 5. FINITE-SIZE SCALING ---")
    multi_n_file = "phase_transition_exact_multi_N_v2.json"
    if !isfile(joinpath(results_dir, multi_n_file))
        println("WARNING: $multi_n_file not found, trying original...")
        multi_n_file = "phase_transition_exact_multi_N.json"
    end

    scaling_result = Dict()
    if isfile(joinpath(results_dir, multi_n_file))
        multi_data = load_json(multi_n_file)
        multi_results = multi_data["results"]

        N_vals = Float64[]
        eta_c_vals = Float64[]
        scaling_details = []

        for key in sort(collect(keys(multi_results)))
            N = parse(Int, replace(key, "N=" => ""))
            results = multi_results[key]
            eta_c, k_below, k_above = find_eta_c(results)
            if !isnan(eta_c)
                push!(N_vals, Float64(N))
                push!(eta_c_vals, eta_c)
                @printf("N=%3d: η_c ≈ %.4f (sign change between k=%s and k=%s)\n",
                        N, eta_c, k_below, k_above)
                push!(scaling_details, Dict(
                    "N" => N, "eta_c" => eta_c,
                    "k_below" => k_below, "k_above" => k_above
                ))
            end
        end

        # --- Also include N=1000 data if available ---
        n1000_file = "phase_transition_exact_n1000.json"
        if isfile(joinpath(results_dir, n1000_file))
            n1000_data = load_json(n1000_file)
            n1000_results = n1000_data["results"]
            eta_c_1000, k_below_1000, k_above_1000 = find_eta_c(n1000_results)
            if !isnan(eta_c_1000)
                push!(N_vals, 1000.0)
                push!(eta_c_vals, eta_c_1000)
                @printf("N=%4d: η_c ≈ %.4f (sign change between k=%s and k=%s)\n",
                        1000, eta_c_1000, k_below_1000, k_above_1000)
                push!(scaling_details, Dict(
                    "N" => 1000, "eta_c" => eta_c_1000,
                    "k_below" => k_below_1000, "k_above" => k_above_1000,
                    "n_seeds" => get(n1000_data, "n_seeds", 3)
                ))
            end
        else
            println("N=1000 data not found, using multi-N data only.")
        end

        if length(N_vals) >= 3
            # Sort by N for display
            perm = sortperm(N_vals)
            N_vals = N_vals[perm]
            eta_c_vals = eta_c_vals[perm]
            scaling_details = scaling_details[perm]

            eta_c_inf, a, r2 = fit_scaling(N_vals, eta_c_vals)
            @printf("\nFit: η_c(N) = %.4f − %.4f/√N\n", eta_c_inf, a)
            @printf("η_c^∞ = %.4f, R² = %.6f\n", eta_c_inf, r2)

            # Also report residuals
            println("\nResiduals:")
            for i in 1:length(N_vals)
                predicted = eta_c_inf - a / sqrt(N_vals[i])
                residual = eta_c_vals[i] - predicted
                @printf("  N=%4d: η_c=%.4f  predicted=%.4f  residual=%+.4f\n",
                        Int(N_vals[i]), eta_c_vals[i], predicted, residual)
            end

            scaling_result = Dict(
                "eta_c_inf" => eta_c_inf, "a" => a, "r_squared" => r2,
                "n_points" => length(N_vals),
                "details" => scaling_details
            )
        else
            println("Not enough data points for scaling fit (need ≥ 3)")
            scaling_result = Dict("details" => scaling_details)
        end
    else
        println("Multi-N data not found.")
    end

    # --- ER comparison ---
    println("\n--- 6. ERDŐS-RÉNYI COMPARISON ---")
    er_file = "er_comparison_n100.json"
    er_comparison = Dict()
    if isfile(joinpath(results_dir, er_file))
        er_data = load_json(er_file)
        er_results = er_data["results"]

        # Find ER sign change
        er_eta_c, er_k_below, er_k_above = find_eta_c(er_results)
        @printf("ER sign change: η_c ≈ %.4f (between k=%s and k=%s)\n",
                er_eta_c, er_k_below, er_k_above)

        # Regular sign change (from N=100 data)
        reg_eta_c, reg_k_below, reg_k_above = find_eta_c(n100_results)
        @printf("Regular sign change: η_c ≈ %.4f (between k=%s and k=%s)\n",
                reg_eta_c, reg_k_below, reg_k_above)
        @printf("Δη_c = %.4f (ER transitions %.4f earlier)\n",
                reg_eta_c - er_eta_c, reg_eta_c - er_eta_c)

        # Per-k comparison
        er_vs_reg = []
        for er_r in sort(er_results, by=r -> r["k_target"])
            k = er_r["k_target"]
            reg_r = filter(r -> r["k_target"] == k, n100_results)
            if !isempty(reg_r)
                reg_r = reg_r[1]
                delta = er_r["kappa_mean"] - reg_r["kappa_mean"]
                @printf("k=%2d: κ_reg=%+.6f  κ_ER=%+.6f  Δ=%+.6f  σ_ER=%.6f\n",
                        k, reg_r["kappa_mean"], er_r["kappa_mean"], delta,
                        er_r["kappa_std_ensemble"])
                push!(er_vs_reg, Dict(
                    "k" => k,
                    "eta" => er_r["ratio"],
                    "kappa_regular" => reg_r["kappa_mean"],
                    "kappa_er" => er_r["kappa_mean"],
                    "delta" => delta,
                    "sigma_er" => er_r["kappa_std_ensemble"]
                ))
            end
        end

        # t-tests at ER transition points (k=12, k=14)
        er_ttest_results = Dict()
        for k_target in [12, 14]
            r = filter(r -> r["k_target"] == k_target, er_results)
            if !isempty(r)
                r = r[1]
                per_seed = haskey(r, "per_seed_kappa_means") ? Float64.(r["per_seed_kappa_means"]) : Float64[r["kappa_mean"]]
                t_stat, p_val, reject = one_sample_ttest(per_seed)
                @printf("ER k=%d: t=%.4f, p=%.2e, reject H₀(κ̄=0): %s\n",
                        k_target, t_stat, p_val, reject ? "YES" : "NO")
                er_ttest_results["k=$k_target"] = Dict(
                    "t_statistic" => t_stat, "p_value" => p_val,
                    "reject_at_005" => reject, "n" => length(per_seed),
                    "mean" => mean(per_seed), "std" => std(per_seed)
                )
            end
        end

        er_comparison = Dict(
            "eta_c_er" => er_eta_c,
            "eta_c_regular" => reg_eta_c,
            "delta_eta_c" => reg_eta_c - er_eta_c,
            "per_k_comparison" => er_vs_reg,
            "er_t_tests" => er_ttest_results,
            "mean_delta" => mean([d["delta"] for d in er_vs_reg]),
            "max_abs_delta" => maximum(abs.([d["delta"] for d in er_vs_reg]))
        )
    else
        println("ER comparison data not found.")
    end

    # --- Save results ---
    output = Dict(
        "experiment" => "statistical_analysis_v2",
        "n100_source" => n100_file,
        "confidence_intervals" => ci_results,
        "t_tests" => ttest_results,
        "heuristic_fit" => heuristic_result,
        "lly_comparison" => lly_comparison,
        "finite_size_scaling" => scaling_result,
        "er_comparison" => er_comparison
    )

    output_file = joinpath(results_dir, "statistical_analysis_v2.json")
    open(output_file, "w") do f
        JSON.print(f, output, 2)
    end

    println("\n", "="^70)
    println("SAVED: $output_file")
    println("="^70)
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
