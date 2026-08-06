# Depression Ollivier-Ricci Curvature Exploratory Network Geometry Scope Gate

## Conference-Safe Claim

This artifact is a repository-backed scope gate, not a clinical or statistical results claim. It records that the current CPC 2026 Ollivier-Ricci curvature and entropic-curvature outputs are graph-level exploratory aggregates and defines the next falsification-oriented experiments.

## Executable Hooks

- Python gate: `code/cpc2026/network_geometry_claim_gate.py`
- Sounio spine: `experiments/sounio_cpc2026/depression_orc_claim.sio`
- Integrated gate: `code/cpc2026/sounio_claim_gate.py`
- Machine-readable status: `results/cpc2026/depression_orc_network_geometry_scope_gate.json` and `results/cpc2026/sounio_depression_orc_claim_gate.json`

## Scope Observations

- Source groups are four severity-labelled semantic networks treated here as nominal graph labels: `mild, minimum, moderate, severe`
- Graph size by source group (`N` nodes, `E` edges): `{'mild': {'N': 3089, 'E': 39840}, 'minimum': {'N': 1634, 'E': 11354}, 'moderate': {'N': 2238, 'E': 24109}, 'severe': {'N': 2685, 'E': 32168}}`
- Numeric ORC/C_ent tables and bootstrap metadata remain in the machine-readable JSON artifacts.
- This memo intentionally does not interpret ORC/C_ent intervals, contrasts, or signs as graph-construction, cohort, clinical, or patient-level uncertainty.
- External-facing interpretation is blocked until null models, resampling units, and size controls are specified.

## Required Boundaries

- This is an exploratory network-geometry scope gate, not a biomarker-candidate claim or validated clinical biomarker.
- This does not claim diagnosis, clinical utility, patient-level prediction, or treatment selection.
- Severity labels are nominal graph labels in this memo; no monotonic severity trend is claimed.
- Context of use: exploratory research and conference hypothesis generation, not clinical decision-making.
- The observations are suitable for audit-trail bookkeeping and next-experiment design only.
- External validation would require independent cohorts, preregistered endpoints, patient-level performance metrics, and a defined context of use.
- Monotonicity assumption: not established; the current group means are non-monotonic and require formal trend testing before any ordered-severity claim.

## Limitations

- Target external cohort: TBD; no access agreement or validation cohort is claimed here. A future cohort must specify language, diagnostic ascertainment, age range, and comorbidity exclusions before confirmatory analysis.
- No degree-preserving, permutation, or other null-model comparison is included in this artifact.
- Negative ORC values are not interpreted against a meaningful semantic-graph null model in this memo.
- Current ORC and C_ent summaries are graph-level aggregate metrics, not patient-level measurements.
- Pairwise C_ent contrasts are recorded internally but are not interpreted as inferential effect sizes here.
- Preregistered margins remain undefined; future continuous severity models and future binary endpoint models require separately justified thresholds.

## Next Falsifiable Experiments

- H1 null-model test: for each source graph, compare observed mean ORC against at least 100 degree-preserving random graphs; only proceed if preregistered z-score or empirical-p thresholds are met after size/density checks.
- H2 size-control test: repeat ORC/C_ent estimates on size-matched subgraphs or include graph size and density as covariates before interpreting between-group differences.
- H3 individual-level test: if per-subject graphs become available, evaluate whether ORC/C_ent features improve a preregistered severity or outcome model beyond graph size/density baselines.
- Context-of-use gate: choose screening, prognosis, monitoring, or response modeling before any marker or biomarker language is allowed.

