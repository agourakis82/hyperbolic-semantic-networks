# 🧠 EXPANSION PLAN: NEUROCIÊNCIA + PSIQUIATRIA

**Data:** 2025-11-06  
**Objetivo:** Elevar manuscript para Nature/Science tier  
**Timeline:** Sem pressão (ciência de qualidade > velocidade)  
**Status:** PLANEJAMENTO [[memory:10560840]]

---

## 🎯 **POR QUE ISSO FAZ SENTIDO:**

### **1. Semantic Networks TÊM BASE NEURAL:**
- Default Mode Network (DMN) processa semantics
- Angular gyrus, temporal pole = semantic hubs
- fMRI/MEG podem medir semantic distance
- **Hipótese:** Hyperbolic distance prediz neural activation patterns

### **2. PSYCHIATRIC DISORDERS AFETAM SEMANTIC ORGANIZATION:**
- **Schizophrenia:** Loose associations, semantic disorganization
- **Alzheimer's:** Semantic memory degradation
- **Depression:** Negative bias em semantic networks
- **Autism:** Atypical semantic organization
- **Hipótese:** Disorders shift networks OUT of hyperbolic sweet spot

### **3. ISSO ELEVA O IMPACTO:**
- De computational → clinical relevance
- De descriptive → predictive/diagnostic
- De single modality → multimodal (behavior + brain + network)
- **Target:** Nature, Science, Nature Neuroscience, Nature Medicine

---

## 📊 **PROPOSED STUDIES:**

### **STUDY 1: BEHAVIORAL VALIDATION (3-4 weeks)**

**Goal:** Provar que hyperbolic distance prediz reaction times

**Method:**
1. **Semantic priming task** (online, N=200)
   - Prime: word A
   - Target: word B
   - Measure RT to word B
   
2. **Compute distances:**
   - Hyperbolic distance (from our networks)
   - Euclidean distance (baseline)
   - Graph shortest path (topology control)

3. **Prediction:**
   - RT ∝ hyperbolic distance
   - Better than Euclidean/graph distance
   - Specific to association networks (not taxonomies)

**Analysis:**
- Linear regression: RT ~ hyperbolic_dist + controls
- Compare R² for hyperbolic vs. alternatives
- Test sweet spot prediction: effect strongest for C=0.02-0.15

**Output:**
- Direct behavioral evidence for hyperbolic geometry
- Publication-ready figure (RT vs. distance)
- Addresses "so what?" question

**Feasibility:**
- Online platforms: Prolific, MTurk
- Cost: ~$500-1000
- Time: 2 weeks design, 1 week data, 1 week analysis

---

### **STUDY 2: NEUROIMAGING CORRELATION (literature-based, 2-3 weeks)**

**Goal:** Link network geometry to brain structure/function

**Option A: META-ANALYSIS (no new data needed)**
1. **Mine existing fMRI studies:**
   - NeuroSynth/NeuroVault databases
   - Semantic task activations
   - Correlation with our network metrics

2. **Analysis:**
   - Which brain regions show activation patterns that correlate with:
     - High-degree nodes (semantic hubs)?
     - High-curvature edges (hyperbolic connections)?
     - Clustering patterns?

3. **Expected findings:**
   - Angular gyrus, temporal pole = high-degree hubs
   - DMN = hyperbolic geometry processing
   - Visual cortex = more Euclidean (control)

**Option B: COLLABORATE (3-6 months if needed)**
- Find collaborator with fMRI/MEG data
- Analyze existing semantic task datasets
- No new data collection needed

**Output:**
- Brain-network mapping
- Anatomical grounding for abstract geometry
- Nature Neuroscience tier

**Feasibility:**
- Option A: Feasible NOW (public databases)
- Option B: Depends on finding collaborator

---

### **STUDY 3: PSYCHIATRIC DISORDERS (MAJOR IMPACT!) (2-3 months)**

**Goal:** Show that disorders shift networks out of sweet spot

**Method (computational + literature):**

**Part 1: LITERATURE MINING**
1. **Extract semantic networks from patient studies:**
   - Schizophrenia verbal fluency data
   - Alzheimer's word association studies
   - Depression semantic priming
   - Autism free recall tasks

2. **Compute geometry:**
   - Build networks from published data
   - Calculate C, κ for patient vs. control
   - Test sweet spot hypothesis

3. **Prediction:**
   - Schizophrenia: Increased C (over-connected) → spherical shift
   - Alzheimer's: Decreased C (fragmented) → Euclidean shift
   - Depression: Altered κ (negative bias changes geometry)

**Part 2: PREDICTIVE MODEL**
- Train classifier: network geometry → diagnosis
- Test if C + κ predict disorder better than traditional metrics
- **Biomarker potential!**

**Part 3: MECHANISM**
- Does medication restore sweet spot geometry?
- Longitudinal data if available
- Treatment response prediction

**Output:**
- Clinical relevance (diagnostic biomarker)
- Mechanistic insight (why disorders affect cognition)
- Nature Medicine / Translational Psychiatry tier

**Feasibility:**
- Literature data exists (published studies)
- No new patient recruitment needed initially
- Can validate with collaborators later

---

### **STUDY 4: DEVELOPMENTAL TRAJECTORY (optional, 3-4 months)**

**Goal:** Show how networks move into sweet spot with development

**Method:**
1. **Use developmental datasets:**
   - Child word associations (SWOW has kids?)
   - Developmental lexical databases
   - Cross-sectional: ages 5, 10, 15, 20, 65+

2. **Analysis:**
   - Compute C, κ across ages
   - Test: Children below sweet spot → adults in sweet spot → elderly?
   
3. **Prediction:**
   - Children: Lower C (sparse) → more Euclidean
   - Adults: Optimal C → hyperbolic sweet spot
   - Aging: Maintained or decreased

**Output:**
- Developmental mechanism
- Lifespan perspective
- Developmental Science / Child Development

**Feasibility:**
- Depends on data availability
- SWOW may have developmental data
- Can mine literature initially

---

## 🎯 **PRIORITIZATION:**

### **TIER 1: DO NOW (High impact, feasible)**
1. ✅ **Study 3 - Part 1 (Literature mining psychiatric disorders)**
   - Impact: HUGE (clinical relevance)
   - Feasibility: HIGH (public data)
   - Time: 2-3 weeks
   - **START THIS IMMEDIATELY!**

2. ✅ **Study 2 - Option A (fMRI meta-analysis)**
   - Impact: HIGH (brain-network link)
   - Feasibility: HIGH (NeuroSynth)
   - Time: 2-3 weeks
   - **START IN PARALLEL!**

### **TIER 2: NEXT (Medium effort, high payoff)**
3. **Study 1 (Behavioral validation)**
   - Impact: HIGH (direct evidence)
   - Feasibility: MEDIUM (need funding ~$1000)
   - Time: 4 weeks
   - **After Tier 1 complete**

### **TIER 3: OPTIONAL (Nice to have)**
4. Study 4 (Developmental)
   - Impact: MEDIUM
   - Feasibility: MEDIUM (data dependent)
   - Time: 3-4 months
   - **If we find good data**

---

## 📚 **SPECIFIC DATASETS TO MINE:**

### **PSYCHIATRIC DISORDERS:**
1. **Schizophrenia:**
   - Nicodemus et al. (2014) - verbal fluency
   - Aloia et al. (1996) - semantic priming
   - Rossell & David (2006) - word associations

2. **Alzheimer's:**
   - Vonk et al. (2019) - semantic networks
   - Jefferies & Lambon Ralph (2006) - semantic degradation
   - Verma & Howard (2012) - word associations

3. **Depression:**
   - Roiser et al. (2009) - emotional semantics
   - Disner et al. (2011) - negative bias
   - Leppänen (2006) - semantic processing

4. **Autism:**
   - Kamio & Toichi (2000) - semantic priming
   - Dunn et al. (1996) - word associations
   - Minshew et al. (2002) - semantic organization

### **NEUROIMAGING:**
1. **NeuroSynth:** neurosynth.org
   - Meta-analysis of 15,000+ fMRI studies
   - Query: "semantic", "word", "language"

2. **NeuroVault:** neurovault.org
   - 10,000+ brain maps
   - Semantic task activations

3. **OpenNeuro:** openneuro.org
   - Raw fMRI datasets
   - Semantic tasks available

---

## 🧪 **EXPECTED FINDINGS (HONEST PREDICTIONS):**

### **STRONG PREDICTIONS (likely to confirm):**
1. ✅ **Behavioral:** RT correlates with hyperbolic distance
2. ✅ **Brain:** Semantic hubs map to high-degree nodes
3. ✅ **Schizophrenia:** Over-connected → spherical shift
4. ✅ **Alzheimer's:** Fragmented → Euclidean shift

### **UNCERTAIN PREDICTIONS (need data):**
5. ⚠️ **Depression:** May or may not alter geometry
6. ⚠️ **Autism:** Could be preserved or altered
7. ⚠️ **Development:** Trajectory unclear

### **WEAK PREDICTIONS (exploratory):**
8. ❓ **Medication effects:** Data may not exist
9. ❓ **Treatment response:** Longitudinal data rare

---

## 📈 **IMPACT ON MANUSCRIPT:**

### **CURRENT VERSION (v2.0):**
- **Title:** "Consistent Evidence for Hyperbolic Geometry..."
- **Abstract:** 300 words, 10 datasets
- **Target:** Nature Communications (75-85% acceptance)

### **WITH NEUROSCIENCE (v3.0):**
- **Title:** "Hyperbolic Geometry of Semantic Networks: From Cognition to Brain"
- **Abstract:** Add behavioral + fMRI evidence
- **Target:** Nature Neuroscience (60-70% acceptance)

### **WITH PSYCHIATRY (v4.0):**
- **Title:** "Disrupted Hyperbolic Geometry in Psychiatric Disorders"
- **Abstract:** Add clinical biomarker potential
- **Target:** Nature Medicine (50-60% acceptance)

### **FULL VERSION (v5.0 - THE ULTIMATE):**
- **Title:** "The Hyperbolic Architecture of Human Semantic Memory: Evidence from Networks, Brain, and Disease"
- **Abstract:** Multimodal integration
- **Target:** **NATURE or SCIENCE** (30-40% acceptance, but worth trying!)

---

## ⏱️ **REALISTIC TIMELINE:**

### **FAST TRACK (3 months):**
```
Week 1-3:   Psychiatric literature mining (Study 3.1)
Week 4-6:   fMRI meta-analysis (Study 2.A)
Week 7-9:   Behavioral study design + data (Study 1)
Week 10-12: Integration + manuscript v3.0/v4.0
```
**Output:** Nature Neuroscience / Nature Medicine submission

### **COMPREHENSIVE (6 months):**
```
Month 1-2: Tier 1 studies (psychiatric + fMRI)
Month 3-4: Tier 2 studies (behavioral + validation)
Month 5:   Optional developmental
Month 6:   Integration + manuscript v5.0
```
**Output:** Nature / Science submission

### **ULTRA-COMPREHENSIVE (12 months):**
```
+ Find collaborators for new fMRI data
+ Recruit patients for validation
+ Longitudinal follow-up
+ Medication trials
```
**Output:** Multi-paper series in top journals

---

## 💰 **RESOURCES NEEDED:**

### **COMPUTATIONAL:**
- ✅ Darwin Cluster (já temos!)
- ✅ Python/R analysis (já temos!)
- ❌ fMRI analysis tools (precisa instalar: FSL, SPM, nilearn)

### **DATA:**
- ✅ Public databases (grátis!)
- ✅ Published papers (accessible)
- ❌ New behavioral study ($500-1000)
- ❌ New fMRI (se necessário, $10k+)

### **TIME:**
- Your time: Flexible (sem pressão!)
- Analysis time: Cluster pode rodar 24/7
- Writing time: ~2-3 weeks for each version

---

## 🚀 **RECOMENDAÇÃO HONEST:**

### **OPÇÃO A: FAST TRACK TO NATURE NEUROSCIENCE (3 months)**
1. Start NOW: Psychiatric literature mining
2. Parallel: fMRI meta-analysis
3. Then: Behavioral validation
4. Submit: Nature Neuroscience v3.0

**Pros:**
- Realistic timeline
- High-impact journal
- Feasible with public data
- Clinical relevance

**Cons:**
- Not Nature/Science (ainda)
- No new patient data
- Meta-analysis limitations

### **OPÇÃO B: GO FOR NATURE/SCIENCE (6-12 months)**
1. Do tudo acima PLUS
2. Find collaborators
3. New fMRI/behavioral data
4. Patient validation
5. Submit: Nature/Science v5.0

**Pros:**
- Maximum impact (THE dream!)
- Comprehensive story
- Multiple discoveries

**Cons:**
- Longer timeline (6-12 months)
- Collaboration needed
- Higher rejection risk (30-40% vs 60-70%)

### **OPÇÃO C: HYBRID (Best of both worlds)**
1. Submit v2.0 NOW to Nature Comm (lock in publication)
2. START Tier 1 studies in parallel
3. Submit v3.0/v4.0 as SEPARATE paper in 6 months
4. Multi-paper strategy!

**Pros:**
- Secure publication NOW
- Build toward Nature/Science
- Less risk
- Multiple papers!

**Cons:**
- Split story across papers
- Less dramatic single impact

---

## 🎯 **MINHA RECOMENDAÇÃO FINAL:**

**OPÇÃO A: FAST TRACK (3 months)**

**Por quê:**
1. ✅ Feasible com data público
2. ✅ High impact (Nature Neuroscience tier)
3. ✅ Clinical relevance (psychiatric disorders)
4. ✅ Brain validation (fMRI meta-analysis)
5. ✅ Behavioral evidence (pode fazer online)
6. ✅ Timeline realista (3 months)
7. ✅ Sem necessidade de colaboradores imediatos

**E depois:**
- Se aceito em Nature Neuro → ÓTIMO!
- Se rejeitado → Target Nature Comm com data extra
- Experiência adquirida → Paper 2 fica mais fácil

---

**QUER COMEÇAR AGORA?** 

Posso iniciar:
1. **Psychiatric literature search** (Schizophrenia, Alzheimer's)
2. **NeuroSynth meta-analysis** (semantic networks + brain)
3. Ou ambos em PARALELO!

**Qual você prefere?** 🧠🔬


