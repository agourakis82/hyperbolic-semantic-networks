"""
POWER-LAW FIT: κ̄(d) ~ A · d^(-β)

Fits log(κ̄(d)) = log(A_k) − β · log(d) via OLS for each k-value,
using exact LP ORC results across d ∈ {4, 8, 16, 32, 64}.

Tests hypothesis: β ≈ 0.5 (Johnson-Lindenstrauss distortion ∝ 1/√d).

Output: results/unified/powerlaw_fit_kappa_d.json
"""

using JSON, Statistics, Printf, LinearAlgebra

const REPO_ROOT = dirname(dirname(dirname(abspath(@__FILE__))))
const RESULTS_DIR = joinpath(REPO_ROOT, "results", "experiments")
const OUTPUT_DIR  = joinpath(REPO_ROOT, "results", "unified")

# Dimensions to fit (must have JSON files)
const DIMS = [4, 8, 16, 32, 64]

# ──────────────────────────────────────────────────────────────────────────────
# Load data
# ──────────────────────────────────────────────────────────────────────────────

function load_dim_data(d::Int)
    path = joinpath(RESULTS_DIR, "hypercomplex_lp_n100_d$(d).json")
    isfile(path) || error("Missing: $path")
    data = JSON.parsefile(path)
    # Build Dict{k => kappa_mean}
    kmap = Dict{Int,Float64}()
    for r in data["results"]
        isnothing(r["kappa_mean"]) && continue
        km = r["kappa_mean"]
        isa(km, Number) || continue
        km > 0 || continue   # skip non-positive (no log-log fit possible)
        kmap[r["k"]] = Float64(km)
    end
    return kmap
end

# ──────────────────────────────────────────────────────────────────────────────
# OLS log-log fit: log(κ̄) = log(A) - β·log(d)
# Returns (beta, log_A, R2)
# ──────────────────────────────────────────────────────────────────────────────

function loglog_ols(dims::Vector{Int}, kappas::Vector{Float64})
    n = length(dims)
    x = log.(Float64.(dims))   # log(d)
    y = log.(kappas)           # log(κ̄)
    x̄ = mean(x)
    ȳ = mean(y)
    Sxx = sum((xi - x̄)^2 for xi in x)
    Sxy = sum((x[i] - x̄) * (y[i] - ȳ) for i in 1:n)
    β   = -Sxy / Sxx           # slope in log-log = -β
    logA = ȳ + β * x̄          # intercept
    ŷ   = [logA - β * xi for xi in x]
    SS_res = sum((y[i] - ŷ[i])^2 for i in 1:n)
    SS_tot = sum((yi - ȳ)^2    for yi in y)
    R2 = 1.0 - SS_res / max(SS_tot, 1e-15)
    return β, exp(logA), R2
end

# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

println("Loading hypercomplex LP data for d ∈ $DIMS ...")
dim_data = Dict(d => load_dim_data(d) for d in DIMS)

# Find k-values present in ALL dimensions
k_sets = [Set(keys(dm)) for dm in values(dim_data)]
common_ks = sort(collect(intersect(k_sets...)))
println("Common k-values across all dims: $common_ks")

# Per-k fit
per_k = []
betas = Float64[]

println("\nPer-k power-law fits:")
println("  k    β       logA    A_k     R²")
println("  " * "─"^42)

for k in common_ks
    kappas = [dim_data[d][k] for d in DIMS]
    β, A, R2 = loglog_ols(DIMS, kappas)
    push!(betas, β)
    push!(per_k, Dict(
        "k"    => k,
        "beta" => round(β, digits=4),
        "A"    => round(A, digits=4),
        "R2"   => round(R2, digits=5),
        "kappa_by_dim" => Dict(string(d) => dim_data[d][k] for d in DIMS)
    ))
    @printf("  k=%-3d β=%.4f  logA=%.4f  A=%.4f  R²=%.5f\n", k, β, log(A), A, R2)
end

β_mean = mean(betas)
β_std  = std(betas; corrected=true)
β_se   = β_std / sqrt(length(betas))
jl_theoretical = 0.5

println("\n" * "─"^50)
@printf("β̄  = %.4f ± %.4f  (SE = %.4f)\n", β_mean, β_std, β_se)
@printf("JL theoretical β = %.1f\n", jl_theoretical)
@printf("Δβ from JL       = %.4f  (%+.1f%%)\n",
    β_mean - jl_theoretical, 100*(β_mean - jl_theoretical)/jl_theoretical)

# k=4 showcase: known values
println("\nk=4 showcase (d=4,8,16,32,64):")
for d in DIMS
    @printf("  d=%-3d  κ̄ = %.6f\n", d, dim_data[d][4])
end
β4, A4, R24 = loglog_ols(DIMS, [dim_data[d][4] for d in DIMS])
@printf("  → β = %.4f, R² = %.5f\n", β4, R24)

# Save output
mkpath(OUTPUT_DIR)
output = Dict(
    "description"        => "Power-law fit κ̄(d) ~ A·d^(-β) per k-value",
    "dimensions_used"    => DIMS,
    "N"                  => 100,
    "n_k_values"         => length(common_ks),
    "beta_mean"          => round(β_mean, digits=5),
    "beta_std"           => round(β_std,  digits=5),
    "beta_se"            => round(β_se,   digits=5),
    "beta_95ci_lo"       => round(β_mean - 1.96*β_se, digits=5),
    "beta_95ci_hi"       => round(β_mean + 1.96*β_se, digits=5),
    "jl_theoretical_beta"=> jl_theoretical,
    "delta_from_jl"      => round(β_mean - jl_theoretical, digits=5),
    "per_k"              => per_k,
)
out_path = joinpath(OUTPUT_DIR, "powerlaw_fit_kappa_d.json")
open(out_path, "w") do f
    JSON.print(f, output, 2)
end
println("\nSaved: $out_path")

# Gate check
println("\n── Verification Gates ──")
gate1 = 0.40 ≤ β_mean ≤ 0.60
gate2 = all(p["R2"] ≥ 0.99 for p in per_k)
@printf("β̄ ∈ [0.40, 0.60]:  %s  (β̄ = %.4f)\n", gate1 ? "PASS ✓" : "FAIL ✗", β_mean)
@printf("All R² ≥ 0.99:      %s\n", gate2 ? "PASS ✓" : "FAIL ✗  (check per-k table above)")
println(gate1 && gate2 ? "\nAll gates PASS ✓" : "\nSome gates FAIL — review output")
