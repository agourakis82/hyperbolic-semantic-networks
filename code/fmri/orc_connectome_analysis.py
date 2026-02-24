#!/usr/bin/env python3
"""
Track A: Ollivier-Ricci Curvature Analysis of ADHD-200 Brain Connectomes
=========================================================================

Tests the central conjecture formalised in DynamicNetworks.lean:

    brain_connectome_sweet_spot_hypothesis:
    Healthy human brain connectomes exhibit the same universal phase
    transition at η ≈ 2.5 (η = ⟨k⟩²/N) found in semantic networks.

Method:
1. Load ADHD-200 resting-state fMRI (10 subjects, already in ~/nilearn_data)
2. Extract MSDL atlas time series (39 functional ROIs — fast for ORC)
3. Compute Pearson correlation (FC) matrix per subject
4. For each density threshold t, build a binary graph (|corr| > t)
5. Compute η = ⟨k⟩²/N and mean ORC κ̄ via Ollivier-Ricci (α = 0.5)
6. Map κ̄(η) curves and compare healthy controls vs ADHD subjects

The semantic network reference curve (from paper) has:
    η < 2.0 → κ̄ < 0  (hyperbolic, tree-like)
    η ≈ 2.5 → κ̄ ≈ 0  (Euclidean critical point)
    η > 3.5 → κ̄ > 0  (spherical, clique-like)

Usage:
    python code/fmri/orc_connectome_analysis.py

Output:
    results/fmri/adhd_orc_analysis.json   — full per-subject data
    results/fmri/adhd_orc_summary.json    — aggregated by diagnosis group
"""

import json
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import networkx as nx
from nilearn import datasets, image
from nilearn.maskers import NiftiMapsMasker
from nilearn.connectome import ConnectivityMeasure
from GraphRicciCurvature.OllivierRicci import OllivierRicci

warnings.filterwarnings("ignore")

# ── Paths ────────────────────────────────────────────────────────────────────

NILEARN_DATA = Path("/home/demetrios/nilearn_data")
RESULTS_DIR = Path("results/fmri")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ── Parameters ───────────────────────────────────────────────────────────────

# Thresholds chosen to span η ∈ [0.1, 6.0] for 39-node MSDL graphs.
# At t≈0.67, 39-node FC matrices have η ≈ 2.5 (the semantic sweet spot).
THRESHOLDS = [0.55, 0.60, 0.65, 0.68, 0.70, 0.73, 0.75, 0.78, 0.80]
ALPHA = 0.5        # ORC idleness parameter (standard)
N_SUBJECTS = 10    # All available in nilearn ADHD-200

# Reference from semantic networks (SWOW English, N=5000 nodes, exact LP)
SEMANTIC_REFERENCE = {
    "dataset": "SWOW English",
    "phase_transition_eta": 2.5,
    "hyperbolic_threshold_eta": 2.0,
    "spherical_threshold_eta": 3.5,
}


# ── Step 1: Load phenotypic data ──────────────────────────────────────────────

def load_phenotypic():
    """Load ADHD diagnosis labels from CSV."""
    pheno_file = NILEARN_DATA / "adhd" / "ADHD200_40subs_motion_parameters_and_phenotypics.csv"
    df = pd.read_csv(pheno_file)
    # Map subject ID → diagnosis (1=ADHD, 0=TDC/healthy)
    return dict(zip(df["Subject"].astype(str).str.zfill(7), df["adhd"]))


# ── Step 2: Atlas and masker ───────────────────────────────────────────────────

def get_msdl_masker():
    """Fetch MSDL atlas and build NiftiMapsMasker.

    MSDL is a *probabilistic* atlas (4D maps image, one volume per region),
    so it requires NiftiMapsMasker rather than NiftiLabelsMasker.
    """
    print("[Atlas] Fetching MSDL atlas (39 functional ROIs)...")
    msdl = datasets.fetch_atlas_msdl()
    masker = NiftiMapsMasker(
        maps_img=msdl.maps,
        standardize="zscore_sample",
        verbose=0,
        resampling_target="data",
    )
    print(f"[Atlas] {len(msdl.labels)} regions: {msdl.labels[:5]} ...")
    return masker, msdl.labels


# ── Step 3: Extract FC matrix ─────────────────────────────────────────────────

def extract_fc(func_file: str, confounds_file: str | None, masker) -> np.ndarray:
    """Extract Pearson FC matrix from a single subject's fMRI run."""
    ts = masker.fit_transform(func_file)
    # Correlation matrix
    conn_measure = ConnectivityMeasure(kind="correlation")
    fc = conn_measure.fit_transform([ts])[0]  # shape (n_rois, n_rois)
    return fc


# ── Step 4: Compute η and κ̄ at one threshold ─────────────────────────────────

def compute_eta_kappa(fc: np.ndarray, threshold: float) -> dict:
    """
    Build a binary graph from FC matrix thresholded at `threshold`,
    compute η = ⟨k⟩²/N and mean ORC κ̄.

    Returns dict with keys: threshold, eta, mean_kappa, n_edges, n_nodes
    """
    n = fc.shape[0]

    # Binary adjacency: edge iff |correlation| > threshold (exclude diagonal)
    adj = (np.abs(fc) > threshold).astype(float)
    np.fill_diagonal(adj, 0.0)

    # Density parameter η = ⟨k⟩²/N
    degrees = adj.sum(axis=1)
    mean_degree = float(degrees.mean())
    eta = mean_degree ** 2 / n

    n_edges = int(adj.sum() / 2)

    if n_edges == 0:
        return {"threshold": threshold, "eta": eta,
                "mean_kappa": None, "n_edges": 0, "n_nodes": n}

    # Build unweighted NetworkX graph (binary adjacency).
    # We use |corr| > threshold to define edges but do NOT assign
    # raw correlations as weights: negative weights cause ORC to diverge.
    G = nx.from_numpy_array(adj)

    # Compute Ollivier-Ricci curvature (α = ALPHA, sequential to avoid fork issues)
    orc = OllivierRicci(G, alpha=ALPHA, verbose="ERROR", proc=1)
    orc.compute_ricci_curvature()

    # Mean curvature over all edges
    curvatures = [
        d["ricciCurvature"]
        for _, _, d in orc.G.edges(data=True)
        if "ricciCurvature" in d
    ]
    mean_kappa = float(np.mean(curvatures)) if curvatures else 0.0

    return {
        "threshold": threshold,
        "eta": round(eta, 4),
        "mean_kappa": round(mean_kappa, 6),
        "n_edges": n_edges,
        "n_nodes": n,
    }


# ── Step 5: Per-subject full curve ────────────────────────────────────────────

def analyze_subject(subject_id: str, func_file: str, confounds_file: str | None,
                    masker, pheno: dict) -> dict:
    """Full pipeline for one subject: FC extraction + ORC curve."""
    print(f"\n  Subject {subject_id}")

    # Diagnosis
    subj_key = subject_id.lstrip("0") or "0"
    diagnosis = pheno.get(subj_key, None)
    if diagnosis is None:
        # Try zero-padded version
        for key in [subject_id, subj_key, subj_key.zfill(7)]:
            if key in pheno:
                diagnosis = pheno[key]
                break
    diag_label = "ADHD" if diagnosis == 1 else ("TDC" if diagnosis == 0 else "unknown")

    print(f"    Diagnosis: {diag_label}")

    # Extract FC matrix
    t0 = time.time()
    try:
        fc = extract_fc(func_file, confounds_file, masker)
    except Exception as e:
        print(f"    [ERROR] FC extraction failed: {e}")
        return None
    print(f"    FC matrix: {fc.shape}, time={time.time()-t0:.1f}s")

    # ORC at each threshold
    curve = []
    for thresh in THRESHOLDS:
        t0 = time.time()
        result = compute_eta_kappa(fc, thresh)
        result["computation_time_s"] = round(time.time() - t0, 2)

        kappa_str = f"{result['mean_kappa']:.4f}" if result["mean_kappa"] is not None else "N/A"
        print(f"    t={thresh:.2f} | η={result['eta']:.3f} | κ̄={kappa_str} "
              f"| edges={result['n_edges']} | t={result['computation_time_s']:.1f}s")
        curve.append(result)

    return {
        "subject_id": subject_id,
        "diagnosis": diag_label,
        "adhd_label": diagnosis,
        "n_rois": fc.shape[0],
        "curve": curve,
    }


# ── Step 6: Aggregate and summarise ──────────────────────────────────────────

def summarise_results(all_subjects: list) -> dict:
    """Aggregate κ̄(η) curves by diagnosis group."""
    groups = {"TDC": [], "ADHD": []}
    for s in all_subjects:
        if s["diagnosis"] in groups:
            groups[s["diagnosis"]].append(s)

    summary = {}
    for group_name, subjects in groups.items():
        if not subjects:
            continue

        # For each threshold, collect (η, κ̄) pairs
        by_thresh = {}
        for s in subjects:
            for point in s["curve"]:
                t = point["threshold"]
                if t not in by_thresh:
                    by_thresh[t] = {"eta": [], "kappa": []}
                if point["mean_kappa"] is not None:
                    by_thresh[t]["eta"].append(point["eta"])
                    by_thresh[t]["kappa"].append(point["mean_kappa"])

        thresh_summary = []
        for t in sorted(by_thresh.keys()):
            etas = by_thresh[t]["eta"]
            kappas = by_thresh[t]["kappa"]
            if etas:
                thresh_summary.append({
                    "threshold": t,
                    "mean_eta": round(float(np.mean(etas)), 4),
                    "std_eta": round(float(np.std(etas)), 4),
                    "mean_kappa": round(float(np.mean(kappas)), 6),
                    "std_kappa": round(float(np.std(kappas)), 6),
                    "n_subjects": len(kappas),
                })

        summary[group_name] = {
            "n_subjects": len(subjects),
            "curve": thresh_summary,
        }

    return summary


def find_critical_eta(curve_data: list) -> float | None:
    """
    Find η* where κ̄ crosses 0 (sign change from negative to positive).
    Interpolates linearly between the two bracketing thresholds.
    """
    valid = [(p["mean_eta"], p["mean_kappa"])
             for p in curve_data
             if p["mean_kappa"] is not None]

    for i in range(1, len(valid)):
        eta_prev, k_prev = valid[i - 1]
        eta_curr, k_curr = valid[i]
        if k_prev is not None and k_curr is not None:
            if k_prev < 0 <= k_curr or k_prev >= 0 > k_curr:
                # Linear interpolation
                frac = abs(k_prev) / (abs(k_prev) + abs(k_curr))
                eta_star = eta_prev + frac * (eta_curr - eta_prev)
                return round(eta_star, 4)
    return None


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("Track A: ORC Phase Transition in ADHD-200 Brain Connectomes")
    print("=" * 70)
    print(f"Semantic reference: η* ≈ {SEMANTIC_REFERENCE['phase_transition_eta']}")
    print(f"Hypothesis: brain connectomes show same universal η* ≈ 2.5")
    print()

    # Load phenotypic labels
    pheno = load_phenotypic()
    print(f"[Pheno] {len(pheno)} subjects with diagnosis labels\n")

    # Load ADHD dataset
    print("[Data] Loading ADHD-200 from local cache...")
    adhd = datasets.fetch_adhd(n_subjects=N_SUBJECTS, data_dir=str(NILEARN_DATA))
    print(f"[Data] {len(adhd.func)} subjects loaded")

    # Build atlas masker
    masker, roi_labels = get_msdl_masker()

    # Analyse each subject
    all_results = []
    for i, (func_file, confounds_file) in enumerate(zip(adhd.func, adhd.confounds)):
        subject_id = Path(func_file).parts[-2]  # e.g. "0010042"
        result = analyze_subject(
            subject_id, func_file, confounds_file, masker, pheno
        )
        if result is not None:
            all_results.append(result)

    print(f"\n[Done] {len(all_results)}/{N_SUBJECTS} subjects processed")

    # Summarise by group
    summary = summarise_results(all_results)

    # Find critical η* per group
    critical_etas = {}
    for group, data in summary.items():
        eta_star = find_critical_eta(data["curve"])
        critical_etas[group] = eta_star
        print(f"\n{group} (n={data['n_subjects']}): η* ≈ {eta_star}")
        print(f"  Semantic reference: η* = {SEMANTIC_REFERENCE['phase_transition_eta']}")
        if eta_star is not None:
            delta = abs(eta_star - SEMANTIC_REFERENCE["phase_transition_eta"])
            print(f"  Δη* from semantic = {delta:.3f}")

    # Hypothesis evaluation
    print("\n" + "=" * 70)
    print("HYPOTHESIS TEST: brain_connectome_sweet_spot_hypothesis")
    print("=" * 70)
    tdc_eta = critical_etas.get("TDC")
    adhd_eta = critical_etas.get("ADHD")
    semantic_eta = SEMANTIC_REFERENCE["phase_transition_eta"]

    if tdc_eta is not None:
        delta_tdc = abs(tdc_eta - semantic_eta)
        print(f"TDC  η* = {tdc_eta:.3f}  (|Δ| from 2.5: {delta_tdc:.3f})")
        if delta_tdc < 0.5:
            print("  ✓ SUPPORTS hypothesis: TDC η* ≈ 2.5")
        else:
            print("  ✗ WEAK: TDC η* far from 2.5")
    else:
        print("  TDC: no zero-crossing detected in η range tested")

    if adhd_eta is not None:
        delta_adhd = abs(adhd_eta - semantic_eta)
        print(f"ADHD η* = {adhd_eta:.3f}  (|Δ| from 2.5: {delta_adhd:.3f})")
        if adhd_eta is not None and tdc_eta is not None:
            group_delta = adhd_eta - tdc_eta
            print(f"  ADHD - TDC Δη* = {group_delta:+.3f}")
            if group_delta > 0.2:
                print("  → ADHD networks are MORE SPHERICAL (shifted toward cliques)")
            elif group_delta < -0.2:
                print("  → ADHD networks are MORE HYPERBOLIC (shifted toward trees)")
            else:
                print("  → Groups are geometrically similar (Δη* < 0.2)")

    # Save full results
    output = {
        "analysis": "Track A: ORC Phase Transition in Brain Connectomes",
        "hypothesis": "brain_connectome_sweet_spot_hypothesis",
        "semantic_reference": SEMANTIC_REFERENCE,
        "parameters": {
            "n_subjects": N_SUBJECTS,
            "atlas": "MSDL (39 ROIs)",
            "orc_alpha": ALPHA,
            "thresholds": THRESHOLDS,
        },
        "per_subject": all_results,
        "group_summary": summary,
        "critical_etas": {k: v for k, v in critical_etas.items()},
        "hypothesis_supported": (
            tdc_eta is not None and abs(tdc_eta - semantic_eta) < 0.5
        ),
    }

    out_file = RESULTS_DIR / "adhd_orc_analysis.json"
    with open(out_file, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\n[Output] Full results saved to: {out_file}")

    # Summary file (compact)
    summary_output = {
        "hypothesis": "brain_connectome_sweet_spot_hypothesis",
        "semantic_eta_star": semantic_eta,
        "brain_eta_star_TDC": critical_etas.get("TDC"),
        "brain_eta_star_ADHD": critical_etas.get("ADHD"),
        "hypothesis_supported": output["hypothesis_supported"],
        "group_summary": summary,
    }
    summary_file = RESULTS_DIR / "adhd_orc_summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary_output, f, indent=2)
    print(f"[Output] Summary saved to: {summary_file}")

    return output


if __name__ == "__main__":
    main()
