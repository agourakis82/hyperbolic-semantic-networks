#!/usr/bin/env julia
# Export 8D octonionic node features for depression networks.
# Format matches SWOW-EN features used by the Sounio O-SSM.
# Output: data/cpc2026/depression_{severity}_node_features.csv

using JSON, Statistics, CSV, DataFrames, Graphs, Random

const SEVERITIES = ["minimum", "mild", "moderate", "severe"]
const RNG = MersenneTwister(20260409)

const RESULTS_DIR = joinpath(@__DIR__, "..", "..", "results")
const UNIFIED_DIR = joinpath(RESULTS_DIR, "unified")
const DATA_DIR = joinpath(@__DIR__, "..", "..", "data", "processed", "depression_networks_optimal")
const OUTPUT_DIR = joinpath(@__DIR__, "..", "..", "data", "cpc2026")

# Warriner et al. (2013) valence norms — load from the pre-merged SWOW file
const VALENCE_PATH = joinpath(@__DIR__, "..", "..", "data", "processed", "swow_en_valence.csv")

function load_graph(severity::String)
    path = joinpath(DATA_DIR, "depression_$(severity)_edges.csv")
    df = CSV.read(path, DataFrame; stringtype=String)

    all_nodes = sort(unique(vcat(df.source, df.target)))
    node_map = Dict(n => i for (i, n) in enumerate(all_nodes))
    N = length(all_nodes)

    g = SimpleGraph(N)
    weights = Dict{Tuple{Int,Int}, Float64}()
    for row in eachrow(df)
        u = node_map[row.source]
        v = node_map[row.target]
        if u != v
            add_edge!(g, u, v)
            key = minmax(u, v)
            weights[key] = get(weights, key, 0.0) + Float64(row.weight)
        end
    end

    ccs = connected_components(g)
    lcc = ccs[argmax(length.(ccs))]
    sort!(lcc)
    g_lcc, _ = induced_subgraph(g, lcc)
    lcc_nodes = all_nodes[lcc]

    lcc_weights = Dict{Tuple{Int,Int}, Float64}()
    for e in edges(g_lcc)
        u_new, v_new = src(e), dst(e)
        u_old, v_old = lcc[u_new], lcc[v_new]
        key_old = minmax(u_old, v_old)
        key_new = minmax(u_new, v_new)
        if haskey(weights, key_old)
            lcc_weights[key_new] = weights[key_old]
        end
    end

    return g_lcc, lcc_nodes, lcc_weights
end

function load_valence_map()
    if !isfile(VALENCE_PATH)
        println("  WARNING: Valence file not found at $VALENCE_PATH, using neutral=0.0")
        return Dict{String, Float64}()
    end
    df = CSV.read(VALENCE_PATH, DataFrame; stringtype=String)
    valence_map = Dict{String, Float64}()
    for row in eachrow(df)
        word = lowercase(strip(string(row.word)))
        # Warriner valence is 1-9, center to [-1,1]
        v = haskey(row, :valence) ? (Float64(row.valence) - 5.0) / 4.0 : 0.0
        valence_map[word] = v
    end
    return valence_map
end

function compute_features(g, node_names, edge_weights, artifact, valence_map)
    N = nv(g)
    kappas_edge = Float64.(artifact["per_edge_curvatures"])
    edge_list = sort([(min(src(e), dst(e)), max(src(e), dst(e))) for e in edges(g)])

    # Per-node kappa
    node_kappa_lists = [Float64[] for _ in 1:N]
    for (i, (u, v)) in enumerate(edge_list)
        if i <= length(kappas_edge)
            push!(node_kappa_lists[u], kappas_edge[i])
            push!(node_kappa_lists[v], kappas_edge[i])
        end
    end
    node_kappa = [isempty(ks) ? 0.0 : mean(ks) for ks in node_kappa_lists]

    # Local entropy
    entropy_norm = zeros(N)
    for v in 1:N
        nbrs = neighbors(g, v)
        deg = length(nbrs)
        if deg <= 1; continue; end
        ws = Float64[get(edge_weights, minmax(v, n), 1.0) for n in nbrs]
        total = sum(ws)
        if total <= 0.0; continue; end
        ps = ws ./ total
        H = -sum(p * log(p) for p in ps if p > 0)
        entropy_norm[v] = H / log(deg)
    end

    # C_ent
    c_ent = node_kappa .* (1.0 .- entropy_norm)

    # Valence
    valence = [get(valence_map, lowercase(n), 0.0) for n in node_names]

    # Spring layout as Poincare proxy (tanh rescale)
    # Simple force-directed layout
    pos = randn(RNG, N, 2) .* 0.1
    for _ in 1:50
        for i in 1:N
            fx, fy = 0.0, 0.0
            for j in neighbors(g, i)
                dx = pos[j, 1] - pos[i, 1]
                dy = pos[j, 2] - pos[i, 2]
                d = sqrt(dx^2 + dy^2) + 1e-6
                fx += dx / d * 0.1
                fy += dy / d * 0.1
            end
            pos[i, 1] += fx
            pos[i, 2] += fy
        end
    end
    # Rescale to disk via tanh
    for i in 1:N
        r = sqrt(pos[i,1]^2 + pos[i,2]^2) + 1e-6
        scale = tanh(r) / r * 0.95
        pos[i, 1] *= scale
        pos[i, 2] *= scale
    end

    # Degree features
    degs = Float64[degree(g, v) for v in 1:N]
    log_degree = log.(degs .+ 1.0)

    # Local eta
    mean_deg = 2.0 * ne(g) / N
    eta_global = mean_deg^2 / N
    eta_local = fill(eta_global, N)

    # Normalize all features to [-1, 1]
    normalize!(x) = begin
        mx = maximum(abs.(x))
        mx > 0 && (x ./= mx)
    end
    normalize!(node_kappa)
    normalize!(entropy_norm)
    normalize!(c_ent)
    normalize!(log_degree)
    normalize!(pos[:, 1])
    normalize!(pos[:, 2])
    normalize!(eta_local)

    return DataFrame(
        idx = 0:(N-1),
        node = node_names,
        kappa = node_kappa,
        entropy_norm = entropy_norm,
        c_ent = c_ent,
        valence = valence,
        poincare_x = pos[:, 1],
        poincare_y = pos[:, 2],
        log_degree = log_degree,
        eta_local = eta_local,
    )
end

function main()
    mkpath(OUTPUT_DIR)
    valence_map = load_valence_map()
    println("Valence map: $(length(valence_map)) entries")

    for sev in SEVERITIES
        println("\nExporting features for depression_$(sev)...")
        g, node_names, edge_weights = load_graph(sev)
        artifact_path = joinpath(UNIFIED_DIR, "depression_$(sev)_exact_lp.json")
        artifact = JSON.parsefile(artifact_path)

        features = compute_features(g, node_names, edge_weights, artifact, valence_map)
        outpath = joinpath(OUTPUT_DIR, "depression_$(sev)_node_features.csv")
        CSV.write(outpath, features)

        n_valence = count(abs.(features.valence) .> 0.001)
        println("  N=$(nv(g)), features=$(ncol(features)), valence_coverage=$(n_valence)/$(nv(g))")
        println("  Saved: $outpath")
    end
end

main()
