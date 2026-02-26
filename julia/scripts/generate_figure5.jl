#!/usr/bin/env julia
# generate_figure5.jl
# Figure 5: Dimensional phase boundary
# Shows κ̄ vs η for three metric spaces at N=100:
#   • Hop-count (d→∞): sign change at η_c ≈ 2.22
#   • S³ / Q4 (d=4): monotone positive
#   • S⁷ / Oct (d=8): monotone positive

import Pkg
ENV["GKSwstype"] = "100"   # headless / no display
for pkg in ["Plots", "JSON", "Printf", "Statistics"]
    try; @eval using $(Symbol(pkg)); catch; Pkg.add(pkg); @eval using $(Symbol(pkg)); end
end

# ── Load data ──────────────────────────────────────────────────────────────
RESULTS = "results/experiments"

function load_kappa(file)
    data = JSON.parsefile(file)
    rows = data["results"]
    ηs  = Float64[r["eta"]   for r in rows]
    κs  = [r["kappa_mean"] for r in rows]   # may contain nothing (null)
    # replace nothing with NaN
    κs_f = [isnothing(k) ? NaN : Float64(k) for k in κs]
    return ηs, κs_f
end

# Hop-count (exact LP, N=100, 10 seeds)
hop_file = "$RESULTS/phase_transition_exact_n100_v2.json"
hop_data = JSON.parsefile(hop_file)
hop_rows = hop_data["results"]
η_hop = Float64[r["k_actual"]^2 / r["N"] for r in hop_rows]
κ_hop = Float64[r["kappa_mean"] for r in hop_rows]

# Hypercomplex exact LP (N=100)
η_d4, κ_d4 = load_kappa("$RESULTS/hypercomplex_lp_n100_d4.json")
η_d8, κ_d8 = load_kappa("$RESULTS/hypercomplex_lp_n100_d8.json")

# d=16 if available
d16_file = "$RESULTS/hypercomplex_lp_n100_d16.json"
has_d16 = isfile(d16_file)
η_d16, κ_d16 = has_d16 ? load_kappa(d16_file) : (Float64[], Float64[])

# ── Plot ──────────────────────────────────────────────────────────────────
gr(size=(700, 480), dpi=150)

plt = plot(
    xlabel = "Density η = k²/N",
    ylabel = "Mean ORC  κ̄",
    title  = "Dimensional phase boundary (N = 100)",
    legend = :right,
    framestyle = :box,
    grid   = true,
    gridalpha = 0.3,
    ylims  = (-0.5, 0.5),
    xlims  = (0, 9.5),
)

# Zero line
hline!(plt, [0.0], color=:black, linestyle=:dash, linewidth=1, label="")

# Hop-count: sign change
plot!(plt, η_hop, κ_hop,
    color     = :steelblue,
    linewidth = 2.5,
    marker    = :circle,
    markersize = 4,
    label     = "Hop-count (d→∞)",
)

# S³ (d=4): monotone positive
valid_d4 = .!isnan.(κ_d4)
plot!(plt, η_d4[valid_d4], κ_d4[valid_d4],
    color     = :firebrick,
    linewidth = 2.5,
    marker    = :diamond,
    markersize = 4,
    label     = "S³ (d=4, quaternionic)",
)

# S⁷ (d=8): monotone positive
valid_d8 = .!isnan.(κ_d8)
plot!(plt, η_d8[valid_d8], κ_d8[valid_d8],
    color     = :forestgreen,
    linewidth = 2.5,
    marker    = :utriangle,
    markersize = 4,
    label     = "S⁷ (d=8, octonionic)",
)

# S¹⁵ (d=16) if available
if has_d16 && !isempty(η_d16)
    valid_d16 = .!isnan.(κ_d16)
    plot!(plt, η_d16[valid_d16], κ_d16[valid_d16],
        color     = :darkorange,
        linewidth = 2.5,
        marker    = :star5,
        markersize = 4,
        label     = "S¹⁵ (d=16, sedenion)",
    )
end

# Annotate η_c for hop-count
# Interpolate: between k=14 (η=1.96, κ=-0.016) and k=16 (η=2.56, κ=+0.022)
η_c_hop = 1.96 + 0.016/(0.016+0.022) * (2.56-1.96)
annotate!(plt, η_c_hop + 0.15, -0.10,
    text(@sprintf("η_c ≈ %.2f", η_c_hop), :steelblue, :left, 9))
vline!(plt, [η_c_hop], color=:steelblue, linestyle=:dot, alpha=0.5, label="")

# Shade hyperbolic (κ<0) region
areamax = 0.0
areavals = fill(-0.45, 2)
plot!(plt, [0.0, 9.5], [-0.45, -0.45], fillrange=[0.0, 0.0],
    fillalpha=0.05, fillcolor=:steelblue, linewidth=0, label="")

# ── Save ──────────────────────────────────────────────────────────────────
mkpath("figures/paper")
savefig(plt, "figures/paper/figure5_dimensional_phase_boundary.pdf")
savefig(plt, "figures/paper/figure5_dimensional_phase_boundary.png")
println("Saved → figures/paper/figure5_dimensional_phase_boundary.{pdf,png}")

# Print summary table
println("\n── Dimensional phase boundary summary (N=100) ──")
@printf("  %-20s  %6s  %8s  %8s\n", "Embedding", "d", "κ at k=4", "κ at k_max")
idx_k4 = argmin(abs.(η_hop .- 0.16))  # k=4 for N=100 → η=0.16
@printf("  %-20s  %6s  %8.3f  %8.3f\n", "Hop-count", "∞", κ_hop[idx_k4], κ_hop[end])
idx_d4_k4 = argmin(abs.(η_d4 .- 0.16))
@printf("  %-20s  %6d  %8.3f  %8.3f\n", "Q4 (S³)", 4, κ_d4[idx_d4_k4], κ_d4[end])
idx_d8_k4 = argmin(abs.(η_d8 .- 0.16))
@printf("  %-20s  %6d  %8.3f  %8.3f\n", "Oct (S⁷)", 8, κ_d8[idx_d8_k4], κ_d8[end])
if has_d16 && !isempty(κ_d16)
    idx_d16_k4 = argmin(abs.(η_d16 .- 0.16))
    @printf("  %-20s  %6d  %8.3f  %8.3f\n", "Sed (S¹⁵)", 16, κ_d16[idx_d16_k4], κ_d16[end])
end
