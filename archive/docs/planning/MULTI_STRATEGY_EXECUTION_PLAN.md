# 🎯 MULTI-STRATEGY EXECUTION PLAN: C+B+A

**Date:** 2025-11-06  
**Approach:** COMPREHENSIVE (All strategies in parallel)  
**Principle:** HONESTIDADE ABSOLUTA [[memory:10560840]]

---

## 🎯 **TRIPLE STRATEGY:**

### **STRATEGY C: Enhanced Agents with OCR** 🤖 (4-6h)
- Add OCR capability (Tesseract, pytesseract)
- Extract tables from images
- Parse complex table structures
- Re-run agents with enhanced capabilities

### **STRATEGY B: Supplementary Materials** 📄 (1-2h)
- Identify journal website (Schizophrenia Bulletin)
- Download supplementary tables/figures
- Extract data from supplements
- Map clustering values to groups

### **STRATEGY A: Manual Deep Read** 🔬 (2-4h)
- Read PMC10031728 full text carefully
- Identify all 6 clustering value contexts
- Map values to groups (FEP, CHR-P, Control)
- Extract additional metrics (path length, etc.)

---

## 📋 **EXECUTION TIMELINE:**

### **PHASE 1: Parallel Setup (30 min)**

**Task 1.1: Install OCR Tools** (10 min)
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr
pip install pytesseract pdf2image pillow
```

**Task 1.2: Locate Supplementary Materials** (10 min)
- Find PMC10031728 on PubMed Central
- Identify supplementary file links
- Download supplementary PDFs/tables

**Task 1.3: Setup Deep Read Environment** (10 min)
- Open PMC10031728 in reader
- Prepare annotation tools
- Create extraction template

---

### **PHASE 2: Parallel Execution (2-4h)**

#### **Track C: Enhanced Agents** 🤖

**Step C1: Implement OCR Agent** (1h)
- Create `OCR_EXTRACTOR` agent
- Add image extraction from PDF
- Add table detection
- Add OCR processing

**Step C2: Enhance Table Parser** (1h)
- Improve `TABLE_ANALYZER` agent
- Add structure recognition
- Add cell value extraction
- Add header identification

**Step C3: Re-run Enhanced Agents** (30 min)
- Execute darwin_agents_pdf_analysis_v2.py
- Process all 5 PDFs
- Extract tables with OCR
- Map values to groups

**Step C4: Validate OCR Results** (30 min)
- Compare OCR output to manual reading
- Identify errors
- Refine OCR parameters

---

#### **Track B: Supplementary Materials** 📄

**Step B1: Download Materials** (30 min)
- Access PMC10031728 on PMC website
- Download supplementary tables (1-3)
- Download supplementary figures
- Save to `data/supplementary/PMC10031728/`

**Step B2: Extract Supplementary Data** (1h)
- Read supplementary tables
- Extract clustering values by group
- Extract path length values
- Extract statistical tests (p-values, effect sizes)

**Step B3: Cross-validate with Main Text** (30 min)
- Match supplementary values to main text
- Verify consistency
- Identify any discrepancies

---

#### **Track A: Manual Deep Read** 🔬

**Step A1: First Pass - Context Extraction** (1h)
- Read full PMC10031728 text
- Identify all 6 clustering value mentions
- Extract context (±200 words)
- Note section numbers/pages

**Step A2: Second Pass - Group Mapping** (1h)
- For each of 6 values, identify group
- Look for FEP, CHR-P, Control labels
- Check figures/tables captions
- Check results section descriptions

**Step A3: Third Pass - Additional Metrics** (1h)
- Extract path length values
- Extract degree values
- Extract sample sizes (n per group)
- Extract p-values and effect sizes

**Step A4: Create Ground Truth Dataset** (30 min)
- Consolidate all manual findings
- Create authoritative mapping
- Document evidence for each value
- Save to `data/manual_extraction/PMC10031728_ground_truth.json`

---

### **PHASE 3: Integration & Validation (1h)**

**Task 3.1: Compare All Three Strategies**
- OCR results vs. Supplementary vs. Manual
- Identify agreements
- Identify discrepancies
- Determine most reliable values

**Task 3.2: Create Final Dataset**
- Combine best data from all sources
- Prioritize: Manual > Supplementary > OCR
- Document confidence levels
- Save to `data/final/patient_control_complete.csv`

**Task 3.3: Statistical Analysis**
- Test sweet spot hypothesis with group labels
- Compute patient vs. control effect sizes
- Perform meta-analysis if applicable
- Generate publication-quality figures

---

## 🛠️ **IMPLEMENTATION:**

### **Enhanced Agents Code Structure:**

```python
# New agents to add:

class OCRExtractor:
    """Extract text from images in PDFs"""
    - extract_images_from_pdf()
    - apply_ocr()
    - detect_tables_in_images()
    - parse_table_structure()

class EnhancedTableAnalyzer:
    """Improved table parsing"""
    - identify_header_rows()
    - identify_data_types()
    - map_columns_to_metrics()
    - extract_patient_control_labels()

class ManualValidationAgent:
    """Validate automated extractions"""
    - compare_with_ground_truth()
    - compute_accuracy()
    - identify_failure_patterns()
    - suggest_improvements()
```

---

## 📊 **SUCCESS CRITERIA:**

### **Minimum Success:**
- ✅ Map 6 clustering values to groups (FEP, CHR-P, Control)
- ✅ Extract at least 1 patient vs. control comparison
- ✅ Compute effect size (Cohen's d)

### **Target Success:**
- ✅ Complete group mapping (all 6 values)
- ✅ Extract path length values
- ✅ Extract sample sizes (n per group)
- ✅ Compute effect sizes for all metrics
- ✅ Validate with supplementary materials

### **Stretch Success:**
- ✅ OCR successfully extracts tables from all 5 PDFs
- ✅ Automated pipeline extracts patient-control data
- ✅ Cross-paper meta-analysis
- ✅ Manuscript v3.0 with psychopathology section

---

## ⏱️ **ESTIMATED TIMELINE:**

**Phase 1 (Setup):** 30 min  
**Phase 2 (Execution):** 4-6 hours  
  - Track C (OCR): 3-4 hours  
  - Track B (Supplementary): 2 hours  
  - Track A (Manual): 3 hours  
  - (Parallel execution reduces total time)  
**Phase 3 (Integration):** 1 hour  

**Total:** 5.5-7.5 hours  
**With breaks:** 1 full day  

---

## 💪 **COMMITMENT:**

Esta é a abordagem MAIS COMPLETA possível! [[memory:10560840]]

- ✅ Não vamos deixar nenhuma pedra sem virar
- ✅ Vamos usar TODAS as ferramentas disponíveis
- ✅ Vamos validar com múltiplas fontes
- ✅ Vamos ser HONESTOS sobre limitações
- ✅ Vamos criar pipeline reusável para futuros papers

---

## 🚀 **READY TO START?**

**Próximo passo:** Começar Phase 1 (Setup) em paralelo!

1. Install OCR tools
2. Locate supplementary materials
3. Prepare manual reading environment

**VAMOS FAZER ISSO!** 🔬💪


