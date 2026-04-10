#!/usr/bin/env julia
# Biased random walks on depression speech networks.
# Each severity level is its own semantic manifold.
# 4 severities × 4 regimes = 16 conditions.

using JSON, Statistics, Printf, Random, CSV, DataFrames, Graphs

const SEVERITIES = ["minimum", "mild", "moderate", "severe"]
const REGIMES = [
    (name="normative",  temperature=0.5, valence_bias=0.0),
    (name="anxious",    temperature=2.0, valence_bias=-1.0),
    (name="ruminative", temperature=0.3, valence_bias=-0.5),
    (name="psychotic",  temperature=5.0, valence_bias=0.0),
]
const N_TRAJECTORIES = 1000
const TRAJECTORY_LENGTH = 200
const RNG = MersenneTwister(20260409)

const RESULTS_DIR = joinpath(@__DIR__, "..", "..", "results")
const UNIFIED_DIR = joinpath(RESULTS_DIR, "unified")
const CPC_DIR = joinpath(RESULTS_DIR, "cpc2026")
const DATA_DIR = joinpath(@__DIR__, "..", "..", "data", "processed", "depression_networks_optimal")

function load_graph(severity::String)
    path = joinpath(DATA_DIR, "depression_$(severity)_edges.csv")
    df = CSV.read(path, DataFrame; stringtype=String)
    all_nodes = sort(unique(vcat(df.source, df.target)))
    node_map = Dict(n => i for (i, n) in enumerate(all_nodes))
    N = length(all_nodes)

    g = SimpleGraph(N)
    weights = Dict{Tuple{Int,Int}, Float64}()
    for row in eachrow(df)
        u, v = node_map[row.source], node_map[row.target]
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
        lcc_weights[minmax(u_new, v_new)] = get(weights, minmax(u_old, v_old), 1.0)
    end

    return g_lcc, lcc_nodes, lcc_weights
end

function compute_node_metrics(g, edge_weights, artifact)
    N = nv(g)
    kappas_edge = Float64.(artifact["per_edge_curvatures"])
    edge_list = sort([(min(src(e), dst(e)), max(src(e), dst(e))) for e in edges(g)])

    # Per-node kappa
    node_kappa = zeros(N)
    node_count = zeros(Int, N)
    for (i, (u, v)) in enumerate(edge_list)
        if i <= length(kappas_edge)
            node_kappa[u] += kappas_edge[i]; node_count[u] += 1
            node_kappa[v] += kappas_edge[i]; node_count[v] += 1
        end
    end
    node_kappa ./= max.(node_count, 1)

    # Local entropy
    entropy_norm = zeros(N)
    for v in 1:N
        nbrs = neighbors(g, v)
        deg = length(nbrs)
        deg <= 1 && continue
        ws = Float64[get(edge_weights, minmax(v, n), 1.0) for n in nbrs]
        total = sum(ws); total <= 0.0 && continue
        ps = ws ./ total
        H = -sum(p * log(p) for p in ps if p > 0)
        entropy_norm[v] = H / log(deg)
    end

    c_ent = node_kappa .* (1.0 .- entropy_norm)
    return node_kappa, entropy_norm, c_ent
end

function biased_walk(g, edge_weights, c_ent, temperature, valence_bias, length_steps)
    N = nv(g)
    trajectory = Vector{Int}(undef, length_steps)
    trajectory[1] = rand(RNG, 1:N)

    for t in 2:length_steps
        v = trajectory[t-1]
        nbrs = neighbors(g, v)
        if isempty(nbrs)
            trajectory[t] = v
            continue
        end

        # Scores: edge weight + valence bias on C_ent
        scores = Float64[]
        for n in nbrs
            w = get(edge_weights, minmax(v, n), 1.0)
            score = w + valence_bias * c_ent[n]
            push!(scores, score)
        end

        # Temperature-scaled softmax
        scores ./= temperature
        max_s = maximum(scores)
        scores .-= max_s
        probs = exp.(scores)
        total = sum(probs)
        total <= 0.0 && (trajectory[t] = nbrs[rand(RNG, 1:length(nbrs))]; continue)
        probs ./= total

        # Sample
        r = rand(RNG)
        cumsum_p = 0.0
        chosen = nbrs[end]
        for (i, p) in enumerate(probs)
            cumsum_p += p
            if r <= cumsum_p
                chosen = nbrs[i]
                break
            end
        end
        trajectory[t] = chosen
    end
    return trajectory
end

function dfa_hurst(series::Vector{Float64})
    x = series .- mean(series)
    profile = cumsum(x)
    n = length(profile)
    scales = unique(Int.(floor.(10 .^ range(log10(4), log10(n ÷ 4), length=8))))
    filter!(s -> s >= 4, scales)
    length(scales) < 2 && return 0.5

    log_scales = Float64[]
    log_fluct = Float64[]
    for s in scales
        n_segments = n ÷ s
        n_segments < 1 && continue
        rms_vals = Float64[]
        for seg in 1:n_segments
            start = (seg - 1) * s + 1
            segment = profile[start:start+s-1]
            t = collect(1.0:s)
            # Linear detrend
            x_mean = mean(t); y_mean = mean(segment)
            slope = sum((t .- x_mean) .* (segment .- y_mean)) / sum((t .- x_mean) .^ 2)
            trend = y_mean .+ slope .* (t .- x_mean)
            residual = segment .- trend
            push!(rms_vals, sqrt(mean(residual .^ 2)))
        end
        isempty(rms_vals) && continue
        push!(log_scales, log(s))
        push!(log_fluct, log(mean(rms_vals)))
    end
    length(log_scales) < 2 && return 0.5

    # Linear fit
    x_mean = mean(log_scales); y_mean = mean(log_fluct)
    slope = sum((log_scales .- x_mean) .* (log_fluct .- y_mean)) / sum((log_scales .- x_mean) .^ 2)
    return clamp(slope, 0.0, 2.0)
end

function cohens_d(x::Vector{Float64}, y::Vector{Float64})
    nx, ny = length(x), length(y)
    pooled = sqrt(((nx-1)*var(x) + (ny-1)*var(y)) / (nx+ny-2))
    pooled == 0.0 ? 0.0 : (mean(y) - mean(x)) / pooled
end

function main()
    mkpath(CPC_DIR)

    println("=" ^ 70)
    println("Depression Trajectory Analysis — 4 severities × 4 regimes")
    println("=" ^ 70)

    all_results = Dict{String, Any}()

    for sev in SEVERITIES
        println("\n▸ Loading depression_$(sev)...")
        g, node_names, edge_weights = load_graph(sev)
        artifact = JSON.parsefile(joinpath(UNIFIED_DIR, "depression_$(sev)_exact_lp.json"))
        node_kappa, entropy_norm, c_ent = compute_node_metrics(g, edge_weights, artifact)

        # High-entropy threshold (90th percentile)
        threshold = quantile(entropy_norm[entropy_norm .> 0], 0.90)

        sev_results = Dict{String, Any}()

        for regime in REGIMES
            c_ent_vars = Float64[]
            residence_fracs = Float64[]
            hurst_exps = Float64[]

            for traj_id in 1:N_TRAJECTORIES
                traj = biased_walk(g, edge_weights, c_ent, regime.temperature, regime.valence_bias, TRAJECTORY_LENGTH)

                # C_ent variance along trajectory
                c_ent_series = c_ent[traj]
                push!(c_ent_vars, var(c_ent_series))

                # Residence in high-entropy nodes
                high_ent_steps = count(t -> entropy_norm[t] > threshold, traj)
                push!(residence_fracs, high_ent_steps / TRAJECTORY_LENGTH)

                # Hurst exponent
                push!(hurst_exps, dfa_hurst(c_ent_series))
            end

            sev_results[regime.name] = Dict(
                "c_ent_var_mean" => mean(c_ent_vars),
                "c_ent_var_std" => std(c_ent_vars),
                "residence_mean" => mean(residence_fracs),
                "residence_std" => std(residence_fracs),
                "hurst_mean" => mean(hurst_exps),
                "hurst_std" => std(hurst_exps),
                "n_trajectories" => N_TRAJECTORIES,
            )

            @printf("  %s × %s: C_ent_var=%.4f  residence=%.3f  Hurst=%.3f\n",
                    sev, regime.name, mean(c_ent_vars), mean(residence_fracs), mean(hurst_exps))
        end

        # Cross-regime effect sizes within this severity
        norm_data = sev_results["normative"]
        for regime in REGIMES[2:end]
            # We need the raw data for effect sizes — recompute quickly
        end

        all_results[sev] = Dict(
            "N" => nv(g), "E" => ne(g),
            "eta" => (2.0 * ne(g) / nv(g))^2 / nv(g),
            "kappa_mean" => artifact["kappa_mean"],
            "regimes" => sev_results,
        )
    end

    # Cross-severity comparison: does ruminative Hurst differ by severity?
    println("\n" * "=" ^ 70)
    println("Cross-Severity Ruminative Hurst:")
    for sev in SEVERITIES
        h = all_results[sev]["regimes"]["ruminative"]["hurst_mean"]
        @printf("  %s: %.3f\n", sev, h)
    end

    # Save
    output = Dict(
        "experiment" => "depression_trajectories",
        "n_trajectories" => N_TRAJECTORIES,
        "trajectory_length" => TRAJECTORY_LENGTH,
        "seed" => 20260409,
        "per_severity" => all_results,
    )

    outpath = joinpath(CPC_DIR, "depression_trajectories.json")
    open(outpath, "w") do f
        JSON.print(f, output, 2)
    end
    println("\nSaved: $outpath")
end

main()
