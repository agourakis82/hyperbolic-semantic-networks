"""
resolution_curvature_large.jl — Resolution-Dependent Curvature at Scale

Same analysis as resolution_curvature.jl but uses Sinkhorn ORC instead of
exact LP, enabling N>5000 networks. Edge sampling + lazy BFS for efficiency.

Usage:
    julia --project=julia -t 8 julia/scripts/resolution_curvature_large.jl
"""

import Pkg
Pkg.instantiate()

using Graphs
using JSON
using Statistics
using Random
using LinearAlgebra

# ─────────────────────────────────────────────────────────────────
# Sinkhorn ORC (replaces exact LP for large N)
# ─────────────────────────────────────────────────────────────────

function sinkhorn_wasserstein1(mu::Vector{Float64}, nu::Vector{Float64},
                                C::Matrix{Float64};
                                epsilon::Float64=0.1,
                                max_iter::Int=200,
                                tol::Float64=1e-6)::Float64
    n = length(mu)
    K = exp.(-C ./ epsilon)

    u = ones(n)
    v = ones(n)

    for iter in 1:max_iter
        u_prev = copy(u)
        u = mu ./ (K * v .+ 1e-300)
        v = nu ./ (K' * u .+ 1e-300)

        if maximum(abs.(u .- u_prev)) < tol
            break
        end
    end

    # Transport plan and cost
    gamma = Diagonal(u) * K * Diagonal(v)
    return sum(C .* gamma)
end

function compute_graph_orc_sinkhorn(g::SimpleGraph;
                                      alpha::Float64=0.5,
                                      max_edges::Int=2000,
                                      epsilon::Float64=0.1,
                                      lazy_bfs::Bool=true)
    N = nv(g)
    ne(g) == 0 && return NaN

    edge_list = collect(edges(g))
    if length(edge_list) > max_edges
        edge_list = edge_list[randperm(length(edge_list))[1:max_edges]]
    end

    # Determine which nodes we need distances for
    if lazy_bfs
        needed_nodes = Set{Int}()
        for e in edge_list
            u, v = src(e), dst(e)
            push!(needed_nodes, u)
            push!(needed_nodes, v)
            for nb in neighbors(g, u); push!(needed_nodes, nb); end
            for nb in neighbors(g, v); push!(needed_nodes, nb); end
        end
        needed_list = sort(collect(needed_nodes))

        # Compute BFS only for needed source nodes
        D_rows = Dict{Int, Vector{Int}}()
        lk = ReentrantLock()
        Threads.@threads for v in needed_list
            dists = gdistances(g, v)
            lock(lk)
            D_rows[v] = dists
            unlock(lk)
        end
    else
        # Full APSP
        D_full = Matrix{Int}(undef, N, N)
        Threads.@threads for v in 1:N
            D_full[v,:] = gdistances(g, v)
        end
    end

    function get_dist(a::Int, b::Int)::Int
        if lazy_bfs
            if haskey(D_rows, a)
                return D_rows[a][b]
            elseif haskey(D_rows, b)
                return D_rows[b][a]
            else
                return typemax(Int)
            end
        else
            return D_full[a, b]
        end
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
        C = Float64[(let d = get_dist(all_nodes[a], all_nodes[b]);
            d == typemax(Int) ? 1000.0 : Float64(d) end) for a in 1:n, b in 1:n]
        d_uv = Float64(get_dist(u, v))
        if d_uv == 0.0
            kappas[i] = 0.0
        else
            W1 = sinkhorn_wasserstein1(mu_vec, nu_vec, C; epsilon=epsilon)
            kappas[i] = isnan(W1) ? NaN : 1.0 - W1 / d_uv
        end
    end

    valid = filter(!isnan, kappas)
    return isempty(valid) ? NaN : mean(valid)
end

# ─────────────────────────────────────────────────────────────────
# Build graph at resolution r (identical to resolution_curvature.jl)
# ─────────────────────────────────────────────────────────────────

function build_resolution_graph(base_edges::Vector{Tuple{Int,Int}},
                                 hyperedges::Vector{Vector{Int}},
                                 n_nodes::Int, r::Float64;
                                 rng::AbstractRNG=MersenneTwister(42))::SimpleGraph
    g = SimpleGraph(n_nodes)
    for (u, v) in base_edges
        add_edge!(g, u+1, v+1)
    end
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
# Resolution sweep
# ─────────────────────────────────────────────────────────────────

function resolution_sweep_large(net_id::String;
                                  n_points::Int=11,
                                  n_seeds::Int=3,
                                  max_edges::Int=2000,
                                  epsilon::Float64=0.1)
    json_path = joinpath(@__DIR__, "..", "..", "data", "processed", "$(net_id)_hyperedges.json")

    if !isfile(json_path)
        println("  SKIP $net_id — no hyperedge file at $json_path")
        return nothing
    end

    println("\n" * "="^60)
    println("Resolution Curvature (Sinkhorn, large-scale): $net_id")
    println("="^60)

    data = JSON.parsefile(json_path)
    n_nodes = data["n_nodes"]

    hyperedges = Vector{Vector{Int}}()
    for he in get(data, "synset_hyperedges", [])
        push!(hyperedges, Int.(he))
    end
    for he in get(data, "hypernymy_hyperedges", [])
        push!(hyperedges, Int.(he))
    end
    hyperedges = unique(sort.(hyperedges))

    # Load base edges
    base_edges = Tuple{Int,Int}[]
    # Map network ID to edge filename (some use different naming)
    edge_name_map = Dict(
        "wordnet_en" => "wordnet_edges.csv",
    )
    edge_fname = get(edge_name_map, net_id, "$(net_id)_edges.csv")
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
    println("  Sinkhorn ε: $epsilon")
    println("  Max edges per ORC: $max_edges")

    r_values = range(0.0, 1.0, length=n_points)
    results_data = []

    for r in r_values
        t0 = time()
        kappas_seeds = Float64[]
        for seed in 1:n_seeds
            rng = MersenneTwister(42 + seed)
            g = build_resolution_graph(base_edges, hyperedges, n_nodes, r; rng=rng)

            if nv(g) < 2 || ne(g) == 0
                push!(kappas_seeds, NaN)
                continue
            end

            km = compute_graph_orc_sinkhorn(g;
                alpha=0.5, max_edges=max_edges, epsilon=epsilon,
                lazy_bfs=(nv(g) > 2000))
            push!(kappas_seeds, km)
        end

        valid_seeds = filter(!isnan, kappas_seeds)
        km = isempty(valid_seeds) ? NaN : mean(valid_seeds)
        ks = isempty(valid_seeds) || length(valid_seeds) < 2 ? NaN : std(valid_seeds)

        # Edge count at this resolution
        rng = MersenneTwister(43)
        g_sample = build_resolution_graph(base_edges, hyperedges, n_nodes, r; rng=rng)
        k_mean = 2 * ne(g_sample) / nv(g_sample)
        eta = k_mean^2 / nv(g_sample)

        elapsed = time() - t0

        push!(results_data, Dict(
            "r" => r,
            "kappa_mean" => km,
            "kappa_std" => ks,
            "n_edges" => ne(g_sample),
            "n_seeds" => length(valid_seeds),
            "k_mean" => k_mean,
            "eta" => eta,
            "time_sec" => elapsed,
        ))

        sign_str = isnan(km) ? "NaN" : (km < 0 ? "−" : "+")
        println("  r=$(round(r, digits=2))  κ̄=$(isnan(km) ? "NaN" : round(km, digits=4))  " *
                "E=$(ne(g_sample))  η=$(round(eta, digits=2))  " *
                "[$sign_str]  $(round(elapsed, digits=1))s")
    end

    out = Dict(
        "network" => net_id,
        "n_nodes" => n_nodes,
        "n_base_edges" => length(base_edges),
        "n_hyperedges" => length(hyperedges),
        "n_points" => n_points,
        "n_seeds" => n_seeds,
        "max_edges" => max_edges,
        "sinkhorn_epsilon" => epsilon,
        "resolution_curve" => results_data,
    )

    out_path = joinpath(@__DIR__, "..", "..", "results", "experiments", "resolution_$(net_id).json")
    mkpath(dirname(out_path))
    open(out_path, "w") do f
        JSON.print(f, out, 2)
    end
    println("  Saved to $out_path")
    return out
end

# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────

NETWORKS = [
    # Can also run on existing small networks for validation
    # "wordnet_en",
    # "conceptnet_en",
    "swow_rp_full",
]

println("Resolution-Dependent Curvature Analysis (Large-Scale Sinkhorn)")
println("Threads: $(Threads.nthreads())")
println("Networks: $(join(NETWORKS, ", "))")

for net_id in NETWORKS
    resolution_sweep_large(net_id; n_points=11, n_seeds=3, max_edges=2000, epsilon=0.1)
end

println("\nAll resolution sweeps complete.")
