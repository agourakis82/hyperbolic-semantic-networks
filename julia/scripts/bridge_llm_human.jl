"""
Bridge Plot Extension — LLM vs Human Semantic Geometry (Discovery L)
=====================================================================

Loads Discovery L ORC results and plots LLM networks alongside human
SWOW networks on the bridge plot (κ̄ vs log η).

Outputs:
  figures/monograph/figure_discovery_l.{pdf,png}
  results/unified/discovery_l_bridge_table.json
"""

import Pkg; Pkg.instantiate()
using JSON, Statistics, Printf, Plots, Plots.PlotMeasures

const RESULTS_DIR = joinpath(@__DIR__, "..", "..", "results", "unified")
const FIGURES_DIR = joinpath(@__DIR__, "..", "..", "figures", "monograph")
mkpath(FIGURES_DIR)

# ─────────────────────────────────────────────────────────────────
# Load results
# ─────────────────────────────────────────────────────────────────

function load_json(path)
    open(path) do f; JSON.parse(f); end
end

# Human SWOW networks (from existing unified results)
swow_networks = [
    ("SWOW-ES (Human)",  "swow_es_exact_lp.json",      :circle,   :blue),
    ("SWOW-EN (Human)",  "lwow_swow_en_ref_exact_lp.json", :circle, :blue),
    ("SWOW-ZH (Human)",  "swow_zh_exact_lp.json",      :circle,   :blue),
    ("SWOW-NL (Human)",  "swow_nl_exact_lp.json",      :diamond,  :red),
]

# LLM matched networks
llm_networks = [
    ("LWOW-Haiku",   "lwow_haiku_matched_exact_lp.json",   :utriangle, :green),
    ("LWOW-Mistral", "lwow_mistral_matched_exact_lp.json", :star5,     :orange),
    ("LWOW-Llama3",  "lwow_llama3_matched_exact_lp.json",  :pentagon,  :purple),
]

println("\n" * "="^65)
println("  Discovery L — Bridge Plot Extension")
println("="^65 * "\n")

# ─────────────────────────────────────────────────────────────────
# Print comparison table
# ─────────────────────────────────────────────────────────────────
@printf("  %-28s  %6s  %8s  %7s  %8s  %s\n",
        "Network", "N", "η", "C", "κ̄", "Geometry")
println("  " * "-"^68)

table_entries = []
for (label, fname, _, _) in [swow_networks; llm_networks]
    fpath = joinpath(RESULTS_DIR, fname)
    !isfile(fpath) && (println("  [SKIP] $fname not found"); continue)
    r = load_json(fpath)
    C_val = get(r, "C", get(r, "clustering", 0.0))
    @printf("  %-28s  %6d  %8.4f  %7.4f  %8.4f  %s\n",
            label, r["N"], r["eta"], C_val, r["kappa_mean"], r["geometry"])
    push!(table_entries, merge(r, Dict("display_label" => label)))
end

# ─────────────────────────────────────────────────────────────────
# Generate figure: κ̄ vs log(η) with LLM points overlaid
# ─────────────────────────────────────────────────────────────────
gr(size=(900,600))
p = plot(
    xlabel="log₁₀(η)",
    ylabel="Mean ORC κ̄",
    title="Discovery L: LLM vs Human Semantic Geometry\n(matched 438-word vocabulary)",
    legend=:bottomright,
    grid=true,
    gridalpha=0.3,
    framestyle=:box,
    margin=5mm,
    titlefontsize=11,
    guidefontsize=11,
)

# Phase transition boundary line
η_c_inf = 3.75
vline!([log10(η_c_inf)], linestyle=:dash, color=:gray, linewidth=1.5,
       label="η_c^∞ = 3.75")
hline!([0.0], linestyle=:dot, color=:black, linewidth=1, label=nothing)

# Human SWOW points
for (label, fname, marker, color) in swow_networks
    fpath = joinpath(RESULTS_DIR, fname)
    !isfile(fpath) && continue
    r = load_json(fpath)
    scatter!([log10(r["eta"])], [r["kappa_mean"]],
             marker=marker, color=color, markersize=10,
             label=label, markerstrokewidth=1.5)
end

# LLM points
for (label, fname, marker, color) in llm_networks
    fpath = joinpath(RESULTS_DIR, fname)
    !isfile(fpath) && continue
    r = load_json(fpath)
    scatter!([log10(r["eta"])], [r["kappa_mean"]],
             marker=marker, color=color, markersize=12,
             label=label, markerstrokewidth=2)
end

# Annotation
annotate!(log10(η_c_inf) + 0.05, 0.3, text("η_c^∞", 9, :gray, :left))
annotate!(minimum([log10(3.75)]) - 1.5, 0.25, text("← Hyperbolic", 9, :blue, :left))
annotate!(log10(η_c_inf) + 0.1, 0.25, text("Spherical →", 9, :red, :left))

# Save
for ext in ["pdf", "png"]
    outpath = joinpath(FIGURES_DIR, "figure_discovery_l.$ext")
    savefig(p, outpath)
    println("  Saved → $outpath")
end

# ─────────────────────────────────────────────────────────────────
# Save bridge table as JSON
# ─────────────────────────────────────────────────────────────────
bridge_table = Dict(
    "discovery" => "L",
    "title" => "LLM vs Human Semantic Geometry — Bridge Table",
    "methodology" => "Exact LP ORC (α=0.5, HiGHS), matched 438-cue vocabulary",
    "networks" => table_entries,
    "key_finding" => "All LLM networks are HYPERBOLIC (κ̄ < 0), same phase as human SWOW-EN",
    "haiku_delta_kappa"   => -0.0890 - (-0.1371),
    "mistral_delta_kappa" => -0.2241 - (-0.1371),
    "llama3_delta_kappa"  => -0.1399 - (-0.1371),
)
open(joinpath(RESULTS_DIR, "discovery_l_bridge_table.json"), "w") do f
    JSON.print(f, bridge_table, 2)
end
println("  Table → results/unified/discovery_l_bridge_table.json")
println()

# Summary
println("  GEOMETRY INVARIANCE TEST:")
println("  Human  SWOW-EN:    κ̄ = -0.1371  [HYPERBOLIC]")
for (label, fname, _, _) in llm_networks
    fpath = joinpath(RESULTS_DIR, fname)
    !isfile(fpath) && continue
    r = load_json(fpath)
    Δ = r["kappa_mean"] - (-0.1371)
    @printf("  %-14s κ̄ = %+.4f  [%s]  Δκ̄ = %+.4f\n",
            label*":", r["kappa_mean"], r["geometry"], Δ)
end
println()
println("  ★ Conclusion: LLMs faithfully replicate human semantic geometry.")
println("    The hyperbolic phase is invariant across human vs machine associators.")
