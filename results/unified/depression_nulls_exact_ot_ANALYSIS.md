# Depression ORC — Exact-OT + Degree-Preserving Null Models

**Date:** 2026-05-26
**Pipeline:** `code/analysis/depression_nulls_exact_ot.py`
**Method:** exact Wasserstein-1 (POT network simplex, no Sinkhorn bias), lazy random walk α=0.5,
largest connected component, Maslov-Sneppen degree-preserving rewiring (10·E swaps), 5 nulls/group.
**Validation:** all four `kappa_real` reproduce `results/unified/depression_*_exact_lp.json`
(Julia/HiGHS) **bit-exact**; `minimum` z reproduces the existing `config_model_nulls.json` (z≈403 with
its own RNG; 267 here under a different seed/null draw — same order of magnitude, same verdict).

## Results

| group    |    N |     E | ⟨k⟩  | κ_real  | κ_null  | Δκ      |     z |
|----------|-----:|------:|-----:|--------:|--------:|--------:|------:|
| minimum  | 1634 | 11354 | 13.9 | −0.1303 | −0.2642 | +0.1339 | 266.8 |
| mild     | 3089 | 39840 | 25.8 | −0.0742 | −0.1004 | +0.0262 |  55.3 |
| moderate | 2238 | 24109 | 21.5 | −0.0871 | −0.1281 | +0.0410 | 194.8 |
| severe   | 2685 | 32168 | 24.0 | −0.0783 | −0.1082 | +0.0299 | 196.1 |

## Verdict (three findings)

1. **Hyperbolicity is real, not a regularization artifact.** Exact OT reproduces the negative κ
   exactly; the earlier Sinkhorn values were not the issue. Under exact OT the ordering is
   `minimum < moderate < severe < mild` — **mild is the least hyperbolic, not moderate**. The
   "moderate is the collapse peak" claim was a Sinkhorn artifact and does not survive.

2. **The severity contrast is largely a DENSITY confound.** `corr(κ_real, ⟨k⟩) = +0.991`.
   The raw curvature ordering across severity is almost entirely explained by mean degree —
   denser groups are less hyperbolic. The depression groups differ in N and edge density, so the
   κ ordering **cannot be attributed to semantic reorganization** without density-matching.

3. **Semantic wiring REDUCES hyperbolicity vs the degree backbone.** All four Δκ > 0 (z = 55–267):
   the degree-preserving null is *more* hyperbolic than the real network in every group. The
   heavy-tailed degree sequence alone produces the tree-like structure; actual semantic edges add
   clustering/triangulation on top. So hyperbolicity here is inherited from degree, not built by
   meaning.

## The one genuine hint

`minimum`'s Δκ (+0.134) is **2.0×** the value extrapolated from the clinical-group Δκ~⟨k⟩ trend
(+0.067). After removing the density trend, the subclinical group still shows excess
de-hyperbolization — a weak signal (n=3 extrapolation) that subclinical semantic structure departs
from degree expectation more than clinical structure does. **This is the only severity effect that
might survive density control, and it is the thing to test next.**

## Density-matched verdict (DONE 2026-05-26) — the effect SURVIVES

`code/analysis/depression_density_matched_orc.py`: all four groups subsampled to common
N≈1500, ⟨k⟩≈10.1, 20 reps each, exact-OT κ. Results in `depression_density_matched_orc.json`.

| group (severity) | matched κ | ±std | CI95 |
|------------------|----------:|-----:|------|
| minimum (sub)    | **−0.1776** | 0.0032 | [−0.1791, −0.1762] |
| moderate         | −0.1672 | 0.0037 | [−0.1689, −0.1656] |
| severe           | −0.1560 | 0.0049 | [−0.1582, −0.1539] |
| mild             | −0.1453 | 0.0064 | [−0.1481, −0.1425] |

**All 6 pairwise CIs separated** (min gap +0.0058, severe vs mild). The density confound shifts
every value more negative (sparser ⇒ more hyperbolic) but **preserves the rank order exactly**:
raw order `minimum > moderate > severe > mild` = matched order. So although `corr(κ_raw,⟨k⟩)=0.991`,
the curvature rank is **robust to density control** — it is not a pure density artifact.

**Headline that survives:** `minimum` (subclinical) is the most hyperbolic group at matched density,
well-separated from all clinical groups. The non-monotonicity (subclinical most hyperbolic; mild,
the mildest clinical group, *least*) is a genuine residual structural effect, not a confound.

Caveats still open: (a) ⟨k⟩=10 is one operating point — sweep it; (b) groups differ in source N
(sampling-stability not corpus-size matched); (c) per-subsample nulls not yet run (the cross-group
separation is what carries the claim now, not vs-null significance).
