#!/usr/bin/env python3
"""
PATIENT VS CONTROL ANALYSIS
Compare depression data against healthy baseline
"""

import pandas as pd
import numpy as np
import json
import scipy.stats as stats

print("="*70)
print("PATIENT VS. CONTROL ANALYSIS")
print("="*70)
print()

# Load healthy baseline
print("Loading healthy baseline...")
with open('results/healthy_controls_swow.json', 'r') as f:
    healthy = json.load(f)

C_healthy = healthy['statistics']['mean_clustering']
C_healthy_std = healthy['statistics']['std_clustering']

print(f"  Healthy baseline: C = {C_healthy:.4f} ± {C_healthy_std:.4f}")
print()

# Load depression data
print("Loading depression data...")
df_dep = pd.read_csv('results/depression_optimal_metrics.csv')

print(f"  Depression levels: {len(df_dep)}")
print()

# Perform comparisons
print("="*70)
print("PATIENT VS. CONTROL COMPARISON")
print("="*70)
print()

results = []

for _, row in df_dep.iterrows():
    severity = row['severity']
    C_patient = row['clustering']
    
    # Effect size (Cohen's d)
    # Using pooled std (assume similar variance)
    pooled_std = np.sqrt((C_healthy_std**2 + 0.005**2) / 2)  # Assume std for single measure
    cohens_d = (C_patient - C_healthy) / pooled_std if pooled_std > 0 else 0
    
    # Percent difference
    pct_diff = ((C_patient - C_healthy) / C_healthy) * 100
    
    # Absolute difference
    abs_diff = C_patient - C_healthy
    
    # Z-score
    z_score = abs_diff / C_healthy_std if C_healthy_std > 0 else 0
    
    # Interpretation
    if abs(cohens_d) < 0.2:
        effect = "Negligible"
    elif abs(cohens_d) < 0.5:
        effect = "Small"
    elif abs(cohens_d) < 0.8:
        effect = "Medium"
    else:
        effect = "Large"
    
    # Direction
    if C_patient > C_healthy:
        direction = "↑ HIGHER (preserved/elevated)"
    elif C_patient < C_healthy:
        direction = "↓ LOWER (disrupted)"
    else:
        direction = "= SAME"
    
    results.append({
        'severity': severity,
        'C_patient': C_patient,
        'C_healthy': C_healthy,
        'difference': abs_diff,
        'percent_diff': pct_diff,
        'cohens_d': cohens_d,
        'z_score': z_score,
        'effect_size': effect,
        'direction': direction
    })
    
    print(f"{severity.upper():12s}")
    print(f"  Patient:  C = {C_patient:.4f}")
    print(f"  Healthy:  C = {C_healthy:.4f}")
    print(f"  Diff:     Δ = {abs_diff:+.4f} ({pct_diff:+.1f}%)")
    print(f"  Cohen's d: {cohens_d:+.2f} ({effect})")
    print(f"  Z-score:   {z_score:+.2f}σ")
    print(f"  Status:    {direction}")
    print()

# Save results
df_results = pd.DataFrame(results)
df_results.to_csv('results/patient_vs_control_comparison.csv', index=False)

print("="*70)
print("SUMMARY")
print("="*70)
print()

# Overall pattern
mean_diff = df_results['difference'].mean()
mean_pct = df_results['percent_diff'].mean()

print(f"Average difference: {mean_diff:+.4f} ({mean_pct:+.1f}%)")
print()

# Count by direction
n_lower = sum(df_results['difference'] < 0)
n_higher = sum(df_results['difference'] > 0)
n_same = sum(df_results['difference'] == 0)

print(f"Distribution:")
print(f"  Lower than healthy:  {n_lower}/{len(df_results)}")
print(f"  Higher than healthy: {n_higher}/{len(df_results)}")
print(f"  Same as healthy:     {n_same}/{len(df_results)}")
print()

# Clinical interpretation
print("="*70)
print("CLINICAL INTERPRETATION")
print("="*70)
print()

print("🔍 Key Findings:")
print()

for _, row in df_results.iterrows():
    sev = row['severity']
    diff = row['difference']
    effect = row['effect_size']
    
    if diff > 0:
        print(f"  • {sev.capitalize()}: PRESERVED/ELEVATED clustering")
        print(f"    → May represent compensatory mechanism or subclinical")
    elif diff < -0.005:  # More than 0.005 below
        print(f"  • {sev.capitalize()}: DISRUPTED clustering ({effect} effect)")
        print(f"    → Network fragmentation consistent with pathology")
    else:
        print(f"  • {sev.capitalize()}: SIMILAR to healthy baseline")
        print(f"    → Borderline or early stage")
    print()

print("✅ Saved: results/patient_vs_control_comparison.csv")
print()

print("="*70)
print("✅ PATIENT VS. CONTROL ANALYSIS COMPLETE!")
print("="*70)

