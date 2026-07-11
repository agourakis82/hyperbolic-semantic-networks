# Geometric Critical Slowing Down

### Ollivier–Ricci curvature as a confidence-typed early-warning signal for critical transitions in mood

**Status:** research proposal + synthetic methods pilot. Honest about the data wall (no longitudinal
mood data on disk). **Date:** 2026-05-26.

---

## 1. The one-sentence bet

A depressive transition is a **"crash" in the momentary-affect network**, and **Ollivier–Ricci
curvature is its fragility hallmark** — a network-geometric early-warning signal that should drop
*ahead of* a transition, carrying more (and more localizable) information than the scalar
autocorrelation/variance statistics the field currently uses — *if and only if* each curvature
estimate is reported with its propagated uncertainty so the warning fires only when statistically
warranted.

## 2. Two mature literatures that have never been joined

**Literature A — Ricci curvature as a fragility / systemic-risk early-warning signal.**
The result that "negative Ollivier–Ricci curvature = network fragility, positive = robustness" is
established and *predictive of crashes* in non-trivial dynamical systems:

- **Finance:** Sandhu, Georgiou & Tannenbaum, *Ricci curvature: an economic indicator for market
  fragility and systemic risk*, **Science Advances 2016** — financial crashes are "invariably
  preceded by system-level changes in robustness"; Ricci curvature is a *crash hallmark*.
  ([science.org](https://www.science.org/doi/10.1126/sciadv.1501495)). Replicated/extended for
  equity markets in [arXiv:2405.07134](https://arxiv.org/html/2405.07134v1).
- **Cancer / omics:** Ricci curvature as a robustness proxy that distinguishes cancer networks
  (Sci Rep 2015; ORCO, *Bioinformatics* 2025
  [PMC11893153](https://pmc.ncbi.nlm.nih.gov/articles/PMC11893153/)).
- **Brain (static):** curvature as a hallmark of structural connectivity (Nat Commun 2019
  [s41467-019-12915-x](https://www.nature.com/articles/s41467-019-12915-x)); discrete Ricci
  curvature captures age + ASD differences in *functional* connectivity (Frontiers Aging Neurosci
  2023 [PMC10244515](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10244515/)).

**Literature B — Critical Slowing Down (CSD) as the dominant temporal early-warning paradigm in
psychopathology.** On ecological-momentary-assessment (EMA/ESM) affect time series, *rising lag-1
autocorrelation and variance* in sliding windows precede depressive/manic transitions:

- van de Leemput et al., *Critical slowing down as early warning for the onset and termination of
  depression*, **PNAS 2014** ([pnas.org](https://www.pnas.org/doi/10.1073/pnas.1312114110)).
- Wichers et al., **Karger PPS 2016** (personalized EWS, medication-tapering single case);
  Smit et al., **Clin Psych Sci 2025** ([sage](https://journals.sagepub.com/doi/10.1177/21677026241305136)).
- Bipolar transitions: prospective EWS in EMA + actigraphy
  ([PMC9471093](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9471093/),
  [PMC8994809](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8994809/)).
- The field's own stated open problem: EWS are **noisy and prone to false alarms** — Scheffer,
  Bringmann et al., *Early warning signals and critical transitions in psychopathology: challenges
  and recommendations* (Curr Opin Psychol 2021
  [S2352250X21000257](https://www.sciencedirect.com/science/article/pii/S2352250X21000257)).

**The gap:** Literature B uses only **scalar** statistics (autocorrelation, SD) on the affect time
series. **Nobody computes the Ricci curvature of the dynamic affect network as the early-warning
signal.** Literature A says curvature *is* the fragility EWS in every other domain. Joining them is
the novel move.

## 3. This is theory, not analogy

The bridge is forced by bifurcation theory, not borrowed by metaphor:

- As a system approaches a local bifurcation (the formal model of a "tipping point"),
  **critical slowing down AND flattening of the potential landscape co-occur**; the dominant
  eigenvalue of the linearized dynamics → 0, the return rate vanishes, and the **curvature of the
  large-deviation rate function vanishes proportionally to the spectral gap**
  (Kuehn, *A mathematical framework for critical transitions*, Physica D 2011
  [arXiv:1101.2899](https://arxiv.org/abs/1101.2899); eigenvalue-EWS
  [PMC6385210](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6385210/)).
- Most directly: recent work casts EWS in **transport-geometric / operator-theoretic** foundations
  (2024 preprint, *Early Warning Signals … Transport-Geometric Foundations*). Ollivier–Ricci
  curvature is *defined* through optimal transport (W₁ between neighbour measures). So OT-geometric
  EWS theory and LLY-ORC are **closely related** through their shared optimal-transport scaffolding.

So: flattening of the potential ⇒ loss of restoring curvature ⇒ the interaction network's
Ollivier–Ricci curvature should change as the transition is approached. This is the testable
prediction.

> **DIRECTION CAVEAT (added 2026-05-27 after math-review).** Two *different* curvature directions
> are in play and must not be conflated. (i) **Bifurcation theory** predicts the *potential/rate-
> function* curvature **flattens toward 0** at a tipping point (CD(K,∞) spectral gap → 0). (ii) The
> **depression empirics** (§4) and the implemented Stage-4 sweep follow the *network Ollivier–Ricci*
> direction, where a more fragile state is **more negative κ (away from 0)**. These are not the same
> curvature and need not move together — the link between them is the heuristic flagged as
> OVERREACH (b)/(c) in the addendum, not an identity. The implemented artifacts test the empirical
> fragility direction (certified departure of κ from a healthy baseline), **not** the
> bifurcation-flattening direction.

## 4. Internal consistency with what we already proved

Our own validated, density-controlled finding: **subclinical (minimum) depression is the most
hyperbolic (most negative κ)** semantic group, robust across exact-OT, degree-nulls,
density-matching, and a 6-cell (N,⟨k⟩) sweep (`results/unified/depression_nulls_exact_ot_ANALYSIS.md`).
Read through the fragility lens, *more-negative κ = more fragile network* — directionally consistent
with "approaching a fragile/critical configuration." The static group difference is the
**time-average** of the dynamic excursions this proposal predicts.

## 5. The hypothesis we are betting on (state, not trait)

Two distinct hypotheses; we commit to the **state** reading (the Sandhu crash precedent supports it):

- **(rejected framing) Trait:** subclinical individuals merely have a more-negative *baseline* κ.
- **★ State (our bet):** *within an individual*, κ(t) of the momentary-affect network **drops along
  the trajectory toward a depressive transition**, co-timed with or *ahead of* the classical
  autocorrelation/variance EWS. The group-level static difference is the integral of these
  excursions.

The pilot is designed for the state hypothesis: a control-parameter sweep / within-trajectory
window analysis, not a between-group contrast.

## 6. Why Sounio is the right instrument (the differentiator must do real work)

The field's #1 complaint is EWS unreliability (§2, Bringmann 2021). EMA affect networks are
**tiny** (6–20 mood items) and windows are short, so per-window κ has large sampling variance — the
*same* pathology that makes scalar CSD noisy. A curvature number with no error bar inherits exactly
this problem. Sounio's epistemic/GUM machinery is built for this, and the LLY-ORC + GPU
`sinkhorn16` bridge (37× speedup, validated this program) makes time-resolved curvature feasible.
Concretely, the pipeline is three typed lines:

```
// κ(t) carries confidence propagated end-to-end, not a bare float.
let marginals_t : Knowledge<Measure> = empirical_neighbour_measures(window_t)   // (a) finite-EMA sampling noise → edge marginals
let kappa_t     : Knowledge<f64>     = lly_orc(marginals_t)                      // (b) GUM propagation through the OT solve
let warn_t      : bool               = (kappa_t.value < baseline.value) and confidence_excludes(kappa_t, baseline)  // (c) gate
```

The early warning fires **only when both** κ(t) drops **and** its propagated confidence interval
excludes the personal baseline. This is the dissertation's "compile-time confidence gate / ISO
uncertainty budget" idea turned into a clinical early-warning gate — a genuinely novel use of the
language, not a rhetorical flourish.

## 7. Pitfall named in advance (the dynamic density confound)

Static κ survived density-matching but `corr(κ, ⟨k⟩) = 0.991`. EMA networks built by sliding-window
partial correlation have density that swings with data quality (missed responses, window length).
**Window-density-matching κ(t)** is the dynamic analog of the density-matched control we already ran;
it is built into the pilot from the start, not rediscovered. A κ(t) drop is only counted as a signal
if it survives matching the window's edge density to the baseline.

## 8. Data wall (honest)

- **No longitudinal mood / EMA data on disk.** Repo data is static-group depression-text co-occurrence graphs (HelaDepDet, NOT SWOW),
  cross-sectional ABIDE-I connectome, physiological EEGMMIDB (no clinical labels), and CHB-MIT
  *annotations only* (no signal). The human-mood test is therefore **proposal-shaped** until a public
  ESM cohort is pulled.
- **Named target dataset:** Kossakowski et al., *Data from "Critical Slowing Down as a Personalized
  Early Warning Signal for Depression"* (J. Open Psychology Data 2017) — single patient, double-blind
  medication tapering, ~239 days, 5–10×/day ESM. The canonical CSD open dataset; the natural first
  external validation substrate.
- **Synthetic substrate present:** `data/cpc2026/trajectories_{normative,anxious,psychotic,ruminative}_input.npz`
  (10000 × 500 × 8). Four *stationary* regimes — good for a methods proof-of-concept, **not** a
  transition test. ⚠ Column 0 is `feature_kappa`: it **must be dropped** (the octonion/sedenion
  curvature-contamination lesson — never let κ leak into the features feeding a curvature claim).

## 9. Pilot plan (runs now, decides feasibility before any clinical claim)

**Pilot 1 — methods proof-of-concept (synthetic, runnable now).**
Build a dynamic k-NN network across the 10000 trajectories at each of 500 timesteps from the **7
curvature-free** features (drop `feature_kappa`); compute window-density-matched LLY-ORC per
timestep; verify (i) the pipeline produces a κ(t) series with GUM confidence bands, (ii) the warning
gate behaves (no false fire on stationary `normative`), and (iii) the three more-fragile regimes
(anxious/psychotic/ruminative) sit at more-negative κ than normative. *This validates the
instrument, not the clinical hypothesis.*

**Pilot 1 — DIRECTIONAL PROBE RESULT (2026-05-26, `/tmp/pilot1_quick.py`).**
kNN network (k=8, 250 subsampled trajectory-nodes, timestep t=250), LLY-ORC via exact POT,
features = {entropy_norm, c_ent, valence, log_degree} (κ, Poincaré coords, η_local dropped):

| regime | mean κ | neg% | reading |
|--------|-------:|-----:|---------|
| normative | +0.165 | 24% | most robust |
| anxious | +0.127 | 27% | |
| ruminative | +0.137 | 32% | |
| psychotic | +0.098 | 33% | most fragile |

**Normative = most robust (highest κ, fewest negative edges); psychotic = most fragile** — the
predicted fragility ordering, on curvature-free inputs. *Caveats (not yet a result):* single
timestep, single subsample, no CIs/permutation nulls yet, and `log_degree` is density-correlated
(the corr(κ,⟨k⟩)=0.991 pitfall) so the window-density control of §7 is required before claiming the
ordering is not a density artifact. Directional confirmation that the instrument behaves and the
fragility axis is present.

**Pilot 2 — synthetic transition sweep (state hypothesis).**
Synthesize a control-parameter interpolation `normative → ruminative` crossing a tipping point; test
whether confidence-gated κ(t) drops *before* the regime label flips, and compare its lead time to
classical lag-1 autocorrelation + variance EWS computed on the same series. Pre-registered kill-test:
if gated-κ does **not** lead (or merely tracks) the scalar EWS, the geometric signal adds nothing —
report as honest negative, as with the octonion associator and the sedenion annihilation null.

**Pilot 3 — external validation (RUN 2026-05-27).** `code/analysis/kossakowski_geometric_csd.py` +
`kossakowski_robustness_sweep.py` on the Kossakowski single-case ESM data (`data/external/kossakowski_csd/`);
full results + caveats in `results/unified/kossakowski_geometric_csd_ANALYSIS.md`.
**Robust (8/8 hyperparameter cells):** Pearson & hyperbolic κ drop during the phase-3 dose reduction
(days 58–70), recovering in phase 5 while depression persists (curvature marks destabilization, not
level). **Honest negatives on the strong claims:** (i) κ does **not** robustly *lead* the scalar
variance/autocorrelation EWS — holds only at 28-day windows (4/8), below the pre-registered 6/8, so
withdrawn; (ii) **partial-correlation κ shows no signal** → cross-metric pre-registration not met (2/3);
(iii) the κ drop is **post-perturbation** (~16–24 d after taper onset), not anticipatory; (iv) n=1.
Net: a robust *descriptive* observation, an honest negative on "κ beats CSD" and "holds across metrics"
— the octonion/sedenion-null discipline applied again. Motivates a multi-subject, spontaneous-transition test.

## 10. Three honest outcomes (named before running)

1. **Geometric EWS wins:** gated-κ(t) leads scalar CSD with fewer false alarms → a new, theoretically
   grounded early-warning signal + a flagship use of Sounio epistemic types.
2. **Redundant:** gated-κ tracks but does not beat autocorrelation/variance → curvature is a
   re-parameterization of CSD, not an improvement. Honest negative.
3. **Partial:** κ(t) localizes *which* affect edges destabilize (spatial information scalar EWS lack)
   even if global lead time is comparable → informative methodological contribution.

## 11. What this explicitly is NOT

Not a resurrection of the sedenion/octonion algebra axis (Phase A closed it as a null,
`results/unified/annihilation_invariant_ANALYSIS.md`). The bold lever here is **curvature dynamics +
epistemic types**, on the one axis that has survived every kill-test. No clinical claim is made until
Pilot 3 runs on real ESM data.

---

*Sources:* Science Advances 2016 (sciadv.1501495); PNAS 2014 (pnas.1312114110); Curr Opin Psychol
2021 (S2352250X21000257); Nat Commun 2019 (s41467-019-12915-x); Frontiers Aging Neurosci 2023
(PMC10244515); Physica D 2011 (arXiv:1101.2899); Bioinformatics 2025 (PMC11893153);
arXiv:2405.07134; Clin Psych Sci 2025 (Sage 21677026241305136); J. Open Psychology Data 2017
(Kossakowski CSD dataset).

---

# Addendum (2026-05-27): GUM-through-Sinkhorn — the implemented Sounio mechanism

The contribution that makes this *uniquely Sounio* is not "curvature with error bars" — it is that
the optimal-transport solve defining κ runs **natively on uncertainty-typed numbers**, so a
measurement uncertainty budget propagates *through* the transport solve into κ, and the early warning
is a **discharged confidence obligation** rather than a post-hoc statistic. Four runnable artifacts
(all `//@ run-pass`, verified with `./bin/souc run`):

| Artifact (in the Sounio repo) | What it establishes |
|---|---|
| `examples/semantic_orc/gum_sinkhorn_2x2_single_edge.sio` | GUM-through-Sinkhorn via finite-difference Jacobian: κ=−0.500, σ=0.194 on a bottleneck edge. Certification **dose-response**: n_eff=30 → conf 612, gate **withholds**; n_eff=300 → conf 877, gate **fires** on the *same* below-baseline curvature — the gate behaves consistently with its certification design. (False-alarm-*rate* reduction vs. a competing detector requires a comparative trial on real EMA data, not shown here.) |
| `stdlib/epistemic/knowledge_transcendental.sio` | `ep_exp`/`ep_log`/`ep_logsumexp2` GUM primitives; self-test cross-validates the logsumexp variance against a finite-difference Jacobian (8/8 PASS). |
| `examples/semantic_orc/epistemic_sinkhorn_orc.sio` | **The headline.** The Sinkhorn fixed point solved on forward-mode AD dual numbers carrying ∂/∂(marginals); GUM variance is **exact**, matching the finite-difference ground truth to ratio **0.999997**. |
| `examples/hyperbolic_semantic_networks/gum_sinkhorn_transition_sweep.sio` | λ-sweep healthy→fragile: κ drops −0.5→−2.0, confidence rises 726→849, gate fires at λ=0.3; classical OU variance + lag-1 autocorrelation (critical slowing down) rise alongside. |

## A methodological finding worth its own line

Propagating a **scalar** variance field through the Sinkhorn u↔v iteration is **wrong**: it
re-injects the marginal variance every iteration and ignores u–v correlation (the delta method has
no variable-identity tracking), inflating Var(κ) by **~249×** over 64 iterations vs. ground truth.
The fix — carry a **gradient vector** (forward-mode AD) with each number — recovers the exact total
derivative, because differentiating the iterates of a contraction converges to the
implicit-function-theorem derivative of the fixed point. *Lesson: GUM-through-an-iterative-solver
needs sensitivity (AD) tracking, not scalar variance propagation.*

## Theory status after external math-review (xai/Grok 4.1, logged 2026-05-27)

The motivating picture — κ, return-rate, critical slowing down, and confidence collapse as "one
optimal-transport object" — was audited and **partially downgraded**. Honest status:

- **[RIGOROUS] (a)** Under the Lott–Sturm–Villani / Bakry–Émery **CD(K,∞)** condition, a Ricci lower
  bound K gives spectral gap λ₁ ≥ K and W₂-contraction of the heat flow at rate e^{−Kt}. Correct.
- **[RIGOROUS] (d)** Forward-mode AD through the converged Sinkhorn solve = the implicit-function
  derivative of the fixed point; hence the exact GUM variance. Correct (and the implemented result).
- **[HEURISTIC — analogy, NOT identity] (b)** Discrete graph Ollivier–Ricci κ is an *analogue* of the
  continuous CD(K,∞) curvature, not the same object (Ollivier 2009; Lin–Lu–Yau; Erbar–Maas give
  separate discrete contraction/spectral-gap theorems). **We do not claim identity.**
- **[HEURISTIC] (c)** "K→0 ⇔ critical slowing down" conflates the spectral gap of the *diffusion
  generator* with the dominant eigenvalue of the *state-dynamics* Jacobian — distinct operators that
  need not coincide. Treated as motivating intuition, not a derived equivalence.
- **[TIGHTENED] (e)** Independent-binomial marginal variance over-estimates Var(κ) (conservative
  bound) **only when all ∂κ/∂pᵢ share sign**; sign changes or the active simplex constraint can
  reverse it. The artifacts state this conservative-bound caveat in their headers.

So the **"four faces" is a motivating analogy, with two rigorous links (a, d) and two heuristic ones
(b, c).** The Sounio contribution stands on (d): the OT solve runs natively on uncertainty types and
its propagated curvature uncertainty is exact. The clinical early-warning claim remains blocked on
real ESM data (Kossakowski 2017); the synthetic sweep is a pipeline + well-posed-comparison
demonstration, not a lead-time result.

**On the "fourth face" (confidence collapse).** The motivating picture said "near κ→0 the OT solve
is ill-conditioned, so confidence collapses." That OT-ill-conditioning *mechanism* is **not
demonstrated** by these artifacts and is withdrawn as a claim. What *is* true in the implementation:
confidence is defined as `1000·(1 − σ/|κ|)`, so it falls automatically as |κ|→0 (relative
uncertainty diverges) and rises as |κ| grows — exactly what the Stage-4 sweep shows (κ −0.5→−2.0,
confidence 726→849). That is a property of the relative-uncertainty *definition*, not evidence of
transport ill-conditioning. The implemented sweep deliberately follows the empirical fragility
direction (κ away from 0); the bifurcation κ→0 direction is a separate, currently undemonstrated
face (see the DIRECTION CAVEAT in §3).
