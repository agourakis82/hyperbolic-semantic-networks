#!/usr/bin/env julia
# Generate CPC 2026 poster figures in Plots.jl.
# 7 panels leading with genuinely strong results.

using JSON, Statistics, CSV, DataFrames, Printf
using Plots, LaTeXStrings, StatsPlots

# Publication styling
default(
    fontfamily="Computer Modern",
    titlefontsize=12,
    guidefontsize=11,
    tickfontsize=9,
    legendfontsize=9,
    dpi=300,
    size=(700, 450),
)

const RESULTS_DIR = joinpath(@__DIR__, "..", "..", "results")
const CPC_DIR = joinpath(RESULTS_DIR, "cpc2026")
const UNIFIED_DIR = joinpath(RESULTS_DIR, "unified")
const EXPERIMENTS_DIR = joinpath(RESULTS_DIR, "experiments")
const POSTER_DIR = joinpath(@__DIR__, "..", "..", "figures", "cpc2026", "poster_jl")
mkpath(POSTER_DIR)

const REGIME_COLORS = Dict(
    "normative"  => :dodgerblue,
    "anxious"    => :red,
    "ruminative" => :orange,
    "psychotic"  => :purple,
)
const REGIME_ORDER = ["normative", "anxious", "ruminative", "psychotic"]

function save_fig(p, name)
    savefig(p, joinpath(POSTER_DIR, "$(name).pdf"))
    savefig(p, joinpath(POSTER_DIR, "$(name).png"))
    println("  Saved $(name).{pdf,png}")
end

# ── Figure 1: Cross-Domain Phase Diagram ────────────────────────────────

function fig1_phase_diagram()
    println("Figure 1: Cross-domain phase diagram")

    cross = CSV.read(joinpath(CPC_DIR, "cross_domain_orc_summary.csv"), DataFrame)
    ref = JSON.parsefile(joinpath(EXPERIMENTS_DIR, "phase_transition_pure_julia.json"))

    ref_eta = Float64[r["ratio"] for r in ref["results"]]
    ref_kappa = Float64[r["kappa_mean"] for r in ref["results"]]
    ref_std = Float64[r["kappa_std"] for r in ref["results"]]

    p = plot(ref_eta, ref_kappa, color=:gray, linewidth=1.5, alpha=0.5,
             ribbon=ref_std, fillalpha=0.08,
             label="Random regular (N=100)",
             xlabel=L"\eta = \langle k \rangle^2 / N",
             ylabel=L"\bar{\kappa}",
             title="Cross-Domain Phase Landscape",
             legend=:bottomright)
    hline!([0.0], color=:gray, linestyle=:dash, alpha=0.5, label="")

    domain_colors = Dict("semantic" => :dodgerblue, "clinical" => :red, "brain" => :green)
    for domain in ["semantic", "clinical", "brain"]
        sub = cross[cross.domain .== domain, :]
        isempty(sub) && continue
        scatter!(sub.eta, sub.kappa_mean,
                 color=domain_colors[domain], markersize=6,
                 markerstrokewidth=0.5, markerstrokecolor=:black,
                 label=uppercasefirst(domain))
    end

    save_fig(p, "poster_fig1_phase_diagram")
end

# ── Figure 2: Depression Curvature Distributions ────────────────────────

function fig2_depression()
    println("Figure 2: Depression curvature distributions")

    epistemic = JSON.parsefile(joinpath(CPC_DIR, "depression_epistemic_orc.json"))

    sevs = ["minimum", "mild", "moderate", "severe"]
    sev_colors = [:green, :orange, :red, :purple]

    # Panel A: Bootstrap CIs
    means = Float64[epistemic["per_severity"][s]["kappa_mean"] for s in sevs]
    ci_lo = Float64[epistemic["per_severity"][s]["ci_lo"] for s in sevs]
    ci_hi = Float64[epistemic["per_severity"][s]["ci_hi"] for s in sevs]
    errs_lo = means .- ci_lo
    errs_hi = ci_hi .- means

    p1 = bar(1:4, means, yerror=(errs_lo, errs_hi),
            color=sev_colors, linecolor=:black, linewidth=0.5,
            xticks=(1:4, uppercasefirst.(sevs)),
            ylabel=L"\bar{\kappa}", title="(A) Mean ORC with 95% Bootstrap CI",
            legend=false, bar_width=0.6)
    hline!([0.0], color=:gray, linestyle=:dash, alpha=0.5)

    # Panel B: Phase location
    etas = Float64[epistemic["per_severity"][s]["eta"] for s in sevs]
    ns = Int[epistemic["per_severity"][s]["N"] for s in sevs]

    p2 = scatter(etas, means, color=sev_colors,
                 markersize=ns ./ 400,
                 markerstrokewidth=0.5, markerstrokecolor=:black,
                 xlabel=L"\eta", ylabel=L"\bar{\kappa}",
                 title="(B) Depression Phase Location",
                 legend=false)
    hline!([0.0], color=:gray, linestyle=:dash, alpha=0.5)
    for (i, s) in enumerate(sevs)
        annotate!(etas[i] + 0.005, means[i] + 0.003,
                  text("N=$(ns[i])", 7, :left))
    end

    p = plot(p1, p2, layout=(1, 2), size=(900, 400),
             plot_title="Depression Speech Networks")
    save_fig(p, "poster_fig2_depression")
end

# ── Figure 3: O-SSM Hidden Entropy Production ──────────────────────────

function fig3_entropy_production()
    println("Figure 3: O-SSM hidden entropy production")

    ossm = JSON.parsefile(joinpath(CPC_DIR, "ossm_statistical_summary.json"))

    # Panel A: Entropy production by regime
    means = Float64[ossm["per_regime"][r]["mean_hidden_entropy_production_rate"] for r in REGIME_ORDER]
    colors = [REGIME_COLORS[r] for r in REGIME_ORDER]

    p1 = bar(1:4, means, color=colors,
            linecolor=:black, linewidth=0.5,
            xticks=(1:4, uppercasefirst.(REGIME_ORDER)),
            ylabel="Hidden Entropy Production Rate",
            title="(A) O-SSM Hidden State Dynamics",
            legend=false, bar_width=0.6)

    # Panel B: Cross-model effect sizes
    cross = ossm["cross_model"]
    metrics = collect(keys(cross))
    markov_ds = Float64[cross[m]["markov_d"] for m in metrics]
    ossm_ds = Float64[cross[m]["ossm_d"] for m in metrics]

    p2 = groupedbar(
        repeat(metrics, outer=2),
        vcat(markov_ds, ossm_ds),
        group=repeat(["Markov", "O-SSM"], inner=length(metrics)),
        orientation=:h,
        color=[:lightblue :salmon],
        linecolor=:black, linewidth=0.5,
        xlabel="Cohen's d (normative vs anxious)",
        title="(B) Effect Size Comparison",
        legend=:bottomright,
    )

    p = plot(p1, p2, layout=(1, 2), size=(1000, 400))
    save_fig(p, "poster_fig3_entropy_production")
end

# ── Figure 4: Ruminative Limit-Cycle Signature ─────────────────────────

function fig4_limit_cycles()
    println("Figure 4: Ruminative limit-cycle signature")

    attractor = CSV.read(joinpath(CPC_DIR, "ossm_attractor_summary.csv"), DataFrame)

    fracs = Float64[]
    colors = Symbol[]
    for r in REGIME_ORDER
        row = attractor[attractor.regime .== r, :]
        push!(fracs, row.limit_cycle_fraction[1])
        push!(colors, REGIME_COLORS[r])
    end

    p = bar(1:4, fracs, color=colors,
           linecolor=:black, linewidth=0.5,
           xticks=(1:4, uppercasefirst.(REGIME_ORDER)),
           ylabel="Limit-Cycle Fraction",
           title="Periodic Attractor Prevalence",
           legend=false, bar_width=0.6, ylim=(0, 0.85))

    for (i, f) in enumerate(fracs)
        annotate!(i, f + 0.02, text(@sprintf("%.1f%%", f * 100), 9, :center))
    end

    save_fig(p, "poster_fig4_limit_cycles")
end

# ── Figure 5: Associator Norm Collapse ──────────────────────────────────

function fig5_associator()
    println("Figure 5: Associator norm collapse")

    ossm = JSON.parsefile(joinpath(CPC_DIR, "ossm_statistical_summary.json"))

    means = Float64[ossm["per_regime"][r]["mean_associator_norm"] for r in REGIME_ORDER]
    ci_lo = Float64[ossm["per_regime"][r]["ci_mean_associator_norm"][1] for r in REGIME_ORDER]
    ci_hi = Float64[ossm["per_regime"][r]["ci_mean_associator_norm"][2] for r in REGIME_ORDER]
    colors = [REGIME_COLORS[r] for r in REGIME_ORDER]

    errs_lo = means .- ci_lo
    errs_hi = ci_hi .- means

    p = bar(1:4, means, yerror=(errs_lo, errs_hi),
           color=colors, linecolor=:black, linewidth=0.5,
           xticks=(1:4, uppercasefirst.(REGIME_ORDER)),
           ylabel=L"\|[a,b,c]\|",
           title="Non-Associative Composition by Regime",
           legend=false, bar_width=0.6)

    d_val = ossm["comparisons"]["normative_vs_anxious_mean_associator_norm"]["cohens_d"]
    annotate!(1.5, maximum(means) / 2,
              text(@sprintf("d = %.2f\n(collapse)", d_val), 9, :center, :red))

    save_fig(p, "poster_fig5_associator")
end

# ── Figure 6: Quaternionic Subspace Occupancy ───────────────────────────

function fig6_subspace()
    println("Figure 6: Quaternionic subspace occupancy")

    occ = CSV.read(joinpath(CPC_DIR, "ossm_subspace_occupancy.csv"), DataFrame)
    subspaces = unique(occ.subspace)

    matrix = zeros(length(REGIME_ORDER), length(subspaces))
    for (i, r) in enumerate(REGIME_ORDER)
        for (j, s) in enumerate(subspaces)
            row = occ[(occ.regime .== r) .& (occ.subspace .== s), :]
            if !isempty(row)
                matrix[i, j] = row.occupancy[1]
            end
        end
    end

    p = heatmap(subspaces, uppercasefirst.(REGIME_ORDER), matrix,
               color=:YlOrRd, clims=(0, maximum(matrix)),
               title="Quaternionic Subspace Occupancy (Fano Plane)",
               xlabel="Subspace", ylabel="Regime",
               size=(650, 350))

    save_fig(p, "poster_fig6_subspace")
end

# ── Figure 7: Cross-Linguistic SWOW ────────────────────────────────────

function fig7_cross_linguistic()
    println("Figure 7: Cross-linguistic SWOW curvature")

    langs = Dict("EN" => "swow_en", "ES" => "swow_es", "ZH" => "swow_zh",
                 "RP" => "swow_rp", "NL" => "swow_nl")
    lang_order = ["EN", "ES", "ZH", "RP", "NL"]

    kappas = Float64[]
    colors = Symbol[]
    for lang in lang_order
        path = joinpath(UNIFIED_DIR, "$(langs[lang])_exact_lp.json")
        d = JSON.parsefile(path)
        push!(kappas, d["kappa_mean"])
        push!(colors, d["kappa_mean"] > 0 ? :red : :dodgerblue)
    end

    p = bar(1:5, kappas, color=colors,
           linecolor=:black, linewidth=0.5,
           xticks=(1:5, lang_order),
           ylabel=L"\bar{\kappa}",
           title="Cross-Linguistic Semantic Curvature (SWOW)",
           legend=false, bar_width=0.6)
    hline!([0.0], color=:gray, linestyle=:dash, alpha=0.5)

    nl_idx = findfirst(==("NL"), lang_order)
    annotate!(nl_idx, kappas[nl_idx] + 0.02,
              text("Spherical\n(supercritical)", 8, :center, :red))

    save_fig(p, "poster_fig7_cross_linguistic")
end

# ── Figure 8: Hurst × Severity Heatmap ─────────────────────────────────

function fig8_hurst_severity()
    println("Figure 8: Ruminative Hurst × severity")

    traj = JSON.parsefile(joinpath(CPC_DIR, "depression_trajectories.json"))
    sevs = ["minimum", "mild", "moderate", "severe"]

    matrix = zeros(length(sevs), length(REGIME_ORDER))
    for (i, sev) in enumerate(sevs)
        for (j, regime) in enumerate(REGIME_ORDER)
            matrix[i, j] = traj["per_severity"][sev]["regimes"][regime]["hurst_mean"]
        end
    end

    p = heatmap(uppercasefirst.(REGIME_ORDER), uppercasefirst.(sevs), matrix,
               color=reverse(cgrad(:RdYlBu)), clims=(0, 1.2),
               title="Ruminative Trapping Intensifies with Depression Severity",
               xlabel="Regime", ylabel="Severity",
               size=(650, 400))

    # Annotate cells with values
    for i in 1:length(sevs)
        for j in 1:length(REGIME_ORDER)
            v = matrix[i, j]
            color = v < 0.4 ? :white : :black
            annotate!(j, i, text(@sprintf("%.2f", v), 9, color, :center))
        end
    end

    save_fig(p, "poster_fig8_hurst_severity")
end

# ── Main ────────────────────────────────────────────────────────────────

function main()
    println("Generating CPC 2026 poster figures (Julia/Plots.jl)\n")

    fig1_phase_diagram()
    fig2_depression()
    fig3_entropy_production()
    fig4_limit_cycles()
    fig5_associator()
    fig6_subspace()
    fig7_cross_linguistic()
    fig8_hurst_severity()

    println("\nAll 8 figures saved to $(POSTER_DIR)/")
end

main()
