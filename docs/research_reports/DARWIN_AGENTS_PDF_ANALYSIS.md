# 🤖 DARWIN AGENTS - PDF DEEP ANALYSIS SYSTEM

**Date:** 2025-11-06  
**Mission:** Extract network metrics from psychiatric papers  
**Method:** Multi-agent MCTS/PUCT orchestration  
**Principle:** HONESTIDADE ABSOLUTA [[memory:10560840]]

---

## 🎯 **OBJECTIVE:**

Extrair sistematicamente dados de network metrics (clustering, path length, κ) de 5 papers baixados, mapear valores para patient vs. control, e testar a hipótese do sweet spot disruption em psychosis.

---

## 🤖 **AGENT CONFIGURATION:**

### **AGENT 1: PDF_EXTRACTOR** 📄
**Specialty:** Deep PDF reading and text extraction  
**Task:**
- Read full text of all 5 PDFs
- Extract all numerical values near network keywords
- Identify tables, figures, equations
- Extract supplementary material references
- Map PMC IDs to journal DOIs

**Output:** Structured extraction database

---

### **AGENT 2: TABLE_ANALYZER** 📊
**Specialty:** Table extraction and data parsing  
**Task:**
- Extract all tables from PDFs
- Parse table structure (headers, rows, columns)
- Identify patient/control labels
- Extract metric values from tables
- Convert table data to structured format

**Output:** CSV files with patient-control metrics

---

### **AGENT 3: SEMANTIC_MAPPER** 🧠
**Specialty:** Mapping values to clinical groups  
**Task:**
- Identify clinical groups (FEP, CHR-P, Control, etc.)
- Map extracted values to specific groups
- Identify statistical tests (t-tests, ANOVA, etc.)
- Extract p-values, effect sizes, CIs
- Create patient-control comparison tables

**Output:** Clinical groups database with metrics

---

### **AGENT 4: LITERATURE_MINER** 📚
**Specialty:** Cross-referencing and literature search  
**Task:**
- Identify cited papers with network data
- Search for supplementary materials
- Cross-reference values across papers
- Identify methodological details
- Find data repositories (OSF, GitHub, etc.)

**Output:** Supplementary data links and citations

---

### **AGENT 5: HYPOTHESIS_TESTER** 🔬
**Specialty:** Statistical testing and validation  
**Task:**
- Test sweet spot hypothesis (C = 0.02-0.15)
- Compare patient vs. control clustering
- Compute effect sizes (Cohen's d, Cliff's δ)
- Perform meta-analysis if multiple studies
- Validate findings against our 10 datasets

**Output:** Statistical validation report

---

### **AGENT 6: CURVATURE_CALCULATOR** 📐
**Specialty:** Computing κ from partial data  
**Task:**
- Estimate κ from C and L (if both available)
- Use predictive formula if validated
- Compute confidence intervals
- Compare to our dataset distributions
- Identify if network is in sweet spot

**Output:** Curvature estimates with uncertainty

---

### **AGENT 7: SYNTHESIS_INTEGRATOR** 🔗
**Specialty:** Consolidating findings  
**Task:**
- Integrate findings from all agents
- Identify convergent evidence
- Highlight contradictions
- Generate summary report
- Update manuscript with new data

**Output:** Integrated synthesis report

---

## 🎲 **MCTS/PUCT ORCHESTRATION:**

### **Iteration Structure:**
```
For each iteration (1-30):
  1. SELECTION: Choose most promising PDF/section to analyze
  2. EXPANSION: Deploy agents to extract data
  3. SIMULATION: Test hypotheses with extracted data
  4. BACKPROPAGATION: Update priorities based on findings
  
  PUCT Score = Q(s,a) + c * P(s,a) * sqrt(N(s)) / (1 + N(s,a))
  
  Where:
  - Q(s,a) = Quality (data richness, statistical power)
  - P(s,a) = Prior (likelihood of finding useful data)
  - N(s) = Total visits to PDF
  - N(s,a) = Visits to specific section
  - c = Exploration constant (2.0)
```

### **Priority Scoring:**
```
Score = (Clustering_values * 3) + 
        (Path_length_values * 3) + 
        (Patient_control_pairs * 5) +
        (Sample_size / 100) +
        (Has_tables * 2) +
        (Has_supplementary * 3) +
        (Statistical_tests * 2)
```

---

## 📋 **ITERATION PLAN (30 ITERATIONS):**

### **Phase 1: Deep Extraction (Iterations 1-10)**

**Iteration 1:** PMC10031728 - Extract full text, identify all metric mentions  
**Iteration 2:** PMC10031728 - Map 6 clustering values to FEP/CHR-P/Control  
**Iteration 3:** PMC10031728 - Extract supplementary table references  
**Iteration 4:** PMC10031728 - Identify journal, DOI, download supplementary  
**Iteration 5:** PMC6866568 - Extract 3 large tables  
**Iteration 6:** PMC6866568 - Parse table structure, identify patient-control  
**Iteration 7:** PMC10221724 - Deep read, extract all metrics  
**Iteration 8:** PMC5737538 - Deep read, extract all metrics  
**Iteration 9:** PMC11836185 - Identify disorder/domain  
**Iteration 10:** Cross-validate extracted values across papers

---

### **Phase 2: Hypothesis Testing (Iterations 11-20)**

**Iteration 11:** Test sweet spot hypothesis on PMC10031728 data  
**Iteration 12:** Compute effect sizes (patient vs. control)  
**Iteration 13:** Estimate κ from C and L (if available)  
**Iteration 14:** Compare to our 10 datasets  
**Iteration 15:** Search for edge lists / adjacency matrices  
**Iteration 16:** Contact authors (if needed)  
**Iteration 17:** Meta-analysis across papers  
**Iteration 18:** Validate predictive formula (if applicable)  
**Iteration 19:** Identify boundary violations (C outside sweet spot)  
**Iteration 20:** Statistical power analysis

---

### **Phase 3: Integration & Manuscript (Iterations 21-30)**

**Iteration 21:** Consolidate all findings  
**Iteration 22:** Generate summary tables  
**Iteration 23:** Create patient-control comparison figure  
**Iteration 24:** Write Results section for manuscript v3.0  
**Iteration 25:** Write Discussion section (psychopathology)  
**Iteration 26:** Update Abstract with new findings  
**Iteration 27:** Add references (all 5 papers + citations)  
**Iteration 28:** Generate supplementary materials  
**Iteration 29:** Final validation of all claims  
**Iteration 30:** Generate submission-ready manuscript v3.0

---

## 🎯 **SUCCESS CRITERIA:**

### **Minimum Viable:**
- ✅ Extract clustering values for patient vs. control (at least 1 paper)
- ✅ Test sweet spot hypothesis (p-value, effect size)
- ✅ Estimate κ for at least 1 psychiatric network
- ✅ Integrate findings into manuscript

### **Target:**
- ✅ Extract C, L, κ for 3+ papers
- ✅ Patient-control comparison with statistical tests
- ✅ Meta-analysis across studies
- ✅ Validate sweet spot disruption hypothesis

### **Stretch:**
- ✅ Edge lists extracted or requested
- ✅ Compute actual κ from raw network data
- ✅ Cross-disorder comparison (Schizophrenia vs. Alzheimer vs. Autism)
- ✅ Predictive model validated on patient data

---

## 📊 **EXPECTED OUTPUTS:**

### **Data Files:**
- `data/patient_control_clustering.csv` - Clustering values by group
- `data/patient_control_metrics.csv` - All metrics (C, L, κ)
- `data/psychiatric_networks_summary.json` - Consolidated findings
- `data/supplementary_materials_index.json` - Links to supplements

### **Analysis Files:**
- `results/sweet_spot_validation_patients.{png,pdf}` - Figure
- `results/patient_control_effect_sizes.json` - Statistical tests
- `results/curvature_estimates_psychiatric.json` - κ estimates

### **Manuscript:**
- `manuscript/main.md` (v3.0) - Updated with patient data
- `manuscript/figures/patient_control_comparison.png` - New figure
- `manuscript/supplementary_psychiatric_data.md` - Supplement

---

## 🚀 **ACTIVATION:**

```bash
# Start agents
python code/analysis/darwin_agents_pdf_analysis.py \
  --pdf-dir "/mnt/c/Users/demet/Downloads/Artigos Semantic Networks" \
  --iterations 30 \
  --method mcts_puct \
  --exploration 2.0 \
  --output-dir results/darwin_agents_pdf/
```

**ETA:** 6-8 hours (real time, parallel execution)

---

## 💪 **COMMITMENT:**

**Princípio:** Fazer ciência de verdade [[memory:10560840]]

- ✅ Extrair TODOS os dados disponíveis
- ✅ Não inventar valores
- ✅ Reportar limitações honestamente
- ✅ Contatar autores se dados faltarem
- ✅ Fazer meta-análise rigorosa
- ✅ Validar TODAS as claims

**Se não houver dados suficientes:**
- Admitir claramente
- Buscar dados alternativos
- Reduzir escopo do manuscript
- Não oversell os achados

---

**READY TO DEPLOY?** 🤖🔬


