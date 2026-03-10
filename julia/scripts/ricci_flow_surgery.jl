"""
RICCI FLOW SURGERY ON SEMANTIC NETWORKS

After normalized Ricci flow amplifies bridge edges (high positive final weight),
this script removes them by a threshold and detects the resulting communities.

Algorithm:
  1. Load per-network ricci_flow_{id}.json (must contain 'final_weights' field)
  2. Compute threshold = mean(w) + 2·std(w) of final edge weights
  3. Remove edges above threshold ("surgery")
  4. Report connected components, sizes, and key betweenness nodes per component

Usage:
    julia --project=julia julia/scripts/ricci_flow_surgery.jl
    julia --project=julia julia/scripts/ricci_flow_surgery.jl --network swow_en
    julia --project=julia julia/scripts/ricci_flow_surgery.jl --sigma 1.5   # tighter threshold
"""

import Pkg
let deps = Pkg.project().dependencies
    for pkg in ["Graphs", "JSON", "Statistics"]
        if !haskey(deps, pkg)
            Pkg.add(pkg)
        end
    end
end

using Graphs
using Statistics
using JSON
using Printf

const RESULTS_DIR = joinpath(@__DIR__, "..", "..", "results", "experiments")

# ─────────────────────────────────────────────────────────────────
# Load final weights from ricci_flow_{id}.json
# ─────────────────────────────────────────────────────────────────

function load_flow_result(network_id::String)
    f = joinpath(RESULTS_DIR, "ricci_flow_$(network_id).json")
    if !isfile(f)
        @warn "File not found: $f"
        return nothing
    end
    d = JSON.parsefile(f)
    if !haskey(d, "final_weights")
        @warn "$(network_id): no 'final_weights' in JSON (re-run ricci_flow_semantic.jl to regenerate)"
        return nothing
    end
    return d
end

# ─────────────────────────────────────────────────────────────────
# Betweenness proxy: degree centrality (fast, avoids O(NE) APSP)
# ─────────────────────────────────────────────────────────────────

function top_degree_nodes(g::SimpleGraph, component::Vector{Int}; top_k=5)
    sub = induced_subgraph(g, component)[1]
    degs = degree(sub)
    idx = sortperm(degs, rev=true)[1:min(top_k, length(degs))]
    return component[idx], degs[idx]
end

# ─────────────────────────────────────────────────────────────────
# Perform surgery on a single network
# ─────────────────────────────────────────────────────────────────

function perform_surgery(network_id::String; sigma_factor::Float64=2.0)
    d = load_flow_result(network_id)
    d === nothing && return nothing

    N = d["N"]
    E = d["E"]
    kappa_initial = d["kappa_initial"]
    kappa_final   = d["kappa_final"]
    eta           = d["eta"]

    # Parse final weights: list of [u, v, w]
    fw = d["final_weights"]
    weights = Dict{Tuple{Int,Int}, Float64}()
    for uvw in fw
        u, v, w = Int(uvw[1]), Int(uvw[2]), Float64(uvw[3])
        weights[(min(u,v), max(u,v))] = w
    end

    ws = collect(values(weights))
    w_mean = mean(ws)
    w_std  = std(ws)
    threshold = w_mean + sigma_factor * w_std

    # Build pruned graph (keep edges with w <= threshold)
    g_pruned = SimpleGraph(N)
    n_kept = 0
    n_removed = 0
    for ((u, v), w) in weights
        if w <= threshold
            add_edge!(g_pruned, u, v)
            n_kept += 1
        else
            n_removed += 1
        end
    end

    # Connected components
    comps = connected_components(g_pruned)
    sort!(comps, by=length, rev=true)
    n_comps = length(comps)
    comp_sizes = [length(c) for c in comps]
    largest_frac = comp_sizes[1] / N

    # Top-degree nodes in each component (up to 5 components)
    comp_hubs = []
    for (i, comp) in enumerate(comps[1:min(5, end)])
        nodes, degs = top_degree_nodes(g_pruned, comp, top_k=5)
        push!(comp_hubs, Dict("component" => i, "size" => length(comp),
                               "top_nodes" => nodes, "top_degrees" => degs))
    end

    result = Dict(
        "network_id"          => network_id,
        "N"                   => N,
        "E_original"          => E,
        "kappa_initial"       => kappa_initial,
        "kappa_final"         => kappa_final,
        "eta"                 => eta,
        "sigma_factor"        => sigma_factor,
        "threshold"           => threshold,
        "w_mean_final"        => w_mean,
        "w_std_final"         => w_std,
        "n_edges_removed"     => n_removed,
        "n_edges_kept"        => n_kept,
        "fraction_removed"    => n_removed / E,
        "n_components"        => n_comps,
        "component_sizes"     => comp_sizes,
        "largest_component_fraction" => largest_frac,
        "component_hubs"      => comp_hubs,
    )

    return result
end

# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────

const ALL_NETWORKS = [
    "swow_es", "swow_en", "swow_zh", "swow_nl",
    "conceptnet_en", "conceptnet_pt",
    "depression_min",
    "wordnet_en", "babelnet_ru", "babelnet_ar",
]

function main()
    # Parse CLI args
    single_network = nothing
    sigma_factor = 2.0
    for (i, arg) in enumerate(ARGS)
        if arg == "--network" && i < length(ARGS)
            single_network = ARGS[i+1]
        elseif arg == "--sigma" && i < length(ARGS)
            sigma_factor = parse(Float64, ARGS[i+1])
        end
    end

    networks = single_network !== nothing ? [single_network] : ALL_NETWORKS

    all_results = Dict{String, Any}[]
    println("="^70)
    println("RICCI FLOW SURGERY (σ=$sigma_factor)")
    println("="^70)
    @printf("%-18s  %5s  %6s  %8s  %8s  %6s  %6s\n",
            "Network", "N", "E", "κ₀→κ_T", "Removed", "N_comp", "LCC%")
    println("-"^80)

    for net_id in networks
        r = perform_surgery(net_id, sigma_factor=sigma_factor)
        r === nothing && continue
        push!(all_results, r)

        @printf("%-18s  %5d  %6d  %+6.3f→%+6.3f  %5d(%4.1f%%)  %6d  %5.1f%%\n",
                r["network_id"], r["N"], r["E_original"],
                r["kappa_initial"], r["kappa_final"],
                r["n_edges_removed"], 100*r["fraction_removed"],
                r["n_components"], 100*r["largest_component_fraction"])

        # Save per-network surgery result
        out_file = joinpath(RESULTS_DIR, "ricci_flow_surgery_$(net_id).json")
        open(out_file, "w") do f
            JSON.print(f, r, 2)
        end
    end

    # Combined output
    combined_file = joinpath(RESULTS_DIR, "ricci_flow_surgery.json")
    open(combined_file, "w") do f
        JSON.print(f, Dict(
            "experiment"   => "ricci_flow_surgery",
            "sigma_factor" => sigma_factor,
            "n_networks"   => length(all_results),
            "results"      => all_results,
        ), 2)
    end
    println("\nSaved: $combined_file")

    # Interpretation summary
    println("\nKEY FINDINGS:")
    for r in all_results
        nc = r["n_components"]
        frac = r["fraction_removed"]
        kappa_final = r["kappa_final"]
        if nc > 3
            regime = "FRAGMENTED"
        elseif nc == 1
            regime = "CONNECTED"
        else
            regime = "SPLIT"
        end
        @printf("  %-18s  κ_T=%+.3f  frac_rm=%.2f  n_comp=%-3d  → %s\n",
                r["network_id"], kappa_final, frac, nc, regime)
    end
end

main()
