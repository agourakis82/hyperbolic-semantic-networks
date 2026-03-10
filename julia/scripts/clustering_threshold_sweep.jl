"""
Clustering Threshold Sweep
Probes whether mean ORC transitions sign near C* ~ 0.05.

Generates Watts-Strogatz graphs with controlled clustering C ∈ [0.01, 0.15]
at fixed eta << eta_c, computes exact LP curvature, and records kappa_mean vs C.

Output: results/experiments/clustering_threshold_sweep.json
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
    idx = Dict(node => i for (i, node) in enumerate(all_nodes))

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

function mean_curvature(g::SimpleGraph)::Float64
    es = collect(edges(g))
    isempty(es) && return 0.0
    kappas = [edge_curvature(g, src(e), dst(e)) for e in es]
    return mean(kappas)
end

function watts_strogatz_clustering(n::Int, k::Int, beta::Float64, rng::AbstractRNG)::SimpleGraph
    g = SimpleGraph(n)
    for i in 1:n, j in 1:k÷2
        add_edge!(g, i, mod1(i+j, n))
    end
    for i in 1:n, j in 1:k÷2
        if rand(rng) < beta
            u = i
            v = mod1(i+j, n)
            rem_edge!(g, u, v)
            w = rand(rng, 1:n)
            attempts = 0
            while (w == u || has_edge(g, u, w)) && attempts < 100
                w = rand(rng, 1:n)
                attempts += 1
            end
            if w != u && !has_edge(g, u, w)
                add_edge!(g, u, w)
            else
                add_edge!(g, u, v)
            end
        end
    end
    return g
end

function mean_clustering(g::SimpleGraph)::Float64
    n = nv(g)
    n == 0 && return 0.0
    cc = [local_clustering_coefficient(g, v) for v in 1:n]
    return mean(cc)
end

function density_parameter(g::SimpleGraph)::Float64
    n = nv(g)
    n == 0 && return 0.0
    k_mean = 2.0 * ne(g) / n
    return k_mean^2 / n
end

function main()
    N = 200
    k = 4
    n_graphs = 20
    beta_values = [0.001, 0.005, 0.01, 0.02, 0.05, 0.10, 0.20, 0.40, 0.70, 1.0]

    results = []

    for beta in beta_values
        kappa_vals = Float64[]
        C_vals = Float64[]
        eta_vals = Float64[]

        for seed in 1:n_graphs
            rng = MersenneTwister(seed)
            g = watts_strogatz_clustering(N, k, beta, rng)
            C = mean_clustering(g)
            eta = density_parameter(g)
            kappa = mean_curvature(g)
            push!(C_vals, C)
            push!(eta_vals, eta)
            push!(kappa_vals, kappa)
        end

        push!(results, Dict(
            "beta" => beta,
            "C_mean" => mean(C_vals),
            "C_std" => std(C_vals),
            "eta_mean" => mean(eta_vals),
            "kappa_mean" => mean(kappa_vals),
            "kappa_std" => std(kappa_vals),
            "n_graphs" => n_graphs,
            "N" => N,
            "k" => k
        ))
        println("beta=$(beta)  C=$(round(mean(C_vals),digits=3))  eta=$(round(mean(eta_vals),digits=3))  kappa=$(round(mean(kappa_vals),digits=4))")
    end

    output = Dict(
        "experiment" => "clustering_threshold_sweep",
        "description" => "Watts-Strogatz sweep: mean ORC vs clustering at fixed eta<<eta_c",
        "method" => "exact_LP",
        "solver" => "HiGHS",
        "results" => results
    )

    out_path = joinpath(@__DIR__, "..", "..", "results", "experiments", "clustering_threshold_sweep.json")
    open(out_path, "w") do f
        JSON.print(f, output, 2)
    end
    println("\nSaved to $out_path")
end

main()
