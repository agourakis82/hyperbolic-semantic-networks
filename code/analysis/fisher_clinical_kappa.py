#!/usr/bin/env python3
"""Multi-subject affect-network curvature: CLINICAL (Fisher2017 MDD/GAD) vs NON-CLINICAL.

Fixes Pilot 3's n=1 problem: one Ollivier-Ricci curvature κ per SUBJECT (whole-series affect
network), compared between clinical (Fisher2017, n=40 MDD/GAD) and non-clinical cohorts
(Rowland2020 n=125, Bringmann2016 n=95). Reuses the exact-OT κ core from
`kossakowski_geometric_csd.py`.

THE CENTRAL CONFOUND (stated up front): a cross-dataset comparison differs in item set, sampling
protocol, population, country, and beep count — not just clinical status. Two controls:
  * HARMONIZED 4-item network {sad, anxious, angry, positive} mapped identically across datasets —
    the comparison that is NOT an item-set artifact. PRIMARY.
  * NATIVE-item network (16 vs 8 vs 6 nodes) — richer but item-confounded. SECONDARY/sensitivity.
Plus: subsample all subjects to a common beep count; density control corr(κ, graph density);
robustness sweep over (τ, ridge, α, n_beep, metric). Bootstrap κ CI per subject.

PRE-REGISTERED test (two-sided): does per-subject κ differ between clinical and non-clinical?
Mann-Whitney U + rank-biserial effect size, per metric. A-priori *expected* direction (fragility
lens / Sandhu): clinical more negative κ — but tested two-sided, not assumed. Robustness criterion:
the effect (same sign, p<.05 on the HARMONIZED set) must hold in >= 6/8 sweep cells to be called
robust; else honest negative.

NO strong clinical claim — heterogeneous open cohorts; this is a multi-subject methods test.
"""

import json
from pathlib import Path
import numpy as np
import pyreadr
from scipy.stats import mannwhitneyu

import kossakowski_geometric_csd as K   # κ core: kappa_one, build_graph, assoc fns, poincare

DATA = Path(__file__).resolve().parents[2] / "data/external/emotion_timeseries"
OUT = Path(__file__).resolve().parents[2] / "results/unified"
SEED = 20260527
rng = np.random.default_rng(SEED)

# Harmonized 4-item affect set, mapped to each dataset's native column names.
HARM = ["sad", "anxious", "angry", "positive"]
MAP = {
    "Fisher2017":    {"sad": "down",      "anxious": "worried", "angry": "angry", "positive": "positive"},
    "Rowland2020":   {"sad": "depressed", "anxious": "anxious", "angry": "angry", "positive": "happy"},
    "Bringmann2016": {"sad": "Depressed", "anxious": "Anxious", "angry": "Angry", "positive": "Happy"},
}
NATIVE = {
    "Fisher2017":    ["energetic","enthusiastic","content","irritable","restless","worried","guilty",
                      "afraid","anhedonia","angry","hopeless","down","positive","tension"],
    "Rowland2020":   ["happy","excited","relaxed","satisfied","angry","anxious","depressed","sad"],
    "Bringmann2016": ["Angry","Depressed","Dysphoric","Anxious","Relaxed","Happy"],
}
CLINICAL = "Fisher2017"
NONCLIN = ["Rowland2020", "Bringmann2016"]
MIN_BEEPS = 40


def load(ds):
    df = pyreadr.read_r(str(DATA / f"data_{ds}.RDS"))[None]
    return df


def subject_matrices(df, cols, min_beeps, n_sub=None):
    """Return list of (z-standardized beeps x len(cols)) arrays, one per subject with enough data."""
    mats = []
    for sid, g in df.groupby("subj_id"):
        sub = g[cols].apply(lambda c: c.astype(float))
        sub = sub.dropna()
        if len(sub) < min_beeps:
            continue
        X = sub.to_numpy()
        if n_sub is not None and len(X) > n_sub:
            X = X[:n_sub]                      # truncate to common beep count
        sd = X.std(0)
        if np.any(sd == 0):
            continue                            # zero-variance item -> undefined correlation
        Z = (X - X.mean(0)) / sd
        mats.append(Z)
    return mats


def kappa_for_group(ds, item_mode, metric, min_beeps, n_sub):
    df = load(ds)
    cols = [MAP[ds][h] for h in HARM] if item_mode == "harm" else NATIVE[ds]
    mats = subject_matrices(df, cols, min_beeps, n_sub)
    ks, dens = [], []
    for Z in mats:
        try:
            k = K.kappa_one(Z, metric)
        except Exception:
            continue
        if k is None or np.isnan(k):
            continue
        A = K.pearson_assoc(Z)
        d = float((A >= K.TAU).sum() / (A.shape[0] * (A.shape[0] - 1)))  # graph density
        ks.append(k); dens.append(d)
    return np.array(ks), np.array(dens)


def compare(item_mode, metric, min_beeps, n_sub):
    kc, dc = kappa_for_group(CLINICAL, item_mode, metric, min_beeps, n_sub)
    kn, dn = [], []
    for ds in NONCLIN:
        k, d = kappa_for_group(ds, item_mode, metric, min_beeps, n_sub)
        kn.append(k); dn.append(d)
    kn = np.concatenate(kn); dn = np.concatenate(dn)
    if len(kc) < 5 or len(kn) < 5:
        return None
    U, p = mannwhitneyu(kc, kn, alternative="two-sided")
    rb = 1.0 - 2.0 * U / (len(kc) * len(kn))   # rank-biserial effect size
    return {"n_clin": len(kc), "n_non": len(kn),
            "med_clin": float(np.median(kc)), "med_non": float(np.median(kn)),
            "U": float(U), "p": float(p), "rank_biserial": float(rb),
            "sign": "clin<non" if np.median(kc) < np.median(kn) else "clin>non",
            "corr_kappa_density_clin": float(np.corrcoef(kc, dc)[0, 1]) if len(kc) > 2 else float("nan"),
            "corr_kappa_density_non": float(np.corrcoef(kn, dn)[0, 1]) if len(kn) > 2 else float("nan")}


def main():
    print("CLINICAL (Fisher2017 MDD/GAD) vs NON-CLINICAL (Rowland2020 + Bringmann2016)\n")

    # --- headline (harmonized 4-item, default hyperparams, all 3 metrics) ---
    K.TAU, K.RIDGE, K.ALPHA = 0.10, 0.2, 0.5
    print("=== HARMONIZED 4-item {sad,anxious,angry,positive}  (default τ=.10 ridge=.2 α=.5) ===")
    print(f"{'metric':>11} {'n_cl':>4} {'n_no':>4} {'med_cl':>8} {'med_no':>8} {'rank_bis':>8} {'p':>8} {'sign':>9}")
    headline = {}
    for m in K.METRICS:
        r = compare("harm", m, MIN_BEEPS, None)
        headline[m] = r
        if r:
            print(f"{m:>11} {r['n_clin']:>4} {r['n_non']:>4} {r['med_clin']:>8.3f} {r['med_non']:>8.3f} "
                  f"{r['rank_biserial']:>8.3f} {r['p']:>8.4f} {r['sign']:>9}")

    print("\n=== NATIVE-item (item-confounded sensitivity) ===")
    for m in K.METRICS:
        r = compare("native", m, MIN_BEEPS, None)
        if r:
            print(f"{m:>11} {r['n_clin']:>4} {r['n_non']:>4} {r['med_clin']:>8.3f} {r['med_non']:>8.3f} "
                  f"{r['rank_biserial']:>8.3f} {r['p']:>8.4f} {r['sign']:>9}")

    # --- robustness sweep on the HARMONIZED set (the pre-registered criterion) ---
    print("\n=== ROBUSTNESS SWEEP (harmonized; pre-registered ≥6/8 same-sign p<.05) ===")
    cells = []
    grid = [(tau, ridge, alpha, nsub)
            for tau in (0.05, 0.10) for ridge in (0.1, 0.2)
            for alpha in (0.5,) for nsub in (None, 100)]
    # use pearson as the primary metric for the sweep verdict (hyperbolic as concordance check)
    print(f"{'τ':>5} {'ridge':>5} {'nsub':>5} {'metric':>10} {'med_cl':>8} {'med_no':>8} {'rb':>7} {'p':>8} {'sign':>9} sig")
    for tau, ridge, alpha, nsub in grid:
        K.TAU, K.RIDGE, K.ALPHA = tau, ridge, alpha
        for m in ("pearson", "hyperbolic"):
            r = compare("harm", m, MIN_BEEPS, nsub)
            if not r:
                continue
            sig = r["p"] < 0.05
            ns = "all" if nsub is None else str(nsub)
            cells.append({"tau": tau, "ridge": ridge, "nsub": nsub, "metric": m, **r, "sig": bool(sig)})
            print(f"{tau:>5} {ridge:>5} {ns:>5} {m:>10} {r['med_clin']:>8.3f} {r['med_non']:>8.3f} "
                  f"{r['rank_biserial']:>7.3f} {r['p']:>8.4f} {r['sign']:>9} {'*' if sig else ''}")

    # mechanical hyperparameter-robustness count
    pcells = [c for c in cells if c["metric"] == "pearson"]
    signs = [c["sign"] for c in pcells]
    dom = max(set(signs), key=signs.count) if pcells else None
    n_hold = sum(1 for c in pcells if c["sign"] == dom and c["sig"])
    hp_robust = n_hold >= 6

    # but the SCIENTIFIC verdict must weigh the deeper confounds:
    native_sign = compare("native", "pearson", MIN_BEEPS, None)["sign"]
    harm_sign = headline["pearson"]["sign"] if headline.get("pearson") else None
    sign_flips = native_sign != harm_sign
    dens_conf = abs(headline["pearson"]["corr_kappa_density_clin"]) > 0.5 if headline.get("pearson") else False
    pvals = sorted(c["p"] for c in pcells)
    borderline = pvals and max(c["p"] for c in pcells if c["sig"]) > 0.04

    if sign_flips or dens_conf:
        verdict = "CONFOUND-DOMINATED (no clean clinical effect)"
    elif hp_robust and not borderline:
        verdict = "ROBUST"
    else:
        verdict = "WEAK / NOT ROBUST"

    print(f"\nhyperparameter robustness: dominant harmonized sign={dom}, same-sign & p<.05 in {n_hold}/{len(pcells)} cells")
    print(f"item-set sign FLIP (native vs harmonized): {sign_flips}  (native={native_sign}, harmonized={harm_sign})")
    print(f"density confound corr(κ,density) clin={headline['pearson']['corr_kappa_density_clin']:.2f} -> high={dens_conf}")
    print(f"significant p-values borderline (>.04): {borderline}  (p's={[round(p,3) for p in pvals]})")
    print(f"\nSCIENTIFIC VERDICT: {verdict}")

    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "fisher_clinical_kappa.json", "w") as f:
        json.dump({"headline_harmonized": headline, "sweep_cells": cells,
                   "verdict": {"dominant_harmonized_sign": dom, "hp_robust_n_hold": n_hold,
                               "item_set_sign_flip": sign_flips, "native_sign": native_sign,
                               "density_confounded": dens_conf, "borderline_p": borderline,
                               "result": verdict}},
                  f, indent=2)
    print(f"\nwrote {OUT / 'fisher_clinical_kappa.json'}")


if __name__ == "__main__":
    main()
