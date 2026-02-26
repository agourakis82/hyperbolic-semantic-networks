"""
COMPARISON: Sinkhorn vs Exact LP Curvature

Loads results from both methods and quantifies:
1. Systematic bias from Sinkhorn entropy regularization
2. Whether the critical point η_c shifts
3. Per-k error analysis
"""

using JSON
using Printf
using Statistics

function load_results(path::String)
    data = JSON.parsefile(path)
    results = data["results"]
    return sort(results, by=r -> r["k_target"])
end

function main()
    base = joinpath(@__DIR__, "..", "..", "results", "experiments")

    sinkhorn_file = joinpath(base, "phase_transition_julia_n100.json")
    exact_file = joinpath(base, "phase_transition_exact_n100.json")

    if !isfile(sinkhorn_file)
        println("ERROR: Sinkhorn results not found at $sinkhorn_file")
        return
    end
    if !isfile(exact_file)
        println("ERROR: Exact results not found at $exact_file")
        println("Run: julia exact_curvature_lp.jl")
        return
    end

    sinkhorn = load_results(sinkhorn_file)
    exact = load_results(exact_file)

    # Build lookup by k_target
    sink_by_k = Dict(r["k_target"] => r for r in sinkhorn)
    exact_by_k = Dict(r["k_target"] => r for r in exact)

    common_k = sort(collect(intersect(keys(sink_by_k), keys(exact_by_k))))

    println("="^80)
    println("COMPARISON: Sinkhorn (ε=0.01) vs Exact LP")
    println("="^80)
    println()

    @printf("%-4s  %-8s  %-12s  %-12s  %-10s  %-8s  %-8s\n",
            "k", "k²/N", "κ_sinkhorn", "κ_exact", "Δκ", "geom_S", "geom_E")
    println("-"^80)

    biases = Float64[]
    sign_changes_sink = 0
    sign_changes_exact = 0
    prev_sink = -1.0
    prev_exact = -1.0

    for k in common_k
        s = sink_by_k[k]
        e = exact_by_k[k]

        κ_s = s["kappa_mean"]
        κ_e = e["kappa_mean"]
        Δ = κ_e - κ_s
        push!(biases, Δ)

        # Detect sign changes
        if prev_sink < 0 && κ_s >= 0
            sign_changes_sink = k
        end
        if prev_exact < 0 && κ_e >= 0
            sign_changes_exact = k
        end
        prev_sink = κ_s
        prev_exact = κ_e

        @printf("%-4d  %-8.3f  %+12.6f  %+12.6f  %+10.6f  %-8s  %-8s\n",
                k, s["ratio"], κ_s, κ_e, Δ, s["geometry"], e["geometry"])
    end

    println("-"^80)
    println()

    # Statistics
    println("--- Bias Statistics ---")
    @printf("Mean bias (exact - sinkhorn):  %+.6f\n", mean(biases))
    @printf("Std  bias:                      %.6f\n", std(biases))
    @printf("Max  bias:                     %+.6f\n", maximum(abs.(biases)))
    println()

    # Critical point
    println("--- Critical Point ---")
    if sign_changes_sink > 0
        @printf("Sinkhorn sign change at k=%d  (k²/N=%.3f)\n",
                sign_changes_sink, sign_changes_sink^2/100)
    else
        println("Sinkhorn: no sign change detected")
    end
    if sign_changes_exact > 0
        @printf("Exact LP sign change at k=%d  (k²/N=%.3f)\n",
                sign_changes_exact, sign_changes_exact^2/100)
    else
        println("Exact LP: no sign change detected")
    end

    # Save comparison
    output_file = joinpath(base, "sinkhorn_vs_exact_comparison.json")
    comparison = Dict(
        "experiment" => "sinkhorn_vs_exact_comparison",
        "common_k_values" => common_k,
        "bias_mean" => mean(biases),
        "bias_std" => std(biases),
        "bias_max" => maximum(abs.(biases)),
        "sign_change_sinkhorn_k" => sign_changes_sink,
        "sign_change_exact_k" => sign_changes_exact,
        "per_k" => [Dict(
            "k" => k,
            "ratio" => sink_by_k[k]["ratio"],
            "kappa_sinkhorn" => sink_by_k[k]["kappa_mean"],
            "kappa_exact" => exact_by_k[k]["kappa_mean"],
            "bias" => exact_by_k[k]["kappa_mean"] - sink_by_k[k]["kappa_mean"]
        ) for k in common_k]
    )

    open(output_file, "w") do f
        JSON.print(f, comparison, 2)
    end
    println("\nSaved: $output_file")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
