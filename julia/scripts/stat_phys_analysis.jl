#!/usr/bin/env julia
#=
Statistical Physics Analysis for J. Stat. Phys. Submission
===========================================================
Computes:
  1. Free-exponent finite-size scaling fit (beta free)
  2. Data collapse plot with optimized gamma
  3. Transition slope scaling (d kappa/d eta at eta_c vs N)
  4. Critical exponent summary table

Requires: JSON, LsqFit, Statistics
=#

import Pkg
let deps = Pkg.project().dependencies
    for pkg in ["JSON"]
        if !haskey(deps, pkg)
            Pkg.add(pkg)
        end
    end
end

using JSON, Statistics, Printf
using LinearAlgebra

# ─────────────────────────────────────────────────────────
# 1. Load data
# ─────────────────────────────────────────────────────────

function load_multi_N(path)
    d = JSON.parsefile(path)
    results = d["results"]
    # Returns Dict: N => [(k, eta, kappa_mean)]
    out = Dict{Int,Vector{NTuple{3,Float64}}}()
    for (key, rlist) in results
        N = parse(Int, split(key, "=")[2])
        pts = NTuple{3,Float64}[]
        for r in rlist
            k = r["k_target"]
            eta = k^2 / N
            kappa = r["kappa_mean"]
            push!(pts, (Float64(k), eta, kappa))
        end
        sort!(pts, by=x->x[1])
        out[N] = pts
    end
    return out
end

function load_n1000(path)
    d = JSON.parsefile(path)
    results = d["results"]
    N = 1000
    pts = NTuple{3,Float64}[]
    for r in results
        k = r["k_target"]
        eta = k^2 / N
        kappa = r["kappa_mean"]
        push!(pts, (Float64(k), eta, kappa))
    end
    sort!(pts, by=x->x[1])
    return Dict(N => pts)
end

multi_N = load_multi_N("../../results/experiments/phase_transition_exact_multi_N_v2.json")
n1000   = load_n1000("../../results/experiments/phase_transition_exact_n1000.json")
all_data = merge(multi_N, n1000)

# ─────────────────────────────────────────────────────────
# 2. Known eta_c values (interpolated from sign changes)
# ─────────────────────────────────────────────────────────

function interpolate_eta_c(pts)
    # Linear interpolation between last negative and first positive kappa
    last_neg = nothing; first_pos = nothing
    for (k, eta, kappa) in pts
        if kappa < 0; last_neg = (eta, kappa); end
        if kappa > 0 && first_pos === nothing; first_pos = (eta, kappa); end
    end
    isnothing(last_neg) || isnothing(first_pos) && return NaN
    e1, k1 = last_neg; e2, k2 = first_pos
    # Linear interpolation: eta_c where kappa = 0
    return e1 + (0 - k1) * (e2 - e1) / (k2 - k1)
end

eta_c_interp = Dict(N => interpolate_eta_c(pts) for (N, pts) in all_data)
N_sorted = sort(collect(keys(all_data)))

println("=== Interpolated eta_c ===")
for N in N_sorted
    @printf("  N=%4d: eta_c = %.4f\n", N, eta_c_interp[N])
end

# ─────────────────────────────────────────────────────────
# 3. Finite-size scaling fits
# ─────────────────────────────────────────────────────────

Nvec   = Float64.(N_sorted)
etavec = [eta_c_interp[N] for N in N_sorted]

# --- 3a. Fixed beta = 0.5 (CLT ansatz) ---
# eta_c(N) = eta_inf - a / sqrt(N)
# Linear regression: y = eta_inf - a * x where x = 1/sqrt(N)
x_fixed = 1.0 ./ sqrt.(Nvec)
A_fixed = hcat(ones(length(x_fixed)), -x_fixed)
coeffs_fixed = A_fixed \ etavec
eta_inf_fixed, a_fixed = coeffs_fixed
resid_fixed = etavec .- (eta_inf_fixed .- a_fixed .* x_fixed)
SS_res = sum(resid_fixed.^2)
SS_tot = sum((etavec .- mean(etavec)).^2)
R2_fixed = 1 - SS_res / SS_tot

println("\n=== Fixed-exponent fit (beta=0.5) ===")
@printf("  eta_inf = %.4f,  a = %.4f,  R² = %.6f\n", eta_inf_fixed, a_fixed, R2_fixed)
println("  Residuals (N=50,100,200,500,1000): ", round.(resid_fixed, digits=4))

# --- 3b. Free-exponent fit (beta free) ---
# eta_c(N) = eta_inf - a * N^(-beta)
# Use gradient-free Nelder-Mead via simple grid search + refinement
function eta_c_model_free(N, params)
    eta_inf, a, beta = params
    return eta_inf .- a .* N.^(-beta)
end

function loss_free(params)
    pred = eta_c_model_free(Nvec, params)
    return sum((etavec .- pred).^2)
end

# Grid search over beta
best_loss = Ref(Inf); best_params = Ref([3.75, 14.62, 0.5])
for beta in 0.1:0.01:1.5
    for eta_inf in 3.0:0.1:6.0
        # For fixed beta and eta_inf, solve for a via LS
        x_free = Nvec.^(-beta)
        a_est = dot(eta_inf .- etavec, x_free) / dot(x_free, x_free)
        params = [eta_inf, a_est, beta]
        l = loss_free(params)
        if l < best_loss[]
            best_loss[] = l
            best_params[] = params
        end
    end
end
best_params_val = best_params[]

# Refine with gradient descent
function refine(params, lr=1e-5, nsteps=100000)
    p = copy(params)
    prev_loss = loss_free(p)
    for _ in 1:nsteps
        eps = 1e-6
        grad = [(loss_free(p .+ eps .* (1:3 .== i)) - loss_free(p)) / eps for i in 1:3]
        p .-= lr .* grad
        p[3] = clamp(p[3], 0.05, 2.0)  # keep beta positive
        p[2] = max(p[2], 0.0)
    end
    return p
end

refined = refine(best_params_val)
eta_inf_free, a_free, beta_free = refined
resid_free = etavec .- eta_c_model_free(Nvec, refined)
SS_res2 = sum(resid_free.^2)
R2_free = 1 - SS_res2 / SS_tot

println("\n=== Free-exponent fit ===")
@printf("  eta_inf = %.4f,  a = %.4f,  beta = %.4f,  R² = %.6f\n",
        eta_inf_free, a_free, beta_free, R2_free)
println("  Residuals: ", round.(resid_free, digits=5))

# Profile likelihood CI for beta (more reliable with 5 points than bootstrap)
println("\n--- Profile CI for beta ---")
# Fit with beta fixed at each value; find range where R² stays within 0.99 of max
ss_tot_local = sum((etavec .- mean(etavec)).^2)
beta_grid = 0.05:0.005:1.5
r2_profile = Float64[]
for beta in beta_grid
    xb = Nvec.^(-beta)
    A = hcat(ones(length(xb)), -xb)
    c = A \ etavec
    resid = etavec .- A * c
    r2 = 1 - sum(resid.^2) / ss_tot_local
    push!(r2_profile, r2)
end
r2_max = maximum(r2_profile)
# 95% CI: region where R² > R²_max - threshold (F-test based: threshold ≈ 0.005 for 5 pts, 3 params)
# More conservative: R² > 0.99 * R²_max
threshold = 0.005
ci_beta = collect(beta_grid)[r2_profile .> r2_max - threshold]
ci_low = isempty(ci_beta) ? NaN : minimum(ci_beta)
ci_high = isempty(ci_beta) ? NaN : maximum(ci_beta)
@printf("  beta = %.3f  [profile CI (R²>%.4f): %.3f, %.3f]\n",
        beta_free, r2_max - threshold, ci_low, ci_high)
@printf("  beta=0.5 within CI: %s\n", ci_low <= 0.5 <= ci_high ? "YES (β=1/2 not ruled out)" : "NO (evidence against CLT scaling)")

# ─────────────────────────────────────────────────────────
# 4. Transition slope at eta_c
# ─────────────────────────────────────────────────────────

println("\n=== Transition slope at eta_c ===")
slopes = Dict{Int,Float64}()
for N in N_sorted
    pts = all_data[N]
    ec = eta_c_interp[N]
    # Find points just below and just above eta_c
    below = filter(x -> x[3] < 0, pts)
    above = filter(x -> x[3] > 0, pts)
    isempty(below) || isempty(above) && continue
    last_neg = last(below)
    first_pos = first(above)
    slope = (first_pos[3] - last_neg[3]) / (first_pos[2] - last_neg[2])
    slopes[N] = slope
    @printf("  N=%4d: slope = %.5f  (k=%d→%d, Δη=%.3f)\n",
            N, slope, Int(last_neg[1]), Int(first_pos[1]),
            first_pos[2] - last_neg[2])
end

# Fit slope ~ a0 * N^alpha  (log-log regression)
N_slope = Float64.(sort(collect(keys(slopes))))
s_slope = [slopes[Int(n)] for n in N_slope]
log_Ns = log.(N_slope); log_ss = log.(s_slope)
# A \ b returns [intercept, slope_exponent]
fit_coeffs = [ones(length(log_Ns)) log_Ns] \ log_ss
log_a0_slope = fit_coeffs[1]   # = log(a0)
alpha_slope  = fit_coeffs[2]   # = slope exponent (nu)
println()
@printf("  Slope ~ N^%.4f (negative => transition weakens with N = crossover)\n", alpha_slope)
@printf("  Prefactor a0 = %.4f\n", exp(log_a0_slope))
@printf("  If alpha > 0: true sharp transition (diverging slope)\n")
@printf("  If alpha < 0: crossover/smooth transition\n")

# ─────────────────────────────────────────────────────────
# 5. Data collapse: find optimal gamma
# ─────────────────────────────────────────────────────────

println("\n=== Data collapse optimization ===")
# For each gamma, collapse the curves by plotting kappa vs (eta - eta_c(N)) * N^gamma
# Measure quality by interpolation variance at shared x-points

function collapse_quality(gamma, N_list, all_data, eta_c_interp)
    # Collect all (x_scaled, kappa) pairs near transition
    all_x = Float64[]; all_k = Float64[]
    for N in N_list
        pts = all_data[N]
        ec = eta_c_interp[N]
        for (k, eta, kappa) in pts
            x = (eta - ec) * N^gamma
            if abs(x) < 5.0  # focus on near-transition region
                push!(all_x, x); push!(all_k, kappa)
            end
        end
    end
    # Sort by x
    idx = sortperm(all_x)
    xs = all_x[idx]; ks = all_k[idx]
    # Measure quality: variance of kappa at nearby x-values across different N
    # Simple proxy: fit a polynomial and compute residuals
    if length(xs) < 6; return Inf; end
    A = hcat(xs, xs.^2, xs.^3)
    coeffs = A \ ks
    resid = ks .- A * coeffs
    return var(resid)
end

N_for_collapse = [N for N in N_sorted if N <= 500]  # exclude N=1000 (too few points near transition)
best_gamma_ref = Ref(0.5); best_q_ref = Ref(Inf)
for gamma in 0.1:0.02:1.2
    q = collapse_quality(gamma, N_for_collapse, all_data, eta_c_interp)
    if q < best_q_ref[]; best_q_ref[] = q; best_gamma_ref[] = gamma; end
end
best_gamma = best_gamma_ref[]; best_q = best_q_ref[]
@printf("  Optimal collapse gamma = %.3f (variance proxy = %.6f)\n", best_gamma, best_q)
@printf("  (gamma = 1/nu where nu is the correlation length exponent)\n")

# Test collapse at gamma=0.5 (mean-field) vs best
q05 = collapse_quality(0.5, N_for_collapse, all_data, eta_c_interp)
@printf("  gamma=0.5 (CLT/mean-field): variance = %.6f\n", q05)
@printf("  gamma=%.2f (optimal):       variance = %.6f\n", best_gamma, best_q)

# ─────────────────────────────────────────────────────────
# 6. Clustering coefficient at eta_c
# ─────────────────────────────────────────────────────────

println("\n=== Clustering coefficient at eta_c (k-regular graphs) ===")
println("  For random k-regular graphs: E[C] ≈ (k-1)/(N-2) * (k-2)/(N-3) ≈ (k-1)²/N² for large N")
println("  At the transition eta_c(N) = (k_c)²/N, so k_c = sqrt(eta_c * N)")
for N in N_sorted
    ec = eta_c_interp[N]
    k_c = sqrt(ec * N)
    C_expected = (k_c - 1)^2 / (N - 2)  # leading approximation
    n_triangles_per_edge = k_c * (k_c - 1) / (N - 1)  # expected common neighbors
    @printf("  N=%4d: k_c=%.1f, E[C]≈%.4f, triangles/edge=%.3f\n",
            N, k_c, C_expected, n_triangles_per_edge)
end
println("  Key: E[C]→0 as N→∞, but triangles/edge → k_c*(k_c-1)/(N-1) → sqrt(eta_c)*O(1/sqrt(N))")
println("  The transition occurs when triangles/edge ≈ constant times 1/sqrt(N) → vanishes!")
println("  Resolution: curvature depends on ABSOLUTE number of triangles seen by OT, not just clustering")

# ─────────────────────────────────────────────────────────
# 7. Summary table for J. Stat. Phys.
# ─────────────────────────────────────────────────────────

println("\n" * "="^60)
println("SUMMARY FOR J. STAT. PHYS.")
println("="^60)
@printf("Fixed-beta fit:   eta_c(N) = %.3f - %.3f/sqrt(N),  R²=%.4f\n",
        eta_inf_fixed, a_fixed, R2_fixed)
@printf("Free-beta fit:    eta_c(N) = %.3f - %.3f/N^%.3f, R²=%.4f\n",
        eta_inf_free, a_free, beta_free, R2_free)
@printf("Beta 95%% CI:      [%.3f, %.3f]\n", ci_low, ci_high)
@printf("Slope exponent:   d(kappa)/d(eta)|_ec ~ N^%.3f\n", alpha_slope)
@printf("Optimal collapse: gamma = %.2f\n", best_gamma)
println()
println("Interpretation:")
if ci_low <= 0.5 <= ci_high
    println("  - beta=0.5 (CLT/mean-field) is WITHIN 95% CI: consistent with CLT scaling")
else
    println("  - beta=0.5 is OUTSIDE 95% CI: evidence for non-mean-field scaling")
end
if alpha_slope < -0.05
    println("  - Slope at eta_c DECREASES with N => crossover, not sharp phase transition")
elseif alpha_slope > 0.05
    println("  - Slope at eta_c INCREASES with N => consistent with true phase transition")
else
    println("  - Slope at eta_c approximately constant => inconclusive")
end

# ─────────────────────────────────────────────────────────
# 8. Dimensional phase boundary (hypercomplex embedding)
# ─────────────────────────────────────────────────────────

println("\n" * "="^60)
println("DIMENSIONAL PHASE BOUNDARY (hypercomplex embedding)")
println("="^60)

function interpolate_eta_c_from_dict(results)
    for i in 2:length(results)
        prev, curr = results[i-1], results[i]
        κ_prev = prev["kappa_mean"]
        κ_curr = curr["kappa_mean"]
        (isnothing(κ_prev) || isnothing(κ_curr)) && continue
        if κ_prev < 0 && κ_curr >= 0
            η_prev, η_curr = prev["eta"], curr["eta"]
            frac = abs(κ_prev) / (abs(κ_prev) + abs(κ_curr))
            return η_prev + frac * (η_curr - η_prev)
        end
    end
    return NaN
end

# Hop-count reference (from multi-N JSON)
hop_ref = Dict(50 => 1.73, 100 => 2.22, 200 => 2.71)

# Embedding label map
emb_label = Dict(4 => "Q4 (S³)", 8 => "Oct (S⁷)")

println("\n  N     d    Embedding     η_c(d)    η_c(hop)  ratio")
println("  " * "-"^55)

for N in [50, 100, 200], d in [4, 8]
    fname = joinpath(dirname(@__FILE__), "../../results/experiments",
                     "hypercomplex_lp_n$(N)_d$(d).json")
    if !isfile(fname)
        @printf("  %-4d  %-4d %-13s  (missing — run hypercomplex_lp.jl --full)\n",
                N, d, emb_label[d])
        continue
    end
    data = JSON.parsefile(fname)
    η_c_d = interpolate_eta_c_from_dict(data["results"])
    η_c_hop = get(hop_ref, N, NaN)
    if isnan(η_c_d)
        @printf("  %-4d  %-4d %-13s  >%.2f     %.2f\n",
                N, d, emb_label[d], data["results"][end]["eta"], η_c_hop)
    else
        ratio = η_c_d / η_c_hop
        @printf("  %-4d  %-4d %-13s  %.3f     %.2f      %.3f\n",
                N, d, emb_label[d], η_c_d, η_c_hop, ratio)
    end
end

println()
println("Interpretation:")
println("  η_c(d) > η_c(hop): compact sphere geometry DELAYS sign change (higher η required)")
println("  η_c(d) = NaN/∞: no sign change observed — sphere eliminates negative ORC entirely")
