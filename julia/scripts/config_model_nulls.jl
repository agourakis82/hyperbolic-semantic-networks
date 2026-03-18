#!/usr/bin/env julia
# Configuration model null comparison for 16 Paper 2 semantic networks.
# Degree-preserving rewiring → exact LP ORC → z-scores and p-values.

import Pkg
let deps = Pkg.project().dependencies
    for pkg in ["JuMP", "HiGHS", "Graphs", "JSON", "CSV", "DataFrames"]
        if !haskey(deps, pkg)
            Pkg.add(pkg)
        end
    end
end

using JuMP, HiGHS, Graphs, Statistics, Random, JSON, Printf, CSV, DataFrames

const DATA_DIR = joinpath(@__DIR__, "..", "..", "data", "processed")
const RESULTS_DIR = joinpath(@__DIR__, "..", "..", "results", "unified")

# ── Network specs (same as unified_semantic_orc.jl) ──────────────────
struct NetworkSpec
    id::String; filename::String; category::String; language::String; has_relation::Bool
end

# Only training networks (matching Table 3 k-regular nulls)
const PAPER2_NETWORKS = [
    NetworkSpec("swow_es", "spanish_edges_FINAL.csv", "association", "Spanish", false),
    NetworkSpec("swow_en", "english_edges_FINAL.csv", "association", "English", false),
    NetworkSpec("swow_zh", "chinese_edges_FINAL.csv", "association", "Chinese", false),
    NetworkSpec("swow_nl", "dutch_edges.csv", "association", "Dutch", false),
    NetworkSpec("conceptnet_en", "conceptnet_en_edges.csv", "knowledge", "English", true),
    NetworkSpec("conceptnet_pt", "conceptnet_pt_edges.csv", "knowledge", "Portuguese", true),
    NetworkSpec("wordnet_en", "wordnet_edges.csv", "taxonomy", "English", true),
    NetworkSpec("wordnet_en_2k", "wordnet_N2000_edges.csv", "taxonomy", "English", true),
    NetworkSpec("babelnet_ru", "babelnet_ru_edges.csv", "taxonomy", "Russian", true),
    NetworkSpec("babelnet_ar", "babelnet_ar_edges.csv", "taxonomy", "Arabic", true),
    NetworkSpec("depression_minimum", "depression_networks_optimal/depression_minimum_edges.csv", "clinical", "English", false),
]

# ── Load network (from unified_semantic_orc.jl) ─────────────────────
function load_network(spec::NetworkSpec)
    filepath = joinpath(DATA_DIR, spec.filename)
    df = CSV.read(filepath, DataFrame; stringtype=String)
    all_nodes = sort(unique(vcat(df.source, df.target)))
    node_to_id = Dict(name => i for (i, name) in enumerate(all_nodes))
    N = length(all_nodes)
    g = SimpleGraph(N)
    for row in eachrow(df)
        u, v = node_to_id[row.source], node_to_id[row.target]
        u != v && add_edge!(g, u, v)
    end
    ccs = connected_components(g)
    if length(ccs) > 1
        largest_cc = ccs[argmax(length.(ccs))]
        g, _ = induced_subgraph(g, sort(largest_cc))
    end
    return g
end

# ── Exact Wasserstein-1 via LP ───────────────────────────────────────
function exact_wasserstein1(mu::Vector{Float64}, nu::Vector{Float64}, C::Matrix{Float64})
    n = length(mu)
    model = Model(HiGHS.Optimizer)
    set_silent(model)
    @variable(model, gamma[1:n, 1:n] >= 0)
    @constraint(model, [i=1:n], sum(gamma[i, j] for j in 1:n) == mu[i])
    @constraint(model, [j=1:n], sum(gamma[i, j] for i in 1:n) == nu[j])
    @objective(model, Min, sum(C[i, j] * gamma[i, j] for i in 1:n, j in 1:n))
    optimize!(model)
    termination_status(model) != OPTIMAL && return NaN
    return objective_value(model)
end

# ── ORC computation ──────────────────────────────────────────────────
function precompute_apsp(g::SimpleGraph)
    N = nv(g)
    D = Matrix{Int}(undef, N, N)
    Threads.@threads for v in 1:N
        D[v, :] = gdistances(g, v)
    end
    return D
end

function compute_edge_curvature(g::SimpleGraph, u::Int, v::Int, D::Matrix{Int}; alpha=0.5)
    mu_u = Dict{Int,Float64}(u => alpha)
    mu_v = Dict{Int,Float64}(v => alpha)
    for z in neighbors(g, u); mu_u[z] = get(mu_u, z, 0.0) + (1-alpha)/length(neighbors(g, u)); end
    for z in neighbors(g, v); mu_v[z] = get(mu_v, z, 0.0) + (1-alpha)/length(neighbors(g, v)); end
    all_nodes = sort(unique(vcat(collect(keys(mu_u)), collect(keys(mu_v)))))
    n = length(all_nodes)
    idx = Dict(node => i for (i, node) in enumerate(all_nodes))
    mu_vec = zeros(n); nu_vec = zeros(n)
    for (node, p) in mu_u; mu_vec[idx[node]] = p; end
    for (node, p) in mu_v; nu_vec[idx[node]] = p; end
    C = [Float64(D[all_nodes[i], all_nodes[j]]) for i in 1:n, j in 1:n]
    W1 = exact_wasserstein1(mu_vec, nu_vec, C)
    d_uv = Float64(D[u, v])
    d_uv == 0.0 && return 0.0
    return 1.0 - W1 / d_uv
end

function compute_mean_kappa(g::SimpleGraph, D::Matrix{Int})
    el = collect(edges(g))
    kappas = Vector{Float64}(undef, length(el))
    Threads.@threads for i in eachindex(el)
        kappas[i] = compute_edge_curvature(g, src(el[i]), dst(el[i]), D)
    end
    return mean(kappas)
end

# ── Degree-preserving edge rewiring (Maslov-Sneppen) ─────────────────
function rewire_graph(g_orig::SimpleGraph; n_swaps_factor=10, rng=Random.GLOBAL_RNG)
    g = copy(g_orig)
    el = collect(edges(g))
    E = length(el)
    n_swaps = n_swaps_factor * E
    successful = 0
    for _ in 1:n_swaps * 5  # allow extra attempts
        successful >= n_swaps && break
        i, j = rand(rng, 1:E), rand(rng, 1:E)
        i == j && continue
        e1, e2 = el[i], el[j]
        u1, v1 = src(e1), dst(e1)
        u2, v2 = src(e2), dst(e2)
        # Try swap: (u1,v1),(u2,v2) → (u1,u2),(v1,v2)
        if rand(rng, Bool)
            a, b, c, d = u1, u2, v1, v2
        else
            a, b, c, d = u1, v2, v1, u2
        end
        (a == b || c == d) && continue
        (has_edge(g, a, b) || has_edge(g, c, d)) && continue
        # Perform swap
        rem_edge!(g, u1, v1)
        rem_edge!(g, u2, v2)
        add_edge!(g, a, b)
        add_edge!(g, c, d)
        # Update edge list
        el[i] = Edge(min(a,b), max(a,b))
        el[j] = Edge(min(c,d), max(c,d))
        successful += 1
    end
    return g
end

# ── Main ─────────────────────────────────────────────────────────────
function main()
    # Minimal null count (exact LP is expensive)
    function n_nulls(N::Int)
        N <= 500 && return 5
        return 3
    end

    println("=" ^ 70)
    println("Configuration Model Null Comparison — 11 Training Networks")
    println("=" ^ 70)
    flush(stdout)

    all_results = []

    for spec in PAPER2_NETWORKS
        g = load_network(spec)
        N, E = nv(g), ne(g)
        deg_seq = degree(g)
        nn = n_nulls(N)

        # Load real κ̄ from precomputed
        real_json = JSON.parsefile(joinpath(RESULTS_DIR, "$(spec.id)_exact_lp.json"))
        kappa_real = real_json["kappa_mean"]

        @printf("\n%s (N=%d, E=%d, ⟨k⟩=%.1f) — %d config nulls\n",
                spec.id, N, E, mean(deg_seq), nn)
        flush(stdout)

        null_kappas = Float64[]
        rng = MersenneTwister(42)

        for s in 1:nn
            g_null = rewire_graph(g; n_swaps_factor=10, rng=rng)
            if !is_connected(g_null)
                @printf("  null %d: disconnected, skipping\n", s)
                continue
            end
            D_null = precompute_apsp(g_null)
            κ_null = compute_mean_kappa(g_null, D_null)
            push!(null_kappas, κ_null)
            @printf("  null %2d/%d: κ̄ = %+.4f\n", s, nn, κ_null)
            flush(stdout)
        end

        if isempty(null_kappas)
            @printf("  SKIPPED: no valid configuration models generated\n")
            push!(all_results, Dict(
                "network_id" => spec.id, "N" => N, "E" => E,
                "kappa_real" => kappa_real, "status" => "SKIPPED",
            ))
            continue
        end

        null_mean = mean(null_kappas)
        null_std = std(null_kappas)
        delta_kappa = kappa_real - null_mean
        z_score = null_std > 0 ? delta_kappa / null_std : NaN
        p_value = null_std > 0 ? 2 * (1 - min(1.0, count(k -> k <= kappa_real, null_kappas) / length(null_kappas))) : NaN
        # Two-sided empirical p-value
        n_extreme = count(k -> abs(k - null_mean) >= abs(kappa_real - null_mean), null_kappas)
        p_empirical = n_extreme / length(null_kappas)

        result = Dict(
            "network_id" => spec.id,
            "category" => spec.category,
            "N" => N, "E" => E,
            "mean_degree" => mean(deg_seq),
            "kappa_real" => kappa_real,
            "kappa_null_mean" => null_mean,
            "kappa_null_std" => null_std,
            "delta_kappa" => delta_kappa,
            "z_score" => z_score,
            "p_empirical" => p_empirical,
            "n_nulls" => length(null_kappas),
            "null_kappas" => null_kappas,
        )
        push!(all_results, result)

        @printf("  RESULT: κ̄_real=%+.4f, κ̄_null=%+.4f±%.4f, Δκ=%+.4f, z=%.2f, p=%.3f\n",
                kappa_real, null_mean, null_std, delta_kappa, z_score, p_empirical)
    end

    # ── Summary table ────────────────────────────────────────────────
    println("\n" * "=" ^ 70)
    println("Summary Table")
    @printf("%-20s  %7s  %7s  %7s  %7s  %5s  %5s\n",
            "Network", "κ̄_real", "κ̄_null", "Δκ", "σ_null", "z", "p")
    println("-" ^ 70)
    for r in all_results
        haskey(r, "status") && r["status"] == "SKIPPED" && continue
        @printf("%-20s  %+.4f  %+.4f  %+.4f  %.4f  %5.1f  %.3f\n",
                r["network_id"], r["kappa_real"], r["kappa_null_mean"],
                r["delta_kappa"], r["kappa_null_std"], r["z_score"], r["p_empirical"])
    end

    # ── Save ─────────────────────────────────────────────────────────
    output = Dict(
        "experiment" => "config_model_nulls_16",
        "n_networks" => 16,
        "method" => "maslov_sneppen_edge_rewiring_10E",
        "orc_method" => "exact_LP_HiGHS",
        "alpha" => 0.5,
        "seed" => 42,
        "results" => all_results,
    )
    outpath = joinpath(RESULTS_DIR, "config_model_nulls.json")
    open(outpath, "w") do f
        JSON.print(f, output, 2)
    end
    println("\nSaved: $outpath")
end

main()
