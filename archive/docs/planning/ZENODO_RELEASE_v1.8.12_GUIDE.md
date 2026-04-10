# 🔖 ZENODO RELEASE v1.8.12 - Complete Guide
**Version:** v1.8.12-submission  
**Date:** 2025-11-05  
**DOI:** 10.5281/zenodo.XXXXXX (to be generated)  
**Status:** Ready for Zenodo release

---

## 🎯 WHY ZENODO BEFORE SUBMISSION?

**Critical Reasons:**
1. ✅ Manuscript cites DOI → Need real DOI before uploading
2. ✅ Reviewers will check DOI → Must be live
3. ✅ Data availability statement → Requires working link
4. ✅ Reproducibility gold standard → Zenodo = permanent archive

**Timeline:**
- Zenodo release: **FIRST** (today)
- Get DOI: Immediate (Zenodo auto-generates)
- Update manuscript with real DOI: 5 minutes
- Submit to journal: **AFTER** DOI confirmed

---

## 📦 ZENODO RELEASE PACKAGE

### **Files to Include:**

**1. Core Dataset (Processed)** ✅
```
data/processed/
├── spanish_edges.csv      (237KB)
├── english_edges.csv      (256KB)
├── dutch_edges.csv        (289KB)
└── chinese_edges.csv      (184KB)

Total: ~966KB
```

**2. Results (Structural Nulls)** ✅
```
results/structural_nulls/
├── spanish_configuration_nulls.json   (M=1000)
├── spanish_triadic_nulls.json        (M=1000)
├── english_configuration_nulls.json  (M=1000)
├── english_triadic_nulls.json        (M=1000)
├── dutch_configuration_nulls.json    (M=1000)
└── chinese_configuration_nulls.json  (M=1000)

Total: ~150KB (6 files)
```

**3. Code (Analysis Pipeline)** ✅
```
code/analysis/
├── preprocess_swow_to_edges.py
├── 07_structural_nulls_single_lang.py  (bug-fixed version)
├── 08_fill_placeholders.py
├── deep_insights_miner.py
└── requirements.txt

Total: ~50KB
```

**4. Documentation** ✅
```
├── README.md                          (project overview)
├── CITATION.cff                       (citation metadata)
├── LICENSE                            (MIT)
├── STRUCTURAL_NULLS_FINAL_6_8.md     (analysis summary)
└── code/analysis/requirements.txt    (dependencies)

Total: ~30KB
```

**5. Manuscript (Submitted Version)** ✅
```
manuscript/
├── manuscript_v1.8.12_FINAL.pdf
└── supplementary_materials.pdf

Total: ~172KB
```

**TOTAL PACKAGE SIZE:** ~1.4MB (well within Zenodo limits)

---

## 📝 ZENODO METADATA

### **Basic Information:**

**Title:**
```
Hyperbolic Semantic Networks: Cross-Linguistic Evidence from Structural Null Models
```

**Short Title:**
```
Hyperbolic Semantic Networks Data & Code
```

**Description:**
```
This repository contains the complete dataset, analysis code, and results for 
the manuscript "Consistent Evidence for Hyperbolic Geometry in Semantic Networks 
Across Four Languages" submitted to Network Science.

We provide:
1. Processed network edge lists for 4 languages (Spanish, English, Dutch, Chinese)
2. Structural null model results (6 analyses, M=1000 replicates each)
3. Complete Python analysis pipeline with bug-fixed algorithms
4. Manuscript PDFs (main text + supplementary materials)

All data derived from publicly available Small World of Words (SWOW) datasets.
All code released under MIT License.
```

**Version:** v1.8.12-submission

**Publication Date:** 2025-11-05

**Authors:**
```
[Your Full Name]
ORCID: XXXX-XXXX-XXXX-XXXX
Affiliation: [Your Institution]
```

**Keywords:**
```
semantic networks
hyperbolic geometry
Ricci curvature
cross-linguistic
cognitive networks
word associations
null models
configuration model
network science
SWOW
```

**License:**
- Code: MIT License
- Data: CC BY-NC-SA 4.0 (derived from SWOW)

**Related Identifiers:**
- Is supplement to: [Journal DOI when available]
- Is derived from: SWOW datasets (smallworldofwords.org)
- Is documented by: arXiv preprint [to be added]

**Funding:** None

**References:**
```
De Deyne, S., Navarro, D. J., Perfors, A., Brysbaert, M., & Storms, G. (2019). 
The "Small World of Words" English word association norms. Behavior Research 
Methods, 51(3), 987-1006.
```

---

## 🔧 ZENODO UPLOAD PROCEDURE

### **Step 1: Create Account (if needed)**
1. Go to: https://zenodo.org
2. Sign in with GitHub (recommended) or ORCID
3. Verify email

### **Step 2: New Upload**
1. Click "New Upload" (top right)
2. Reserve DOI: Click "Get a DOI now" (optional but recommended)
   - This reserves your DOI before finalizing
   - Allows you to cite it in manuscript before publishing release

### **Step 3: Upload Files**

**Create ZIP archive first:**
```bash
cd /home/agourakis82/workspace/hyperbolic-semantic-networks

# Create release directory
mkdir -p zenodo-release-v1.8.12

# Copy essential files
cp -r data/processed zenodo-release-v1.8.12/
cp -r results/structural_nulls zenodo-release-v1.8.12/results/
cp -r code/analysis/*.py zenodo-release-v1.8.12/code/
cp code/analysis/requirements.txt zenodo-release-v1.8.12/
cp manuscript/manuscript_v1.8.12_FINAL.pdf zenodo-release-v1.8.12/
cp submission/supplementary_materials.pdf zenodo-release-v1.8.12/
cp README.md LICENSE CITATION.cff zenodo-release-v1.8.12/

# Create ZIP
cd zenodo-release-v1.8.12
zip -r ../hyperbolic-semantic-networks-v1.8.12.zip . -x "*.pyc" "*.pyo" "__pycache__/*"
cd ..

# Verify size
ls -lh hyperbolic-semantic-networks-v1.8.12.zip
```

**Then upload ZIP to Zenodo interface**

---

### **Step 4: Fill Metadata Form**

**Upload type:** Dataset  
**Publication type:** Research Article  
**Access:** Open Access  
**License:** MIT License (code) + CC BY-NC-SA 4.0 (data)

**Communities:** (optional but recommended)
- Network Science
- Cognitive Science
- Computational Linguistics

---

### **Step 5: Publish**

**IMPORTANT:** 
- ⚠️ **Don't click "Publish" yet** if you reserved DOI
- First, note the reserved DOI (e.g., 10.5281/zenodo.XXXXXX)
- Update manuscript with this DOI
- Regenerate PDF
- **Then** come back and publish

**After Publishing:**
- DOI becomes active immediately
- All files permanently archived
- Citable, discoverable, versioned

---

## 🔄 WORKFLOW WITH DOI RESERVATION

### **Option A: Reserve DOI First (RECOMMENDED)**

```
1. Zenodo: Reserve DOI
   ↓
2. Note reserved DOI (10.5281/zenodo.XXXXXX)
   ↓
3. Update manuscript with real DOI
   ↓
4. Regenerate PDF v1.8.12-FINAL
   ↓
5. Add new PDF to Zenodo draft
   ↓
6. Publish Zenodo (DOI activated)
   ↓
7. Verify DOI works
   ↓
8. Submit to Network Science with real DOI
```

**Advantage:** Manuscript has correct DOI from day 1

---

### **Option B: Publish Immediately (FASTER)**

```
1. Zenodo: Upload all files
   ↓
2. Fill metadata
   ↓
3. Publish immediately (DOI auto-generated)
   ↓
4. Copy new DOI
   ↓
5. Update manuscript
   ↓
6. Regenerate PDF
   ↓
7. Submit to Network Science
   ↓
8. Update Zenodo with final PDF (creates v1.8.12.1)
```

**Advantage:** Faster (no waiting)  
**Disadvantage:** Manuscript DOI slightly different from archive initially

---

## 📋 ZENODO CHECKLIST

### **Files Prepared:**
- [x] Processed edge lists (4 CSVs)
- [x] Structural null results (6 JSONs)
- [x] Analysis code (5 Python scripts)
- [x] requirements.txt
- [x] README.md
- [x] LICENSE (MIT)
- [x] CITATION.cff
- [x] Manuscript PDF
- [x] Supplementary PDF

### **Metadata Prepared:**
- [x] Title
- [x] Description
- [x] Authors + ORCID
- [x] Keywords (10)
- [x] License
- [x] Version number
- [x] Related identifiers

### **Post-Publication:**
- [ ] Get DOI
- [ ] Update manuscript if needed
- [ ] Verify all links work
- [ ] Add to CV
- [ ] Link from GitHub

---

## 🎯 CURRENT DOI STATUS

**In Manuscript:** `10.5281/zenodo.17489685`

**Status:** ⚠️ **VERIFY IF THIS IS REAL OR PLACEHOLDER**

**Check:**
```bash
curl -I https://doi.org/10.5281/zenodo.17489685
```

**If 404:** This is placeholder, need to:
1. Create real Zenodo deposit
2. Get real DOI
3. Update manuscript
4. Regenerate PDF

**If 200:** DOI already exists, check if it's yours:
1. Visit https://zenodo.org/record/17489685
2. If it's your existing deposit → Update with v1.8.12
3. If it's someone else's → Create new deposit, update manuscript

---

## 🚀 RECOMMENDED ACTION

### **IMMEDIATE (Next 30 minutes):**

1. **Check current DOI:**
```bash
curl -I https://doi.org/10.5281/zenodo.17489685
```

2. **If DOI doesn't exist OR isn't yours:**
   - Create Zenodo account
   - Reserve new DOI
   - Update manuscript with real DOI
   - Regenerate PDF
   - Publish Zenodo
   - **Then** submit to journal

3. **If DOI exists and is yours:**
   - Create new version (v1.8.12)
   - Upload updated files
   - Publish new version
   - **Then** submit to journal

---

## 📄 CITATION.cff (Already Prepared)

Para o Zenodo, certifique-se de que `CITATION.cff` está atualizado:

```yaml
cff-version: 1.2.0
message: "If you use this dataset or code, please cite it as below."
type: dataset
title: "Hyperbolic Semantic Networks: Cross-Linguistic Evidence"
version: v1.8.12-submission
date-released: 2025-11-05
authors:
  - family-names: "[Your Last Name]"
    given-names: "[Your First Name]"
    orcid: "https://orcid.org/XXXX-XXXX-XXXX-XXXX"
repository-code: "https://github.com/agourakis82/hyperbolic-semantic-networks"
license: MIT
keywords:
  - semantic networks
  - hyperbolic geometry
  - Ricci curvature
  - SWOW
```

---

## ⏱️ TIMELINE

**Option A (Reserve DOI):**
- Create Zenodo draft: 5 min
- Reserve DOI: instant
- Update manuscript: 5 min
- Regenerate PDF: 2 min
- Publish Zenodo: 5 min
- **Total:** 17 minutes → **Then submit to journal**

**Option B (Direct publish):**
- Upload to Zenodo: 10 min
- Fill metadata: 5 min
- Publish: instant (DOI generated)
- **Total:** 15 minutes → **Then submit to journal**

---

**Quer que eu:**
1. **Verifique o DOI atual** (17489685)
2. **Crie instruções específicas** para seu caso
3. **Prepare o ZIP** para upload?

**Ou prefere fazer manualmente?** 🔖
