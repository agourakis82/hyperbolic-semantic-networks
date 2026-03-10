"""
forman_ricci.jl — Scalable Forman-Ricci curvature on large semantic networks

Demonstrates O(E) scalability vs O(N³·E) exact LP ORC.
Runs on full-scale networks (N > 1000) that are infeasible for exact ORC.

Usage:
    julia --project=julia julia/scripts/forman_ricci.jl
"""

import Pkg
Pkg.instantiate()

using Graphs, Statistics, JSON, Printf

const DATA_DIR = joinpath(@__DIR__, "..", "..", "data", "processed")

function load_graph(csv_path::String)
    node_map = Dict{String,Int}()
    edge_list = Tuple{Int,Int}[]
    open(csv_path) do f
        for line in eachline(f)
            startswith(line, "source") && continue
            startswith(line, "#") && continue
            parts = split(strip(line), ",")
            length(parts) < 2 && continue
            s, t = parts[1], parts[2]
            s == t && continue
            if !haskey(node_map, s); node_map[s] = length(node_map) + 1; end
            if !haskey(node_map, t); node_map[t] = length(node_map) + 1; end
            push!(edge_list, (node_map[s], node_map[t]))
        end
    end
    N = length(node_map)
    g = SimpleGraph(N)
    for (u, v) in edge_list; add_edge!(g, u, v); end
    cc = connected_components(g)
    if length(cc) > 1
        largest = cc[argmax(length.(cc))]
        g, _ = induced_subgraph(g, largest)
    end
    return g
end

function edge_triangles(g, u, v)
    length(intersect(Set(neighbors(g, u)), Set(neighbors(g, v))))
end

function forman_all(g::SimpleGraph)
    edge_list = collect(edges(g))
    vals = Vector{Float64}(undef, length(edge_list))
    Threads.@threads for i in 1:length(edge_list)
        e = edge_list[i]
        u, v = src(e), dst(e)
        t = edge_triangles(g, u, v)
        vals[i] = 4.0 - degree(g, u) - degree(g, v) + 3.0 * t
    end
    return vals
end

function clustering_coefficient(g::SimpleGraph)
    triangles = 0; triples = 0
    for v in vertices(g)
        d = degree(g, v)
        d < 2 && continue
        nbrs = neighbors(g, v)
        tri_v = 0
        for i in 1:length(nbrs), j in (i+1):length(nbrs)
            has_edge(g, nbrs[i], nbrs[j]) && (tri_v += 1)
        end
        triangles += tri_v
        triples += d * (d - 1) ÷ 2
    end
    triples == 0 ? 0.0 : triangles / triples
end

# Large-scale networks
LARGE_NETWORKS = [
    ("swow_en_full", "english_edges.csv"),
    ("swow_es_full", "spanish_edges.csv"),
    ("swow_zh_full", "chinese_edges.csv"),
    ("swow_nl_full", "dutch_edges.csv"),
    ("conceptnet_en_full", "conceptnet_en_edges.csv"),
    ("conceptnet_pt_full", "conceptnet_pt_edges.csv"),
    ("wordnet_en_2k", "wordnet_N2000_edges.csv"),
    ("eat_en", "eat_en_edges.csv"),
    ("depression_expanded", "depression_expanded_10bins.csv"),
]

println("=" ^ 90)
println("FORMAN-RICCI CURVATURE — Large-Scale Networks (O(E) computation)")
println("=" ^ 90)

all_results = Dict[]
for (net_id, filename) in LARGE_NETWORKS
    csv_path = joinpath(DATA_DIR, filename)
    !isfile(csv_path) && (println("  SKIP $net_id"); continue)

    t0 = time()
    g = load_graph(csv_path)
    N = nv(g); E = ne(g)
    kavg = 2.0 * E / N
    eta = kavg^2 / N

    vals = forman_all(g)
    C = clustering_coefficient(g)
    elapsed = time() - t0

    fm = mean(vals)
    fs = std(vals)
    frac_neg = count(x -> x < 0, vals) / length(vals)

    println(@sprintf("  %-22s N=%6d E=%7d ⟨k⟩=%6.1f η=%8.3f C=%.3f | F̄=%9.2f ± %7.2f  (%.1fs)",
            net_id, N, E, kavg, eta, C, fm, fs, elapsed))

    push!(all_results, Dict(
        "network" => net_id, "N" => N, "E" => E,
        "kavg" => kavg, "eta" => eta, "C" => C,
        "forman_mean" => fm, "forman_std" => fs,
        "fraction_negative" => frac_neg,
        "compute_time_s" => elapsed,
    ))
end

out_path = joinpath(@__DIR__, "..", "..", "results", "experiments", "forman_large_scale.json")
open(out_path, "w") do f
    JSON.print(f, all_results, 2)
end
println("\nSaved to $out_path")
println("Done.")
