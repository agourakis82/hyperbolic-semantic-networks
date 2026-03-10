"""
clifford_orc.jl — Clifford Algebra Signature Sweep for ORC

Sweeps Clifford signatures Cl(p,q) and computes κ̄ for:
  1. k-regular random graphs N=100, k ∈ {4, 14, 16} (representative points)
  2. All 11 semantic networks (from unified results)

Scientific question:
  Does a timelike dimension in the Clifford embedding (q > 0) restore κ < 0
  for graphs that show κ > 0 under sphere (Cl(n,0)) embedding?

Expected:
  - Cl(n,0): same as sphere embedding → all positive for high-k graphs
  - Cl(n-1,1): Minkowski-like → may restore negative κ for low-k (hyperbolic) graphs
  - Cl(1,n-1): fully timelike → all distances imaginary (abs value) → behavior unclear

Usage:
    julia --project=julia -t 8 julia/scripts/clifford_orc.jl
"""

import Pkg
Pkg.instantiate()

using Graphs
using JSON
using Statistics
using Random
using LinearAlgebra
using JuMP
using HiGHS

include(joinpath(@__DIR__, "..", "src", "Curvature", "CliffordORC.jl"))
using .CliffordORC

# ─────────────────────────────────────────────────────────────────
# Signatures to sweep
# ─────────────────────────────────────────────────────────────────

SIGNATURES_TO_TEST = [
    CliffordSignature(4, 0),    # Euclidean 4D — baseline (= S³)
    CliffordSignature(3, 1),    # Minkowski 4D — 1 timelike
    CliffordSignature(2, 2),    # Split 4D — balanced
    CliffordSignature(1, 3),    # Anti-Minkowski 4D — mostly timelike
    CliffordSignature(8, 0),    # Euclidean 8D — baseline (= S⁷)
    CliffordSignature(7, 1),    # Minkowski 8D
    CliffordSignature(4, 4),    # Split 8D
    CliffordSignature(16, 0),   # Euclidean 16D — baseline (= S¹⁵)
    CliffordSignature(15, 1),   # Minkowski 16D
    CliffordSignature(8, 8),    # Split 16D
]

# ─────────────────────────────────────────────────────────────────
# Graph generators
# ─────────────────────────────────────────────────────────────────

function random_regular_or_er(N::Int, k::Int; seed::Int=42)::SimpleGraph
    # Use Erdos-Renyi with p=k/N as proxy (random regular needs special algorithm)
    rng = MersenneTwister(seed)
    p = k / N
    return erdos_renyi(N, p; rng=rng)
end

# ─────────────────────────────────────────────────────────────────
# Main sweep
# ─────────────────────────────────────────────────────────────────

function run_kregular_sweep(; N::Int=100, k_values::Vector{Int}=[4, 10, 14, 16, 20])
    println("\n" * "="^60)
    println("Clifford Signature Sweep — k-regular N=$N")
    println("="^60)

    results = Dict[]

    for k in k_values
        println("\n  k=$k (η=$(round(k^2/N, digits=3)))")
        g = random_regular_or_er(N, k)
        ne_actual = ne(g)
        println("    Edges: $ne_actual")

        row = Dict("N" => N, "k" => k, "eta" => k^2/N, "n_edges" => ne_actual,
                   "signatures" => Dict())

        for sig in SIGNATURES_TO_TEST
            kappas = clifford_all_curvatures(g, sig; alpha=0.5)
            valid = filter(!isnan, kappas)
            if isempty(valid)
                println("    $(sig): no valid edges")
                continue
            end
            km = mean(valid)
            ks = std(valid)
            row["signatures"]["$(sig.p)_$(sig.q)"] = Dict(
                "p" => sig.p, "q" => sig.q,
                "kappa_mean" => km,
                "kappa_std" => ks,
                "n_valid" => length(valid),
            )
            sign_str = km < 0 ? "HYPERBOLIC" : (km > 0 ? "SPHERICAL" : "EUCLIDEAN")
            println("    $(sig): κ̄=$(round(km, digits=4)) ± $(round(ks, digits=4))  [$sign_str]")
        end
        push!(results, row)
    end

    return results
end

function run_semantic_sweep(; alpha::Float64=0.5)
    println("\n" * "="^60)
    println("Clifford Signature Sweep — Semantic Networks")
    println("="^60)

    results_dir = joinpath(@__DIR__, "..", "..", "results", "unified")
    # Skip depression variants and 2k wordnet (too large for signature sweep)
    skip_ids = Set(["depression_mild", "depression_moderate", "depression_severe",
                    "depression_minimum", "wordnet_en_2k", "framenet_en"])
    network_files = filter(f -> endswith(f, "_exact_lp.json") &&
                           !(replace(f, "_exact_lp.json" => "") in skip_ids),
                          readdir(results_dir))

    all_results = Dict[]

    for fname in network_files
        net_id = replace(fname, "_exact_lp.json" => "")
        path = joinpath(results_dir, fname)
        data = JSON.parsefile(path)

        # Map network id → edge file name
        edge_name_map = Dict(
            "swow_es" => "spanish_edges_FINAL.csv",
            "swow_en" => "english_edges_FINAL.csv",
            "swow_zh" => "chinese_edges_FINAL.csv",
            "swow_nl" => "dutch_edges.csv",
            "conceptnet_en" => "conceptnet_en_edges.csv",
            "conceptnet_pt" => "conceptnet_pt_edges.csv",
            "wordnet_en" => "wordnet_edges.csv",
            "wordnet_en_2k" => "wordnet_N2000_edges.csv",
            "babelnet_ru" => "babelnet_ru_edges.csv",
            "babelnet_ar" => "babelnet_ar_edges.csv",
            "eat_en" => "eat_en_edges.csv",
            "framenet_en" => "framenet_en_edges.csv",
            "swow_rp" => "swow_rp_edges.csv",
            "wordnet_de" => "wordnet_de_edges.csv",
            "usf_en" => "usf_en_edges.csv",
            "depression_minimum" => "depression_networks_optimal/depression_minimum_edges.csv",
            "depression_mild" => "depression_networks_optimal/depression_mild_edges.csv",
            "depression_moderate" => "depression_networks_optimal/depression_moderate_edges.csv",
            "depression_severe" => "depression_networks_optimal/depression_severe_edges.csv",
        )
        edge_fname = get(edge_name_map, net_id, net_id * "_edges.csv")
        edge_file = joinpath(@__DIR__, "..", "..", "data", "processed", edge_fname)

        if !isfile(edge_file)
            println("  Skipping $net_id — edge file not found: $edge_file")
            continue
        end

        # Load graph — handle both integer and string node names
        node_map = Dict{String,Int}()
        edge_pairs = Tuple{Int,Int}[]
        try
            open(edge_file) do f
                for line in eachline(f)
                    startswith(line, "#") && continue
                    startswith(line, "source") && continue
                    parts = split(strip(line), ",")
                    length(parts) < 2 && continue
                    u_str, v_str = parts[1], parts[2]
                    u_str == v_str && continue
                    if !haskey(node_map, u_str)
                        node_map[u_str] = length(node_map) + 1
                    end
                    if !haskey(node_map, v_str)
                        node_map[v_str] = length(node_map) + 1
                    end
                    push!(edge_pairs, (node_map[u_str], node_map[v_str]))
                end
            end
        catch e
            println("  Skipping $net_id — error loading graph: $e")
            continue
        end

        if isempty(edge_pairs)
            println("  Skipping $net_id — 0 edges loaded")
            continue
        end

        N_actual = length(node_map)
        g = SimpleGraph(N_actual)
        for (u, v) in edge_pairs
            add_edge!(g, u, v)
        end

        eta = get(data, "eta", 0.0)
        kappa_pairwise = get(data, "kappa_mean", NaN)
        geometry = get(data, "geometry", "unknown")

        println("\n  Network: $net_id (N=$(nv(g)), E=$(ne(g)), η=$(round(eta, digits=3)), κ̄_pw=$(round(kappa_pairwise, digits=4)))")

        row = Dict(
            "network" => net_id, "N" => nv(g), "E" => ne(g),
            "eta" => eta, "kappa_pairwise" => kappa_pairwise,
            "geometry_pairwise" => geometry,
            "signatures" => Dict()
        )

        # Only test 4D and 8D signatures to keep runtime manageable
        sigs_to_run = [
            CliffordSignature(4, 0),
            CliffordSignature(3, 1),
            CliffordSignature(2, 2),
            CliffordSignature(8, 0),
            CliffordSignature(7, 1),
        ]

        for sig in sigs_to_run
            kappas = clifford_all_curvatures(g, sig; alpha=alpha)
            valid = filter(!isnan, kappas)
            isempty(valid) && continue
            km = mean(valid)
            ks = std(valid)
            row["signatures"]["$(sig.p)_$(sig.q)"] = Dict(
                "p" => sig.p, "q" => sig.q,
                "kappa_mean" => km, "kappa_std" => ks,
                "n_valid" => length(valid),
            )
            sign_str = km < 0 ? "HYPERBOLIC" : (km > 0 ? "SPHERICAL" : "EUCLIDEAN")
            println("    $(sig): κ̄=$(round(km, digits=4))  [$sign_str]")
        end
        push!(all_results, row)
    end

    return all_results
end

# ─────────────────────────────────────────────────────────────────
# Run and save
# ─────────────────────────────────────────────────────────────────

println("Clifford Algebra ORC Sweep")
println("Testing $(length(SIGNATURES_TO_TEST)) signatures")
println("Threads: $(Threads.nthreads())")

k_results = run_kregular_sweep(N=100, k_values=[4, 10, 14, 16, 20])

out_k = joinpath(@__DIR__, "..", "..", "results", "experiments", "clifford_kregular_n100.json")
open(out_k, "w") do f
    JSON.print(f, k_results, 2)
end
println("\nSaved k-regular results to $out_k")

sem_results = run_semantic_sweep()
out_sem = joinpath(@__DIR__, "..", "..", "results", "experiments", "clifford_semantic.json")
open(out_sem, "w") do f
    JSON.print(f, sem_results, 2)
end
println("Saved semantic results to $out_sem")

# Summary table
println("\n" * "="^60)
println("SUMMARY: Cl(p,q) vs Sphere — k-regular N=100")
println("="^60)
println("  sig      |  k=4   |  k=14  |  k=16  |  k=20  ")
println("  ---------|--------|--------|--------|--------")
for sig in [CliffordSignature(4,0), CliffordSignature(3,1), CliffordSignature(2,2),
            CliffordSignature(1,3), CliffordSignature(8,0), CliffordSignature(7,1)]
    sig_key = "$(sig.p)_$(sig.q)"
    vals = []
    for row in k_results
        sigs = get(row, "signatures", Dict())
        if haskey(sigs, sig_key)
            km = sigs[sig_key]["kappa_mean"]
            push!(vals, lpad(round(km, digits=3), 7))
        else
            push!(vals, "    N/A")
        end
    end
    println("  $(lpad(string(sig), 9)) | $(join(vals, " | "))")
end

println("\nDone.")
