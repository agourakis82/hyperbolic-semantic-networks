# Progress Report: A3 + B2 Parallel Execution
**Date**: 2026-02-20  
**Tasks**: A3 (Sounio N=100 Validation) + B2 (HCP Data Download)

---

## A3: Sounio N=100 Validation

### Status: ⏳ RUNNING (background process)

**What's happening**:
- Compiling and running `phase_transition_n100.sio`
- Testing 15 k-values: k=2,3,4,6,8,10,12,14,16,18,20,25,30,35,40
- N=100 nodes per graph (vs N=20 in initial experiment)
- Expected runtime: 5-10 minutes

**Files created**:
- `experiments/01_epistemic_uncertainty/phase_transition_n100.sio` (394 lines)
  - Array sizes scaled up: adj[4000], deg[100], dist[10000], measure[41], cost/kmat[1681]
  - MAX_K=40 to match Julia reference values
- `experiments/01_epistemic_uncertainty/run_n100.sh` (run script)

**Validation targets** (Julia reference, N=200):
- k=3  → κ ≈ -0.303 (hyperbolic)
- k=22 → κ ≈ -0.013 (transition)
- k=40 → κ ≈ +0.073 (spherical)

**Expected output**:
- `results/sounio/phase_transition_n100.csv`
- CSV with columns: N,k,ratio,kappa_mean,kappa_std,std_err_mean,n_edges,pred,obs

**Success criteria**:
- ✓ Compilation successful (already verified)
- ⏳ Curvature values match Julia within ±0.05 (accounting for N=100 vs N=200)
- ⏳ Phase transition visible at k²/N ≈ 2.5 (k_crit ≈ 15.81 for N=100)

---

## B2: HCP Data Download

### Status: 📋 INSTRUCTIONS PROVIDED (manual download required)

**What's needed**:
- Download parcellated fMRI data for 10 HCP subjects
- Data type: CIFTI `.dtseries.nii` files (resting-state + language task)
- Total size: ~1-2 GB (100-200 MB per subject)

**Subjects to download**:
1. 100307
2. 100408
3. 101107
4. 101309
5. 101915
6. 103111
7. 103414
8. 103818
9. 105014
10. 105115

**Download methods**:

### Option A: Manual (ConnectomeDB) — RECOMMENDED
1. Go to: https://db.humanconnectome.org
2. Login with institutional credentials (already registered)
3. Navigate to: WU-Minn HCP Data - 1200 Subjects
4. For each subject, download 4 files:
   - `rfMRI_REST1_LR_Atlas_MSMAll.dtseries.nii`
   - `rfMRI_REST1_RL_Atlas_MSMAll.dtseries.nii`
   - `tfMRI_LANGUAGE_LR_Atlas_MSMAll.dtseries.nii`
   - `tfMRI_LANGUAGE_RL_Atlas_MSMAll.dtseries.nii`
5. Save to: `data/hcp/<subject_id>/`

### Option B: Automated (AWS S3)
```bash
# Requires AWS CLI
python code/fmri/download_hcp_data.py --method aws
```

**Files created**:
- `code/fmri/HCP_DOWNLOAD_GUIDE.md` (detailed instructions)
- `code/fmri/download_hcp_data.py` (automated download script)
- `code/fmri/README.md` (fMRI analysis overview)

**Verification**:
```bash
python code/fmri/download_hcp_data.py --method verify
```

**Next steps after download**:
- B3: Brain network construction (time series → connectivity matrix)
- B4: Compute brain network curvature
- B5: Semantic-brain correlation analysis

---

## Summary

### Completed
✅ A1: Sounio compiler setup  
✅ A2: Compile phase_transition.sio (N=20)  
✅ B1: HCP registration + Python tools  

### In Progress
⏳ **A3: Sounio N=100 validation** (running in background, ~5-10 min)  
📋 **B2: HCP data download** (manual download instructions provided)

### Next
- [ ] A3: Wait for N=100 results, validate against Julia
- [ ] B2: User downloads HCP data (or use AWS script)
- [ ] A4: SWOW real network loading
- [ ] B3: Brain network construction pipeline

---

## How to Check Progress

### A3 (Sounio N=100)
```bash
# Check if still running
ps aux | grep souc

# View partial results (if any)
tail -f results/sounio/phase_transition_n100.csv

# View build log
tail -f results/sounio/phase_transition_n100.log
```

### B2 (HCP Download)
```bash
# Check download status
python code/fmri/download_hcp_data.py --method verify

# Start AWS download (if preferred)
python code/fmri/download_hcp_data.py --method aws
```

---

**Estimated time to completion**:
- A3: 5-10 minutes (automated)
- B2: 2-3 hours (manual download, depends on network speed)

