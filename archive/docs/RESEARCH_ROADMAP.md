# Research Roadmap: The Next Discoveries

## Priority 1: Verify the Phase Transition (High Impact, Low Effort)

### Experiment: Synthetic Network Sweep

**Goal**: Verify that κ changes sign when ⟨k⟩² ≈ N

**Method**:
1. Fix N = 500
2. Create random regular graphs with k ∈ [2, 4, 6, 8, 10, 15, 20, 30, 40, 50, 60]
3. Compute Ollivier-Ricci curvature for each
4. Plot κ vs ⟨k⟩ and κ vs ⟨k⟩²/N

**Prediction**:
- ⟨k⟩ < √N ≈ 22: κ < 0 (hyperbolic)
- ⟨k⟩ ≈ √N: κ ≈ 0 (transition)
- ⟨k⟩ > √N: κ > 0 (spherical)

**Timeline**: 1-2 days (code ready: `experiment_phase_transition.py`)

**Impact**: ⭐⭐⭐⭐⭐
- Proves universal law
- Publishable as standalone finding
- Opens door to geometric network theory

---

## Priority 2: Cross-Linguistic Expansion (High Impact, Medium Effort)

### Experiment: Test 10-20 Languages

**Goal**: Verify hyperbolic geometry is universal across human languages

**Languages to test**:
- **Germanic**: German, Dutch (if different data), Swedish, Norwegian
- **Romance**: French, Italian, Portuguese, Romanian
- **Slavic**: Russian (BabelNet available), Polish, Czech
- **Asian**: Japanese, Korean, Thai, Vietnamese
- **Semitic**: Arabic (BabelNet available), Hebrew
- **Other**: Turkish, Finnish, Hungarian, Swahili

**Method**:
1. Obtain SWOW or equivalent free association data
2. Build networks (N ≈ 500, use R1 responses only)
3. Compute ⟨k⟩, C, κ, α for each
4. Test universality: Do all have κ < 0?

**Prediction**:
- All languages with ⟨k⟩ < 5 will have κ < 0
- κ values will cluster around -0.15 to -0.25
- α values will cluster around 2.8-3.0

**Timeline**: 2-4 weeks (depends on data availability)

**Impact**: ⭐⭐⭐⭐⭐
- Major cross-linguistic study
- High-profile publication (Nature Human Behaviour, PNAS)
- Establishes universality

---

## Priority 3: Gromov δ-Hyperbolicity (Medium Impact, Low Effort)

### Experiment: Direct Measure of Tree-Likeness

**Goal**: Compute Gromov δ-hyperbolicity and correlate with Ollivier-Ricci κ

**Method**:
1. For each network, sample ~1000 random quadruples (w,x,y,z)
2. Compute: δ = max over quadruples of [d(w,x) + d(y,z) - max{d(w,y)+d(x,z), d(w,z)+d(x,y)}] / 2
3. Compare δ to mean κ

**Expected correlation**: δ ≈ -1/κ (from Jost-Liu theorem)

**Why interesting**: δ measures "tree-likeness" directly

**Timeline**: 1 week

**Impact**: ⭐⭐⭐
- Connects to theoretical graph theory
- Validates Ollivier-Ricci findings
- Publishable in specialized journal (Journal of Complex Networks)

---

## Priority 4: Hyperbolic Embeddings (High Impact, Medium Effort)

### Experiment: Embed in Poincaré Disk

**Goal**: Show semantic networks naturally embed in low-dimensional hyperbolic space

**Method**:
1. Use Poincaré embeddings (hyperbolic space)
2. Embed Spanish/English/Chinese networks in 2D, 5D, 10D
3. Compare distortion to Euclidean embeddings
4. Visualize 2D embeddings (beautiful plots!)

**Prediction**:
- Hyperbolic embeddings have **lower distortion**
- 5D hyperbolic ~ 300D Euclidean (huge savings)
- 2D visualization shows hierarchical structure

**Tools**:
- `gensim` (Poincaré embeddings)
- Or implement custom using `torch` + Riemannian SGD

**Timeline**: 2-3 weeks

**Impact**: ⭐⭐⭐⭐⭐
- Beautiful visualizations
- Practical for AI/NLP
- High-profile publication (ICLR, NeurIPS)

---

## Priority 5: Neural Validation (Ultra-High Impact, High Effort)

### Experiment: fMRI Semantic Space Geometry

**Goal**: Measure whether **brain representations** are hyperbolic

**Method**:
1. fMRI experiment: Show subjects concept words
2. Measure BOLD response patterns (RSA)
3. Compute pairwise concept distances
4. Fit hyperbolic vs Euclidean metric
5. Compare: Which geometry fits neural distances better?

**Prediction**: Hyperbolic metric fits better (R² > 0.8)

**Challenges**:
- Need fMRI access (expensive)
- Need 20-30 subjects
- Need ~100 concept words with known semantic network structure

**Timeline**: 6-12 months (full study)

**Impact**: ⭐⭐⭐⭐⭐
- Direct brain evidence
- Nature Neuroscience level publication
- Transforms field (neuroscience + linguistics)

---

## Priority 6: Development & Pathology (High Impact, High Effort)

### Experiment A: Child vs Adult Networks

**Goal**: Test if hyperbolic geometry emerges with development

**Method**:
1. Collect semantic networks from children (ages 5, 7, 10, 13, 16, adult)
2. Compute κ for each age group
3. Track evolution: Does κ become more negative with age?

**Prediction**:
- Young children (5-7): Less hyperbolic (κ closer to 0)
- Adolescents (13-16): More hyperbolic (κ ≈ -0.2)
- Adults: Most hyperbolic (κ ≈ -0.25)

**Why**: Knowledge becomes more hierarchically organized with age

**Timeline**: 6-12 months (data collection difficult)

**Impact**: ⭐⭐⭐⭐
- Developmental cognitive science
- Developmental Science, Child Development journals

---

### Experiment B: Clinical Populations

**Goal**: Test if semantic network geometry changes in pathology

**Populations**:
1. **Aphasia** (language impairment after stroke)
2. **Alzheimer's** (semantic memory loss)
3. **Schizophrenia** (thought disorder)
4. **Autism** (atypical semantic processing)

**Method**:
1. Collect semantic networks from patients
2. Compare κ to matched controls
3. Correlate κ with symptom severity

**Predictions**:
- **Alzheimer's**: κ → 0 (loss of hierarchical structure)
- **Schizophrenia**: κ more variable (disorganized thought)
- **Aphasia**: κ preserved? (structural vs access deficit)

**Timeline**: 12-18 months

**Impact**: ⭐⭐⭐⭐⭐
- Clinical relevance
- Potential biomarker
- Nature Medicine, Brain journals

---

## Priority 7: Cross-Modal Semantics (Medium Impact, High Effort)

### Experiment: Visual, Auditory, Motor Semantic Networks

**Goal**: Test if non-linguistic semantic networks are also hyperbolic

**Domains**:
1. **Visual**: Image similarity networks (ImageNet, COCO)
2. **Auditory**: Sound similarity networks (AudioSet)
3. **Motor**: Action similarity networks (kinematic data)

**Method**:
1. Construct similarity networks from human judgments or neural data
2. Threshold to create graphs (top 3 neighbors per node)
3. Compute κ, ⟨k⟩, α

**Prediction**: All sparse (⟨k⟩ < 5) perceptual networks are hyperbolic

**Timeline**: 3-6 months

**Impact**: ⭐⭐⭐⭐
- Extends beyond language
- Shows general cognitive principle
- Cognitive Science, Cognition journals

---

## Priority 8: Theoretical Derivation (Medium Impact, Very High Effort)

### Goal: Derive κ from First Principles

**Mathematical challenge**: Derive exact formula for κ as function of network topology

**Approach**:
1. Start with κ = 1 - W₁(μᵤ, μᵥ) / d(u,v)
2. Approximate W₁ for random graphs with degree distribution P(k)
3. Use mean-field theory or cavity method
4. Derive: κ ≈ f(⟨k⟩, ⟨k²⟩, N, tree-likeness)

**Goal formula**:
```
κ ≈ 1 - c₁·(1 - ⟨k⟩²/N) - c₂·tree_measure
```

Where c₁, c₂ are constants.

**Why hard**: Wasserstein distance is a complex optimization problem

**Timeline**: 6-12 months (PhD-level math problem)

**Impact**: ⭐⭐⭐⭐
- Fundamental theory
- Physical Review E, Journal of Statistical Physics
- Opens new subfield

---

## Priority 9: Ricci Flow Universality (Low Impact, Medium Effort)

### Goal: Explain 80-87% Clustering Drop

**Mathematical challenge**: Prove the Ricci flow clustering drop is universal for hyperbolic random graphs

**Approach**:
1. Simulate Ricci flow on synthetic scale-free graphs
2. Vary N, ⟨k⟩, α, test consistency of drop percentage
3. Derive analytical approximation

**Conjecture**:
```
ΔC / C_initial ≈ 0.85 ± 0.05
```

For all hyperbolic random graphs with α ∈ [2, 3].

**Timeline**: 2-3 months

**Impact**: ⭐⭐⭐
- Specialized interest (geometric graph theory)
- Journal of Complex Networks

---

## Priority 10: AI Applications (High Practical Impact, Medium Effort)

### Application A: Better Word Embeddings

**Goal**: Create hyperbolic word embeddings from semantic networks

**Method**:
1. Train Poincaré embeddings on SWOW data
2. Compare to Word2Vec, GloVe on standard benchmarks
3. Test on hierarchy-sensitive tasks (hypernymy detection, taxonomy completion)

**Prediction**: Hyperbolic embeddings outperform Euclidean on hierarchical tasks

**Timeline**: 1-2 months

**Impact**: ⭐⭐⭐⭐
- Practical for NLP
- EMNLP, ACL conferences

---

### Application B: Knowledge Graph Completion

**Goal**: Use hyperbolic geometry for knowledge graph embeddings

**Method**:
1. Apply to ConceptNet, WordNet
2. Test link prediction: Predict missing is-a, part-of relations
3. Compare hyperbolic vs Euclidean embeddings

**Prediction**: Hyperbolic geometry captures hierarchical relations better

**Timeline**: 2-3 months

**Impact**: ⭐⭐⭐⭐
- Practical for AI
- KDD, WWW, ICLR conferences

---

## Summary: Impact vs Effort Matrix

```
                    HIGH IMPACT

         Neural      Cross-Ling   Hyperbolic   Clinical
HIGH     Valid.      Expansion    Embeddings   Pathology
EFFORT    (P5)         (P2)         (P4)         (P6)
            |           |            |            |
            |           |            |            |
         Theory      Cross-Modal   AI Apps    Dev. Study
MEDIUM   Derive      Semantics   Embed/KG      (P6)
            (P8)         (P7)        (P10)
            |           |            |            |
            |           |            |            |
         Ricci Flow  Gromov δ    Phase
LOW        (P9)        (P3)     Transition
EFFORT                           (P1)

                    LOW IMPACT → HIGH IMPACT
```

---

## Recommended Timeline (Next 12 Months)

### Month 1-2: Quick Wins
- ✅ **P1**: Phase transition experiment (validate ⟨k⟩²/N law)
- ✅ **P3**: Gromov δ-hyperbolicity (theoretical validation)

### Month 3-4: Data Collection
- **P2**: Cross-linguistic expansion (start with 5 languages)
- **P4**: Hyperbolic embeddings (Poincaré disk, visualizations)

### Month 5-8: Deep Analysis
- **P2**: Complete 10-language study
- **P4**: Complete embedding study + benchmarks
- **P10**: AI applications (word embeddings, knowledge graphs)

### Month 9-12: Neuroscience (if resources available)
- **P5**: fMRI study design + pilot
- **P6**: Clinical data collection (start with one population)

---

## Publication Strategy

### Paper 1: "The Geometry of Meaning" (submit Month 3)
- **Content**: Core findings + phase transition + cross-linguistic
- **Target**: Nature Human Behaviour, PNAS
- **Impact**: Establishes field

### Paper 2: "Hyperbolic Embeddings" (submit Month 6)
- **Content**: Poincaré embeddings + AI applications
- **Target**: ICLR, NeurIPS
- **Impact**: Practical AI impact

### Paper 3: "Neural Hyperbolic Geometry" (submit Month 12)
- **Content**: fMRI validation + clinical
- **Target**: Nature Neuroscience, Neuron
- **Impact**: Neuroscience breakthrough

---

## Funding Opportunities

### Grants to Apply For:

1. **NSF Cognitive Neuroscience** ($500k, 3 years)
   - For P5 (fMRI validation)

2. **NIH Brain Initiative** ($1M, 5 years)
   - For P5 + P6 (neural + clinical)

3. **ERC Starting Grant** (€1.5M, 5 years)
   - For comprehensive program (P1-P7)

4. **Google Faculty Research Award** ($75k, 1 year)
   - For P4 + P10 (AI applications)

5. **ONR Multidisciplinary University Research Initiative (MURI)** ($7.5M, 5 years)
   - For full theoretical + experimental program

---

## Why This Matters

This is not just about semantic networks. It's about discovering **geometric laws of cognition**.

Just as:
- Physics discovered laws of motion
- Chemistry discovered periodic table
- Biology discovered DNA structure

**We may be discovering the fundamental geometry of thought.**

And geometry is **universal**.

That's what makes this exciting.

Let's find out what's true.
