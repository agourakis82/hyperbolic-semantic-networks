"""
resolution_curvature.jl — Resolution-Dependent Curvature Analysis

Computes κ̄(r) where r ∈ [0, 1] is a resolution parameter:
  r=0: original pairwise graph (each hyperedge collapsed to a single edge)
  r=1: full clique expansion (all hyperedges unpacked into cliques)

For intermediate r: randomly sample r fraction of hyperedges to expand.

This characterizes the curvature flow under resolution change.

Usage:
    julia --project=julia -t 8 julia/scripts/resolution_curvature.jl
"""

import Pkg
Pkg.instantiate()

using Graphs
using JSON
using Statistics
using Random
using JuMP
using HiGHS

# ─────────────────────────────────────────────────────────────────
# LP ORC (same as other scripts)
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

function compute_graph_orc(g::SimpleGraph; alpha::Float64=0.5, max_edges::Int=500)
    N = nv(g)
    ne(g) == 0 && return NaN

    D = Matrix{Int}(undef, N, N)
    Threads.@threads for v in 1:N
        D[v,:] = gdistances(g, v)
    end

    edge_list = collect(edges(g))
    if length(edge_list) > max_edges
        edge_list = edge_list[randperm(length(edge_list))[1:max_edges]]
    end

    kappas = Vector{Float64}(undef, length(edge_list))
    Threads.@threads for i in 1:length(edge_list)
        e = edge_list[i]
        u, v = src(e), dst(e)
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
        idx = Dict(node => j for (j,node) in enumerate(all_nodes))
        mu_vec = zeros(n); nu_vec = zeros(n)
        for (node,p) in mu_dict; mu_vec[idx[node]] = p; end
        for (node,p) in nu_dict; nu_vec[idx[node]] = p; end
        C = Float64[D[all_nodes[a], all_nodes[b]] == typemax(Int) ? 1000.0 :
                    Float64(D[all_nodes[a], all_nodes[b]]) for a in 1:n, b in 1:n]
        d_uv = Float64(D[u, v])
        if d_uv == 0.0
            kappas[i] = 0.0
        else
            W1 = exact_wasserstein1(mu_vec, nu_vec, C)
            kappas[i] = isnan(W1) ? NaN : 1.0 - W1 / d_uv
        end
    end

    valid = filter(!isnan, kappas)
    return isempty(valid) ? NaN : mean(valid)
end

# ─────────────────────────────────────────────────────────────────
# Build graph at resolution r
# ─────────────────────────────────────────────────────────────────

"""
    build_resolution_graph(base_edges, hyperedges, n_nodes, r; rng) -> SimpleGraph

Build a graph that combines:
  - All original pairwise edges (always included)
  - r fraction of hyperedges expanded as cliques

r=0: only original pairwise edges
r=1: all hyperedges expanded
"""
function build_resolution_graph(base_edges::Vector{Tuple{Int,Int}},
                                 hyperedges::Vector{Vector{Int}},
                                 n_nodes::Int, r::Float64;
                                 rng::AbstractRNG=MersenneTwister(42))::SimpleGraph
    g = SimpleGraph(n_nodes)

    # Always add base edges
    for (u, v) in base_edges
        add_edge!(g, u+1, v+1)  # 0-indexed → 1-indexed
    end

    # Sample r fraction of hyperedges
    n_expand = round(Int, r * length(hyperedges))
    if n_expand > 0
        selected = sort(randperm(rng, length(hyperedges))[1:n_expand])
        for idx in selected
            he = hyperedges[idx]
            for i in 1:length(he)
                for j in (i+1):length(he)
                    add_edge!(g, he[i]+1, he[j]+1)
                end
            end
        end
    end

    return g
end

# ─────────────────────────────────────────────────────────────────
# Resolution sweep for a single network
# ─────────────────────────────────────────────────────────────────

function resolution_sweep(net_id::String; n_points::Int=11, n_seeds::Int=3)
    json_path = joinpath(@__DIR__, "..", "..", "data", "processed", "$(net_id)_hyperedges.json")

    if !isfile(json_path)
        println("  SKIP $net_id — no hyperedge file")
        return nothing
    end

    println("\n" * "="^60)
    println("Resolution Curvature: $net_id")
    println("="^60)

    data = JSON.parsefile(json_path)
    n_nodes = data["n_nodes"]

    # Collect all hyperedges
    hyperedges = Vector{Vector{Int}}()
    for he in get(data, "synset_hyperedges", [])
        push!(hyperedges, Int.(he))
    end
    for he in get(data, "hypernymy_hyperedges", [])
        push!(hyperedges, Int.(he))
    end
    hyperedges = unique(sort.(hyperedges))

    # Base pairwise edges (from original network, not clique expansion)
    # Load from the original edge file
    base_edges = Tuple{Int,Int}[]
    edge_files = Dict(
        "wordnet_en" => "wordnet_edges.csv",
        "conceptnet_en" => "conceptnet_en_edges.csv",
        "conceptnet_pt" => "conceptnet_pt_edges.csv",
        "babelnet_ru" => "babelnet_ru_edges.csv",
        "babelnet_ar" => "babelnet_ar_edges.csv",
    )

    edge_fname = get(edge_files, net_id, "$(net_id)_edges.csv")
    edge_path = joinpath(@__DIR__, "..", "..", "data", "processed", edge_fname)

    if isfile(edge_path)
        node_map = Dict{String,Int}()
        open(edge_path) do f
            for line in eachline(f)
                startswith(line, "source") && continue
                startswith(line, "#") && continue
                parts = split(strip(line), ",")
                length(parts) < 2 && continue
                s, t = parts[1], parts[2]
                s == t && continue
                if !haskey(node_map, s); node_map[s] = length(node_map); end
                if !haskey(node_map, t); node_map[t] = length(node_map); end
                push!(base_edges, (node_map[s], node_map[t]))
            end
        end
    end

    println("  Nodes: $n_nodes")
    println("  Base edges: $(length(base_edges))")
    println("  Hyperedges: $(length(hyperedges))")

    # Resolution sweep
    r_values = range(0.0, 1.0, length=n_points)
    results_data = []

    for r in r_values
        kappas_seeds = Float64[]
        for seed in 1:n_seeds
            rng = MersenneTwister(42 + seed)
            g = build_resolution_graph(base_edges, hyperedges, max(n_nodes, length(get(Dict(), "x", [])) + 1), r; rng=rng)

            # Use actual number of nodes from graph
            if nv(g) < 2 || ne(g) == 0
                push!(kappas_seeds, NaN)
                continue
            end

            km = compute_graph_orc(g; alpha=0.5, max_edges=300)
            push!(kappas_seeds, km)
        end

        valid_seeds = filter(!isnan, kappas_seeds)
        km = isempty(valid_seeds) ? NaN : mean(valid_seeds)
        ks = isempty(valid_seeds) || length(valid_seeds) < 2 ? NaN : std(valid_seeds)

        # Count edges at this resolution (use first seed)
        rng = MersenneTwister(43)
        g_sample = build_resolution_graph(base_edges, hyperedges, n_nodes, r; rng=rng)

        push!(results_data, Dict(
            "r" => r,
            "kappa_mean" => km,
            "kappa_std" => ks,
            "n_edges" => ne(g_sample),
            "n_seeds" => length(valid_seeds),
        ))

        sign_str = isnan(km) ? "NaN" : (km < 0 ? "−" : "+")
        println("  r=$(round(r, digits=2))  κ̄=$(isnan(km) ? "NaN" : round(km, digits=4))  E=$(ne(g_sample))  [$sign_str]")
    end

    out = Dict(
        "network" => net_id,
        "n_nodes" => n_nodes,
        "n_base_edges" => length(base_edges),
        "n_hyperedges" => length(hyperedges),
        "n_points" => n_points,
        "n_seeds" => n_seeds,
        "resolution_curve" => results_data,
    )

    out_path = joinpath(@__DIR__, "..", "..", "results", "experiments", "resolution_$(net_id).json")
    open(out_path, "w") do f
        JSON.print(f, out, 2)
    end
    println("  Saved to $out_path")
    return out
end

# ─────────────────────────────────────────────────────────────────
# Run all
# ─────────────────────────────────────────────────────────────────

NETWORKS = ["wordnet_en", "conceptnet_en", "babelnet_ru"]

println("Resolution-Dependent Curvature Analysis")
println("Threads: $(Threads.nthreads())")

for net_id in NETWORKS
    resolution_sweep(net_id; n_points=11, n_seeds=3)
end

println("\nAll resolution sweeps complete.")
