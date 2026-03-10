"""
orchid_semantic.jl — ORCHID Hyperedge ORC on Semantic Networks

Computes hyperedge Ollivier-Ricci curvature for:
  - WordNet EN (oewn:2024) — synset + hypernymy hyperedges
  - For comparison: pairwise projection ORC (standard ORC on clique expansion)

Hypothesis: Taxonomies (WordNet/BabelNet) that appear Euclidean under pairwise ORC
will reveal negative hyperedge curvature under ORCHID — the tree structure is
encoded in hyperedges, not pairwise edges.

Usage:
    julia --project=julia -t 8 julia/scripts/orchid_semantic.jl
"""

import Pkg
Pkg.instantiate()

using Graphs
using JSON
using Statistics
using Random
using JuMP
using HiGHS

# Load ORCHID module
include(joinpath(@__DIR__, "..", "src", "Curvature", "ORCHID.jl"))
using .ORCHID

# ─────────────────────────────────────────────────────────────────
# Helpers: pairwise ORC on clique expansion (for comparison)
# ─────────────────────────────────────────────────────────────────

function exact_wasserstein1(mu::Vector{Float64}, nu::Vector{Float64},
                             C::Matrix{Float64})::Float64
    n = length(mu)
    model = Model(HiGHS.Optimizer)
    set_silent(model)
    @variable(model, gamma[1:n, 1:n] >= 0)
    @constraint(model, [i=1:n], sum(gamma[i,j] for j in 1:n) == mu[i])
    @constraint(model, [j=1:n], sum(gamma[i,j] for i in 1:n) == nu[j])
    @objective(model, Min, sum(C[i,j]*gamma[i,j] for i in 1:n, j in 1:n))
    optimize!(model)
    termination_status(model) == OPTIMAL || return NaN
    return objective_value(model)
end

function pairwise_edge_curvature(g::SimpleGraph, u::Int, v::Int,
                                  D::Matrix{Int}; alpha::Float64=0.5)::Float64
    mu_dict = Dict{Int,Float64}(u => alpha)
    nu_dict = Dict{Int,Float64}(v => alpha)
    for nb in neighbors(g, u)
        mu_dict[nb] = get(mu_dict, nb, 0.0) + (1.0-alpha)/degree(g,u)
    end
    for nb in neighbors(g, v)
        nu_dict[nb] = get(nu_dict, nb, 0.0) + (1.0-alpha)/degree(g,v)
    end
    all_nodes = sort(unique(vcat(collect(keys(mu_dict)), collect(keys(nu_dict)))))
    n = length(all_nodes)
    idx = Dict(node => i for (i,node) in enumerate(all_nodes))
    mu_vec = zeros(n); nu_vec = zeros(n)
    for (node,p) in mu_dict; mu_vec[idx[node]] = p; end
    for (node,p) in nu_dict; nu_vec[idx[node]] = p; end
    C = Float64[D[all_nodes[i], all_nodes[j]] == typemax(Int) ? 1000.0 :
                Float64(D[all_nodes[i], all_nodes[j]]) for i in 1:n, j in 1:n]
    d_uv = Float64(D[u, v])
    d_uv == 0.0 && return 0.0
    W1 = exact_wasserstein1(mu_vec, nu_vec, C)
    isnan(W1) && return NaN
    return 1.0 - W1 / d_uv
end

function pairwise_orc(g::SimpleGraph; alpha::Float64=0.5)
    N = nv(g)
    D = Matrix{Int}(undef, N, N)
    Threads.@threads for v in 1:N
        D[v,:] = gdistances(g, v)
    end
    edge_list = collect(edges(g))
    kappas = Vector{Float64}(undef, length(edge_list))
    Threads.@threads for i in 1:length(edge_list)
        e = edge_list[i]
        kappas[i] = pairwise_edge_curvature(g, src(e), dst(e), D; alpha=alpha)
    end
    return filter(!isnan, kappas)
end

# ─────────────────────────────────────────────────────────────────
# Main analysis
# ─────────────────────────────────────────────────────────────────

function analyze_network(net_id::String; max_size::Int=8, alpha::Float64=0.5)
    json_path = joinpath(@__DIR__, "..", "..", "data", "processed", "$(net_id)_hyperedges.json")

    if !isfile(json_path)
        println("  SKIP $net_id — hyperedge file not found: $json_path")
        return nothing
    end

    println("\n" * "="^60)
    println("ORCHID Analysis: $net_id")
    println("="^60)

    # Load hypergraph
    H = load_wordnet_hypergraph(json_path; use_synset=true, use_hypernymy=true)
    stats = JSON.parsefile(json_path)["stats"]

    println("\nHyperedge statistics:")
    println("  Synset hyperedges: $(stats["n_synset_hyperedges"])")
    println("  Hypernymy hyperedges: $(stats["n_hypernymy_hyperedges"])")
    println("  Mean synset size: $(round(stats["mean_synset_size"], digits=2))")
    println("  Pairwise projection edges: $(stats["n_pairwise_edges"])")
    println("  Clique-expansion graph: $(nv(H.pairwise_graph))v / $(ne(H.pairwise_graph))e")

    # 1. ORCHID curvature on hyperedges
    println("\n[1] ORCHID hyperedge curvature (max_size=$max_size)...")
    t0 = time()
    kappas_orchid, processed_edges = orchid_all_curvatures(H; alpha=alpha, max_size=max_size)
    t1 = time()
    valid_orchid = filter(!isnan, kappas_orchid)
    println("  Done in $(round(t1-t0, digits=1))s")
    println("  Processed: $(length(processed_edges)) hyperedges, $(length(valid_orchid)) valid")
    println("  κ̄_orchid = $(round(mean(valid_orchid), digits=4)) ± $(round(std(valid_orchid), digits=4))")
    println("  κ_min = $(round(minimum(valid_orchid), digits=4))")
    println("  κ_max = $(round(maximum(valid_orchid), digits=4))")
    pct_neg = 100.0 * count(x -> x < 0, valid_orchid) / length(valid_orchid)
    println("  Fraction negative: $(round(pct_neg, digits=1))%")

    # Breakdown by hyperedge size
    println("\n  By hyperedge size:")
    for s in 2:max_size
        idx = findall(i -> length(processed_edges[i]) == s, 1:length(processed_edges))
        isempty(idx) && continue
        k_s = filter(!isnan, kappas_orchid[idx])
        isempty(k_s) && continue
        println("    size=$s: n=$(length(k_s)), κ̄=$(round(mean(k_s), digits=4))")
    end

    # 2. Pairwise ORC on clique expansion (for comparison)
    println("\n[2] Pairwise ORC on clique-expansion graph...")
    g_clique = H.pairwise_graph
    if ne(g_clique) > 5000
        println("  Too many edges ($(ne(g_clique))) — sampling 500 random edges")
        edge_list = collect(edges(g_clique))
        sampled = edge_list[randperm(length(edge_list))[1:500]]
        N = nv(g_clique)
        D = Matrix{Int}(undef, N, N)
        Threads.@threads for v in 1:N
            D[v,:] = gdistances(g_clique, v)
        end
        kappas_pw = [pairwise_edge_curvature(g_clique, src(e), dst(e), D; alpha=alpha)
                     for e in sampled]
    else
        kappas_pw = pairwise_orc(g_clique; alpha=alpha)
    end
    valid_pw = filter(!isnan, kappas_pw)
    println("  κ̄_pairwise = $(round(mean(valid_pw), digits=4)) ± $(round(std(valid_pw), digits=4))")
    pct_neg_pw = 100.0 * count(x -> x < 0, valid_pw) / length(valid_pw)
    println("  Fraction negative: $(round(pct_neg_pw, digits=1))%")

    println("\n  COMPARISON:")
    println("  κ̄_orchid   = $(round(mean(valid_orchid), digits=4))  (hyperedge ORC)")
    println("  κ̄_pairwise = $(round(mean(valid_pw), digits=4))  (clique-expansion ORC)")
    delta = mean(valid_orchid) - mean(valid_pw)
    println("  Δκ = κ̄_orchid - κ̄_pairwise = $(round(delta, digits=4))")
    if mean(valid_orchid) < mean(valid_pw)
        println("  ✓ ORCHID reveals MORE negative curvature than pairwise projection")
        println("    → confirms hyperedge structure encodes hyperbolic geometry")
    else
        println("  ✗ ORCHID does not reveal more negative curvature")
    end

    # Save results
    results = Dict(
        "network" => net_id,
        "alpha" => alpha,
        "max_size" => max_size,
        "n_nodes" => H.n_nodes,
        "n_hyperedges_total" => length(H.hyperedges),
        "n_hyperedges_processed" => length(processed_edges),
        "orchid" => Dict(
            "kappa_mean" => mean(valid_orchid),
            "kappa_std" => std(valid_orchid),
            "kappa_min" => minimum(valid_orchid),
            "kappa_max" => maximum(valid_orchid),
            "n_valid" => length(valid_orchid),
            "fraction_negative" => pct_neg / 100.0,
        ),
        "pairwise_clique_expansion" => Dict(
            "kappa_mean" => mean(valid_pw),
            "kappa_std" => std(valid_pw),
            "n_valid" => length(valid_pw),
            "fraction_negative" => pct_neg_pw / 100.0,
        ),
        "delta_kappa" => delta,
        "interpretation" => delta < 0 ? "ORCHID_more_negative" : "pairwise_more_negative",
    )

    out_path = joinpath(@__DIR__, "..", "..", "results", "experiments", "orchid_$(net_id).json")
    open(out_path, "w") do f
        JSON.print(f, results, 2)
    end
    println("\nSaved to $out_path")

    return results
end

# ─────────────────────────────────────────────────────────────────
# Run all networks with hyperedge files
# ─────────────────────────────────────────────────────────────────

NETWORKS = ["wordnet_en", "conceptnet_en", "conceptnet_pt", "babelnet_ru", "babelnet_ar"]

println("ORCHID Multi-Network Analysis")
println("Networks: $(join(NETWORKS, ", "))")
println("Threads: $(Threads.nthreads())")

all_results = Dict[]
for net_id in NETWORKS
    r = analyze_network(net_id; max_size=8, alpha=0.5)
    !isnothing(r) && push!(all_results, r)
end

# Summary table
println("\n" * "="^70)
println("SUMMARY: Resolution-Dependent Curvature")
println("="^70)
println("  Network          | κ̄_orchid  | κ̄_clique  | Δκ_resolution")
println("  -----------------+----------+----------+-------------")
for r in all_results
    net = r["network"]
    ko = round(r["orchid"]["kappa_mean"], digits=4)
    kc = round(r["pairwise_clique_expansion"]["kappa_mean"], digits=4)
    dk = round(r["delta_kappa"], digits=4)
    println("  $(rpad(net, 18))| $(lpad(ko, 8)) | $(lpad(kc, 8)) | $(lpad(dk, 11))")
end
println("\nDone.")
