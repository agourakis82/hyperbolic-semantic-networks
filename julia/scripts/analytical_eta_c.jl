"""
ANALYTICAL η_c DERIVATION FROM HEHL FORMULA

Extends the Hehl matching heuristic (hehl_improved_analytical.jl) with
clustering-dependent triangle counts to derive an analytical phase boundary
η_c(N, C) for ORC sign change.

Key insight: In real networks, expected common neighbors E[t] is driven by
clustering coefficient C, not random incidence. Substituting t = C·(k−1) into
the Hehl framework gives κ(η, C, k, N) and the analytical boundary η_c(N, C).

This explains WHY taxonomies (C≈0) are Euclidean while association networks
(C>0.10) are hyperbolic under the same η regime.

References:
  [1] M. Hehl et al., arXiv:2407.08854 — Ollivier-Ricci curvature of regular graphs
  [2] Phase transition data from results/experiments/

Usage:
    julia analytical_eta_c.jl
"""

using Statistics
using Random
using JSON
using Printf
using Distributions

# ─────────────────────────────────────────────────────────────────
# Core analytical functions
# ─────────────────────────────────────────────────────────────────

"""
    hehl_kappa(k, eta, C, N; alpha=0.5)

Clustering-dependent ORC approximation via Hehl's formula.

Uses the matching heuristic for exclusive neighborhood transport,
with triangle count driven by clustering coefficient C.

# Arguments
- `k`: degree (integer or float)
- `eta`: density parameter η = k²/N
- `C`: clustering coefficient
- `N`: number of nodes
- `alpha`: idleness parameter (default 0.5)

# Returns
- Approximate mean ORC κ
"""
function hehl_kappa(k::Real, eta::Real, C::Real, N::Real; alpha::Float64=0.5)
    k = Float64(k)

    # Expected common neighbors from two sources:
    # 1. Random incidence (Erdős-Rényi-like): t_rand = (k-1)²/(N-1)
    # 2. Clustering-driven: t_clust = C·(k-1)
    t_rand = (k - 1)^2 / (N - 1)
    t_clust = C * (k - 1)
    t = max(t_rand, t_clust)
    t = clamp(t, 0.0, k - 1)

    # Exclusive neighbors per side
    n_exc = max(0.0, k - 1 - t)

    if n_exc < 1e-10
        # Only triangles — can match at cost 0
        W1 = alpha * 1.0
        return 1.0 - W1
    end

    # Edge probability in exclusive bipartite graph
    p_edge = eta / k

    # Expected maximum matching in random bipartite graph
    # Heuristic: E[|M|] = n_exc · (1 − exp(−p_edge · n_exc))
    expected_matching = n_exc * (1.0 - exp(-p_edge * n_exc))
    expected_matching = min(expected_matching, n_exc)

    frac_matched = expected_matching / n_exc

    # Mass per exclusive node
    mass_exc = (1 - alpha) * n_exc / k

    # Transport costs:
    # - Matched edges: cost 1 (direct neighbor-to-neighbor)
    # - Unmatched: cost 3 (exc_u → u → v → exc_v)
    cost_matched = mass_exc * frac_matched * 1.0
    cost_unmatched = mass_exc * (1 - frac_matched) * 3.0

    # Triangle mass: cost 0 (stays put)
    cost_triangles = 0.0

    # Idleness: α from u to v, cost 1
    cost_idle = alpha * 1.0

    # Total Wasserstein-1
    W1 = cost_idle + cost_triangles + cost_matched + cost_unmatched

    return 1.0 - W1
end

"""
    hehl_kappa_sampled(k, eta, C, N; alpha=0.5, n_samples=1000)

Sample-based version: draw t from Poisson(C·(k-1)) and average.
More accurate than the deterministic version for moderate k.
"""
function hehl_kappa_sampled(k::Int, eta::Float64, C::Float64, N::Int;
                             alpha::Float64=0.5, n_samples::Int=1000,
                             rng::AbstractRNG=Random.GLOBAL_RNG)
    curvatures = Float64[]

    # Mean triangles from clustering
    lambda_t = C * (k - 1)
    # Also consider random incidence
    lambda_rand = (k - 1)^2 / (N - 1)
    lambda = max(lambda_t, lambda_rand)

    for _ in 1:n_samples
        t = rand(rng, Poisson(lambda))
        t = clamp(t, 0, k - 1)

        n_exc = max(0, k - 1 - t)

        if n_exc == 0
            push!(curvatures, 1.0 - alpha)
            continue
        end

        p_edge = eta / k
        expected_matching = n_exc * (1.0 - exp(-p_edge * n_exc))
        expected_matching = min(expected_matching, Float64(n_exc))
        frac_matched = expected_matching / n_exc

        mass_exc = (1 - alpha) * n_exc / k
        W1 = alpha + mass_exc * frac_matched + mass_exc * (1 - frac_matched) * 3.0

        push!(curvatures, 1.0 - W1)
    end

    return mean(curvatures), std(curvatures)
end

# ─────────────────────────────────────────────────────────────────
# Root-finding: η_c(N, C)
# ─────────────────────────────────────────────────────────────────

"""
    find_eta_c(N, C; alpha=0.5, tol=1e-4)

Find the critical η where κ crosses zero, via bisection.
Converts η to k via k = √(η·N).

Returns η_c or nothing if no crossing found in [0.01, 20].
"""
function find_eta_c(N::Real, C::Real; alpha::Float64=0.5, tol::Float64=1e-4)
    # Minimum η such that k = √(η·N) ≥ 2
    eta_min = 4.0 / N
    eta_lo, eta_hi = eta_min, 20.0

    k_lo = sqrt(eta_lo * N)
    k_hi = sqrt(eta_hi * N)

    kappa_lo = hehl_kappa(k_lo, eta_lo, C, N; alpha=alpha)
    kappa_hi = hehl_kappa(k_hi, eta_hi, C, N; alpha=alpha)

    # Check if there's a sign change
    if kappa_lo >= 0
        return eta_lo  # Already positive at minimum η
    end
    if kappa_hi <= 0
        return nothing  # Never crosses zero
    end

    # Bisection
    for _ in 1:100
        eta_mid = (eta_lo + eta_hi) / 2
        k_mid = sqrt(eta_mid * N)
        kappa_mid = hehl_kappa(k_mid, eta_mid, C, N; alpha=alpha)

        if abs(kappa_mid) < tol
            return eta_mid
        elseif kappa_mid < 0
            eta_lo = eta_mid
        else
            eta_hi = eta_mid
        end
    end

    return (eta_lo + eta_hi) / 2
end

# ─────────────────────────────────────────────────────────────────
# Phase boundary sweep
# ─────────────────────────────────────────────────────────────────

"""
    analytical_boundary(; C_range, N_values)

Compute η_c(C) curves for multiple N values.
"""
function analytical_boundary(;
    C_range::AbstractRange=0.0:0.01:0.30,
    N_values::Vector{Int}=[100, 200, 500, 1000, 10000]
)
    results = Dict{String, Any}()

    for N in N_values
        curve = Dict{String, Any}[]
        for C in C_range
            eta_c = find_eta_c(N, C)
            push!(curve, Dict("C" => C, "eta_c" => eta_c))
        end
        results["N=$N"] = curve
    end

    return results
end

# ─────────────────────────────────────────────────────────────────
# Validation: random regular N=1000
# ─────────────────────────────────────────────────────────────────

function validate_n1000()
    @info "Validating against N=1000 random regular data..."

    # Load empirical data
    data_path = joinpath(@__DIR__, "..", "..", "results", "experiments",
                         "phase_transition_exact_n1000.json")

    if !isfile(data_path)
        @warn "N=1000 data not found at $data_path"
        return nothing
    end

    emp_data = JSON.parsefile(data_path)["results"]

    N = 1000
    C_rand = 0.0  # Random regular: clustering ≈ 0 for large N
    alpha = 0.5

    comparisons = Dict{String, Any}[]

    @printf("%-4s %6s %10s %10s %10s\n", "k", "η", "κ_emp", "κ_anl", "error")
    @printf("%s\n", "-"^44)

    for point in emp_data
        k = point["k_target"]
        eta = point["ratio"]
        kappa_emp = point["kappa_mean"]

        # Analytical prediction (C≈0 for random regular)
        # For random regular, clustering = (k-1)/(N-1) ≈ k/N
        C_rr = (k - 1) / (N - 1)
        kappa_anl = hehl_kappa(k, eta, C_rr, N; alpha=alpha)

        err = abs(kappa_emp - kappa_anl)

        push!(comparisons, Dict(
            "k" => k, "eta" => eta,
            "kappa_empirical" => kappa_emp,
            "kappa_analytical" => kappa_anl,
            "error" => err
        ))

        @printf("%4d %6.3f %+.6f %+.6f %10.6f\n", k, eta, kappa_emp, kappa_anl, err)
    end

    mse = mean([c["error"]^2 for c in comparisons])
    mae = mean([c["error"] for c in comparisons])

    @info "Validation: MSE=$(round(mse, digits=6)), MAE=$(round(mae, digits=6))"

    # Find analytical η_c
    eta_c_anl = find_eta_c(N, 0.0)
    @info "Analytical η_c(N=1000, C=0) = $(round(eta_c_anl, digits=3))"
    @info "Empirical η_c(N=1000) ≈ 3.32"

    return Dict(
        "comparisons" => comparisons,
        "mse" => mse,
        "mae" => mae,
        "eta_c_analytical" => eta_c_anl,
        "eta_c_empirical" => 3.32
    )
end

# ─────────────────────────────────────────────────────────────────
# Validation: semantic networks
# ─────────────────────────────────────────────────────────────────

function validate_semantic_networks()
    @info "\nValidating against 11 semantic networks..."

    # Load bridge analysis for network properties
    bridge_path = joinpath(@__DIR__, "..", "..", "results", "unified", "bridge_analysis.json")
    if !isfile(bridge_path)
        @warn "Bridge analysis not found"
        return nothing
    end

    bridge = JSON.parsefile(bridge_path)
    networks = bridge["bridge"]

    comparisons = Dict{String, Any}[]

    @printf("\n%-20s %5s %5s %6s %6s %+9s %+9s %9s\n",
            "Network", "N", "k", "η", "C", "κ_real", "κ_anl", "error")
    @printf("%s\n", "-"^82)

    for net in networks
        id = net["network_id"]
        N = net["N"]
        k = net["mean_k"]
        eta = net["eta"]
        C = net["clustering"]
        kappa_real = net["kappa_mean"]

        # Analytical prediction
        kappa_anl = hehl_kappa(k, eta, C, N)
        err = abs(kappa_real - kappa_anl)

        push!(comparisons, Dict(
            "network_id" => id,
            "N" => N,
            "mean_k" => k,
            "eta" => eta,
            "clustering" => C,
            "kappa_real" => kappa_real,
            "kappa_analytical" => kappa_anl,
            "error" => err,
            "sign_match" => sign(kappa_real) == sign(kappa_anl)
        ))

        @printf("%-20s %5d %5.1f %6.3f %6.3f %+9.4f %+9.4f %9.4f\n",
                id, N, k, eta, C, kappa_real, kappa_anl, err)
    end

    mae = mean([c["error"] for c in comparisons])
    sign_accuracy = sum([c["sign_match"] ? 1 : 0 for c in comparisons]) / length(comparisons)

    @info "Semantic networks: MAE=$(round(mae, digits=4)), sign accuracy=$(round(sign_accuracy*100, digits=1))%"

    return Dict(
        "comparisons" => comparisons,
        "mae" => mae,
        "sign_accuracy" => sign_accuracy
    )
end

# ─────────────────────────────────────────────────────────────────
# Validation: η_c scaling across N
# ─────────────────────────────────────────────────────────────────

function validate_eta_c_scaling()
    @info "\nValidating η_c(N) scaling..."

    # Empirical η_c values from bridge analysis
    Ns = [50, 100, 200, 500, 1000]
    eta_c_emp = [1.7292, 2.2167, 2.7065, 3.0922, 3.3213]

    comparisons = Dict{String, Any}[]

    @printf("\n%6s %8s %8s %8s\n", "N", "η_c emp", "η_c anl", "error")
    @printf("%s\n", "-"^34)

    for (N, eta_emp) in zip(Ns, eta_c_emp)
        eta_anl = find_eta_c(N, 0.0)  # C=0 for random regular
        err = eta_anl !== nothing ? abs(eta_emp - eta_anl) : NaN

        push!(comparisons, Dict(
            "N" => N,
            "eta_c_empirical" => eta_emp,
            "eta_c_analytical" => eta_anl,
            "error" => err
        ))

        eta_str = eta_anl !== nothing ? @sprintf("%.4f", eta_anl) : "N/A"
        @printf("%6d %8.4f %8s %8.4f\n", N, eta_emp, eta_str, err)
    end

    valid = filter(c -> !isnan(c["error"]), comparisons)
    if !isempty(valid)
        mae = mean([c["error"] for c in valid])
        @info "η_c scaling: MAE=$(round(mae, digits=4))"
    end

    return comparisons
end

# ─────────────────────────────────────────────────────────────────
# Figure 8 data: Analytical phase boundary
# (Actual rendering done in generate_monograph_figures.jl)
# ─────────────────────────────────────────────────────────────────

"""
    compute_figure8_data()

Pre-compute analytical boundary curves for Figure 8.
Returns data dict saved to JSON for plotting by generate_monograph_figures.jl.
"""
function compute_figure8_data()
    @info "\nComputing Figure 8 data: Analytical Phase Boundary..."

    C_range = collect(0.0:0.005:0.30)
    N_values = [100, 200, 500, 1000]
    N_inf_approx = 100000

    curves = Dict{String, Any}()

    # N→∞ curve
    eta_c_inf = Float64[]
    for C in C_range
        eta_c = find_eta_c(N_inf_approx, C)
        push!(eta_c_inf, eta_c !== nothing ? eta_c : NaN)
    end
    curves["N_inf"] = Dict("C" => C_range, "eta_c" => eta_c_inf)

    # Finite N curves
    for N in N_values
        eta_c_curve = Float64[]
        for C in C_range
            eta_c = find_eta_c(N, C)
            push!(eta_c_curve, eta_c !== nothing ? eta_c : NaN)
        end
        curves["N=$N"] = Dict("C" => C_range, "eta_c" => eta_c_curve)
    end

    return curves
end

# ─────────────────────────────────────────────────────────────────
# Configuration model nulls
# ─────────────────────────────────────────────────────────────────

"""
    run_config_nulls(; n_replicates=10)

Generate configuration model null networks for 5 key semantic networks
and compute ORC statistics.

Note: This requires loading the actual network edge lists and computing
ORC via LP, so it takes ~30 min. For now, we produce analytical predictions
using the Hehl formula with the actual degree distribution statistics.
"""
function config_null_predictions()
    @info "\nConfiguration model null predictions (analytical)..."

    # Load bridge analysis for network properties
    bridge_path = joinpath(@__DIR__, "..", "..", "results", "unified", "bridge_analysis.json")
    if !isfile(bridge_path)
        @warn "Bridge analysis not found"
        return nothing
    end

    bridge = JSON.parsefile(bridge_path)
    null_models = bridge["null_models"]

    # Key networks for config null comparison
    target_ids = ["depression_minimum", "conceptnet_en", "swow_nl", "swow_zh", "wordnet_en"]

    comparisons = Dict{String, Any}[]

    @printf("\n%-20s %5s %6s %6s %+9s %+9s %+9s\n",
            "Network", "k", "C", "η", "κ_real", "κ_k-reg", "κ_config")
    @printf("%s\n", "-"^72)

    for net in bridge["bridge"]
        id = net["network_id"]
        id in target_ids || continue

        N = net["N"]
        k = net["mean_k"]
        eta = net["eta"]
        C = net["clustering"]
        kappa_real = net["kappa_mean"]

        # k-regular null (from null_models)
        kappa_kreg = haskey(null_models, id) ? null_models[id]["null_kappa_mean"] : NaN

        # Config model prediction: same mean degree but C ≈ k/N (random)
        # Config model preserves degree sequence → heterogeneity matters
        # For config model, clustering ≈ (⟨k²⟩ - ⟨k⟩)² / (N · ⟨k⟩³)
        # Approximation: C_config ≈ k/(N-1) for not-too-heterogeneous networks
        C_config = k / (N - 1)

        # Config model also has degree heterogeneity: coefficient of variation
        # For k-regular: CV=0. For config model: CV > 0 → asymmetric neighborhoods → more negative κ
        # Heuristic correction: κ_config ≈ κ_kreg × (1 + 0.1 × CV²)
        # Since we don't have the actual degree distribution, use bridge null as proxy
        kappa_config = hehl_kappa(k, eta, C_config, N)

        push!(comparisons, Dict(
            "network_id" => id,
            "N" => N, "mean_k" => k, "eta" => eta, "clustering" => C,
            "kappa_real" => kappa_real,
            "kappa_kregular" => kappa_kreg,
            "kappa_config_analytical" => kappa_config,
            "C_config" => C_config
        ))

        @printf("%-20s %5.1f %6.3f %6.3f %+9.4f %+9.4f %+9.4f\n",
                id, k, C, eta, kappa_real, kappa_kreg, kappa_config)
    end

    return comparisons
end

# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────

function main()
    @info "="^70
    @info "ANALYTICAL η_c DERIVATION FROM HEHL FORMULA"
    @info "="^70

    results = Dict{String, Any}()

    # 1. Validate against N=1000 random regular
    n1000 = validate_n1000()
    if n1000 !== nothing
        results["n1000_validation"] = n1000
    end

    # 2. Validate against semantic networks
    semantic = validate_semantic_networks()
    if semantic !== nothing
        results["semantic_validation"] = semantic
    end

    # 3. Validate η_c scaling
    scaling = validate_eta_c_scaling()
    results["eta_c_scaling"] = scaling

    # 4. Compute phase boundary
    @info "\nComputing analytical phase boundaries..."
    boundary = analytical_boundary()
    results["phase_boundary"] = boundary

    # Print η_c(C) for key C values at N→∞
    @printf("\n%8s %8s\n", "C", "η_c(∞)")
    @printf("%s\n", "-"^18)
    for C in [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30]
        eta_c = find_eta_c(100000, C)
        eta_str = eta_c !== nothing ? @sprintf("%.3f", eta_c) : "N/A"
        @printf("%8.2f %8s\n", C, eta_str)
    end

    # 5. Config null predictions
    config = config_null_predictions()
    if config !== nothing
        results["config_null_predictions"] = config
    end

    # 6. Key formulas for monograph
    results["formulas"] = Dict(
        "hehl_kappa" => "κ(k,η,C,N) = 1 - [α + (1-α)·n_exc/k · (f_m + 3(1-f_m))]",
        "n_exc" => "n_exc = k - 1 - max(C·(k-1), (k-1)²/(N-1))",
        "matching" => "E[|M|] = n_exc · (1 - exp(-η·n_exc/k²))",
        "f_matched" => "f_m = E[|M|]/n_exc",
        "eta_c" => "η_c(N,C) = root of κ(√(η·N), η, C, N) = 0"
    )

    # 7. Compute Figure 8 data (rendered by generate_monograph_figures.jl)
    fig8_data = compute_figure8_data()
    results["figure8_data"] = fig8_data

    # Save results
    output_path = joinpath(@__DIR__, "..", "..", "results", "unified", "analytical_eta_c.json")
    mkpath(dirname(output_path))

    open(output_path, "w") do f
        JSON.print(f, results, 2)
    end

    @info "\nResults saved to: $output_path"

    return results
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
