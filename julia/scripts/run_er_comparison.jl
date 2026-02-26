"""
Erdős-Rényi G(N,p) comparison at N=100.

For each k used in the regular graph sweep, generate G(100, p) with p = k/99
(so expected degree matches k). Compute exact ORC and LLY. This tests whether
the phase transition is specific to regular graphs or also appears in ER graphs.

Key hypothesis: ER graphs should show a similar sign change in κ̄_ORC near the
same η = k²/N threshold, but with higher variance due to degree heterogeneity.
"""

include("exact_curvature_lp.jl")

using Graphs: erdos_renyi

function create_er_graph(N::Int, p::Float64; seed::Int=42)::SimpleGraph
    Random.seed!(seed)
    g = erdos_renyi(N, p)

    # Largest connected component (same treatment as regular graphs)
    ccs = connected_components(g)
    if length(ccs) > 1
        largest_cc = ccs[argmax(length.(ccs))]
        g = induced_subgraph(g, largest_cc)[1]
    end

    return g
end

function run_er_sweep(N::Int, k_values::Vector{Int}; seeds::Vector{Int}=[42],
                      alpha::Float64=0.5)
    println("="^70)
    println("ERDŐS-RÉNYI G(N,p) COMPARISON SWEEP")
    println("N=$N, alpha=$alpha, seeds=$seeds")
    println("Threads: $(Threads.nthreads())")
    println("="^70)

    results = []

    for k in k_values
        p = k / (N - 1)
        ratio = k^2 / N
        @printf("\nk=%d  p=%.4f  (expected η=k²/N=%.3f)\n", k, p, ratio)

        seed_results = Float64[]
        seed_lly_results = Float64[]
        seed_k_actual = Float64[]
        last_kappas = Float64[]
        last_lly_kappas = Float64[]
        last_g = nothing

        for seed in seeds
            g = create_er_graph(N, p; seed=seed)
            n_actual = nv(g)
            e_actual = ne(g)
            k_actual = 2.0 * e_actual / n_actual

            start_time = time()
            kappas = compute_graph_curvature_exact(g; alpha=alpha)
            elapsed = time() - start_time

            lly_kappas = compute_graph_lly_curvature(g)

            kappa_mean = mean(kappas)
            lly_mean = mean(lly_kappas)
            push!(seed_results, kappa_mean)
            push!(seed_lly_results, lly_mean)
            push!(seed_k_actual, k_actual)

            last_kappas = kappas
            last_lly_kappas = lly_kappas
            last_g = g

            @printf("  seed=%d: N=%d E=%d <k>=%.2f κ_ORC=%.6f κ_LLY=%.6f (%.1fs)\n",
                    seed, n_actual, e_actual, k_actual, kappa_mean, lly_mean, elapsed)
        end

        ensemble_mean = mean(seed_results)
        ensemble_std = length(seed_results) > 1 ? std(seed_results) : 0.0
        lly_ensemble_mean = mean(seed_lly_results)
        lly_ensemble_std = length(seed_lly_results) > 1 ? std(seed_lly_results) : 0.0
        k_actual_mean = mean(seed_k_actual)

        if ensemble_mean < -0.05
            geometry = "HYPERBOLIC"
        elseif ensemble_mean > 0.05
            geometry = "SPHERICAL"
        else
            geometry = "EUCLIDEAN/TRANSITION"
        end

        push!(results, Dict(
            "k_target" => k,
            "p" => p,
            "k_actual_mean" => k_actual_mean,
            "N" => nv(last_g),
            "E" => ne(last_g),
            "ratio" => ratio,
            "ratio_actual" => k_actual_mean^2 / N,
            "kappa_mean" => ensemble_mean,
            "kappa_std_ensemble" => ensemble_std,
            "kappa_std_edges" => std(last_kappas),
            "kappa_min" => minimum(last_kappas),
            "kappa_max" => maximum(last_kappas),
            "kappa_median" => median(last_kappas),
            "per_seed_kappa_means" => seed_results,
            "per_seed_k_actual" => seed_k_actual,
            "lly_kappa_mean" => lly_ensemble_mean,
            "lly_kappa_std_ensemble" => lly_ensemble_std,
            "lly_kappa_std_edges" => std(last_lly_kappas),
            "per_seed_lly_means" => seed_lly_results,
            "geometry" => geometry,
            "n_seeds" => length(seeds)
        ))

        @printf("  ENSEMBLE: κ_ORC=%.6f ± %.6f  κ_LLY=%.6f ± %.6f  [%s]\n",
                ensemble_mean, ensemble_std, lly_ensemble_mean, lly_ensemble_std, geometry)
    end

    return results
end

function run_er_comparison()
    N = 100
    # Same k values as regular graph sweep for direct comparison
    k_values = [2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 25, 30, 35, 40]
    seeds = [42, 137, 271, 314, 577, 691, 823, 967, 1049, 1153]

    println("Erdős-Rényi comparison: N=$N, k_values=$k_values")
    println("Using $(length(seeds)) seeds for statistical power")

    results = run_er_sweep(N, k_values; seeds=seeds)

    output_dir = joinpath(@__DIR__, "..", "..", "results", "experiments")
    mkpath(output_dir)
    output_file = joinpath(output_dir, "er_comparison_n100.json")

    output_data = Dict(
        "experiment" => "erdos_renyi_comparison_n100",
        "method" => "exact_LP",
        "solver" => "HiGHS",
        "graph_model" => "Erdős-Rényi G(N,p) with p=k/(N-1)",
        "description" => "ER comparison with same k values as regular graph sweep (10 seeds)",
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

    # Comparison summary
    println("\n--- Erdős-Rényi vs Regular Graph Comparison ---")
    println("k\tη\tκ_ORC_ER\tκ_LLY_ER\tgeometry")
    for r in sort(results, by=r -> r["k_target"])
        @printf("%d\t%.2f\t%+.6f\t%+.6f\t%s\n",
                r["k_target"], r["ratio"], r["kappa_mean"], r["lly_kappa_mean"], r["geometry"])
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
            @printf("\n*** ER SIGN CHANGE: between k=%d (η=%.3f) and k=%d (η=%.3f)\n",
                    sorted[i-1]["k_target"], eta1, sorted[i]["k_target"], eta2)
            @printf("*** Interpolated η_c(ER) ≈ %.3f\n", eta_c)
            @printf("*** Compare with regular graph η_c ≈ 2.26 (N=100)\n")
            break
        end
    end
end

run_er_comparison()
