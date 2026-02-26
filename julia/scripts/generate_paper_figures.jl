"""
PUBLICATION FIGURES for ORC Phase Transition Manuscript

Generates three figures for the paper:
  Figure 1: Phase transition (κ̄ vs η) with 95% CI error bars, multi-N overlay
  Figure 2: Sinkhorn vs Exact comparison (dual panel)
  Figure 3: (a) Curvature concentration (σ vs η), (b) Critical point scaling (η_c vs N)

Usage:
    julia generate_paper_figures.jl
"""

import Pkg
let deps = Pkg.project().dependencies
    for pkg in ["JSON", "Plots", "Distributions", "LaTeXStrings"]
        if !haskey(deps, pkg)
            Pkg.add(pkg)
        end
    end
end

using JSON
using Statistics
using Distributions
using Plots
using LaTeXStrings
using Printf

# Publication styling
default(
    fontfamily="Computer Modern",
    titlefontsize=12,
    guidefontsize=11,
    tickfontsize=9,
    legendfontsize=9,
    dpi=300,
    size=(600, 400)
)

results_dir = joinpath(@__DIR__, "..", "..", "results", "experiments")
figures_dir = joinpath(@__DIR__, "..", "..", "figures", "paper")
mkpath(figures_dir)

function load_json(filename)
    filepath = joinpath(results_dir, filename)
    if !isfile(filepath)
        error("File not found: $filepath")
    end
    return JSON.parsefile(filepath)
end

# ─────────────────────────────────────────────────────────────────
# Figure 1: Phase transition plot with error bars
# ─────────────────────────────────────────────────────────────────

function figure1_phase_transition()
    println("Generating Figure 1: Phase transition plot...")

    # Try v2, fall back to v1
    multi_file = isfile(joinpath(results_dir, "phase_transition_exact_multi_N_v2.json")) ?
        "phase_transition_exact_multi_N_v2.json" : "phase_transition_exact_multi_N.json"
    n100_file = isfile(joinpath(results_dir, "phase_transition_exact_n100_v2.json")) ?
        "phase_transition_exact_n100_v2.json" : "phase_transition_exact_n100.json"

    p = plot(xlabel=L"\eta = k^2/N", ylabel=L"\bar{\kappa}",
             title="Phase Transition in Mean ORC",
             legend=:bottomright, grid=true, gridalpha=0.3)

    # Horizontal line at κ=0
    hline!(p, [0.0], color=:black, linestyle=:dash, linewidth=0.8, label="")

    # Shaded regions
    plot!(p, [0, 20], [0, 0], fillrange=-0.5, fillalpha=0.05, fillcolor=:blue,
          linewidth=0, label="")
    plot!(p, [0, 20], [0, 0], fillrange=0.5, fillalpha=0.05, fillcolor=:red,
          linewidth=0, label="")

    # Markers and colors for different N
    markers = [:circle, :square, :diamond, :utriangle]
    colors = [:royalblue, :crimson, :forestgreen, :darkorange]

    # Plot multi-N data
    if isfile(joinpath(results_dir, multi_file))
        multi_data = load_json(multi_file)
        multi_results = multi_data["results"]

        for (idx, key) in enumerate(sort(collect(keys(multi_results))))
            N = parse(Int, replace(key, "N=" => ""))
            results = sort(multi_results[key], by=r -> r["ratio"])

            etas = Float64[r["ratio"] for r in results]
            kappas = Float64[r["kappa_mean"] for r in results]

            # Compute error bars from per-seed data if available
            errors = Float64[]
            for r in results
                if haskey(r, "per_seed_kappa_means")
                    per_seed = Float64.(r["per_seed_kappa_means"])
                    n = length(per_seed)
                    if n >= 2
                        t_crit = quantile(TDist(n - 1), 0.975)
                        push!(errors, t_crit * std(per_seed) / sqrt(n))
                    else
                        push!(errors, 0.0)
                    end
                else
                    push!(errors, r["kappa_std_ensemble"])
                end
            end

            c = idx <= length(colors) ? colors[idx] : :gray
            m = idx <= length(markers) ? markers[idx] : :circle

            plot!(p, etas, kappas, yerr=errors,
                  marker=m, markersize=4, color=c, linewidth=1.5,
                  markerstrokewidth=0.5, label="N=$N")
        end
    else
        # Fall back to N=100 only
        n100_data = load_json(n100_file)
        results = sort(n100_data["results"], by=r -> r["ratio"])

        etas = Float64[r["ratio"] for r in results]
        kappas = Float64[r["kappa_mean"] for r in results]
        errors = Float64[r["kappa_std_ensemble"] for r in results]

        plot!(p, etas, kappas, yerr=errors,
              marker=:circle, markersize=4, color=:royalblue, linewidth=1.5,
              label="N=100")
    end

    # Overlay ER data if available
    er_file = "er_comparison_n100.json"
    if isfile(joinpath(results_dir, er_file))
        er_data = load_json(er_file)
        er_results = sort(er_data["results"], by=r -> r["ratio"])

        er_etas = Float64[r["ratio"] for r in er_results]
        er_kappas = Float64[r["kappa_mean"] for r in er_results]
        er_errors = Float64[]
        for r in er_results
            if haskey(r, "per_seed_kappa_means")
                per_seed = Float64.(r["per_seed_kappa_means"])
                n = length(per_seed)
                if n >= 2
                    t_crit = quantile(TDist(n - 1), 0.975)
                    push!(er_errors, t_crit * std(per_seed) / sqrt(n))
                else
                    push!(er_errors, 0.0)
                end
            else
                push!(er_errors, r["kappa_std_ensemble"])
            end
        end

        plot!(p, er_etas, er_kappas, yerr=er_errors,
              marker=:star5, markersize=5, color=:purple, linewidth=1.5,
              linestyle=:dash, markerstrokewidth=0.5, label="ER (N=100)")
    end

    xlims!(p, (-0.5, 17))
    ylims!(p, (-0.45, 0.25))

    # Add annotation for transition region
    annotate!(p, 2.5, -0.38, text(L"\eta_c \approx 2.5", 9, :center))

    savefig(p, joinpath(figures_dir, "figure1_phase_transition.pdf"))
    savefig(p, joinpath(figures_dir, "figure1_phase_transition.png"))
    println("  Saved: figure1_phase_transition.{pdf,png}")
end

# ─────────────────────────────────────────────────────────────────
# Figure 2: Sinkhorn vs Exact comparison
# ─────────────────────────────────────────────────────────────────

function figure2_sinkhorn_comparison()
    println("Generating Figure 2: Sinkhorn vs Exact comparison...")

    comp_file = "sinkhorn_vs_exact_comparison.json"
    if !isfile(joinpath(results_dir, comp_file))
        println("  WARNING: Sinkhorn comparison file not found, skipping Figure 2")
        return
    end

    comp_data = load_json(comp_file)

    # Extract per-k data
    per_k = sort(comp_data["per_k"], by=r -> r["k"])
    ks = Int[r["k"] for r in per_k]
    etas = Float64[r["ratio"] for r in per_k]
    kappa_sinkhorn = Float64[r["kappa_sinkhorn"] for r in per_k]
    kappa_exact = Float64[r["kappa_exact"] for r in per_k]
    bias = Float64[r["bias"] for r in per_k]

    # Left panel: Overlay curves
    p1 = plot(xlabel=L"\eta = k^2/N", ylabel=L"\bar{\kappa}",
              title="ORC: Sinkhorn vs Exact LP", legend=:bottomright,
              grid=true, gridalpha=0.3)
    hline!(p1, [0.0], color=:black, linestyle=:dash, linewidth=0.8, label="")
    plot!(p1, etas, kappa_exact, marker=:circle, markersize=4,
          color=:royalblue, linewidth=1.5, label="Exact LP")
    plot!(p1, etas, kappa_sinkhorn, marker=:diamond, markersize=4,
          color=:coral, linewidth=1.5, linestyle=:dash, label="Sinkhorn (ε=0.01)")

    # Right panel: Bias
    p2 = plot(xlabel=L"\eta = k^2/N", ylabel=L"\Delta\kappa",
              title="Sinkhorn Bias", legend=false,
              grid=true, gridalpha=0.3)
    hline!(p2, [0.0], color=:black, linestyle=:dash, linewidth=0.8)
    bar!(p2, etas, bias, bar_width=0.3, color=:slategray, alpha=0.7)

    # Add summary text
    bias_mean = comp_data["bias_mean"]
    bias_max = comp_data["bias_max"]
    annotate!(p2, 10.0, maximum(abs.(bias)) * 0.8,
              text(@sprintf("mean = %.3f\nmax|Δ| = %.3f", bias_mean, bias_max), 8, :center))

    p = plot(p1, p2, layout=(1, 2), size=(900, 350))

    savefig(p, joinpath(figures_dir, "figure2_sinkhorn_comparison.pdf"))
    savefig(p, joinpath(figures_dir, "figure2_sinkhorn_comparison.png"))
    println("  Saved: figure2_sinkhorn_comparison.{pdf,png}")
end

# ─────────────────────────────────────────────────────────────────
# Figure 3: Concentration + Critical point scaling
# ─────────────────────────────────────────────────────────────────

function figure3_concentration_and_scaling()
    println("Generating Figure 3: Concentration + Critical point scaling...")

    # Panel (a): Curvature concentration (σ_edges vs η)
    n100_file = isfile(joinpath(results_dir, "phase_transition_exact_n100_v2.json")) ?
        "phase_transition_exact_n100_v2.json" : "phase_transition_exact_n100.json"
    n100_data = load_json(n100_file)
    results = sort(n100_data["results"], by=r -> r["ratio"])

    etas = Float64[r["ratio"] for r in results]
    sigmas = Float64[r["kappa_std_edges"] for r in results]

    p1 = plot(xlabel=L"\eta = k^2/N", ylabel=L"\sigma_{\mathrm{edges}}",
              title="(a) Curvature Concentration (N=100)",
              legend=false, grid=true, gridalpha=0.3)
    plot!(p1, etas, sigmas, marker=:circle, markersize=4,
          color=:royalblue, linewidth=1.5)

    # Panel (b): Critical point scaling
    multi_file = isfile(joinpath(results_dir, "phase_transition_exact_multi_N_v2.json")) ?
        "phase_transition_exact_multi_N_v2.json" : "phase_transition_exact_multi_N.json"

    p2 = plot(xlabel=L"1/\sqrt{N}", ylabel=L"\eta_c",
              title="(b) Critical Point Scaling",
              legend=:topright, grid=true, gridalpha=0.3)

    if isfile(joinpath(results_dir, multi_file))
        multi_data = load_json(multi_file)
        multi_results = multi_data["results"]

        N_vals = Float64[]
        eta_c_vals = Float64[]

        for key in sort(collect(keys(multi_results)))
            N = parse(Int, replace(key, "N=" => ""))
            results_n = multi_results[key]

            # Find sign change
            sorted = sort(results_n, by=r -> r["ratio"])
            for i in 2:length(sorted)
                if sorted[i-1]["kappa_mean"] < 0 && sorted[i]["kappa_mean"] >= 0
                    eta1 = sorted[i-1]["ratio"]
                    eta2 = sorted[i]["ratio"]
                    k1 = sorted[i-1]["kappa_mean"]
                    k2 = sorted[i]["kappa_mean"]
                    eta_c = eta1 + (0.0 - k1) * (eta2 - eta1) / (k2 - k1)
                    push!(N_vals, Float64(N))
                    push!(eta_c_vals, eta_c)
                    break
                end
            end
        end

        # Also include N=1000 data if available
        n1000_file = "phase_transition_exact_n1000.json"
        if isfile(joinpath(results_dir, n1000_file))
            n1000_data = load_json(n1000_file)
            n1000_results = n1000_data["results"]
            sorted = sort(n1000_results, by=r -> r["ratio"])
            for i in 2:length(sorted)
                if sorted[i-1]["kappa_mean"] < 0 && sorted[i]["kappa_mean"] >= 0
                    eta1 = sorted[i-1]["ratio"]
                    eta2 = sorted[i]["ratio"]
                    k1 = sorted[i-1]["kappa_mean"]
                    k2 = sorted[i]["kappa_mean"]
                    eta_c = eta1 + (0.0 - k1) * (eta2 - eta1) / (k2 - k1)
                    push!(N_vals, 1000.0)
                    push!(eta_c_vals, eta_c)
                    break
                end
            end
        end

        if !isempty(N_vals)
            # Sort by N
            perm = sortperm(N_vals)
            N_vals = N_vals[perm]
            eta_c_vals = eta_c_vals[perm]

            inv_sqrt_N = 1.0 ./ sqrt.(N_vals)
            scatter!(p2, inv_sqrt_N, eta_c_vals,
                     marker=:circle, markersize=6, color=:crimson,
                     label="Data (N=50–1000)")

            # Fit line if enough points
            if length(N_vals) >= 3
                x = inv_sqrt_N
                y = eta_c_vals
                x_mean = mean(x)
                y_mean = mean(y)
                beta1 = sum((x .- x_mean) .* (y .- y_mean)) / sum((x .- x_mean).^2)
                beta0 = y_mean - beta1 * x_mean

                x_fit = range(0, maximum(x) * 1.1, length=50)
                y_fit = beta0 .+ beta1 .* x_fit

                plot!(p2, collect(x_fit), collect(y_fit),
                      color=:crimson, linewidth=1.5, linestyle=:dash,
                      label=@sprintf("η_c^∞ = %.2f (R²=%.3f)", beta0,
                            1.0 - sum((y .- (beta0 .+ beta1 .* x)).^2) / sum((y .- mean(y)).^2)))
            end
        end
    end

    p = plot(p1, p2, layout=(1, 2), size=(900, 350))

    savefig(p, joinpath(figures_dir, "figure3_concentration_scaling.pdf"))
    savefig(p, joinpath(figures_dir, "figure3_concentration_scaling.png"))
    println("  Saved: figure3_concentration_scaling.{pdf,png}")
end

# ─────────────────────────────────────────────────────────────────
# Figure 4: Erdős-Rényi vs Regular comparison
# ─────────────────────────────────────────────────────────────────

function figure4_er_comparison()
    println("Generating Figure 4: ER vs Regular comparison...")

    er_file = "er_comparison_n100.json"
    if !isfile(joinpath(results_dir, er_file))
        println("  WARNING: ER comparison file not found, skipping Figure 4")
        return
    end

    n100_file = isfile(joinpath(results_dir, "phase_transition_exact_n100_v2.json")) ?
        "phase_transition_exact_n100_v2.json" : "phase_transition_exact_n100.json"

    er_data = load_json(er_file)
    n100_data = load_json(n100_file)

    er_results = sort(er_data["results"], by=r -> r["ratio"])
    reg_results = sort(n100_data["results"], by=r -> r["ratio"])

    # Left panel: Overlay of ER and regular curves
    p1 = plot(xlabel=L"\eta = k^2/N", ylabel=L"\bar{\kappa}",
              title="(a) ER vs Regular (N=100)",
              legend=:bottomright, grid=true, gridalpha=0.3)
    hline!(p1, [0.0], color=:black, linestyle=:dash, linewidth=0.8, label="")

    # Regular
    reg_etas = Float64[r["ratio"] for r in reg_results]
    reg_kappas = Float64[r["kappa_mean"] for r in reg_results]
    reg_errors = Float64[]
    for r in reg_results
        if haskey(r, "per_seed_kappa_means")
            per_seed = Float64.(r["per_seed_kappa_means"])
            n = length(per_seed)
            if n >= 2
                t_crit = quantile(TDist(n - 1), 0.975)
                push!(reg_errors, t_crit * std(per_seed) / sqrt(n))
            else
                push!(reg_errors, 0.0)
            end
        else
            push!(reg_errors, r["kappa_std_ensemble"])
        end
    end

    plot!(p1, reg_etas, reg_kappas, yerr=reg_errors,
          marker=:circle, markersize=4, color=:royalblue, linewidth=1.5,
          markerstrokewidth=0.5, label="k-regular")

    # ER
    er_etas = Float64[r["ratio"] for r in er_results]
    er_kappas = Float64[r["kappa_mean"] for r in er_results]
    er_errors = Float64[]
    for r in er_results
        if haskey(r, "per_seed_kappa_means")
            per_seed = Float64.(r["per_seed_kappa_means"])
            n = length(per_seed)
            if n >= 2
                t_crit = quantile(TDist(n - 1), 0.975)
                push!(er_errors, t_crit * std(per_seed) / sqrt(n))
            else
                push!(er_errors, 0.0)
            end
        else
            push!(er_errors, r["kappa_std_ensemble"])
        end
    end

    plot!(p1, er_etas, er_kappas, yerr=er_errors,
          marker=:diamond, markersize=4, color=:coral, linewidth=1.5,
          linestyle=:dash, markerstrokewidth=0.5, label="G(N,p)")

    xlims!(p1, (-0.5, 17))
    ylims!(p1, (-0.45, 0.25))

    # Right panel: Per-k difference (ER - regular)
    p2 = plot(xlabel=L"\eta = k^2/N", ylabel=L"\Delta\bar{\kappa} = \kappa_{\mathrm{ER}} - \kappa_{\mathrm{reg}}",
              title="(b) ER − Regular Difference",
              legend=false, grid=true, gridalpha=0.3)
    hline!(p2, [0.0], color=:black, linestyle=:dash, linewidth=0.8)

    # Compute deltas at common k values
    common_etas = Float64[]
    deltas = Float64[]
    for er_r in er_results
        k = er_r["k_target"]
        reg_r = filter(r -> r["k_target"] == k, reg_results)
        if !isempty(reg_r)
            push!(common_etas, er_r["ratio"])
            push!(deltas, er_r["kappa_mean"] - reg_r[1]["kappa_mean"])
        end
    end

    bar!(p2, common_etas, deltas, bar_width=0.3, color=:mediumpurple, alpha=0.7)

    p = plot(p1, p2, layout=(1, 2), size=(900, 350))

    savefig(p, joinpath(figures_dir, "figure4_er_comparison.pdf"))
    savefig(p, joinpath(figures_dir, "figure4_er_comparison.png"))
    println("  Saved: figure4_er_comparison.{pdf,png}")
end

# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────

function main()
    println("="^70)
    println("GENERATING PUBLICATION FIGURES")
    println("="^70)

    figure1_phase_transition()
    figure2_sinkhorn_comparison()
    figure3_concentration_and_scaling()
    figure4_er_comparison()

    println("\n", "="^70)
    println("All figures saved to: $figures_dir")
    println("="^70)
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
