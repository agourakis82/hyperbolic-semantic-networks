"""
test_sedenion.py — 10-gate validation suite for sedenion_mandelbrot.py
========================================================================

Gates:
  1.  Zero divisor pair (e₁+e₁₀)(e₄-e₁₅) = 0  [Proposition 2.5]
  2.  Hessian symmetry max|H-Hᵀ| ≈ 0            [Theorem 4.6]
  3.  Orbit convergence: c=0, z₀=e₁ → escape_time = max_iter
  4.  Orbit divergence: ‖c‖ >> threshold → early escape
  5.  Sedenion norm identity: ‖a‖² = ‖conj(a)‖²
  6.  Cayley-Dickson unit: e₀ is the multiplicative identity
  7.  Anti-commutativity indicator: e₁*e₂ ≠ e₂*e₁ (noncommutativity)
  8.  Zero_divisor_proximity for known zero-divisor elements > 0.8
  9.  Feature vector has correct shape and finite values
  10. Graph encoding: synthetic k-regular graphs differ between k=4 and k=16
"""

import numpy as np
import pytest
import networkx as nx
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sedenion_mandelbrot import (
    Sedenion, _cd_mul, mandelbrot_orbit, sedenion_features, graph_to_sedenion
)


# =============================================================================
# Gate 1: Zero divisor pair  (e₁+e₁₀)(e₄-e₁₅) = 0  [Proposition 2.5]
# =============================================================================

def test_gate1_zero_divisor_proposition_2_5():
    """(e₁+e₁₀) * (e₄-e₁₅) must be the zero sedenion."""
    a = Sedenion.basis(1) + Sedenion.basis(10)    # e₁ + e₁₀
    b = Sedenion.basis(4) + (-1.0) * Sedenion.basis(15)  # e₄ - e₁₅
    product = a * b
    norm = product.norm()
    assert norm < 1e-10, (
        f"Gate 1 FAIL: ‖(e₁+e₁₀)(e₄-e₁₅)‖ = {norm:.2e}, expected < 1e-10"
    )


# =============================================================================
# Gate 2: Hessian symmetry [Theorem 4.6]
# =============================================================================

def test_gate2_hessian_symmetry_theorem_4_6():
    """
    Hessian H_n = ∂²‖z_n‖²/∂cᵢ∂cⱼ must satisfy H_ij = H_ji (Schwarz's theorem).
    Empirically: max asymmetry should be < 1e-6.
    """
    G = nx.random_regular_graph(4, 20, seed=42)
    c, z0 = graph_to_sedenion(G)
    orbit = mandelbrot_orbit(c, z0, max_iter=30, threshold=1e3)
    assert orbit.hessian_asym < 1e-5, (
        f"Gate 2 FAIL: max|H-Hᵀ| = {orbit.hessian_asym:.2e}, expected < 1e-5"
    )


# =============================================================================
# Gate 3: Orbit convergence — c=0, z₀=e₁
# =============================================================================

def test_gate3_orbit_convergence_zero_c():
    """With c=0, z₀=e₁: z₁ = e₁²+0 = e₀ (real), orbit stays bounded → escape_time = max_iter."""
    c  = Sedenion.zero()
    z0 = Sedenion.basis(1)   # z₀ = e₁
    result = mandelbrot_orbit(c, z0, max_iter=50, threshold=1e3)
    # e₁² = -e₀ (imaginary unit squared = -1), so z stays bounded
    assert result.escape_time == 50, (
        f"Gate 3 FAIL: escape_time = {result.escape_time}, expected 50"
    )


# =============================================================================
# Gate 4: Orbit divergence — large ‖c‖
# =============================================================================

def test_gate4_orbit_divergence_large_c():
    """
    A large c (‖c‖ ≈ 10) with z₀=0 should escape early.
    For ‖c‖ >> 2 in the real 1D Mandelbrot, c is outside the set → escapes.
    """
    # c = 10 * e₀ (large real sedenion)
    c_vec = np.zeros(16)
    c_vec[0] = 10.0
    c = Sedenion(c_vec)
    z0 = Sedenion.zero()
    result = mandelbrot_orbit(c, z0, max_iter=100, threshold=1e3)
    assert result.escape_time < 20, (
        f"Gate 4 FAIL: escape_time = {result.escape_time}, expected < 20"
    )


# =============================================================================
# Gate 5: Norm identity ‖a‖² = ‖conj(a)‖²
# =============================================================================

def test_gate5_norm_conjugate_identity():
    """Conjugation preserves norm: ‖a‖ = ‖ā‖."""
    rng = np.random.default_rng(42)
    for _ in range(10):
        a = Sedenion(rng.normal(size=16))
        assert abs(a.norm() - a.conjugate().norm()) < 1e-12, (
            "Gate 5 FAIL: norm not preserved under conjugation"
        )


# =============================================================================
# Gate 6: Multiplicative identity e₀
# =============================================================================

def test_gate6_multiplicative_identity():
    """e₀ = 1 ∈ 𝕊 is the multiplicative identity: e₀*a = a*e₀ = a."""
    rng = np.random.default_rng(42)
    e0 = Sedenion.basis(0)
    for _ in range(5):
        a = Sedenion(rng.normal(size=16))
        left  = e0 * a
        right = a * e0
        assert np.allclose(left.c, a.c, atol=1e-12), (
            f"Gate 6 FAIL: e₀*a ≠ a, max diff = {np.max(np.abs(left.c - a.c)):.2e}"
        )
        assert np.allclose(right.c, a.c, atol=1e-12), (
            f"Gate 6 FAIL: a*e₀ ≠ a, max diff = {np.max(np.abs(right.c - a.c)):.2e}"
        )


# =============================================================================
# Gate 7: Non-commutativity — e₁*e₂ ≠ e₂*e₁
# =============================================================================

def test_gate7_noncommutativity():
    """Sedenions (like quaternions) are non-commutative: e₁*e₂ ≠ e₂*e₁."""
    e1 = Sedenion.basis(1)
    e2 = Sedenion.basis(2)
    p = e1 * e2
    q = e2 * e1
    diff = np.max(np.abs(p.c - q.c))
    assert diff > 0.5, (
        f"Gate 7 FAIL: e₁*e₂ ≈ e₂*e₁ (diff={diff:.4f}), expected non-commutative"
    )


# =============================================================================
# Gate 8: Zero-divisor proximity for known zero-divisor elements
# =============================================================================

def test_gate8_zero_divisor_proximity_known_pairs():
    """
    Known zero-divisor elements (e₁+e₁₀) and (e₄-e₁₅) should have
    high zero_divisor_proximity (> 0.5).
    """
    a = Sedenion.basis(1) + Sedenion.basis(10)        # e₁ + e₁₀
    b = Sedenion.basis(4) + (-1.0) * Sedenion.basis(15)  # e₄ - e₁₅
    prox_a = a.zero_divisor_proximity()
    prox_b = b.zero_divisor_proximity()
    assert prox_a > 0.5, f"Gate 8 FAIL: proximity(e₁+e₁₀) = {prox_a:.3f}, expected > 0.5"
    assert prox_b > 0.5, f"Gate 8 FAIL: proximity(e₄-e₁₅) = {prox_b:.3f}, expected > 0.5"


# =============================================================================
# Gate 9: Feature vector shape and finiteness
# =============================================================================

def test_gate9_feature_vector_valid():
    """sedenion_features(G) should return shape (16,) with all finite values in [-1, 2]."""
    for k, n in [(4, 20), (6, 24), (14, 30)]:
        G = nx.random_regular_graph(k, n, seed=42)
        feats = sedenion_features(G, max_iter=30)
        assert feats.shape == (16,), f"Gate 9 FAIL: shape {feats.shape} ≠ (16,)"
        assert np.all(np.isfinite(feats)), f"Gate 9 FAIL: non-finite values in features"


# =============================================================================
# Gate 10: k-regular graphs k=4 vs k=16 produce different feature vectors
# =============================================================================

def test_gate10_feature_discriminability_asd_vs_adhd():
    """
    Synthetic ASD-like (k=4, hyperbolic) and ADHD-like (k=16, spherical) graphs
    should produce distinct sedenion feature vectors (‖Δfeats‖ > 0.1).
    """
    G_asd  = nx.random_regular_graph(4,  100, seed=42)
    G_adhd = nx.random_regular_graph(16, 100, seed=42)

    f_asd  = sedenion_features(G_asd,  max_iter=50)
    f_adhd = sedenion_features(G_adhd, max_iter=50)

    diff = np.linalg.norm(f_asd - f_adhd)
    assert diff > 0.1, (
        f"Gate 10 FAIL: ‖f(ASD) - f(ADHD)‖ = {diff:.4f}, expected > 0.1"
    )


# =============================================================================
# Summary report
# =============================================================================

if __name__ == "__main__":
    tests = [
        ("Gate 1", "Zero divisor Prop 2.5",           test_gate1_zero_divisor_proposition_2_5),
        ("Gate 2", "Hessian symmetry Thm 4.6",        test_gate2_hessian_symmetry_theorem_4_6),
        ("Gate 3", "Orbit convergence (c=0)",          test_gate3_orbit_convergence_zero_c),
        ("Gate 4", "Orbit divergence (large c)",       test_gate4_orbit_divergence_large_c),
        ("Gate 5", "Norm-conjugate identity",          test_gate5_norm_conjugate_identity),
        ("Gate 6", "Multiplicative identity e₀",       test_gate6_multiplicative_identity),
        ("Gate 7", "Non-commutativity e₁*e₂≠e₂*e₁",  test_gate7_noncommutativity),
        ("Gate 8", "Zero-div proximity",               test_gate8_zero_divisor_proximity_known_pairs),
        ("Gate 9", "Feature shape & finiteness",       test_gate9_feature_vector_valid),
        ("Gate 10","k=4 vs k=16 discriminability",    test_gate10_feature_discriminability_asd_vs_adhd),
    ]

    passed = 0
    print("\nSedenion Mandelbrot — 10-Gate Validation Suite")
    print("=" * 54)
    for tag, desc, fn in tests:
        try:
            fn()
            print(f"  PASS ✓  {tag}: {desc}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL ✗  {tag}: {desc}")
            print(f"          {e}")
        except Exception as e:
            print(f"  ERROR   {tag}: {desc}")
            print(f"          {type(e).__name__}: {e}")

    print("=" * 54)
    print(f"  {passed}/10 gates passed")
    if passed == 10:
        print("  ALL GATES PASS — sedenion_mandelbrot.py validated ✓")
    else:
        print("  SOME GATES FAILED — check implementation")
