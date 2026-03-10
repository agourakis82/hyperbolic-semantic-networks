"""
Gromov δ-Hyperbolicity Cross-Validation (Discovery H)

First-ever comparison of Ollivier-Ricci curvature (ORC) and Gromov δ-hyperbolicity
on semantic + biological networks. Tests whether the ORC phase classification agrees
with the classical four-point condition on δ-hyperbolic metric spaces.

Algorithm:
  1. BFS all-pairs distances for each network
  2. Sample 4-tuples and compute δ = (s₁ - s₂)/2 where s₁≥s₂≥s₃ are the sorted
     pair-sums of opposite sides
  3. δ_max = maximum δ over sampled 4-tuples
  4. Cross-validate: does sign(κ̄) agree with δ_max?

Networks (skip if N > 1000 — BFS too slow):
  11 semantic training + 5 held-out + 4 biological = up to 20 networks

Output:
  results/experiments/gromov_hyperbolicity.json
  figures/monograph/figure14_gromov_vs_orc.pdf/.png
"""

using Pkg
Pkg.activate(joinpath(@__DIR__, ".."))

try
    using Graphs, JSON, Statistics, Random, Printf
catch
    Pkg.add(["Graphs", "JSON", "Statistics"])
    using Graphs, JSON, Statistics, Random, Printf
end

import Pkg as PkgPlots
let deps = PkgPlots.project().dependencies
    for pkg in ["Plots", "LaTeXStrings"]
        haskey(deps, pkg) || PkgPlots.add(pkg)
    end
end
using Plots, LaTeXStrings
gr()

const DATA_DIR    = joinpath(@__DIR__, "..", "..", "data", "processed")
const UNIFIED_DIR = joinpath(@__DIR__, "..", "..", "results", "unified")
const RESULTS_DIR = joinpath(@__DIR__, "..", "..", "results", "experiments")
const FIGURES_DIR = joinpath(@__DIR__, "..", "..", "figures", "monograph")

const N_SAMPLES_SMALL = 50_000   # N ≤ 300
const N_SAMPLES_LARGE = 100_000  # N > 300
const MAX_N = 900                 # skip larger networks (too slow)

# ─── Network registry ─────────────────────────────────────────────────────────

const NETWORKS = [
    # (id, csv_file, kappa_json, kappa_field, geometry, label)
    # --- 11 semantic training ---
    ("swow_es",       "spanish_edges_FINAL.csv",    "swow_es_exact_lp.json",       "kappa_mean", "Hyperbolic",  "SWOW Spanish"),
    ("swow_en",       "english_edges_FINAL.csv",    "swow_en_exact_lp.json",       "kappa_mean", "Hyperbolic",  "SWOW English"),
    ("swow_zh",       "chinese_edges_FINAL.csv",    "swow_zh_exact_lp.json",       "kappa_mean", "Hyperbolic",  "SWOW Chinese"),
    ("swow_nl",       "dutch_edges.csv",            "swow_nl_exact_lp.json",       "kappa_mean", "Spherical",   "SWOW Dutch"),
    ("conceptnet_en", "conceptnet_en_edges.csv",    "conceptnet_en_exact_lp.json", "kappa_mean", "Hyperbolic",  "ConceptNet EN"),
    ("conceptnet_pt", "conceptnet_pt_edges.csv",    "conceptnet_pt_exact_lp.json", "kappa_mean", "Hyperbolic",  "ConceptNet PT"),
    ("wordnet_en",    "wordnet_edges.csv",           "wordnet_en_exact_lp.json",    "kappa_mean", "Euclidean",   "WordNet EN"),
    ("babelnet_ar",   "babelnet_ar_edges.csv",      "babelnet_ar_exact_lp.json",   "kappa_mean", "Euclidean",   "BabelNet AR"),
    ("babelnet_ru",   "babelnet_ru_edges.csv",      "babelnet_ru_exact_lp.json",   "kappa_mean", "Euclidean",   "BabelNet RU"),
    # --- 5 held-out semantic ---
    ("swow_rp",       "swow_rp_edges.csv",          "swow_rp_exact_lp.json",       "kappa_mean", "Hyperbolic",  "SWOW Rioplatense"),
    ("eat_en",        "eat_en_edges.csv",            "eat_en_exact_lp.json",        "kappa_mean", "Hyperbolic",  "EAT"),
    ("usf_en",        "usf_en_edges.csv",            "usf_en_exact_lp.json",        "kappa_mean", "Hyperbolic",  "USF"),
    ("wordnet_de",    "wordnet_de_edges.csv",        "wordnet_de_exact_lp.json",    "kappa_mean", "Euclidean",   "WordNet DE"),
    ("framenet_en",   "framenet_en_edges.csv",       "framenet_en_exact_lp.json",   "kappa_mean", "Hyperbolic",  "FrameNet EN"),
    # --- 4 biological (exact LP exists) ---
    ("celegans_neural",    "bio_celegans_edges.csv",          "bio_network_orc.json", "celegans_neural",   "Spherical", "C. elegans neural"),
    ("ecoli_grn",          "bio_ecoli_grn_edges.csv",         "bio_network_orc.json", "ecoli_grn",         "Spherical", "E. coli GRN"),
    ("ecoli_ppi",          "bio_ecoli_ppi_edges.csv",         "bio_network_orc.json", "ecoli_ppi",         "Spherical", "E. coli PPI"),
    ("celegans_metabolic", "bio_celegans_metabolic_edges.csv","bio_network_orc.json", "celegans_metabolic","Spherical", "C. elegans metabolic"),
]

# ─── Load κ̄ for a network ────────────────────────────────────────────────────

function load_kappa(json_file::String, field::String)
    path_unified = joinpath(UNIFIED_DIR, json_file)
    path_exp     = joinpath(RESULTS_DIR, json_file)
    if json_file == "bio_network_orc.json"
        d = JSON.parsefile(path_exp)
        for r in d["results"]
            r["network_id"] == field && return r["kappa_mean"]
        end
        return NaN
    elseif isfile(path_unified)
        d = JSON.parsefile(path_unified)
        return get(d, field, NaN)
    else
        return NaN
    end
end

# ─── Load edge list → SimpleGraph ─────────────────────────────────────────────

function load_graph(csv_path::String)
    node_idx = Dict{String, Int}()
    edges_raw = Tuple{Int,Int}[]
    open(csv_path) do f
        header = readline(f)
        for line in eachline(f)
            parts = split(strip(line), ',')
            length(parts) < 2 && continue
            s, t = String(parts[1]), String(parts[2])
            u = get!(node_idx, s, length(node_idx) + 1)
            v = get!(node_idx, t, length(node_idx) + 1)
            u != v && push!(edges_raw, (u, v))
        end
    end
    N = length(node_idx)
    N == 0 && return SimpleGraph(0)
    g = SimpleGraph(N)
    for (u, v) in edges_raw
        add_edge!(g, u, v)
    end
    return g
end

# ─── BFS all-pairs distances ──────────────────────────────────────────────────

function bfs_distances(g::SimpleGraph, source::Int)::Vector{Int}
    n = nv(g)
    dist = fill(-1, n)
    dist[source] = 0
    queue = [source]
    head = 1
    while head <= length(queue)
        u = queue[head]; head += 1
        for v in neighbors(g, u)
            if dist[v] == -1
                dist[v] = dist[u] + 1
                push!(queue, v)
            end
        end
    end
    return dist
end

function all_pairs_distances(g::SimpleGraph)::Matrix{Int}
    n = nv(g)
    D = Matrix{Int}(undef, n, n)
    for i in 1:n
        D[i, :] = bfs_distances(g, i)
    end
    return D
end

# ─── Gromov δ computation ─────────────────────────────────────────────────────

function gromov_delta(D::Matrix{Int}; n_samples::Int=50_000, rng::AbstractRNG=MersenneTwister(42))
    n = size(D, 1)
    n < 4 && return 0.0

    delta_max = 0.0
    for _ in 1:n_samples
        x, y, u, v = rand(rng, 1:n, 4)
        (x==y || x==u || x==v || y==u || y==v || u==v) && continue
        # BFS returns -1 for disconnected; skip if any pair is disconnected
        (D[x,y] < 0 || D[u,v] < 0 || D[x,u] < 0 || D[y,v] < 0 || D[x,v] < 0 || D[y,u] < 0) && continue
        s1 = D[x,y] + D[u,v]
        s2 = D[x,u] + D[y,v]
        s3 = D[x,v] + D[y,u]
        # Sort descending
        if s2 > s1; s1, s2 = s2, s1; end
        if s3 > s2; s2, s3 = s3, s2; end
        if s2 > s1; s1, s2 = s2, s1; end
        δ = (s1 - s2) / 2.0
        δ > delta_max && (delta_max = δ)
    end
    return delta_max
end

# ─── Main loop ────────────────────────────────────────────────────────────────

println("=== Gromov δ-Hyperbolicity Cross-Validation ===\n")

all_results = []
rng = MersenneTwister(42)

for (nid, csv_file, kappa_json, kappa_field, expected_geom, label) in NETWORKS
    csv_path = joinpath(DATA_DIR, csv_file)
    isfile(csv_path) || (println("  SKIP $label (edge file not found)"); continue)

    g = load_graph(csv_path)
    N = nv(g); E = ne(g)
    N < 4 && (println("  SKIP $label (N<4)"); continue)
    N > MAX_N && (println("  SKIP $label (N=$N > $MAX_N)"); continue)

    κ̄ = load_kappa(kappa_json, kappa_field)
    actual_geom = if !isnan(κ̄)
        κ̄ > 0.03 ? "Spherical" : (κ̄ < -0.03 ? "Hyperbolic" : "Euclidean")
    else expected_geom end

    n_samples = N ≤ 300 ? N_SAMPLES_SMALL : N_SAMPLES_LARGE

    t_bfs = @elapsed D = all_pairs_distances(g)
    # Count connected pairs
    n_connected = count(D[i,j] > 0 for i in 1:N, j in i+1:N)
    t_delta = @elapsed δ = gromov_delta(D; n_samples=n_samples, rng=rng)

    @printf("%-25s N=%4d E=%5d  δ=%5.2f  κ̄=%+.4f  [%s]  BFS=%.1fs\n",
        label, N, E, δ, isnan(κ̄) ? 0.0 : κ̄, actual_geom, t_bfs)

    push!(all_results, Dict(
        "network_id"       => nid,
        "label"            => label,
        "N"                => N,
        "E"                => E,
        "geometry"         => actual_geom,
        "kappa_mean"       => isnan(κ̄) ? nothing : κ̄,
        "gromov_delta_max" => δ,
        "n_samples"        => n_samples,
        "n_connected_pairs"=> n_connected,
        "bfs_time_s"       => t_bfs,
        "delta_time_s"     => t_delta,
    ))
end

# ─── Cross-validation statistics ──────────────────────────────────────────────

println("\n=== δ by geometry class ===")
geom_delta = Dict("Hyperbolic"=>Float64[], "Euclidean"=>Float64[], "Spherical"=>Float64[])
valid = filter(r -> r["kappa_mean"] !== nothing, all_results)
for r in valid
    push!(geom_delta[r["geometry"]], r["gromov_delta_max"])
end
for (g, vals) in sort(collect(geom_delta))
    isempty(vals) && continue
    @printf("  %-10s: mean δ = %.3f ± %.3f  (n=%d)\n", g, mean(vals), std(vals), length(vals))
end

# Pearson correlation: δ vs κ̄
δ_all = [r["gromov_delta_max"] for r in valid]
κ_all = [r["kappa_mean"] for r in valid]
n  = length(δ_all)
if n > 2
    δ_bar, κ_bar = mean(δ_all), mean(κ_all)
    r_pearson = sum((δ_all .- δ_bar) .* (κ_all .- κ_bar)) /
                sqrt(sum((δ_all .- δ_bar).^2) * sum((κ_all .- κ_bar).^2))
    @printf("\nPearson r(δ, κ̄) = %.4f  (n=%d)\n", r_pearson, n)
    # Sign agreement
    sign_agree = mean((δ_all .> median(δ_all)) .!= (κ_all .> 0))
    println("Sign disagreement rate: $(round(100*sign_agree, digits=1))%")
else
    r_pearson = NaN
end

# ─── Save JSON ────────────────────────────────────────────────────────────────

output = Dict(
    "experiment"        => "gromov_hyperbolicity",
    "description"       => "Gromov δ-hyperbolicity vs ORC cross-validation on 20 networks",
    "n_samples_small"   => N_SAMPLES_SMALL,
    "n_samples_large"   => N_SAMPLES_LARGE,
    "max_N"             => MAX_N,
    "pearson_r_delta_kappa" => isnan(r_pearson) ? nothing : r_pearson,
    "class_means"       => Dict(
        g => Dict("mean_delta"=>mean(v), "std_delta"=>(length(v)>1 ? std(v) : 0.0), "n"=>length(v))
        for (g, v) in geom_delta if !isempty(v)
    ),
    "results"           => all_results
)

open(joinpath(RESULTS_DIR, "gromov_hyperbolicity.json"), "w") do f
    JSON.print(f, output, 2)
end
println("\nSaved gromov_hyperbolicity.json")

# ─── Figure: δ vs κ̄ scatter ──────────────────────────────────────────────────

geom_colors = Dict("Hyperbolic"=>:royalblue, "Euclidean"=>:gray50, "Spherical"=>:firebrick)
geom_shapes = Dict("Hyperbolic"=>:circle,    "Euclidean"=>:square, "Spherical"=>:diamond)

p = plot(
    xlabel    = L"\delta_{\max} \; \textrm{(Gromov hyperbolicity)}",
    ylabel    = L"\bar{\kappa} \; \textrm{(mean ORC)}",
    title     = "Gromov δ vs.\ ORC: cross-validation of geometry measures",
    legend    = :bottomright,
    size      = (720, 520),
    dpi       = 150,
    grid      = true,
    gridalpha = 0.3,
    framestyle = :box,
    margin    = 5Plots.mm
)
hline!(p, [0.0], color=:black, lw=1, linestyle=:dot, label="")

for geom in ["Hyperbolic", "Euclidean", "Spherical"]
    pts = filter(r -> r["geometry"] == geom && r["kappa_mean"] !== nothing, all_results)
    isempty(pts) && continue
    xs = [r["gromov_delta_max"] for r in pts]
    ys = [r["kappa_mean"] for r in pts]
    scatter!(p, xs, ys,
        markersize=7, markercolor=geom_colors[geom],
        markershape=geom_shapes[geom], markerstrokewidth=0.5,
        markerstrokecolor=:gray30, label=geom)
end

# Annotation
if !isnan(r_pearson)
    annotate!(p, maximum(δ_all)*0.6, minimum(κ_all)*0.8,
        text(@sprintf("Pearson r = %.3f", r_pearson), 9, :left, :black))
end

savefig(p, joinpath(FIGURES_DIR, "figure14_gromov_vs_orc.pdf"))
savefig(p, joinpath(FIGURES_DIR, "figure14_gromov_vs_orc.png"))
println("Saved figure14_gromov_vs_orc.{pdf,png}")
