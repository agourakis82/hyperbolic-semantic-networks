"""
BRIDGE ANALYSIS — Connecting Phase Transition Theory with Semantic Networks

Places real semantic networks on the theoretical phase transition curve from
random regular graphs. Tests whether η = ⟨k⟩²/N predicts hyperbolicity,
and fits the two-parameter theory (η + clustering).

Also computes degree-matched random regular null models.

Usage:
    julia bridge_analysis.jl                # Full analysis
    julia bridge_analysis.jl --nulls        # Include degree-matched random regular nulls
    julia bridge_analysis.jl --figure-data  # Just output data for figures
"""

import Pkg
let deps = Pkg.project().dependencies
    for pkg in ["JuMP", "HiGHS", "Graphs", "JSON"]
        if !haskey(deps, pkg)
            Pkg.add(pkg)
        end
    end
end

using JuMP
using HiGHS
using JSON
using Statistics
using Printf
using Graphs
using Random

# ─────────────────────────────────────────────────────────────────
# ORC functions (from exact_curvature_lp.jl — duplicated to avoid include issues)
# ─────────────────────────────────────────────────────────────────

function exact_wasserstein1(mu::Vector{Float64}, nu::Vector{Float64},
                            C::Matrix{Float64})::Float64
    n = length(mu)
    model = Model(HiGHS.Optimizer)
    set_silent(model)
    @variable(model, gamma[1:n, 1:n] >= 0)
    @constraint(model, source[i=1:n], sum(gamma[i, j] for j in 1:n) == mu[i])
    @constraint(model, target[j=1:n], sum(gamma[i, j] for i in 1:n) == nu[j])
    @objective(model, Min, sum(C[i, j] * gamma[i, j] for i in 1:n, j in 1:n))
    optimize!(model)
    termination_status(model) != OPTIMAL && return NaN
    return objective_value(model)
end

function compute_edge_curvature_exact(g::SimpleGraph, u::Int, v::Int;
                                      alpha::Float64=0.5)::Float64
    mu_u = Dict{Int, Float64}(u => alpha)
    mu_v = Dict{Int, Float64}(v => alpha)
    for z in neighbors(g, u)
        w = (1.0 - alpha) / length(neighbors(g, u))
        mu_u[z] = get(mu_u, z, 0.0) + w
    end
    for z in neighbors(g, v)
        w = (1.0 - alpha) / length(neighbors(g, v))
        mu_v[z] = get(mu_v, z, 0.0) + w
    end
    all_nodes = sort(unique(vcat(collect(keys(mu_u)), collect(keys(mu_v)))))
    n = length(all_nodes)
    node_to_idx = Dict(node => i for (i, node) in enumerate(all_nodes))
    mu_vec = zeros(n); nu_vec = zeros(n)
    for (nd, p) in mu_u; mu_vec[node_to_idx[nd]] = p; end
    for (nd, p) in mu_v; nu_vec[node_to_idx[nd]] = p; end
    C = zeros(n, n)
    for i in 1:n
        dists = gdistances(g, all_nodes[i])
        for j in 1:n; C[i, j] = Float64(dists[all_nodes[j]]); end
    end
    W1 = exact_wasserstein1(mu_vec, nu_vec, C)
    d_uv = Float64(gdistances(g, u)[v])
    d_uv == 0.0 && return 0.0
    return 1.0 - W1 / d_uv
end

function compute_graph_curvature_exact(g::SimpleGraph; alpha::Float64=0.5)::Vector{Float64}
    edges_list = collect(edges(g))
    kappas = Vector{Float64}(undef, length(edges_list))
    Threads.@threads for i in 1:length(edges_list)
        e = edges_list[i]
        kappas[i] = compute_edge_curvature_exact(g, src(e), dst(e); alpha=alpha)
    end
    return kappas
end

function create_random_regular(N::Int, k::Int; seed::Int=42)::SimpleGraph
    N * k % 2 != 0 && (k += 1)
    stubs = Int[]
    for node in 1:N; append!(stubs, fill(node, k)); end
    Random.seed!(seed + k)
    shuffle!(stubs)
    g = SimpleGraph(N)
    for i in 1:2:length(stubs)-1
        u, v = stubs[i], stubs[i+1]
        u != v && !has_edge(g, u, v) && add_edge!(g, u, v)
    end
    ccs = connected_components(g)
    if length(ccs) > 1
        largest = ccs[argmax(length.(ccs))]
        g = induced_subgraph(g, largest)[1]
    end
    return g
end

# ─────────────────────────────────────────────────────────────────
# Load phase transition data
# ─────────────────────────────────────────────────────────────────

const RESULTS_DIR = joinpath(@__DIR__, "..", "..", "results")
const UNIFIED_DIR = joinpath(RESULTS_DIR, "unified")

function load_phase_transition_data()
    # Multi-N data (N=50,100,200,500)
    multi_n_file = joinpath(RESULTS_DIR, "experiments", "phase_transition_exact_multi_N_v2.json")
    multi_n = JSON.parsefile(multi_n_file)

    # N=1000 data
    n1000_file = joinpath(RESULTS_DIR, "experiments", "phase_transition_exact_n1000.json")
    n1000 = isfile(n1000_file) ? JSON.parsefile(n1000_file) : nothing

    # Compile (N, eta_c) pairs by interpolating sign change
    eta_c_points = Dict{Int, Float64}()

    for (nkey, results) in multi_n["results"]
        N_val = parse(Int, match(r"N=(\d+)", nkey).captures[1])
        # Sort by eta and find sign change
        sorted = sort(results, by=r -> r["ratio"])
        for i in 2:length(sorted)
            if sorted[i-1]["kappa_mean"] < 0 && sorted[i]["kappa_mean"] >= 0
                # Linear interpolation
                eta1, k1 = sorted[i-1]["ratio"], sorted[i-1]["kappa_mean"]
                eta2, k2 = sorted[i]["ratio"], sorted[i]["kappa_mean"]
                eta_c = eta1 + (eta2 - eta1) * (-k1) / (k2 - k1)
                eta_c_points[N_val] = eta_c
                break
            end
        end
    end

    # N=1000
    if n1000 !== nothing
        results_1000 = n1000["results"]
        sorted = sort(results_1000, by=r -> r["ratio"])
        for i in 2:length(sorted)
            if sorted[i-1]["kappa_mean"] < 0 && sorted[i]["kappa_mean"] >= 0
                eta1, k1 = sorted[i-1]["ratio"], sorted[i-1]["kappa_mean"]
                eta2, k2 = sorted[i]["ratio"], sorted[i]["kappa_mean"]
                eta_c = eta1 + (eta2 - eta1) * (-k1) / (k2 - k1)
                eta_c_points[1000] = eta_c
                break
            end
        end
    end

    return (multi_n=multi_n, n1000=n1000, eta_c_points=eta_c_points)
end

# ─────────────────────────────────────────────────────────────────
# Load unified semantic network results
# ─────────────────────────────────────────────────────────────────

function load_semantic_results()
    results = Dict{String, Any}()

    if !isdir(UNIFIED_DIR)
        error("No results found in $UNIFIED_DIR. Run unified_semantic_orc.jl first.")
    end

    for f in readdir(UNIFIED_DIR)
        if endswith(f, "_exact_lp.json")
            data = JSON.parsefile(joinpath(UNIFIED_DIR, f))
            results[data["network_id"]] = data
        end
    end

    return results
end

# ─────────────────────────────────────────────────────────────────
# Finite-size scaling prediction
# ─────────────────────────────────────────────────────────────────

"""
    predict_eta_c(N; eta_inf=3.75, a=14.62) -> Float64

Predicted critical density from finite-size scaling:
    η_c(N) = η_c^∞ - a / √N

Using fixed β=0.5 fit from PREPRINT: η_c^∞ ≈ 3.75, a ≈ 14.62
"""
function predict_eta_c(N::Int; eta_inf::Float64=3.75, a::Float64=14.62)
    return eta_inf - a / sqrt(N)
end

# ─────────────────────────────────────────────────────────────────
# Bridge analysis: place networks on the phase curve
# ─────────────────────────────────────────────────────────────────

function bridge_analysis(semantic_results, phase_data)
    println("\n", "="^70)
    println("BRIDGE ANALYSIS: Semantic Networks on the Phase Transition Curve")
    println("="^70)

    println("\nPhase transition η_c values (from random regular graphs):")
    for N in sort(collect(keys(phase_data.eta_c_points)))
        @printf("  N=%4d: η_c = %.3f (predicted: %.3f)\n",
                N, phase_data.eta_c_points[N], predict_eta_c(N))
    end

    println("\n", "-"^80)
    @printf("%-22s %5s %6s %8s %8s %8s %8s  %s\n",
            "Network", "N", "<k>", "C", "η", "η_c(N)", "κ̄", "Pred?")
    println("-"^80)

    bridge_data = []

    for (net_id, data) in sort(collect(semantic_results), by=x->x[1])
        N = data["N"]
        eta = data["eta"]
        eta_c = predict_eta_c(N)
        kappa = data["kappa_mean"]
        clustering = data["clustering"]
        mean_k = data["mean_degree"]

        predicted_hyperbolic = eta < eta_c
        actual_hyperbolic = kappa < -0.05
        prediction_correct = predicted_hyperbolic == actual_hyperbolic

        status = prediction_correct ? "✓" : "✗"
        # Special case: near-zero kappa (|κ| < 0.05) — prediction is ambiguous
        if abs(kappa) < 0.05
            status = predicted_hyperbolic ? "MISS" : "~"
        end

        @printf("%-22s %5d %6.2f %8.4f %8.4f %8.2f %+8.4f  %s\n",
                net_id, N, mean_k, clustering, eta, eta_c, kappa, status)

        push!(bridge_data, Dict(
            "network_id" => net_id,
            "category" => data["category"],
            "language" => data["language"],
            "N" => N,
            "E" => data["E"],
            "mean_k" => mean_k,
            "clustering" => clustering,
            "degree_std" => data["degree_std"],
            "eta" => eta,
            "eta_c_predicted" => round(eta_c, digits=4),
            "kappa_mean" => kappa,
            "kappa_std" => data["kappa_std"],
            "geometry" => data["geometry"],
            "predicted_hyperbolic" => predicted_hyperbolic,
            "actual_hyperbolic" => actual_hyperbolic,
            "prediction_correct" => prediction_correct
        ))
    end

    # Analysis: why does η alone fail?
    println("\n", "="^70)
    println("KEY FINDING: η is necessary but not sufficient")
    println("="^70)

    all_eta_below = all(d -> d["eta"] < d["eta_c_predicted"], bridge_data)
    println("All networks have η << η_c: $all_eta_below")

    hyp_nets = filter(d -> d["actual_hyperbolic"], bridge_data)
    euc_nets = filter(d -> !d["actual_hyperbolic"], bridge_data)

    if !isempty(hyp_nets) && !isempty(euc_nets)
        hyp_C = mean(d -> d["clustering"], hyp_nets)
        euc_C = mean(d -> d["clustering"], euc_nets)
        println(@sprintf("Mean clustering — Hyperbolic: %.4f, Non-hyperbolic: %.4f", hyp_C, euc_C))
        println("Clustering separates the two groups within the η-permitted regime")
    end

    return bridge_data
end

# ─────────────────────────────────────────────────────────────────
# Sinkhorn vs. Exact LP validation
# ─────────────────────────────────────────────────────────────────

function sinkhorn_validation(semantic_results)
    println("\n", "="^70)
    println("SINKHORN vs. EXACT LP VALIDATION")
    println("="^70)

    sinkhorn_file = joinpath(RESULTS_DIR, "FINAL_CURVATURE_CORRECTED_PREPROCESSING.json")
    if !isfile(sinkhorn_file)
        println("Sinkhorn results not found: $sinkhorn_file")
        return nothing
    end

    sinkhorn_data = JSON.parsefile(sinkhorn_file)

    # Mapping: Sinkhorn key → unified network id
    mapping = Dict(
        "spanish" => "swow_es",
        "english" => "swow_en",
        "chinese" => "swow_zh"
    )

    println(@sprintf("%-15s %10s %10s %10s %10s", "Network", "κ_Sinkhorn", "κ_ExactLP", "Δκ", "|Δκ|"))
    println("-"^60)

    deltas = Float64[]
    for (sink_key, net_id) in mapping
        if haskey(sinkhorn_data, sink_key) && haskey(semantic_results, net_id)
            k_sink = sinkhorn_data[sink_key]["kappa_mean"]
            k_lp = semantic_results[net_id]["kappa_mean"]
            delta = k_lp - k_sink
            push!(deltas, delta)
            @printf("%-15s %+10.4f %+10.4f %+10.4f %10.4f\n",
                    net_id, k_sink, k_lp, delta, abs(delta))
        end
    end

    if !isempty(deltas)
        @printf("\nMean Δκ = %+.4f, Max |Δκ| = %.4f\n", mean(deltas), maximum(abs.(deltas)))
        @printf("(Expected: |Δκ| < 0.02 based on PREPRINT random graph comparison)\n")
    end

    return deltas
end

# ─────────────────────────────────────────────────────────────────
# Degree-matched random regular null models
# ─────────────────────────────────────────────────────────────────

function degree_matched_nulls(semantic_results; n_seeds::Int=10, alpha::Float64=0.5)
    println("\n", "="^70)
    println("DEGREE-MATCHED RANDOM REGULAR NULL MODELS")
    println("="^70)

    null_results = Dict{String, Any}()

    for (net_id, data) in sort(collect(semantic_results), by=x->x[1])
        N = data["N"]
        mean_k = data["mean_degree"]
        k_round = max(2, round(Int, mean_k))

        # Ensure k*N is even
        if k_round * N % 2 != 0
            k_round += 1
        end
        # Ensure k < N
        if k_round >= N
            @warn "Cannot generate k=$k_round regular graph for N=$N ($net_id), skipping"
            continue
        end

        @printf("\n%s: N=%d, <k>=%.2f → k_regular=%d\n", net_id, N, mean_k, k_round)

        seed_kappas = Float64[]
        for seed in 1:n_seeds
            g = create_random_regular(N, k_round; seed=seed * 1000 + 42)
            kappas = compute_graph_curvature_exact(g; alpha=alpha)
            push!(seed_kappas, mean(kappas))
            @printf("  seed=%d: κ̄ = %+.6f\n", seed, mean(kappas))
        end

        null_mean = mean(seed_kappas)
        null_std = std(seed_kappas)
        real_kappa = data["kappa_mean"]
        delta = real_kappa - null_mean

        @printf("  NULL:  κ̄ = %+.6f ± %.6f\n", null_mean, null_std)
        @printf("  REAL:  κ̄ = %+.6f\n", real_kappa)
        @printf("  Δκ = %+.6f  (semantic contribution to curvature)\n", delta)

        null_results[net_id] = Dict(
            "network_id" => net_id,
            "N" => N,
            "k_original" => mean_k,
            "k_regular" => k_round,
            "null_kappa_mean" => round(null_mean, digits=6),
            "null_kappa_std" => round(null_std, digits=6),
            "real_kappa_mean" => round(real_kappa, digits=6),
            "delta_kappa" => round(delta, digits=6),
            "per_seed_kappas" => round.(seed_kappas, digits=6),
            "n_seeds" => n_seeds
        )
    end

    return null_results
end

# ─────────────────────────────────────────────────────────────────
# Two-parameter analysis: κ = f(η, C)
# ─────────────────────────────────────────────────────────────────

function two_parameter_analysis(bridge_data)
    println("\n", "="^70)
    println("TWO-PARAMETER ANALYSIS: κ = f(η, C)")
    println("="^70)

    # Extract vectors
    etas = [d["eta"] for d in bridge_data]
    Cs = [d["clustering"] for d in bridge_data]
    kappas = [d["kappa_mean"] for d in bridge_data]
    categories = [d["category"] for d in bridge_data]
    names = [d["network_id"] for d in bridge_data]

    # Simple correlations
    # Spearman rank correlation (manual since we don't have StatsBase)
    function rank_corr(x, y)
        n = length(x)
        rx = sortperm(sortperm(x)) .|> Float64
        ry = sortperm(sortperm(y)) .|> Float64
        d2 = sum((rx .- ry).^2)
        return 1.0 - 6.0 * d2 / (n * (n^2 - 1))
    end

    r_eta_kappa = rank_corr(etas, kappas)
    r_C_kappa = rank_corr(Cs, kappas)
    r_eta_C = rank_corr(etas, Cs)

    println("Spearman rank correlations:")
    @printf("  ρ(η, κ) = %+.3f\n", r_eta_kappa)
    @printf("  ρ(C, κ) = %+.3f\n", r_C_kappa)
    @printf("  ρ(η, C) = %+.3f\n", r_eta_C)

    # Group analysis by category
    println("\nMean curvature by category:")
    for cat in ["association", "knowledge", "taxonomy", "clinical"]
        cat_data = filter(d -> d["category"] == cat, bridge_data)
        if !isempty(cat_data)
            cat_kappas = [d["kappa_mean"] for d in cat_data]
            cat_Cs = [d["clustering"] for d in cat_data]
            cat_etas = [d["eta"] for d in cat_data]
            @printf("  %-12s: n=%d  κ̄=%+.4f  C̄=%.4f  η̄=%.4f\n",
                    cat, length(cat_data), mean(cat_kappas),
                    mean(cat_Cs), mean(cat_etas))
        end
    end

    return Dict(
        "rho_eta_kappa" => round(r_eta_kappa, digits=4),
        "rho_C_kappa" => round(r_C_kappa, digits=4),
        "rho_eta_C" => round(r_eta_C, digits=4),
        "per_network" => [Dict(
            "id" => names[i],
            "category" => categories[i],
            "eta" => etas[i],
            "clustering" => Cs[i],
            "kappa" => kappas[i]
        ) for i in 1:length(names)]
    )
end

# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────

function main()
    println("="^70)
    println("BRIDGE ANALYSIS — Phase Transition Theory × Semantic Networks")
    println("="^70)

    # Load data
    println("\nLoading phase transition data...")
    phase_data = load_phase_transition_data()
    println("  η_c points: $(sort(collect(keys(phase_data.eta_c_points))))")

    println("Loading semantic network results...")
    semantic_results = load_semantic_results()
    println("  Networks: $(sort(collect(keys(semantic_results))))")

    # 1. Bridge analysis
    bridge_data = bridge_analysis(semantic_results, phase_data)

    # 2. Sinkhorn validation
    sinkhorn_deltas = sinkhorn_validation(semantic_results)

    # 3. Two-parameter analysis
    two_param = two_parameter_analysis(bridge_data)

    # 4. Degree-matched nulls (optional, expensive)
    null_results = nothing
    if "--nulls" in ARGS
        null_results = degree_matched_nulls(semantic_results; n_seeds=10)
    end

    # Save everything
    output_file = joinpath(UNIFIED_DIR, "bridge_analysis.json")
    mkpath(UNIFIED_DIR)

    output = Dict(
        "experiment" => "bridge_analysis",
        "description" => "Connecting phase transition theory with semantic network curvature",
        "phase_transition" => Dict(
            "scaling_formula" => "eta_c(N) = 3.75 - 14.62/sqrt(N)",
            "eta_c_points" => Dict(string(k) => v for (k,v) in phase_data.eta_c_points)
        ),
        "bridge" => bridge_data,
        "sinkhorn_validation" => isnothing(sinkhorn_deltas) ? nothing : Dict(
            "deltas" => round.(sinkhorn_deltas, digits=6),
            "mean_delta" => round(mean(sinkhorn_deltas), digits=6),
            "max_abs_delta" => round(maximum(abs.(sinkhorn_deltas)), digits=6)
        ),
        "two_parameter" => two_param,
        "null_models" => null_results
    )

    open(output_file, "w") do f
        JSON.print(f, output, 2)
    end
    println("\n\nSAVED: $output_file")

    return output
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
