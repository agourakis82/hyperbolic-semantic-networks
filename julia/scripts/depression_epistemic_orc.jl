#!/usr/bin/env julia
# Epistemic bootstrap CIs for κ̄ on 4 depression speech networks.
# Uses precomputed per-edge curvatures from exact LP artifacts.
# Also computes per-node entropic curvature C_ent = κ × (1 - H_norm).

using JSON, Statistics, Printf, Random, CSV, DataFrames, Graphs

const SEVERITIES = ["minimum", "mild", "moderate", "severe"]
const N_BOOTSTRAP = 10_000
const RNG = MersenneTwister(20260409)

const RESULTS_DIR = joinpath(@__DIR__, "..", "..", "results")
const UNIFIED_DIR = joinpath(RESULTS_DIR, "unified")
const CPC_DIR = joinpath(RESULTS_DIR, "cpc2026")
const DATA_DIR = joinpath(@__DIR__, "..", "..", "data", "processed", "depression_networks_optimal")

function bootstrap_ci(kappas::Vector{Float64}; n_boot=N_BOOTSTRAP, alpha=0.05)
    E = length(kappas)
    means = Vector{Float64}(undef, n_boot)
    for b in 1:n_boot
        s = 0.0
        for _ in 1:E
            s += kappas[rand(RNG, 1:E)]
        end
        means[b] = s / E
    end
    sort!(means)
    lo_idx = max(1, Int(floor(alpha / 2 * n_boot)))
    hi_idx = min(n_boot, Int(ceil((1 - alpha / 2) * n_boot)))
    return (
        mean = mean(kappas),
        se = std(means),
        ci_lo = means[lo_idx],
        ci_hi = means[hi_idx],
        boot_std = std(means),
        n_boot = n_boot,
    )
end

function jackknife_influence(kappas::Vector{Float64})
    E = length(kappas)
    full_mean = mean(kappas)
    total = sum(kappas)
    influences = [(total - kappas[i]) / (E - 1) - full_mean for i in 1:E]
    return (max_influence=maximum(abs.(influences)), influence_std=std(influences))
end

function load_depression_graph(severity::String)
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

    # Largest connected component
    ccs = connected_components(g)
    lcc = ccs[argmax(length.(ccs))]
    sort!(lcc)
    g_lcc, vmap = induced_subgraph(g, lcc)

    lcc_nodes = all_nodes[lcc]
    lcc_weights = Dict{Tuple{Int,Int}, Float64}()
    for (e_new, v_old) in enumerate(lcc)
        for n_new in neighbors(g_lcc, e_new)
            old_u, old_v = lcc[e_new], lcc[n_new]
            key_old = minmax(old_u, old_v)
            key_new = minmax(e_new, n_new)
            if haskey(weights, key_old)
                lcc_weights[key_new] = weights[key_old]
            end
        end
    end

    return g_lcc, lcc_nodes, lcc_weights
end

function compute_local_entropy(g, node_weights)
    N = nv(g)
    entropy_vals = zeros(N)
    entropy_norm_vals = zeros(N)

    for v in 1:N
        nbrs = neighbors(g, v)
        deg = length(nbrs)
        if deg <= 1
            continue
        end
        ws = Float64[get(node_weights, minmax(v, n), 1.0) for n in nbrs]
        total = sum(ws)
        if total <= 0.0
            continue
        end
        ps = ws ./ total
        H = -sum(p * log(p) for p in ps if p > 0)
        entropy_vals[v] = H
        entropy_norm_vals[v] = H / log(deg)
    end

    return entropy_vals, entropy_norm_vals
end

function derive_node_kappa(g, per_edge_curvatures::Vector{Float64})
    N = nv(g)
    edge_list = sort([(min(src(e), dst(e)), max(src(e), dst(e))) for e in edges(g)])

    if length(edge_list) != length(per_edge_curvatures)
        error("Edge count mismatch: $(length(edge_list)) vs $(length(per_edge_curvatures))")
    end

    node_kappas = [Float64[] for _ in 1:N]
    for (i, (u, v)) in enumerate(edge_list)
        push!(node_kappas[u], per_edge_curvatures[i])
        push!(node_kappas[v], per_edge_curvatures[i])
    end

    return [isempty(ks) ? 0.0 : mean(ks) for ks in node_kappas]
end

function cohens_d(x::Vector{Float64}, y::Vector{Float64})
    nx, ny = length(x), length(y)
    pooled = sqrt(((nx - 1) * var(x) + (ny - 1) * var(y)) / (nx + ny - 2))
    pooled == 0.0 ? 0.0 : (mean(y) - mean(x)) / pooled
end

function main()
    mkpath(CPC_DIR)

    println("=" ^ 70)
    println("Depression Epistemic ORC — Bootstrap 95% CIs")
    println("=" ^ 70)
    @printf("  %-12s  %5s  %5s  %+8s  %6s  %s\n",
            "Severity", "N", "E", "κ̄", "SE", "95% CI")
    println("-" ^ 70)

    per_severity = Dict{String, Any}()
    all_node_metrics = DataFrame()

    for sev in SEVERITIES
        # Load artifact
        artifact_path = joinpath(UNIFIED_DIR, "depression_$(sev)_exact_lp.json")
        artifact = JSON.parsefile(artifact_path)
        kappas = Float64.(artifact["per_edge_curvatures"])

        # Bootstrap CI on edge curvatures
        b = bootstrap_ci(kappas)
        j = jackknife_influence(kappas)

        ci_regime = b.ci_lo > 0.0 ? "SPHERICAL" : (b.ci_hi < 0.0 ? "HYPERBOLIC" : "UNCERTAIN")

        # Load graph for node-level metrics
        g, node_names, edge_weights = load_depression_graph(sev)
        N_graph = nv(g)
        E_graph = ne(g)
        mean_deg = 2.0 * E_graph / N_graph
        eta = mean_deg^2 / N_graph

        # Node-level kappa and C_ent
        node_kappa = derive_node_kappa(g, kappas)
        _, entropy_norm = compute_local_entropy(g, edge_weights)
        c_ent = node_kappa .* (1.0 .- entropy_norm)

        # Append to node metrics
        sev_df = DataFrame(
            node = node_names,
            severity = fill(sev, N_graph),
            kappa = node_kappa,
            entropy_norm = entropy_norm,
            C_ent = c_ent,
            degree = [degree(g, v) for v in 1:N_graph],
        )
        all_node_metrics = vcat(all_node_metrics, sev_df)

        per_severity[sev] = Dict(
            "N" => N_graph, "E" => E_graph,
            "eta" => eta,
            "kappa_mean" => b.mean,
            "kappa_std" => artifact["kappa_std"],
            "se" => b.se,
            "ci_lo" => b.ci_lo, "ci_hi" => b.ci_hi,
            "boot_std" => b.boot_std,
            "n_boot" => b.n_boot,
            "ci_regime" => ci_regime,
            "jackknife_max_influence" => j.max_influence,
            "jackknife_influence_std" => j.influence_std,
            "C_ent_mean" => mean(c_ent),
            "C_ent_std" => std(c_ent),
            "frac_spherical" => artifact["frac_spherical"],
        )

        @printf("  %-12s  %5d  %5d  %+.4f  %.4f  [%+.4f, %+.4f]  %s\n",
                sev, N_graph, E_graph, b.mean, b.se, b.ci_lo, b.ci_hi, ci_regime)
    end

    # Pairwise Cohen's d on C_ent
    println("\nPairwise Cohen's d (C_ent):")
    pairwise = Dict{String, Any}()
    for i in 1:length(SEVERITIES)
        for j in (i+1):length(SEVERITIES)
            s1, s2 = SEVERITIES[i], SEVERITIES[j]
            x = all_node_metrics[all_node_metrics.severity .== s1, :C_ent]
            y = all_node_metrics[all_node_metrics.severity .== s2, :C_ent]
            d = cohens_d(x, y)
            pairwise["$(s1)_vs_$(s2)"] = Dict("cohens_d" => d, "n1" => length(x), "n2" => length(y))
            @printf("  %s vs %s: d = %.3f\n", s1, s2, d)
        end
    end

    # Key tests
    println("\nKey Tests:")
    all_hyp = all(per_severity[s]["ci_hi"] < 0.0 for s in SEVERITIES)
    println("  All CIs entirely < 0 (HYPERBOLIC): $(all_hyp ? "PASS" : "FAIL")")

    min_most = per_severity["minimum"]["kappa_mean"] < per_severity["mild"]["kappa_mean"]
    println("  Minimum most negative: $(min_most ? "PASS" : "FAIL")")

    # Save
    output = Dict(
        "experiment" => "depression_epistemic_orc",
        "n_bootstrap" => N_BOOTSTRAP,
        "seed" => 20260409,
        "per_severity" => per_severity,
        "pairwise_cohens_d" => pairwise,
    )

    outpath = joinpath(CPC_DIR, "depression_epistemic_orc.json")
    open(outpath, "w") do f
        JSON.print(f, output, 2)
    end
    println("\nSaved: $outpath")

    # Save node metrics as CSV (Julia-native, no Parquet dependency needed)
    csv_path = joinpath(CPC_DIR, "depression_node_metrics.csv")
    CSV.write(csv_path, all_node_metrics)
    println("Saved: $csv_path ($(nrow(all_node_metrics)) rows)")
end

main()
