"""
multi_curvature_comparison.jl — Forman-Ricci + LLY curvature for all semantic networks

Computes three curvature notions for comparison with ORC (from unified_semantic_orc.jl):
  1. Forman-Ricci curvature: F(e) = 4 - deg(u) - deg(v) + 3·triangles(e)
  2. Lin-Lu-Yau (LLY) curvature (α=0): κ_LLY = triangles(e)/max(deg(u),deg(v))
     (Simplified formula valid for α=0, see Lin-Lu-Yau 2011)

Usage:
    julia --project=julia -t 8 julia/scripts/multi_curvature_comparison.jl
"""

import Pkg
Pkg.instantiate()

using Graphs
using Statistics
using JSON
using CSV
using DataFrames
using Printf

# ─────────────────────────────────────────────────────────────────
# Network registry (reused from unified_semantic_orc.jl)
# ─────────────────────────────────────────────────────────────────

const DATA_DIR = joinpath(@__DIR__, "..", "..", "data", "processed")
const RESULTS_DIR = joinpath(@__DIR__, "..", "..", "results", "experiments")

struct NetworkSpec
    id::String
    filename::String
    category::String
    language::String
    has_relation::Bool
end

const NETWORKS = [
    NetworkSpec("swow_es", "spanish_edges_FINAL.csv", "association", "Spanish", false),
    NetworkSpec("swow_en", "english_edges_FINAL.csv", "association", "English", false),
    NetworkSpec("swow_zh", "chinese_edges_FINAL.csv", "association", "Chinese", false),
    NetworkSpec("swow_nl", "dutch_edges.csv", "association", "Dutch", false),
    NetworkSpec("conceptnet_en", "conceptnet_en_edges.csv", "knowledge", "English", true),
    NetworkSpec("conceptnet_pt", "conceptnet_pt_edges.csv", "knowledge", "Portuguese", true),
    NetworkSpec("wordnet_en", "wordnet_edges.csv", "taxonomy", "English", true),
    NetworkSpec("wordnet_en_2k", "wordnet_N2000_edges.csv", "taxonomy", "English", true),
    NetworkSpec("babelnet_ru", "babelnet_ru_edges.csv", "taxonomy", "Russian", true),
    NetworkSpec("babelnet_ar", "babelnet_ar_edges.csv", "taxonomy", "Arabic", true),
    NetworkSpec("eat_en", "eat_en_edges.csv", "association", "British English", false),
    NetworkSpec("framenet_en", "framenet_en_edges.csv", "frames", "English", false),
    NetworkSpec("swow_rp", "swow_rp_edges.csv", "association", "Arg. Spanish", false),
    NetworkSpec("wordnet_de", "wordnet_de_edges.csv", "taxonomy", "German", false),
    NetworkSpec("usf_en", "usf_en_edges.csv", "association", "American English", false),
    NetworkSpec("depression_minimum", "depression_networks_optimal/depression_minimum_edges.csv", "clinical", "English", false),
]

# ─────────────────────────────────────────────────────────────────
# CSV loader (simplified from unified_semantic_orc.jl)
# ─────────────────────────────────────────────────────────────────

function load_network(spec::NetworkSpec)
    csv_path = joinpath(DATA_DIR, spec.filename)
    if !isfile(csv_path)
        return nothing
    end

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
    for (u, v) in edge_list
        add_edge!(g, u, v)
    end

    # Largest connected component
    cc = connected_components(g)
    if length(cc) > 1
        largest = cc[argmax(length.(cc))]
        g, _ = induced_subgraph(g, largest)
    end

    return g
end

# ─────────────────────────────────────────────────────────────────
# Curvature computations
# ─────────────────────────────────────────────────────────────────

"""Count triangles containing edge (u,v)."""
function edge_triangles(g::SimpleGraph, u::Int, v::Int)::Int
    return length(intersect(Set(neighbors(g, u)), Set(neighbors(g, v))))
end

"""
Forman-Ricci curvature for edge (u,v):
  F(u,v) = 4 - deg(u) - deg(v) + 3·triangles(u,v)
"""
function forman_ricci(g::SimpleGraph, u::Int, v::Int)::Float64
    t = edge_triangles(g, u, v)
    return 4.0 - degree(g, u) - degree(g, v) + 3.0 * t
end

"""
Lin-Lu-Yau curvature (α=0) for edge (u,v):
  κ_LLY(u,v) = triangles(u,v) / max(deg(u), deg(v)) - 1 + 1/max(deg(u),deg(v))

Simplified from the full LLY formula for α=0 (no idleness).
Actually uses the exact Lin-Lu-Yau 2011 formula:
  κ_LLY(u,v) = (triangles(u,v) / max(deg(u),deg(v))) + (triangles(u,v) / min(deg(u),deg(v))) - 1
  when both endpoints have degree ≥ 2.
"""
function lly_curvature(g::SimpleGraph, u::Int, v::Int)::Float64
    du = degree(g, u)
    dv = degree(g, v)
    (du < 1 || dv < 1) && return 0.0
    t = edge_triangles(g, u, v)
    # Exact LLY formula (Lin-Lu-Yau 2011, Theorem 1.1):
    # κ(x,y) ≥ t/max(d_x, d_y) + t/min(d_x, d_y) + 2/max(d_x, d_y) - 2
    # For adjacent vertices with d(x,y)=1:
    dmax = max(du, dv)
    dmin = min(du, dv)
    return t / dmax + t / dmin + 2.0 / dmax - 2.0
end

"""Compute global clustering coefficient."""
function clustering_coefficient(g::SimpleGraph)::Float64
    triangles = 0
    triples = 0
    for v in vertices(g)
        d = degree(g, v)
        if d >= 2
            nbrs = neighbors(g, v)
            tri_v = 0
            for i in 1:length(nbrs)
                for j in (i+1):length(nbrs)
                    if has_edge(g, nbrs[i], nbrs[j])
                        tri_v += 1
                    end
                end
            end
            triangles += tri_v
            triples += d * (d - 1) ÷ 2
        end
    end
    triples == 0 && return 0.0
    return triangles / triples
end

# ─────────────────────────────────────────────────────────────────
# Main analysis
# ─────────────────────────────────────────────────────────────────

function analyze_network(spec::NetworkSpec)
    g = load_network(spec)
    isnothing(g) && return nothing

    N = nv(g)
    E = ne(g)
    kavg = 2.0 * E / N
    eta = kavg^2 / N
    C = clustering_coefficient(g)

    edge_list = collect(edges(g))

    # Forman-Ricci
    forman_vals = [forman_ricci(g, src(e), dst(e)) for e in edge_list]
    forman_mean = mean(forman_vals)
    forman_std = std(forman_vals)
    forman_neg = count(x -> x < 0, forman_vals) / length(forman_vals)

    # LLY
    lly_vals = [lly_curvature(g, src(e), dst(e)) for e in edge_list]
    lly_mean = mean(lly_vals)
    lly_std = std(lly_vals)
    lly_neg = count(x -> x < 0, lly_vals) / length(lly_vals)

    # Classify
    forman_geo = forman_mean < -0.5 ? "HYPERBOLIC" : (forman_mean > 0.5 ? "SPHERICAL" : "EUCLIDEAN")
    lly_geo = lly_mean < -0.01 ? "HYPERBOLIC" : (lly_mean > 0.01 ? "SPHERICAL" : "EUCLIDEAN")

    println("  $(rpad(spec.id, 20)) N=$(lpad(N,5)) E=$(lpad(E,6)) η=$(lpad(@sprintf("%.3f", eta),6)) " *
            "C=$(lpad(@sprintf("%.3f", C),5)) | " *
            "Forman=$(lpad(@sprintf("%.3f", forman_mean),8)) [$(forman_geo)] | " *
            "LLY=$(lpad(@sprintf("%.4f", lly_mean),8)) [$(lly_geo)]")

    return Dict(
        "network" => spec.id,
        "category" => spec.category,
        "language" => spec.language,
        "N" => N, "E" => E,
        "kavg" => kavg, "eta" => eta, "C" => C,
        "forman" => Dict(
            "mean" => forman_mean, "std" => forman_std,
            "fraction_negative" => forman_neg,
            "geometry" => forman_geo,
        ),
        "lly" => Dict(
            "mean" => lly_mean, "std" => lly_std,
            "fraction_negative" => lly_neg,
            "geometry" => lly_geo,
        ),
    )
end

# ─────────────────────────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────────────────────────

println("=" ^ 120)
println("MULTI-CURVATURE COMPARISON: Forman-Ricci + LLY for Semantic Networks")
println("=" ^ 120)
println()

all_results = Dict[]
for spec in NETWORKS
    r = analyze_network(spec)
    !isnothing(r) && push!(all_results, r)
end

# Save results
out_path = joinpath(RESULTS_DIR, "multi_curvature_comparison.json")
open(out_path, "w") do f
    JSON.print(f, all_results, 2)
end
println("\nSaved $(length(all_results)) networks to $out_path")

# Summary: sign agreement with ORC
println("\n" * "=" ^ 80)
println("SIGN AGREEMENT SUMMARY")
println("=" ^ 80)

# Load ORC results for comparison
orc_results = Dict{String, Float64}()
for net_id in [r["network"] for r in all_results]
    orc_file = joinpath(@__DIR__, "..", "..", "results", "unified", "$(net_id)_exact_lp.json")
    if isfile(orc_file)
        orc_data = JSON.parsefile(orc_file)
        orc_results[net_id] = get(orc_data, "kappa_mean", NaN)
    end
end

println("  $(rpad("Network", 22)) $(rpad("ORC", 10)) $(rpad("Forman", 10)) $(rpad("LLY", 10)) ORC-Forman  ORC-LLY")
println("  " * "-"^74)
for r in all_results
    net = r["network"]
    orc_val = get(orc_results, net, NaN)
    forman_val = r["forman"]["mean"]
    lly_val = r["lly"]["mean"]

    orc_sign = isnan(orc_val) ? "?" : (orc_val < -0.01 ? "-" : (orc_val > 0.01 ? "+" : "0"))
    forman_sign = forman_val < -0.5 ? "-" : (forman_val > 0.5 ? "+" : "0")
    lly_sign = lly_val < -0.01 ? "-" : (lly_val > 0.01 ? "+" : "0")

    agree_forman = orc_sign == "?" ? "?" : (orc_sign == forman_sign ? "✓" : "✗")
    agree_lly = orc_sign == "?" ? "?" : (orc_sign == lly_sign ? "✓" : "✗")

    println("  $(rpad(net, 22)) $(rpad(isnan(orc_val) ? "N/A" : @sprintf("%.4f", orc_val), 10)) " *
            "$(rpad(@sprintf("%.3f", forman_val), 10)) $(rpad(@sprintf("%.4f", lly_val), 10)) " *
            "$(rpad(agree_forman, 11)) $(agree_lly)")
end

println("\nDone.")
