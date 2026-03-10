"""
Discovery L — LLM vs Human Semantic Geometry
=============================================

Computes exact LP Ollivier-Ricci curvature on:
  1. Full LWOW networks (Haiku, Mistral, Llama3) — η comparison
  2. Matched-vocabulary subgraphs (restricted to SWOW-EN 438 cues)
     for direct, scale-controlled κ̄ comparison

Key question: Do LLMs produce the same semantic geometry as humans?
"""

import Pkg
let deps = Pkg.project().dependencies
    for pkg in ["JuMP", "HiGHS", "Graphs", "JSON", "CSV", "DataFrames"]
        haskey(deps, pkg) || Pkg.add(pkg)
    end
end

using JuMP, HiGHS, Graphs, Statistics, Random, JSON, Printf, CSV, DataFrames

const DATA_DIR    = joinpath(@__DIR__, "..", "..", "data", "processed")
const RESULTS_DIR = joinpath(@__DIR__, "..", "..", "results", "unified")
mkpath(RESULTS_DIR)

η_c(N) = 3.75 - 14.62 / sqrt(N)

# ─────────────────────────────────────────────────────────────────
# Exact LP ORC solver (same as unified_semantic_orc.jl)
# ─────────────────────────────────────────────────────────────────

function compute_wasserstein(g, u, v, dist_matrix, alpha=0.5)
    nbrs_u = [u; neighbors(g, u)]
    nbrs_v = [v; neighbors(g, v)]
    du = degree(g, u)
    dv = degree(g, v)

    mu = Dict(nbrs_u[1] => alpha)
    for w in nbrs_u[2:end]; mu[w] = get(mu, w, 0.0) + (1-alpha)/du; end
    nu = Dict(nbrs_v[1] => alpha)
    for w in nbrs_v[2:end]; nu[w] = get(nu, w, 0.0) + (1-alpha)/dv; end

    support_u = collect(keys(mu))
    support_v = collect(keys(nu))
    m, n = length(support_u), length(support_v)

    model = Model(HiGHS.Optimizer)
    set_silent(model)
    set_optimizer_attribute(model, "presolve", "on")
    set_optimizer_attribute(model, "primal_feasibility_tolerance", 1e-7)

    @variable(model, T[1:m, 1:n] >= 0)
    @objective(model, Min, sum(T[i,j] * dist_matrix[support_u[i], support_v[j]]
                               for i in 1:m, j in 1:n))
    for i in 1:m; @constraint(model, sum(T[i,:]) == mu[support_u[i]]); end
    for j in 1:n; @constraint(model, sum(T[:,j]) == nu[support_v[j]]); end

    optimize!(model)
    termination_status(model) == MOI.OPTIMAL || return 0.0
    return objective_value(model)
end

function compute_graph_curvature(g; alpha=0.5, verbose=false)
    N = nv(g)
    verbose && println("  Computing APSP for N=$N...")
    dist_matrix = Matrix{Float64}(undef, N, N)
    for v in 1:N
        d = gdistances(g, v)
        dist_matrix[v, :] = Float64.(d)
    end

    edges_list = collect(edges(g))
    E = length(edges_list)
    κ = zeros(E)
    verbose && println("  Computing ORC on $E edges...")
    for (idx, e) in enumerate(edges_list)
        u, v = src(e), dst(e)
        W = compute_wasserstein(g, u, v, dist_matrix, alpha)
        κ[idx] = 1 - W / dist_matrix[u, v]
        verbose && idx % 50 == 0 && @printf("    edge %d/%d  κ=%.4f\r", idx, E, κ[idx])
    end
    verbose && println()
    return κ, edges_list
end

# ─────────────────────────────────────────────────────────────────
# Network loader
# ─────────────────────────────────────────────────────────────────

function load_csv_network(filepath)
    df = CSV.read(filepath, DataFrame; stringtype=String)
    all_nodes = sort(unique(vcat(df.source, df.target)))
    node_to_id = Dict(name => i for (i, name) in enumerate(all_nodes))
    N = length(all_nodes)
    g = SimpleGraph(N)
    for row in eachrow(df)
        u = node_to_id[row.source]
        v = node_to_id[row.target]
        u != v && add_edge!(g, u, v)
    end
    comps = connected_components(g)
    lcc = comps[argmax(length.(comps))]
    g_lcc = induced_subgraph(g, lcc)[1]
    lcc_names = all_nodes[lcc]
    return g_lcc, lcc_names
end

"""
Load LLM edge file restricted to vocabulary in `vocab_set`.
Returns induced subgraph on matched vocabulary (largest CC).
"""
function load_matched_subgraph(filepath, vocab_set)
    df = CSV.read(filepath, DataFrame; stringtype=String)
    # Filter to rows where both source AND target are in vocab
    df_f = filter(row -> (row.source in vocab_set) && (row.target in vocab_set), df)
    isempty(df_f) && error("No edges remain after vocabulary filtering!")

    all_nodes = sort(unique(vcat(df_f.source, df_f.target)))
    node_to_id = Dict(name => i for (i, name) in enumerate(all_nodes))
    N = length(all_nodes)
    g = SimpleGraph(N)
    for row in eachrow(df_f)
        u = node_to_id[row.source]
        v = node_to_id[row.target]
        u != v && add_edge!(g, u, v)
    end
    comps = connected_components(g)
    lcc = comps[argmax(length.(comps))]
    g_lcc = induced_subgraph(g, lcc)[1]
    lcc_names = all_nodes[lcc]
    return g_lcc, lcc_names, length(lcc) / length(all_nodes)
end

function network_stats(g)
    N = nv(g); E = ne(g)
    k = 2E/N
    η = k^2/N
    # clustering
    tris = 0; trips = 0
    for v in vertices(g)
        nbrs = neighbors(g, v)
        d = length(nbrs)
        d < 2 && continue
        trips += d*(d-1)
        for i in 1:length(nbrs), j in (i+1):length(nbrs)
            has_edge(g, nbrs[i], nbrs[j]) && (tris += 2)
        end
    end
    C = trips > 0 ? tris/trips : 0.0
    return (N=N, E=E, k_mean=k, eta=η, C=C, eta_c=η_c(N))
end

function run_and_save(label, id, g, extra_meta=Dict())
    println("\n  ▶ Running ORC: $label (N=$(nv(g)), E=$(ne(g)))")
    κ, _ = compute_graph_curvature(g; verbose=true)
    stats = network_stats(g)
    κ_mean = mean(κ)
    κ_std  = std(κ)
    regime = κ_mean > 0 ? "SPHERICAL" : κ_mean < 0 ? "HYPERBOLIC" : "EUCLIDEAN"
    @printf("  κ̄ = %.4f ± %.4f  [%s]  η=%.4f (η_c=%.3f)\n",
            κ_mean, κ_std, regime, stats.eta, stats.eta_c)

    result = merge(Dict(
        "id" => id,
        "label" => label,
        "N" => stats.N,
        "E" => stats.E,
        "k_mean" => stats.k_mean,
        "eta" => stats.eta,
        "eta_c" => stats.eta_c,
        "C" => stats.C,
        "kappa_mean" => κ_mean,
        "kappa_std" => κ_std,
        "kappa_min" => minimum(κ),
        "kappa_max" => maximum(κ),
        "geometry" => regime,
        "frac_hyperbolic" => mean(κ .< 0),
        "frac_spherical" => mean(κ .> 0),
        "frac_euclidean" => mean(κ .== 0),
    ), extra_meta)

    outpath = joinpath(RESULTS_DIR, "$(id)_exact_lp.json")
    open(outpath, "w") do f; JSON.print(f, result, 2); end
    println("  Saved → $outpath")
    return result
end

# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

println("\n" * "="^65)
println("  Discovery L — LLM vs Human Semantic Geometry")
println("  Exact LP ORC (α=0.5, HiGHS)")
println("="^65)

# ── Step 1: Load SWOW-EN to get reference vocabulary ──────────────
println("\n[1/4] Loading SWOW-EN (human baseline)...")
swow_path = joinpath(DATA_DIR, "english_edges_FINAL.csv")
g_swow, names_swow = load_csv_network(swow_path)
vocab_swow = Set(names_swow)
println("  SWOW-EN vocabulary: $(length(vocab_swow)) words (LCC nodes)")

# ── Step 2: Run ORC on SWOW-EN ─────────────────────────────────
r_swow = run_and_save("SWOW-EN (Human)", "lwow_swow_en_ref", g_swow,
                      Dict("source" => "human", "model" => "human_swow_en"))

# ── Step 3: Matched-vocab subgraphs for each LLM ──────────────────
llm_configs = [
    ("LWOW-Haiku",   "lwow_haiku",   "lwow_haiku_edges.csv"),
    ("LWOW-Mistral", "lwow_mistral", "lwow_mistral_edges.csv"),
    ("LWOW-Llama3",  "lwow_llama3",  "lwow_llama3_edges.csv"),
]

results_matched = [r_swow]
for (label, id, filename) in llm_configs
    println("\n[Loading matched subgraph] $label...")
    fpath = joinpath(DATA_DIR, filename)
    g_m, names_m, lcc_frac = load_matched_subgraph(fpath, vocab_swow)
    s = network_stats(g_m)
    @printf("  Matched N=%d, E=%d, <k>=%.2f, η=%.4f, C=%.4f (%.0f%% LCC)\n",
            s.N, s.E, s.k_mean, s.eta, s.C, lcc_frac*100)

    r = run_and_save("$label (matched vocab)", "$(id)_matched", g_m,
                     Dict("source" => "llm", "model" => id,
                          "comparison" => "matched_to_swow_en",
                          "lcc_fraction" => lcc_frac))
    push!(results_matched, r)
end

# ── Step 4: Summary ────────────────────────────────────────────────
println("\n" * "="^65)
println("  DISCOVERY L — FINAL COMPARISON (matched vocabulary)")
println("="^65)
println()
@printf("  %-28s  %6s  %8s  %7s  %8s  %s\n",
        "Network", "N", "η", "C", "κ̄", "Geometry")
println("  " * "-"^68)
for r in results_matched
    @printf("  %-28s  %6d  %8.4f  %7.4f  %8.4f  %s\n",
            r["label"], r["N"], r["eta"], r["C"], r["kappa_mean"], r["geometry"])
end
println()

# Compute Δκ vs human
κ_human = r_swow["kappa_mean"]
println("  Δκ̄ = κ̄_LLM − κ̄_human:")
for r in results_matched[2:end]
    Δκ = r["kappa_mean"] - κ_human
    sign_match = sign(r["kappa_mean"]) == sign(κ_human) ? "SAME SIGN ✓" : "SIGN FLIP ✗"
    @printf("    %-28s  Δκ̄ = %+.4f  [%s]\n", r["label"], Δκ, sign_match)
end

println()
if all(r["kappa_mean"] < 0 for r in results_matched)
    println("  ★ KEY FINDING: ALL LLM networks are HYPERBOLIC — same geometry as human SWOW-EN")
    println("    LLMs preserve the sparse, tree-like semantic topology of human associations.")
    println("    Tag: [EMPIRICAL — Discovery L]")
elseif any(r["kappa_mean"] > 0 for r in results_matched[2:end])
    spherical = filter(r -> r["kappa_mean"] > 0, results_matched[2:end])
    println("  ★ KEY FINDING: $(length(spherical)) LLM network(s) are SPHERICAL — geometrically alien!")
    for r in spherical
        println("    - $(r["label"]): κ̄=$(round(r["kappa_mean"], digits=4))")
    end
    println("    Tag: [EMPIRICAL — Discovery L]")
else
    println("  ★ Mixed geometry — see per-network results above.")
end

# Save combined summary
summary = Dict(
    "discovery" => "L",
    "title" => "LLM vs Human Semantic Geometry",
    "human_swow_en" => r_swow,
    "llm_networks_matched" => results_matched[2:end],
    "conclusion" => all(r["kappa_mean"] < 0 for r in results_matched) ?
        "All networks hyperbolic: LLMs preserve human semantic geometry" :
        "Mixed: some LLMs show different geometry"
)
open(joinpath(RESULTS_DIR, "discovery_l_summary.json"), "w") do f
    JSON.print(f, summary, 2)
end
println("\n  Full summary → results/unified/discovery_l_summary.json")
