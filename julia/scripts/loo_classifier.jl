#!/usr/bin/env julia
# LOO Cross-Validation of (η, C) Three-Regime Classifier
# Reads precomputed JSON results — zero ORC re-computation needed.

using JSON, Statistics, Printf

# ── 16 Paper 2 networks ──────────────────────────────────────────────
const PAPER2_NETWORKS = [
    # Training set (11)
    "swow_es", "swow_en", "swow_zh", "swow_nl",
    "conceptnet_en", "conceptnet_pt",
    "wordnet_en", "wordnet_en_2k", "babelnet_ru", "babelnet_ar",
    "depression_minimum",
    # Held-out test set (5)
    "swow_rp", "eat_en", "usf_en", "wordnet_de", "framenet_en",
]

# ── Finite-size scaling: η_c(N) = 3.75 − 14.62/√N ──────────────────
eta_c(N::Int) = 3.75 - 14.62 / sqrt(N)

# ── Load precomputed results ─────────────────────────────────────────
function load_network_data(results_dir::String)
    data = Dict{String, Dict{String, Any}}()
    for nid in PAPER2_NETWORKS
        path = joinpath(results_dir, "$(nid)_exact_lp.json")
        d = JSON.parsefile(path)
        data[nid] = d
    end
    return data
end

# ── True regime from ORC sign ────────────────────────────────────────
function true_regime(d::Dict)
    κ = d["kappa_mean"]
    if κ > 0.01
        return "SPHERICAL"
    elseif κ < -0.01
        return "HYPERBOLIC"
    else
        return "EUCLIDEAN"
    end
end

# ── Classify using (η, C, C*) ───────────────────────────────────────
function classify(η::Float64, C::Float64, N::Int, Cstar::Float64)
    if η > eta_c(N)
        return "SPHERICAL"
    elseif C > Cstar
        return "HYPERBOLIC"
    else
        return "EUCLIDEAN"
    end
end

# ── Grid search for optimal C* on a set of networks ─────────────────
function find_optimal_cstar(data::Dict, network_ids::Vector{String};
                            grid_min=0.005, grid_max=0.200, grid_step=0.005)
    best_acc = -1
    best_cstar = 0.05
    grid = grid_min:grid_step:grid_max
    for cstar in grid
        correct = 0
        for nid in network_ids
            d = data[nid]
            pred = classify(d["eta"], d["clustering"], d["N"], cstar)
            if pred == true_regime(d)
                correct += 1
            end
        end
        acc = correct / length(network_ids)
        if acc > best_acc || (acc == best_acc && abs(cstar - 0.05) < abs(best_cstar - 0.05))
            best_acc = acc
            best_cstar = cstar
        end
    end
    return best_cstar, best_acc
end

# ── Main ─────────────────────────────────────────────────────────────
function main()
    results_dir = joinpath(@__DIR__, "..", "..", "results", "unified")
    data = load_network_data(results_dir)

    println("=" ^ 70)
    println("LOO Cross-Validation of (η, C) Three-Regime Classifier")
    println("=" ^ 70)

    # ── LOO-16 ───────────────────────────────────────────────────────
    loo_results = []
    cstar_values = Float64[]

    for (i, left_out) in enumerate(PAPER2_NETWORKS)
        train_ids = [nid for nid in PAPER2_NETWORKS if nid != left_out]
        cstar, train_acc = find_optimal_cstar(data, train_ids)
        push!(cstar_values, cstar)

        d = data[left_out]
        pred = classify(d["eta"], d["clustering"], d["N"], cstar)
        actual = true_regime(d)
        correct = pred == actual

        push!(loo_results, Dict(
            "network_id" => left_out,
            "predicted" => pred,
            "actual" => actual,
            "correct" => correct,
            "cstar_fitted" => cstar,
            "train_accuracy" => train_acc,
            "eta" => d["eta"],
            "clustering" => d["clustering"],
            "N" => d["N"],
            "kappa_mean" => d["kappa_mean"],
        ))

        mark = correct ? "✓" : "✗"
        @printf("  %2d. %-20s  pred=%-11s actual=%-11s C*=%.3f  %s\n",
                i, left_out, pred, actual, cstar, mark)
    end

    loo_accuracy = count(r -> r["correct"], loo_results) / length(loo_results)
    cstar_mean = mean(cstar_values)
    cstar_std = std(cstar_values)
    cstar_min = minimum(cstar_values)
    cstar_max = maximum(cstar_values)

    println()
    @printf("LOO-16 accuracy: %d/%d = %.1f%%\n", count(r -> r["correct"], loo_results), 16, 100 * loo_accuracy)
    @printf("C* stability: mean=%.3f, std=%.3f, range=[%.3f, %.3f]\n", cstar_mean, cstar_std, cstar_min, cstar_max)

    # ── Confusion matrix ─────────────────────────────────────────────
    regimes = ["HYPERBOLIC", "EUCLIDEAN", "SPHERICAL"]
    println("\nConfusion Matrix (rows=actual, cols=predicted):")
    @printf("  %12s  %s  %s  %s\n", "", "HYP", "EUC", "SPH")
    for actual in regimes
        counts = [count(r -> r["actual"] == actual && r["predicted"] == pred, loo_results) for pred in regimes]
        @printf("  %12s  %3d  %3d  %3d\n", actual, counts...)
    end

    # ── Sensitivity: accuracy vs C* on full 16 ──────────────────────
    sensitivity = []
    for cstar in 0.005:0.005:0.200
        correct = 0
        for nid in PAPER2_NETWORKS
            d = data[nid]
            pred = classify(d["eta"], d["clustering"], d["N"], cstar)
            if pred == true_regime(d)
                correct += 1
            end
        end
        push!(sensitivity, Dict("cstar" => cstar, "accuracy" => correct / 16, "n_correct" => correct))
    end

    println("\nSensitivity: Accuracy vs C* (full 16 networks):")
    for s in sensitivity
        bar = "█" ^ Int(round(s["accuracy"] * 20))
        @printf("  C*=%.3f  acc=%.1f%%  %s\n", s["cstar"], 100 * s["accuracy"], bar)
    end

    # ── Misclassified networks ───────────────────────────────────────
    misclassified = [r for r in loo_results if !r["correct"]]
    if !isempty(misclassified)
        println("\nMisclassified networks:")
        for r in misclassified
            @printf("  %s: pred=%s, actual=%s (η=%.3f, C=%.3f, κ̄=%.3f)\n",
                    r["network_id"], r["predicted"], r["actual"],
                    r["eta"], r["clustering"], r["kappa_mean"])
        end
    end

    # ── Save ─────────────────────────────────────────────────────────
    output = Dict(
        "experiment" => "loo_classifier_16",
        "n_networks" => 16,
        "loo_accuracy" => loo_accuracy,
        "loo_correct" => count(r -> r["correct"], loo_results),
        "cstar_mean" => cstar_mean,
        "cstar_std" => cstar_std,
        "cstar_min" => cstar_min,
        "cstar_max" => cstar_max,
        "per_fold" => loo_results,
        "sensitivity" => sensitivity,
        "eta_c_formula" => "3.75 - 14.62/sqrt(N)",
    )

    outpath = joinpath(results_dir, "loo_classifier.json")
    open(outpath, "w") do f
        JSON.print(f, output, 2)
    end
    println("\nSaved: $outpath")
end

main()
