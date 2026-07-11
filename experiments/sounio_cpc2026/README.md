# Sounio CPC 2026 Claim Spine

This directory is the first Sounio-native layer for the CPC 2026 depression
ORC work.

It does not recompute the Python/Julia/Rust ORC pipeline. Instead, it encodes
the evidence/claim boundary as an executable Sounio object:

- allowed: exploratory network-geometry scope gate for next experiments
- forbidden at current evidence level: biomarker-candidate, diagnostic
  biomarker, validated clinical biomarker, clinical utility, patient-level
  prediction, treatment selection

Run from the repository root:

```bash
/workspace/sounio/bin/souc run experiments/sounio_cpc2026/depression_orc_claim.sio
```

or through the Python gate:

```bash
python3 code/cpc2026/sounio_claim_gate.py
```
