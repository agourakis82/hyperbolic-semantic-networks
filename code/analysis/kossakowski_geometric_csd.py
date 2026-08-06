#!/usr/bin/env python3
"""Pilot 3 — Geometric Critical Slowing Down on REAL ESM data (Kossakowski 2017).

Single-case MDD tapering study: 1476 momentary measurements, 239 days, 12 mood items,
5 design phases (3 = gradual dose reduction = the perturbation). Tests whether the
Ollivier-Ricci curvature of the time-varying momentary-affect network carries an
early-warning signal for the depressive transition, head-to-head with the classical
scalar CSD indicators (variance + lag-1 autocorrelation).

PRE-REGISTERED (per user decision 2026-05-27): compute kappa(t) under THREE edge metrics
and require the headline pattern to hold across all three:
  A. partial correlation   d = 1 - |partial r|   (ridge-regularized precision; field standard)
  B. Pearson correlation   d = 1 - |r|
  C. hyperbolic embedding  Poincare-disk geodesic distance of an MDS embedding of (1-|r|)

Uncertainty: BOOTSTRAP over beeps within each window (captures network-estimation +
sampling noise jointly) — the honest real-data analog of the GUM-through-Sinkhorn
propagation validated on the 2x2 synthetic case (examples/semantic_orc/epistemic_sinkhorn_orc.sio).

This file: Stage P3a — loader, windowing, kappa(t) under the 3 metrics, aligned to phase
and the weekly `dep` score. (Bootstrap gate + EWS lead-time comparison: P3b.)

NO clinical claim. n=1 single case; this is a methods pilot on the canonical CSD dataset.
"""

import csv
import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np
import networkx as nx
import ot

DATA = Path(__file__).resolve().parents[2] / "data/external/kossakowski_csd/ESMdata/ESMdata.csv"
OUT = Path(__file__).resolve().parents[2] / "results/unified"

MOOD = ["mood_relaxed", "mood_down", "mood_irritat", "mood_satisfi", "mood_lonely",
        "mood_anxious", "mood_enthus", "mood_suspic", "mood_cheerf", "mood_guilty",
        "mood_doubt", "mood_strong"]
# valence sign for building a "negative affect" composite (CSD signal); +1 = negative pole
NEG_SIGN = {"mood_relaxed": -1, "mood_down": +1, "mood_irritat": +1, "mood_satisfi": -1,
            "mood_lonely": +1, "mood_anxious": +1, "mood_enthus": -1, "mood_suspic": +1,
            "mood_cheerf": -1, "mood_guilty": +1, "mood_doubt": +1, "mood_strong": -1}

ALPHA = 0.5          # lazy random-walk laziness
WIN_DAYS = 28        # sliding window width (days) — matches CSD moving-window literature
STEP_DAYS = 4        # window step
RIDGE = 0.2          # ridge fraction for partial-correlation precision regularization
TAU = 0.10           # edge inclusion threshold on |association|
SEED = 20260527


def _parse_date(s):
    return datetime.strptime(s.strip(), "%d/%m/%y")


def load():
    # NB: the `dayno` column is day-of-year and RESETS across the 2012->2013 boundary;
    # the true chronology is the `date` field (file order is monotonic in date). Use a
    # global day offset from the first date as the time axis.
    rows = []
    with open(DATA, newline="") as f:
        for r in csv.DictReader(f):
            try:
                date = _parse_date(r["date"]); phase = int(r["phase"])
            except (ValueError, KeyError):
                continue
            mood = []
            ok = True
            for m in MOOD:
                v = r[m].strip()
                if v == "" or v.upper() == "NA":
                    ok = False; break
                mood.append(float(v))
            if not ok:
                continue
            dep = r["dep"].strip()
            dep = float(dep) if dep not in ("", "NA") else None
            rows.append({"date": date, "phase": phase, "mood": np.array(mood), "dep": dep})
    rows.sort(key=lambda x: x["date"])
    origin = rows[0]["date"]
    for r in rows:
        r["dayno"] = (r["date"] - origin).days
    return rows


def standardize(rows):
    X = np.array([r["mood"] for r in rows])          # (T, 12)
    mu = X.mean(0); sd = X.std(0); sd[sd == 0] = 1.0
    Z = (X - mu) / sd
    for i, r in enumerate(rows):
        r["z"] = Z[i]
    return Z


# ---- association matrices ----------------------------------------------------

def pearson_assoc(W):
    C = np.corrcoef(W.T)
    np.fill_diagonal(C, 0.0)
    return np.abs(np.nan_to_num(C))


def partial_assoc(W):
    cov = np.cov(W.T)
    ridge = RIDGE * np.trace(cov) / cov.shape[0]
    prec = np.linalg.inv(cov + ridge * np.eye(cov.shape[0]))
    d = np.sqrt(np.outer(np.diag(prec), np.diag(prec)))
    pc = -prec / d
    np.fill_diagonal(pc, 0.0)
    return np.abs(np.nan_to_num(pc))


# ---- graph from association + distances --------------------------------------

def build_graph(assoc):
    """Weighted graph; edge length = 1-|assoc|; keep edges >= TAU, ensure connectivity."""
    n = assoc.shape[0]
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if assoc[i, j] >= TAU:
                g.add_edge(i, j, w=assoc[i, j], d=1.0 - assoc[i, j])
    # connect components via strongest available cross-edges (so shortest paths exist)
    while nx.number_connected_components(g) > 1:
        comps = list(nx.connected_components(g))
        best = None
        for a in comps[0]:
            for j in range(n):
                if j not in comps[0] and assoc[a, j] > 0:
                    if best is None or assoc[a, j] > best[2]:
                        best = (a, j, assoc[a, j])
        if best is None:
            break
        a, j, w = best
        g.add_edge(a, j, w=max(w, 1e-3), d=1.0 - max(w, 1e-3))
    return g


def poincare_metric(assoc):
    """Embed dissimilarity (1-|assoc|) into the Poincare disk via classical MDS->2D,
    radial-map into the disk, return pairwise geodesic-distance matrix."""
    n = assoc.shape[0]
    D = 1.0 - assoc
    np.fill_diagonal(D, 0.0)
    # classical MDS to 2D
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J
    vals, vecs = np.linalg.eigh(B)
    idx = np.argsort(vals)[::-1][:2]
    L = np.sqrt(np.clip(vals[idx], 0, None))
    Y = vecs[:, idx] * L                       # (n,2) Euclidean coords
    # radial map into disk: scale so max radius -> 0.9
    r = np.linalg.norm(Y, axis=1)
    rmax = r.max() if r.max() > 0 else 1.0
    Y = Y * (0.9 / rmax)
    # Poincare geodesic distances
    M = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            u, v = Y[i], Y[j]
            num = np.sum((u - v) ** 2)
            den = (1 - np.sum(u ** 2)) * (1 - np.sum(v ** 2))
            dd = math.acosh(1 + 2 * num / max(den, 1e-9))
            M[i, j] = M[j, i] = dd
    return M


# ---- Ollivier-Ricci curvature ------------------------------------------------

def lazy_measure(g, x):
    nbrs = list(g.neighbors(x))
    m = {x: ALPHA}
    if nbrs:
        wsum = sum(g[x][z]["w"] for z in nbrs)
        for z in nbrs:
            p = (1.0 - ALPHA) * (g[x][z]["w"] / wsum if wsum > 0 else 1.0 / len(nbrs))
            m[z] = m.get(z, 0.0) + p
    return m


def mean_kappa_graph(g):
    """LLY-ORC with weighted shortest-path distances (metrics A,B)."""
    dist = dict(nx.all_pairs_dijkstra_path_length(g, weight="d"))
    ks = []
    for u, v in g.edges():
        mu, nu = lazy_measure(g, u), lazy_measure(g, v)
        sn, tn = list(mu), list(nu)
        a = np.array([mu[s] for s in sn]); b = np.array([nu[t] for t in tn])
        M = np.array([[dist[s].get(t, len(g)) for t in tn] for s in sn], float)
        duv = g[u][v]["d"]
        if duv <= 0:
            continue
        ks.append(1.0 - ot.emd2(a, b, M) / duv)
    return float(np.mean(ks)) if ks else float("nan")


def mean_kappa_poincare(g, Mp):
    """LLY-ORC using the Poincare geodesic distance matrix Mp as the metric."""
    ks = []
    for u, v in g.edges():
        mu, nu = lazy_measure(g, u), lazy_measure(g, v)
        sn, tn = list(mu), list(nu)
        a = np.array([mu[s] for s in sn]); b = np.array([nu[t] for t in tn])
        M = np.array([[Mp[s, t] for t in tn] for s in sn], float)
        duv = Mp[u, v]
        if duv <= 0:
            continue
        ks.append(1.0 - ot.emd2(a, b, M) / duv)
    return float(np.mean(ks)) if ks else float("nan")


def kappa_one(W, name):
    if name == "partial":
        return mean_kappa_graph(build_graph(partial_assoc(W)))
    if name == "pearson":
        return mean_kappa_graph(build_graph(pearson_assoc(W)))
    # hyperbolic: topology from Pearson, metric from Poincare embedding
    A = pearson_assoc(W)
    return mean_kappa_poincare(build_graph(A), poincare_metric(A))


METRICS = ["partial", "pearson", "hyperbolic"]


def kappa_all_metrics(W):
    return {m: kappa_one(W, m) for m in METRICS}


def bootstrap_kappa(W, name, B, rng):
    """Beep-bootstrap (resample rows with replacement) -> (mean, std) of kappa.
    Captures network-estimation + sampling noise jointly — the real-data analog of
    GUM-through-Sinkhorn. Returns NaNs filtered."""
    n = W.shape[0]
    vals = []
    for _ in range(B):
        idx = rng.integers(0, n, size=n)
        try:
            k = kappa_one(W[idx], name)
            if not math.isnan(k):
                vals.append(k)
        except Exception:
            continue
    if len(vals) < 5:
        return float("nan"), float("nan")
    return float(np.mean(vals)), float(np.std(vals))


def rolling_ews(rows, idx_by_window):
    """Classical CSD on the negative-affect composite: per window, variance and lag-1
    autocorrelation of the composite beep series within that window."""
    comp = np.array([np.dot([NEG_SIGN[m] for m in MOOD], r["z"]) for r in rows])
    out = []
    for idx in idx_by_window:
        x = comp[idx]
        v = float(np.var(x))
        if len(x) > 2 and v > 1e-9:
            ac1 = float(np.corrcoef(x[:-1], x[1:])[0, 1])
        else:
            ac1 = float("nan")
        out.append({"var": v, "ac1": ac1})
    return out


def first_cross(mids, vals, baseline, sd, direction, k=2.0):
    """First window-mid where vals cross baseline by k*sd in `direction` ('down'/'up')
    and STAY crossed for >=2 consecutive windows. Returns mid day or None."""
    n = len(vals)
    for i in range(n - 1):
        if any(math.isnan(v) for v in (vals[i], vals[i + 1])):
            continue
        if direction == "down":
            c = vals[i] < baseline - k * sd and vals[i + 1] < baseline - k * sd
        else:
            c = vals[i] > baseline + k * sd and vals[i + 1] > baseline + k * sd
        if c:
            return mids[i]
    return None


def main():
    rng = np.random.default_rng(SEED)
    B = 120
    rows = load()
    standardize(rows)
    days = np.array([r["dayno"] for r in rows])
    d0, d1 = days.min(), days.max()
    print(f"loaded {len(rows)} beeps over days {d0:.0f}..{d1:.0f}  (B={B} bootstrap)")

    idx_by_window = []
    starts = []
    start = d0
    while start + WIN_DAYS <= d1 + STEP_DAYS:
        lo, hi = start, start + WIN_DAYS
        idx = [i for i, dd in enumerate(days) if lo <= dd < hi]
        if len(idx) >= 20:
            idx_by_window.append(idx); starts.append(lo)
        start += STEP_DAYS

    ews = rolling_ews(rows, idx_by_window)
    series = []
    for w, idx in enumerate(idx_by_window):
        lo = starts[w]; hi = lo + WIN_DAYS
        W = np.array([rows[i]["z"] for i in idx])
        ka = kappa_all_metrics(W)
        boot = {m: bootstrap_kappa(W, m, B, rng) for m in METRICS}
        phases = [rows[i]["phase"] for i in idx]
        deps = [rows[i]["dep"] for i in idx if rows[i]["dep"] is not None]
        rec = {
            "win_mid": float((lo + hi) / 2), "n_beeps": len(idx),
            "phase_mode": int(max(set(phases), key=phases.count)),
            "dep_mean": float(np.mean(deps)) if deps else None,
            "ews_var": ews[w]["var"], "ews_ac1": ews[w]["ac1"],
        }
        for m in METRICS:
            rec[f"kappa_{m}"] = ka[m]
            rec[f"kappa_{m}_boot_mean"] = boot[m][0]
            rec[f"kappa_{m}_boot_sd"] = boot[m][1]
        series.append(rec)

    mids = [s["win_mid"] for s in series]
    phase_mode = [s["phase_mode"] for s in series]

    print(f"\n{len(series)} windows (W={WIN_DAYS}d, step={STEP_DAYS}d)")
    hdr = f"{'mid':>4} {'ph':>2} {'dep':>5}  {'k_part':>7}{'±sd':>6}  {'k_pear':>7}{'±sd':>6}  {'k_hyp':>7}{'±sd':>6}  {'var':>5} {'ac1':>5}"
    print(hdr)
    for s in series:
        dep = f"{s['dep_mean']:.2f}" if s['dep_mean'] is not None else "  -  "
        print(f"{s['win_mid']:4.0f} {s['phase_mode']:2d} {dep:>5}  "
              f"{s['kappa_partial']:7.3f}{s['kappa_partial_boot_sd']:6.3f}  "
              f"{s['kappa_pearson']:7.3f}{s['kappa_pearson_boot_sd']:6.3f}  "
              f"{s['kappa_hyperbolic']:7.3f}{s['kappa_hyperbolic_boot_sd']:6.3f}  "
              f"{s['ews_var']:5.2f} {s['ews_ac1']:5.2f}")

    # ---- transition alignment + lead-time analysis ----
    # Baseline = phases 1-2 (pre-reduction). Transition onset = first sustained dep rise.
    base_w = [i for i, s in enumerate(series) if s["phase_mode"] <= 2]
    dep_vals = [s["dep_mean"] for s in series if s["dep_mean"] is not None]
    dep_mids = [s["win_mid"] for s in series if s["dep_mean"] is not None]
    base_dep = np.mean([series[i]["dep_mean"] for i in base_w if series[i]["dep_mean"] is not None])
    peak_dep = max(v for v in dep_vals)
    # Robust onset: first window where dep crosses the baseline->peak MIDPOINT and stays
    # crossed for >=2 windows (baseline sd is too small to use as a threshold — it caught
    # within-baseline noise and mislabeled day 14 as the onset).
    mid_thresh = base_dep + 0.5 * (peak_dep - base_dep)
    dep_onset = None
    for i in range(len(dep_vals) - 1):
        if dep_vals[i] > mid_thresh and dep_vals[i + 1] > mid_thresh:
            dep_onset = dep_mids[i]; break
    analysis_thresh = float(mid_thresh)

    analysis = {"baseline_dep": float(base_dep), "peak_dep": float(peak_dep),
                "onset_threshold": analysis_thresh, "dep_transition_onset_day": dep_onset, "signals": {}}
    print(f"\n--- transition: baseline dep={base_dep:.3f}, midpoint thresh={mid_thresh:.3f}, "
          f"onset(sustained>midpoint)= day {dep_onset} ---")
    for m in METRICS:
        kv = [s[f"kappa_{m}"] for s in series]
        bsd = np.nanmean([s[f"kappa_{m}_boot_sd"] for s in series])
        base_k = np.mean([series[i][f"kappa_{m}"] for i in base_w])
        # geometric signal = kappa drops (down) below baseline by 2 bootstrap-sd
        k_signal = first_cross(mids, kv, base_k, bsd, "down", k=2.0)
        analysis["signals"][f"kappa_{m}"] = {"baseline": float(base_k), "boot_sd": float(bsd),
                                             "first_signal_day": k_signal}
    # classical EWS signals (rise)
    for key in ["ews_var", "ews_ac1"]:
        vv = [s[key] for s in series]
        base_v = np.nanmean([series[i][key] for i in base_w])
        base_vsd = np.nanstd([series[i][key] for i in base_w])
        sig = first_cross(mids, vv, base_v, max(base_vsd, 1e-6), "up", k=2.0)
        analysis["signals"][key] = {"baseline": float(base_v), "first_signal_day": sig}

    print(f"{'signal':>18}  first_signal_day  lead_vs_dep_onset")
    for name, info in analysis["signals"].items():
        sd = info["first_signal_day"]
        lead = (dep_onset - sd) if (sd is not None and dep_onset is not None) else None
        analysis["signals"][name]["lead_days_vs_dep_onset"] = lead
        print(f"{name:>18}  {str(sd):>16}  {str(lead):>17}")

    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "kossakowski_geometric_csd.json", "w") as f:
        json.dump({"params": {"win_days": WIN_DAYS, "step_days": STEP_DAYS, "alpha": ALPHA,
                              "ridge": RIDGE, "tau": TAU, "seed": SEED, "bootstrap_B": B},
                  "windows": series, "analysis": analysis}, f, indent=2)
    print(f"\nwrote {OUT / 'kossakowski_geometric_csd.json'}")


if __name__ == "__main__":
    main()
