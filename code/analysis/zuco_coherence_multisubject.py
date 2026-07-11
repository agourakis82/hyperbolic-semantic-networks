#!/usr/bin/env python3
"""Close the coherence bridge at GROUP level — does the raw-coherence channel-network small-worldness
(σ=1.57 in 1 subject) replicate across subjects?

The feature files contain sentenceData.rawData (raw EEG per sentence, time × 105 ch). We compute true
inter-channel magnitude-squared COHERENCE (alpha band) per subject — NOT band-power co-activation — build
the 16-channel coherence network, and test small-worldness σ across the 6 downloaded subjects.

Pre-registered question (PPCR_protocol_zuco_kec_multisubject.md, the open scale-up): is the
coherence-network small-world (σ>1) consistently across subjects? Decision: σ>1 in ≥5/6 AND group CI
excludes 1 → coherence bridge CONFIRMED at group level. Honest scope: 6 subjects, 16 of 105 channels,
alpha band, reading task.
"""

import glob, json
from pathlib import Path
import numpy as np
import h5py
from scipy.signal import coherence
import networkx as nx
import ot

FEAT = Path(__file__).resolve().parents[2] / "data/external/zuco/features_NR"
OUT = Path(__file__).resolve().parents[2] / "results/unified"
FS = 500.0
N_CH = 16
TAU = 0.30
ALPHA = 0.5
MAX_SAMP = 60000          # ~120 s of concatenated reading per subject (compute bound)
SEED = 20260527


def load_raw_concat(path):
    try:
        f = h5py.File(path, "r")
    except OSError:
        return None
    with f:
        rd = f["sentenceData"]["rawData"]
        segs = []
        total = 0
        for s in range(rd.shape[0]):
            try:
                a = np.array(f[rd[s, 0]]).astype(np.float64)   # (T, 105)
            except Exception:
                continue
            if a.ndim != 2 or a.shape[1] < 100:
                continue
            if not np.isfinite(a).all():
                continue                                        # drop bad-channel sentences
            segs.append(a); total += a.shape[0]
            if total >= MAX_SAMP:
                break
    if not segs:
        return None
    X = np.vstack(segs)                                          # (T, 105)
    return X


def coherence_net(X, n_ch):
    var = X.var(0)
    idx = np.sort(np.argsort(var)[::-1][:n_ch])                  # active channels
    sig = X[:, idx] - X[:, idx].mean(0)
    C = np.eye(n_ch)
    for i in range(n_ch):
        for j in range(i + 1, n_ch):
            fc, cxy = coherence(sig[:, i], sig[:, j], fs=FS, nperseg=int(FS * 2))
            m = (fc >= 8) & (fc <= 13)
            v = float(np.mean(cxy[m])) if m.any() else 0.0
            C[i, j] = C[j, i] = (v if np.isfinite(v) else 0.0)
    return C


def build_graph(C):
    n = C.shape[0]; g = nx.Graph(); g.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if C[i, j] >= TAU:
                g.add_edge(i, j, w=C[i, j], d=1.0 - C[i, j])
    while nx.number_connected_components(g) > 1:
        comps = list(nx.connected_components(g)); c0 = comps[0]; best = None
        for a in c0:
            for j in range(n):
                if j not in c0 and C[a, j] > 0 and (best is None or C[a, j] > best[2]):
                    best = (a, j, C[a, j])
        if best is None: break
        g.add_edge(best[0], best[1], w=max(best[2], 1e-3), d=1.0 - max(best[2], 1e-3))
    return g


def mean_orc(g):
    dist = dict(nx.all_pairs_dijkstra_path_length(g, weight="d")); ks = []
    for u, v in g.edges():
        def mu(x):
            nb = list(g.neighbors(x)); m = {x: ALPHA}
            ws = sum(g[x][z]["w"] for z in nb) if nb else 0.0
            for z in nb: m[z] = m.get(z, 0.0) + (1 - ALPHA) * (g[x][z]["w"]/ws if ws > 0 else 1.0/len(nb))
            return m
        mu_, nu_ = mu(u), mu(v); su, sv = list(mu_), list(nu_)
        a = np.array([mu_[x] for x in su]); b = np.array([nu_[x] for x in sv])
        Md = np.array([[dist[s].get(t, 5) for t in sv] for s in su], float)
        if g[u][v]["d"] > 0: ks.append(1.0 - ot.emd2(a, b, Md)/g[u][v]["d"])
    return float(np.mean(ks)) if ks else float("nan")


def von_neumann(g):
    L = nx.laplacian_matrix(g, weight="w").toarray().astype(float)
    lam = np.linalg.eigvalsh(L); pos = lam[lam > 1e-9]
    if pos.size == 0: return 0.0
    p = pos / pos.sum(); return float(-np.sum(p*np.log(p))/np.log(g.number_of_nodes()))


def small_worldness(g, rng):
    if not nx.is_connected(g): return float("nan")
    C = nx.average_clustering(g); L = nx.average_shortest_path_length(g)
    Cr, Lr = [], []
    for _ in range(20):
        r = nx.gnm_random_graph(g.number_of_nodes(), g.number_of_edges(), seed=int(rng.integers(1e9)))
        if nx.is_connected(r): Cr.append(nx.average_clustering(r)); Lr.append(nx.average_shortest_path_length(r))
    if not Cr: return float("nan")
    return (C/np.mean(Cr)) / (L/np.mean(Lr))


def main():
    rng = np.random.default_rng(SEED)
    rows = []
    for path in sorted(glob.glob(str(FEAT / "results*_NR.mat"))):
        subj = Path(path).stem.replace("results", "").replace("_NR", "")
        X = load_raw_concat(path)
        if X is None or X.shape[0] < 5000:
            print(f"  {subj}: insufficient clean raw, skip"); continue
        C = coherence_net(X, N_CH)
        g = build_graph(C)
        sigma = small_worldness(g, rng)
        K = mean_orc(g); E = von_neumann(g)
        Cmean = float(C[np.triu_indices(N_CH, 1)].mean())
        rows.append({"subject": subj, "samples": int(X.shape[0]), "n_edges": g.number_of_edges(),
                     "sigma": sigma, "K_orc": K, "E_norm": E, "C_coh": Cmean})
        print(f"  {subj}: σ={sigma:.2f}  K={K:+.3f}  E={E:.3f}  C(coh)={Cmean:.3f}  (T={X.shape[0]}, E={g.number_of_edges()})")

    if rows:
        sig = np.array([r["sigma"] for r in rows if np.isfinite(r["sigma"])])
        n = len(sig); m = float(sig.mean()); sd = float(sig.std())
        ci_lo = m - 1.96 * sd / np.sqrt(n); ci_hi = m + 1.96 * sd / np.sqrt(n)
        n_gt1 = int((sig > 1).sum())
        confirmed = (n_gt1 >= max(5, int(np.ceil(0.8 * len(rows))))) and ci_lo > 1.0
        print(f"\n=== COHERENCE-network small-worldness, GROUP (n={len(rows)}) ===")
        print(f"  σ = {m:.3f} ± {sd:.3f}  95%CI [{ci_lo:.3f}, {ci_hi:.3f}]")
        print(f"  σ>1 in {n_gt1}/{len(rows)} subjects")
        print(f"  K = {np.mean([r['K_orc'] for r in rows]):+.3f}  (spherical channel geometry)")
        verdict = ("COHERENCE BRIDGE CONFIRMED at group level (σ>1 robust)" if confirmed
                   else "NOT CONFIRMED — coherence small-worldness not robust across subjects")
        print(f"\nVERDICT: {verdict}")
        OUT.mkdir(parents=True, exist_ok=True)
        with open(OUT / "zuco_coherence_multisubject.json", "w") as f:
            json.dump({"connectivity": "alpha magnitude-squared coherence (raw)", "n_channels": N_CH,
                       "tau": TAU, "subjects": rows,
                       "group_sigma": {"mean": m, "sd": sd, "ci": [ci_lo, ci_hi], "n_gt1": f"{n_gt1}/{len(rows)}"},
                       "verdict": verdict}, f, indent=2)
        print(f"wrote {OUT / 'zuco_coherence_multisubject.json'}")


if __name__ == "__main__":
    main()
