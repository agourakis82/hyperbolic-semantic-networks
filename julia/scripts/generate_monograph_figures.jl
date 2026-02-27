"""
MONOGRAPH FIGURE GENERATION

Generates all publication figures for the unified monograph:
1. The Bridge Figure: semantic networks on the phase transition curve
2. Clustering-curvature scatter (three-regime classification)
3. Hypercomplex comparison: hop-count vs. sphere-embedded ORC
4. Phase transition curves (multi-N scaling)

Usage:
    julia generate_monograph_figures.jl
"""

import Pkg
let deps = Pkg.project().dependencies
    for pkg in ["JSON", "Plots", "StatsPlots", "LaTeXStrings", "ColorSchemes"]
        if !haskey(deps, pkg)
            Pkg.add(pkg)
        end
    end
end

using JSON, Plots, Statistics, Printf, LaTeXStrings

# Use GR backend for PDF/PNG output
gr()

const RESULTS_DIR = joinpath(@__DIR__, "..", "..", "results")
const UNIFIED_DIR = joinpath(RESULTS_DIR, "unified")
const FIGURES_DIR = joinpath(@__DIR__, "..", "..", "figures", "monograph")
mkpath(FIGURES_DIR)

# ─────────────────────────────────────────────────────────────────
# Load all data
# ─────────────────────────────────────────────────────────────────

function load_all_data()
    # Semantic network results
    networks = Dict{String, Any}()
    for f in readdir(UNIFIED_DIR)
        if endswith(f, "_exact_lp.json")
            data = JSON.parsefile(joinpath(UNIFIED_DIR, f))
            networks[data["network_id"]] = data
        end
    end

    # Phase transition data (multi-N)
    phase_file = joinpath(RESULTS_DIR, "experiments", "phase_transition_exact_multi_N_v2.json")
    phase_data = JSON.parsefile(phase_file)

    # N=1000 data
    n1000_file = joinpath(RESULTS_DIR, "experiments", "phase_transition_exact_n1000.json")
    n1000 = isfile(n1000_file) ? JSON.parsefile(n1000_file) : nothing

    # Hypercomplex results
    hyper_file = joinpath(UNIFIED_DIR, "hypercomplex_semantic_orc.json")
    hyper_data = isfile(hyper_file) ? JSON.parsefile(hyper_file) : nothing

    # Bridge analysis (includes null models)
    bridge_file = joinpath(UNIFIED_DIR, "bridge_analysis.json")
    bridge_data = isfile(bridge_file) ? JSON.parsefile(bridge_file) : nothing

    return (networks=networks, phase=phase_data, n1000=n1000, hyper=hyper_data, bridge=bridge_data)
end

# ─────────────────────────────────────────────────────────────────
# Figure 1: Phase Transition Curves (multi-N)
# ─────────────────────────────────────────────────────────────────

function figure1_phase_transition(data)
    println("Generating Figure 1: Phase Transition Curves...")

    p = plot(
        xlabel=L"\eta = k^2/N",
        ylabel=L"\bar{\kappa}",
        title="Curvature Sign Change in Random Regular Graphs",
        legend=:bottomright,
        size=(700, 450),
        dpi=300,
        grid=true,
        gridstyle=:dash,
        gridalpha=0.3,
        framestyle=:box,
    )

    # Plot zero line
    hline!([0.0], color=:black, linewidth=0.5, linestyle=:dash, label=nothing)

    colors = Dict("N=50" => :blue, "N=100" => :red, "N=200" => :green,
                   "N=500" => :purple)

    for (nkey, results) in sort(collect(data.phase["results"]), by=x->x[1])
        sorted = sort(results, by=r -> r["ratio"])
        etas = [r["ratio"] for r in sorted]
        kappas = [r["kappa_mean"] for r in sorted]
        stds = [r["kappa_std_ensemble"] for r in sorted]

        c = get(colors, nkey, :gray)
        plot!(etas, kappas, color=c, linewidth=2, marker=:circle, markersize=4,
              label=nkey, ribbon=stds, fillalpha=0.15)
    end

    # N=1000 if available
    if !isnothing(data.n1000)
        sorted = sort(data.n1000["results"], by=r -> r["ratio"])
        etas = [r["ratio"] for r in sorted]
        kappas = [r["kappa_mean"] for r in sorted]
        plot!(etas, kappas, color=:orange, linewidth=2, marker=:circle,
              markersize=4, label="N=1000")
    end

    # Finite-size scaling curve
    N_range = 50:10:1200
    eta_c_curve = [3.75 - 14.62/sqrt(N) for N in N_range]
    # Plot as vertical region
    annotate!(3.5, -0.12, text(L"\eta_c(N) = 3.75 - 14.62/\sqrt{N}", 8, :gray))

    savefig(p, joinpath(FIGURES_DIR, "figure1_phase_transition.pdf"))
    savefig(p, joinpath(FIGURES_DIR, "figure1_phase_transition.png"))
    println("  Saved figure1_phase_transition.{pdf,png}")
end

# ─────────────────────────────────────────────────────────────────
# Figure 2: THE BRIDGE FIGURE — semantic networks on the phase curve
# ─────────────────────────────────────────────────────────────────

function figure2_bridge(data)
    println("Generating Figure 2: Bridge Figure...")

    p = plot(
        xlabel=L"\eta = \langle k \rangle^2 / N",
        ylabel=L"\bar{\kappa}",
        title="Semantic Networks on the Phase Transition Curve",
        legend=:topright,
        size=(800, 500),
        dpi=300,
        grid=true,
        gridstyle=:dash,
        gridalpha=0.3,
        framestyle=:box,
        xscale=:log10,
    )

    # Zero line
    hline!([0.0], color=:black, linewidth=1, linestyle=:dash, label=nothing)

    # Phase transition boundary region (η_c corridor)
    # η_c(N) ranges from ~1.7 (N=50) to ~3.3 (N=1000) to 3.75 (N→∞)
    vspan!([1.5, 4.0], color=:gray, alpha=0.1, label=nothing)
    annotate!(2.5, 0.15, text(L"\eta_c \text{ corridor}", 9, :gray))

    # Background: random graph data points
    for (nkey, results) in data.phase["results"]
        sorted = sort(results, by=r -> r["ratio"])
        etas = [r["ratio"] for r in sorted]
        kappas = [r["kappa_mean"] for r in sorted]
        plot!(etas, kappas, color=:lightgray, linewidth=1, alpha=0.5,
              marker=:circle, markersize=2, markercolor=:lightgray, label=nothing)
    end

    # Semantic networks
    category_style = Dict(
        "association" => (shape=:circle, color=:blue, ms=10),
        "knowledge" => (shape=:diamond, color=:green, ms=10),
        "taxonomy" => (shape=:square, color=:red, ms=8),
        "clinical" => (shape=:star5, color=:purple, ms=10),
    )

    # Plot each network
    for (net_id, net_data) in sort(collect(data.networks), by=x->x[1])
        eta = net_data["eta"]
        kappa = net_data["kappa_mean"]
        cat = net_data["category"]
        C = net_data["clustering"]

        style = get(category_style, cat, (shape=:circle, color=:black, ms=6))

        # Color intensity by clustering
        alpha_val = clamp(0.3 + C * 3.0, 0.3, 1.0)

        scatter!([eta], [kappa],
                marker=style.shape, markersize=style.ms,
                markercolor=style.color, markerstrokecolor=:black,
                markerstrokewidth=1, alpha=alpha_val,
                label=nothing)

        # Label
        offset_x = eta > 1.0 ? 1.3 : 1.5
        offset_y = kappa > 0 ? 0.015 : -0.025
        annotate!(eta * offset_x, kappa + offset_y,
                  text(replace(net_id, "_" => " "), 7, :black))
    end

    # Legend entries (manual)
    scatter!([], [], marker=:circle, markersize=8, color=:blue, label="Association (SWOW)")
    scatter!([], [], marker=:diamond, markersize=8, color=:green, label="Knowledge (ConceptNet)")
    scatter!([], [], marker=:square, markersize=8, color=:red, label="Taxonomy (WordNet/BabelNet)")
    scatter!([], [], marker=:star5, markersize=8, color=:purple, label="Clinical (Depression)")

    # Regime labels
    annotate!(0.005, -0.20, text("HYPERBOLIC\n(η < η_c, C > 0.05)", 9, :blue))
    annotate!(0.005, 0.02, text("EUCLIDEAN\n(η < η_c, C ≈ 0)", 9, :red))
    annotate!(5.0, 0.12, text("SPHERICAL\n(η > η_c)", 9, :orange))

    savefig(p, joinpath(FIGURES_DIR, "figure2_bridge.pdf"))
    savefig(p, joinpath(FIGURES_DIR, "figure2_bridge.png"))
    println("  Saved figure2_bridge.{pdf,png}")
end

# ─────────────────────────────────────────────────────────────────
# Figure 3: Clustering vs. Curvature (three-regime scatter)
# ─────────────────────────────────────────────────────────────────

function figure3_clustering_curvature(data)
    println("Generating Figure 3: Clustering vs Curvature...")

    p = plot(
        xlabel="Clustering Coefficient (C)",
        ylabel=L"\bar{\kappa}",
        title="Three-Regime Classification: η + C → Geometry",
        legend=:bottomleft,
        size=(700, 450),
        dpi=300,
        grid=true,
        gridstyle=:dash,
        gridalpha=0.3,
        framestyle=:box,
        xlim=(-0.01, 0.28),
        ylim=(-0.28, 0.15),
    )

    hline!([0.0], color=:black, linewidth=0.5, linestyle=:dash, label=nothing)
    vline!([0.05], color=:gray, linewidth=1, linestyle=:dot,
           label=L"C^* \approx 0.05")

    category_colors = Dict(
        "association" => :blue, "knowledge" => :green,
        "taxonomy" => :red, "clinical" => :purple
    )
    category_shapes = Dict(
        "association" => :circle, "knowledge" => :diamond,
        "taxonomy" => :square, "clinical" => :star5
    )

    for (net_id, net_data) in data.networks
        C = net_data["clustering"]
        kappa = net_data["kappa_mean"]
        cat = net_data["category"]

        color = get(category_colors, cat, :black)
        shape = get(category_shapes, cat, :circle)

        scatter!([C], [kappa], marker=shape, markersize=10,
                color=color, markerstrokecolor=:black, markerstrokewidth=1,
                label=nothing)
        annotate!(C + 0.005, kappa - 0.015,
                  text(replace(net_id, "_" => " "), 6, :black))
    end

    # Legend
    scatter!([], [], marker=:circle, markersize=8, color=:blue, label="Association")
    scatter!([], [], marker=:diamond, markersize=8, color=:green, label="Knowledge")
    scatter!([], [], marker=:square, markersize=8, color=:red, label="Taxonomy")
    scatter!([], [], marker=:star5, markersize=8, color=:purple, label="Clinical")

    savefig(p, joinpath(FIGURES_DIR, "figure3_clustering_curvature.pdf"))
    savefig(p, joinpath(FIGURES_DIR, "figure3_clustering_curvature.png"))
    println("  Saved figure3_clustering_curvature.{pdf,png}")
end

# ─────────────────────────────────────────────────────────────────
# Figure 4: Hypercomplex comparison (hop vs sphere)
# ─────────────────────────────────────────────────────────────────

function figure4_hypercomplex(data)
    if isnothing(data.hyper)
        println("Skipping Figure 4: No hypercomplex results found")
        return
    end

    println("Generating Figure 4: Hypercomplex Comparison...")

    results = data.hyper["results"]

    # Match with hop-count results
    net_ids = String[]
    kappas_hop = Float64[]
    kappas_sphere = Float64[]

    for r in results
        net_id = r["network_id"]
        hop_file = joinpath(UNIFIED_DIR, "$(net_id)_exact_lp.json")
        if isfile(hop_file)
            hop_data = JSON.parsefile(hop_file)
            push!(net_ids, net_id)
            push!(kappas_hop, hop_data["kappa_mean"])
            push!(kappas_sphere, r["kappa_hyper_mean"])
        end
    end

    p = plot(
        xlabel=L"\bar{\kappa}_{\mathrm{hop}}",
        ylabel=L"\bar{\kappa}_{\mathrm{sphere}}\ (S^3)",
        title="Hop-Count vs. Sphere-Embedded ORC",
        legend=:topleft,
        size=(600, 550),
        dpi=300,
        aspect_ratio=:auto,
        grid=true,
        gridstyle=:dash,
        gridalpha=0.3,
        framestyle=:box,
    )

    # Identity line
    lims = (-0.4, 1.0)
    plot!([lims[1], lims[2]], [lims[1], lims[2]], color=:gray, linewidth=1,
          linestyle=:dash, label="y = x")

    # Zero lines
    hline!([0.0], color=:black, linewidth=0.5, linestyle=:dot, label=nothing)
    vline!([0.0], color=:black, linewidth=0.5, linestyle=:dot, label=nothing)

    # Quadrant labels
    annotate!(-0.25, 0.7, text("Flip to\nspherical", 9, :red, :center))
    annotate!(-0.25, -0.15, text("Stays\nhyperbolic", 9, :blue, :center))

    for i in 1:length(net_ids)
        # Color by whether it flipped
        c = kappas_sphere[i] > 0 && kappas_hop[i] < 0 ? :red : :blue
        # SWOW Spanish = special
        if net_ids[i] == "swow_es"
            c = :gold
        end

        scatter!([kappas_hop[i]], [kappas_sphere[i]],
                markersize=10, color=c, markerstrokecolor=:black,
                markerstrokewidth=1.5, label=nothing)

        annotate!(kappas_hop[i], kappas_sphere[i] - 0.04,
                  text(replace(net_ids[i], "_" => " "), 6, :black))
    end

    scatter!([], [], markersize=8, color=:red, label="Flipped (hop→sphere)")
    scatter!([], [], markersize=8, color=:gold, label="SWOW Spanish (robust)")
    scatter!([], [], markersize=8, color=:blue, label="Remained hyperbolic")

    savefig(p, joinpath(FIGURES_DIR, "figure4_hypercomplex.pdf"))
    savefig(p, joinpath(FIGURES_DIR, "figure4_hypercomplex.png"))
    println("  Saved figure4_hypercomplex.{pdf,png}")
end

# ─────────────────────────────────────────────────────────────────
# Figure 5: Three-Regime Phase Diagram (η vs C, colored by κ)
# ─────────────────────────────────────────────────────────────────

function figure5_phase_diagram(data)
    println("Generating Figure 5: Two-Parameter Phase Diagram...")

    p = plot(
        xlabel=L"\eta = \langle k \rangle^2 / N",
        ylabel="Clustering Coefficient (C)",
        title="Two-Parameter Phase Diagram of Semantic Networks",
        legend=:topright,
        size=(700, 500),
        dpi=300,
        grid=true,
        gridstyle=:dash,
        gridalpha=0.3,
        framestyle=:box,
        xscale=:log10,
    )

    # Regime boundaries
    hline!([0.05], color=:gray, linewidth=1.5, linestyle=:dash,
           label=L"C^* = 0.05")

    # Collect data
    for (net_id, net_data) in data.networks
        eta = net_data["eta"]
        C = net_data["clustering"]
        kappa = net_data["kappa_mean"]

        # Color by curvature sign
        if kappa > 0.05
            c = :orange  # Spherical
        elseif kappa < -0.05
            c = :blue    # Hyperbolic
        else
            c = :gray    # Euclidean
        end

        # Size by |κ|
        ms = 6 + 30 * abs(kappa)

        scatter!([eta], [C], markersize=ms, color=c,
                markerstrokecolor=:black, markerstrokewidth=1.5,
                alpha=0.8, label=nothing)
        annotate!(eta * 1.4, C + 0.008,
                  text(replace(net_id, "_" => " "), 6, :black))
    end

    # Legend
    scatter!([], [], markersize=10, color=:blue, label="Hyperbolic (κ < 0)")
    scatter!([], [], markersize=10, color=:gray, label="Euclidean (κ ≈ 0)")
    scatter!([], [], markersize=10, color=:orange, label="Spherical (κ > 0)")

    # Regime labels with background
    annotate!(0.015, 0.18, text("HYPERBOLIC\nCORRIDOR", 10, :blue, :bold))
    annotate!(0.015, 0.003, text("TREE-LIKE\nEUCLIDEAN", 10, :gray, :bold))

    savefig(p, joinpath(FIGURES_DIR, "figure5_phase_diagram.pdf"))
    savefig(p, joinpath(FIGURES_DIR, "figure5_phase_diagram.png"))
    println("  Saved figure5_phase_diagram.{pdf,png}")
end

# ─────────────────────────────────────────────────────────────────
# Figure 6: Edge curvature distributions (violin/box)
# ─────────────────────────────────────────────────────────────────

function figure6_distributions(data)
    println("Generating Figure 6: Edge Curvature Distributions...")

    # Select representative networks
    representative = ["swow_es", "swow_en", "conceptnet_en", "wordnet_en",
                       "babelnet_ar", "swow_nl", "depression_minimum"]

    net_kappas = []
    net_labels = String[]

    for net_id in representative
        if haskey(data.networks, net_id)
            kappas = data.networks[net_id]["per_edge_curvatures"]
            push!(net_kappas, kappas)
            push!(net_labels, replace(net_id, "_" => "\n"))
        end
    end

    if isempty(net_kappas)
        println("  No edge curvature data found")
        return
    end

    p = plot(
        ylabel=L"\kappa(u,v)",
        title="Per-Edge Curvature Distributions",
        legend=false,
        size=(900, 450),
        dpi=300,
        grid=true,
        gridalpha=0.3,
        framestyle=:box,
    )

    hline!([0.0], color=:black, linewidth=0.5, linestyle=:dash)

    for (i, kappas) in enumerate(net_kappas)
        # Box plot manually
        q1 = quantile(kappas, 0.25)
        q2 = quantile(kappas, 0.50)
        q3 = quantile(kappas, 0.75)
        iqr = q3 - q1
        lower = max(minimum(kappas), q1 - 1.5 * iqr)
        upper = min(maximum(kappas), q3 + 1.5 * iqr)
        mu = mean(kappas)

        # Color by sign of mean
        c = mu > 0.05 ? :orange : mu < -0.05 ? :blue : :gray

        # Box
        plot!([i-0.3, i+0.3, i+0.3, i-0.3, i-0.3],
              [q1, q1, q3, q3, q1], color=c, fill=true, fillalpha=0.3,
              linewidth=1.5, label=nothing)
        # Median line
        plot!([i-0.3, i+0.3], [q2, q2], color=:black, linewidth=2, label=nothing)
        # Mean dot
        scatter!([i], [mu], color=c, markersize=6, markerstrokecolor=:black,
                markerstrokewidth=1, label=nothing)
        # Whiskers
        plot!([i, i], [lower, q1], color=c, linewidth=1, label=nothing)
        plot!([i, i], [q3, upper], color=c, linewidth=1, label=nothing)
    end

    xticks!(1:length(net_labels), net_labels, rotation=0, fontsize=7)

    savefig(p, joinpath(FIGURES_DIR, "figure6_distributions.pdf"))
    savefig(p, joinpath(FIGURES_DIR, "figure6_distributions.png"))
    println("  Saved figure6_distributions.{pdf,png}")
end

# ─────────────────────────────────────────────────────────────────
# Figure 7: Null Model Comparison (real vs. degree-matched random)
# ─────────────────────────────────────────────────────────────────

function figure7_null_models(data)
    if isnothing(data.bridge) || !haskey(data.bridge, "null_models")
        println("Skipping Figure 7: No null model data found")
        return
    end

    println("Generating Figure 7: Null Model Comparison...")

    nulls = data.bridge["null_models"]

    # Sort networks by delta_kappa for visual clarity
    sorted_nets = sort(collect(nulls), by=x -> x[2]["delta_kappa"])

    net_ids = [x[1] for x in sorted_nets]
    kappas_real = [x[2]["real_kappa_mean"] for x in sorted_nets]
    kappas_null = [x[2]["null_kappa_mean"] for x in sorted_nets]
    kappas_null_std = [x[2]["null_kappa_std"] for x in sorted_nets]
    deltas = [x[2]["delta_kappa"] for x in sorted_nets]

    n = length(net_ids)

    p = plot(
        ylabel=L"\bar{\kappa}",
        title="Real vs. Degree-Matched Null Model Curvature",
        legend=:bottomright,
        size=(900, 500),
        dpi=300,
        grid=true,
        gridstyle=:dash,
        gridalpha=0.3,
        framestyle=:box,
    )

    hline!([0.0], color=:black, linewidth=0.5, linestyle=:dash, label=nothing)

    # Null model bars (with error bars)
    bar_width = 0.35
    for i in 1:n
        # Null bar
        plot!([i - bar_width/2, i - bar_width/2, i + bar_width/2 - 0.4, i + bar_width/2 - 0.4, i - bar_width/2],
              [0, kappas_null[i], kappas_null[i], 0, 0],
              fill=true, fillcolor=:lightgray, fillalpha=0.7,
              linecolor=:gray, linewidth=1, label= i==1 ? "Null (random k-regular)" : nothing)

        # Real bar
        plot!([i + bar_width/2 - 0.3, i + bar_width/2 - 0.3, i + bar_width, i + bar_width, i + bar_width/2 - 0.3],
              [0, kappas_real[i], kappas_real[i], 0, 0],
              fill=true, fillcolor=:steelblue, fillalpha=0.7,
              linecolor=:blue, linewidth=1, label= i==1 ? "Real semantic network" : nothing)

        # Delta annotation
        y_pos = max(kappas_real[i], kappas_null[i]) + 0.02
        annotate!(i, y_pos, text(@sprintf("Δ=%+.2f", deltas[i]), 6, :black))
    end

    # Clean labels
    labels = [replace(id, "_" => "\n") for id in net_ids]
    xticks!(1:n, labels, rotation=0, fontsize=6)

    savefig(p, joinpath(FIGURES_DIR, "figure7_null_models.pdf"))
    savefig(p, joinpath(FIGURES_DIR, "figure7_null_models.png"))
    println("  Saved figure7_null_models.{pdf,png}")
end

# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────

function main()
    println("="^70)
    println("MONOGRAPH FIGURE GENERATION")
    println("="^70)

    data = load_all_data()
    println("Loaded $(length(data.networks)) networks")

    figure1_phase_transition(data)
    figure2_bridge(data)
    figure3_clustering_curvature(data)
    figure4_hypercomplex(data)
    figure5_phase_diagram(data)
    figure6_distributions(data)
    figure7_null_models(data)

    println("\n", "="^70)
    println("All figures saved to: $FIGURES_DIR")
    println("="^70)
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
