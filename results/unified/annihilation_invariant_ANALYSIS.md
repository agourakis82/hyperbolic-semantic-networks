# Phase A — Sedenion ZD Annihilation Invariant: Honest Negative

**Date:** 2026-05-26  
**Script:** `code/analysis/annihilation_invariant.py`  
**Method:** Path B discretization — assign each node to nearest of 84 algebraic ZD primitive
vectors (cosine similarity), count edges whose endpoint-label pair is one of the 168 sedenion
ZD pairs, compare to (a) permutation null and (b) random codebook (kill-test 1).  
**Kill-test 2:** 16D features curvature-free (no κ, no κ-gradient). ✓ by construction.  
**Kill-test 3:** ||F||² ordering matches ZD-fraction ordering (minimum>moderate>severe>mild) —
but the signal itself is degenerate (see below).  

## Results — Semantic substrate

| group    | ZD-edge frac | (zd/total)  | perm-null z | rand-codebook z | verdict       |
|----------|-------------|-------------|-------------|-----------------|---------------|
| minimum  | 0.0029      | 33/11354    | −0.56       | 0.00            | null          |
| mild     | 0.0000      | 0/39840     | 0.00        | 0.00            | null          |
| moderate | 0.0001      | 2/24109     | −0.09       | 0.00            | null          |
| severe   | 0.0000      | 0/32168     | 0.00        | 0.00            | null          |

Kill-test 1: algebraic z ≈ random codebook z in all groups → no algebraic advantage.  
Kill-test 3: ||F||² rank = ZD-fraction rank → signal is norm-dominated (moot given fractions ≈ 0).

## Results — ABIDE-I substrate

cross-group ZD fraction (first 50×50 ASD×TD pairs): 0.0100; permutation null z=−1.27
(below null expectation); random codebook: 0.0000. No algebraic signal.

## Root cause

The mapping `graph-node-features → 16D → nearest ZD vertex` breaks the algebraic structure
that gives ZD pairs their meaning. Three compounding reasons:

1. **Feature clustering.** The 16D feature vector (log_degree, clustering, pagerank, …) lives in
   the positive orthant [0,1]^16. Its direction is determined by whichever 2–3 features dominate.
   Across nodes in the same large graph, the dominant features are similar (hub nodes dominate
   all structural measures). This concentrates most nodes into 1–4 of the 84 ZD vertices.

2. **ZD pairs are algebraically sparse.** 168 ZD pairs out of C(84,2)=3486 possible pairs ≈ 4.8%.
   When most nodes land on the same 1–4 vertices, almost all edges are within-cluster
   (same-vertex label), which is explicitly NOT a ZD pair (no non-zero sedenion is a ZD
   with itself). ZD pairs require DIFFERENT vertices with a specific algebraic relationship.

3. **Algebraic ≠ geometric.** ZD pairs are defined by `a·b=0` in the sedenion product. This is
   a condition on the algebraic representation, NOT on the geometric distance between vertices.
   The 84 ZD vertices that are nearest-neighbor to the feature vectors are not necessarily
   ZD-paired with each other — cosine similarity selects vertices by direction, not by
   annihilation relationship.

## Verdict

**NULL RESULT.** The sedenion ZD-discretization approach does not carry group structure on
either depression severity networks or the ABIDE-I connectome. This is a structural failure of
the approach — the mapping from arbitrary graph statistics to sedenion space cannot preserve
the algebraic annihilation relationship that makes ZD pairs meaningful.

This is the same class of result as the **octonion associator rejection** (2026-05-26):
both attempts imported non-associative algebra structure into a graph-feature embedding that
lacked algebraic grounding. The octonion associator re-encoded curvature; the ZD
discretization produces near-zero edge counts irrespective of group.

## What would be needed for a valid test

A valid sedenion annihilation test requires that the 16D embedding of each node be
**algebraically motivated** — e.g., arising from a natural sedenion product over the graph
(such as path products, edge-weight tensor structure, or connection to a representation
where sedenion algebra is the natural symmetry group). Assigning arbitrary structural
statistics to sedenion basis coordinates and then checking ZD compatibility is category error:
the assignment doesn't commute with the product.

**This result closes the Phase A sedenion annihilation program on these two datasets.** The
honest negative is retained as the documented negative control, parallel to the octonion
associator result.

## ONE ROBUST AXIS (unchanged)

**Ollivier-Ricci curvature** remains the single validated geometric axis: subclinical
(minimum) most hyperbolic, robust to exact-OT, degree-nulls, density matching, and a 6-cell
(N,⟨k⟩) sweep with per-edge KS separation. No second axis has been established.
