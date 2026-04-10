# 🤖 DARWIN DATA MINING AGENTS - PSYCHOPATHOLOGY NETWORKS

**Date:** 2025-11-06  
**Mission:** Find real semantic network data from psychopathology studies  
**Repositories:** Zenodo, OSF, GitHub, Figshare, Dryad  
**Principle:** HONESTIDADE ABSOLUTA [[memory:10560840]]

---

## 🎯 **OBJECTIVE:**

**Find downloadable datasets with:**
1. Semantic networks from psychiatric patients
2. Patient vs. Control comparisons
3. Edge lists or adjacency matrices
4. Network metrics (clustering, path length, etc.)

**Target Disorders:**
- Schizophrenia / FEP / Psychosis
- Alzheimer's / Dementia
- Depression / MDD
- Autism / ASD

---

## 🤖 **SPECIALIZED AGENTS:**

### **AGENT 1: REPOSITORY_SCOUT** 🔍
**Mission:** Search data repositories for semantic network datasets

**Targets:**
- Zenodo (zenodo.org)
- OSF (osf.io)
- GitHub (github.com)
- Figshare (figshare.com)
- Dryad (datadryad.org)
- DataCite (datacite.org)

**Search Terms:**
- "semantic network" + "schizophrenia"
- "semantic fluency" + "psychosis"
- "thought disorder" + "network"
- "word association" + "patient"
- "semantic speech" + "control"

**Output:** List of dataset URLs with metadata

---

### **AGENT 2: METADATA_EXTRACTOR** 📋
**Mission:** Extract metadata from found datasets

**Information to Extract:**
- Title, authors, year
- Dataset description
- File formats (CSV, JSON, GraphML, etc.)
- Sample size (n patients, n controls)
- Network type (semantic, word association, etc.)
- Metrics available

**Output:** Structured metadata database

---

### **AGENT 3: DATA_DOWNLOADER** 📥
**Mission:** Download accessible datasets

**Actions:**
- Check license (open access?)
- Download data files
- Verify file integrity
- Organize in `data/external/`

**Output:** Downloaded datasets ready for analysis

---

### **AGENT 4: FORMAT_CONVERTER** 🔄
**Mission:** Convert various formats to standard edge lists

**Supported Formats:**
- CSV (edge lists)
- JSON (graph objects)
- GraphML (XML format)
- Adjacency matrices
- PAJEK (.net)
- GML (Graph Modeling Language)

**Output:** Standardized edge lists (source, target, weight)

---

### **AGENT 5: NETWORK_ANALYZER** 📊
**Mission:** Compute network metrics for found datasets

**Metrics to Compute:**
- Clustering coefficient (C)
- Path length (L)
- Ollivier-Ricci curvature (κ)
- Entropy (H)
- Coherence (C_global)
- **KEC composite score**

**Output:** Complete metrics for patient vs. control

---

### **AGENT 6: KEC_CALCULATOR** 🧮
**Mission:** Compute KEC 3.0 for all datasets

**Formula:**
```
KEC = (H_z + κ_z - C_z) / 3
```

**Comparison:**
- Patient vs. Control
- Effect sizes (Cohen's d)
- Statistical tests (t-test, Mann-Whitney)

**Output:** KEC pathology signatures

---

### **AGENT 7: META_ANALYZER** 📈
**Mission:** Perform meta-analysis across datasets

**Actions:**
- Pool data from multiple studies
- Compute weighted effect sizes
- Test for heterogeneity (I², Q)
- Generate forest plots

**Output:** Meta-analytic KEC pathology estimate

---

## 🔍 **SEARCH STRATEGY:**

### **Phase 1: Broad Search (1-2 hours)**

**Zenodo:**
```
Search: "semantic network" AND "schizophrenia"
Search: "word association" AND "patient"
Search: "semantic fluency" AND "control"
```

**OSF:**
```
Search: semantic network psychosis
Search: thought disorder data
Search: semantic speech patient
```

**GitHub:**
```
Search: semantic-network schizophrenia dataset
Search: psychosis-network-analysis data
Search: semantic-speech-fep
```

**Expected:** 10-50 potential datasets

---

### **Phase 2: Filtering (30 min)**

**Criteria:**
- ✅ Has network data (edge lists or adjacency)
- ✅ Has patient-control comparison
- ✅ Psychiatric disorder (schizophrenia, etc.)
- ✅ Open access / downloadable
- ❌ Exclude: brain connectivity (fMRI, not semantic)
- ❌ Exclude: purely behavioral data (no networks)

**Expected:** 5-10 usable datasets

---

### **Phase 3: Download & Analysis (2-4 hours)**

**Actions:**
1. Download datasets
2. Convert to standard format
3. Compute C, κ, H, Coherence
4. Calculate KEC
5. Compare patient vs. control
6. Compute effect sizes

**Expected:** 3-5 complete analyses

---

## 📊 **EXPECTED DATASETS:**

### **Type 1: Semantic Fluency Networks**
- Verbal fluency task data
- Animal naming, category fluency
- Network constructed from transitions
- **Common in:** Alzheimer's, schizophrenia studies

### **Type 2: Word Association Networks**
- Word association task responses
- Free association data
- Similar to SWOW but for patients
- **Common in:** Schizophrenia, thought disorder

### **Type 3: Speech Network Data**
- Transcribed speech data
- Semantic speech networks (like PMC10031728)
- Edge lists from parsed speech
- **Common in:** FEP, psychosis studies

### **Type 4: Priming / Spreading Activation**
- Semantic priming task data
- Network inferred from RT patterns
- Less common but valuable

---

## 🎯 **TARGET PUBLICATIONS WITH DATA:**

### **Known Papers with Supplementary Data:**

1. **Mota et al. (2012, 2014)** - Schizophrenia speech graphs
   - Check: PLOS ONE supplementary
   - Expected: Edge lists or adjacency matrices

2. **Siew et al. (2019)** - Semantic networks in clinical disorders
   - Check: Behavior Research Methods supplementary
   - Expected: Network metrics tables

3. **Kenett et al. (2016, 2018)** - Semantic network structure
   - Check: OSF repositories (Kenett Lab)
   - Expected: Network data files

4. **Hills et al. (2015)** - Semantic search in memory
   - Check: Dryad or journal supplementary
   - Expected: Fluency task data

5. **Vitevitch lab** - Phonological networks (related)
   - Check: GitHub repositories
   - Expected: Network datasets

---

## 🛠️ **IMPLEMENTATION:**

### **Script 1: Repository Search**
```python
# Search Zenodo API
zenodo_results = search_zenodo(
    query="semantic network schizophrenia",
    type="dataset"
)

# Search OSF API
osf_results = search_osf(
    query="semantic network patient",
    resource_type="data"
)

# Search GitHub
github_results = search_github(
    query="semantic-network dataset psychosis",
    language="csv json"
)
```

### **Script 2: Download & Analyze**
```python
for dataset in found_datasets:
    # Download
    download_dataset(dataset.url, dataset.format)
    
    # Convert to edge list
    edges = convert_to_edgelist(dataset.files)
    
    # Build network
    G = build_network(edges)
    
    # Compute metrics
    C = compute_clustering(G)
    κ = compute_curvature(G)
    H = compute_entropy(G)
    Coh = compute_coherence(G)
    
    # Compute KEC
    KEC = compute_kec(κ, H, Coh)
    
    # Store results
    save_results(dataset.id, metrics)
```

---

## 📋 **EXECUTION PLAN:**

### **NOW (Next 3 hours):**

**Hour 1: Repository Search**
- Search Zenodo (30 min)
- Search OSF (20 min)
- Search GitHub (10 min)

**Hour 2: Filtering & Metadata**
- Review found datasets (30 min)
- Extract metadata (30 min)

**Hour 3: Download & Quick Analysis**
- Download top 3 datasets (20 min)
- Convert formats (20 min)
- Initial network analysis (20 min)

---

### **TOMORROW (4-6 hours):**

**Deep Analysis:**
- Compute full metrics (C, κ, H, Coherence)
- Calculate KEC for all datasets
- Patient vs. control comparisons
- Statistical tests & effect sizes

**Meta-Analysis:**
- Pool data across studies
- Weighted effect sizes
- Heterogeneity tests
- Generate plots

---

## 🎯 **SUCCESS CRITERIA:**

### **Minimum:**
- ✅ Find 3+ datasets with semantic networks
- ✅ At least 1 with patient-control comparison
- ✅ Compute KEC for 1 dataset

### **Target:**
- ✅ Find 5+ datasets
- ✅ 3+ with patient-control data
- ✅ Compute KEC for all
- ✅ Meta-analysis of ΔKEC

### **Stretch:**
- ✅ Find 10+ datasets
- ✅ Multiple disorders (schizophrenia, Alzheimer's, etc.)
- ✅ Comprehensive meta-analysis
- ✅ Novel KEC pathology signatures

---

## 💪 **COMMITMENT:**

**Princípio:** HONESTIDADE ABSOLUTA [[memory:10560840]]

- ✅ Buscar TODAS as fontes disponíveis
- ✅ Verificar licenses e citações corretas
- ✅ Reportar limitações honestamente
- ✅ Não forçar interpretações se dados insuficientes
- ✅ Meta-análise rigorosa com heterogeneidade

**Se não houver dados suficientes:**
- Admitir claramente
- Focar no sweet spot discovery principal
- Mencionar KEC como hypothetical extension
- Não oversell psychiatric findings

---

## 🚀 **READY TO ACTIVATE:**

**Command:**
```bash
python code/analysis/darwin_data_mining_agents.py \
  --repositories zenodo,osf,github,figshare \
  --keywords "semantic network,schizophrenia,psychosis,patient" \
  --output-dir data/external/psychopathology/
```

**ETA:** 3-6 hours for complete data mining + analysis

---

**VAMOS COMEÇAR O DATA MINING! 🔍💾🤖**


