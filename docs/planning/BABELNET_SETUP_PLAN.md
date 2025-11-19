# 🔧 BABELNET SETUP - PLANO DE EXECUÇÃO COMPLETO

**Data:** 2025-11-06  
**Objetivo:** Extrair semantic networks para Russian 🇷🇺 + Arabic 🇸🇦 via BabelNet

---

## 📋 **PLANO DE EXECUÇÃO (2-3 DIAS):**

### **DIA 1: SETUP + REGISTRO (4-6 horas)**

#### **Passo 1: Registro BabelNet** ⏱️ 10 min
```bash
# AÇÃO MANUAL NECESSÁRIA:
# 1. Abrir: https://babelnet.org/register
# 2. Preencher formulário (nome, email, afiliação)
# 3. Aguardar email com API key (geralmente instantâneo)
```

**Informações para registro:**
- Name: Demetrios Agourakis
- Email: [seu email]
- Affiliation: [sua instituição/PhD]
- Purpose: Academic research - semantic network geometry analysis

#### **Passo 2: Install BabelNet Python Client** ⏱️ 5 min
```bash
cd /home/agourakis82/workspace/hyperbolic-semantic-networks
pip install babelnet
```

#### **Passo 3: Configurar babelnet_conf.yml** ⏱️ 2 min
```bash
# Após receber API key por email:
cat > babelnet_conf.yml << EOF
RESTFUL_KEY: 'SUA_API_KEY_AQUI'
RESTFUL_URL: 'https://babelnet.io/v9/service'
EOF
```

#### **Passo 4: Testar API** ⏱️ 5 min
```python
import babelnet as bn
from babelnet.language import Language

# Test query
synsets = bn.get_synsets('дом', from_langs=[Language.RU])  # Russian: house
print(f"Found {len(synsets)} synsets for 'дом' (house)")
```

#### **Passo 5: Extrair Russian Synsets** ⏱️ 3-4 horas
```python
# Script: extract_babelnet_russian.py
# Strategy: 
#   - Get top 1000 most frequent Russian words
#   - Query BabelNet for synsets
#   - Extract semantic relations
#   - Build network
# Limit: 1,000 queries/dia (may need 2 days)
```

---

### **DIA 2: EXTRAÇÃO ARABIC** (4-6 horas)

#### **Passo 6: Extrair Arabic Synsets** ⏱️ 3-4 horas
```python
# Script: extract_babelnet_arabic.py
# Same strategy as Russian
# Limit: 1,000 queries/dia
```

#### **Passo 7: Build Networks** ⏱️ 1 hour
```python
# Build NetworkX graphs from BabelNet data
# Extract LCC
# Compute basic stats
```

---

### **DIA 3: CURVATURE + NULLS** (8-12 horas)

#### **Passo 8: Compute Curvatures** ⏱️ 2-3 hours
```python
# Ollivier-Ricci curvature for RU + AR
# Parallel execution
```

#### **Passo 9: Configuration Nulls M=1000** ⏱️ 6-8 hours
```python
# Parallel null model generation
# 2 languages × 1000 replicates
```

#### **Passo 10: Meta-analysis + Manuscript** ⏱️ 3-4 hours
```python
# Integrate 7 datasets
# Update figures
# Update tables
# Update discussion
```

---

## ⚠️ **LIMITAÇÕES E RISCOS:**

### **1. Rate Limits:**
- **Problema:** 1,000 queries/dia pode ser insuficiente
- **Solução:** Dividir extração em 2 dias (RU dia 1, AR dia 2)
- **Risk:** Se precisar >1000 queries/língua, pode levar 3-4 dias

### **2. Data Quality:**
- **Problema:** BabelNet integra múltiplas fontes (qualidade variável)
- **Solução:** Filtrar por confiança/source
- **Risk:** Network pode ter ruído

### **3. Comparabilidade:**
- **Problema:** BabelNet ≠ ConceptNet ≠ SWOW (métodos diferentes)
- **Solução:** Justificar no paper como "validation across sources"
- **Risk:** Reviewers podem questionar mixing methods

### **4. Infraestrutura:**
- **Problema:** Modo RPC requer ~100GB download + Docker
- **Solução:** Usar modo Online (mais lento mas funcional)
- **Risk:** Rate limits severos

---

## 💰 **CUSTO-BENEFÍCIO FINAL:**

### **INVESTIMENTO:**
```
Tempo: 2-3 dias (~24-36 horas)
Complexidade: ALTA
Risk: MÉDIO
```

### **RETORNO:**
```
+2 datasets (RU, AR)
Total: 7 datasets (vs. 5 atual)
Acceptance: 75-80% → 80-85% (+5%)
```

### **RATIO:**
```
30 horas de trabalho para +5% acceptance
= 6 horas/1% acceptance gain
```

---

## 🎯 **AVALIAÇÃO HONESTA:** [[memory:10560840]]

### **COM 5 DATASETS (ATUAL):**
- ✅ Homogeneidade metodológica
- ✅ 100% replication (5/5 hyperbolic)
- ✅ Portuguese 🇧🇷 = compelling story
- ✅ 2 construction methods (association + knowledge)
- ✅ 4 language families
- ✅ Rigor científico ALTO
- **Acceptance: 75-80%** ✅

### **COM 7 DATASETS (BABELNET):**
- ⚠️ Heterogeneidade de sources (SWOW + ConceptNet + BabelNet)
- ✅ 7 datasets total
- ⚠️ Mixing methods pode gerar crítica
- ✅ Mais línguas
- **Acceptance: 80-85%** (se reviewers aceitarem mixing)
- **Risk:** Reviewers podem preferir homogeneidade

---

## 📌 **PRÓXIMOS PASSOS:**

### **SE PROSSEGUIR COM BABELNET:**

1. **AGORA:** Registrar em babelnet.org/register
2. **+10 min:** Aguardar email com API key
3. **+15 min:** Setup Python client + config file
4. **+30 min:** Script de extração
5. **+3-4h:** Extrair Russian (Day 1)
6. **+3-4h:** Extrair Arabic (Day 2)
7. **+10h:** Build + curvature + nulls (Day 3)

**TOTAL: 2.5-3 dias**

---

## ✅ **AÇÃO IMEDIATA:**

**Você precisa registrar manualmente em:**
👉 **https://babelnet.org/register**

**Preencher:**
- Name: Demetrios Agourakis
- Email: [seu email institucional]
- Affiliation: [PhD institution]
- Purpose: "Academic research on semantic network geometry for PhD thesis"

**Após receber API key, me informe e eu configuro tudo automaticamente!**

---

**Enquanto isso, vou preparar os scripts de extração...**


