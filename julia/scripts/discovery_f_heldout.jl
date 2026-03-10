"""
Discovery F — Held-Out Test Set Generalization

Loads the 5 held-out semantic networks (SWOW-RP, EAT, USF, WordNet-DE, FrameNet),
applies the two-parameter model (η, C) fitted on the 11-network training set,
and computes test-set R², MAE, and phase classification accuracy.

Output: results/experiments/heldout_generalization.json
"""

using Pkg
Pkg.activate(joinpath(@__DIR__, ".."))

using JSON, Statistics, Printf, LinearAlgebra

const UNIFIED_DIR  = joinpath(@__DIR__, "..", "..", "results", "unified")
const RESULTS_DIR  = joinpath(@__DIR__, "..", "..", "results", "experiments")

# ─── Training set (11 networks) — from paper Table 1 ─────────────────────────

training = [
    (id="swow_es",          η=0.017, C=0.136, κ=-0.068,  geom="Hyperbolic"),
    (id="swow_en",          η=0.020, C=0.128, κ=-0.137,  geom="Hyperbolic"),
    (id="swow_zh",          η=0.023, C=0.173, κ=-0.144,  geom="Hyperbolic"),
    (id="swow_nl",          η=7.558, C=0.238, κ=+0.099,  geom="Spherical"),
    (id="conceptnet_en",    η=0.223, C=0.108, κ=-0.233,  geom="Hyperbolic"),
    (id="conceptnet_pt",    η=0.085, C=0.106, κ=-0.236,  geom="Hyperbolic"),
    (id="wordnet_en",       η=0.009, C=0.013, κ=-0.002,  geom="Euclidean"),
    (id="wordnet_en_2k",    η=0.002, C=0.002, κ=-0.005,  geom="Euclidean"),
    (id="babelnet_ru",      η=0.009, C=0.001, κ=-0.030,  geom="Euclidean"),
    (id="babelnet_ar",      η=0.032, C=0.000, κ=-0.012,  geom="Euclidean"),
    (id="depression_min",   η=0.118, C=0.159, κ=-0.130,  geom="Hyperbolic"),
]

# ─── Test set (5 held-out networks) — from paper Table 1 ─────────────────────

test_nets = [
    (id="swow_rp",    label="SWOW Rioplatense", η=0.040, C=0.154, κ=-0.264, geom="Hyperbolic"),
    (id="eat_en",     label="EAT",              η=1.851, C=0.143, κ=-0.046, geom="Hyperbolic"),
    (id="usf_en",     label="USF",              η=0.062, C=0.143, κ=-0.321, geom="Hyperbolic"),
    (id="wordnet_de", label="WordNet DE",       η=0.006, C=0.022, κ=-0.023, geom="Euclidean"),
    (id="framenet",   label="FrameNet",         η=0.009, C=0.045, κ=-0.202, geom="Hyperbolic"),
]

# ─── Two-parameter model prediction ──────────────────────────────────────────

C_STAR   = 0.05
ETA_C_INF = 3.75

function predict(η, C)::String
    η > ETA_C_INF && return "Spherical"
    C >= C_STAR   && return "Hyperbolic"
    return "Euclidean"
end

# ─── Fit linear model κ = a + b·log(η) + c·C on training set ─────────────────
# (for continuous R² metric, not just classification)

function linfit_3(X::Matrix{Float64}, y::Vector{Float64})
    # OLS: y = Xβ, X = [1 | log_η | C]
    β = (X'X) \ (X'y)
    ŷ = X * β
    ss_res = sum((y .- ŷ).^2)
    r2 = 1.0 - ss_res / sum((y .- mean(y)).^2)
    return β, r2, ŷ
end

# Training predictors
X_train = hcat(ones(length(training)),
               [log(max(t.η, 1e-6)) for t in training],
               [t.C for t in training])
y_train = [t.κ for t in training]
β, r2_train, ŷ_train = linfit_3(X_train, y_train)

println("=== Training set fit ===")
@printf("β = [%.4f, %.4f, %.4f] (intercept, log_η coef, C coef)\n", β...)
@printf("Training R² = %.4f\n", r2_train)

# ─── Apply to test set ────────────────────────────────────────────────────────

println("\n=== Test set predictions ===")
println("Network         | η      | C     | κ̄(obs)  | κ̄(pred) | pred_geom | true_geom | ✓?")
println("----------------|--------|-------|---------|---------|-----------|-----------|---")

test_results = []
κ_obs  = Float64[]
κ_pred = Float64[]
n_correct = Ref(0)

for t in test_nets
    x = [1.0, log(max(t.η, 1e-6)), t.C]
    κ_p = dot(β, x)
    pred_geom = predict(t.η, t.C)
    correct = pred_geom == t.geom
    n_correct[] += correct ? 1 : 0
    push!(κ_obs, t.κ)
    push!(κ_pred, κ_p)

    @printf("%-16s | %.4f | %.3f | %+.4f | %+.4f | %-9s | %-9s | %s\n",
        t.label, t.η, t.C, t.κ, κ_p,
        pred_geom, t.geom, correct ? "✓" : "✗")

    push!(test_results, Dict(
        "network_id" => t.id, "label" => t.label,
        "eta" => t.η, "C" => t.C,
        "kappa_obs" => t.κ, "kappa_pred" => κ_p,
        "pred_geometry" => pred_geom, "true_geometry" => t.geom,
        "correct" => correct
    ))
end

# Test-set R² and MAE
ȳ_test = mean(κ_obs)
r2_test = 1.0 - sum((κ_obs .- κ_pred).^2) / sum((κ_obs .- ȳ_test).^2)
mae     = mean(abs.(κ_obs .- κ_pred))
rmse    = sqrt(mean((κ_obs .- κ_pred).^2))

println("\n=== Test set generalization metrics ===")
@printf("Classification accuracy: %d/5\n", n_correct[])
@printf("R² (continuous κ̄):       %.4f\n", r2_test)
@printf("MAE:                     %.4f\n", mae)
@printf("RMSE:                    %.4f\n", rmse)
println("\nNote: FrameNet (C=0.045 ≈ C*=0.05) is the borderline case;")
println("      at C*→0.04 all 5/5 would be correctly classified.")

# ─── Save ─────────────────────────────────────────────────────────────────────

output = Dict(
    "experiment"       => "heldout_generalization",
    "description"      => "Two-parameter model (η,C) generalization to 5 held-out test networks",
    "model"            => Dict("C_star"=>C_STAR, "eta_c_inf"=>ETA_C_INF,
                               "linear_coefs"=>β, "r2_train"=>r2_train),
    "test_classification_accuracy" => "$(n_correct[])/5",
    "test_r2"          => r2_test,
    "test_mae"         => mae,
    "test_rmse"        => rmse,
    "test_results"     => test_results
)

open(joinpath(RESULTS_DIR, "heldout_generalization.json"), "w") do f
    JSON.print(f, output, 2)
end
println("\nSaved heldout_generalization.json")
