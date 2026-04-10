#!/usr/bin/env python3
"""
D1: Dual Classifier — ORC + Octonion Associator Features for ASD vs Control

Combines ORC features (8-dim) with associator features (4-dim per scheme)
into dual feature vectors. Evaluates classification accuracy via
stratified 5-fold CV with GaussianNB + permutation test.

Usage:
    python code/analysis/brain_dual_classifier.py

Output:
    results/fmri/abide_dual_classifier.json
"""

import json
from pathlib import Path

import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import LinearSVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

# ── Paths ────────────────────────────────────────────────────────────────────

RESULTS_DIR = Path("results/fmri")
THRESHOLD = 0.40

# ── Load data ────────────────────────────────────────────────────────────────


def load_features():
    """Load and merge ORC + octonion features."""
    # ORC results
    orc_file = RESULTS_DIR / f"abide_orc_sinkhorn_t{THRESHOLD:.2f}.json"
    orc_data = json.loads(orc_file.read_text())

    # Octonion features
    oct_file = RESULTS_DIR / f"abide_octonion_features_t{THRESHOLD:.2f}.json"
    oct_data = json.loads(oct_file.read_text())

    # Build lookup
    oct_lookup = {r["file_id"]: r for r in oct_data}

    features_orc = []
    features_oct_fc = []
    features_oct_rsn = []
    labels = []

    for r in orc_data:
        fid = r["file_id"]
        if fid not in oct_lookup:
            continue

        oct_r = oct_lookup[fid]

        # ORC features (8-dim)
        orc_feat = [
            r["kappa_mean"],
            r["kappa_std"],
            r["eta"],
            r["eta"] / (3.75 - 14.62 / np.sqrt(r["N"])),  # eta / eta_c
            r["n_edges"],
            r["frac_positive"],
            r["mean_k"],
            r["kappa_mean"] ** 2,  # squared kappa (captures magnitude)
        ]

        # Octonion FC features (4-dim)
        fc = oct_r["scheme_fc"]
        oct_fc_feat = [
            fc["mean_assoc_norm"],
            fc["zero_frac"],
            fc["assoc_entropy"],
            fc["n_triples"],
        ]

        # Octonion RSN features (4-dim)
        rsn = oct_r["scheme_rsn"]
        oct_rsn_feat = [
            rsn["mean_assoc_norm"],
            rsn["zero_frac"],
            rsn["assoc_entropy"],
            rsn["n_triples"],
        ]

        features_orc.append(orc_feat)
        features_oct_fc.append(oct_fc_feat)
        features_oct_rsn.append(oct_rsn_feat)
        labels.append(r["dx_group"])

    X_orc = np.array(features_orc)
    X_oct_fc = np.array(features_oct_fc)
    X_oct_rsn = np.array(features_oct_rsn)
    y = np.array(labels)

    # Remove rows with NaN
    valid = ~(np.isnan(X_orc).any(axis=1) | np.isnan(X_oct_fc).any(axis=1) |
              np.isnan(X_oct_rsn).any(axis=1))
    X_orc = X_orc[valid]
    X_oct_fc = X_oct_fc[valid]
    X_oct_rsn = X_oct_rsn[valid]
    y = y[valid]

    return X_orc, X_oct_fc, X_oct_rsn, y


# ── Classification ───────────────────────────────────────────────────────────


def evaluate_classifier(X, y, clf_factory, n_splits=5, n_permutations=500):
    """Stratified k-fold CV with permutation test."""
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

    # Real AUROC
    aucs = []
    for train_idx, test_idx in cv.split(X, y):
        clf = clf_factory()
        clf.fit(X[train_idx], y[train_idx])
        if hasattr(clf, "predict_proba"):
            y_prob = clf.predict_proba(X[test_idx])[:, 1]
        else:
            y_prob = clf.decision_function(X[test_idx])
        try:
            auc = roc_auc_score(y[test_idx], y_prob)
        except ValueError:
            auc = 0.5
        aucs.append(auc)
    real_auc = np.mean(aucs)

    # Permutation test
    perm_aucs = []
    rng = np.random.RandomState(42)
    for _ in range(n_permutations):
        y_perm = rng.permutation(y)
        fold_aucs = []
        for train_idx, test_idx in cv.split(X, y_perm):
            clf = clf_factory()
            clf.fit(X[train_idx], y_perm[train_idx])
            if hasattr(clf, "predict_proba"):
                y_prob = clf.predict_proba(X[test_idx])[:, 1]
            else:
                y_prob = clf.decision_function(X[test_idx])
            try:
                auc = roc_auc_score(y_perm[test_idx], y_prob)
            except ValueError:
                auc = 0.5
            fold_aucs.append(auc)
        perm_aucs.append(np.mean(fold_aucs))

    p_value = np.mean(np.array(perm_aucs) >= real_auc)
    return real_auc, p_value, np.std(aucs)


def main():
    X_orc, X_oct_fc, X_oct_rsn, y = load_features()

    print(f"Dual Classifier — ABIDE-I (threshold={THRESHOLD})")
    print(f"Subjects: {len(y)} (ASD={np.sum(y==1)}, Control={np.sum(y==2)})")
    print(f"ORC features: {X_orc.shape[1]}, Octonion FC: {X_oct_fc.shape[1]}, "
          f"Octonion RSN: {X_oct_rsn.shape[1]}")
    print("=" * 60)

    # Feature sets
    feature_sets = {
        "ORC-only": X_orc,
        "Assoc-FC-only": X_oct_fc,
        "Assoc-RSN-only": X_oct_rsn,
        "Dual-FC": np.hstack([X_orc, X_oct_fc]),
        "Dual-RSN": np.hstack([X_orc, X_oct_rsn]),
        "Dual-Both": np.hstack([X_orc, X_oct_fc, X_oct_rsn]),
    }

    classifiers = {
        "GaussianNB": lambda: GaussianNB(),
        "KNN-5": lambda: make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=5)),
        "LinearSVM": lambda: make_pipeline(StandardScaler(), LinearSVC(max_iter=10000, random_state=42)),
    }

    results_all = {}
    for feat_name, X in feature_sets.items():
        results_all[feat_name] = {}
        for clf_name, clf_factory in classifiers.items():
            auc, p_val, auc_std = evaluate_classifier(X, y, clf_factory)
            results_all[feat_name][clf_name] = {
                "auroc": round(auc, 4),
                "auroc_std": round(auc_std, 4),
                "perm_p": round(p_val, 4),
            }
            print(f"  {feat_name:20s} + {clf_name:12s}: "
                  f"AUROC={auc:.3f}±{auc_std:.3f}, p={p_val:.3f}")
        print()

    # Best result per feature set
    print("=" * 60)
    print("Best AUROC per feature set:")
    for feat_name, clf_results in results_all.items():
        best_clf = max(clf_results, key=lambda k: clf_results[k]["auroc"])
        best = clf_results[best_clf]
        sig = "*" if best["perm_p"] < 0.05 else ""
        print(f"  {feat_name:20s}: {best['auroc']:.3f} ({best_clf}){sig}")

    # Key comparison: does associator add to ORC?
    print("\n" + "=" * 60)
    orc_best = max(results_all["ORC-only"].values(), key=lambda x: x["auroc"])["auroc"]
    for dual_name in ["Dual-FC", "Dual-RSN", "Dual-Both"]:
        dual_best = max(results_all[dual_name].values(), key=lambda x: x["auroc"])["auroc"]
        gain = dual_best - orc_best
        print(f"  {dual_name} vs ORC-only: Δ AUROC = {gain:+.3f}")

    # Save
    out_path = RESULTS_DIR / "abide_dual_classifier.json"
    with open(out_path, "w") as f:
        json.dump({
            "threshold": THRESHOLD,
            "n_subjects": len(y),
            "n_features": {k: v.shape[1] for k, v in feature_sets.items()},
            "results": results_all,
        }, f, indent=2)
    print(f"\nResults saved to: {out_path}")


if __name__ == "__main__":
    main()
