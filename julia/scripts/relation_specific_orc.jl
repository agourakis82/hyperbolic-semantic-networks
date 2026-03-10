"""
relation_specific_orc.jl — ORC by Semantic Relation Type

For ConceptNet EN (26 relation types), computes pairwise ORC on each
relation-specific subgraph separately.

Scientific question: Do certain semantic relations create more hyperbolic
geometry than others?

Expected:
  - Hierarchical: /r/IsA, /r/MannerOf → more negative κ̄
  - Associative: /r/RelatedTo, /r/SimilarTo → more positive κ̄

Usage:
    julia --project=julia -t 8 julia/scripts/relation_specific_orc.jl
"""

import Pkg
Pkg.instantiate()

using Graphs
using JSON
using Statistics
using JuMP
using HiGHS
using CSV
using DataFrames

# ─────────────────────────────────────────────────────────────────
# LP ORC (reuse from unified_semantic_orc.jl)
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

function edge_curvature(g::SimpleGraph, u::Int, v::Int, D::Matrix{Int};
                         alpha::Float64=0.5)::Float64
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

# ─────────────────────────────────────────────────────────────────
# Main: relation-specific analysis
# ─────────────────────────────────────────────────────────────────

function analyze_relations(csv_path::String, net_id::String; alpha::Float64=0.5, min_edges::Int=10)
    println("\n" * "="^60)
    println("Relation-Specific ORC: $net_id")
    println("="^60)

    # Load edges with relation types
    node_map = Dict{String,Int}()
    edges_by_rel = Dict{String,Vector{Tuple{Int,Int}}}()

    open(csv_path) do f
        for line in eachline(f)
            startswith(line, "source") && continue
            startswith(line, "#") && continue
            parts = split(strip(line), ",")
            length(parts) < 4 && continue
            s, t, _, rel = parts[1], parts[2], parts[3], parts[4]
            s == t && continue

            if !haskey(node_map, s); node_map[s] = length(node_map) + 1; end
            if !haskey(node_map, t); node_map[t] = length(node_map) + 1; end

            if !haskey(edges_by_rel, rel); edges_by_rel[rel] = Tuple{Int,Int}[]; end
            push!(edges_by_rel[rel], (node_map[s], node_map[t]))
        end
    end

    N = length(node_map)
    println("  Total nodes: $N")
    println("  Relation types: $(length(edges_by_rel))")

    results = Dict[]

    for (rel, rel_edges) in sort(collect(edges_by_rel), by=x->-length(x[2]))
        n_edges = length(rel_edges)
        if n_edges < min_edges
            continue
        end

        # Build subgraph for this relation
        g = SimpleGraph(N)
        for (u, v) in rel_edges
            add_edge!(g, u, v)
        end
        actual_edges = ne(g)
        actual_nodes = count(v -> degree(g, v) > 0, 1:N)

        if actual_edges < min_edges
            continue
        end

        # APSP on full node set
        D = Matrix{Int}(undef, N, N)
        Threads.@threads for v in 1:N
            D[v,:] = gdistances(g, v)
        end

        # Compute ORC for edges in this relation's subgraph
        edge_list = collect(edges(g))
        kappas = Vector{Float64}(undef, length(edge_list))
        Threads.@threads for i in 1:length(edge_list)
            e = edge_list[i]
            kappas[i] = edge_curvature(g, src(e), dst(e), D; alpha=alpha)
        end

        valid = filter(!isnan, kappas)
        if isempty(valid)
            continue
        end

        km = mean(valid)
        ks = std(valid)
        pct_neg = 100.0 * count(x -> x < 0, valid) / length(valid)
        sign_str = km < -0.01 ? "HYPERBOLIC" : (km > 0.01 ? "SPHERICAL" : "EUCLIDEAN")

        row = Dict(
            "relation" => rel,
            "n_edges" => actual_edges,
            "n_nodes" => actual_nodes,
            "kappa_mean" => km,
            "kappa_std" => ks,
            "fraction_negative" => pct_neg / 100.0,
            "geometry" => sign_str,
        )
        push!(results, row)

        println("  $(rpad(rel, 25)) E=$(lpad(actual_edges, 4))  κ̄=$(lpad(round(km, digits=4), 8))  [$sign_str]")
    end

    # Save
    out = Dict(
        "network" => net_id,
        "n_nodes" => N,
        "n_relations" => length(edges_by_rel),
        "alpha" => alpha,
        "min_edges" => min_edges,
        "relations" => results,
    )
    out_path = joinpath(@__DIR__, "..", "..", "results", "experiments", "relation_orc_$(net_id).json")
    open(out_path, "w") do f
        JSON.print(f, out, 2)
    end
    println("\n  Saved to $out_path")
    return out
end

# ─────────────────────────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────────────────────────

data_dir = joinpath(@__DIR__, "..", "..", "data", "processed")

NETWORKS = [
    ("conceptnet_en", joinpath(data_dir, "conceptnet_en_edges.csv")),
    ("conceptnet_pt", joinpath(data_dir, "conceptnet_pt_edges.csv")),
    ("babelnet_ru", joinpath(data_dir, "babelnet_ru_edges.csv")),
    ("babelnet_ar", joinpath(data_dir, "babelnet_ar_edges.csv")),
]

for (net_id, csv_path) in NETWORKS
    if isfile(csv_path)
        analyze_relations(csv_path, net_id; min_edges=10)
    else
        println("  SKIP $net_id — file not found")
    end
end

println("\nAll relation-specific analyses complete.")
