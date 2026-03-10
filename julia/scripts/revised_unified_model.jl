"""
Revised Three-Parameter Model: (η, C, G) for Cross-Domain Geometry Classification

Tests whether adding degree heterogeneity G = σ_k/⟨k⟩ to the two-parameter (η, C)
model fixes biological network mispredictions.

Data sources (all pre-computed, no new LP):
  results/unified/*_exact_lp.json  — 11 semantic training + 5 held-out
  results/experiments/bio_network_orc.json — 4 biological with exact LP

Output: results/experiments/revised_unified_model.json
"""

import Pkg
let deps = Pkg.project().dependencies
    for pkg in ["JSON", "Printf", "Statistics"]
        haskey(deps, pkg) || Pkg.add(pkg)
    end
end

using JSON, Printf, Statistics

const UNIFIED_DIR  = joinpath(@__DIR__, "..", "..", "results", "unified")
const RESULTS_DIR  = joinpath(@__DIR__, "..", "..", "results", "experiments")
const ETA_C_INF    = 3.75
const C_STAR_OLD   = 0.05   # original semantic-trained threshold

# ─── Geometry classifier (two-parameter) ─────────────────────────────────────

function classify_2param(η, C; eta_c=ETA_C_INF, c_star=C_STAR_OLD)
    η > eta_c && return "Spherical"
    C > c_star && return "Hyperbolic"
    return "Euclidean"
end

function classify_3param(η, C, G; eta_c=ETA_C_INF, c_star=C_STAR_OLD, c_star_bio=0.22)
    η > eta_c && return "Spherical"
    # High G (star-hub) + any C → elevated κ̄ → use biological threshold
    c_eff = G > 0.5 ? c_star_bio : c_star
    C > c_eff && return "Hyperbolic"
    return "Euclidean"
end

function actual_class(kappa_mean)
    kappa_mean > 0.03  && return "Spherical"
    kappa_mean < -0.03 && return "Hyperbolic"
    return "Euclidean"
end

# ─── Load semantic networks ───────────────────────────────────────────────────

training_ids = ["swow_es", "swow_en", "swow_zh", "swow_nl",
                "conceptnet_en", "conceptnet_pt",
                "wordnet_en", "babelnet_ar", "babelnet_ru", "depression_minimum"]

heldout_ids  = ["swow_rp", "eat_en", "usf_en", "wordnet_de", "framenet_en"]

networks = []

for nid in vcat(training_ids, heldout_ids)
    # Find the file
    candidates = filter(f -> startswith(f, nid) && endswith(f, "_exact_lp.json"),
                        readdir(UNIFIED_DIR))
    isempty(candidates) && (println("  SKIP $nid (no JSON)"); continue)
    d = JSON.parsefile(joinpath(UNIFIED_DIR, candidates[1]))
    η  = get(d, "eta",        NaN)
    C  = get(d, "clustering", NaN)
    κ̄  = get(d, "kappa_mean", NaN)
    mean_k = get(d, "mean_degree",  NaN)
    deg_std = get(d, "degree_std",  NaN)
    G  = (!isnan(mean_k) && mean_k > 0) ? deg_std / mean_k : NaN
    split = (nid in training_ids) ? "train" : "heldout"
    push!(networks, (id=nid, label=get(d,"network_id",nid), split=split, domain="semantic",
                     η=η, C=C, G=G, κ̄=κ̄,
                     actual=actual_class(κ̄)))
end

# ─── Load biological networks ─────────────────────────────────────────────────

bio_data = JSON.parsefile(joinpath(RESULTS_DIR, "bio_network_orc.json"))
bio_G_table = Dict(
    "celegans_neural"   => (N=115, mean_k=12.19, deg_std=6.87),   # from bio_network_orc metadata
    "ecoli_grn"         => (N=127, mean_k=2.90,  deg_std=2.617),
    "ecoli_ppi"         => (N=97,  mean_k=39.94, deg_std=2.14),
    "celegans_metabolic"=> (N=214, mean_k=9.36,  deg_std=5.31),
)

for r in bio_data["results"]
    isnothing(r["kappa_mean"]) && continue   # yeast PPI (LP skipped)
    nid = r["network_id"]
    η   = r["eta"]
    C   = r["C"]
    κ̄   = r["kappa_mean"]
    # Compute G from stored metadata if available
    G = if haskey(bio_G_table, nid)
        bio_G_table[nid].deg_std / bio_G_table[nid].mean_k
    else
        NaN
    end
    push!(networks, (id=nid, label=r["label"], split="bio_test", domain="biological",
                     η=η, C=C, G=G, κ̄=κ̄,
                     actual=actual_class(κ̄)))
end

# ─── Evaluate models ──────────────────────────────────────────────────────────

println("=== Feature Matrix & Classification Results ===\n")
@printf("%-22s %-8s %-7s %-6s %-6s %-10s %-10s %-10s %-8s\n",
    "Network", "Split", "η", "C", "G", "κ̄", "2-param", "3-param", "Actual")
println("─"^95)

results_table = []
for n in networks
    p2 = classify_2param(n.η, n.C)
    p3 = classify_3param(n.η, n.C, isnan(n.G) ? 0.0 : n.G)
    ok2 = (p2 == n.actual) ? "✓" : "✗"
    ok3 = (p3 == n.actual) ? "✓" : "✗"
    G_str = isnan(n.G) ? "?" : @sprintf("%.2f", n.G)
    @printf("%-22s %-8s %-7.4f %-6.3f %-6s %-10.4f %-10s %-10s %-8s\n",
        n.id[1:min(21,end)], n.split, n.η, n.C, G_str, n.κ̄, "$(p2)$(ok2)", "$(p3)$(ok3)", n.actual)
    push!(results_table, Dict(
        "network_id"=>n.id, "label"=>n.label, "split"=>n.split, "domain"=>n.domain,
        "eta"=>n.η, "C"=>n.C, "G"=>isnan(n.G) ? nothing : n.G, "kappa_mean"=>n.κ̄,
        "actual"=>n.actual, "pred_2param"=>p2, "pred_3param"=>p3,
        "correct_2param"=>(p2==n.actual), "correct_3param"=>(p3==n.actual)
    ))
end

# ─── Accuracy by split ────────────────────────────────────────────────────────

println("\n=== Accuracy by split ===")
for split in ["train", "heldout", "bio_test"]
    grp = filter(r -> r["split"] == split, results_table)
    isempty(grp) && continue
    acc2 = mean(r["correct_2param"] for r in grp)
    acc3 = mean(r["correct_3param"] for r in grp)
    @printf("  %-10s: 2-param = %d/%d (%.0f%%)   3-param = %d/%d (%.0f%%)\n",
        split,
        sum(r["correct_2param"] for r in grp), length(grp), 100*acc2,
        sum(r["correct_3param"] for r in grp), length(grp), 100*acc3)
end

# ─── Optimal C* search ────────────────────────────────────────────────────────

println("\n=== Optimal C* for all networks (η-boundary fixed) ===")
all_C = [n.C for n in networks]
all_actual = [n.actual for n in networks]
all_eta = [n.η for n in networks]
best_acc = Ref(0.0); best_cstar = Ref(0.0)
for c_star in 0.01:0.01:0.90
    preds = [classify_2param(all_eta[i], all_C[i]; c_star=c_star) for i in 1:length(all_C)]
    acc = mean(preds .== all_actual)
    if acc > best_acc[]
        best_acc[] = acc; best_cstar[] = c_star
    end
end
best_acc_val = best_acc[]
best_cstar_val = best_cstar[]
@printf("  Best C* = %.2f → accuracy = %.0f%% (n=%d)\n",
    best_cstar_val, 100*best_acc_val, length(networks))

# ─── Save ─────────────────────────────────────────────────────────────────────

output = Dict(
    "experiment"        => "revised_unified_model",
    "description"       => "Two-param vs three-param model cross-domain evaluation",
    "C_star_old"        => C_STAR_OLD,
    "C_star_bio"        => 0.22,
    "C_star_optimal"    => best_cstar_val,
    "C_star_optimal_acc"=> best_acc_val,
    "n_networks"        => length(results_table),
    "networks"          => results_table,
    "accuracy_by_split" => Dict(
        split => Dict(
            "n"          => count(r["split"]==split for r in results_table),
            "acc_2param" => mean(r["correct_2param"] for r in results_table if r["split"]==split),
            "acc_3param" => mean(r["correct_3param"] for r in results_table if r["split"]==split),
        ) for split in ["train","heldout","bio_test"]
          if any(r["split"]==split for r in results_table)
    )
)

open(joinpath(RESULTS_DIR, "revised_unified_model.json"), "w") do f
    JSON.print(f, output, 2)
end
println("\nSaved revised_unified_model.json")
