"""
Analyze Ricci Flow Convergence Fingerprinting (Discovery K)

Loads existing ricci_flow_*.json files (51 time steps each, 11 networks)
and tests whether geometry class (hyperbolic/Euclidean/spherical) leaves
a distinct divergence signature in discrete Ricci flow trajectories.

Key observation: SWOW-ES (hyperbolic) κ̄: -0.069 → -0.280 (amplifies, not converges!)
Hypothesis: flow amplifies geometry class — opposite of smooth Ricci flow.

Output:
  results/experiments/ricci_flow_analysis.json
  figures/monograph/figure13_ricci_flow_trajectories.pdf/.png
"""

import Pkg
let deps = Pkg.project().dependencies
    for pkg in ["JSON", "Plots", "LaTeXStrings", "Printf", "Statistics"]
        haskey(deps, pkg) || Pkg.add(pkg)
    end
end

using JSON, Plots, Statistics, LaTeXStrings, Printf
gr()

const RESULTS_DIR = joinpath(@__DIR__, "..", "..", "results", "experiments")
const FIGURES_DIR = joinpath(@__DIR__, "..", "..", "figures", "monograph")
const ETA_C_INF   = 3.75

# ─── Network registry (11 individual ricci_flow_*.json files) ─────────────────

const FLOW_FILES = [
    ("swow_es",      "ricci_flow_swow_es.json",      "Hyperbolic", "SWOW Spanish",     0.017),
    ("swow_en",      "ricci_flow_swow_en.json",      "Hyperbolic", "SWOW English",     0.020),
    ("swow_zh",      "ricci_flow_swow_zh.json",      "Hyperbolic", "SWOW Chinese",     0.023),
    ("swow_nl",      "ricci_flow_swow_nl.json",      "Spherical",  "SWOW Dutch",       7.558),
    ("conceptnet_en","ricci_flow_conceptnet_en.json","Hyperbolic", "ConceptNet EN",    0.223),
    ("conceptnet_pt","ricci_flow_conceptnet_pt.json","Hyperbolic", "ConceptNet PT",    0.085),
    ("wordnet_en",   "ricci_flow_wordnet_en.json",   "Euclidean",  "WordNet EN",       0.009),
    ("babelnet_ar",  "ricci_flow_babelnet_ar.json",  "Euclidean",  "BabelNet AR",      0.032),
    ("babelnet_ru",  "ricci_flow_babelnet_ru.json",  "Euclidean",  "BabelNet RU",      0.009),
    ("depression_min","ricci_flow_depression_min.json","Hyperbolic","Depression min",  0.118),
]

# ─── Load and analyze ─────────────────────────────────────────────────────────

println("=== Ricci Flow Convergence Analysis ===\n")

records = []
trajectories = Dict{String, Vector{Float64}}()

for (nid, fname, geom, label, eta) in FLOW_FILES
    path = joinpath(RESULTS_DIR, fname)
    isfile(path) || (println("  SKIP $fname (not found)"); continue)

    d = JSON.parsefile(path)
    traj = d["trajectory"]

    κ_init  = traj[1]["kappa_mean"]
    κ_final = traj[end]["kappa_mean"]
    Δκ      = κ_final - κ_init
    rate    = Δκ / (length(traj) - 1)

    w_gini_init  = traj[1]["w_gini"]
    w_gini_final = traj[end]["w_gini"]
    Δw_gini      = w_gini_final - w_gini_init

    κ_std_init  = traj[1]["kappa_std"]
    κ_std_final = traj[end]["kappa_std"]
    Δκ_std      = κ_std_final - κ_std_init

    dist_to_boundary = eta - ETA_C_INF  # negative = below, positive = above

    push!(records, Dict(
        "network_id"         => nid,
        "label"              => label,
        "geometry"           => geom,
        "eta"                => eta,
        "dist_to_boundary"   => dist_to_boundary,
        "kappa_initial"      => κ_init,
        "kappa_final"        => κ_final,
        "delta_kappa"        => Δκ,
        "divergence_rate"    => rate,
        "w_gini_initial"     => w_gini_init,
        "w_gini_final"       => w_gini_final,
        "delta_w_gini"       => Δw_gini,
        "kappa_std_initial"  => κ_std_init,
        "kappa_std_final"    => κ_std_final,
        "delta_kappa_std"    => Δκ_std,
        "n_steps"            => length(traj) - 1,
    ))

    trajectories[nid] = [step["kappa_mean"] for step in traj]

    @printf("%-20s [%-10s] κ̄: %+.4f → %+.4f  Δκ̄=%+.4f  Δw_gini=%.3f\n",
        label, geom, κ_init, κ_final, Δκ, Δw_gini)
end

# ─── Hypothesis tests ─────────────────────────────────────────────────────────

println("\n=== Hypothesis Tests ===")

geom_groups = Dict("Hyperbolic"=>Float64[], "Euclidean"=>Float64[], "Spherical"=>Float64[])
for r in records
    push!(geom_groups[r["geometry"]], r["delta_kappa"])
end

println("\nH1 — Δκ̄ by geometry class (should be: Hyp<0, Euc≈0, Sph>0):")
for (g, vals) in sort(collect(geom_groups))
    isempty(vals) && continue
    @printf("  %-10s: mean Δκ̄ = %+.4f ± %.4f (n=%d)\n", g, mean(vals), std(vals), length(vals))
end

# H1 check: all hyperbolic Δκ < 0, all spherical Δκ > 0
hyp_pass = all(r["delta_kappa"] < 0 for r in records if r["geometry"] == "Hyperbolic")
sph_pass = all(r["delta_kappa"] > 0 for r in records if r["geometry"] == "Spherical")
println("  H1 PASS (all Hyp<0): $hyp_pass  |  H1 PASS (all Sph>0): $sph_pass")

println("\nH3 — Δw_gini by geometry class (weight concentration grows fastest for Hyperbolic):")
geom_gini = Dict("Hyperbolic"=>Float64[], "Euclidean"=>Float64[], "Spherical"=>Float64[])
for r in records
    push!(geom_gini[r["geometry"]], r["delta_w_gini"])
end
for (g, vals) in sort(collect(geom_gini))
    isempty(vals) && continue
    @printf("  %-10s: mean Δw_gini = %.4f\n", g, mean(vals))
end

println("\nH4 — Δκ_std by geometry class (curvature heterogeneity diverges for Hyperbolic):")
geom_kstd = Dict("Hyperbolic"=>Float64[], "Euclidean"=>Float64[], "Spherical"=>Float64[])
for r in records
    push!(geom_kstd[r["geometry"]], r["delta_kappa_std"])
end
for (g, vals) in sort(collect(geom_kstd))
    isempty(vals) && continue
    @printf("  %-10s: mean Δκ_std = %+.4f\n", g, mean(vals))
end

# ─── Save JSON ────────────────────────────────────────────────────────────────

analysis = Dict(
    "experiment"    => "ricci_flow_analysis",
    "description"   => "Discrete Ricci flow convergence fingerprinting: geometry class divergence signatures",
    "dt"            => 0.5,
    "n_steps"       => 50,
    "eta_c_inf"     => ETA_C_INF,
    "H1_all_hyp_negative" => hyp_pass,
    "H1_all_sph_positive" => sph_pass,
    "class_means"   => Dict(
        g => Dict(
            "delta_kappa_mean" => mean(geom_groups[g]),
            "delta_kappa_std"  => length(geom_groups[g]) > 1 ? std(geom_groups[g]) : 0.0,
            "n" => length(geom_groups[g])
        ) for g in ["Hyperbolic","Euclidean","Spherical"] if !isempty(geom_groups[g])
    ),
    "networks"      => records
)

open(joinpath(RESULTS_DIR, "ricci_flow_analysis.json"), "w") do f
    JSON.print(f, analysis, 2)
end
println("\nSaved ricci_flow_analysis.json")

# ─── Figure: κ̄(t) trajectories ───────────────────────────────────────────────

geom_colors = Dict("Hyperbolic"=>:royalblue, "Euclidean"=>:gray50, "Spherical"=>:firebrick)
geom_styles = Dict("Hyperbolic"=>:solid,     "Euclidean"=>:dash,   "Spherical"=>:solid)

p = plot(
    xlabel    = L"t \; \textrm{(Ricci flow step)}",
    ylabel    = L"\bar{\kappa}(t) \; \textrm{(mean ORC)}",
    title     = "Ricci Flow Fingerprinting: curvature trajectories by geometry class",
    legend    = :bottomleft,
    size      = (760, 500),
    dpi       = 150,
    grid      = true,
    gridalpha = 0.3,
    framestyle = :box,
    margin    = 5Plots.mm
)
hline!(p, [0.0], color=:black, lw=1, linestyle=:dot, label="")

seen_geoms = Set{String}()

for (nid, fname, geom, label, eta) in FLOW_FILES
    haskey(trajectories, nid) || continue
    traj = trajectories[nid]
    steps = 0:length(traj)-1
    col  = geom_colors[geom]
    sty  = geom_styles[geom]
    lbl  = geom in seen_geoms ? "" : geom
    push!(seen_geoms, geom)
    plot!(p, collect(steps), traj, lw=(geom=="Spherical" ? 2.5 : 1.5),
          color=col, linestyle=sty, alpha=(geom=="Euclidean" ? 0.7 : 0.9), label=lbl)
end

# Annotate extremes
for r in records
    nid = r["network_id"]
    haskey(trajectories, nid) || continue
    if r["geometry"] == "Spherical"
        annotate!(p, 51, r["kappa_final"]+0.005,
            text(r["label"], 7, :left, geom_colors["Spherical"]))
    end
end

savefig(p, joinpath(FIGURES_DIR, "figure13_ricci_flow_trajectories.pdf"))
savefig(p, joinpath(FIGURES_DIR, "figure13_ricci_flow_trajectories.png"))
println("Saved figure13_ricci_flow_trajectories.{pdf,png}")
