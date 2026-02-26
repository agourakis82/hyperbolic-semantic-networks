"""
N=1000 exact LP sweep — narrowed k values near predicted transition.

Finite-size scaling predicts η_c(1000) ≈ 3.71 - 14.23/√1000 ≈ 3.26
So k_c ≈ √(3.26 × 1000) ≈ 57. Sweep k ∈ {48, 50, 52, 54, 56, 58, 60, 62, 64, 66} with 3 seeds.
"""

include("exact_curvature_lp.jl")

function run_n1000()
    N = 1000
    # Narrowed k values around predicted transition (k_c ≈ 57)
    # Also include a few lower/higher for context
    k_values = [48, 50, 52, 54, 56, 58, 60, 62, 64, 66]
    # Filter for parity: N*k must be even. N=1000 is even, so all k work.
    seeds = [42, 137, 271]

    println("N=1000 sweep: k_values=$k_values, seeds=$seeds")
    println("Predicted η_c ≈ 3.26, k_c ≈ 57")

    results = run_sweep(N, k_values; seeds=seeds)

    output_dir = joinpath(@__DIR__, "..", "..", "results", "experiments")
    mkpath(output_dir)
    output_file = joinpath(output_dir, "phase_transition_exact_n1000.json")

    output_data = Dict(
        "experiment" => "phase_transition_exact_n1000",
        "method" => "exact_LP",
        "solver" => "HiGHS",
        "description" => "N=1000 sweep near predicted transition (3 seeds)",
        "alpha" => 0.5,
        "N_fixed" => N,
        "n_seeds" => length(seeds),
        "seeds" => seeds,
        "n_threads" => Threads.nthreads(),
        "results" => results
    )

    open(output_file, "w") do f
        JSON.print(f, output_data, 2)
    end

    println("\nSAVED: $output_file")

    # Quick summary
    println("\n--- N=1000 Transition Summary ---")
    for r in sort(results, by=r -> r["k_target"])
        sign = r["kappa_mean"] > 0 ? "+" : ""
        @printf("k=%d  η=%.3f  κ_ORC=%s%.6f  κ_LLY=%.6f  [%s]\n",
                r["k_target"], r["ratio"], sign, r["kappa_mean"], r["lly_kappa_mean"], r["geometry"])
    end

    # Find sign change
    sorted = sort(results, by=r -> r["ratio"])
    for i in 2:length(sorted)
        if sorted[i-1]["kappa_mean"] < 0 && sorted[i]["kappa_mean"] >= 0
            eta1 = sorted[i-1]["ratio"]
            eta2 = sorted[i]["ratio"]
            k1 = sorted[i-1]["kappa_mean"]
            k2 = sorted[i]["kappa_mean"]
            eta_c = eta1 + (0.0 - k1) * (eta2 - eta1) / (k2 - k1)
            @printf("\n*** SIGN CHANGE: between k=%d (η=%.3f) and k=%d (η=%.3f)\n",
                    sorted[i-1]["k_target"], eta1, sorted[i]["k_target"], eta2)
            @printf("*** Interpolated η_c ≈ %.3f (predicted: 3.26)\n", eta_c)
            break
        end
    end
end

run_n1000()
