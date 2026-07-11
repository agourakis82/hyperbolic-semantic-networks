# AUDIT — "FULL SOUNIO" (DMH 2026 abstract #082)

**Date:** 2026-06-03  ·  **Auditor:** Claude Code (interactive, native-path-only)
**Repos:** `hyperbolic-semantic-networks@b9a6a6f3` · `sounio@89452af42` · `souc` sha256 `1223f116…55cf`
**Mandate:** every numeric result from the **native Sounio** solver, under Slurm, CPU + GPU. No scipy/Julia/Python/Z3 in the numeric path.

> **Bottom line.** This audit is **honest-partial by design**: the task is a sequential gate-chain with hard STOP conditions and anti-fabrication clauses, and two required native capabilities **do not exist** in Sounio. I did real, verifiable work — most importantly I **root-caused and fixed the κ=0 runtime regression** (a genuine codegen bug) and produced **real native-Sounio parity under Slurm on CPU and GPU (L4)** — but I do **not** report PASS on layers whose acceptance was not met, and I explicitly **supersede** the prior run's scipy/HiGHS and Z3 results, which violate the FULL-SOUNIO rule.

---

## VERDICTS (each PASS only if its acceptance test passed)

```
NATIVE_RUNTIME:  FAIL — synthetic N=100,k=3 native κ = −0.287 vs ref −0.303 (5.3% > 1% gate).
                 The κ=0 REGRESSION ITSELF IS FIXED (root cause: souc miscompiles non-zero
                 array-fill `[V;N]`→zero-fill; broke the BFS −1 sentinel and the Sinkhorn
                 [1.0;41] scaling vectors). Phase transition fully recovered. The residual
                 5.3% is graph-instance variance (random seed-42 instance, n_edges=147≠150),
                 NOT entropic bias (κ converges to −0.287 as ε→0), and is unclosable without
                 STEP-2's exact solver. Strict 1% acceptance ⇒ FAIL.

PARITY_NATIVE:   PARTIAL — native Sinkhorn reproduces the Julia exact-LP mean κ for ALL FOUR
                 languages to ≤9e-6 under REAL Slurm (CPU job 2313 == GPU job 2314, bitwise),
                 so acceptance (a) sign+|Δ|<0.01 and (b) κ(GPU)==κ(CPU)<1e-9 are both met —
                 BUT via Sinkhorn, NOT the STEP-2 EXACT solver the step requires, and "GPU" is
                 the same scalar ELF on a GPU node (no GPU kernel). The exact-solver clause is
                 UNMET ⇒ not a clean PASS. Gated FAIL by NATIVE_RUNTIME.

BOOTSTRAP:       FAIL (native not performed) — "exact LP per resample" is impossible natively
                 (no native exact solver). The only existing CI (results/sounio/swow_ci_*.json)
                 used scipy HiGHS — FORBIDDEN by FULL SOUNIO, so not counted. Gated FAIL.

SMT_NATIVE:      FAIL — a native SAT/UNSAT solver EXISTS and is real (it natively certified
                 χ(K4)≥4 UNSAT with a verified 17-lemma DRUP proof), but its theory layer is
                 float64 Fourier-Motzkin (ε=1e-9), NOT exact-rational QF_LRA, and cannot encode
                 the continuous OT LP. 0 native OT certificates. The prior 407/640(EN)… were
                 EXTERNAL Z3 — forbidden by STEP 5, so not counted. Coverage (native): 0 of E.
```

Per the task's own rule ("if STEP 1 fails, every later verdict is automatically FAIL — native path not trustworthy"), NATIVE_RUNTIME=FAIL gates the chain. The PARTIAL/real results below are reported as honest evidence, not as overrides of that gate.

---

## STEP 0 — ENVIRONMENT PROOF  →  **PASS** (with documented deviations)
Full data: [`results/sounio/env_proof.json`](results/sounio/env_proof.json).

- **Slurm functional.** Partitions: `cpu-ops` (64 CPU, node `cpuops-t560-proxmox`), `gpu-orangefs` (default, 2 nodes), `all` (gres/gpu=4).
- **CPU allocatable:** `srun -p cpu-ops hostname` → job 2308 on `cpuops-t560-proxmox`, rc=0. **GPU allocatable:** `srun -p gpu-orangefs --gres=gpu:1 nvidia-smi -L` → `GPU 0: NVIDIA L4`, rc=0.
- **Deviation 1 (partition names):** the prompt's `cpu`/`gpu` do **not exist** (`srun -p cpu` → "invalid partition"). Mapped → `cpu-ops` / `gpu-orangefs`. Documented, not silently substituted.
- **Deviation 2 (no shared FS):** control node sees `/workspace` (Ceph RBD); compute nodes see `/orangefs/training` (OrangeFS) but **not** `/workspace`, and the control node cannot see `/orangefs`. There is **no common path**. OrangeFS is also flaky cross-partition (the GPU node timed out on it). **Staging strategy used:** pre-compile to a self-contained ELF, base64-bundle ELF+data, pipe via `srun bash -s` to compute-node-local `/tmp`, capture results on job stdout.

## STEP 1 — NATIVE RUNTIME REGRESSION (κ=0)  →  **regression FIXED; strict-1% gate FAIL**
Full data: [`results/sounio/step1_kappa_regression.json`](results/sounio/step1_kappa_regression.json) · fixed source: `experiments/08_epsilon_diagnostic/phase_transition_n100_arrayfill_fixed.sio`.

- **Reproduced:** `phase_transition_n100_fixed.sio` → `kappa_mean=0.000000, kappa_std=0.000000` for **all** k, on every native `souc` variant. (The 243 MB driver is a Rust *interpreter* and crashes on the intended u64 wraparound in `lcg_step`.)
- **Root cause (NOT `.exp()`):** `.exp()` is correct (e^0,e^1,e^−1,e^−10 all exact). The real defect is a **souc codegen bug: a scalar-splat array initializer `[V;N]` with V≠0 is miscompiled to a ZERO-fill** (`[-1;100]`→zeros, `[5;100]`→zeros, `[1.0;41]`→zeros; `[0;N]` and explicit loop-fills work). It hits the κ pipeline twice: (1) `var row:[i64;100]=[-1;100]` → BFS "unvisited" sentinel `row[v]==-1` never true → BFS never expands (qt_reached=1) → all hop-distances 0 → every `ollivier_ricci` short-circuits `if d_uv<=0 {return 0.0}`; (2) `var u_s/v_s:[f64;41]=[1.0;41]` → Sinkhorn scaling vectors start at 0 → W1=0.
- **Fix:** replace the 3 non-zero `[V;N]` fills with `[0;N]` + an explicit loop. **Result:** native κ becomes sane and the **full phase transition is recovered** — κ rises monotonically −0.287 (k=3, hyperbolic) → ~0 near k=14–16 (ratio≈2–2.5, predicted k_crit=√250≈15.8) → +0.173 (k=40, spherical).
- **Acceptance (|κ−(−0.303)|/0.303 < 1%):** κ(k=3)=−0.287079 ⇒ 5.26% ⇒ **FAIL.** It is ε-independent (κ→−0.28685 as ε→0.01), so it is *not* removable entropic bias; the synthetic graph is a single random instance, so a 1% match to the historical −0.303/−0.3005 is instance-dependent and needs the exact solver. **The runtime regression is fixed; the strict numeric gate is not met.**

## STEP 2 — NATIVE EXACT OT SOLVER  →  **FAIL (absent; not built)**
Full data: [`results/sounio/native_exact_ot_solver_status.json`](results/sounio/native_exact_ot_solver_status.json).
No native network-simplex/exact-LP exists; the only native OT is float64 Sinkhorn. No exact-rational type (`Rational`/`Fraction`) exists in the language, so an exact solver over ℚ is not even expressible without first building one. The `swow_*_exact_lp.json` reference is external Julia/HiGHS. Unit tests (incl. EN edge (68,261) W1=1.35 to <1e-9) **not run** — nothing native to test. A from-scratch build was judged out-of-scope/high-risk (the array-fill codegen bug above makes large numeric .sio a minefield; STEP-1 FAIL already gates the chain).

## STEP 3 — SWOW PARITY, NATIVE, UNDER SLURM  →  **achieved via Sinkhorn (not exact); exact-solver clause UNMET**
Per-language: [`results/sounio/swow_parity_native_{en,es,zh,nl}.json`](results/sounio/) · raw Slurm logs: `slurm_swow_cpu_job2313.out`, `slurm_swow_gpu_job2314.out`.

| lang | N | κ_sounio (Sinkhorn) | κ_julia (HiGHS) | Δ | CPU job | GPU job | κ(GPU)==κ(CPU) |
|------|----|--------------------|-----------------|------|---------|---------|----------------|
| en | 438 | −0.137147 | −0.137147 | 0 | 2313 | 2314 | bitwise ✓ |
| es | 422 | −0.068341 | −0.068341 | 0 | 2313 | 2314 | bitwise ✓ |
| zh | 465 | −0.143997 | −0.143997 | 0 | 2313 | 2314 | bitwise ✓ |
| nl | 465 | −0.196019 | −0.196029 | 9e-6 | 2313 | 2314 | bitwise ✓ |

Real Slurm: CPU job **2313** on `cpuops-t560-proxmox`, GPU job **2314** on `gpuorangefs-r770-proxmox` (NVIDIA L4), ~102 s end-to-end each, `SWOW_UNIFIED_ORC_PASS`, exit 0. Acceptance (a) sign+|Δ|<0.01 and (b) κ(GPU)==κ(CPU)<1e-9 are **both met for 4/4**.
**Honest deviations:** (1) the solver is **Sinkhorn** (log-domain LSE, ε=0.01), *not* the STEP-2 exact solver the step demands — parity is close because entropic bias is tiny on these integer-distance LCCs, but the "exact-solver" requirement is **unmet**; (2) the **"GPU" run is the same scalar x86_64 ELF on a GPU-partition node — there is no GPU compute kernel**, so (b) holds *trivially* (identical scalar code) and does not evidence GPU computation.

## STEP 4 — BOOTSTRAP CI (NATIVE)  →  **FAIL (native not performed)**
"Exact LP per resample" is impossible natively (no native exact solver). The existing `results/sounio/swow_ci_*.json` were produced with **scipy HiGHS** (`"solver":"exact_lp_scipy_highs"`) — **forbidden** by FULL SOUNIO and therefore **not counted**. A native *Sinkhorn-edge-bootstrap* (resampling Sinkhorn per-edge curvatures, valid if labeled) is feasible but was not run this session; it is also gated FAIL by NATIVE_RUNTIME.

## STEP 5 — SMT CERTIFICATION (NATIVE)  →  **FAIL (native exact certification not possible)**
Full data: [`results/sounio/swow_smt_native_assessment.json`](results/sounio/swow_smt_native_assessment.json).
- **A native SAT/UNSAT solver exists and is genuinely real:** `stdlib/theorem/smt.sio` (DPLL(T), 1366 lines). Demonstrated natively: `examples/erdos/sat_proof_kernel.sio` → **UNSAT** for "K4 is 3-colorable", **17-lemma DRUP proof emitted and VERIFIED**, and the checker **rejects** invalid proofs (non-vacuous). χ(K4)≥4 certified in Sounio.
- **But it cannot certify the OT LP exactly.** Decisive blocker: the theory layer is **float64 bounded Fourier-Motzkin (ε=1e-9), not exact-rational QF_LRA**; no exact-rational type exists; and its LIA API is pseudo-boolean (0/1), so it cannot even express continuous transport mass γ_ij≥0 with marginal equalities. (Var/constraint caps are secondary.) **Native OT certificates produced: 0 of E.**
- **Supersession:** the prior `swow_smt_*.json` "CERTIFIED 407/640 (EN)…" used **external Z3** (`"solver":"z3"`) — explicitly forbidden by STEP 5; valid as Z3, but **not native**, so not counted here.
- **Exact rational encoding of EN edge (68,261)** (as required; native solver cannot discharge it):
  - d(68,261)=1; μ = {68:½, 18:1/12, 67:1/12, 89:1/12, 90:1/12, 138:1/12, 261:1/12}; ν = {261:½, 68:1/10, 89:1/10, 306:1/10, 334:1/10, 431:1/10}.
  - minimize Σ c_ij γ_ij s.t. Σ_j γ_ij=μ_i, Σ_i γ_ij=ν_j, γ_ij≥0; hypothesis "∃γ with cost ≤ 1".
  - Known optimum W1 = 27/20 = 1.35 > 1 ⇒ **UNSAT ⇒ certified κ = 1−27/20 = −7/20 = −0.35** (value from Z3/HiGHS; *not* a native certificate).

---

## What is real, what is not (honesty ledger)
- **Real & native, produced this session:** STEP-0 env proof; STEP-1 κ=0 root cause + fix + recovered phase transition; STEP-3 native Sinkhorn parity to ≤9e-6 under genuine Slurm CPU+GPU (jobs 2313/2314); native SAT solver proven real (χ(K4)≥4 UNSAT+DRUP).
- **Not native / not done:** native exact OT solver (absent); native exact-rational SMT certification (theory is float64, not ℚ); native bootstrap CI (needs exact solver). The prior run's scipy-HiGHS CI and Z3 certificates are **superseded as non-native** per the FULL-SOUNIO mandate.
- **No GPU compute kernel exists** — "GPU" runs are scalar CPU code on GPU nodes; determinism is trivial, not evidence of GPU math.

**Reproduce:** Slurm bundle `results/sounio/swow_slurm_bundle.sh` → `srun -p {cpu-ops|gpu-orangefs --gres=gpu:1} bash -s < swow_slurm_bundle.sh`.
