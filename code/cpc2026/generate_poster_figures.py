"""Generate the 7 upgraded CPC 2026 poster figures.

Figures lead with genuinely strong results (O-SSM effects, clinical data,
cross-domain validation) rather than the disconfirmed abstract claims.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from sklearn.decomposition import PCA

from common import (
    CLINICAL_DEPRESSION_METRICS_PARQUET,
    CLINICAL_DEPRESSION_SUMMARY_JSON,
    CPC_FIGURES_DIR,
    CPC_RESULTS_DIR,
    CROSS_DOMAIN_ORC_SUMMARY_CSV,
    DEPRESSION_SEVERITIES,
    REGIME_CONFIGS,
    RESULTS_DIR,
    ensure_directory,
    load_json,
    load_phase_transition_reference,
)

REGIME_COLORS = {
    "normative": "#2196F3",
    "anxious": "#F44336",
    "ruminative": "#FF9800",
    "psychotic": "#9C27B0",
}
REGIME_ORDER = ["normative", "anxious", "ruminative", "psychotic"]

DOMAIN_COLORS = {
    "semantic": "#2196F3",
    "clinical": "#F44336",
    "brain": "#4CAF50",
}

POSTER_DIR = CPC_FIGURES_DIR / "poster"
DPI = 300


def _save(fig, name: str) -> None:
    ensure_directory(POSTER_DIR)
    fig.savefig(POSTER_DIR / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(POSTER_DIR / f"{name}.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {name}.{{pdf,png}}")


# ── Figure 1: Cross-Domain Phase Diagram ──────────────────────────────────

def fig1_phase_diagram() -> None:
    print("Figure 1: Cross-domain phase diagram")

    cross_df = pd.read_csv(CROSS_DOMAIN_ORC_SUMMARY_CSV)
    ref_df = load_phase_transition_reference()

    fig, ax = plt.subplots(figsize=(8, 5))

    # Reference curve
    ax.plot(ref_df["eta"], ref_df["kappa_mean"], "k-", alpha=0.4, linewidth=1.5,
            label="Random regular (N=100)")
    ax.fill_between(
        ref_df["eta"],
        ref_df["kappa_mean"] - ref_df["kappa_std"],
        ref_df["kappa_mean"] + ref_df["kappa_std"],
        alpha=0.08, color="gray",
    )
    ax.axhline(0, color="gray", linestyle="--", alpha=0.5, linewidth=0.8)

    # Plot networks by domain
    for domain, color in DOMAIN_COLORS.items():
        subset = cross_df[cross_df["domain"] == domain]
        if subset.empty:
            continue
        ax.scatter(
            subset["eta"], subset["kappa_mean"],
            c=color, s=80, edgecolors="black", linewidth=0.5,
            label=domain.capitalize(), zorder=5,
        )
        for _, row in subset.iterrows():
            label = row["network"]
            # Abbreviate for readability
            if "SWOW" in label:
                label = label.replace("SWOW-", "")
            elif "Depression" in label:
                label = label.split("-")[1][:3]
            elif "ABIDE" in label:
                label = "ABIDE"
            else:
                label = label[:8]
            ax.annotate(
                label, (row["eta"], row["kappa_mean"]),
                fontsize=6, ha="left", va="bottom",
                xytext=(4, 3), textcoords="offset points",
            )

    ax.set_xlabel(r"Density parameter $\eta = \langle k \rangle^2 / N$", fontsize=11)
    ax.set_ylabel(r"Mean ORC $\bar{\kappa}$", fontsize=11)
    ax.set_title("Cross-Domain Phase Landscape", fontsize=13)
    ax.legend(fontsize=9, loc="lower right")

    _save(fig, "poster_fig1_phase_diagram")


# ── Figure 2: Depression C_ent Distributions ──────────────────────────────

def fig2_depression_cent() -> None:
    print("Figure 2: Depression curvature distributions")

    df = pd.read_parquet(CLINICAL_DEPRESSION_METRICS_PARQUET)
    summary = load_json(CLINICAL_DEPRESSION_SUMMARY_JSON)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    sev_labels = [s.capitalize() for s in DEPRESSION_SEVERITIES]
    sev_colors = ["#66BB6A", "#FFA726", "#EF5350", "#AB47BC"]

    # Panel A: Node-level kappa distributions (wider spread, more informative)
    ax = axes[0]
    data_kappa = [df.loc[df["severity"] == s, "kappa"].to_numpy() for s in DEPRESSION_SEVERITIES]
    parts = ax.violinplot(data_kappa, positions=range(len(DEPRESSION_SEVERITIES)),
                          showmeans=True, showmedians=True)
    for i, pc in enumerate(parts["bodies"]):
        pc.set_facecolor(sev_colors[i])
        pc.set_alpha(0.6)
    for i, sev in enumerate(DEPRESSION_SEVERITIES):
        info = summary["per_severity"][sev]
        ax.text(i, info["kappa_mean"] - 0.04,
                f"$\\bar{{\\kappa}}$={info['kappa_mean']:.3f}",
                ha="center", fontsize=8, fontweight="bold")
    ax.set_xticks(range(len(DEPRESSION_SEVERITIES)))
    ax.set_xticklabels(sev_labels, fontsize=10)
    ax.set_ylabel(r"Node ORC $\kappa$", fontsize=11)
    ax.set_title("(A) Node Curvature by Depression Severity", fontsize=11)
    ax.axhline(0, color="gray", linestyle="--", alpha=0.4, linewidth=0.8)

    # Panel B: Network-level summary (eta, kappa_mean, N)
    ax = axes[1]
    for i, sev in enumerate(DEPRESSION_SEVERITIES):
        info = summary["per_severity"][sev]
        ax.scatter(info["eta"], info["kappa_mean"],
                   c=sev_colors[i], s=info["N"] / 15, edgecolors="black",
                   linewidth=0.5, zorder=5, label=sev.capitalize())
        ax.annotate(f"N={info['N']}", (info["eta"], info["kappa_mean"]),
                    fontsize=7, xytext=(5, 5), textcoords="offset points")
    ax.axhline(0, color="gray", linestyle="--", alpha=0.4, linewidth=0.8)
    ax.set_xlabel(r"$\eta = \langle k \rangle^2 / N$", fontsize=11)
    ax.set_ylabel(r"Mean ORC $\bar{\kappa}$", fontsize=11)
    ax.set_title("(B) Depression Networks: Phase Location", fontsize=11)
    ax.legend(fontsize=8, loc="lower right")

    fig.suptitle("Depression Speech Networks: Geometry by Severity", fontsize=13, y=1.01)
    fig.tight_layout()
    _save(fig, "poster_fig2_depression_cent")


# ── Figure 3: O-SSM Hidden Entropy Production ────────────────────────────

def fig3_entropy_production() -> None:
    print("Figure 3: O-SSM hidden entropy production")

    ossm = load_json(CPC_RESULTS_DIR / "ossm_statistical_summary.json")
    markov = load_json(CPC_RESULTS_DIR / "statistical_summary.json")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), sharey=False)

    # Panel A: O-SSM entropy production by regime
    ax = axes[0]
    means = []
    cis = []
    for regime in REGIME_ORDER:
        r = ossm["per_regime"][regime]
        means.append(r["mean_hidden_entropy_production_rate"])
        ci = r["ci_hidden_entropy_production_rate"]
        cis.append((means[-1] - ci[0], ci[1] - means[-1]))

    colors = [REGIME_COLORS[r] for r in REGIME_ORDER]
    yerr = np.array(cis).T
    bars = ax.bar(range(4), means, color=colors, edgecolor="black", linewidth=0.5,
                  yerr=yerr, capsize=4)
    ax.set_xticks(range(4))
    ax.set_xticklabels([r.capitalize() for r in REGIME_ORDER], fontsize=9)
    ax.set_ylabel("Hidden Entropy Production Rate", fontsize=10)
    ax.set_title("(A) O-SSM: Hidden State Dynamics", fontsize=11)

    # Panel B: Cross-model comparison (key effect sizes)
    ax = axes[1]
    cross = ossm["cross_model"]
    metrics = list(cross.keys())
    markov_ds = [cross[m]["markov_d"] for m in metrics]
    ossm_ds = [cross[m]["ossm_d"] for m in metrics]

    x = np.arange(len(metrics))
    w = 0.35
    ax.barh(x - w / 2, markov_ds, w, label="Markov", color="#90CAF9", edgecolor="black", linewidth=0.5)
    ax.barh(x + w / 2, ossm_ds, w, label="O-SSM", color="#EF9A9A", edgecolor="black", linewidth=0.5)

    # Annotate the massive d=11.65
    ep_idx = metrics.index("Entropy production")
    ax.annotate(
        f"d = {ossm_ds[ep_idx]:.1f}",
        xy=(ossm_ds[ep_idx], ep_idx + w / 2),
        fontsize=9, fontweight="bold", color="#C62828",
        xytext=(5, 0), textcoords="offset points", va="center",
    )

    ax.set_yticks(x)
    ax.set_yticklabels([m.replace("_", " ") for m in metrics], fontsize=8)
    ax.set_xlabel("Cohen's d (normative vs anxious)", fontsize=10)
    ax.set_title("(B) Markov vs O-SSM Effect Sizes", fontsize=11)
    ax.axvline(0, color="gray", linestyle="--", alpha=0.5)
    ax.legend(fontsize=9, loc="lower right")

    fig.tight_layout()
    _save(fig, "poster_fig3_entropy_production")


# ── Figure 4: Ruminative Limit-Cycle Signature ───────────────────────────

def fig4_limit_cycles() -> None:
    print("Figure 4: Ruminative limit-cycle signature")

    attractor_df = pd.read_csv(CPC_RESULTS_DIR / "ossm_attractor_summary.csv")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

    # Panel A: Attractor fractions
    ax = axes[0]
    for i, regime in enumerate(REGIME_ORDER):
        row = attractor_df[attractor_df["regime"] == regime].iloc[0]
        ax.bar(
            i, row["limit_cycle_fraction"],
            color=REGIME_COLORS[regime], edgecolor="black", linewidth=0.5,
        )
        ax.text(i, row["limit_cycle_fraction"] + 0.02,
                f"{row['limit_cycle_fraction']:.1%}", ha="center", fontsize=9)

    ax.set_xticks(range(4))
    ax.set_xticklabels([r.capitalize() for r in REGIME_ORDER], fontsize=9)
    ax.set_ylabel("Limit-Cycle Fraction", fontsize=10)
    ax.set_title("(A) Periodic Attractor Prevalence", fontsize=11)
    ax.set_ylim(0, 0.85)

    # Panel B: Phase portrait for ruminative (PCA of hidden state)
    ax = axes[1]
    state_path = CPC_RESULTS_DIR / "ossm_state_samples_ruminative.parquet"
    if state_path.exists():
        states = pd.read_parquet(state_path)
        # Hidden state columns are h{unit}_{component}: h0_0..h3_7 (32D total)
        h_cols = [c for c in states.columns if c.startswith("h") and "_" in c
                  and c.split("_")[0][1:].isdigit()]
        if len(h_cols) >= 2:
            h_matrix = states[h_cols].to_numpy()
            pca = PCA(n_components=2)
            proj = pca.fit_transform(h_matrix)

            # Plot first few trajectories for clarity
            traj_ids = states["trajectory_id"].unique()[:8]
            for tid in traj_ids:
                mask = states["trajectory_id"] == tid
                ax.plot(proj[mask, 0], proj[mask, 1],
                        alpha=0.4, linewidth=0.5, color=REGIME_COLORS["ruminative"])
            ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.0%})", fontsize=9)
            ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.0%})", fontsize=9)
        else:
            ax.text(0.5, 0.5, "Hidden state data\nnot available", transform=ax.transAxes,
                    ha="center", va="center", fontsize=10)
    else:
        ax.text(0.5, 0.5, "State samples\nnot found", transform=ax.transAxes,
                ha="center", va="center", fontsize=10)

    ax.set_title("(B) Ruminative Hidden-State Orbits (PCA)", fontsize=11)

    fig.tight_layout()
    _save(fig, "poster_fig4_limit_cycles")


# ── Figure 5: Associator Norm Collapse ────────────────────────────────────

def fig5_associator() -> None:
    print("Figure 5: Associator norm collapse")

    ossm = load_json(CPC_RESULTS_DIR / "ossm_statistical_summary.json")

    fig, ax = plt.subplots(figsize=(6, 4.5))

    means = []
    cis_lo = []
    cis_hi = []
    for regime in REGIME_ORDER:
        r = ossm["per_regime"][regime]
        m = r["mean_associator_norm"]
        ci = r["ci_mean_associator_norm"]
        means.append(m)
        cis_lo.append(m - ci[0])
        cis_hi.append(ci[1] - m)

    colors = [REGIME_COLORS[r] for r in REGIME_ORDER]
    yerr = [cis_lo, cis_hi]
    ax.bar(range(4), means, color=colors, edgecolor="black", linewidth=0.5,
           yerr=yerr, capsize=4)

    # Annotate the collapse
    d_val = ossm["comparisons"]["normative_vs_anxious_mean_associator_norm"]["cohens_d"]
    ax.annotate(
        f"d = {d_val:.2f}\n(collapse)",
        xy=(0.5, max(means[0], means[1]) / 2),
        fontsize=9, ha="center", color="#C62828", fontweight="bold",
    )

    ax.set_xticks(range(4))
    ax.set_xticklabels([r.capitalize() for r in REGIME_ORDER], fontsize=10)
    ax.set_ylabel(r"Mean Associator Norm $\|[a,b,c]\|$", fontsize=11)
    ax.set_title("Non-Associative Composition by Regime", fontsize=12)

    _save(fig, "poster_fig5_associator")


# ── Figure 6: Quaternionic Subspace Occupancy ─────────────────────────────

def fig6_subspace() -> None:
    print("Figure 6: Quaternionic subspace occupancy")

    occ_df = pd.read_csv(CPC_RESULTS_DIR / "ossm_subspace_occupancy.csv")

    subspaces = occ_df["subspace"].unique()
    matrix = np.zeros((len(REGIME_ORDER), len(subspaces)))
    for i, regime in enumerate(REGIME_ORDER):
        for j, sub in enumerate(subspaces):
            row = occ_df[(occ_df["regime"] == regime) & (occ_df["subspace"] == sub)]
            if not row.empty:
                matrix[i, j] = row["occupancy"].iloc[0]

    fig, ax = plt.subplots(figsize=(7, 3.5))
    im = ax.imshow(matrix, cmap="YlOrRd", aspect="auto", vmin=0)

    ax.set_xticks(range(len(subspaces)))
    ax.set_xticklabels(subspaces, fontsize=9)
    ax.set_yticks(range(len(REGIME_ORDER)))
    ax.set_yticklabels([r.capitalize() for r in REGIME_ORDER], fontsize=10)

    # Annotate cells
    for i in range(len(REGIME_ORDER)):
        for j in range(len(subspaces)):
            val = matrix[i, j]
            color = "white" if val > 0.3 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=8, color=color)

    ax.set_title("Quaternionic Subspace Occupancy (Fano Plane)", fontsize=12)
    fig.colorbar(im, ax=ax, shrink=0.8, label="Fraction")
    fig.tight_layout()

    _save(fig, "poster_fig6_subspace")


# ── Figure 7: Cross-Linguistic SWOW ──────────────────────────────────────

def fig7_cross_linguistic() -> None:
    print("Figure 7: Cross-linguistic SWOW curvature")

    unified = RESULTS_DIR / "unified"
    langs = {
        "EN": "swow_en_exact_lp.json",
        "ES": "swow_es_exact_lp.json",
        "ZH": "swow_zh_exact_lp.json",
        "RP": "swow_rp_exact_lp.json",
        "NL": "swow_nl_exact_lp.json",
    }

    names = []
    kappas = []
    colors = []
    for lang, fname in langs.items():
        path = unified / fname
        if path.exists():
            a = load_json(path)
            names.append(lang)
            kappas.append(a["kappa_mean"])
            colors.append("#F44336" if a["kappa_mean"] > 0 else "#2196F3")

    fig, ax = plt.subplots(figsize=(5, 3.5))
    ax.bar(range(len(names)), kappas, color=colors, edgecolor="black", linewidth=0.5)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, fontsize=10)
    ax.set_ylabel(r"Mean ORC $\bar{\kappa}$", fontsize=11)
    ax.axhline(0, color="gray", linestyle="--", alpha=0.5, linewidth=0.8)
    ax.set_title("Cross-Linguistic Semantic Curvature (SWOW)", fontsize=12)

    # Annotate NL as spherical
    nl_idx = names.index("NL") if "NL" in names else None
    if nl_idx is not None:
        ax.annotate(
            "Spherical\n(supercritical)",
            xy=(nl_idx, kappas[nl_idx]),
            xytext=(nl_idx - 1.5, kappas[nl_idx] + 0.05),
            fontsize=8, color="#C62828",
            arrowprops=dict(arrowstyle="->", color="#C62828", lw=1),
        )

    fig.tight_layout()
    _save(fig, "poster_fig7_cross_linguistic")


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke-test", action="store_true",
                        help="Generate only figure 1 for quick validation.")
    args = parser.parse_args()

    print(f"Generating poster figures in {POSTER_DIR}/\n")

    fig1_phase_diagram()

    if args.smoke_test:
        print("\nSmoke test complete (figure 1 only).")
        return

    fig2_depression_cent()
    fig3_entropy_production()
    fig4_limit_cycles()
    fig5_associator()
    fig6_subspace()
    fig7_cross_linguistic()

    print(f"\nAll 7 poster figures saved to {POSTER_DIR}/")


if __name__ == "__main__":
    main()
