import Mathlib.Data.Real.Basic
import Mathlib.Order.Interval.Set.Basic
import Mathlib.Data.Finset.Basic
import «HyperbolicSemanticNetworks».Basic
import «HyperbolicSemanticNetworks».Curvature
import «HyperbolicSemanticNetworks».PhaseTransition
import «HyperbolicSemanticNetworks».Axioms
/-!
# Dynamic Networks and Temporal Stability of Ollivier-Ricci Curvature

This module formalizes the mathematics of **time-varying semantic networks**
and proves that Ollivier-Ricci curvature is **temporally stable** under slow
network evolution — a prerequisite for using mean ORC as a biomarker in fMRI
connectome analysis.

## Key Results

1. **`temporal_ORC_stability`** (Theorem, proved by induction on t):
   If a dynamic network W(t) evolves slowly — graphDist(W(t), W(t+1)) ≤ δ per
   step — and ORC is L-Lipschitz in edge weights, then:
   ```
   |κ̄(W(t)) - κ̄(W(0))| ≤ L · δ · t
   ```
   **Proof method**: Induction on t, using the triangle inequality for |·| and
   the one-step Lipschitz bound at each stage.

2. **`sweetSpot_persistence`** (Theorem):
   A network with κ̄(W(0)) < -γ (strictly hyperbolic, margin γ) stays in the
   hyperbolic regime for all t with L · δ · t < γ.

3. **`ORC_biomarker_sensitivity`** (Theorem):
   Contrapositive of Lipschitz: geometrically separated networks must be
   separated in edge-weight space, graphDist(G, H) ≥ |κ̄(G) - κ̄(H)| / L.

## Connection to McDiarmid's Inequality

The Lipschitz constant L = 4/n (`ORC_Lipschitz_constant`) equals
`Axioms.curvature_lipschitz_constant n`, the bounded differences constant
used in McDiarmid's inequality. This is proved as `McDiarmid_equals_Lipschitz`
(by `rfl`). The two stability perspectives — deterministic Lipschitz and
probabilistic McDiarmid concentration — are two sides of the same coin.

## Application to fMRI Connectomics (Track A)

The `brain_connectome_sweet_spot_hypothesis` axiom conjectures that healthy
human brain connectomes, when thresholded at the appropriate density level,
sit near the critical value η ≈ 2.5. This will be tested empirically in
Track A using the ADHD-200 resting-state fMRI dataset.

## References

- McDiarmid (1989): "On the method of bounded differences"
- Ni et al. (2019): "Community detection on networks via Ricci flow"
- Agourakis (2025): "Boundary Conditions for Hyperbolic Geometry in Semantic
  Networks" (this work; Track A validates the brain connectome hypothesis)
-/


namespace HyperbolicSemanticNetworks

noncomputable section

namespace DynamicNetworks

variable {V : Type} [Fintype V] [DecidableEq V]

/-! ## Dynamic Network Model -/

/-- A dynamic network: a discrete-time family of weighted graphs on vertex set V.
    For fMRI connectomes, each time step represents one TR (repetition time,
    typically 2–3 seconds in resting-state protocols). -/
def DynamicNetwork (V : Type) [Fintype V] [DecidableEq V] :=
  ℕ → WeightedGraph V

/-! ## Graph Distance (L1 Edge-Weight Metric) -/

/-- The L1 distance between two weighted graphs: sum of absolute edge weight
    differences over all ordered pairs (u, v).
    graphDist(G, H) = Σ_{u,v} |G.weights(u,v) - H.weights(u,v)|

    This measures how far two network configurations are in weight-space.
    For symmetric graphs, the sum double-counts each edge, but the factor of 2
    is absorbed into the Lipschitz constant. -/
noncomputable def graphDist (G H : WeightedGraph V) : ℝ :=
  ∑ u : V, ∑ v : V, |G.weights u v - H.weights u v|

/-- Graph distance is non-negative. -/
lemma graphDist_nonneg (G H : WeightedGraph V) : 0 ≤ graphDist G H := by
  apply Finset.sum_nonneg
  intro u _
  apply Finset.sum_nonneg
  intro v _
  exact abs_nonneg _

/-- Graph distance is symmetric: graphDist(G, H) = graphDist(H, G). -/
lemma graphDist_comm (G H : WeightedGraph V) : graphDist G H = graphDist H G := by
  simp [graphDist, abs_sub_comm]

/-- Graph distance to self is zero. -/
lemma graphDist_self (G : WeightedGraph V) : graphDist G G = 0 := by
  simp [graphDist]

/-! ## Mean ORC -/

/-- Mean Ollivier-Ricci curvature of a network G under idleness parameter α.
    This is the primary biomarker for network geometry:
    - κ̄ < 0: hyperbolic (tree-like, typical for semantic networks at η < 2.5)
    - κ̄ ≈ 0: Euclidean (flat, critical point at η ≈ 2.5)
    - κ̄ > 0: spherical (clique-like, high clustering at η > 3.5) -/
noncomputable def meanORC (G : WeightedGraph V) (α : Curvature.Idleness) : ℝ :=
  Curvature.meanCurvature G α

/-! ## Lipschitz Constant -/

/-- The Lipschitz constant for mean ORC under edge weight perturbations.
    Equals Axioms.curvature_lipschitz_constant n = 4/n.

    Justification: adding or removing one edge in a graph on n vertices
    changes the mean ORC by at most 4/n (the "bounded differences" property
    used in McDiarmid's inequality). -/
noncomputable def ORC_Lipschitz_constant (n : ℕ) : ℝ :=
  Axioms.curvature_lipschitz_constant n

/-- The Lipschitz constant equals 4/n by definition. -/
lemma ORC_Lipschitz_constant_eq (n : ℕ) :
    ORC_Lipschitz_constant n = 4 / n := rfl

/-! ## ORC Lipschitz Axiom -/

/-- **Axiom**: Mean ORC is Lipschitz continuous in edge weights.

    |κ̄(G) - κ̄(H)| ≤ (4/n) · graphDist(G, H)

    This is the deterministic counterpart of McDiarmid's inequality:
    Lipschitz continuity is precisely the bounded differences property
    instantiated to specific networks rather than random graph distributions.

    The formal proof would require tracking how each edge weight change
    propagates through: (1) the probability measures μᵤ, μᵥ, (2) the
    Wasserstein LP, (3) each κ(u,v), and (4) the mean over all pairs.
    We axiomatize because completing step (2) formally requires the full
    LP duality theory for finite transport problems. -/
axiom ORC_Lipschitz
    (α : Curvature.Idleness) (G H : WeightedGraph V) :
    |meanORC G α - meanORC H α| ≤
      ORC_Lipschitz_constant (Fintype.card V) * graphDist G H

/-! ## Main Theorem: Temporal Stability of ORC -/

/-- **Theorem** (proved by induction on t):
    Mean ORC is temporally stable for slowly-evolving networks.

    **Hypotheses**:
    - W : ℕ → WeightedGraph V (dynamic network)
    - L ≥ 0 (Lipschitz constant)
    - δ ≥ 0 (maximum per-step drift in weight-space)
    - h_slow: graphDist(W(t), W(t+1)) ≤ δ for all t
    - h_lip: |κ̄(G) - κ̄(H)| ≤ L · graphDist(G, H) for all G, H

    **Conclusion**: |κ̄(W(t)) - κ̄(W(0))| ≤ L · δ · t for all t : ℕ

    **Proof**:
    - Base (t = 0): |κ̄(W(0)) - κ̄(W(0))| = 0 = L·δ·0 ✓
    - Step (t = n+1): By triangle inequality,
        |κ̄(W(n+1)) - κ̄(W(0))|
        ≤ |κ̄(W(n+1)) - κ̄(W(n))| + |κ̄(W(n)) - κ̄(W(0))|
        ≤ L · graphDist(W(n), W(n+1)) + L · δ · n   (Lipschitz + IH)
        ≤ L · δ + L · δ · n                           (h_slow n)
        = L · δ · (n+1) ✓

    The general form (parameterized by L and h_lip) allows instantiation
    with either the axiomatic ORC_Lipschitz constant or empirical estimates
    from Track A data. -/
theorem temporal_ORC_stability
    (W : DynamicNetwork V) (α : Curvature.Idleness)
    (L δ : ℝ) (hL : 0 ≤ L) (_hδ : 0 ≤ δ)
    (h_slow : ∀ t : ℕ, graphDist (W t) (W (t + 1)) ≤ δ)
    (h_lip : ∀ G H : WeightedGraph V,
             |meanORC G α - meanORC H α| ≤ L * graphDist G H) :
    ∀ t : ℕ, |meanORC (W t) α - meanORC (W 0) α| ≤ L * δ * (t : ℝ) := by
  intro t
  induction t with
  | zero => simp
  | succ n ih =>
    -- Triangle inequality: split the difference via the intermediate state W(n)
    have tri : |meanORC (W (n + 1)) α - meanORC (W 0) α| ≤
               |meanORC (W (n + 1)) α - meanORC (W n) α| +
               |meanORC (W n) α - meanORC (W 0) α| := by
      have key : meanORC (W (n + 1)) α - meanORC (W 0) α =
                 (meanORC (W (n + 1)) α - meanORC (W n) α) +
                 (meanORC (W n) α - meanORC (W 0) α) := by ring
      rw [key]
      exact abs_add _ _
    -- Bound the one-step change via the Lipschitz hypothesis
    have step : |meanORC (W (n + 1)) α - meanORC (W n) α| ≤ L * δ :=
      calc |meanORC (W (n + 1)) α - meanORC (W n) α|
          = |meanORC (W n) α - meanORC (W (n + 1)) α| := abs_sub_comm _ _
        _ ≤ L * graphDist (W n) (W (n + 1)) := h_lip (W n) (W (n + 1))
        _ ≤ L * δ := mul_le_mul_of_nonneg_left (h_slow n) hL
    -- Combine inductive hypothesis and one-step bound
    calc |meanORC (W (n + 1)) α - meanORC (W 0) α|
        ≤ |meanORC (W (n + 1)) α - meanORC (W n) α| +
          |meanORC (W n) α - meanORC (W 0) α| := tri
      _ ≤ L * δ + L * δ * (n : ℝ) := add_le_add step ih
      _ = L * δ * ((↑(n + 1) : ℝ)) := by push_cast; ring

/-! ## Corollary: Persistence of Hyperbolic Regime -/

/-- **Theorem**: A network in the strictly hyperbolic regime stays hyperbolic
    under sufficiently slow evolution.

    If κ̄(W(0)) < -γ (strictly negative, margin γ > 0) and the network
    evolves so slowly that L · δ · t < γ, then κ̄(W(t)) < 0.

    **Proof**: From temporal_ORC_stability,
      κ̄(W(t)) - κ̄(W(0)) ≤ |κ̄(W(t)) - κ̄(W(0))| ≤ L · δ · t < γ
    Hence κ̄(W(t)) < κ̄(W(0)) + γ < -γ + γ = 0 ✓

    **Clinical interpretation**: A brain network stably in the "healthy
    hyperbolic" range (κ̄ < -γ) is robust to day-to-day fluctuations in
    functional connectivity, as long as those fluctuations are small
    relative to the margin γ. -/
theorem sweetSpot_persistence
    (W : DynamicNetwork V) (α : Curvature.Idleness)
    (L δ γ : ℝ) (hL : 0 ≤ L) (hδ : 0 ≤ δ) (_hγ : 0 < γ)
    (h_slow : ∀ t : ℕ, graphDist (W t) (W (t + 1)) ≤ δ)
    (h_lip : ∀ G H : WeightedGraph V,
             |meanORC G α - meanORC H α| ≤ L * graphDist G H)
    (h_init : meanORC (W 0) α < -γ) :
    ∀ t : ℕ, L * δ * (t : ℝ) < γ → meanORC (W t) α < 0 := by
  intro t h_small
  have h_bound := temporal_ORC_stability W α L δ hL hδ h_slow h_lip t
  -- From |a - b| ≤ c we extract the upper half: a - b ≤ c
  have h_upper : meanORC (W t) α - meanORC (W 0) α ≤ L * δ * (t : ℝ) :=
    le_trans (le_abs_self _) h_bound
  linarith

/-! ## ORC as a Geometric Biomarker -/

/-- The hyperbolic sweet spot condition: density parameter within ε of 2.5.
    A network satisfies this when η = ⟨k⟩²/N is close to the empirical
    critical value (≈ 2.5) where geometry transitions from hyperbolic to
    Euclidean to spherical. -/
def IsHyperbolicSweetSpot (G : WeightedGraph V) (ε : ℝ) : Prop :=
  |PhaseTransition.densityParameter G - PhaseTransition.empiricalCriticalValue| ≤ ε

/-- **Theorem**: ORC sensitivity — if two networks differ in curvature,
    they must be separated in edge-weight space.

    graphDist(G, H) ≥ |κ̄(G) - κ̄(H)| / L

    **Proof**: Immediate from the Lipschitz bound rearranged.

    **Clinical interpretation**: If a healthy brain (κ̄ₕ < 0) and a
    pathological brain (κ̄_p ≥ 0) have different ORC values, their
    functional connectivity matrices must differ by at least
    |κ̄ₕ - κ̄_p| / L in the L1 sense. ORC detects geometry changes
    that are too small to see edge-by-edge but large enough in aggregate. -/
theorem ORC_biomarker_sensitivity
    (α : Curvature.Idleness) (G H : WeightedGraph V)
    (L : ℝ) (hL : 0 < L)
    (h_lip : ∀ G' H' : WeightedGraph V,
             |meanORC G' α - meanORC H' α| ≤ L * graphDist G' H') :
    |meanORC G α - meanORC H α| / L ≤ graphDist G H := by
  rw [div_le_iff₀ hL]
  calc |meanORC G α - meanORC H α|
      ≤ L * graphDist G H := h_lip G H
    _ = graphDist G H * L := mul_comm L (graphDist G H)

/-! ## Brain Connectome Hypothesis (Track A) -/

/-- **Axiom** (empirical conjecture — to be validated in Track A):
    Healthy human brain connectomes, when thresholded at the appropriate
    density level, exhibit the same universal phase transition at η ≈ 2.5
    that was found in semantic networks (SWOW English and Spanish datasets).

    Specifically: there exists a threshold ε such that the density parameter
    of a healthy resting-state functional connectivity matrix falls within ε
    of the critical value 2.5.

    **Evidence supporting the conjecture**:
    - fMRI resting-state networks are known to have small-world topology
    - Small-world networks are associated with moderate clustering C ∈ [0.02, 0.15]
    - The semantic network "hyperbolic sweet spot" exactly matches this range
    - Both semantic and functional connectivity encode hierarchical structure

    **This axiom will be replaced by a theorem** once Track A completes the
    empirical analysis of ADHD-200 resting-state fMRI data. The Python pipeline
    in code/fmri/ computes FC matrices, applies ORC via the Rust library, and
    maps κ̄(η) across density thresholds for healthy and ADHD subjects.

    The key prediction: healthy subjects cluster near η* ≈ 2.5 with κ̄ < 0,
    while ADHD subjects show either shifted η* or increased temporal variance
    of κ̄ (captured by temporal_ORC_stability with larger δ). -/
axiom brain_connectome_sweet_spot_hypothesis
    (G_brain : WeightedGraph V)
    (_h_healthy : True)  -- placeholder for clinical "healthy subject" predicate
    (η_star : ℝ) (_h_η : η_star = PhaseTransition.empiricalCriticalValue) :
    ∃ ε > 0, IsHyperbolicSweetSpot G_brain ε

/-! ## McDiarmid = Lipschitz: Two Perspectives on the Same Constant -/

/-- **Theorem**: The ORC Lipschitz constant and McDiarmid's bounded differences
    constant are definitionally equal: both equal 4/n.

    This connects two stability perspectives:
    - **Lipschitz view** (deterministic): if we perturb one network's edges by
      amount ε, the mean ORC changes by at most (4/n)·ε. Holds for any network.
    - **McDiarmid view** (probabilistic): if we randomly flip one edge in G(n,p),
      the mean ORC concentrates with deviation probability ≤ 2exp(-2t²n²/N·(4/n)²).

    Both give exactly L = 4/n. The proof is by definitional unfolding (`rfl`). -/
theorem McDiarmid_equals_Lipschitz (n : ℕ) :
    ORC_Lipschitz_constant n = Axioms.curvature_lipschitz_constant n := rfl

end DynamicNetworks

end

end HyperbolicSemanticNetworks
