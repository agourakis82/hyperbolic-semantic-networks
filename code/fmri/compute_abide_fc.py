#!/usr/bin/env python3
"""
A1: Functional Connectivity Matrix Extraction — ABIDE-I (CC200, 200 ROIs)

Loads preprocessed ABIDE-I time series (.1D files, CPAC pipeline, CC200 parcellation),
computes Pearson FC matrices, applies Fisher z-transform, and saves per-subject .npz files.

Usage:
    python code/fmri/compute_abide_fc.py

Output:
    data/processed/abide_fc/{file_id}_fc.npz       — per-subject FC matrix (200x200)
    data/processed/abide_phenotypic_matched.csv     — phenotypic data for matched subjects
"""

import os
from pathlib import Path

import numpy as np
import pandas as pd

# ── Paths ────────────────────────────────────────────────────────────────────

ABIDE_DIR = Path("/home/demetrios/nilearn_data/ABIDE_pcp/cpac/nofilt_noglobal")
PHENO_CSV = Path("/home/demetrios/nilearn_data/ABIDE_pcp/Phenotypic_V1_0b_preprocessed1.csv")
FC_OUT = Path("data/processed/abide_fc")
FC_OUT.mkdir(parents=True, exist_ok=True)

# ── Parameters ───────────────────────────────────────────────────────────────

MIN_TIMEPOINTS = 100  # exclude subjects with fewer timepoints
N_ROIS = 200          # CC200 parcellation

# ── Main ─────────────────────────────────────────────────────────────────────


def load_timeseries(filepath):
    """Load a .1D file (tab-separated, no header) → (T, 200) array."""
    ts = np.loadtxt(filepath)
    if ts.ndim != 2 or ts.shape[1] != N_ROIS:
        raise ValueError(f"Expected (T, {N_ROIS}), got {ts.shape}")
    return ts


def compute_fc(ts):
    """Pearson correlation → Fisher z-transform."""
    fc = np.corrcoef(ts.T)  # (200, 200)
    np.fill_diagonal(fc, 0.0)
    # Clamp to avoid arctanh(±1) = ±inf
    fc = np.clip(fc, -0.9999, 0.9999)
    z_fc = np.arctanh(fc)
    return z_fc


def main():
    # Load phenotypic data
    pheno = pd.read_csv(PHENO_CSV)
    pheno = pheno[pheno["FILE_ID"] != "no_filename"].copy()

    # Discover .1D files on disk
    onefile_ids = {
        f.replace("_rois_cc200.1D", "")
        for f in os.listdir(ABIDE_DIR)
        if f.endswith("_rois_cc200.1D")
    }

    # Match to phenotypic
    matched = pheno[pheno["FILE_ID"].isin(onefile_ids)].copy()
    print(f"Subjects on disk: {len(onefile_ids)}")
    print(f"Matched to phenotypic: {len(matched)}")

    results = []
    skipped = 0

    for _, row in matched.iterrows():
        file_id = row["FILE_ID"]
        filepath = ABIDE_DIR / f"{file_id}_rois_cc200.1D"

        ts = load_timeseries(filepath)
        n_timepoints = ts.shape[0]

        if n_timepoints < MIN_TIMEPOINTS:
            print(f"  SKIP {file_id}: only {n_timepoints} timepoints")
            skipped += 1
            continue

        # Check for constant ROIs (zero variance → NaN correlation)
        roi_std = ts.std(axis=0)
        n_bad_rois = (roi_std < 1e-10).sum()
        if n_bad_rois > 10:
            print(f"  SKIP {file_id}: {n_bad_rois} constant ROIs")
            skipped += 1
            continue

        z_fc = compute_fc(ts)

        # Save FC matrix
        out_path = FC_OUT / f"{file_id}_fc.npz"
        np.savez_compressed(out_path, z_fc=z_fc, n_timepoints=n_timepoints,
                            n_bad_rois=n_bad_rois)

        results.append({
            "file_id": file_id,
            "sub_id": row["SUB_ID"],
            "site_id": row["SITE_ID"],
            "dx_group": row["DX_GROUP"],
            "age": row["AGE_AT_SCAN"],
            "sex": row["SEX"],
            "n_timepoints": n_timepoints,
            "n_bad_rois": int(n_bad_rois),
            "fc_mean": float(np.mean(np.abs(z_fc))),
            "fc_max": float(np.max(np.abs(z_fc))),
        })

    # Save matched phenotypic
    results_df = pd.DataFrame(results)
    results_df.to_csv("data/processed/abide_phenotypic_matched.csv", index=False)

    print(f"\n{'='*60}")
    print(f"Processed: {len(results)} subjects ({skipped} skipped)")
    print(f"DX breakdown: {results_df['dx_group'].value_counts().to_dict()}")
    print(f"FC matrices saved to: {FC_OUT}")
    print(f"Phenotypic saved to: data/processed/abide_phenotypic_matched.csv")


if __name__ == "__main__":
    main()
