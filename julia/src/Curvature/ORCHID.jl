"""
ORCHID.jl — Hyperedge Ollivier-Ricci Curvature

Implements ORC for hypergraphs following the ORCHID framework.
For a hyperedge e = {v₁, ..., vₖ}, we define:

    κ(e) = 1 - W₁(μ_e, ν_e) / diam(e)

where:
  - μ_e = idleness-α probability measure on the "source" neighborhood
           (union of N(v) for all v ∈ e, weighted by degree)
  - ν_e = uniform measure on the hyperedge e itself
  - W₁  = exact Wasserstein-1 distance (LP via JuMP/HiGHS)
  - diam(e) = max pairwise graph distance between nodes in e

For pairwise edges (|e|=2), this reduces to standard Ollivier-Ricci ORC.

Reference: Inspired by Leal, Giscard, Peyré "Ollivier Ricci Curvature on Hypergraphs"
and the ORCHID computational framework.
"""

module ORCHID

using Graphs
using LinearAlgebra
using JuMP
using HiGHS
using JSON
using Statistics

export HyperGraph, orchid_curvature, orchid_all_curvatures, load_wordnet_hypergraph

# ─────────────────────────────────────────────────────────────────
# Data structures
# ─────────────────────────────────────────────────────────────────

"""
    HyperGraph

Stores a hypergraph as:
  - `n_nodes`: number of nodes
  - `hyperedges`: list of hyperedges (each is a sorted Vector{Int})
  - `pairwise_graph`: SimpleGraph — clique expansion for APSP
  - `node_names`: optional Dict{Int,String}
"""
struct HyperGraph
    n_nodes::Int
    hyperedges::Vector{Vector{Int}}
    pairwise_graph::SimpleGraph
    node_names::Dict{Int,String}
end

function HyperGraph(n_nodes::Int, hyperedges::Vector{Vector{Int}};
                    node_names::Dict{Int,String} = Dict{Int,String}())
    # Build clique expansion
    g = SimpleGraph(n_nodes)
    for he in hyperedges
        for i in 1:length(he)
            for j in (i+1):length(he)
                add_edge!(g, he[i]+1, he[j]+1)  # 0-indexed → 1-indexed
            end
        end
    end
    HyperGraph(n_nodes, hyperedges, g, node_names)
end

# ─────────────────────────────────────────────────────────────────
# LP Wasserstein (reuse same as unified_semantic_orc.jl)
# ─────────────────────────────────────────────────────────────────

function exact_wasserstein1(mu::Vector{Float64}, nu::Vector{Float64},
                             C::Matrix{Float64})::Float64
    n = length(mu)
    @assert length(nu) == n
    @assert size(C) == (n, n)

    model = Model(HiGHS.Optimizer)
    set_silent(model)

    @variable(model, gamma[1:n, 1:n] >= 0)
    @constraint(model, [i=1:n], sum(gamma[i, j] for j in 1:n) == mu[i])
    @constraint(model, [j=1:n], sum(gamma[i, j] for i in 1:n) == nu[j])
    @objective(model, Min, sum(C[i,j] * gamma[i,j] for i in 1:n, j in 1:n))

    optimize!(model)
    termination_status(model) == OPTIMAL || return NaN
    return objective_value(model)
end

# ─────────────────────────────────────────────────────────────────
# APSP on clique-expansion graph
# ─────────────────────────────────────────────────────────────────

function compute_apsp(g::SimpleGraph)::Matrix{Int}
    N = nv(g)
    D = Matrix{Int}(undef, N, N)
    Threads.@threads for v in 1:N
        D[v, :] = gdistances(g, v)
    end
    return D
end

# ─────────────────────────────────────────────────────────────────
# Core ORCHID curvature for a single hyperedge
# ─────────────────────────────────────────────────────────────────

"""
    orchid_curvature(H, e, D; alpha=0.5) -> Float64

Compute ORCHID curvature for hyperedge `e` (0-indexed node IDs).

    κ(e) = 1 - W₁(μ_e, ν_e) / diam(e)

μ_e: idleness-α measure on neighborhood of e
  - Each node v ∈ e contributes weight 1/|e| to the measure
  - v itself retains mass α/|e|
  - Each neighbor w of v in the clique-expansion gets (1-α)/(|e|⋅deg(v))

ν_e: uniform measure on nodes of e (1/|e| each)
"""
function orchid_curvature(H::HyperGraph, e::Vector{Int}, D::Matrix{Int};
                           alpha::Float64=0.5)::Float64
    k = length(e)
    k < 2 && return NaN

    g = H.pairwise_graph
    # Convert to 1-indexed for Graphs.jl
    e1 = e .+ 1

    # ── Build μ_e (source measure on neighborhood of hyperedge) ──
    mu_dict = Dict{Int,Float64}()
    for v1 in e1
        # Each hyperedge node contributes equal weight 1/k
        # Idleness: v1 keeps mass α/k
        mu_dict[v1] = get(mu_dict, v1, 0.0) + alpha / k
        # Spread to neighbors
        nbrs = neighbors(g, v1)
        if !isempty(nbrs)
            w = (1.0 - alpha) / (k * length(nbrs))
            for nb in nbrs
                mu_dict[nb] = get(mu_dict, nb, 0.0) + w
            end
        end
    end

    # ── Build ν_e (uniform measure on hyperedge nodes) ──
    nu_dict = Dict{Int,Float64}()
    for v1 in e1
        nu_dict[v1] = 1.0 / k
    end

    # ── Support = union of both ──
    all_nodes = sort(unique(vcat(collect(keys(mu_dict)), collect(keys(nu_dict)))))
    n = length(all_nodes)
    node_to_idx = Dict(node => i for (i, node) in enumerate(all_nodes))

    mu_vec = zeros(n)
    nu_vec = zeros(n)
    for (node, prob) in mu_dict
        mu_vec[node_to_idx[node]] = prob
    end
    for (node, prob) in nu_dict
        nu_vec[node_to_idx[node]] = prob
    end

    # Normalize (numerical safety)
    sum_mu = sum(mu_vec)
    sum_nu = sum(nu_vec)
    abs(sum_mu - 1.0) > 1e-9 && (mu_vec ./= sum_mu)
    abs(sum_nu - 1.0) > 1e-9 && (nu_vec ./= sum_nu)

    # ── Cost matrix from APSP ──
    C = zeros(n, n)
    for i in 1:n
        for j in 1:n
            di = D[all_nodes[i], all_nodes[j]]
            C[i,j] = di == typemax(Int) ? 1000.0 : Float64(di)
        end
    end

    # ── Diameter of hyperedge ──
    diam = maximum(D[e1[i], e1[j]] for i in 1:k for j in (i+1):k)
    diam == 0 && return 0.0
    diam == typemax(Int) && return NaN

    W1 = exact_wasserstein1(mu_vec, nu_vec, C)
    isnan(W1) && return NaN

    return 1.0 - W1 / Float64(diam)
end

# ─────────────────────────────────────────────────────────────────
# Batch computation
# ─────────────────────────────────────────────────────────────────

"""
    orchid_all_curvatures(H; alpha=0.5, max_size=10) -> (Vector{Float64}, Vector{Vector{Int}})

Compute ORCHID curvature for all hyperedges in H.
Hyperedges larger than `max_size` are skipped (LP becomes expensive).
Returns (curvatures, processed_hyperedges).
"""
function orchid_all_curvatures(H::HyperGraph; alpha::Float64=0.5,
                                max_size::Int=10)::Tuple{Vector{Float64},Vector{Vector{Int}}}
    println("  Computing APSP on clique-expansion graph ($(nv(H.pairwise_graph)) nodes, $(ne(H.pairwise_graph)) edges)...")
    D = compute_apsp(H.pairwise_graph)

    valid_edges = [e for e in H.hyperedges if length(e) <= max_size && length(e) >= 2]
    println("  Processing $(length(valid_edges)) hyperedges (of $(length(H.hyperedges)) total, max_size=$max_size)...")

    kappas = Vector{Float64}(undef, length(valid_edges))
    Threads.@threads for i in 1:length(valid_edges)
        kappas[i] = orchid_curvature(H, valid_edges[i], D; alpha=alpha)
    end

    return kappas, valid_edges
end

# ─────────────────────────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────────────────────────

"""
    load_wordnet_hypergraph(json_path; use_synset=true, use_hypernymy=true) -> HyperGraph

Load hyperedges from the JSON file produced by extract_wordnet_hyperedges.py.
"""
function load_wordnet_hypergraph(json_path::String;
                                  use_synset::Bool=true,
                                  use_hypernymy::Bool=true)::HyperGraph
    data = JSON.parsefile(json_path)
    n = data["n_nodes"]
    node_names = Dict{Int,String}(parse(Int,k) => v for (k,v) in data["nodes"])

    hyperedges = Vector{Vector{Int}}()
    if use_synset
        for he in data["synset_hyperedges"]
            push!(hyperedges, Int.(he))
        end
    end
    if use_hypernymy
        for he in data["hypernymy_hyperedges"]
            push!(hyperedges, Int.(he))
        end
    end

    # Deduplicate
    unique_edges = unique(sort.(hyperedges))

    println("Loaded $(n) nodes, $(length(unique_edges)) unique hyperedges from $json_path")
    return HyperGraph(n, unique_edges; node_names=node_names)
end

end  # module ORCHID
