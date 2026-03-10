"""
Analyze Multi-k WS Sweep + Generate Figure 12

Combines k=4 (existing) with k=6, k=8 (new) to test universality of ∂κ̄/∂C > 0.
Produces updated figure12_watts_strogatz.pdf showing all three k-values.

Output:
  results/experiments/multi_k_ws_analysis.json
  figures/monograph/figure12_watts_strogatz.pdf/.png
"""

import Pkg
let deps = Pkg.project().dependencies
    for pkg in ["JSON", "Plots", "LaTeXStrings", "Printf"]
        haskey(deps, pkg) || Pkg.add(pkg)
    end
end

using JSON, Plots, Statistics, LaTeXStrings, Printf
gr()

const RESULTS_DIR = joinpath(@__DIR__, "..", "..", "results", "experiments")
const FIGURES_DIR = joinpath(@__DIR__, "..", "..", "figures", "monograph")

# ─── Load k=4 data (existing sweep) ──────────────────────────────────────────

sweep4 = JSON.parsefile(joinpath(RESULTS_DIR, "clustering_threshold_sweep.json"))
rows4  = sweep4["results"]

# ─── Load k=6,8 data (new sweep) ─────────────────────────────────────────────

sweep_mk = JSON.parsefile(joinpath(RESULTS_DIR, "multi_k_ws_sweep.json"))

# ─── Linear regression helper ─────────────────────────────────────────────────

function linreg(x::Vector{Float64}, y::Vector{Float64})
    x̄, ȳ = mean(x), mean(y)
    ss_xy = sum((x .- x̄) .* (y .- ȳ))
    ss_xx = sum((x .- x̄).^2)
    b     = ss_xy / ss_xx
    a     = ȳ - b * x̄
    ŷ     = a .+ b .* x
    ss_res = sum((y .- ŷ).^2)
    r2     = 1.0 - ss_res / sum((y .- ȳ).^2)
    n      = length(x)
    se_b   = sqrt(ss_res / ((n-2) * ss_xx))
    t_crit = 2.306  # t_{8, 0.025}
    return (a=a, b=b, r2=r2, se_b=se_b, ci_lo=b-t_crit*se_b, ci_hi=b+t_crit*se_b)
end

# ─── Assemble per-k data ───────────────────────────────────────────────────────

k_datasets = Dict{Int, NamedTuple}()

# k=4
C4 = [r["C_mean"]     for r in rows4]
κ4 = [r["kappa_mean"] for r in rows4]
σ4 = [r["kappa_std"]  for r in rows4]
β4 = [r["beta"]       for r in rows4]
r4 = linreg(C4, κ4)
k_datasets[4] = (C=C4, κ=κ4, σ=σ4, β=β4, reg=r4, N=200)

# k=6 and k=8
for k_key in ["k6", "k8"]
    d    = sweep_mk["results"][k_key]
    k    = d["k"]
    N    = d["N"]
    rows = d["rows"]
    C    = [r["C_mean"]     for r in rows]
    κ    = [r["kappa_mean"] for r in rows]
    σ    = [r["kappa_std"]  for r in rows]
    β    = [r["beta"]       for r in rows]
    reg  = linreg(C, κ)
    k_datasets[k] = (C=C, κ=κ, σ=σ, β=β, reg=reg, N=N)
end

println("=== Slope universality test ===")
for k in sort(collect(keys(k_datasets)))
    d = k_datasets[k]
    @printf("k=%d (N=%d, η≈%.3f): ∂κ̄/∂C = %.3f ± %.3f  CI=[%.3f,%.3f]  R²=%.4f\n",
        k, d.N, k^2/d.N, d.reg.b, d.reg.se_b, d.reg.ci_lo, d.reg.ci_hi, d.reg.r2)
end

slopes = [k_datasets[k].reg.b for k in [4,6,8]]
println("\nSlope mean across k: $(round(mean(slopes), digits=3))")
println("Slope std across k:  $(round(std(slopes), digits=3))")
println("All slopes positive: $(all(s > 0 for s in slopes))")

# ─── Save analysis JSON ────────────────────────────────────────────────────────

analysis = Dict(
    "experiment"   => "multi_k_ws_analysis",
    "description"  => "Universality of ∂κ̄/∂C > 0 across k ∈ {4,6,8}",
    "k_values"     => [4, 6, 8],
    "eta_target"   => 0.08,
    "results"      => Dict(
        "k$(k)" => Dict(
            "k"         => k,
            "N"         => k_datasets[k].N,
            "slope"     => k_datasets[k].reg.b,
            "intercept" => k_datasets[k].reg.a,
            "r2"        => k_datasets[k].reg.r2,
            "se_slope"  => k_datasets[k].reg.se_b,
            "ci_95_lo"  => k_datasets[k].reg.ci_lo,
            "ci_95_hi"  => k_datasets[k].reg.ci_hi
        ) for k in [4,6,8]
    ),
    "slope_mean"   => mean(slopes),
    "slope_std"    => std(slopes),
    "all_positive" => all(s > 0 for s in slopes)
)

open(joinpath(RESULTS_DIR, "multi_k_ws_analysis.json"), "w") do f
    JSON.print(f, analysis, 2)
end
println("Saved multi_k_ws_analysis.json")

# ─── Figure: C vs κ̄ for all k, with fits ────────────────────────────────────

k_colors = Dict(4 => :royalblue, 6 => :darkgreen, 8 => :firebrick)
k_shapes = Dict(4 => :circle,    6 => :square,    8 => :diamond)

p = plot(
    xlabel    = L"C \; \textrm{(clustering coefficient)}",
    ylabel    = L"\bar{\kappa} \; \textrm{(mean ORC)}",
    title     = "Theorem 2 universality: ∂κ̄/∂C > 0 for k ∈ {4, 6, 8}",
    legend    = :topleft,
    size      = (720, 520),
    dpi       = 150,
    grid      = true,
    gridalpha = 0.3,
    framestyle = :box,
    margin    = 5Plots.mm
)

for k in [4, 6, 8]
    d   = k_datasets[k]
    col = k_colors[k]
    shp = k_shapes[k]
    reg = d.reg

    # Regression line
    C_fit = range(minimum(d.C), maximum(d.C), length=80)
    plot!(p, collect(C_fit), reg.a .+ reg.b .* C_fit,
        lw=2, color=col, linestyle=:solid, label="")

    # Data points
    scatter!(p, d.C, d.κ,
        yerror=d.σ,
        markersize=6,
        markercolor=col,
        markerstrokecolor=:gray30,
        markerstrokewidth=0.5,
        markershape=shp,
        label=@sprintf("k=%d: slope=%.3f (R²=%.3f)", k, reg.b, reg.r2))
end

savefig(p, joinpath(FIGURES_DIR, "figure12_watts_strogatz.pdf"))
savefig(p, joinpath(FIGURES_DIR, "figure12_watts_strogatz.png"))
println("Saved figure12_watts_strogatz.{pdf,png}")
