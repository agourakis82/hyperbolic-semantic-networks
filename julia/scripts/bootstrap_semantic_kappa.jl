#!/usr/bin/env julia
# Bootstrap 95% CIs for κ̄ on all 16 Paper 2 semantic networks.
# Uses precomputed per-edge curvatures — zero ORC re-computation.

using JSON, Statistics, Printf, Random

const PAPER2_NETWORKS = [
    "swow_es", "swow_en", "swow_zh", "swow_nl",
    "conceptnet_en", "conceptnet_pt",
    "wordnet_en", "wordnet_en_2k", "babelnet_ru", "babelnet_ar",
    "depression_minimum",
    "swow_rp", "eat_en", "usf_en", "wordnet_de", "framenet_en",
]

const N_BOOTSTRAP = 10_000
const RNG = MersenneTwister(42)

function bootstrap_ci(kappas::Vector{Float64}; n_boot=N_BOOTSTRAP, alpha=0.05)
    E = length(kappas)
    means = Vector{Float64}(undef, n_boot)
    for b in 1:n_boot
        s = 0.0
        for _ in 1:E
            s += kappas[rand(RNG, 1:E)]
        end
        means[b] = s / E
    end
    sort!(means)
    lo_idx = max(1, Int(floor(alpha / 2 * n_boot)))
    hi_idx = min(n_boot, Int(ceil((1 - alpha / 2) * n_boot)))
    return (
        mean = mean(kappas),
        se = std(means),
        ci_lo = means[lo_idx],
        ci_hi = means[hi_idx],
        boot_std = std(means),
        n_boot = n_boot,
    )
end

function jackknife_influence(kappas::Vector{Float64})
    E = length(kappas)
    full_mean = mean(kappas)
    total = sum(kappas)
    influences = [(total - kappas[i]) / (E - 1) - full_mean for i in 1:E]
    max_influence = maximum(abs.(influences))
    return (max_influence=max_influence, influence_std=std(influences))
end

function main()
    results_dir = joinpath(@__DIR__, "..", "..", "results", "unified")

    println("=" ^ 70)
    println("Bootstrap 95% CIs for κ̄ — 16 Semantic Networks")
    println("=" ^ 70)
    @printf("  %-20s  %7s  %7s  %7s   %s  %s\n",
            "Network", "κ̄", "SE", "boot_σ", "95% CI", "Regime")
    println("-" ^ 70)

    all_results = []

    for nid in PAPER2_NETWORKS
        path = joinpath(results_dir, "$(nid)_exact_lp.json")
        d = JSON.parsefile(path)
        kappas = Float64.(d["per_edge_curvatures"])

        b = bootstrap_ci(kappas)
        j = jackknife_influence(kappas)

        # Regime from CI
        if b.ci_lo > 0.0
            ci_regime = "SPHERICAL"
        elseif b.ci_hi < 0.0
            ci_regime = "HYPERBOLIC"
        else
            ci_regime = "UNCERTAIN"
        end

        push!(all_results, Dict(
            "network_id" => nid,
            "N" => d["N"],
            "E" => d["E"],
            "kappa_mean" => b.mean,
            "kappa_std" => d["kappa_std"],
            "se" => b.se,
            "ci_lo" => b.ci_lo,
            "ci_hi" => b.ci_hi,
            "boot_std" => b.boot_std,
            "n_boot" => b.n_boot,
            "ci_regime" => ci_regime,
            "jackknife_max_influence" => j.max_influence,
            "jackknife_influence_std" => j.influence_std,
            "eta" => d["eta"],
            "clustering" => d["clustering"],
        ))

        @printf("  %-20s  %+.4f  %.4f  %.4f   [%+.4f, %+.4f]  %s\n",
                nid, b.mean, b.se, b.boot_std, b.ci_lo, b.ci_hi, ci_regime)
    end

    # Key tests
    println("\n" * "=" ^ 70)
    println("Key Tests:")

    nl = findfirst(r -> r["network_id"] == "swow_nl", all_results)
    if nl !== nothing
        r = all_results[nl]
        pass = r["ci_lo"] > 0.0
        println("  Dutch SWOW CI entirely > 0: $(pass ? "PASS" : "FAIL") (CI_lo = $(r["ci_lo"]))")
    end

    fn = findfirst(r -> r["network_id"] == "framenet_en", all_results)
    if fn !== nothing
        r = all_results[fn]
        pass = r["ci_hi"] < 0.0
        println("  FrameNet CI entirely < 0:   $(pass ? "PASS" : "FAIL") (CI_hi = $(r["ci_hi"]))")
    end

    # Count uncertain
    n_uncertain = count(r -> r["ci_regime"] == "UNCERTAIN", all_results)
    println("  Networks with CI spanning 0: $n_uncertain/16")

    # Save
    output = Dict(
        "experiment" => "bootstrap_kappa_16",
        "n_bootstrap" => N_BOOTSTRAP,
        "seed" => 42,
        "alpha" => 0.05,
        "n_networks" => 16,
        "results" => all_results,
    )

    outpath = joinpath(results_dir, "bootstrap_kappa_16.json")
    open(outpath, "w") do f
        JSON.print(f, output, 2)
    end
    println("\nSaved: $outpath")
end

main()
