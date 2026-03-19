#!/usr/bin/env julia
# Behavioral Correlation: Per-node ORC vs Lexical Decision RT
# Uses BLP (British Lexicon Project) reaction times matched to SWOW-EN nodes.

using JSON, Statistics, Printf, CSV, DataFrames, Graphs

const RESULTS_DIR = joinpath(@__DIR__, "..", "..", "results", "unified")
const DATA_DIR = joinpath(@__DIR__, "..", "..", "data", "processed")

function main()
    # ── Load SWOW-EN edge list and build LCC graph ────────────────────
    edges_df = CSV.read(joinpath(DATA_DIR, "english_edges_FINAL.csv"), DataFrame; stringtype=String)
    all_nodes_raw = sort(unique(vcat(edges_df.source, edges_df.target)))
    node_to_id_raw = Dict(name => i for (i, name) in enumerate(all_nodes_raw))

    g_raw = SimpleGraph(length(all_nodes_raw))
    for row in eachrow(edges_df)
        u, v = node_to_id_raw[row.source], node_to_id_raw[row.target]
        u != v && add_edge!(g_raw, u, v)
    end
    # Extract LCC (same as unified_semantic_orc.jl)
    ccs = connected_components(g_raw)
    largest_cc = ccs[argmax(length.(ccs))]
    lcc_set = Set(sort(largest_cc))
    id_to_name_raw = Dict(i => name for (name, i) in node_to_id_raw)
    lcc_names = sort([id_to_name_raw[i] for i in largest_cc])
    N = length(lcc_names)

    # ── Load per-edge curvatures (ordered by Graphs.jl edge iterator) ─
    d = JSON.parsefile(joinpath(RESULTS_DIR, "swow_en_exact_lp.json"))
    per_edge_kappa = d["per_edge_curvatures"]

    # Build LCC graph with consistent node IDs
    lcc_node_to_id = Dict(name => i for (i, name) in enumerate(lcc_names))
    g_lcc = SimpleGraph(N)
    for row in eachrow(edges_df)
        haskey(lcc_node_to_id, row.source) || continue
        haskey(lcc_node_to_id, row.target) || continue
        u, v = lcc_node_to_id[row.source], lcc_node_to_id[row.target]
        u != v && add_edge!(g_lcc, u, v)
    end

    @printf("  LCC: N=%d, E=%d, per_edge_kappa=%d\n", N, ne(g_lcc), length(per_edge_kappa))

    # ── Compute per-node mean curvature ──────────────────────────────
    edge_list = collect(edges(g_lcc))
    node_kappas = Dict{String, Vector{Float64}}()
    for (i, e) in enumerate(edge_list)
        i > length(per_edge_kappa) && break
        κ = per_edge_kappa[i]
        for nid in [src(e), dst(e)]
            name = lcc_names[nid]
            if !haskey(node_kappas, name)
                node_kappas[name] = Float64[]
            end
            push!(node_kappas[name], κ)
        end
    end

    node_mean_kappa = Dict(n => mean(ks) for (n, ks) in node_kappas)
    node_degree = Dict(n => length(ks) for (n, ks) in node_kappas)
    all_nodes = lcc_names

    # ── Load BLP reaction times ──────────────────────────────────────
    blp_path = "/tmp/13428_2011_118_MOESM3_ESM/blp-items.txt"
    if !isfile(blp_path)
        error("BLP data not found at $blp_path. Download from Springer supplementary.")
    end
    blp_df = CSV.read(blp_path, DataFrame; delim='\t', stringtype=String, missingstring="NA")
    blp_words = filter(row -> row.lexicality == "W" && !ismissing(row.rt), blp_df)
    blp_rt = Dict(lowercase(String(row.spelling)) => Float64(row.rt) for row in eachrow(blp_words))
    blp_acc = Dict(lowercase(String(row.spelling)) => Float64(row.accuracy) for row in eachrow(blp_words))

    # ── Match nodes ──────────────────────────────────────────────────
    matched_nodes = String[]
    kappas = Float64[]
    rts = Float64[]
    degrees = Int[]
    word_lengths = Int[]
    accuracies = Float64[]

    for node in all_nodes
        lnode = lowercase(node)
        if haskey(blp_rt, lnode) && haskey(node_mean_kappa, node)
            push!(matched_nodes, node)
            push!(kappas, node_mean_kappa[node])
            push!(rts, blp_rt[lnode])
            push!(degrees, node_degree[node])
            push!(word_lengths, length(node))
            push!(accuracies, blp_acc[lnode])
        end
    end

    n_matched = length(matched_nodes)
    println("=" ^ 70)
    println("Behavioral Correlation: Per-Node ORC vs Lexical Decision RT")
    println("=" ^ 70)
    @printf("  SWOW-EN nodes: %d, BLP words: %d, Matched: %d (%.1f%%)\n",
            N, length(blp_rt), n_matched, 100 * n_matched / N)

    # ── Pearson correlation ──────────────────────────────────────────
    function pearson_r(x, y)
        n = length(x)
        mx, my = mean(x), mean(y)
        sx, sy = std(x), std(y)
        r = sum((x .- mx) .* (y .- my)) / ((n - 1) * sx * sy)
        # t-test for significance
        t = r * sqrt((n - 2) / (1 - r^2))
        # Approximate p-value (two-tailed, df = n-2)
        df = n - 2
        # Use normal approximation for large df
        p = 2 * exp(-0.5 * t^2) / sqrt(2π) * sqrt(df) / abs(t)  # rough
        return r, t, p
    end

    # ── Spearman rank correlation ────────────────────────────────────
    function spearman_rho(x, y)
        rx = sortperm(sortperm(x))
        ry = sortperm(sortperm(y))
        return pearson_r(Float64.(rx), Float64.(ry))
    end

    println("\n── Raw Correlations ──")
    r_raw, t_raw, _ = pearson_r(kappas, rts)
    rho_raw, _, _ = spearman_rho(kappas, rts)
    @printf("  Pearson r(κ, RT)  = %+.4f  (t = %.2f, n = %d)\n", r_raw, t_raw, n_matched)
    @printf("  Spearman ρ(κ, RT) = %+.4f\n", rho_raw)

    # ── Control correlations ─────────────────────────────────────────
    r_deg, _, _ = pearson_r(Float64.(degrees), rts)
    r_len, _, _ = pearson_r(Float64.(word_lengths), rts)
    r_kd, _, _ = pearson_r(kappas, Float64.(degrees))
    @printf("\n  r(degree, RT)     = %+.4f\n", r_deg)
    @printf("  r(word_length, RT)= %+.4f\n", r_len)
    @printf("  r(κ, degree)      = %+.4f\n", r_kd)

    # ── Partial correlation: κ vs RT controlling for degree + length ─
    # Residualize κ and RT against degree and word length
    function residualize(y, X)
        # Simple OLS: y = Xβ + ε, return ε
        n = length(y)
        k = size(X, 2)
        # Add intercept
        X_aug = hcat(ones(n), X)
        β = X_aug \ y  # least squares
        return y .- X_aug * β
    end

    controls = hcat(Float64.(degrees), Float64.(word_lengths))
    kappa_resid = residualize(kappas, controls)
    rt_resid = residualize(rts, controls)

    r_partial, t_partial, _ = pearson_r(kappa_resid, rt_resid)
    rho_partial, _, _ = spearman_rho(kappa_resid, rt_resid)

    println("\n── Partial Correlations (controlling for degree + word length) ──")
    @printf("  Partial r(κ, RT | deg, len)  = %+.4f  (t = %.2f)\n", r_partial, t_partial)
    @printf("  Partial ρ(κ, RT | deg, len)  = %+.4f\n", rho_partial)

    # ── Bootstrap CI for partial correlation ─────────────────────────
    n_boot = 10_000
    boot_r = Float64[]
    for _ in 1:n_boot
        idx = rand(1:n_matched, n_matched)
        kr = kappa_resid[idx]
        rr = rt_resid[idx]
        r, _, _ = pearson_r(kr, rr)
        push!(boot_r, r)
    end
    sort!(boot_r)
    ci_lo = boot_r[Int(floor(0.025 * n_boot))]
    ci_hi = boot_r[Int(ceil(0.975 * n_boot))]
    @printf("  Bootstrap 95%% CI: [%+.4f, %+.4f]\n", ci_lo, ci_hi)

    sig = (ci_lo > 0.0 || ci_hi < 0.0) ? "SIGNIFICANT" : "NOT SIGNIFICANT"
    println("  $sig (CI excludes zero: $(ci_lo > 0 || ci_hi < 0))")

    # ── Regime-stratified analysis ───────────────────────────────────
    println("\n── Regime-Stratified RT ──")
    hyp_idx = findall(k -> k < -0.05, kappas)
    euc_idx = findall(k -> abs(k) <= 0.05, kappas)
    sph_idx = findall(k -> k > 0.05, kappas)

    for (name, idx) in [("Hyperbolic (κ < -0.05)", hyp_idx),
                         ("Euclidean (|κ| ≤ 0.05)", euc_idx),
                         ("Spherical (κ > +0.05)", sph_idx)]
        if !isempty(idx)
            rt_group = rts[idx]
            @printf("  %-28s  n=%3d  RT=%.1f±%.1f ms  κ̄=%+.3f\n",
                    name, length(idx), mean(rt_group), std(rt_group),
                    mean(kappas[idx]))
        end
    end

    # ── t-test: hyperbolic vs spherical RT ───────────────────────────
    if !isempty(hyp_idx) && !isempty(sph_idx)
        rt_hyp = rts[hyp_idx]
        rt_sph = rts[sph_idx]
        diff = mean(rt_hyp) - mean(rt_sph)
        se = sqrt(var(rt_hyp)/length(rt_hyp) + var(rt_sph)/length(rt_sph))
        t_val = diff / se
        @printf("\n  Hyp vs Sph RT difference: %.1f ms (t = %.2f)\n", diff, t_val)
    end

    # ── Save ─────────────────────────────────────────────────────────
    output = Dict(
        "experiment" => "behavioral_correlation_blp",
        "source" => "British Lexicon Project (Keuleers et al., 2012)",
        "swow_network" => "swow_en",
        "n_nodes" => N,
        "n_matched" => n_matched,
        "coverage" => n_matched / N,
        "pearson_r_raw" => r_raw,
        "spearman_rho_raw" => rho_raw,
        "partial_r" => r_partial,
        "partial_rho" => rho_partial,
        "partial_r_ci_lo" => ci_lo,
        "partial_r_ci_hi" => ci_hi,
        "controls" => ["degree", "word_length"],
        "n_bootstrap" => n_boot,
        "regime_rt" => Dict(
            "hyperbolic_n" => length(hyp_idx),
            "hyperbolic_rt_mean" => isempty(hyp_idx) ? NaN : mean(rts[hyp_idx]),
            "euclidean_n" => length(euc_idx),
            "euclidean_rt_mean" => isempty(euc_idx) ? NaN : mean(rts[euc_idx]),
            "spherical_n" => length(sph_idx),
            "spherical_rt_mean" => isempty(sph_idx) ? NaN : mean(rts[sph_idx]),
        ),
        "per_node" => [Dict(
            "word" => matched_nodes[i],
            "kappa" => kappas[i],
            "rt" => rts[i],
            "degree" => degrees[i],
            "word_length" => word_lengths[i],
        ) for i in 1:n_matched],
    )

    outpath = joinpath(RESULTS_DIR, "behavioral_correlation_blp.json")
    open(outpath, "w") do f
        JSON.print(f, output, 2)
    end
    println("\nSaved: $outpath")
end

main()
