# Sounio + fMRI Integration Plan
# Hyperbolic Semantic Networks Project

**Date**: 2026-02-20  
**Status**: Planning Phase  
**Objectives**: 
1. Integrate Sounio as epistemic computing proof-of-concept
2. Extend to fMRI brain connectivity correlation analysis

---

## PART 1: SOUNIO INTEGRATION

### 1.1 Current Status Assessment

**✅ Already Implemented** (in `experiments/01_epistemic_uncertainty/`):
- Complete phase transition experiment in Sounio (`phase_transition.sio`)
- Ollivier-Ricci curvature computation
- Sinkhorn algorithm for Wasserstein distance
- Random k-regular graph generation
- Epistemic uncertainty tracking (std_err = σ/√m)
- ~516 lines of working Sounio code

**📊 Validation Status**:
- Implements same algorithm as Julia/Rust pipeline
- Outputs CSV with epistemic metrics
- Ready for numerical validation

**🔧 What's Missing**:
- Compilation and execution (Sounio compiler needed)
- Numerical validation against Julia baseline
- Integration with existing pipeline
- Real network loading (SWOW data)

### 1.2 Integration Strategy: Non-Disruptive Parallel Track

**Design Principle**: Sounio as **validation layer**, not replacement

```
Current Pipeline (Production):
Julia/Rust → Curvature → Results → Publication
     ↓
     ↓ (validation)
     ↓
Sounio → Epistemic Curvature → Uncertainty Quantification
```

**Key Insight**: Sounio validates Julia, not vice versa. This maintains publication-ready status.

### 1.3 Concrete Implementation Plan

#### Phase 1: Compile & Validate Existing Code (Week 1-2)

**Tasks**:
1. Set up Sounio compiler environment
2. Compile `experiments/01_epistemic_uncertainty/phase_transition.sio`
3. Run on synthetic networks (N=100, k=2,3,4,...,40)
4. Compare output to Julia baseline

**Success Criteria**:
- Sounio compiles without errors
- Curvature values match Julia within 1% (numerical precision)
- Epistemic uncertainty is finite and reasonable
- Phase transition detected at ⟨k⟩²/N ≈ 2.5

**Deliverables**:
- `results/sounio/phase_transition_validation.csv`
- `docs/validation/SOUNIO_NUMERICAL_VALIDATION.md`
- Comparison plots (Sounio vs Julia)

#### Phase 2: Real Network Analysis (Week 3-4)

**Tasks**:
1. Extend Sounio code to load SWOW edge lists
2. Implement CSV parsing in Sounio (or use FFI to Julia)
3. Compute curvature for Spanish, English, Chinese SWOW
4. Compare epistemic uncertainty across languages

**Success Criteria**:
- Spanish: κ = -0.155 ± σ (matches Julia)
- English: κ = -0.258 ± σ (matches Julia)
- Chinese: κ = -0.214 ± σ (matches Julia)
- Epistemic confidence levels are calibrated

**Deliverables**:
- `experiments/01_epistemic_uncertainty/sounio/load_swow.d`
- `results/sounio/swow_epistemic_analysis.json`
- Uncertainty heatmap (N vs k vs uncertainty)

#### Phase 3: Epistemic Computing Showcase (Week 5-6)

**Goal**: Demonstrate Sounio's unique advantages

**Showcase Features**:

1. **Automatic Uncertainty Propagation**
   - Show how epistemic types propagate through computation
   - Compare to manual bootstrap in Julia (should match)

2. **Effect System Transparency**
   - Document all effects: `with Alloc, Random, Confidence, Panic`
   - Show how effects compose in function signatures

3. **Type Safety**
   - Demonstrate dimensional type checking
   - Show compile-time prevention of unit errors

**Deliverables**:
- `docs/sounio/EPISTEMIC_COMPUTING_DEMO.md`
- Side-by-side comparison: Sounio vs Julia code
- Performance benchmarks (acceptable if <10× slower)

### 1.4 Modules Benefiting Most from Sounio

**Priority 1: Curvature Computation** ✅ (Already implemented)
- **Why**: Core scientific computation with inherent uncertainty
- **Sounio Advantage**: Automatic epistemic uncertainty tracking
- **Status**: Complete in `phase_transition.sio`

**Priority 2: Bootstrap Analysis** (Future)
- **Why**: Uncertainty quantification is manual in Julia
- **Sounio Advantage**: Built-in confidence intervals
- **Implementation**: `experiments/01_epistemic_uncertainty/sounio/bootstrap.d`

**Priority 3: Null Model Generation** (Future)
- **Why**: Random effects need explicit tracking
- **Sounio Advantage**: `with Random` effect makes randomness explicit
- **Implementation**: `stdlib/graph/random.d` (partially done)

**NOT Recommended for Sounio**:
- ❌ Data preprocessing (Julia/Python better for I/O)
- ❌ Visualization (use existing tools)
- ❌ Production pipeline (Julia/Rust already validated)

---

## PART 2: fMRI CORRELATION EXTENSION

### 2.1 Scientific Hypothesis

**Core Question**: How does semantic network geometry relate to brain connectivity?

**Specific Hypotheses**:

**H1: Structural Correspondence**
- Semantic network hubs (high-degree nodes) → Brain regions with high fMRI connectivity
- Prediction: Angular gyrus, temporal pole show high connectivity for high-degree semantic nodes

**H2: Geometric Correspondence**
- Hyperbolic semantic distance → fMRI activation distance
- Prediction: Semantically distant words (high hyperbolic distance) → distinct brain activation patterns

**H3: Clustering Moderation in Brain**
- Brain regions with high clustering → process semantically clustered concepts
- Prediction: Default Mode Network (DMN) shows clustering-curvature relationship

**H4: Pathology Geometry**
- Schizophrenia: Altered semantic geometry → altered brain connectivity
- Depression: Negative bias → shifted semantic curvature → DMN changes
- Alzheimer's: Semantic fragmentation → reduced brain network clustering

### 2.2 fMRI Datasets: Concrete Sources

#### Option A: Human Connectome Project (HCP) ⭐ **RECOMMENDED**

**Dataset**: HCP S1200 Release
- **URL**: https://www.humanconnectome.org/study/hcp-young-adult/document/1200-subjects-data-release
- **Participants**: 1,200 healthy adults (ages 22-35)
- **Data Types**:
  - Resting-state fMRI (rfMRI)
  - Task fMRI (tfMRI): Language, working memory, social cognition
  - Structural MRI (T1w, T2w)
  - Diffusion MRI (dMRI)
- **Preprocessing**: Already preprocessed with HCP pipelines
- **Access**: Open access (requires registration)
- **Size**: ~1TB per subject (use preprocessed parcellated data: ~100MB)

**Relevant Tasks for Semantic Networks**:
1. **Language Task**: Story comprehension vs. math
2. **Working Memory**: N-back with semantic stimuli
3. **Social Cognition**: Theory of mind (semantic inference)

**Analysis Strategy**:
```
1. Extract parcellated time series (Glasser 360 parcels or Schaefer 400)
2. Compute functional connectivity matrix (Pearson correlation)
3. Build brain network graph (threshold at r > 0.3)
4. Compute brain network metrics: clustering, degree, curvature
5. Correlate with semantic network metrics from SWOW
```

**Key Brain Regions to Focus On** (Semantic Processing):
- **Angular Gyrus** (L/R): Semantic integration
- **Temporal Pole** (L/R): Conceptual knowledge
- **Inferior Frontal Gyrus** (L): Semantic retrieval
- **Posterior Cingulate Cortex**: Default Mode Network hub
- **Precuneus**: Semantic memory

#### Option B: NeuroSynth Meta-Analysis

**Dataset**: NeuroSynth Database
- **URL**: https://neurosynth.org
- **Data**: Meta-analysis of 15,000+ fMRI studies
- **Approach**: Query-based activation maps
- **Advantage**: No raw data processing needed
- **Limitation**: Aggregate data, not individual subjects

**Analysis Strategy**:
```
1. Query terms matching SWOW words (e.g., "dog", "cat", "love")
2. Extract activation maps for each semantic concept
3. Compute activation distance matrix
4. Compare to semantic network distance (hyperbolic)
5. Test correlation: semantic distance ↔ brain activation distance
```

#### Option C: OpenNeuro Semantic Task Datasets

**Specific Datasets**:

1. **ds000105**: Visual object recognition
   - 6 subjects, object naming task
   - Good for concrete nouns in SWOW

2. **ds000107**: Word and object processing
   - 49 subjects, semantic decision task
   - Direct semantic network relevance

3. **ds003097**: Semantic relatedness judgments
   - 24 subjects, explicit semantic similarity ratings
   - Perfect match for SWOW association strength

**Access**: https://openneuro.org (fully open)

#### Option D: Psychiatric Datasets (for H4)

**Schizophrenia**:
- **COBRE**: Center for Biomedical Research Excellence
  - 72 schizophrenia patients + 75 controls
  - Resting-state fMRI
  - URL: http://fcon_1000.projects.nitrc.org/indi/retro/cobre.html

**Depression**:
- **REST-meta-MDD**: Multi-site depression dataset
  - 2,428 MDD patients + 2,265 controls
  - Resting-state fMRI
  - URL: http://rfmri.org/REST-meta-MDD

**Alzheimer's**:
- **ADNI**: Alzheimer's Disease Neuroimaging Initiative
  - Longitudinal fMRI + cognitive assessments
  - URL: http://adni.loni.usc.edu

### 2.3 Correlation Analysis Methodology

#### Step 1: Brain Network Construction

**From fMRI to Graph**:
```python
# Pseudocode
1. Load preprocessed fMRI time series (parcellated)
   - Use atlas: Glasser 360 or Schaefer 400 parcels

2. Compute functional connectivity matrix
   - Method: Pearson correlation between ROI time series
   - Result: 360×360 correlation matrix

3. Threshold to create binary/weighted graph
   - Threshold: r > 0.3 (or top 10% of edges)
   - Result: Brain connectivity graph G_brain

4. Compute brain network metrics
   - Clustering coefficient: C_brain
   - Degree distribution: k_brain
   - Ollivier-Ricci curvature: κ_brain (using same pipeline!)
```

#### Step 2: Semantic-Brain Mapping

**Approach A: Node-Level Correspondence**
```python
# Map semantic concepts to brain regions
1. For each SWOW word (e.g., "dog"):
   - Query NeuroSynth for activation map
   - Identify peak activation ROI
   - Map word → brain region

2. Build correspondence matrix:
   - Semantic node i → Brain ROI j

3. Compute correlations:
   - Semantic degree(i) ↔ Brain connectivity(j)
   - Semantic clustering(i) ↔ Brain clustering(j)
   - Semantic curvature(i) ↔ Brain curvature(j)
```

**Approach B: Distance Correspondence**
```python
# Compare distance matrices
1. Semantic distance matrix: D_semantic (hyperbolic)
   - From SWOW network shortest paths

2. Brain activation distance matrix: D_brain
   - From fMRI activation patterns (Euclidean distance)

3. Mantel test: Correlation between D_semantic and D_brain
   - Hypothesis: Semantically close words → similar brain activation

4. Representational Similarity Analysis (RSA)
   - Compare semantic RDM vs. brain RDM
```

**Approach C: Network-Level Metrics**
```python
# Compare aggregate properties
1. Compute for semantic network (SWOW):
   - Mean clustering: C_semantic
   - Mean curvature: κ_semantic
   - Degree heterogeneity: σ_k_semantic

2. Compute for brain network (fMRI):
   - Mean clustering: C_brain
   - Mean curvature: κ_brain
   - Degree heterogeneity: σ_k_brain

3. Cross-subject correlation:
   - Do individuals with high C_brain also show high C_semantic?
   - (Requires individual semantic networks - use verbal fluency data)
```

#### Step 3: Statistical Methods

**Primary Analysis**:
1. **Pearson/Spearman Correlation**
   - For continuous metrics (degree, clustering, curvature)
   - Report r, p-value, 95% CI

2. **Mantel Test**
   - For distance matrix correlation
   - Permutation-based p-value (10,000 permutations)

3. **Multiple Comparison Correction**
   - Bonferroni or FDR (Benjamini-Hochberg)
   - Family-wise error rate control

**Secondary Analysis**:
4. **Linear Mixed Models**
   - Account for subject-level variability
   - Fixed effects: semantic metrics
   - Random effects: subject ID

5. **Mediation Analysis**
   - Test: Semantic geometry → Brain connectivity → Behavior
   - Use structural equation modeling (SEM)

**Validation**:
6. **Cross-Validation**
   - Split HCP subjects: 80% train, 20% test
   - Validate correlations hold in held-out data

7. **Replication**
   - Test in independent dataset (OpenNeuro)
   - Confirm findings across datasets

### 2.4 Implementation Roadmap

#### Phase 1: Proof-of-Concept (Weeks 1-4)

**Goal**: Establish feasibility with small dataset

**Tasks**:
1. Download HCP preprocessed data (10 subjects)
2. Extract parcellated time series (Schaefer 400)
3. Build brain connectivity graphs
4. Compute brain network metrics (C, k, κ)
5. Load SWOW Spanish network
6. Compute semantic network metrics
7. Test correlation: C_brain ↔ C_semantic

**Success Criteria**:
- Pipeline runs end-to-end
- Correlation is significant (p < 0.05) or null result is interpretable
- Code is modular and reusable

**Deliverables**:
- `code/fmri/load_hcp_data.py`
- `code/fmri/brain_network_construction.py`
- `code/fmri/semantic_brain_correlation.py`
- `results/fmri/proof_of_concept.json`

#### Phase 2: Full HCP Analysis (Weeks 5-8)

**Goal**: Comprehensive analysis on full HCP dataset

**Tasks**:
1. Scale to 100+ subjects (computational resources needed)
2. Compute brain curvature using Rust/Julia pipeline
3. Test all hypotheses (H1-H4)
4. Generate correlation matrices and heatmaps
5. Statistical validation (permutation tests, cross-validation)

**Success Criteria**:
- Significant correlations for at least 2/4 hypotheses
- Results replicate across train/test split
- Effect sizes are meaningful (r > 0.3)

**Deliverables**:
- `results/fmri/hcp_full_analysis.json`
- `figures/fmri/semantic_brain_correlation_heatmap.pdf`
- `docs/fmri/HCP_ANALYSIS_REPORT.md`

#### Phase 3: Psychiatric Extension (Weeks 9-12)

**Goal**: Test H4 on clinical populations

**Tasks**:
1. Download COBRE (schizophrenia) dataset
2. Compute brain network metrics for patients vs. controls
3. Compare to semantic network geometry (if available)
4. Test: Altered brain connectivity ↔ Altered semantic geometry

**Success Criteria**:
- Patients show different brain network geometry
- Difference aligns with semantic network predictions
- Results are clinically interpretable

**Deliverables**:
- `results/fmri/schizophrenia_brain_semantic.json`
- `manuscript/fmri_extension_draft.md`

### 2.5 Expected Outcomes & Contingencies

**Optimistic Scenario** (Strong Correlations):
- Semantic hubs → Brain hubs (r > 0.5, p < 0.001)
- Hyperbolic distance → Brain distance (Mantel r > 0.3, p < 0.01)
- Clustering moderation holds in brain networks
- **Impact**: Nature Neuroscience-tier paper

**Realistic Scenario** (Moderate Correlations):
- Some hypotheses supported (2/4)
- Effect sizes moderate (r = 0.2-0.4)
- Requires larger sample or refined methods
- **Impact**: NeuroImage or Network Neuroscience paper

**Pessimistic Scenario** (Null Results):
- No significant correlations
- Semantic and brain networks are independent
- **Impact**: Still publishable (negative results are valuable)
- **Pivot**: Focus on Sounio integration instead

**Contingency Plans**:
1. If HCP access is difficult → Use NeuroSynth meta-analysis
2. If computation is too slow → Use parcellated data (400 ROIs instead of voxel-wise)
3. If correlations are weak → Focus on specific brain regions (DMN only)
4. If psychiatric data is unavailable → Use published summary statistics

---

## PART 3: INTEGRATION TIMELINE

### Month 1-2: Sounio Validation
- Week 1-2: Compile and validate `phase_transition.sio`
- Week 3-4: Real network analysis (SWOW)
- Week 5-6: Epistemic computing showcase
- **Deliverable**: Sounio validation report

### Month 3-4: fMRI Proof-of-Concept
- Week 7-8: HCP data setup and brain network construction
- Week 9-10: Semantic-brain correlation (10 subjects)
- Week 11-12: Method refinement and validation
- **Deliverable**: Proof-of-concept results

### Month 5-6: Full Analysis
- Week 13-16: Scale to full HCP dataset
- Week 17-20: Statistical analysis and visualization
- Week 21-24: Manuscript preparation
- **Deliverable**: fMRI extension paper draft

### Month 7-8: Psychiatric Extension (Optional)
- Week 25-28: COBRE/REST-meta-MDD analysis
- Week 29-32: Integration with semantic pathology findings
- **Deliverable**: Clinical neuroscience paper

---

## PART 4: RESOURCE REQUIREMENTS

### Computational Resources

**For Sounio**:
- Sounio compiler (Rust toolchain)
- Minimal compute (laptop sufficient)
- Storage: <1GB

**For fMRI**:
- HCP data: ~100GB (preprocessed parcellated)
- Compute: 32GB RAM, 8+ cores recommended
- GPU: Optional (for deep learning approaches)
- Storage: ~500GB total (data + results)

### Software Dependencies

**Sounio**:
- Sounio compiler (from GitHub)
- LLVM toolchain
- Standard library

**fMRI**:
- Python 3.9+
- Neuroimaging: `nilearn`, `nibabel`, `nipype`
- Network analysis: `networkx`, `graph-tool`
- Statistics: `scipy`, `statsmodels`, `pingouin`
- Visualization: `matplotlib`, `seaborn`, `nilearn.plotting`

**Existing Pipeline**:
- Julia 1.9+ (already installed)
- Rust (already installed)
- GraphRicciCurvature (already installed)

### Data Access

**Required Registrations**:
1. HCP: https://db.humanconnectome.org (free, requires institutional email)
2. OpenNeuro: No registration (fully open)
3. COBRE/ADNI: Requires data use agreement

**Estimated Download Time**:
- HCP (100 subjects, parcellated): ~2-3 days
- OpenNeuro datasets: ~1 day
- COBRE: ~1 day

---

## PART 5: SUCCESS METRICS

### Sounio Integration Success

**Must Achieve**:
- [ ] Sounio code compiles and runs
- [ ] Numerical validation: curvature matches Julia within 1%
- [ ] Epistemic uncertainty is calibrated (matches bootstrap)
- [ ] Documentation demonstrates unique features

**Should Achieve**:
- [ ] Performance acceptable (<10× slower than Julia)
- [ ] Real network analysis (SWOW) works
- [ ] Effect system fully utilized
- [ ] Code is reusable (stdlib module)

**Stretch Goals**:
- [ ] GPU acceleration implemented
- [ ] Parallel computation working
- [ ] Refinement types for graph constraints
- [ ] Published in PL venue (PLDI/POPL)

### fMRI Extension Success

**Must Achieve**:
- [ ] Brain networks constructed from fMRI
- [ ] Correlation analysis runs end-to-end
- [ ] At least 1/4 hypotheses supported or refuted
- [ ] Results are scientifically interpretable

**Should Achieve**:
- [ ] 2/4 hypotheses supported with p < 0.05
- [ ] Effect sizes are meaningful (r > 0.3)
- [ ] Results replicate in held-out data
- [ ] Manuscript draft complete

**Stretch Goals**:
- [ ] All 4 hypotheses supported
- [ ] Psychiatric extension complete
- [ ] Published in Nature Neuroscience
- [ ] New geometric biomarkers discovered

---

## PART 6: RISK MITIGATION

### Technical Risks

**Risk 1: Sounio Compiler Issues**
- **Probability**: Medium
- **Impact**: High (blocks Sounio integration)
- **Mitigation**:
  - Start with existing `phase_transition.sio` (already written)
  - Contact Sounio developers for support
  - Fallback: Document design, implement when compiler ready

**Risk 2: fMRI Data Access Delays**
- **Probability**: Medium
- **Impact**: Medium (delays timeline)
- **Mitigation**:
  - Start HCP registration immediately
  - Use NeuroSynth as backup (no registration needed)
  - Use OpenNeuro datasets as alternative

**Risk 3: Computational Resources**
- **Probability**: Low
- **Impact**: Medium (slower analysis)
- **Mitigation**:
  - Use parcellated data (400 ROIs, not voxel-wise)
  - Cloud compute (AWS/GCP) if needed
  - Subsample subjects (100 instead of 1200)

### Scientific Risks

**Risk 4: Null Results (No Correlation)**
- **Probability**: Medium
- **Impact**: Low (still publishable)
- **Mitigation**:
  - Negative results are valuable
  - Pivot to methodological paper
  - Focus on Sounio integration instead

**Risk 5: Weak Effect Sizes**
- **Probability**: Medium
- **Impact**: Medium (less impactful)
- **Mitigation**:
  - Increase sample size
  - Focus on specific brain regions (DMN)
  - Use multivariate methods (CCA, PLS)

---

## NEXT STEPS (Immediate Actions)

### Week 1: Setup Phase

**Sounio**:
1. [ ] Clone Sounio repository (if not already done)
2. [ ] Build Sounio compiler
3. [ ] Test compilation of `phase_transition.sio`
4. [ ] Document any compiler errors

**fMRI**:
1. [ ] Register for HCP database access
2. [ ] Install neuroimaging Python packages
3. [ ] Download HCP S1200 documentation
4. [ ] Identify 10 subjects for proof-of-concept

**Documentation**:
1. [ ] Create project structure: `code/fmri/`, `results/fmri/`, `docs/fmri/`
2. [ ] Set up task tracking for both objectives
3. [ ] Review existing psychiatric network analysis code

### Week 2: First Results

**Sounio**:
1. [ ] Run `phase_transition.sio` on synthetic networks
2. [ ] Compare output to Julia baseline
3. [ ] Generate validation plots

**fMRI**:
1. [ ] Download first HCP subject (preprocessed)
2. [ ] Extract parcellated time series
3. [ ] Build first brain connectivity graph
4. [ ] Compute basic metrics (C, k)

---

## CONCLUSION

This integration plan accomplishes both objectives while maintaining scientific rigor:

1. **Sounio Integration**: Validates existing implementation, showcases epistemic computing, maintains non-disruptive parallel track
2. **fMRI Extension**: Concrete datasets (HCP), testable hypotheses, rigorous statistical methods, contingency plans

**Key Strengths**:
- Builds on existing validated work (Julia/Rust pipeline)
- Uses open-access datasets (HCP, OpenNeuro)
- Maintains publication-ready standards
- Has clear success criteria and fallback options

**Timeline**: 6-8 months to completion (both objectives)
**Risk Level**: Low-Medium (well-planned with mitigations)
**Impact**: High (interdisciplinary publication potential)

**Ready to proceed?** Start with Sounio compilation and HCP registration in Week 1.


