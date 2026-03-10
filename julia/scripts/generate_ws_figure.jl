"""
Generate Figure 11: Watts-Strogatz Clustering Monotonicity (Theorem 2)

Shows κ̄ vs C with empirical linear fit and β-colored path.

Output: figures/monograph/figure11_watts_strogatz.{pdf,png}
"""

import Pkg
let deps = Pkg.project().dependencies
    for pkg in ["JSON", "Plots", "LaTeXStrings", "ColorSchemes"]
        haskey(deps, pkg) || Pkg.add(pkg)
    end
end

using JSON, Plots, Statistics, LaTeXStrings, Printf
gr()

const RESULTS_DIR = joinpath(@__DIR__, "..", "..", "results")
const FIGURES_DIR = joinpath(@__DIR__, "..", "..", "figures", "monograph")
mkpath(FIGURES_DIR)

# ─── Load data ────────────────────────────────────────────────────────────────

sweep    = JSON.parsefile(joinpath(RESULTS_DIR, "experiments", "clustering_threshold_sweep.json"))
analysis = JSON.parsefile(joinpath(RESULTS_DIR, "experiments", "clustering_sweep_analysis.json"))

rows   = sweep["results"]
C_vals = [r["C_mean"]     for r in rows]
κ_vals = [r["kappa_mean"] for r in rows]
κ_std  = [r["kappa_std"]  for r in rows]
β_vals = [r["beta"]       for r in rows]

a   = analysis["linear_regression"]["intercept"]
b   = analysis["linear_regression"]["slope"]
r2  = analysis["linear_regression"]["r2"]
ci_lo = analysis["linear_regression"]["ci_95_lo"]
ci_hi = analysis["linear_regression"]["ci_95_hi"]

# ─── Hehl formula curve ───────────────────────────────────────────────────────

function hehl_kappa(C::Float64; k::Int=4, η::Float64=0.08, α::Float64=0.5)
    n_exc = (1.0 - C) * (k - 1)
    f_m   = 1.0 - exp(-η * n_exc / k^2)
    W1    = α + (1.0 - α) * (n_exc / k) * (f_m + 3.0 * (1.0 - f_m))
    return 1.0 - W1
end

C_curve   = range(0.01, 0.50, length=100)
κ_hehl    = [hehl_kappa(c) for c in C_curve]
C_fit     = range(minimum(C_vals), maximum(C_vals), length=100)
κ_fit     = a .+ b .* C_fit

# ─── Color map for β ─────────────────────────────────────────────────────────

log_β = log10.(β_vals)
β_norm = (log_β .- minimum(log_β)) ./ (maximum(log_β) - minimum(log_β))
colors = [cgrad(:viridis)[v] for v in β_norm]

# ─── Plot ─────────────────────────────────────────────────────────────────────

p = plot(
    xlabel = L"C \; \textrm{(clustering coefficient)}",
    ylabel = L"\bar{\kappa} \; \textrm{(mean ORC)}",
    title  = "Theorem 2: Clustering Monotonicity of ORC",
    legend = :topleft,
    size   = (700, 500),
    dpi    = 150,
    grid   = true,
    gridalpha = 0.3,
    framestyle = :box,
    margin = 5Plots.mm
)

# Empirical regression line
plot!(p, C_fit, κ_fit,
    lw=2, color=:royalblue, linestyle=:solid,
    label=@sprintf("Empirical fit: slope = %.3f (R² = %.3f)", b, r2))

# Hehl formula curve (shifted to show slope comparison)
# Shift Hehl to match at midpoint since it operates in different regime
C_mid = mean(C_vals)
κ_mid_emp  = a + b*C_mid
κ_mid_hehl = hehl_kappa(C_mid)
κ_hehl_shifted = κ_hehl .+ (κ_mid_emp - κ_mid_hehl)
plot!(p, collect(C_curve), κ_hehl_shifted,
    lw=2, color=:darkorange, linestyle=:dash,
    label=@sprintf("Hehl formula slope ≈ %.2f (shifted)", 1.109))

# Data points colored by β
for i in 1:length(β_vals)
    scatter!(p, [C_vals[i]], [κ_vals[i]],
        yerror=[κ_std[i]],
        markersize=7,
        markercolor=colors[i],
        markerstrokecolor=:gray30,
        markerstrokewidth=0.5,
        label=(i == 1 ? L"\beta \;\textrm{(rewiring prob.)}" : ""),
        markershape=:circle)
end

# Annotate β values at extremes
annotate!(p, C_vals[1]+0.01, κ_vals[1]+0.01, text(@sprintf("β=%.3f", β_vals[1]), 7, :left, :black))
annotate!(p, C_vals[end]+0.01, κ_vals[end]-0.01, text(@sprintf("β=%.1f", β_vals[end]), 7, :left, :black))

# Slope annotation box
annotate!(p, 0.35, 0.27,
    text(@sprintf("∂κ̄/∂C = %.3f ± %.3f\n95%% CI: [%.3f, %.3f]\nR² = %.4f, p ≪ 0.001",
        b, analysis["linear_regression"]["se_slope"], ci_lo, ci_hi, r2),
    8, :left, :royalblue))

savefig(p, joinpath(FIGURES_DIR, "figure12_watts_strogatz.pdf"))
savefig(p, joinpath(FIGURES_DIR, "figure12_watts_strogatz.png"))
println("Saved figure12_watts_strogatz.{pdf,png} to $(FIGURES_DIR)")
