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

    # Analytical η_c data
    anl_file = joinpath(UNIFIED_DIR, "analytical_eta_c.json")
    anl_data = isfile(anl_file) ? JSON.parsefile(anl_file) : nothing

    return (networks=networks, phase=phase_data, n1000=n1000, hyper=hyper_data, bridge=bridge_data, analytical=anl_data)
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

    println("Generating Figure 4: Hypercomplex Dimensional Hierarchy...")

    results = data.hyper["results"]

    # Group results by network
    by_net = Dict{String, Dict{Int, Float64}}()
    for r in results
        nid = r["network_id"]
        d = r["embedding_dim"]
        if !haskey(by_net, nid)
            by_net[nid] = Dict{Int, Float64}()
        end
        by_net[nid][d] = r["kappa_hyper_mean"]
    end

    # Get hop-count values
    hop_vals = Dict{String, Float64}()
    for nid in keys(by_net)
        hop_file = joinpath(UNIFIED_DIR, "$(nid)_exact_lp.json")
        if isfile(hop_file)
            hop_vals[nid] = JSON.parsefile(hop_file)["kappa_mean"]
        end
    end

    # Nice labels
    labels = Dict(
        "swow_es" => "SWOW ES", "swow_en" => "SWOW EN", "swow_zh" => "SWOW ZH",
        "swow_nl" => "SWOW NL", "conceptnet_en" => "CN EN", "conceptnet_pt" => "CN PT",
        "wordnet_en" => "WN EN", "wordnet_en_2k" => "WN 2K",
        "babelnet_ru" => "BN RU", "babelnet_ar" => "BN AR",
        "depression_minimum" => "Depr."
    )

    # Category colors
    cat_colors = Dict(
        "swow_es" => :royalblue, "swow_en" => :dodgerblue, "swow_zh" => :steelblue,
        "swow_nl" => :cornflowerblue,
        "conceptnet_en" => :forestgreen, "conceptnet_pt" => :seagreen,
        "wordnet_en" => :firebrick, "wordnet_en_2k" => :indianred,
        "babelnet_ru" => :darkorange, "babelnet_ar" => :orange,
        "depression_minimum" => :purple
    )

    # Load deep hypercomplex semantic data (d=32) from Sounio results if available
    # Format: network_id,N,E,d,kappa_geo,geometry (one per line, skip # comments)
    exp_dir = joinpath(RESULTS_DIR, "experiments")
    sounio_d32 = joinpath(exp_dir, "hypercomplex_semantic_sounio_d32.txt")
    if isfile(sounio_d32)
        for line in readlines(sounio_d32)
            startswith(line, "#") && continue
            isempty(strip(line)) && continue
            parts = split(strip(line), ",")
            length(parts) < 5 && continue
            nid = parts[1]
            try
                κ = parse(Float64, parts[5])
                if haskey(by_net, nid)
                    by_net[nid][32] = κ
                end
            catch; end
        end
    end

    # Determine which dimensions are available across all networks
    all_dims_present = Set{Int}()
    for nid in keys(by_net)
        for d in keys(by_net[nid])
            push!(all_dims_present, d)
        end
    end
    deep_dims = sort([d for d in all_dims_present if d > 16])
    plot_dims = [4, 8, 16, deep_dims...]
    dim_labels_base = Dict(4 => "S³", 8 => "S⁷", 16 => "S¹⁵", 32 => "S³¹", 64 => "S⁶³")
    dim_labels = vcat(["Hop"], [get(dim_labels_base, d, "S$(d-1)") for d in plot_dims])
    n_cols = 1 + length(plot_dims)

    p = plot(
        xlabel="Embedding Space",
        ylabel=L"\bar{\kappa}",
        title="Curvature Across the Cayley-Dickson Tower",
        legend=:topright,
        size=(900, 500),
        dpi=300,
        grid=true,
        gridstyle=:dash,
        gridalpha=0.3,
        framestyle=:box,
        xticks=(1:n_cols, dim_labels),
    )

    hline!([0.0], color=:black, linewidth=1.0, linestyle=:dash, label=nothing)

    # Plot each network as a line across all available dimensions
    for nid in sort(collect(keys(by_net)))
        if !haskey(hop_vals, nid)
            continue
        end
        vals = Float64[]
        push!(vals, hop_vals[nid])
        for d in plot_dims
            push!(vals, get(by_net[nid], d, NaN))
        end

        c = get(cat_colors, nid, :gray)
        lbl = get(labels, nid, nid)
        lw = nid == "swow_es" ? 3 : 1.5

        plot!(1:n_cols, vals, color=c, linewidth=lw, marker=:circle, markersize=5,
              markerstrokecolor=:black, markerstrokewidth=0.5, label=lbl)
    end

    # Power-law fit κ̄(d) ~ A·d^(-β) if d=32 or d=64 data available
    if !isempty(deep_dims)
        # Use k=4 SWOW-ES as representative network for fit
        fit_net = "swow_es"
        if haskey(by_net, fit_net)
            fit_ds = Float64[]; fit_ks = Float64[]
            for d in [4, 8, 16, deep_dims...]
                v = get(by_net[fit_net], d, NaN)
                if !isnan(v) && v > 0
                    push!(fit_ds, d); push!(fit_ks, v)
                end
            end
            if length(fit_ds) >= 3
                # log-log fit: log(κ) = log(A) - β·log(d)
                log_d = log.(fit_ds); log_k = log.(fit_ks)
                beta = -(sum(log_d .* log_k) - sum(log_d)*sum(log_k)/length(log_d)) /
                        (sum(log_d.^2) - sum(log_d)^2/length(log_d))
                log_A = sum(log_k)/length(log_k) + beta * sum(log_d)/length(log_d)
                A = exp(log_A)
                d_fine = 4:0.5:maximum(plot_dims)+4
                k_fit = [A * d^(-beta) for d in d_fine]
                # Map d_fine to x-axis positions
                x_fine = [1 + log2(d/4) + 1 for d in d_fine]  # approximate spacing
                annotate!(n_cols - 0.5, minimum(k_fit)+0.01,
                          text(@sprintf("κ∝d^{-%.2f}", beta), 8, :gray, :right))
            end
        end
    end

    # Annotate the flip region
    annotate!(1.5, -0.05, text("← sign flip zone", 8, :red, :left))

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
# Figure 8: Analytical Phase Boundary
# ─────────────────────────────────────────────────────────────────

function figure8_analytical_boundary(data)
    if data.analytical === nothing || data.bridge === nothing
        println("Skipping Figure 8: No analytical or bridge data found")
        return
    end

    println("Generating Figure 8: Analytical Phase Boundary...")

    fig8 = data.analytical["figure8_data"]

    p = plot(
        xlabel="C (clustering coefficient)",
        ylabel="η_c (critical density)",
        title="Analytical Phase Boundary: η_c(C, N)",
        legend=:topright,
        size=(700, 500),
        dpi=300,
        grid=true, gridstyle=:dash, gridalpha=0.3,
        framestyle=:box,
        ylims=(0, 8),
        xlims=(-0.01, 0.30),
    )

    # N→∞ curve (thick, black)
    if haskey(fig8, "N_inf")
        C_vals = fig8["N_inf"]["C"]
        eta_vals = fig8["N_inf"]["eta_c"]
        # Filter out NaN
        valid = [(c, e) for (c, e) in zip(C_vals, eta_vals) if !isnan(e)]
        if !isempty(valid)
            plot!(first.(valid), last.(valid), color=:black, linewidth=3,
                  linestyle=:solid, label="N → ∞")
        end
    end

    # Finite N curves
    N_labels = ["N=100", "N=200", "N=500", "N=1000"]
    line_colors = [:blue, :red, :green, :purple]
    line_styles = [:dash, :dashdot, :dot, :solid]

    for (i, nlbl) in enumerate(N_labels)
        if haskey(fig8, nlbl)
            C_vals = fig8[nlbl]["C"]
            eta_vals = fig8[nlbl]["eta_c"]
            valid = [(c, e) for (c, e) in zip(C_vals, eta_vals) if !isnan(e)]
            if !isempty(valid)
                plot!(first.(valid), last.(valid), color=line_colors[i], linewidth=1.5,
                      linestyle=line_styles[i], label=nlbl)
            end
        end
    end

    # Overlay semantic networks from bridge data
    short_labels = Dict(
        "swow_nl" => "NL", "swow_en" => "EN", "swow_es" => "ES",
        "swow_zh" => "ZH", "conceptnet_en" => "CN-en",
        "conceptnet_pt" => "CN-pt", "wordnet_en" => "WN",
        "wordnet_en_2k" => "WN-2k", "babelnet_ru" => "BN-ru",
        "babelnet_ar" => "BN-ar", "depression_minimum" => "DEP"
    )

    for net in data.bridge["bridge"]
        C = net["clustering"]
        eta = net["eta"]
        kappa = net["kappa_mean"]
        id = net["network_id"]

        # Color by geometry
        if kappa > 0.05
            mc = :red; ms = :star5
        elseif kappa < -0.05
            mc = :blue; ms = :circle
        else
            mc = :gray; ms = :diamond
        end

        scatter!([C], [eta], color=mc, marker=ms, markersize=8,
                 markerstrokewidth=1.5, markerstrokecolor=:black,
                 label=nothing)

        label_text = get(short_labels, id, id)
        offset_y = kappa > 0 ? 0.25 : -0.25
        annotate!(C + 0.005, eta + offset_y, text(label_text, 7, :left))
    end

    # Regime annotations
    annotate!(0.22, 1.0, text("η < η_c: hyperbolic", 9, :blue, :center))
    annotate!(0.22, 7.0, text("η > η_c: spherical", 9, :red, :center))

    savefig(p, joinpath(FIGURES_DIR, "figure8_analytical_boundary.pdf"))
    savefig(p, joinpath(FIGURES_DIR, "figure8_analytical_boundary.png"))
    println("  Saved figure8_analytical_boundary.{pdf,png}")
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
    figure8_analytical_boundary(data)

    println("\n", "="^70)
    println("All figures saved to: $FIGURES_DIR")
    println("="^70)
end

# ─────────────────────────────────────────────────────────────────
# Figure 9: BA Sign-Change Comparison
# ─────────────────────────────────────────────────────────────────

function figure9_ba_comparison()
    println("Generating Figure 9: BA Sign-Change Comparison...")

    exp_dir = joinpath(RESULTS_DIR, "experiments")

    # Load available BA data files
    ba_datasets = Dict{String, Any}()
    for N in [100, 200, 500, 1000]
        f = joinpath(exp_dir, "ba_comparison_n$(N).json")
        if isfile(f)
            ba_datasets["N=$N"] = JSON.parsefile(f)
        end
    end
    if isempty(ba_datasets)
        println("  No BA comparison data found — skipping figure 9")
        return
    end

    # Load ER data (use multi-N, pick N=100)
    er_file = joinpath(exp_dir, "er_comparison_n100.json")
    er_data = isfile(er_file) ? JSON.parsefile(er_file) : nothing

    # Load regular k-regular data (multi-N, pick N=100 slice)
    phase_file = joinpath(exp_dir, "phase_transition_exact_n100_v2.json")
    phase_data = isfile(phase_file) ? JSON.parsefile(phase_file) : nothing

    p = plot(
        xlabel=L"\eta = \langle k \rangle^2 / N",
        ylabel=L"\bar{\kappa}\ \text{(mean ORC)}",
        title="Curvature Sign Change: Three Random Graph Families (N=100)",
        legend=:bottomright,
        size=(800, 500),
        dpi=300,
        grid=true,
        gridstyle=:dash,
        gridalpha=0.3,
        framestyle=:box,
        xlims=(0, 12),
    )
    hline!([0.0], color=:black, linewidth=0.8, linestyle=:dash, label=nothing)

    # k-regular (blue)
    if !isnothing(phase_data)
        res = sort(phase_data["results"], by=r -> r["ratio"])
        plot!(
            [r["ratio"] for r in res],
            [r["kappa_mean"] for r in res],
            color=:steelblue, linewidth=2, marker=:circle, markersize=5,
            label=L"k\text{-regular}\ (\eta_c \approx 2.22)",
            ribbon=[r["kappa_std_ensemble"] for r in res],
            fillalpha=0.15,
        )
        vline!([2.22], color=:steelblue, linewidth=1, linestyle=:dot, label=nothing)
    end

    # ER (orange) — uses "ratio" key (= η) in er_comparison_n100.json
    if !isnothing(er_data)
        res = sort(er_data["results"], by=r -> r["ratio"])
        er_std = [get(r, "kappa_std_ensemble", 0.0) for r in res]
        plot!(
            [r["ratio"] for r in res],
            [r["kappa_mean"] for r in res],
            color=:darkorange, linewidth=2, marker=:diamond, markersize=5,
            label=L"\mathrm{Erd\H{o}s\text{-}R\acute{e}nyi}\ (\eta_c \approx 1.90)",
            ribbon=er_std,
            fillalpha=0.15,
        )
        vline!([1.90], color=:darkorange, linewidth=1, linestyle=:dot, label=nothing)
    end

    # BA (red shades) — N=100 primary, overlay N=200+ if available
    ba_colors  = Dict("N=100" => :crimson, "N=200" => :red3,   "N=500" => :red4,    "N=1000" => :darkred)
    ba_markers = Dict("N=100" => :utriangle,"N=200" => :dtriangle,"N=500" => :star5, "N=1000" => :pentagon)
    # Per-N interpolated η_c values (from sign-change analysis)
    ba_etac    = Dict("N=100" => 1.491, "N=200" => 1.863, "N=500" => 2.10, "N=1000" => 2.20)
    for (nkey, bdat) in sort(collect(ba_datasets), by=x->x[1])
        res = sort(bdat["results"], by=r -> r["eta"])
        c  = get(ba_colors,  nkey, :red)
        mk = get(ba_markers, nkey, :utriangle)
        ηc = get(ba_etac,    nkey, 1.5)
        plot!(
            [r["eta"] for r in res],
            [r["kappa_mean"] for r in res],
            color=c, linewidth=2, marker=mk, markersize=5,
            label="BA $nkey (η_c≈$(round(ηc, digits=2)))",
            ribbon=[r["kappa_std_ensemble"] for r in res],
            fillalpha=0.12,
        )
        vline!([ηc], color=c, linewidth=0.8, linestyle=:dot, label=nothing)
    end

    annotate!([
        (2.22+0.1, -0.25, text(L"\eta_c^\mathrm{reg}", 9, :steelblue, :left)),
        (1.90+0.1, -0.25, text(L"\eta_c^\mathrm{ER}", 9, :darkorange, :left)),
        (1.49+0.1, -0.25, text(L"\eta_c^\mathrm{BA}(100)", 8, :crimson, :left)),
        (1.863+0.05, 0.05, text(L"\eta_c^\mathrm{BA}(200)", 8, :red3, :left)),
    ])

    savefig(p, joinpath(FIGURES_DIR, "figure9_ba_comparison.pdf"))
    savefig(p, joinpath(FIGURES_DIR, "figure9_ba_comparison.png"))
    println("  Saved figure9_ba_comparison.{pdf,png}")
end

# ─────────────────────────────────────────────────────────────────
# Figure 10: Ricci Flow Trajectories
# ─────────────────────────────────────────────────────────────────

function figure10_ricci_flow()
    println("Generating Figure 10: Ricci Flow Trajectories...")

    exp_dir = joinpath(RESULTS_DIR, "experiments")

    # Color scheme by geometric regime (plain hex strings, no Colors.jl needed)
    regime_colors = Dict(
        "swow_nl"          => "#d62728",   # red — spherical
        "swow_es"          => "#1f77b4",   # blue — hyperbolic assoc
        "swow_en"          => "#4393c3",   # blue lighter
        "swow_zh"          => "#74c7e8",   # blue lightest
        "conceptnet_en"    => "#2ca02c",   # green — knowledge
        "conceptnet_pt"    => "#74c476",   # green light
        "depression_min"   => "#9467bd",   # purple — clinical
        "wordnet_en"       => "#7f7f7f",   # gray — taxonomy
        "babelnet_ru"      => "#aec7e8",   # gray-blue
        "babelnet_ar"      => "#c7c7c7",   # light gray
    )
    regime_labels = Dict(
        "swow_nl"       => "SWOW-NL (Spherical)",
        "swow_en"       => "SWOW-EN (Sparse hyp.)",
        "swow_es"       => "SWOW-ES",
        "swow_zh"       => "SWOW-ZH",
        "conceptnet_en" => "ConceptNet-EN (Dense hyp.)",
        "conceptnet_pt" => "ConceptNet-PT",
        "depression_min"=> "Depression (Clinical)",
        "wordnet_en"    => "WordNet-EN (Euclidean)",
        "babelnet_ru"   => "BabelNet-RU",
        "babelnet_ar"   => "BabelNet-AR",
    )
    # Bold lines for representative networks
    bold_ids = Set(["swow_nl", "swow_en", "conceptnet_en"])

    p_kappa = plot(
        xlabel="Iteration t",
        ylabel=L"\bar{\kappa}(t)",
        title="Discrete Ricci Flow: Three Qualitative Regimes",
        legend=:outertopright,
        size=(900, 500),
        dpi=300,
        grid=true,
        gridstyle=:dash,
        gridalpha=0.3,
        framestyle=:box,
    )
    hline!([0.0], color=:black, linewidth=0.5, linestyle=:dash, label=nothing)

    p_gini = plot(
        xlabel="Iteration t",
        ylabel="Gini(t)",
        title="Edge Weight Inequality Under Flow",
        legend=:outertopright,
        size=(900, 400),
        dpi=300,
        grid=true,
        gridstyle=:dash,
        gridalpha=0.3,
        framestyle=:box,
        ylims=(0, 0.6),
    )

    for (net_id, net_color) in regime_colors
        f = joinpath(exp_dir, "ricci_flow_$(net_id).json")
        !isfile(f) && continue
        d = JSON.parsefile(f)
        traj = d["trajectory"]
        ts      = [pt["t"]          for pt in traj]
        kappas  = [pt["kappa_mean"] for pt in traj]
        ginis   = [pt["w_gini"]     for pt in traj]

        lw = net_id in bold_ids ? 2.5 : 1.2
        lbl = get(regime_labels, net_id, net_id)
        plot!(p_kappa, ts, kappas, color=net_color, linewidth=lw, label=lbl)
        plot!(p_gini,  ts, ginis,  color=net_color, linewidth=lw, label=lbl)
    end

    # Regime annotations on kappa plot
    annotate!(p_kappa, [(48, 0.08,  text("Spherical", 8, :crimson, :right)),
                         (48, -0.28, text("Sparse hyp.", 8, :steelblue, :right)),
                         (48, -0.24, text("Dense hyp.", 8, :green, :right))])

    combined = plot(p_kappa, p_gini, layout=(2,1), size=(900, 800), dpi=300)
    savefig(combined, joinpath(FIGURES_DIR, "figure10_ricci_flow.pdf"))
    savefig(combined, joinpath(FIGURES_DIR, "figure10_ricci_flow.png"))
    println("  Saved figure10_ricci_flow.{pdf,png}")
end

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
    figure8_analytical_boundary(data)
    figure9_ba_comparison()
    figure10_ricci_flow()
    figure11_powerlaw()

    println("\n", "="^70)
    println("All figures saved to: $FIGURES_DIR")
    println("="^70)
end

# ─────────────────────────────────────────────────────────────────
# Figure 11: Power-Law Decay of ORC with Embedding Dimension
# ─────────────────────────────────────────────────────────────────

function figure11_powerlaw()
    println("Generating Figure 11: Power-Law κ̄(d) Decay...")

    fit_file = joinpath(UNIFIED_DIR, "powerlaw_fit_kappa_d.json")
    if !isfile(fit_file)
        println("  No power-law fit data found — skipping figure 11")
        return
    end
    fit = JSON.parsefile(fit_file)

    dims = Int.(fit["dimensions_used"])

    # Also check for d=128
    d128_file = joinpath(RESULTS_DIR, "experiments", "hypercomplex_lp_n100_d128.json")
    has_d128 = isfile(d128_file)

    p = plot(
        xscale=:log10, yscale=:log10,
        xlabel=L"d\ \text{(embedding dimension)}",
        ylabel=L"\bar{\kappa}(d)",
        title=L"\bar{\kappa}(d) \sim A_k \cdot d^{-\beta}\ \text{across Cayley--Dickson tower}",
        legend=:topright,
        size=(750, 500),
        dpi=300,
        grid=true,
        gridstyle=:dash,
        gridalpha=0.3,
        framestyle=:box,
    )

    # Color ramp by k
    k_values = [p["k"] for p in fit["per_k"]]
    n_k = length(k_values)
    colors = cgrad(:viridis, n_k, categorical=true)

    for (i, kdata) in enumerate(fit["per_k"])
        k = kdata["k"]
        β = kdata["beta"]
        A = kdata["A"]
        kappas = [kdata["kappa_by_dim"][string(d)] for d in dims]

        # Add d=128 point if available
        plot_dims = copy(dims)
        plot_kappas = copy(kappas)
        if has_d128
            d128_data = JSON.parsefile(d128_file)
            for r in d128_data["results"]
                if r["k"] == k && !isnothing(r["kappa_mean"])
                    push!(plot_dims, 128)
                    push!(plot_kappas, Float64(r["kappa_mean"]))
                    break
                end
            end
        end

        scatter!(plot_dims, plot_kappas,
                 color=colors[i], markersize=4, markerstrokewidth=0,
                 label=nothing)

        # Fitted line
        d_range = range(minimum(dims) * 0.9, maximum(plot_dims) * 1.1, length=50)
        plot!(d_range, A .* d_range .^ (-β),
              color=colors[i], linewidth=1.2, linestyle=:dash, label=nothing)
    end

    # Annotate mean beta
    β_mean = fit["beta_mean"]
    β_std  = fit["beta_std"]
    annotate!(6.0, 0.06,
        text(@sprintf("\\bar{\\beta} = %.3f \\pm %.3f\nJL bound: \\beta = 0.5", β_mean, β_std),
             9, :left, :black))

    # JL reference slope (β=0.5) from k=8 intercept
    d_ref = range(4, 70, length=50)
    kappa_ref_anchor = 0.279  # k=8 at d=4
    plot!(d_ref, kappa_ref_anchor .* (d_ref ./ 4.0) .^ (-0.5),
          color=:black, linewidth=1.5, linestyle=:dot,
          label=L"\beta=0.5\ \text{(JL bound)}")

    savefig(p, joinpath(FIGURES_DIR, "figure11_powerlaw.pdf"))
    savefig(p, joinpath(FIGURES_DIR, "figure11_powerlaw.png"))
    println("  Saved figure11_powerlaw.{pdf,png}")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
