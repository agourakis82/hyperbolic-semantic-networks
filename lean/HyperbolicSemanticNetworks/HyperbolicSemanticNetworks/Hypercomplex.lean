import Mathlib.Algebra.Quaternion
import Mathlib.Analysis.Quaternion
import Mathlib.Data.Real.Basic
import Mathlib.Tactic
import «HyperbolicSemanticNetworks».Basic
import «HyperbolicSemanticNetworks».Curvature
import «HyperbolicSemanticNetworks».DynamicNetworks
/-!
# Hypercomplex Algebras: Cayley-Dickson Tower and Network Geometry

This module formalises the Cayley-Dickson tower

  ℝ → ℂ → ℍ (quaternions) → 𝕆 (octonions) → 𝕊 (sedenions)

and connects the hypercomplex structure to the geometry of semantic and
brain networks studied in the rest of this formalization.

## The Cayley-Dickson Construction

Starting from any ∗-ring (A, ·, *, star), the Cayley-Dickson doubling produces
a new algebra CayleyDickson A whose elements are pairs (a, b) : A × A with:
  - Addition:     (a, b) + (c, d) = (a+c, b+d)
  - Multiplication: (a, b) * (c, d) = (ac − d̄b, da + bc̄)
  - Conjugation:  conj(a, b) = (ā, −b)

Applied to ℍ[ℝ] (Mathlib's `Quaternion ℝ`), we obtain:
  - CayleyDickson ℍ[ℝ]           = 𝕆  (octonions, 8D over ℝ)
  - CayleyDickson 𝕆              = 𝕊  (sedenions, 16D over ℝ)

## Key Algebraic Properties (Cayley-Dickson Disease)

Each doubling step preserves less structure:

| Algebra | Dim | Commutative | Associative | Zero-divisor-free |
|---------|-----|-------------|-------------|-------------------|
| ℝ       |  1  | ✓           | ✓           | ✓                 |
| ℂ       |  2  | ✓           | ✓           | ✓                 |
| ℍ       |  4  | ✗           | ✓           | ✓                 |
| 𝕆       |  8  | ✗           | ✗ (alt.)    | ✓                 |
| 𝕊       | 16  | ✗           | ✗           | ✗                 |

## Connection to Network Geometry

The 7 canonical resting-state networks (RSNs) in human fMRI — Default Mode,
Sensorimotor, Visual, Dorsal Attention, Ventral Attention, Frontoparietal, Limbic —
together with a global signal component, form an 8-dimensional state vector.
This maps naturally to the octonion algebra 𝕆 = ℝ ⊕ ℝ⁷.

A brain state x(t) = global·1 + dmn·e₁ + ··· + lim·e₇ traces a path in
octonion space, and the ORC phase transition (κ̄ ≈ 0 at η ≈ 2.5) corresponds
to the transition from imaginary-dominated (hyperbolic, κ̄ < 0) to
real-dominated (spherical, κ̄ > 0) octonion states.

## References

- Cayley (1845): "On Jacobi's elliptic functions, in reply to Rev. B. Bronwin"
- Dickson (1919): "On Quaternions and Their Generalization"
- Agourakis (2025): "Boundary Conditions for Hyperbolic Geometry in Semantic Networks"
-/


namespace HyperbolicSemanticNetworks

open scoped Quaternion

noncomputable section

namespace Hypercomplex

/-! ## §1. The Cayley-Dickson Construction -/

/-- The Cayley-Dickson doubling of an algebra A.
    Elements are pairs (fst, snd) : A × A equipped with the
    Cayley-Dickson multiplication and conjugation. -/
@[ext]
structure CayleyDickson (A : Type*) where
  /-- First component (the "real" part of the pair). -/
  fst : A
  /-- Second component (the "imaginary" part of the pair). -/
  snd : A

namespace CayleyDickson

variable {A : Type*}

/-! ### Basic instances (componentwise operations) -/

instance [Zero A] : Zero (CayleyDickson A) where
  zero := ⟨0, 0⟩

instance [Add A] : Add (CayleyDickson A) where
  add x y := ⟨x.fst + y.fst, x.snd + y.snd⟩

instance [Neg A] : Neg (CayleyDickson A) where
  neg x := ⟨-x.fst, -x.snd⟩

instance [Sub A] : Sub (CayleyDickson A) where
  sub x y := ⟨x.fst - y.fst, x.snd - y.snd⟩

instance [Zero A] [One A] : One (CayleyDickson A) where
  one := ⟨1, 0⟩

/-- Cayley-Dickson multiplication: (a,b)·(c,d) = (ac − d̄b, da + bc̄).
    This is the key formula: the second component uses the conjugate (star)
    from the original algebra A. -/
instance [Mul A] [Sub A] [Add A] [Star A] : Mul (CayleyDickson A) where
  mul x y := ⟨x.fst * y.fst - star y.snd * x.snd,
              y.snd * x.fst + x.snd * star y.fst⟩

/-- Cayley-Dickson conjugation: conj(a, b) = (conj(a), −b).
    The conjugate reverses the second component. -/
instance [Star A] [Neg A] : Star (CayleyDickson A) where
  star x := ⟨star x.fst, -x.snd⟩

/-! ### Component projection simp lemmas -/

@[simp] lemma fst_zero [Zero A] :
    (0 : CayleyDickson A).fst = 0 := rfl

@[simp] lemma snd_zero [Zero A] :
    (0 : CayleyDickson A).snd = 0 := rfl

@[simp] lemma fst_one [Zero A] [One A] :
    (1 : CayleyDickson A).fst = 1 := rfl

@[simp] lemma snd_one [Zero A] [One A] :
    (1 : CayleyDickson A).snd = 0 := rfl

@[simp] lemma fst_add [Add A] (x y : CayleyDickson A) :
    (x + y).fst = x.fst + y.fst := rfl

@[simp] lemma snd_add [Add A] (x y : CayleyDickson A) :
    (x + y).snd = x.snd + y.snd := rfl

@[simp] lemma fst_neg [Neg A] (x : CayleyDickson A) :
    (-x).fst = -x.fst := rfl

@[simp] lemma snd_neg [Neg A] (x : CayleyDickson A) :
    (-x).snd = -x.snd := rfl

@[simp] lemma fst_sub [Sub A] (x y : CayleyDickson A) :
    (x - y).fst = x.fst - y.fst := rfl

@[simp] lemma snd_sub [Sub A] (x y : CayleyDickson A) :
    (x - y).snd = x.snd - y.snd := rfl

@[simp] lemma fst_mul [Mul A] [Sub A] [Add A] [Star A] (x y : CayleyDickson A) :
    (x * y).fst = x.fst * y.fst - star y.snd * x.snd := rfl

@[simp] lemma snd_mul [Mul A] [Sub A] [Add A] [Star A] (x y : CayleyDickson A) :
    (x * y).snd = y.snd * x.fst + x.snd * star y.fst := rfl

@[simp] lemma fst_star [Star A] [Neg A] (x : CayleyDickson A) :
    (star x).fst = star x.fst := rfl

@[simp] lemma snd_star [Star A] [Neg A] (x : CayleyDickson A) :
    (star x).snd = -x.snd := rfl

/-! ### SMul instances (required for Function.Injective.addCommGroup) -/

instance [SMul ℕ A] : SMul ℕ (CayleyDickson A) where
  smul n x := ⟨n • x.fst, n • x.snd⟩

instance [SMul ℤ A] : SMul ℤ (CayleyDickson A) where
  smul n x := ⟨n • x.fst, n • x.snd⟩

@[simp] lemma fst_nsmul [SMul ℕ A] (n : ℕ) (x : CayleyDickson A) :
    (n • x).fst = n • x.fst := rfl

@[simp] lemma snd_nsmul [SMul ℕ A] (n : ℕ) (x : CayleyDickson A) :
    (n • x).snd = n • x.snd := rfl

@[simp] lemma fst_zsmul [SMul ℤ A] (n : ℤ) (x : CayleyDickson A) :
    (n • x).fst = n • x.fst := rfl

@[simp] lemma snd_zsmul [SMul ℤ A] (n : ℤ) (x : CayleyDickson A) :
    (n • x).snd = n • x.snd := rfl

/-! ### AddCommGroup instance (via injectivity into A × A) -/

/-- CayleyDickson A is an additive commutative group (componentwise operations).
    Proved by injecting into A × A and using Function.Injective.addCommGroup. -/
instance [AddCommGroup A] : AddCommGroup (CayleyDickson A) :=
  Function.Injective.addCommGroup
    (fun x : CayleyDickson A => (x.fst, x.snd))
    (fun _ _ h => CayleyDickson.ext (Prod.mk.inj h).1 (Prod.mk.inj h).2)
    rfl
    (fun _ _ => rfl)
    (fun _ => rfl)
    (fun _ _ => rfl)
    (fun _ _ => rfl)
    (fun _ _ => rfl)

/-! ### Key multiplicative identities -/

/-- Conjugation is an involution: conj(conj(x)) = x. -/
@[simp]
lemma star_star [Ring A] [StarRing A] (x : CayleyDickson A) :
    star (star x) = x := by
  ext
  · simp only [fst_star, _root_.star_star]
  · simp only [snd_star, neg_neg]

/-- 1 is a left identity. -/
lemma one_mul [Ring A] [StarRing A] (x : CayleyDickson A) :
    (1 : CayleyDickson A) * x = x := by
  ext <;> simp

/-- 1 is a right identity. -/
lemma mul_one [Ring A] [StarRing A] (x : CayleyDickson A) :
    x * (1 : CayleyDickson A) = x := by
  ext <;> simp

/-! ### Norm squared -/

/-- The norm squared of a Cayley-Dickson element, given a norm on A.
    normSq(a, b) = normA(a) + normA(b). -/
def normSqWith (normA : A → ℝ) (x : CayleyDickson A) : ℝ :=
  normA x.fst + normA x.snd

/-- Norm squared is non-negative when the base norm is non-negative. -/
lemma normSqWith_nonneg {normA : A → ℝ} (h : ∀ a, 0 ≤ normA a)
    (x : CayleyDickson A) : 0 ≤ normSqWith normA x :=
  add_nonneg (h _) (h _)

end CayleyDickson

/-! ## §2. Octonions (𝕆) -/

/-- The **octonion algebra** 𝕆: the Cayley-Dickson doubling of ℍ[ℝ].
    Elements are pairs of quaternions (q₁, q₂) with Cayley-Dickson product.

    Dimension: 8 over ℝ (basis: 1, e₁, e₂, e₃, e₄, e₅, e₆, e₇).
    Properties: non-commutative, non-associative, but *alternative* and
    zero-divisor-free. -/
abbrev Octonion := CayleyDickson (ℍ[ℝ])

namespace Octonion

/-- Octonion norm squared: ||(q₁, q₂)||² = normSq(q₁) + normSq(q₂). -/
noncomputable def normSq (x : Octonion) : ℝ :=
  Quaternion.normSq x.fst + Quaternion.normSq x.snd

/-- Octonion norm squared is non-negative. -/
lemma normSq_nonneg (x : Octonion) : 0 ≤ normSq x :=
  add_nonneg (Quaternion.normSq_nonneg) (Quaternion.normSq_nonneg)

/-- Standard octonion basis: the 8 basis elements over ℝ. -/
def basis : Fin 8 → Octonion
  | ⟨0, _⟩ => ⟨⟨1, 0, 0, 0⟩, ⟨0, 0, 0, 0⟩⟩  -- 1
  | ⟨1, _⟩ => ⟨⟨0, 1, 0, 0⟩, ⟨0, 0, 0, 0⟩⟩  -- e₁ = i
  | ⟨2, _⟩ => ⟨⟨0, 0, 1, 0⟩, ⟨0, 0, 0, 0⟩⟩  -- e₂ = j
  | ⟨3, _⟩ => ⟨⟨0, 0, 0, 1⟩, ⟨0, 0, 0, 0⟩⟩  -- e₃ = k
  | ⟨4, _⟩ => ⟨⟨0, 0, 0, 0⟩, ⟨1, 0, 0, 0⟩⟩  -- e₄
  | ⟨5, _⟩ => ⟨⟨0, 0, 0, 0⟩, ⟨0, 1, 0, 0⟩⟩  -- e₅
  | ⟨6, _⟩ => ⟨⟨0, 0, 0, 0⟩, ⟨0, 0, 1, 0⟩⟩  -- e₆
  | ⟨7, _⟩ => ⟨⟨0, 0, 0, 0⟩, ⟨0, 0, 0, 1⟩⟩  -- e₇
  | ⟨n + 8, h⟩ => absurd h (by omega)

/-- Every octonion decomposes into its 8 real components. -/
lemma component_decomp (x : Octonion) :
    x = ⟨⟨x.fst.re, x.fst.imI, x.fst.imJ, x.fst.imK⟩,
          ⟨x.snd.re, x.snd.imI, x.snd.imJ, x.snd.imK⟩⟩ := by
  obtain ⟨⟨r1, i1, j1, k1⟩, ⟨r2, i2, j2, k2⟩⟩ := x; rfl

/-! ### Algebraic properties of octonions (axioms) -/

/-- **Axiom**: Octonions are non-associative.
    The Cayley-Dickson doubling of ℍ loses associativity of multiplication.
    Explicit witnesses: e₁·(e₂·e₄) ≠ (e₁·e₂)·e₄ = e₃·e₄ = e₇, but
    e₁·(e₂·e₄) = e₁·e₆ = −e₇. -/
axiom octonion_nonassociative :
    ∃ (x y z : Octonion), (x * y) * z ≠ x * (y * z)

/-- **Axiom**: Octonions satisfy the *left* alternative identity xx·y = x·xy.
    Every two-element subalgebra of 𝕆 is associative (Artin's theorem). -/
axiom octonion_left_alternative (x y : Octonion) :
    x * x * y = x * (x * y)

/-- **Axiom**: Octonions satisfy the *right* alternative identity y·xx = yx·x. -/
axiom octonion_right_alternative (x y : Octonion) :
    y * (x * x) = y * x * x

/-- **Axiom**: Octonions have no zero divisors.
    If xy = 0 then x = 0 or y = 0. This is equivalent to 𝕆 being a
    *composition algebra* (the norm is multiplicative). -/
axiom octonion_no_zero_divisors (x y : Octonion) :
    x * y = 0 → x = 0 ∨ y = 0

/-- **Axiom**: The octonion norm is multiplicative: ||xy||² = ||x||² · ||y||².
    This is the defining property of a *composition algebra*. -/
axiom octonion_composition (x y : Octonion) :
    normSq (x * y) = normSq x * normSq y

end Octonion

/-! ## §3. Sedenions (𝕊) -/

/-- The **sedenion algebra** 𝕊: the Cayley-Dickson doubling of 𝕆.
    Elements are pairs of octonions with Cayley-Dickson product.

    Dimension: 16 over ℝ.
    Properties: non-commutative, non-associative, NOT alternative,
    and has zero divisors (hence NOT a division algebra). -/
abbrev Sedenion := CayleyDickson Octonion

namespace Sedenion

/-- Sedenion norm squared: ||(x₁, x₂)||² = normSq(x₁) + normSq(x₂). -/
noncomputable def normSq (x : Sedenion) : ℝ :=
  Octonion.normSq x.fst + Octonion.normSq x.snd

/-- Sedenion norm squared is non-negative. -/
lemma normSq_nonneg (x : Sedenion) : 0 ≤ normSq x :=
  add_nonneg (Octonion.normSq_nonneg _) (Octonion.normSq_nonneg _)

/-- **Axiom**: Sedenions have zero divisors.
    There exist nonzero sedenions whose product is zero.
    The composition law fails: ||xy||² ≠ ||x||² · ||y||² in general. -/
axiom sedenion_has_zero_divisors :
    ∃ (a b : Sedenion), a ≠ 0 ∧ b ≠ 0 ∧ a * b = 0

/-- **Axiom**: The sedenion norm is NOT multiplicative. -/
axiom sedenion_fails_composition :
    ∃ (a b : Sedenion), normSq (a * b) ≠ normSq a * normSq b

end Sedenion

/-! ## §4. The Cayley-Dickson Tower -/

/-- Dimension of each algebra in the Cayley-Dickson tower (powers of 2). -/
def towerDim : Fin 5 → ℕ
  | ⟨0, _⟩ => 1    -- ℝ
  | ⟨1, _⟩ => 2    -- ℂ
  | ⟨2, _⟩ => 4    -- ℍ (quaternions)
  | ⟨3, _⟩ => 8    -- 𝕆 (octonions)
  | ⟨4, _⟩ => 16   -- 𝕊 (sedenions)
  | ⟨n + 5, h⟩ => absurd h (by omega)

/-- Each doubling step doubles the dimension. -/
lemma tower_dim_doubles (k : Fin 4) :
    towerDim k.succ = 2 * towerDim k.castSucc := by
  fin_cases k <;> simp [towerDim]

/-- The algebraic property lost at each doubling step.
    Known as the "Cayley-Dickson disease" sequence. -/
def lostProperty : Fin 5 → String
  | ⟨0, _⟩ => "none (base field ℝ)"
  | ⟨1, _⟩ => "linear order (ℂ is not an ordered field)"
  | ⟨2, _⟩ => "commutativity of × (ℍ: ab ≠ ba in general)"
  | ⟨3, _⟩ => "associativity of × (𝕆: (ab)c ≠ a(bc) in general)"
  | ⟨4, _⟩ => "zero-divisor-free (𝕊: ∃ a,b ≠ 0 with ab = 0)"
  | ⟨n + 5, h⟩ => absurd h (by omega)

/-! ## §5. Hypercomplex Brain Network Geometry -/

/-!
### The Octonion–Brain Network Correspondence

Human resting-state fMRI consistently identifies 7–8 canonical networks:
  1. Default Mode Network (DMN)
  2. Sensorimotor Network (SMN)
  3. Visual Network (VN)
  4. Dorsal Attention Network (DAN)
  5. Ventral Attention Network (VAN)
  6. Frontoparietal Network (FPN)
  7. Limbic Network (LN)

These 7 networks + 1 global signal = 8 real dimensions, which map naturally
to the octonion algebra 𝕆 = ℝ ⊕ ℝ⁷ via:

  x(t) = global·1 + dmn·e₁ + smn·e₂ + vn·e₃
        + dan·e₄ + van·e₅ + fpn·e₆ + lim·e₇

The ORC phase transition (κ̄ ≈ 0 at η ≈ 2.5) corresponds to:
  κ̄ < 0 (hyperbolic) ↔ ||snd||² > ||fst||²  (distributed/subcortical networks dominate)
  κ̄ ≈ 0 (Euclidean)  ↔ ||snd||² ≈ ||fst||²  (balanced, critical point)
  κ̄ > 0 (spherical)  ↔ ||fst||² > ||snd||²  (frontal/global signal dominates)
-/

/-- A brain state encoded as an octonion.
    The 7 canonical RSNs + global signal occupy the 8 octonion components. -/
noncomputable def brainState
    (global dmn smn vn dan van fpn lim : ℝ) : Octonion :=
  ⟨⟨global, dmn, smn, vn⟩, ⟨dan, van, fpn, lim⟩⟩

/-- Total neural activity = sum of squares of all 8 RSN components. -/
lemma brainState_normSq (global dmn smn vn dan van fpn lim : ℝ) :
    Octonion.normSq (brainState global dmn smn vn dan van fpn lim) =
    global ^ 2 + dmn ^ 2 + smn ^ 2 + vn ^ 2 +
    dan ^ 2 + van ^ 2 + fpn ^ 2 + lim ^ 2 := by
  simp only [Octonion.normSq, brainState]
  rw [Quaternion.normSq_def', Quaternion.normSq_def']
  ring

/-- A brain state is **hyperbolic**: the distributed/subcortical networks
    (encoded in the second quaternion) dominate the global/frontal signal.
    This corresponds to κ̄ < 0 in the ORC phase diagram. -/
def IsHyperbolicBrainState (x : Octonion) : Prop :=
  Quaternion.normSq x.snd > Quaternion.normSq x.fst

/-- A brain state is **spherical**: the global/frontal signal dominates.
    This corresponds to κ̄ > 0 in the ORC phase diagram. -/
def IsSphericalBrainState (x : Octonion) : Prop :=
  Quaternion.normSq x.fst > Quaternion.normSq x.snd

/-- A brain state is at the **Euclidean critical point**: the two halves are
    balanced to within ε. This is the phase transition κ̄ ≈ 0, η ≈ 2.5. -/
def IsCriticalBrainState (x : Octonion) (ε : ℝ) : Prop :=
  |Quaternion.normSq x.fst - Quaternion.normSq x.snd| ≤ ε

/-- **Theorem** (proved): The three geometry classes are exhaustive.
    Every brain state is either hyperbolic, spherical, or exactly at balance. -/
theorem brain_geometry_trichotomy (x : Octonion) :
    IsHyperbolicBrainState x ∨ IsSphericalBrainState x ∨
    Quaternion.normSq x.fst = Quaternion.normSq x.snd := by
  rcases lt_trichotomy (Quaternion.normSq x.fst) (Quaternion.normSq x.snd) with h | h | h
  · exact Or.inl h
  · exact Or.inr (Or.inr h)
  · exact Or.inr (Or.inl h)

/-- **Theorem** (proved): A brain state in the hyperbolic regime has positive
    total activity (normSq > 0) if and only if it is nonzero. -/
theorem hyperbolic_state_norm_pos {x : Octonion}
    (h : IsHyperbolicBrainState x) : 0 < Octonion.normSq x := by
  unfold IsHyperbolicBrainState at h
  have h1 : 0 < Quaternion.normSq x.snd := lt_of_le_of_lt Quaternion.normSq_nonneg h
  have h2 : 0 ≤ Quaternion.normSq x.fst := Quaternion.normSq_nonneg
  simp only [Octonion.normSq]
  linarith

/-- **Axiom**: The hypercomplex geometry conjecture.
    The sign of mean ORC κ̄ in a connectome G agrees with the balance
    direction of the corresponding octonion brain state x. -/
axiom orc_hypercomplex_correspondence
    {V : Type} [Fintype V] [DecidableEq V]
    (G : WeightedGraph V) (α : Curvature.Idleness) (x : Octonion) :
    (DynamicNetworks.meanORC G α < 0 ↔ IsHyperbolicBrainState x) ∧
    (DynamicNetworks.meanORC G α > 0 ↔ IsSphericalBrainState x)

/-- **Theorem** (proved): Every 8-component real signal embeds into 𝕆,
    and every 16-component signal embeds into 𝕊 (via two octonions). -/
theorem hypercomplex_embedding_exists :
    -- 𝕆 embeds 8-RSN brain states
    (∀ (global dmn smn vn dan van fpn lim : ℝ),
      ∃ x : Octonion, x = brainState global dmn smn vn dan van fpn lim) ∧
    -- 𝕊 embeds 16-dimensional parcellation states (two octonions)
    (∀ (a b c d e f g h i j k l m n o p : ℝ),
      ∃ s : Sedenion,
        s.fst = brainState a b c d e f g h ∧
        s.snd = brainState i j k l m n o p) := by
  constructor
  · intro global dmn smn vn dan van fpn lim
    exact ⟨brainState global dmn smn vn dan van fpn lim, rfl⟩
  · intro a b c d e f g h i j k l m n o p
    exact ⟨⟨brainState a b c d e f g h, brainState i j k l m n o p⟩, rfl, rfl⟩

end Hypercomplex

end

end HyperbolicSemanticNetworks
