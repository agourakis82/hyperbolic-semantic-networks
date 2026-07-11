#!/usr/bin/env python3
"""Within-dataset affect-network curvature — Rowland2020 (the confound-clean design).

Fisher-vs-non-clinical (fisher_clinical_kappa.py) was CONFOUND-DOMINATED: node-count + cross-cohort
artifacts flipped the sign. This avoids both: ONE dataset, ONE protocol, the SAME 8 mood items, the
SAME node count — only group membership (and time) vary.

Rowland & Wenzel (2020): 125 subjects, between-subject arms group∈{1,2} (n=64 / n=61), 40 days × 6
beeps/day (240 scheduled), 8 mood items {happy,excited,relaxed,satisfied,angry,anxious,depressed,sad}
on 0–100. (group is constant within subject = between-subject design.)

TWO tests, both two-sided, density-controlled:
  A. BETWEEN-ARM: per-subject whole-series κ, group 1 vs group 2. The cleanest possible κ group
     comparison (no node-count, no cross-cohort confound).
  B. TEMPORAL (manipulated-transition analog): per-subject Δκ = κ(days 21–40) − κ(days 1–20); test
     whether Δκ differs between arms (group × time interaction on affect-network curvature).

Density control: the static work + Fisher both showed corr(κ, density) ≈ 0.7–0.9. We (i) report mean
density per group, and (ii) compare density-RESIDUALIZED κ (regress κ on density across subjects, test
residuals by group) — if the group effect vanishes after residualizing, it was density, not curvature.

Robustness sweep over (τ, ridge, metric). PRE-REGISTERED: a between-arm effect is "real" only if it is
same-sign & p<.05 in ≥6/8 sweep cells AND survives density-residualization. Else honest negative.
NOTE which group is the intervention is not assumed; tested two-sided.
"""

import json
from pathlib import Path
import numpy as np
import pyreadr
from scipy.stats import mannwhitneyu

import kossakowski_geometric_csd as K

DATA = Path(__file__).resolve().parents[2] / "data/external/emotion_timeseries/data_Rowland2020.RDS"
OUT = Path(__file__).resolve().parents[2] / "results/unified"
MOOD = ["happy", "excited", "relaxed", "satisfied", "angry", "anxious", "depressed", "sad"]
MIN_BEEPS = 40
SEED = 20260527


def load():
    return pyreadr.read_r(str(DATA))[None]


def subj_kappa(df, metric, day_lo=None, day_hi=None):
    """Per-subject κ + density + group, optionally restricted to a day range."""
    rows = []
    for sid, g in df.groupby("subj_id"):
        if day_lo is not None:
            g = g[(g["dayno"] >= day_lo) & (g["dayno"] <= day_hi)]
        sub = g[MOOD].dropna()
        if len(sub) < MIN_BEEPS:
            continue
        X = sub.to_numpy().astype(float)
        sd = X.std(0)
        if np.any(sd == 0):
            continue
        Z = (X - X.mean(0)) / sd
        try:
            k = K.kappa_one(Z, metric)
        except Exception:
            continue
        if k is None or np.isnan(k):
            continue
        A = K.pearson_assoc(Z)
        dens = float((A >= K.TAU).sum() / (A.shape[0] * (A.shape[0] - 1)))
        rows.append((int(g["group"].iloc[0]), k, dens))
    return rows


def residualize(ks, dens):
    """Return κ residuals after linear regression on density."""
    ks = np.asarray(ks); dens = np.asarray(dens)
    Amat = np.vstack([dens, np.ones_like(dens)]).T
    beta, *_ = np.linalg.lstsq(Amat, ks, rcond=None)
    return ks - Amat @ beta


def between_arm(df, metric):
    rows = subj_kappa(df, metric)
    g1 = [r for r in rows if r[0] == 1]; g2 = [r for r in rows if r[0] == 2]
    if len(g1) < 5 or len(g2) < 5:
        return None
    k1 = np.array([r[1] for r in g1]); k2 = np.array([r[1] for r in g2])
    U, p = mannwhitneyu(k1, k2, alternative="two-sided")
    rb = 1.0 - 2.0 * U / (len(k1) * len(k2))
    # density-residualized
    allk = np.array([r[1] for r in rows]); alld = np.array([r[2] for r in rows])
    allg = np.array([r[0] for r in rows])
    resid = residualize(allk, alld)
    r1, r2 = resid[allg == 1], resid[allg == 2]
    Ur, pr = mannwhitneyu(r1, r2, alternative="two-sided")
    return {"n1": len(k1), "n2": len(k2), "med1": float(np.median(k1)), "med2": float(np.median(k2)),
            "dens1": float(np.median([r[2] for r in g1])), "dens2": float(np.median([r[2] for r in g2])),
            "p": float(p), "rank_biserial": float(rb),
            "sign": "g1<g2" if np.median(k1) < np.median(k2) else "g1>g2",
            "p_resid_density": float(pr), "corr_k_dens": float(np.corrcoef(allk, alld)[0, 1])}


def temporal(df, metric):
    early = {r[0:1][0]: [] for r in []}  # placeholder
    e = subj_kappa(df, metric, 1, 20)
    l = subj_kappa(df, metric, 21, 40)
    # align by subject: rebuild with subject ids
    return e, l


def temporal_delta(df, metric):
    em, lm = {}, {}
    for sid, g in df.groupby("subj_id"):
        grp = int(g["group"].iloc[0])
        for tag, lo, hi, store in (("e", 1, 20, em), ("l", 21, 40, lm)):
            sub = g[(g["dayno"] >= lo) & (g["dayno"] <= hi)][MOOD].dropna()
            if len(sub) < MIN_BEEPS:
                continue
            X = sub.to_numpy().astype(float); sd = X.std(0)
            if np.any(sd == 0):
                continue
            Z = (X - X.mean(0)) / sd
            try:
                k = K.kappa_one(Z, metric)
            except Exception:
                continue
            if k is not None and not np.isnan(k):
                store[sid] = (grp, k)
    deltas = {sid: (em[sid][0], lm[sid][1] - em[sid][1]) for sid in em if sid in lm}
    d1 = [d for g, d in deltas.values() if g == 1]
    d2 = [d for g, d in deltas.values() if g == 2]
    if len(d1) < 5 or len(d2) < 5:
        return None
    U, p = mannwhitneyu(d1, d2, alternative="two-sided")
    rb = 1.0 - 2.0 * U / (len(d1) * len(d2))
    return {"n1": len(d1), "n2": len(d2), "med_dk1": float(np.median(d1)), "med_dk2": float(np.median(d2)),
            "p": float(p), "rank_biserial": float(rb)}


def main():
    df = load()
    print("Rowland2020 within-dataset (same 8 items, same protocol; arms g1 n=64 / g2 n=61)\n")

    K.TAU, K.RIDGE, K.ALPHA = 0.10, 0.2, 0.5
    print("=== TEST A: between-arm per-subject κ (default τ=.10 ridge=.2) ===")
    print(f"{'metric':>11} {'n1':>3} {'n2':>3} {'med1':>7} {'med2':>7} {'rb':>7} {'p':>8} {'sign':>6} "
          f"{'dens1':>6} {'dens2':>6} {'p_resid':>8} {'corr_kd':>8}")
    headA = {}
    for m in K.METRICS:
        r = between_arm(df, m); headA[m] = r
        if r:
            print(f"{m:>11} {r['n1']:>3} {r['n2']:>3} {r['med1']:>7.3f} {r['med2']:>7.3f} {r['rank_biserial']:>7.3f} "
                  f"{r['p']:>8.4f} {r['sign']:>6} {r['dens1']:>6.2f} {r['dens2']:>6.2f} "
                  f"{r['p_resid_density']:>8.4f} {r['corr_k_dens']:>8.2f}")

    print("\n=== TEST B: temporal Δκ (late−early) by arm — manipulated-transition analog ===")
    headB = {}
    for m in K.METRICS:
        r = temporal_delta(df, m); headB[m] = r
        if r:
            print(f"{m:>11} n1={r['n1']} n2={r['n2']} med_Δκ1={r['med_dk1']:+.4f} med_Δκ2={r['med_dk2']:+.4f} "
                  f"rb={r['rank_biserial']:+.3f} p={r['p']:.4f}")

    print("\n=== ROBUSTNESS SWEEP (between-arm, pearson + hyperbolic) ===")
    cells = []
    for tau in (0.05, 0.10):
        for ridge in (0.1, 0.2):
            K.TAU, K.RIDGE = tau, ridge
            for m in ("pearson", "hyperbolic"):
                r = between_arm(df, m)
                if not r:
                    continue
                sig = r["p"] < 0.05
                cells.append({"tau": tau, "ridge": ridge, "metric": m, **r, "sig": bool(sig)})
                print(f"  τ={tau} ridge={ridge} {m:>10}: med1={r['med1']:.3f} med2={r['med2']:.3f} "
                      f"rb={r['rank_biserial']:+.3f} p={r['p']:.4f} {r['sign']} {'*' if sig else ''}")

    pcells = [c for c in cells if c["metric"] == "pearson"]
    signs = [c["sign"] for c in pcells]
    dom = max(set(signs), key=signs.count) if pcells else None
    n_hold = sum(1 for c in pcells if c["sign"] == dom and c["sig"])
    # density survival on the default pearson cell
    dp = headA["pearson"]
    dens_survives = dp and dp["p_resid_density"] < 0.05 and dp["sign"] != "n/a"
    if dom and n_hold >= 6 and dens_survives:
        verdict = "ROBUST (survives sweep + density-residualization)"
    elif dom and n_hold >= 6 and not dens_survives:
        verdict = "DENSITY-CONFOUNDED (sweep-robust but vanishes after density-residualization)"
    else:
        verdict = "NOT ROBUST (honest negative)"
    print(f"\nbetween-arm pearson: dominant sign={dom}, sig in {n_hold}/8; "
          f"density-residualized p={dp['p_resid_density']:.4f} (survives={dens_survives})")
    print(f"SCIENTIFIC VERDICT: {verdict}")

    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "rowland_within_kappa.json", "w") as f:
        json.dump({"test_A_between_arm": headA, "test_B_temporal_delta": headB,
                   "sweep_cells": cells, "verdict": verdict, "n_hold": n_hold,
                   "density_residualized_survives": bool(dens_survives)}, f, indent=2)
    print(f"\nwrote {OUT / 'rowland_within_kappa.json'}")


if __name__ == "__main__":
    main()
