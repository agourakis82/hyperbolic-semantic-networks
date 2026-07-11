#!/usr/bin/env python3
"""PPCR reconstruction — network curvature of depression-severity text (executes the frozen protocol).

Implements EXACTLY the pre-registered SAP in docs/research/PPCR_protocol_depression_curvature.md.
Rebuilds on the re-acquired real HelaDepDet corpus. Nothing here is tuned to a target; the construction
(window=5, min-word≥5, N_node=1000, α=0.5) is pre-specified and blinded to the severity label, which is
used ONLY at the comparison step.

Primary endpoint (frozen): sign+significance of minimum-vs-pooled-clinical κ under the stratified
density-distribution match. Decision rule: minimum most-hyperbolic in ≥8/10 seeds AND worst-case
matched-edge Mann-Whitney p < 0.05 → CONFIRMATORY; else NULL; survives primary but not robustness → PARTIAL.

Object (honest): word CO-OCCURRENCE networks of depression-severity-labeled social-media text
(speech-graph tradition). NOT SWOW, NOT semantic-memory, NOT brain. No individual/diagnostic claim.
"""

import csv, json, os, re, random
from pathlib import Path
import numpy as np
import networkx as nx
import ot
from scipy.stats import mannwhitneyu

DATA = Path(__file__).resolve().parents[2] / "data/external/Depression_Severity_Levels_Dataset/Depression_Severity_Levels_Dataset.csv"
OUT = Path(__file__).resolve().parents[2] / "results/unified"
STRATA = ["minimum", "mild", "moderate", "severe"]
CLINICAL = ["mild", "moderate", "severe"]

# --- PRE-SPECIFIED construction (protocol §8); primary = defaults, sensitivity grid via env ---
N_PER_CLASS = int(os.environ.get("PPCR_N", "250"))
WINDOW = int(os.environ.get("PPCR_WINDOW", "5"))
MIN_WORD = int(os.environ.get("PPCR_MINWORD", "5"))
N_NODE = 1000
ALPHA = 0.5
N_BINS = 10
K_SEEDS = int(os.environ.get("PPCR_SEEDS", "10"))
BASE_SEED = 20260527
TAG = os.environ.get("PPCR_TAG", "")

WORD_RE = re.compile(r"[a-z]{%d,}" % MIN_WORD)


def load_corpus():
    by = {s: [] for s in STRATA}
    with open(DATA, newline="", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            lab = row["label"].strip().lower()
            if lab in by and row["text"].strip():
                by[lab].append(row["text"])
    return by


def build_cooccur(texts):
    g = nx.Graph()
    for t in texts:
        w = WORD_RE.findall(t.lower())
        for i in range(len(w)):
            for j in range(i + 1, min(i + WINDOW, len(w))):
                if w[i] != w[j]:
                    if g.has_edge(w[i], w[j]):
                        g[w[i]][w[j]]["weight"] += 1
                    else:
                        g.add_edge(w[i], w[j], weight=1)
    return g


def subsample(g, n, rng):
    cc = max(nx.connected_components(g), key=len)
    h = g.subgraph(cc).copy()
    if h.number_of_nodes() > n:
        nodes = rng.sample(list(h.nodes()), n)
        h = h.subgraph(nodes).copy()
        cc = max(nx.connected_components(h), key=len)
        h = h.subgraph(cc).copy()
    return nx.convert_node_labels_to_integers(h)


def lazy_measure(g, x):
    nbrs = list(g.neighbors(x))
    m = {x: ALPHA}
    if nbrs:
        w = (1.0 - ALPHA) / len(nbrs)
        for z in nbrs:
            m[z] = m.get(z, 0.0) + w
    return m


def per_edge_kappa(g):
    deg = dict(g.degree())
    dist_cache = {}
    ks, dens = [], []
    for u, v in g.edges():
        mu, nu = lazy_measure(g, u), lazy_measure(g, v)
        sn, tn = list(mu), list(nu)
        a = np.array([mu[s] for s in sn]); b = np.array([nu[t] for t in tn])
        M = np.empty((len(sn), len(tn)))
        for i, s in enumerate(sn):
            ds = dist_cache.get(s)
            if ds is None:
                ds = nx.single_source_shortest_path_length(g, s); dist_cache[s] = ds
            for j, t in enumerate(tn):
                M[i, j] = ds.get(t, len(g))
        ks.append(1.0 - ot.emd2(a, b, M))
        dens.append(0.5 * (deg[u] + deg[v]))
    return np.array(ks), np.array(dens)


def stratified_match_min_vs_clinical(per, rng):
    """Primary analysis: equate density distribution across 4 strata (decile bins), compare
    minimum vs pooled clinical matched-edge κ. Returns (matched_means, mw_p, rank_biserial, min_is_most)."""
    all_d = np.concatenate([per[s]["dens"] for s in STRATA])
    edges = np.quantile(all_d, np.linspace(0, 1, N_BINS + 1)); edges[-1] += 1e-9
    matched = {s: [] for s in STRATA}
    for b in range(N_BINS):
        lo, hi = edges[b], edges[b + 1]
        pools = {s: per[s]["kappa"][(per[s]["dens"] >= lo) & (per[s]["dens"] < hi)] for s in STRATA}
        m = min(len(pools[s]) for s in STRATA)
        if m < 5:
            continue
        for s in STRATA:
            matched[s].extend(rng.sample(list(pools[s]), m))
    mm = {s: float(np.mean(matched[s])) for s in STRATA}
    minv = np.array(matched["minimum"])
    clin = np.concatenate([np.array(matched[s]) for s in CLINICAL])
    U, p = mannwhitneyu(minv, clin, alternative="two-sided")
    rb = 1.0 - 2.0 * U / (len(minv) * len(clin))
    min_is_most = all(mm["minimum"] <= mm[s] for s in CLINICAL)   # most negative = most hyperbolic
    return mm, float(p), float(rb), bool(min_is_most)


def main():
    corpus = load_corpus()
    print("HelaDepDet loaded:", {s: len(corpus[s]) for s in STRATA})
    seeds_report = []
    for k in range(K_SEEDS):
        seed = BASE_SEED + k
        rng = random.Random(seed)
        per = {}
        for s in STRATA:
            texts = rng.sample(corpus[s], N_PER_CLASS)        # stratified random sample (blinded)
            g = subsample(build_cooccur(texts), N_NODE, rng)
            ks, dens = per_edge_kappa(g)
            per[s] = {"kappa": ks, "dens": dens, "N": g.number_of_nodes(), "E": g.number_of_edges()}
        # raw (unmatched) means for the confound contrast
        raw = {s: float(per[s]["kappa"].mean()) for s in STRATA}
        mm, p, rb, min_most = stratified_match_min_vs_clinical(per, rng)
        seeds_report.append({"seed": seed, "raw_mean_kappa": raw, "matched_mean_kappa": mm,
                             "matched_min_vs_clinical_p": p, "rank_biserial": rb,
                             "min_is_most_hyperbolic": min_most,
                             "sizes": {s: [per[s]["N"], per[s]["E"]] for s in STRATA}})
        print(f"seed {seed}: matched min κ={mm['minimum']:+.4f} "
              f"clin κ=({mm['mild']:+.3f},{mm['moderate']:+.3f},{mm['severe']:+.3f}) "
              f"min_most={min_most} p={p:.2e} rb={rb:+.3f}")

    # --- pre-registered decision rule ---
    n_min_most = sum(r["min_is_most_hyperbolic"] for r in seeds_report)
    worst_p = max(r["matched_min_vs_clinical_p"] for r in seeds_report)
    matched_min = [r["matched_mean_kappa"]["minimum"] for r in seeds_report]
    agg = {s: (float(np.mean([r["matched_mean_kappa"][s] for r in seeds_report])),
               float(np.std([r["matched_mean_kappa"][s] for r in seeds_report]))) for s in STRATA}
    thresh = 0.8 * K_SEEDS
    decision = ("CONFIRMATORY" if (n_min_most >= thresh and worst_p < 0.05) else "NULL")

    print(f"\n=== PRIMARY DECISION (protocol §9) ===")
    print(f"minimum most-hyperbolic in {n_min_most}/{K_SEEDS} seeds (rule: ≥8)")
    print(f"worst-case matched min-vs-clinical p = {worst_p:.2e} (rule: <0.05)")
    print("matched κ (mean±SD across seeds):")
    for s in sorted(STRATA, key=lambda s: agg[s][0]):
        print(f"  {s:9s}: {agg[s][0]:+.4f} ± {agg[s][1]:.4f}")
    print(f"\nDECISION: {decision}")

    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / f"ppcr_depression_curvature_rebuild{TAG}.json", "w") as f:
        json.dump({"protocol": "docs/research/PPCR_protocol_depression_curvature.md",
                   "construction": {"n_per_class": N_PER_CLASS, "window": WINDOW, "min_word": MIN_WORD,
                                    "n_node": N_NODE, "alpha": ALPHA, "n_bins": N_BINS, "k_seeds": K_SEEDS},
                   "seeds": seeds_report,
                   "primary": {"n_min_most": n_min_most, "k_seeds": K_SEEDS, "worst_p": worst_p,
                               "matched_kappa_mean_sd": agg, "decision": decision}}, f, indent=2)
    print(f"wrote {OUT / 'ppcr_depression_curvature_rebuild.json'}")


if __name__ == "__main__":
    main()
