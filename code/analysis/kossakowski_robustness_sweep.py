#!/usr/bin/env python3
"""Pilot 3c — hyperparameter robustness sweep for the Kossakowski geometric-CSD headline.

The n=1 positive-leaning headline (Pearson & hyperbolic kappa drop earlier than the scalar
variance/autocorrelation EWS on the same windows) must not hinge on a lucky hyperparameter choice.
Sweep WIN_DAYS x TAU x RIDGE (2x2x2 = 8 cells). No bootstrap (fast); the kappa "signal" is the first
window (sustained >=2) where kappa drops below baseline_mean - 2*sd, with sd = std of kappa ACROSS
the baseline (phase 1-2) windows. Scalar EWS signal = first sustained rise above baseline_mean+2*sd.

PRE-REGISTERED criterion: the headline = "BOTH kappa_pearson AND kappa_hyperbolic signal strictly
earlier than the earliest scalar EWS (var/ac1)" must hold in >= 6 of 8 cells. Else: honest negative.
(Partial-correlation kappa is NOT part of the headline — it already failed in the main analysis.)
"""

import json
from pathlib import Path
import numpy as np

import kossakowski_geometric_csd as K   # reuse loader + assoc/kappa core

OUT = Path(__file__).resolve().parents[2] / "results/unified"

WIN_GRID = [21, 28]
TAU_GRID = [0.05, 0.10]
RIDGE_GRID = [0.1, 0.2]


def kappa_series_for(rows, win_days, step_days=4):
    days = np.array([r["dayno"] for r in rows])
    d0, d1 = days.min(), days.max()
    series = []
    start = d0
    while start + win_days <= d1 + step_days:
        lo, hi = start, start + win_days
        idx = [i for i, dd in enumerate(days) if lo <= dd < hi]
        if len(idx) >= 20:
            W = np.array([rows[i]["z"] for i in idx])
            phases = [rows[i]["phase"] for i in idx]
            deps = [rows[i]["dep"] for i in idx if rows[i]["dep"] is not None]
            comp = np.array([np.dot([K.NEG_SIGN[m] for m in K.MOOD], rows[i]["z"]) for i in idx])
            ac1 = float(np.corrcoef(comp[:-1], comp[1:])[0, 1]) if len(comp) > 2 and np.var(comp) > 1e-9 else np.nan
            series.append({
                "mid": (lo + hi) / 2, "phase": int(max(set(phases), key=phases.count)),
                "dep": float(np.mean(deps)) if deps else None,
                "k_pearson": K.kappa_one(W, "pearson"),
                "k_hyperbolic": K.kappa_one(W, "hyperbolic"),
                "var": float(np.var(comp)), "ac1": ac1,
            })
        start += step_days
    return series


def first_sustained(mids, vals, thresh, direction):
    for i in range(len(vals) - 1):
        a, b = vals[i], vals[i + 1]
        if a is None or b is None or (isinstance(a, float) and np.isnan(a)) or (isinstance(b, float) and np.isnan(b)):
            continue
        if direction == "down" and a < thresh and b < thresh:
            return mids[i]
        if direction == "up" and a > thresh and b > thresh:
            return mids[i]
    return None


def main():
    rows = K.load(); K.standardize(rows)
    cells = []
    for win in WIN_GRID:
        for tau in TAU_GRID:
            for ridge in RIDGE_GRID:
                K.TAU = tau; K.RIDGE = ridge          # monkeypatch module globals
                s = kappa_series_for(rows, win)
                mids = [w["mid"] for w in s]
                base = [w for w in s if w["phase"] <= 2]
                dep_vals = [w["dep"] for w in s]
                base_dep = np.mean([w["dep"] for w in base if w["dep"] is not None])
                peak_dep = max(v for v in dep_vals if v is not None)
                mid_thresh = base_dep + 0.5 * (peak_dep - base_dep)
                onset = first_sustained(mids, dep_vals, mid_thresh, "up")

                def k_signal(key):
                    bm = np.mean([w[key] for w in base]); bsd = np.std([w[key] for w in base])
                    return first_sustained(mids, [w[key] for w in s], bm - 2 * max(bsd, 1e-4), "down")

                def e_signal(key):
                    bm = np.nanmean([w[key] for w in base]); bsd = np.nanstd([w[key] for w in base])
                    return first_sustained(mids, [w[key] for w in s], bm + 2 * max(bsd, 1e-4), "up")

                kp, kh = k_signal("k_pearson"), k_signal("k_hyperbolic")
                ev, ea = e_signal("var"), e_signal("ac1")
                scalars = [x for x in (ev, ea) if x is not None]
                earliest_scalar = min(scalars) if scalars else None
                # headline: both geometric signals exist AND both strictly earlier than earliest scalar
                holds = (kp is not None and kh is not None and earliest_scalar is not None
                         and kp < earliest_scalar and kh < earliest_scalar)
                cells.append({"win": win, "tau": tau, "ridge": ridge, "onset": onset,
                              "k_pearson": kp, "k_hyperbolic": kh, "ews_var": ev, "ews_ac1": ea,
                              "earliest_scalar": earliest_scalar, "headline_holds": bool(holds)})

    n_hold = sum(c["headline_holds"] for c in cells)
    print(f"{'win':>3} {'tau':>5} {'ridge':>5} | {'onset':>5} {'k_pear':>6} {'k_hyp':>6} {'evar':>5} {'eac1':>5} {'scalar':>6} | holds")
    for c in cells:
        f = lambda x: ("-" if x is None else f"{x:.0f}")
        print(f"{c['win']:>3} {c['tau']:>5} {c['ridge']:>5} | {f(c['onset']):>5} {f(c['k_pearson']):>6} "
              f"{f(c['k_hyperbolic']):>6} {f(c['ews_var']):>5} {f(c['ews_ac1']):>5} {f(c['earliest_scalar']):>6} | {c['headline_holds']}")
    verdict = "HARDENED" if n_hold >= 6 else "NOT ROBUST (honest negative)"
    print(f"\nheadline holds in {n_hold}/8 cells  ->  {verdict}  (pre-registered threshold: >=6/8)")

    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "kossakowski_robustness_sweep.json", "w") as f:
        json.dump({"grid": {"win": WIN_GRID, "tau": TAU_GRID, "ridge": RIDGE_GRID},
                  "criterion": "both kappa_pearson and kappa_hyperbolic signal earlier than earliest scalar EWS; >=6/8",
                  "n_hold": n_hold, "verdict": verdict, "cells": cells}, f, indent=2)
    print(f"wrote {OUT / 'kossakowski_robustness_sweep.json'}")


if __name__ == "__main__":
    main()
