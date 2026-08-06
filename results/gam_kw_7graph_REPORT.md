# GAM + Kruskal–Wallis re-run on the 7-graph set (ConceptNet removed, Dutch added)

**Set (n=7):** 4 SWOW (ES/EN/ZH/NL) + 3 taxonomy (WordNet EN, BabelNet RU/AR). Weighted clustering C and weighted GRC κ̄ (α=0.5), matching Table-1. Data: `results/phase_diagram_metrics_7graph.csv`.

| network | category | family | C (weighted) | σ_k | κ̄ |
|---|---|---|---|---|---|
| BabelNet (AR) | Taxonomy | Semitic | 0.0000 | 2.61 | −0.012 |
| BabelNet (RU) | Taxonomy | Indo-European | 0.0003 | 2.73 | −0.030 |
| SWOW (EN) | Association | Indo-European | 0.0263 | 1.84 | −0.258 |
| SWOW (ZH) | Association | Sino-Tibetan | 0.0290 | 2.03 | −0.214 |
| SWOW (ES) | Association | Indo-European | 0.0338 | 1.74 | −0.155 |
| SWOW (NL) | Association | Indo-European | 0.0373 | 2.62 | −0.270 |
| WordNet (EN) | Taxonomy | Indo-European | 0.0456 | 4.07 | −0.002 |

## Kruskal–Wallis
- **By language family** (the manuscript's test): **H = 1.11, p = 0.57 → no significant family effect.** Conclusion matches the manuscript; the exact H differs (manuscript 1.83) because this network-level KW on group sizes 5/1/1 is very low-power and fragile (the 8-graph version gives H=2.08, not 1.83 — not exactly reproducible).
- **By category (Association vs Taxonomy)** — the structurally meaningful contrast: **H = 4.50, p = 0.034 → SIGNIFICANT.** Association networks are significantly more hyperbolic than taxonomies. This is the robust statistical claim; recommend leading with it.

## GAM  κ̄ ~ s(C)
- Explained deviance = **0.795 only at the gridsearch best λ=0.026 (near-interpolation of 7 points = overfitting)**; with meaningful smoothing (λ ∈ [0.1, 30]) it falls to **0.18–0.68**.
- Fitted κ̄ minimum at **C ≈ 0.024**; descriptive "sweet spot" (fitted κ̄ < −0.05) **C ∈ [0.002, 0.046]**.
- The manuscript's **R²=0.78 + sweet spot [0.023, 0.147]** does NOT robustly reproduce: the 0.78 is an N=7 overfitting artifact, and the upper bound 0.147 is unsupported (no network has weighted C > 0.046). Removing ConceptNet (which sat at C=0.014–0.017 and filled the valley's lower wall) is the main cause of the weakened fit.

## σ_k as secondary moderator — DROP
The manuscript's σ_k interaction (p=0.004) was driven by ConceptNet (σ_k 5.6–7.3). In the 7-graph set the 4 SWOW have σ_k 1.7–2.6 while taxonomies are **higher** (2.6–4.1), so "elevated σ_k drives hyperbolicity" reverses direction. An interaction test at N=7 is not defensible. **Recommend dropping the σ_k-moderator claim**, not re-fitting it.

## Recommended manuscript reframing (§3.2)
1. Lead with the **categorical** result: Association vs Taxonomy, KW H=4.50, p=0.034.
2. Keep the family-effect null (H=1.11, p=0.57).
3. Replace the GAM "R²=0.78, sweet spot [0.023,0.147]" with an honest descriptive statement: SWOW networks occupy a narrow weighted-clustering band (C≈0.026–0.037) where κ̄ is strongly negative, bounded by near-Euclidean taxonomies at both very low (C≈0) and higher (C≈0.046) clustering — a valley pattern; a formal GAM smooth is under-powered at n=7.
4. Drop the σ_k secondary-moderator claim.
