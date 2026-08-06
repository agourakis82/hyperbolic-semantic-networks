#!/usr/bin/env python3
"""Pre-ictal vs interictal EEG network curvature — CHB-MIT chb01 (within-patient transition test).

The substrate that fixes every flaw of the Kossakowski pilot: a SPONTANEOUS, second-marked,
within-patient critical transition (epileptic seizure) with dense neural data and a fixed montage.

Per 30-s window of scalp EEG (23 bipolar channels, 256 Hz): build the channel connectivity network
(|Pearson| over the window), compute exact-OT Ollivier-Ricci mean curvature κ. This yields κ(t).
Compare:
  * INTERICTAL baseline (seizure-free files chb01_01, chb01_02)
  * PRE-ICTAL run-up (the 30 min before each seizure onset)
and test whether κ shifts/trends approaching the seizure — the curvature-as-critical-slowing-down
hypothesis on a hard ground-truth transition.

Within-patient, same montage, fixed 23 nodes → no node-count or cross-cohort confound. Density is
controlled per-window (the corr(κ,⟨k⟩) trap). Two-sided, pre-registered; honest-negative ready.
NOT a seizure-prediction claim — a within-patient curvature characterization on n=1 patient (chb01),
to be extended to more patients if the within-patient signal survives.
"""

import json
from pathlib import Path
import numpy as np
import pyedflib
from scipy.stats import mannwhitneyu, linregress

import kossakowski_geometric_csd as K

CHB = Path(__file__).resolve().parents[2] / "data/external/chbmit/chb01"
OUT = Path(__file__).resolve().parents[2] / "results/unified"

FS = 256
WIN_S = 30                  # window length (s)
PREICTAL_S = 1800           # 30 min pre-ictal horizon
SEIZURE = {"chb01_03": 2996, "chb01_04": 1467, "chb01_16": 1015, "chb01_18": 1720}
INTERICTAL = ["chb01_01", "chb01_02"]
SEED = 20260527


def read_edf(path):
    f = pyedflib.EdfReader(str(path))
    n = f.signals_in_file
    sigs = np.vstack([f.readSignal(i) for i in range(n)])   # (channels, samples)
    f.close()
    return sigs


def kappa_track(sigs, metric="pearson"):
    """κ per non-overlapping WIN_S window across the recording. Returns (t_centers, kappas, dens)."""
    win = WIN_S * FS
    nwin = sigs.shape[1] // win
    ts, ks, ds = [], [], []
    for w in range(nwin):
        seg = sigs[:, w * win:(w + 1) * win].T          # (samples, channels)
        sd = seg.std(0)
        if np.any(sd < 1e-6):
            continue
        Z = (seg - seg.mean(0)) / sd
        try:
            k = K.kappa_one(Z, metric)
        except Exception:
            continue
        if k is None or np.isnan(k):
            continue
        A = K.pearson_assoc(Z)
        dens = float((A >= K.TAU).sum() / (A.shape[0] * (A.shape[0] - 1)))
        ts.append((w + 0.5) * WIN_S); ks.append(k); ds.append(dens)
    return np.array(ts), np.array(ks), np.array(ds)


def main():
    K.TAU, K.ALPHA = 0.30, 0.5      # EEG correlations are high; stricter τ for a meaningful graph
    rng = np.random.default_rng(SEED)

    if not CHB.exists() or not list(CHB.glob("*.edf")):
        print(f"[BLOCKED] no EDF files in {CHB} yet"); return

    # interictal baseline κ
    inter = []
    for f in INTERICTAL:
        p = CHB / f"{f}.edf"
        if not p.exists():
            continue
        _, ks, ds = kappa_track(read_edf(p))
        inter.append((ks, ds))
        print(f"{f}: {len(ks)} windows, κ median={np.median(ks):.3f}")
    if not inter:
        print("[BLOCKED] no interictal files present"); return
    ki = np.concatenate([x[0] for x in inter]); di = np.concatenate([x[1] for x in inter])

    # pre-ictal κ per seizure file
    preictal_ks, preictal_ds, trends = [], [], []
    for f, onset in SEIZURE.items():
        p = CHB / f"{f}.edf"
        if not p.exists():
            continue
        ts, ks, ds = kappa_track(read_edf(p))
        pre = (ts >= onset - PREICTAL_S) & (ts < onset)        # 30 min pre-ictal, excludes ictal
        kp = ks[pre]; tp = ts[pre]; dp = ds[pre]
        if len(kp) < 5:
            continue
        preictal_ks.append(kp); preictal_ds.append(dp)
        # trend of κ vs time within the pre-ictal run-up (negative slope = κ dropping toward onset)
        sl = linregress(tp, kp)
        trends.append({"file": f, "onset": onset, "n_pre": len(kp),
                       "preictal_median": float(np.median(kp)), "slope_per_s": float(sl.slope),
                       "slope_p": float(sl.pvalue)})
        print(f"{f}: seizure@{onset}s, {len(kp)} pre-ictal windows, κ median={np.median(kp):.3f}, "
              f"trend slope={sl.slope:.2e}/s (p={sl.pvalue:.3f})")

    kp_all = np.concatenate(preictal_ks) if preictal_ks else np.array([])
    dp_all = np.concatenate(preictal_ds) if preictal_ds else np.array([])

    # TEST 1: pre-ictal vs interictal κ (two-sided)
    res = {}
    if len(kp_all) >= 5:
        U, pmw = mannwhitneyu(kp_all, ki, alternative="two-sided")
        rb = 1.0 - 2.0 * U / (len(kp_all) * len(ki))
        res["preictal_vs_interictal"] = {
            "n_pre": int(len(kp_all)), "n_inter": int(len(ki)),
            "med_pre": float(np.median(kp_all)), "med_inter": float(np.median(ki)),
            "rank_biserial": float(rb), "p": float(pmw),
            "sign": "pre<inter" if np.median(kp_all) < np.median(ki) else "pre>inter"}
        print(f"\nPRE-ICTAL vs INTERICTAL: med_pre={np.median(kp_all):.3f} med_inter={np.median(ki):.3f} "
              f"rank_bis={rb:+.3f} p={pmw:.4f} ({res['preictal_vs_interictal']['sign']})")

    # density confound check + CONTROL
    corr_kd = float(np.corrcoef(ki, di)[0, 1]) if len(ki) > 2 else float("nan")
    res["corr_kappa_density_interictal"] = corr_kd

    # (a) density-RESIDUALIZED test: regress κ on density over pooled windows, compare residuals.
    allk = np.concatenate([kp_all, ki]); alld = np.concatenate([dp_all, di])
    Amat = np.vstack([alld, np.ones_like(alld)]).T
    beta, *_ = np.linalg.lstsq(Amat, allk, rcond=None)
    resid = allk - Amat @ beta
    rp = resid[:len(kp_all)]; rqi = resid[len(kp_all):]
    Ur, pr = mannwhitneyu(rp, rqi, alternative="two-sided")
    res["density_residualized"] = {"p": float(pr),
                                   "med_resid_pre": float(np.median(rp)),
                                   "med_resid_inter": float(np.median(rqi))}
    # (b) density-MATCHED test: restrict to overlapping density band, compare κ
    lo = max(dp_all.min(), di.min()); hi = min(dp_all.max(), di.max())
    mp = kp_all[(dp_all >= lo) & (dp_all <= hi)]; mi = ki[(di >= lo) & (di <= hi)]
    if len(mp) >= 5 and len(mi) >= 5:
        Um, pm = mannwhitneyu(mp, mi, alternative="two-sided")
        res["density_matched"] = {"p": float(pm), "n_pre": int(len(mp)), "n_inter": int(len(mi)),
                                  "med_pre": float(np.median(mp)), "med_inter": float(np.median(mi)),
                                  "band": [float(lo), float(hi)]}
    else:
        res["density_matched"] = {"p": None, "note": "insufficient density overlap"}
    # (c) STRATIFIED density-matched test (the decisive control): bin density, within each bin draw
    # equal n from pre and inter so the density DISTRIBUTIONS match, then compare κ. Repeat, average p.
    bins = np.linspace(min(dp_all.min(), di.min()), max(dp_all.max(), di.max()), 9)
    pvals_strat, diffs = [], []
    for _ in range(50):
        pk, ik = [], []
        for b in range(len(bins) - 1):
            ppool = kp_all[(dp_all >= bins[b]) & (dp_all < bins[b + 1])]
            ipool = ki[(di >= bins[b]) & (di < bins[b + 1])]
            m = min(len(ppool), len(ipool))
            if m == 0:
                continue
            pk.extend(rng.choice(ppool, m, replace=False))
            ik.extend(rng.choice(ipool, m, replace=False))
        if len(pk) >= 10 and len(ik) >= 10:
            _, ps = mannwhitneyu(pk, ik, alternative="two-sided")
            pvals_strat.append(ps); diffs.append(np.median(pk) - np.median(ik))
    strat_p = float(np.median(pvals_strat)) if pvals_strat else None
    strat_diff = float(np.median(diffs)) if diffs else None
    res["density_stratified_matched"] = {"median_p": strat_p, "median_kappa_diff": strat_diff,
                                         "n_matched_total": int(len(pk)) if pvals_strat else 0}

    print(f"density-RESIDUALIZED pre vs inter: p={pr:.4f} (med_resid pre={np.median(rp):+.4f} inter={np.median(rqi):+.4f})")
    if strat_p is not None:
        print(f"density-STRATIFIED-MATCHED (decisive): median p={strat_p:.4f}, median κ-diff={strat_diff:+.4f} "
              f"(n≈{len(pk)}/bin-matched)")
    dm = res["density_matched"]
    if dm.get("p") is not None:
        print(f"density-MATCHED [{dm['band'][0]:.2f},{dm['band'][1]:.2f}] pre vs inter: "
              f"p={dm['p']:.4f} (med pre={dm['med_pre']:.3f} inter={dm['med_inter']:.3f}, n={dm['n_pre']}/{dm['n_inter']})")

    # TEST 2: consistent pre-ictal downward trend across seizures?
    slopes = [t["slope_per_s"] for t in trends]
    res["preictal_trends"] = trends
    res["n_seizures"] = len(trends)
    res["n_negative_slope"] = int(sum(1 for s in slopes if s < 0))
    print(f"\nTREND: {res['n_negative_slope']}/{len(slopes)} seizures show negative κ slope toward onset")
    print(f"density confound corr(κ,density) interictal = {corr_kd:.2f}")

    # honest verdict — the density CONTROLS decide, not the raw shift
    pv = res.get("preictal_vs_interictal", {})
    raw_sig = pv.get("p", 1.0) < 0.05
    # the STRATIFIED-matched test is the decisive density control (equates distributions);
    # residualized is the linear ANCOVA cross-check. Require BOTH to survive.
    resid_sig = res["density_residualized"]["p"] < 0.05
    strat_sig = (res["density_stratified_matched"]["median_p"] is not None
                 and res["density_stratified_matched"]["median_p"] < 0.05)
    survives_density = resid_sig and strat_sig
    consistent_trend = len(slopes) > 0 and res["n_negative_slope"] >= 0.75 * len(slopes)

    if raw_sig and survives_density and consistent_trend:
        verdict = "POSITIVE — pre-ictal κ shift survives density control AND trends toward onset; extend to more patients"
    elif raw_sig and survives_density:
        verdict = "PARTIAL — pre-ictal κ shift survives density control but no consistent onset trend (level shift, not slowing-down)"
    elif raw_sig and not survives_density:
        verdict = "DENSITY ARTIFACT — raw pre-ictal κ shift does NOT survive density control (pre-ictal synchronization, re-expressed as curvature)"
    else:
        verdict = "NULL (no pre-ictal κ shift on chb01)"
    res["verdict"] = verdict
    print(f"\nVERDICT (chb01, n=1 patient): {verdict}")

    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "chb01_preictal_curvature.json", "w") as f:
        json.dump({"params": {"fs": FS, "win_s": WIN_S, "preictal_s": PREICTAL_S, "tau": K.TAU},
                  "result": res}, f, indent=2)
    print(f"wrote {OUT / 'chb01_preictal_curvature.json'}")


if __name__ == "__main__":
    main()
