"""
asd_phase_test.py — Test ASD vs TD curvature phase prediction using ABIDE-I

Hypothesis: ASD brain networks may be closer to or below η_c (hyperbolic)
while ADHD is above η_c (spherical, confirmed in Phase 8).

Uses nilearn to download ABIDE-I preprocessed ROI timeseries (CC200 atlas),
computes correlation matrices, thresholds to binary graphs, and computes
Forman-Ricci curvature (O(E), scalable) + graph metrics (η, C).

Usage:
    python code/analysis/asd_phase_test.py
"""

import numpy as np
import json
from pathlib import Path


def compute_forman(adj):
    """Forman-Ricci curvature for all edges in adjacency matrix."""
    N = adj.shape[0]
    degrees = adj.sum(axis=1)
    curvatures = []
    for i in range(N):
        for j in range(i+1, N):
            if adj[i, j] == 0:
                continue
            # Count triangles
            t = int((adj[i, :] * adj[j, :]).sum())
            F = 4 - degrees[i] - degrees[j] + 3 * t
            curvatures.append(F)
    return curvatures


def compute_graph_metrics(adj):
    """Compute η, C, mean degree, Forman curvature from binary adjacency."""
    N = adj.shape[0]
    degrees = adj.sum(axis=1)
    E = int(adj.sum() / 2)
    kavg = degrees.mean()
    eta = kavg**2 / N

    # Global clustering coefficient
    triangles = 0
    triples = 0
    for v in range(N):
        d = int(degrees[v])
        if d < 2:
            continue
        nbrs = np.where(adj[v, :] > 0)[0]
        tri_v = 0
        for ii in range(len(nbrs)):
            for jj in range(ii+1, len(nbrs)):
                if adj[nbrs[ii], nbrs[jj]] > 0:
                    tri_v += 1
        triangles += tri_v
        triples += d * (d - 1) // 2
    C = triangles / triples if triples > 0 else 0.0

    # Forman
    forman_vals = compute_forman(adj)
    forman_mean = np.mean(forman_vals) if forman_vals else 0.0

    # η_c for this N
    eta_c = 3.75 - 14.62 / np.sqrt(N)

    return {
        "N": N, "E": E, "kavg": float(kavg), "eta": float(eta),
        "C": float(C), "eta_c": float(eta_c),
        "forman_mean": float(forman_mean),
        "phase": "SPHERICAL" if eta > eta_c else ("HYPERBOLIC" if C > 0.05 else "EUCLIDEAN"),
    }


def main():
    print("=" * 70)
    print("ABIDE-I Phase Test: ASD vs TD Brain Functional Connectivity")
    print("=" * 70)

    # Download ABIDE-I data via nilearn
    print("\nDownloading ABIDE-I preprocessed data (CC200 atlas, CPAC)...")
    from nilearn import datasets

    # Get ASD subjects
    asd_data = datasets.fetch_abide_pcp(
        n_subjects=30,
        derivatives=['rois_cc200'],
        pipeline='cpac',
        quality_checked=False,
        DX_GROUP=1,  # ASD
    )

    # Get TD subjects
    td_data = datasets.fetch_abide_pcp(
        n_subjects=30,
        derivatives=['rois_cc200'],
        pipeline='cpac',
        quality_checked=False,
        DX_GROUP=2,  # TD controls
    )

    print(f"  ASD subjects: {len(asd_data['rois_cc200'])}")
    print(f"  TD subjects: {len(td_data['rois_cc200'])}")

    thresholds = [0.3, 0.4, 0.5]
    results = {"ASD": [], "TD": []}

    for group_name, data in [("ASD", asd_data), ("TD", td_data)]:
        print(f"\n--- {group_name} ---")
        ts_files = data['rois_cc200']

        for idx, ts_data in enumerate(ts_files[:20]):  # Process up to 20
            try:
                if isinstance(ts_data, str):
                    ts = np.loadtxt(ts_data)
                else:
                    ts = np.array(ts_data)
                if ts.ndim != 2 or ts.shape[0] < 50:
                    continue

                # Compute correlation matrix
                corr = np.corrcoef(ts.T)
                np.fill_diagonal(corr, 0)

                for thresh in thresholds:
                    adj = (np.abs(corr) > thresh).astype(float)
                    np.fill_diagonal(adj, 0)

                    # Skip if too sparse or disconnected
                    degrees = adj.sum(axis=1)
                    if (degrees > 0).sum() < 30:
                        continue

                    # Use only nodes with degree > 0
                    active = degrees > 0
                    adj_sub = adj[np.ix_(active, active)]

                    metrics = compute_graph_metrics(adj_sub)
                    metrics["subject_idx"] = idx
                    metrics["group"] = group_name
                    metrics["threshold"] = thresh

                    print(f"  [{group_name}] subj={idx:2d} thresh={thresh:.1f}: "
                          f"N={metrics['N']:3d} E={metrics['E']:5d} "
                          f"η={metrics['eta']:.3f} C={metrics['C']:.3f} "
                          f"η_c={metrics['eta_c']:.2f} [{metrics['phase']}] "
                          f"F̄={metrics['forman_mean']:.1f}")

                    results[group_name].append(metrics)
            except Exception as e:
                print(f"  [{group_name}] subj={idx}: SKIP ({e})")
                continue

    # Summary
    print("\n" + "=" * 70)
    print("PHASE SUMMARY BY GROUP AND THRESHOLD")
    print("=" * 70)

    for thresh in thresholds:
        print(f"\n  Threshold = {thresh}")
        for group in ["ASD", "TD"]:
            grp = [r for r in results[group] if r["threshold"] == thresh]
            if not grp:
                continue
            etas = [r["eta"] for r in grp]
            Cs = [r["C"] for r in grp]
            phases = [r["phase"] for r in grp]
            n_sph = phases.count("SPHERICAL")
            n_hyp = phases.count("HYPERBOLIC")
            n_euc = phases.count("EUCLIDEAN")
            print(f"    {group:4s}: n={len(grp):2d}  η̄={np.mean(etas):.3f}±{np.std(etas):.3f}  "
                  f"C̄={np.mean(Cs):.3f}  "
                  f"Spherical={n_sph} Hyperbolic={n_hyp} Euclidean={n_euc}")

    # Save
    out_path = Path("results/experiments/asd_td_phase_test.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
