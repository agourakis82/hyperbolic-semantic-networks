#!/usr/bin/env python3
"""Multi-subject ZuCo KEC + small-worldness — executes PPCR_protocol_zuco_kec_multisubject.md.

Per subject: parse alpha band-power per channel per sentence (sentenceData.mean_a1), build the 16
highest-variance channel CO-ACTIVATION network (corr of band-power across sentences — feature-scale C,
NOT raw coherence; declared in protocol §4), compute KEC{K,E,C} + small-worldness σ. Group = subject unit.

Honest scope: feature-scale co-activation, 16 of ~105 channels, alpha band, subset of subjects. Methods
scaling + the text↔brain small-worldness bridge, not a clinical claim.
"""

import glob, json
from pathlib import Path
import numpy as np
import h5py
import networkx as nx
import ot

FEAT = Path(__file__).resolve().parents[2] / "data/external/zuco/features_NR"
OUT = Path(__file__).resolve().parents[2] / "results/unified"
N_CH = 16
TAU = 0.30
ALPHA = 0.5
SEED = 20260527


def load_bandpower(path, band="mean_a1"):
    try:
        f = h5py.File(path, "r")              # skips truncated/incomplete downloads
    except OSError:
        return None
    with f:
        refs = f["sentenceData"][band]
        rows = []
        for s in range(refs.shape[0]):
            try:
                v = np.array(f[refs[s, 0]]).ravel().astype(float)
            except Exception:
                continue
            if v.size >= 100 and np.isfinite(v).all():
                rows.append(v)
    if not rows:
        return None
    m = min(len(r) for r in rows)
    return np.array([r[:m] for r in rows])      # (n_sent × n_chan)


def coactivation(M):
    C = np.corrcoef(M.T)                          # channel × channel band-power correlation
    return np.abs(np.nan_to_num(C, nan=0.0))


def build_graph(Cmat, idx):
    sub = Cmat[np.ix_(idx, idx)]
    n = len(idx)
    g = nx.Graph(); g.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if sub[i, j] >= TAU:
                g.add_edge(i, j, w=sub[i, j], d=1.0 - sub[i, j])
    while nx.number_connected_components(g) > 1:
        comps = list(nx.connected_components(g)); c0 = comps[0]; best = None
        for a in c0:
            for j in range(n):
                if j not in c0 and sub[a, j] > 0 and (best is None or sub[a, j] > best[2]):
                    best = (a, j, sub[a, j])
        if best is None: break
        g.add_edge(best[0], best[1], w=max(best[2], 1e-3), d=1.0 - max(best[2], 1e-3))
    return g


def mean_orc(g):
    dist = dict(nx.all_pairs_dijkstra_path_length(g, weight="d"))
    ks = []
    for u, v in g.edges():
        def mu(x):
            nb = list(g.neighbors(x)); m = {x: ALPHA}
            ws = sum(g[x][z]["w"] for z in nb) if nb else 0.0
            for z in nb:
                m[z] = m.get(z, 0.0) + (1 - ALPHA) * (g[x][z]["w"]/ws if ws > 0 else 1.0/len(nb))
            return m
        mu_, nu_ = mu(u), mu(v); su, sv = list(mu_), list(nu_)
        a = np.array([mu_[x] for x in su]); b = np.array([nu_[x] for x in sv])
        Md = np.array([[dist[s].get(t, 5) for t in sv] for s in su], float)
        if g[u][v]["d"] > 0:
            ks.append(1.0 - ot.emd2(a, b, Md)/g[u][v]["d"])
    return float(np.mean(ks)) if ks else float("nan")


def von_neumann(g):
    L = nx.laplacian_matrix(g, weight="w").toarray().astype(float)
    lam = np.linalg.eigvalsh(L)
    pos = lam[lam > 1e-9]
    if pos.size == 0: return 0.0, 0.0
    p = pos / pos.sum()
    return float(-np.sum(p*np.log(p)) / np.log(g.number_of_nodes())), float(np.sort(lam)[1])


def small_worldness(g, rng):
    if not nx.is_connected(g): return float("nan")
    C = nx.average_clustering(g); L = nx.average_shortest_path_length(g)
    Cr, Lr = [], []
    for _ in range(20):
        r = nx.gnm_random_graph(g.number_of_nodes(), g.number_of_edges(), seed=int(rng.integers(1e9)))
        if nx.is_connected(r):
            Cr.append(nx.average_clustering(r)); Lr.append(nx.average_shortest_path_length(r))
    if not Cr: return float("nan")
    return (C/np.mean(Cr)) / (L/np.mean(Lr))


def main():
    rng = np.random.default_rng(SEED)
    files = sorted(glob.glob(str(FEAT / "results*_NR.mat")))
    print(f"{len(files)} subject feature files present")
    rows = []
    for path in files:
        subj = Path(path).stem.replace("results", "").replace("_NR", "")
        M = load_bandpower(path)
        if M is None or M.shape[0] < 20:
            print(f"  {subj}: insufficient data, skip"); continue
        Cmat = coactivation(M)
        var = M.var(0); idx = np.sort(np.argsort(var)[::-1][:N_CH])
        g = build_graph(Cmat, idx)
        K = mean_orc(g)
        Enorm, lam2 = von_neumann(g)
        Cmean = float(Cmat[np.ix_(idx, idx)][np.triu_indices(N_CH, 1)].mean())
        sigma = small_worldness(g, rng)
        rows.append({"subject": subj, "n_sent": int(M.shape[0]), "n_edges": g.number_of_edges(),
                     "K_orc": K, "E_norm": Enorm, "C_coact": Cmean, "lambda2": lam2, "sigma": sigma})
        print(f"  {subj}: K={K:+.3f} E={Enorm:.3f} C={Cmean:.3f} σ={sigma:.2f}  (sent={M.shape[0]}, E={g.number_of_edges()})")

    if rows:
        def agg(k): vals=[r[k] for r in rows if np.isfinite(r[k])]; return (float(np.mean(vals)), float(np.std(vals)), len(vals))
        n = len(rows)
        sig_gt1 = sum(1 for r in rows if np.isfinite(r["sigma"]) and r["sigma"] > 1)
        print(f"\n=== GROUP (n={n} subjects) ===")
        for k in ["K_orc", "E_norm", "C_coact", "sigma"]:
            m, sd, c = agg(k); print(f"  {k:8s}: {m:+.3f} ± {sd:.3f} (n={c})")
        print(f"  small-world (σ>1) in {sig_gt1}/{n} subjects")
        OUT.mkdir(parents=True, exist_ok=True)
        with open(OUT / "zuco_kec_multisubject.json", "w") as f:
            json.dump({"protocol": "docs/research/PPCR_protocol_zuco_kec_multisubject.md",
                       "n_channels": N_CH, "band": "alpha(mean_a1)", "tau": TAU,
                       "subjects": rows,
                       "group": {k: agg(k) for k in ["K_orc","E_norm","C_coact","sigma"]},
                       "small_world_fraction": f"{sig_gt1}/{n}"}, f, indent=2)
        print(f"wrote {OUT / 'zuco_kec_multisubject.json'}")


if __name__ == "__main__":
    main()
