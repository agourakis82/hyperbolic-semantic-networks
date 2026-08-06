#!/usr/bin/env python3
"""Lane B closure — ZuCo EEG → inter-channel network → KEC{K,E,C}.

Sounio-first division of labour: Python does I/O + connectivity (plumbing); the *certified* KEC
instrument lives in Sounio (examples/semantic_orc/kec_spectral.sio / kec_epistemic_spectral.sio).
This script (a) loads real ZuCo EEG, (b) builds a 16-channel inter-channel COHERENCE network — the
substrate-appropriate C for signals (vs the graph λ₂ used for word networks), (c) computes a reference
KEC, and (d) EMITS the 16×16 Laplacian as a Sounio source so the native verified KEC consumes it and
agrees.

KEC on the channel graph:
  K = mean Ollivier–Ricci curvature (exact OT, lazy walk) of the coherence-thresholded graph.
  E = von Neumann spectral entropy of the coherence-graph Laplacian (p_i=λ_i/Σλ, S=−Σ p ln p, /ln n).
  C = mean inter-channel magnitude-squared coherence in the alpha band (8–13 Hz) — the EEG coherence;
      algebraic connectivity λ₂ also reported (graph-coherence, for cross-substrate comparability).

Honest scope: one subject, one recording, 16 of 105 channels, broadband-derived demo. NOT a clinical
or group claim — a methods closure showing real ZuCo EEG flows through the KEC pipeline end-to-end.
"""

import json
from pathlib import Path
import numpy as np
import h5py
from scipy.signal import butter, filtfilt, coherence
import networkx as nx
import ot

MAT = Path(__file__).resolve().parents[2] / "data/external/zuco/gip_ZAB_SR5_EEG.mat"
OUT = Path(__file__).resolve().parents[2] / "results/unified"
SIO_OUT = Path(__file__).resolve().parents[2].parent / "sounio/examples/semantic_orc/zuco_kec_input.sio"
N_CH = 16
ALPHA = 0.5
TAU = 0.30
FS = 500.0
WIN_S = 60                # use first 60 s (30000 samples)


def load_eeg():
    with h5py.File(MAT, "r") as f:
        data = np.array(f["EEG"]["data"])          # (T, 105)
        srate = float(np.array(f["EEG"]["srate"]).ravel()[0])
    return data, srate


def pick_channels(data, n):
    # 16 most-active channels (highest variance) — avoids flat/bad channels (ZuCo has bad-channel
    # interpolation; evenly-spaced selection can hit a flat channel → nan coherence / disconnection).
    var = data.var(0)
    idx = np.sort(np.argsort(var)[::-1][:n])
    return data[:, idx], idx


def bandpass(x, lo, hi, fs):
    b, a = butter(4, [lo / (fs / 2), hi / (fs / 2)], btype="band")
    return filtfilt(b, a, x, axis=0)


def coherence_matrix(sig, fs, band=(8.0, 13.0)):
    """16×16 mean magnitude-squared coherence in the alpha band."""
    n = sig.shape[1]
    C = np.eye(n)
    for i in range(n):
        for j in range(i + 1, n):
            fcoh, cxy = coherence(sig[:, i], sig[:, j], fs=fs, nperseg=int(fs * 2))
            m = (fcoh >= band[0]) & (fcoh <= band[1])
            v = float(np.mean(cxy[m])) if m.any() else 0.0
            if not np.isfinite(v):
                v = 0.0                       # flat/bad channel guard
            C[i, j] = C[j, i] = v
    return np.nan_to_num(C, nan=0.0)


def von_neumann_entropy(g):
    n = g.number_of_nodes()
    L = nx.laplacian_matrix(g, weight="w").toarray().astype(float)
    lam = np.linalg.eigvalsh(L)
    lam = lam[lam > 1e-9]
    if lam.size == 0:
        return 0.0, 0.0, 0.0
    p = lam / lam.sum()
    S = float(-np.sum(p * np.log(p)))
    lam_sorted = np.sort(np.linalg.eigvalsh(L))
    lambda2 = float(lam_sorted[1])
    return S, S / np.log(n), lambda2


def mean_orc(g):
    dist = dict(nx.all_pairs_dijkstra_path_length(g, weight="d"))
    ks = []
    for u, v in g.edges():
        def mu(x):
            nb = list(g.neighbors(x)); m = {x: ALPHA}
            wsum = sum(g[x][z]["w"] for z in nb) if nb else 0.0
            for z in nb:
                m[z] = m.get(z, 0.0) + (1 - ALPHA) * (g[x][z]["w"] / wsum if wsum > 0 else 1.0 / len(nb))
            return m
        m_u, m_v = mu(u), mu(v)
        su, sv = list(m_u), list(m_v)
        a = np.array([m_u[x] for x in su]); b = np.array([m_v[x] for x in sv])
        M = np.array([[dist[s].get(t, 5) for t in sv] for s in su], float)
        duv = g[u][v]["d"]
        if duv > 0:
            ks.append(1.0 - ot.emd2(a, b, M) / duv)
    return float(np.mean(ks)) if ks else float("nan")


def build_graph(Cmat):
    n = Cmat.shape[0]
    g = nx.Graph(); g.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if Cmat[i, j] >= TAU:
                g.add_edge(i, j, w=Cmat[i, j], d=1.0 - Cmat[i, j])
    # connect if fragmented (strongest available cross-edges)
    while nx.number_connected_components(g) > 1:
        comps = list(nx.connected_components(g)); a0 = list(comps[0]); best = None
        for a in a0:
            for j in range(n):
                if j not in comps[0] and Cmat[a, j] > 0 and (best is None or Cmat[a, j] > best[2]):
                    best = (a, j, Cmat[a, j])
        if best is None:
            break
        g.add_edge(best[0], best[1], w=max(best[2], 1e-3), d=1.0 - max(best[2], 1e-3))
    return g


def emit_sounio(g, n, E_ref, lambda2_ref):
    """Emit a SELF-CONTAINED native Sounio KEC program: fills the real ZuCo channel-coherence
    Laplacian into a local var, runs the verified Jacobi eigensolver, computes von Neumann spectral
    entropy + λ₂, and asserts agreement with the Python reference (E_ref, lambda2_ref)."""
    L = nx.laplacian_matrix(g, weight="w").toarray().astype(float)
    fill = "\n".join(f"    L[{i*n+j}] = {L[i,j]:.6f}" for i in range(n) for j in range(n))
    src = f'''//@ run-pass
//! ZuCo channel-coherence KEC — NATIVE Sounio, on a real EEG Laplacian (subject ZAB) emitted by
//! code/analysis/zuco_kec.py. Closes Lane B: real reading-EEG → channel network → certified Sounio
//! spectral KEC (von Neumann entropy + λ₂), agreeing with the Python reference.

fn et_abs(x: f64) -> f64 {{ if x < 0.0 {{ 0.0 - x }} else {{ x }} }}
fn et_sqrt(x: f64) -> f64 with Mut, Div, Panic {{
    if x <= 0.0 {{ return 0.0 }}
    var y = x; var i: i64 = 0
    while i < 30 {{ y = 0.5 * (y + x / y); i = i + 1 }}
    y
}}
fn et_ln(x: f64) -> f64 with Mut, Div, Panic {{
    if x <= 0.0 {{ return -1000000.0 }}
    let ln2 = 0.6931471805599453
    var v = x; var k: i64 = 0
    while v > 2.0 {{ v = v / 2.0; k = k + 1 }}
    while v < 1.0 {{ v = v * 2.0; k = k - 1 }}
    let y = (v - 1.0) / (v + 1.0); let yy = y * y
    var result = 0.0; var power = y; var i: i64 = 1
    while i <= 29 {{ result = result + power / (i as f64); power = power * yy; i = i + 2 }}
    2.0 * result + (k as f64) * ln2
}}

fn main() -> i64 with IO, Mut, Div, Panic {{
    let n: i64 = {n}
    var L: [f64; 256] = [0.0; 256]
{fill}
    // Jacobi cyclic sweeps (sqrt-only)
    var sweep: i64 = 0
    while sweep < 60 {{
        var p: i64 = 0
        while p < n {{
            var q: i64 = p + 1
            while q < n {{
                let apq = L[p * n + q]
                if et_abs(apq) > 1e-12 {{
                    let app = L[p * n + p]; let aqq = L[q * n + q]
                    let theta = (aqq - app) / (2.0 * apq)
                    let denom = et_abs(theta) + et_sqrt(theta * theta + 1.0)
                    var t = 1.0 / denom
                    if theta < 0.0 {{ t = 0.0 - t }}
                    let c = 1.0 / et_sqrt(t * t + 1.0); let s = t * c
                    var k: i64 = 0
                    while k < n {{
                        let lkp = L[k * n + p]; let lkq = L[k * n + q]
                        L[k * n + p] = c * lkp - s * lkq
                        L[k * n + q] = s * lkp + c * lkq
                        k = k + 1
                    }}
                    k = 0
                    while k < n {{
                        let lpk = L[p * n + k]; let lqk = L[q * n + k]
                        L[p * n + k] = c * lpk - s * lqk
                        L[q * n + k] = s * lpk + c * lqk
                        k = k + 1
                    }}
                }}
                q = q + 1
            }}
            p = p + 1
        }}
        sweep = sweep + 1
    }}
    var eig: [f64; 16] = [0.0; 16]
    var i: i64 = 0
    while i < n {{ eig[i] = L[i * n + i]; i = i + 1 }}
    i = 1
    while i < n {{
        let key = eig[i]; var j: i64 = i - 1
        while j >= 0 && eig[j] > key {{ eig[j + 1] = eig[j]; j = j - 1 }}
        eig[j + 1] = key; i = i + 1
    }}
    var total = 0.0
    i = 0
    while i < n {{ if eig[i] > 1e-9 {{ total = total + eig[i] }} ; i = i + 1 }}
    var S = 0.0
    i = 0
    while i < n {{ if eig[i] > 1e-9 {{ let pi = eig[i] / total; S = S - pi * et_ln(pi) }} ; i = i + 1 }}
    let lambda2 = eig[1]
    print("E_vonneumann="); print(S); println("")
    print("lambda2="); print(lambda2); println("")
    let e_ref = {E_ref:.6f}
    let l2_ref = {lambda2_ref:.6f}
    if et_abs(S - e_ref) < 0.01 && et_abs(lambda2 - l2_ref) < 0.005 {{
        println("ZUCO_KEC_NATIVE_PASS")
        println("claim=real_zuco_reading_EEG_through_native_sounio_KEC")
        println("matches_python_reference=true")
        0
    }} else {{
        println("ZUCO_KEC_NATIVE_FAIL")
        1
    }}
}}
'''
    SIO_OUT.write_text(src)


def main():
    data, srate = load_eeg()
    print(f"ZuCo EEG: {data.shape[0]} samples × {data.shape[1]} channels @ {srate:.0f} Hz")
    n_keep = min(int(WIN_S * srate), data.shape[0])
    sig16, idx = pick_channels(data[:n_keep], N_CH)
    sig16 = sig16 - sig16.mean(0)
    print(f"using first {n_keep/srate:.0f}s, channels {list(idx)}")

    Cmat = coherence_matrix(sig16, srate)
    mean_coh = float(Cmat[np.triu_indices(N_CH, 1)].mean())
    g = build_graph(Cmat)
    print(f"channel graph: {g.number_of_nodes()} nodes, {g.number_of_edges()} edges (τ={TAU})")

    K = mean_orc(g)
    E, Enorm, lambda2 = von_neumann_entropy(g)
    print(f"\n=== KEC on real ZuCo channel-coherence network ===")
    print(f"  K (mean Ollivier-Ricci curvature) = {K:+.4f}")
    print(f"  E (von Neumann spectral entropy)  = {E:.4f}  (norm {Enorm:.4f})")
    print(f"  C (mean alpha inter-channel coherence) = {mean_coh:.4f}")
    print(f"  λ₂ (algebraic connectivity)        = {lambda2:.4f}")

    emit_sounio(g, N_CH, E, lambda2)
    print(f"\nemitted self-contained native Sounio KEC → {SIO_OUT}")

    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "zuco_kec.json", "w") as f:
        json.dump({"source": "gip_ZAB_SR5_EEG.mat", "n_channels": N_CH, "channels": idx.tolist(),
                   "window_s": WIN_S, "tau": TAU,
                   "KEC": {"K_orc": K, "E_vonneumann": E, "E_norm": Enorm,
                           "C_alpha_coherence": mean_coh, "lambda2": lambda2}}, f, indent=2)
    print(f"wrote {OUT / 'zuco_kec.json'}")


if __name__ == "__main__":
    main()
