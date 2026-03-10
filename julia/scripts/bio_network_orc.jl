"""
Biological Network ORC — Discovery G

Computes exact LP Ollivier-Ricci curvature on 5 canonical biological networks:
  1. C. elegans neural connectome
  2. Yeast S. cerevisiae PPI (STRING, score ≥ 900)
  3. E. coli gene regulatory network
  4. E. coli PPI (STRING, score ≥ 990)
  5. C. elegans metabolic network

Applies the two-parameter model (η, C) to predict geometry and compares
against semantic networks — tests universality of the phase boundary.

Output: results/experiments/bio_network_orc.json
"""

using Pkg
Pkg.activate(joinpath(@__DIR__, ".."))

try
    using JuMP, HiGHS
catch
    Pkg.add(["JuMP", "HiGHS"])
    using JuMP, HiGHS
end

using Graphs, Statistics, Random, JSON, CSV, Printf

const DATA_DIR    = joinpath(@__DIR__, "..", "..", "data", "processed")
const RESULTS_DIR = joinpath(@__DIR__, "..", "..", "results", "experiments")

# ─── ORC machinery ────────────────────────────────────────────────────────────

function exact_wasserstein1(mu::Vector{Float64}, nu::Vector{Float64},
                             cost_matrix::Matrix{Float64})::Float64
    n = length(mu)
    model = Model(HiGHS.Optimizer)
    set_silent(model)
    @variable(model, γ[1:n, 1:n] >= 0)
    @constraint(model, [i=1:n], sum(γ[i, :]) == mu[i])
    @constraint(model, [j=1:n], sum(γ[:, j]) == nu[j])
    @objective(model, Min, sum(cost_matrix[i,j] * γ[i,j] for i in 1:n, j in 1:n))
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
    n  = length(all_nodes)
    μv = [get(mu_u, nd, 0.0) for nd in all_nodes]
    νv = [get(mu_v, nd, 0.0) for nd in all_nodes]
    du = bfs_distances(g, u)
    C  = [abs(du[all_nodes[i]] - du[all_nodes[j]]) for i in 1:n, j in 1:n]
    return 1.0 - exact_wasserstein1(μv, νv, C)
end

function graph_orc(g::SimpleGraph; alpha::Float64=0.5)
    es = collect(edges(g))
    κs = [edge_curvature(g, src(e), dst(e); alpha=alpha) for e in es]
    return κs
end

# ─── Load edge list ───────────────────────────────────────────────────────────

function load_edgelist(path::String)::SimpleGraph
    node_map = Dict{String, Int}()
    id = Ref(0)
    edges_raw = Tuple{Int,Int}[]
    for line in eachline(path)
        startswith(line, "source") && continue  # header
        parts = split(strip(line), ",")
        length(parts) < 2 && continue
        s, t = strip(parts[1]), strip(parts[2])
        s == t && continue
        u = get!(node_map, s, (id[] += 1; id[]))
        v = get!(node_map, t, (id[] += 1; id[]))
        push!(edges_raw, (u, v))
    end
    n = length(node_map)
    g = SimpleGraph(n)
    for (u, v) in edges_raw
        add_edge!(g, u, v)
    end
    return g
end

function mean_clustering(g::SimpleGraph)::Float64
    n = nv(g)
    n == 0 && return 0.0
    return mean(local_clustering_coefficient(g, v) for v in 1:n)
end

# ─── Phase prediction ─────────────────────────────────────────────────────────

function predict_geometry(η, C; eta_c_inf=3.75, C_star=0.05)::String
    if η > eta_c_inf
        return "Spherical"
    elseif C >= C_star
        return "Hyperbolic"
    else
        return "Euclidean"
    end
end

# ─── Networks to analyze ──────────────────────────────────────────────────────

networks = [
    (id="celegans_neural",    file="bio_celegans_edges.csv",
     label="C. elegans neural", source="White et al. 1986 via Netzschleuder"),
    (id="ecoli_grn",          file="bio_ecoli_grn_edges.csv",
     label="E. coli GRN",       source="Shen-Orr 2002 via Netzschleuder"),
    (id="ecoli_ppi",          file="bio_ecoli_ppi_edges.csv",
     label="E. coli PPI",       source="STRING v12, score≥990"),
    (id="celegans_metabolic", file="bio_celegans_metabolic_edges.csv",
     label="C. elegans metabolic", source="Netzschleuder"),
    (id="yeast_ppi",          file="bio_yeast_ppi_edges.csv",
     label="Yeast PPI",          source="STRING v12, score≥900, 20-core"),
]

results = []

for net in networks
    path = joinpath(DATA_DIR, net.file)
    if !isfile(path)
        println("SKIP $(net.id) — file not found")
        continue
    end

    g = load_edgelist(path)
    # Use LCC
    comps = connected_components(g)
    lcc_nodes = comps[argmax(length.(comps))]
    g_lcc = induced_subgraph(g, lcc_nodes)[1]

    N  = nv(g_lcc)
    E  = ne(g_lcc)
    k̄  = 2.0 * E / N
    C  = mean_clustering(g_lcc)
    η  = k̄^2 / N
    pred = predict_geometry(η, C)

    @printf("\n=== %s (N=%d, E=%d, <k>=%.2f, C=%.3f, η=%.3f) ===\n",
            net.label, N, E, k̄, C, η)
    @printf("  Predicted geometry: %s\n", pred)

    # Exact LP ORC (skip if > 8000 edges — use mean estimate from η instead)
    if E > 8000
        println("  NOTE: E=$E > 8000, skipping exact LP (too slow). Using η-model prediction only.")
        push!(results, Dict(
            "network_id" => net.id, "label" => net.label, "source" => net.source,
            "N" => N, "E" => E, "k_mean" => k̄, "C" => C, "eta" => η,
            "kappa_mean" => nothing, "kappa_std" => nothing,
            "predicted_geometry" => pred, "method" => "eta_model_only",
            "note" => "E>8000 edges, exact LP skipped"
        ))
        continue
    end

    κs   = graph_orc(g_lcc)
    κ̄    = mean(κs)
    κσ   = std(κs)
    actual = κ̄ > 0.02 ? "Spherical" : (κ̄ < -0.02 ? "Hyperbolic" : "Euclidean")
    correct = pred == actual

    @printf("  κ̄ = %.4f ± %.4f  → %s  [pred=%s, %s]\n",
            κ̄, κσ, actual, pred, correct ? "✓" : "✗")

    push!(results, Dict(
        "network_id" => net.id, "label" => net.label, "source" => net.source,
        "N" => N, "E" => E, "k_mean" => k̄, "C" => C, "eta" => η,
        "kappa_mean" => κ̄, "kappa_std" => κσ,
        "predicted_geometry" => pred, "actual_geometry" => actual,
        "prediction_correct" => correct, "method" => "exact_LP"
    ))
end

output = Dict(
    "experiment"  => "bio_network_orc",
    "description" => "Exact LP ORC on 5 canonical biological networks",
    "eta_c_inf"   => 3.75, "C_star" => 0.05, "alpha" => 0.5,
    "results"     => results
)

out_path = joinpath(RESULTS_DIR, "bio_network_orc.json")
open(out_path, "w") do f; JSON.print(f, output, 2); end
println("\nSaved to $out_path")
