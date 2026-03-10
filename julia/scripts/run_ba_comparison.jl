"""
Barabási-Albert G(N,m) ORC comparison at N=100 and N=500.

For each attachment parameter m, generate BA scale-free graphs and compute
exact ORC. Tests whether the phase transition generalizes from regular/ER
to degree-heterogeneous graphs, and which density parameter best predicts
the sign change:
  η  = ⟨k⟩²/N        (current — controls expected common neighbors)
  η' = ⟨k²⟩/N        (second moment — natural in percolation theory)
  η''= ⟨k(k-1)⟩/N    (excess degree — controls triangle formation)

Key hypothesis: BA graphs should show a sign change at LOWER η than regular
graphs due to degree heterogeneity. The excess-degree parameter η'' may
collapse regular, ER, and BA sign changes onto a single curve.
"""

include("exact_curvature_lp.jl")

using Graphs: barabasi_albert

function create_ba_graph(N::Int, m::Int; seed::Int=42)::SimpleGraph
    g = barabasi_albert(N, m; seed=seed)

    # Largest connected component (BA is always connected for m≥1, but be safe)
    ccs = connected_components(g)
    if length(ccs) > 1
        largest_cc = ccs[argmax(length.(ccs))]
        g = induced_subgraph(g, largest_cc)[1]
    end

    return g
end

"""Compute degree distribution statistics for a graph."""
function degree_stats(g::SimpleGraph)
    degs = Float64.(degree(g))
    k_mean = mean(degs)
    k_std = std(degs)
    k_max = maximum(degs)
    k_min = minimum(degs)
    k_second_moment = mean(degs .^ 2)
    k_excess = mean(degs .* (degs .- 1.0))
    return (k_mean=k_mean, k_std=k_std, k_max=k_max, k_min=k_min,
            k_second_moment=k_second_moment, k_excess=k_excess)
end

"""Stratify edge curvatures by endpoint degree class."""
function stratify_curvatures(g::SimpleGraph, kappas::Vector{Float64}, hub_threshold::Float64)
    edges_list = collect(edges(g))
    degs = degree(g)

    hub_hub = Float64[]
    hub_leaf = Float64[]
    leaf_leaf = Float64[]

    for (i, e) in enumerate(edges_list)
        du = degs[src(e)]
        dv = degs[dst(e)]
        u_hub = du > hub_threshold
        v_hub = dv > hub_threshold

        if u_hub && v_hub
            push!(hub_hub, kappas[i])
        elseif u_hub || v_hub
            push!(hub_leaf, kappas[i])
        else
            push!(leaf_leaf, kappas[i])
        end
    end

    return (hub_hub=hub_hub, hub_leaf=hub_leaf, leaf_leaf=leaf_leaf)
end

function run_ba_sweep(N::Int, m_values::Vector{Int}; seeds::Vector{Int}=[42],
                      alpha::Float64=0.5)
    println("="^70)
    println("BARABÁSI-ALBERT G(N,m) ORC SWEEP")
    println("N=$N, alpha=$alpha, seeds=$seeds")
    println("Threads: $(Threads.nthreads())")
    println("="^70)

    results = []

    for m in m_values
        @printf("\nm=%d  (expected <k> ≈ %d)\n", m, 2m)

        seed_results = Float64[]
        seed_lly_results = Float64[]
        seed_degree_stats = []
        last_kappas = Float64[]
        last_lly_kappas = Float64[]
        last_g = nothing
        last_strat = nothing

        for seed in seeds
            g = create_ba_graph(N, m; seed=seed)
            n_actual = nv(g)
            e_actual = ne(g)

            ds = degree_stats(g)

            start_time = time()
            kappas = compute_graph_curvature_exact(g; alpha=alpha)
            elapsed = time() - start_time

            lly_kappas = compute_graph_lly_curvature(g)

            kappa_mean = mean(kappas)
            lly_mean = mean(lly_kappas)
            push!(seed_results, kappa_mean)
            push!(seed_lly_results, lly_mean)
            push!(seed_degree_stats, ds)

            last_kappas = kappas
            last_lly_kappas = lly_kappas
            last_g = g

            # Stratify by hub/leaf
            hub_threshold = ds.k_mean + 2.0 * ds.k_std
            last_strat = stratify_curvatures(g, kappas, hub_threshold)

            @printf("  seed=%d: N=%d E=%d <k>=%.2f σ_k=%.2f k_max=%.0f κ_ORC=%.6f (%.1fs)\n",
                    seed, n_actual, e_actual, ds.k_mean, ds.k_std, ds.k_max, kappa_mean, elapsed)
        end

        ensemble_mean = mean(seed_results)
        ensemble_std = length(seed_results) > 1 ? std(seed_results) : 0.0
        lly_ensemble_mean = mean(seed_lly_results)
        lly_ensemble_std = length(seed_lly_results) > 1 ? std(seed_lly_results) : 0.0

        # Average degree stats across seeds
        avg_k_mean = mean([ds.k_mean for ds in seed_degree_stats])
        avg_k_std = mean([ds.k_std for ds in seed_degree_stats])
        avg_k_max = mean([ds.k_max for ds in seed_degree_stats])
        avg_k_min = mean([ds.k_min for ds in seed_degree_stats])
        avg_k2 = mean([ds.k_second_moment for ds in seed_degree_stats])
        avg_kk1 = mean([ds.k_excess for ds in seed_degree_stats])

        # Three density parameters
        eta = avg_k_mean^2 / N
        eta_prime = avg_k2 / N
        eta_double_prime = avg_kk1 / N

        if ensemble_mean < -0.05
            geometry = "HYPERBOLIC"
        elseif ensemble_mean > 0.05
            geometry = "SPHERICAL"
        else
            geometry = "EUCLIDEAN/TRANSITION"
        end

        # Stratified curvature means (from last seed)
        strat_hub_hub = isempty(last_strat.hub_hub) ? nothing : mean(last_strat.hub_hub)
        strat_hub_leaf = isempty(last_strat.hub_leaf) ? nothing : mean(last_strat.hub_leaf)
        strat_leaf_leaf = isempty(last_strat.leaf_leaf) ? nothing : mean(last_strat.leaf_leaf)

        push!(results, Dict(
            "m" => m,
            "N" => nv(last_g),
            "E" => ne(last_g),
            # Degree distribution
            "k_mean" => avg_k_mean,
            "k_std" => avg_k_std,
            "k_max" => avg_k_max,
            "k_min" => avg_k_min,
            "k_second_moment" => avg_k2,
            "k_excess" => avg_kk1,
            # Three density parameters
            "eta" => eta,
            "eta_prime" => eta_prime,
            "eta_double_prime" => eta_double_prime,
            # ORC results
            "kappa_mean" => ensemble_mean,
            "kappa_std_ensemble" => ensemble_std,
            "kappa_std_edges" => std(last_kappas),
            "kappa_min" => minimum(last_kappas),
            "kappa_max" => maximum(last_kappas),
            "kappa_median" => median(last_kappas),
            "per_seed_kappa_means" => seed_results,
            # LLY
            "lly_kappa_mean" => lly_ensemble_mean,
            "lly_kappa_std_ensemble" => lly_ensemble_std,
            "per_seed_lly_means" => seed_lly_results,
            # Stratified curvature
            "kappa_hub_hub" => strat_hub_hub,
            "kappa_hub_leaf" => strat_hub_leaf,
            "kappa_leaf_leaf" => strat_leaf_leaf,
            "n_hub_hub_edges" => length(last_strat.hub_hub),
            "n_hub_leaf_edges" => length(last_strat.hub_leaf),
            "n_leaf_leaf_edges" => length(last_strat.leaf_leaf),
            # Clustering
            "clustering" => Graphs.global_clustering_coefficient(last_g),
            # Meta
            "geometry" => geometry,
            "n_seeds" => length(seeds)
        ))

        @printf("  ENSEMBLE: κ_ORC=%+.6f ± %.6f  η=%.3f  η'=%.3f  η''=%.3f  [%s]\n",
                ensemble_mean, ensemble_std, eta, eta_prime, eta_double_prime, geometry)
        if strat_hub_hub !== nothing
            @printf("  STRATIFIED: hub-hub=%+.4f (%d)  hub-leaf=%+.4f (%d)  leaf-leaf=%+.4f (%d)\n",
                    strat_hub_hub, length(last_strat.hub_hub),
                    something(strat_hub_leaf, NaN), length(last_strat.hub_leaf),
                    something(strat_leaf_leaf, NaN), length(last_strat.leaf_leaf))
        end
    end

    return results
end

function find_sign_change(results, eta_key::String)
    sorted = sort(results, by=r -> r[eta_key])
    for i in 2:length(sorted)
        if sorted[i-1]["kappa_mean"] < 0 && sorted[i]["kappa_mean"] >= 0
            eta1 = sorted[i-1][eta_key]
            eta2 = sorted[i][eta_key]
            k1 = sorted[i-1]["kappa_mean"]
            k2 = sorted[i]["kappa_mean"]
            eta_c = eta1 + (0.0 - k1) * (eta2 - eta1) / (k2 - k1)
            return (m1=sorted[i-1]["m"], m2=sorted[i]["m"],
                    eta1=eta1, eta2=eta2, eta_c=eta_c)
        end
    end
    return nothing
end

function run_ba_comparison(; N::Int=100)
    m_values = [2, 3, 4, 5, 6, 8, 10, 12, 15, 20]
    seeds = [42, 137, 271, 314, 577, 691, 823, 967, 1049, 1153]

    println("Barabási-Albert comparison: N=$N, m_values=$m_values")
    println("Using $(length(seeds)) seeds for statistical power")

    results = run_ba_sweep(N, m_values; seeds=seeds)

    output_dir = joinpath(@__DIR__, "..", "..", "results", "experiments")
    mkpath(output_dir)
    output_file = joinpath(output_dir, "ba_comparison_n$(N).json")

    output_data = Dict(
        "experiment" => "barabasi_albert_comparison_n$(N)",
        "method" => "exact_LP",
        "solver" => "HiGHS",
        "graph_model" => "Barabási-Albert G(N,m) preferential attachment",
        "description" => "BA scale-free comparison with 3 density parameters (10 seeds)",
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

    # Summary table
    println("\n--- Barabási-Albert ORC Summary (N=$N) ---")
    println("m\t<k>\tσ_k\tη\tη'\tη''\tC\tκ_ORC\t\tgeometry")
    for r in sort(results, by=r -> r["m"])
        @printf("%d\t%.1f\t%.1f\t%.3f\t%.3f\t%.3f\t%.3f\t%+.6f\t%s\n",
                r["m"], r["k_mean"], r["k_std"], r["eta"], r["eta_prime"],
                r["eta_double_prime"], r["clustering"], r["kappa_mean"], r["geometry"])
    end

    # Find sign changes for each density parameter
    println("\n--- Sign Change Analysis ---")
    for (name, key) in [("η = <k>²/N", "eta"), ("η' = <k²>/N", "eta_prime"),
                         ("η'' = <k(k-1)>/N", "eta_double_prime")]
        sc = find_sign_change(results, key)
        if sc !== nothing
            @printf("%s: sign change between m=%d (%s=%.3f) and m=%d (%s=%.3f)\n",
                    name, sc.m1, key, sc.eta1, sc.m2, key, sc.eta2)
            @printf("  Interpolated %s_c(BA, N=%d) ≈ %.3f\n", key, N, sc.eta_c)
        else
            @printf("%s: no sign change found in range\n", name)
        end
    end

    # Comparison with regular and ER
    println("\n--- Cross-Model Comparison (N=$N) ---")
    sc_eta = find_sign_change(results, "eta")
    if sc_eta !== nothing
        @printf("η_c(BA)      ≈ %.3f\n", sc_eta.eta_c)
    end
    @printf("η_c(ER)      ≈ 1.90  (from er_comparison_n100.json)\n")
    @printf("η_c(regular) ≈ 2.22  (from phase_transition_pure_julia.json)\n")

    # Stratified curvature summary
    println("\n--- Stratified Curvature (last seed) ---")
    println("m\thub-hub\t\thub-leaf\tleaf-leaf")
    for r in sort(results, by=r -> r["m"])
        hh = r["kappa_hub_hub"] === nothing ? "N/A" : @sprintf("%+.4f (%d)", r["kappa_hub_hub"], r["n_hub_hub_edges"])
        hl = r["kappa_hub_leaf"] === nothing ? "N/A" : @sprintf("%+.4f (%d)", r["kappa_hub_leaf"], r["n_hub_leaf_edges"])
        ll = r["kappa_leaf_leaf"] === nothing ? "N/A" : @sprintf("%+.4f (%d)", r["kappa_leaf_leaf"], r["n_leaf_leaf_edges"])
        @printf("%d\t%s\t%s\t%s\n", r["m"], hh, hl, ll)
    end
end

# Run N=100 by default
run_ba_comparison(N=100)
