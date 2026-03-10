"""
Dense Network Validation
Constructs additional dense networks (eta > eta_c) to confirm the spherical prediction.

Strategy: Use ConceptNet English edges with progressively lower weight thresholds
to build networks with increasing density, then compute exact LP curvature.
Also generates synthetic dense random regular graphs as a controlled baseline.

Output: results/experiments/dense_network_validation.json
"""

using Pkg
Pkg.activate(joinpath(@__DIR__, ".."))

try
    using JuMP, HiGHS
catch
    Pkg.add(["JuMP", "HiGHS"])
    using JuMP, HiGHS
end

using Graphs
using Statistics
using Random
using JSON
using CSV
using DataFrames

function exact_wasserstein1(mu::Vector{Float64}, nu::Vector{Float64},
                             cost_matrix::Matrix{Float64})::Float64
    n = length(mu)
    model = Model(HiGHS.Optimizer)
    set_silent(model)
    @variable(model, gamma[1:n, 1:n] >= 0)
    @constraint(model, [i=1:n], sum(gamma[i, :]) == mu[i])
    @constraint(model, [j=1:n], sum(gamma[:, j]) == nu[j])
    @objective(model, Min, sum(cost_matrix[i,j] * gamma[i,j] for i in 1:n, j in 1:n))
    optimize!(model)
    return objective_value(model)
end

function build_lazy_measure(g::SimpleGraph, v::Int; alpha::Float64=0.5)::Dict{Int,Float64}
    mu = Dict{Int,Float64}()
    mu[v] = alpha
    nbrs = neighbors(g, v)
    if !isempty(nbrs)
        w = (1.0 - alpha) / length(nbrs)
        for u in nbrs
            mu[u] = get(mu, u, 0.0) + w
        end
    end
    return mu
end

function bfs_distances(g::SimpleGraph, source::Int)::Vector{Float64}
    n = nv(g)
    dist = fill(Inf, n)
    dist[source] = 0.0
    queue = [source]
    while !isempty(queue)
        u = popfirst!(queue)
        for v in neighbors(g, u)
            if isinf(dist[v])
                dist[v] = dist[u] + 1.0
                push!(queue, v)
            end
        end
    end
    return dist
end

function edge_curvature(g::SimpleGraph, u::Int, v::Int; alpha::Float64=0.5)::Float64
    mu_u = build_lazy_measure(g, u; alpha=alpha)
    mu_v = build_lazy_measure(g, v; alpha=alpha)
    all_nodes = collect(union(keys(mu_u), keys(mu_v)))
    n = length(all_nodes)

    mu_vec = [get(mu_u, nd, 0.0) for nd in all_nodes]
    nu_vec = [get(mu_v, nd, 0.0) for nd in all_nodes]

    dists_u = bfs_distances(g, u)
    C_mat = Matrix{Float64}(undef, n, n)
    for i in 1:n, j in 1:n
        C_mat[i,j] = dists_u[all_nodes[i]] == Inf || dists_u[all_nodes[j]] == Inf ?
                     Float64(nv(g)) : abs(dists_u[all_nodes[i]] - dists_u[all_nodes[j]])
    end

    W1 = exact_wasserstein1(mu_vec, nu_vec, C_mat)
    return 1.0 - W1
end

function sample_edges(g::SimpleGraph, max_edges::Int)
    es = collect(edges(g))
    length(es) <= max_edges && return es
    return sample(es, max_edges; replace=false)
end

function mean_curvature_sampled(g::SimpleGraph; max_edges::Int=500)::Float64
    es = collect(edges(g))
    isempty(es) && return 0.0
    if length(es) > max_edges
        rng = MersenneTwister(42)
        idx = randperm(rng, length(es))[1:max_edges]
        es = es[idx]
    end
    kappas = [edge_curvature(g, src(e), dst(e)) for e in es]
    return mean(kappas)
end

function density_parameter(g::SimpleGraph)::Float64
    n = nv(g)
    n == 0 && return 0.0
    k_mean = 2.0 * ne(g) / n
    return k_mean^2 / n
end

function eta_c(N::Int)::Float64
    return 3.75 - 14.62 / sqrt(N)
end

function synthetic_dense_kregular(N::Int, k::Int, rng::AbstractRNG)::SimpleGraph
    g = SimpleGraph(N)
    for i in 1:N, j in 1:k÷2
        add_edge!(g, i, mod1(i+j, N))
    end
    return g
end

function main()
    results = []

    println("=== Synthetic dense k-regular graphs (eta > eta_c) ===")
    for (N, k) in [(200, 30), (200, 50), (500, 50), (500, 100)]
        rng = MersenneTwister(42)
        g = synthetic_dense_kregular(N, k, rng)
        g = induced_subgraph(g, connected_components(g)[1])[1]
        n_actual = nv(g)
        k_mean = 2.0 * ne(g) / n_actual
        eta = k_mean^2 / n_actual
        ec = eta_c(n_actual)
        kappa = mean_curvature_sampled(g; max_edges=200)
        geometry = kappa > 0.01 ? "SPHERICAL" : kappa < -0.01 ? "HYPERBOLIC" : "EUCLIDEAN"

        push!(results, Dict(
            "network" => "synthetic_kregular_N$(N)_k$(k)",
            "type" => "synthetic",
            "N" => n_actual, "k_mean" => k_mean,
            "eta" => eta, "eta_c" => ec, "eta_gt_etac" => eta > ec,
            "kappa_mean" => kappa, "geometry" => geometry,
            "method" => "exact_LP", "solver" => "HiGHS"
        ))
        println("N=$(n_actual) k=$(k)  eta=$(round(eta,digits=2))  eta_c=$(round(ec,digits=2))  kappa=$(round(kappa,digits=4))  -> $(geometry)")
    end

    println("\n=== ConceptNet English (varying edge threshold) ===")
    cn_path = joinpath(@__DIR__, "..", "..", "data", "processed", "conceptnet_en_edges.csv")
    if isfile(cn_path)
        df = CSV.read(cn_path, DataFrame)
        weight_col = "weight" in names(df) ? :weight : names(df)[3]
        src_col = names(df)[1]
        dst_col = names(df)[2]
        thresholds = [0.5, 0.3, 0.2, 0.1]
        for thresh in thresholds
            df_t = filter(row -> row[weight_col] >= thresh, df)
            nodes = union(Set(df_t[!, src_col]), Set(df_t[!, dst_col]))
            node_idx = Dict(n => i for (i, n) in enumerate(collect(nodes)))
            g = SimpleGraph(length(nodes))
            for row in eachrow(df_t)
                u = get(node_idx, row[src_col], 0)
                v = get(node_idx, row[dst_col], 0)
                u > 0 && v > 0 && u != v && add_edge!(g, u, v)
            end
            cc = connected_components(g)
            g = induced_subgraph(g, cc[argmax(length.(cc))])[1]
            n_actual = nv(g)
            n_actual < 10 && continue
            k_mean = 2.0 * ne(g) / n_actual
            eta = k_mean^2 / n_actual
            ec = eta_c(n_actual)
            kappa = mean_curvature_sampled(g; max_edges=300)
            geometry = kappa > 0.01 ? "SPHERICAL" : kappa < -0.01 ? "HYPERBOLIC" : "EUCLIDEAN"
            push!(results, Dict(
                "network" => "conceptnet_en_thresh$(thresh)",
                "type" => "conceptnet", "weight_threshold" => thresh,
                "N" => n_actual, "k_mean" => k_mean,
                "eta" => eta, "eta_c" => ec, "eta_gt_etac" => eta > ec,
                "kappa_mean" => kappa, "geometry" => geometry,
                "method" => "exact_LP", "solver" => "HiGHS"
            ))
            println("ConceptNet thresh=$(thresh)  N=$(n_actual)  eta=$(round(eta,digits=2))  eta_c=$(round(ec,digits=2))  kappa=$(round(kappa,digits=4))  -> $(geometry)")
        end
    else
        println("ConceptNet edges not found at $cn_path, skipping.")
    end

    output = Dict(
        "experiment" => "dense_network_validation",
        "description" => "Tests spherical prediction (eta > eta_c => kappa > 0) on additional dense networks",
        "method" => "exact_LP", "solver" => "HiGHS",
        "results" => results
    )

    out_path = joinpath(@__DIR__, "..", "..", "results", "experiments", "dense_network_validation.json")
    open(out_path, "w") do f
        JSON.print(f, output, 2)
    end
    println("\nSaved to $out_path")
end

main()
