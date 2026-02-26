# fMRI Data Download Guide
# Hyperbolic Semantic Networks - fMRI Integration

**Goal**: Download resting-state fMRI data for proof-of-concept brain connectivity analysis.

**UPDATED**: Using OpenNeuro datasets (easier access than HCP)

**Target Data**:
- **Source**: OpenNeuro (https://openneuro.org)
- **Parcellation**: Will apply Schaefer 400 regions during preprocessing
- **Modality**: Resting-state fMRI
- **Subjects**: 10-20 subjects (proof-of-concept)
- **Size**: ~50-100 MB per subject (preprocessed)

---

## Option 1: OpenNeuro Datasets (RECOMMENDED - Easy Access)

### Dataset Options:

**A. ds000228 - Resting-state fMRI (UCLA Consortium)**
- URL: https://openneuro.org/datasets/ds000228
- Subjects: 122 healthy adults
- Preprocessed: Available via fMRIPrep
- Download: Direct via browser or AWS S3

**B. ds005747 - 7T Resting-state fMRI**
- URL: https://openneuro.org/datasets/ds005747
- High-resolution 7T data
- Smaller sample size but higher quality

**C. ds000030 - UCLA CNP (Consortium for Neuropsychiatric Phenomics)**
- URL: https://openneuro.org/datasets/ds000030
- Large sample, well-validated
- Multiple tasks + resting-state

### Download from OpenNeuro:

```bash
# Install DataLad (OpenNeuro uses DataLad for downloads)
pip install datalad

# Clone dataset (example: ds000228)
datalad clone https://github.com/OpenNeuroDatasets/ds000228.git data/openneuro/ds000228

# Download specific subjects (first 10)
cd data/openneuro/ds000228
datalad get sub-pixar001/func/*rest*.nii.gz
datalad get sub-pixar002/func/*rest*.nii.gz
# ... repeat for 10 subjects
```

**OR use direct download** (no DataLad needed):

```bash
# Download via AWS S3 (OpenNeuro mirror)
aws s3 sync \
  s3://openneuro.org/ds000228 \
  data/openneuro/ds000228 \
  --no-sign-request \
  --exclude "*" \
  --include "sub-pixar00[1-9]/func/*rest*.nii.gz" \
  --include "sub-pixar010/func/*rest*.nii.gz"
```

---

## Option 2: HCP Data (Original Plan - Requires Registration)

### ⚠️ Note: HCP download requires institutional access and is more complex

---

## Step 1: Access HCP Data via ConnectomeDB

### Option A: Direct Download via ConnectomeDB (Recommended)

1. **Login to ConnectomeDB**:
   - URL: https://db.humanconnectome.org
   - Use your institutional credentials (you mentioned already registered for BALSA)

2. **Navigate to S1200 Release**:
   - Go to "WU-Minn HCP Data - 1200 Subjects"
   - Filter: "Structural Preprocessed" + "Functional Preprocessed"

3. **Download Parcellated Time Series**:
   - Look for: `<subject_id>_rfMRI_REST_Atlas_MSMAll.dtseries.nii` (resting-state)
   - Look for: `<subject_id>_tfMRI_LANGUAGE_Atlas_MSMAll.dtseries.nii` (language task)
   - These are CIFTI files with parcellated data

4. **Subject Selection** (10 subjects for proof-of-concept):
   - Recommended: 100307, 100408, 101107, 101309, 101915, 103111, 103414, 103818, 105014, 105115
   - These are from the first batch, well-validated

### Option B: AWS S3 Bucket (Faster for bulk download)

HCP data is mirrored on AWS S3 (free egress for research):

```bash
# Install AWS CLI
pip install awscli

# Configure (no credentials needed for public HCP bucket)
aws configure set default.s3.signature_version s3v4

# Download example subject 100307
aws s3 sync \
  s3://hcp-openaccess/HCP_1200/100307/MNINonLinear/Results/ \
  data/hcp/100307/ \
  --no-sign-request \
  --exclude "*" \
  --include "*rfMRI_REST*Atlas*.dtseries.nii" \
  --include "*tfMRI_LANGUAGE*Atlas*.dtseries.nii"
```

---

## Step 2: Extract Parcellated Time Series

Once you have the `.dtseries.nii` CIFTI files, use `nibabel` to extract time series:

```python
import nibabel as nib
import numpy as np

# Load CIFTI file
cifti = nib.load('data/hcp/100307/rfMRI_REST1_LR_Atlas_MSMAll.dtseries.nii')
data = cifti.get_fdata()  # Shape: (timepoints, grayordinates)

# For Schaefer 400: extract first 400 parcels
# (Assuming parcellation is in the CIFTI structure)
# You may need to use workbench_command to apply Schaefer parcellation
```

**Alternative**: Use HCP Pipelines' pre-parcellated outputs if available.

---

## Step 3: Verify Data Structure

Expected directory structure:
```
data/hcp/
├── 100307/
│   ├── rfMRI_REST1_LR_timeseries_schaefer400.npy
│   ├── rfMRI_REST1_RL_timeseries_schaefer400.npy
│   ├── tfMRI_LANGUAGE_LR_timeseries_schaefer400.npy
│   └── tfMRI_LANGUAGE_RL_timeseries_schaefer400.npy
├── 100408/
│   └── ...
└── ...
```

Each `.npy` file: shape `(n_timepoints, 400)` for Schaefer 400 parcellation.

---

## Step 4: Automated Download Script

See `code/fmri/download_hcp_data.py` for automated download of 10 subjects.

---

## Troubleshooting

**Issue**: CIFTI files don't have Schaefer parcellation
- **Solution**: Use Connectome Workbench to apply Schaefer atlas:
  ```bash
  wb_command -cifti-parcellate \
    input.dtseries.nii \
    Schaefer2018_400Parcels_7Networks.dlabel.nii \
    COLUMN \
    output_schaefer400.ptseries.nii
  ```

**Issue**: AWS download fails
- **Solution**: Use ConnectomeDB web interface for manual download

**Issue**: Need Schaefer atlas file
- **Solution**: Download from https://github.com/ThomasYeoLab/CBIG/tree/master/stable_projects/brain_parcellation/Schaefer2018_LocalGlobal

---

## Next Steps

After downloading data:
1. Run `code/fmri/brain_network_construction.py` to build connectivity matrices
2. Compute Ollivier-Ricci curvature on brain graphs
3. Correlate with semantic network metrics

---

**Estimated Time**: 2-3 hours for 10 subjects (depending on download speed)
**Storage**: ~1-2 GB total

