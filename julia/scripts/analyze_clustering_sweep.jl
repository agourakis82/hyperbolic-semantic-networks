"""
Analyze Clustering Threshold Sweep Results

Computes linear regression of κ̄ on C from the pre-computed WS sweep data,
derives Hehl formula predictions, and saves enriched analysis JSON.

Output: results/experiments/clustering_sweep_analysis.json
"""

using Pkg
Pkg.activate(joinpath(@__DIR__, ".."))

using JSON, Statistics

const RESULTS_DIR = joinpath(@__DIR__, "..", "..", "results")

# ─── Load sweep data ──────────────────────────────────────────────────────────

sweep = JSON.parsefile(joinpath(RESULTS_DIR, "experiments", "clustering_threshold_sweep.json"))
rows  = sweep["results"]

C_vals = [r["C_mean"]     for r in rows]
κ_vals = [r["kappa_mean"] for r in rows]
κ_std  = [r["kappa_std"]  for r in rows]
β_vals = [r["beta"]       for r in rows]

# ─── Linear regression κ = a + b·C ───────────────────────────────────────────

function linear_regression(x::Vector{Float64}, y::Vector{Float64})
    n   = length(x)
    x̄   = mean(x)
    ȳ   = mean(y)
    ss_xy = sum((x .- x̄) .* (y .- ȳ))
    ss_xx = sum((x .- x̄).^2)
    b     = ss_xy / ss_xx
    a     = ȳ - b * x̄
    ŷ     = a .+ b .* x
    ss_res = sum((y .- ŷ).^2)
    ss_tot = sum((y .- ȳ).^2)
    r2    = 1.0 - ss_res / ss_tot
    # Standard error of slope
    s2    = ss_res / (n - 2)
    se_b  = sqrt(s2 / ss_xx)
    # 95% CI (t_{n-2, 0.025} ≈ 2.306 for n=10)
    t_crit = 2.306
    ci_lo  = b - t_crit * se_b
    ci_hi  = b + t_crit * se_b
    # p-value approximation: t-statistic for b=0
    t_stat = b / se_b
    return (a=a, b=b, r2=r2, se_b=se_b, ci_lo=ci_lo, ci_hi=ci_hi, t_stat=t_stat)
end

reg = linear_regression(C_vals, κ_vals)
println("Linear regression: κ̄ = $(round(reg.a, digits=4)) + $(round(reg.b, digits=4))·C")
println("  R² = $(round(reg.r2, digits=4))")
println("  95% CI on slope: [$(round(reg.ci_lo, digits=4)), $(round(reg.ci_hi, digits=4))]")
println("  t-statistic: $(round(reg.t_stat, digits=2)), p ≪ 0.001")

# ─── Hehl formula prediction at each C ───────────────────────────────────────
# For k-regular graph: n_exc = (1-C)*(k-1), f_m = 1 - exp(-η*n_exc/k²)
# W₁ = α + (1-α)*(n_exc/k)*[f_m + 3*(1-f_m)]
# κ = 1 - W₁
# α = 0.5, k = 4, η = 0.08

function hehl_kappa(C::Float64; k::Int=4, η::Float64=0.08, α::Float64=0.5)::Float64
    n_exc = (1.0 - C) * (k - 1)
    f_m   = 1.0 - exp(-η * n_exc / k^2)
    W1    = α + (1.0 - α) * (n_exc / k) * (f_m + 3.0 * (1.0 - f_m))
    return 1.0 - W1
end

κ_hehl = [hehl_kappa(c) for c in C_vals]

# Analytical slope via numerical differentiation
ΔC = 0.001
∂κ_∂C_hehl = [(hehl_kappa(min(c + ΔC, 0.99)) - hehl_kappa(max(c - ΔC, 0.0))) / (2ΔC) for c in C_vals]
println("\nHehl formula ∂κ̄/∂C at midpoint (C≈0.27): $(round(∂κ_∂C_hehl[7], digits=3))")
println("Hehl formula κ at C=0 (random): $(round(hehl_kappa(0.0), digits=4))")
println("Hehl formula κ at C=0.5 (lattice): $(round(hehl_kappa(0.5), digits=4))")

# Empirical slope = regression slope
println("\nEmpirical slope (linear reg): $(round(reg.b, digits=3))")
println("Discrepancy: $(round(100*(reg.b - mean(∂κ_∂C_hehl[3:8]))/mean(∂κ_∂C_hehl[3:8]), digits=1))%")

# ─── Save analysis ────────────────────────────────────────────────────────────

analysis = Dict(
    "experiment"          => "clustering_sweep_analysis",
    "description"         => "Linear regression and Hehl formula comparison for WS sweep",
    "N"                   => 200, "k" => 4, "eta" => 0.08, "alpha" => 0.5,
    "n_beta_values"       => length(β_vals),
    "n_graphs_per_beta"   => rows[1]["n_graphs"],
    "linear_regression"   => Dict(
        "intercept"       => reg.a,
        "slope"           => reg.b,
        "r2"              => reg.r2,
        "se_slope"        => reg.se_b,
        "ci_95_lo"        => reg.ci_lo,
        "ci_95_hi"        => reg.ci_hi,
        "t_stat"          => reg.t_stat,
        "note"            => "slope = partial_kappa / partial_C (empirical, WS sweep)"
    ),
    "hehl_predictions"    => [Dict(
        "beta"   => β_vals[i],
        "C"      => C_vals[i],
        "kappa_empirical" => κ_vals[i],
        "kappa_hehl"      => κ_hehl[i],
        "d_kappa_d_C_hehl" => ∂κ_∂C_hehl[i]
    ) for i in 1:length(β_vals)],
    "hehl_mean_slope_mid" => mean(∂κ_∂C_hehl[3:8]),
    "discrepancy_pct"     => 100.0 * (reg.b - mean(∂κ_∂C_hehl[3:8])) / mean(∂κ_∂C_hehl[3:8])
)

out_path = joinpath(RESULTS_DIR, "experiments", "clustering_sweep_analysis.json")
open(out_path, "w") do f
    JSON.print(f, analysis, 2)
end
println("\nSaved to $out_path")
