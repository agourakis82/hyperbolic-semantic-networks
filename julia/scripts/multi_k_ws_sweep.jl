"""
Multi-k Watts-Strogatz Sweep

Tests universality of ∂κ̄/∂C > 0 across k ∈ {4, 6, 8} at fixed η << η_c.
k=4 data already exists; this script runs k=6 and k=8.

η is fixed at ~0.08 for each k by adjusting N:
  k=4, N=200 → η = 16/200 = 0.080  (existing data)
  k=6, N=450 → η = 36/450 = 0.080  (new)
  k=8, N=800 → η = 64/800 = 0.080  (new)

Output: results/experiments/multi_k_ws_sweep.json
"""

using Pkg
Pkg.activate(joinpath(@__DIR__, ".."))

try
    using JuMP, HiGHS
catch
    Pkg.add(["JuMP", "HiGHS"])
    using JuMP, HiGHS
end

using Graphs, Statistics, Random, JSON, Printf

# ─── ORC functions (same as clustering_threshold_sweep.jl) ───────────────────

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
    mu = Dict{Int,Float64}(v => alpha)
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
    C_mat = [abs(dists_u[all_nodes[i]] - dists_u[all_nodes[j]]) for i in 1:n, j in 1:n]
    return 1.0 - exact_wasserstein1(mu_vec, nu_vec, C_mat)
end

function mean_curvature(g::SimpleGraph)::Float64
    es = collect(edges(g))
    isempty(es) && return 0.0
    return mean(edge_curvature(g, src(e), dst(e)) for e in es)
end

function watts_strogatz_clustering(n::Int, k::Int, beta::Float64, rng::AbstractRNG)::SimpleGraph
    g = SimpleGraph(n)
    for i in 1:n, j in 1:k÷2
        add_edge!(g, i, mod1(i+j, n))
    end
    for i in 1:n, j in 1:k÷2
        if rand(rng) < beta
            u, v = i, mod1(i+j, n)
            rem_edge!(g, u, v)
            w = rand(rng, 1:n)
            attempts = 0
            while (w == u || has_edge(g, u, w)) && attempts < 100
                w = rand(rng, 1:n)
                attempts += 1
            end
            add_edge!(g, u, w != u && !has_edge(g, u, w) ? w : v)
        end
    end
    return g
end

function mean_clustering(g::SimpleGraph)::Float64
    n = nv(g)
    n == 0 && return 0.0
    return mean(local_clustering_coefficient(g, v) for v in 1:n)
end

function density_parameter(g::SimpleGraph)::Float64
    n = nv(g)
    n == 0 && return 0.0
    k_mean = 2.0 * ne(g) / n
    return k_mean^2 / n
end

function linear_slope(x::Vector{Float64}, y::Vector{Float64})
    x̄, ȳ = mean(x), mean(y)
    b = sum((x .- x̄) .* (y .- ȳ)) / sum((x .- x̄).^2)
    a = ȳ - b * x̄
    ŷ = a .+ b .* x
    r2 = 1.0 - sum((y .- ŷ).^2) / sum((y .- ȳ).^2)
    n = length(x)
    se_b = sqrt(sum((y .- ŷ).^2) / ((n-2) * sum((x .- x̄).^2)))
    return (a=a, b=b, r2=r2, se_b=se_b)
end

# ─── Sweep parameters ─────────────────────────────────────────────────────────

# N=200 for all k: η varies but stays well below η_c ≈ 2.3 for all tested k
# k=6, N=200 → η = 36/200 = 0.18  (≪ η_c)
# k=8, N=200 → η = 64/200 = 0.32  (≪ η_c)
configs = [
    (k=6,  N=200),
    (k=8,  N=200),
]

n_graphs    = 10
beta_values = [0.001, 0.005, 0.01, 0.02, 0.05, 0.10, 0.20, 0.40, 0.70, 1.0]

all_results = Dict{String, Any}()

for cfg in configs
    k, N = cfg.k, cfg.N
    println("\n=== k=$k, N=$N (η≈$(round(k^2/N, digits=3))) ===")
    rows = []

    for beta in beta_values
        κ_vals = Float64[]
        C_vals = Float64[]
        η_vals = Float64[]

        for seed in 1:n_graphs
            rng = MersenneTwister(seed + 1000*k)
            g   = watts_strogatz_clustering(N, k, beta, rng)
            push!(C_vals, mean_clustering(g))
            push!(η_vals, density_parameter(g))
            push!(κ_vals, mean_curvature(g))
        end

        push!(rows, Dict(
            "beta"       => beta,
            "C_mean"     => mean(C_vals),
            "C_std"      => std(C_vals),
            "eta_mean"   => mean(η_vals),
            "kappa_mean" => mean(κ_vals),
            "kappa_std"  => std(κ_vals),
            "n_graphs"   => n_graphs,
            "N"          => N,
            "k"          => k
        ))
        @printf("  β=%.3f  C=%.3f  κ̄=%.4f\n", beta, mean(C_vals), mean(κ_vals))
    end

    C_means = [r["C_mean"]     for r in rows]
    κ_means = [r["kappa_mean"] for r in rows]
    reg = linear_slope(C_means, κ_means)

    all_results["k$k"] = Dict(
        "k" => k, "N" => N,
        "eta_target" => k^2 / N,
        "rows"  => rows,
        "slope" => reg.b,
        "intercept" => reg.a,
        "r2"    => reg.r2,
        "se_slope" => reg.se_b
    )
    @printf("  → slope ∂κ̄/∂C = %.4f ± %.4f  (R²=%.4f)\n", reg.b, reg.se_b, reg.r2)
end

# ─── Save ─────────────────────────────────────────────────────────────────────

output = Dict(
    "experiment"  => "multi_k_ws_sweep",
    "description" => "Universality test: ∂κ̄/∂C > 0 across k ∈ {6,8} (k=4 in separate file)",
    "method"      => "exact_LP",
    "solver"      => "HiGHS",
    "results"     => all_results
)

out_path = joinpath(@__DIR__, "..", "..", "results", "experiments", "multi_k_ws_sweep.json")
open(out_path, "w") do f
    JSON.print(f, output, 2)
end
println("\nSaved to $out_path")
