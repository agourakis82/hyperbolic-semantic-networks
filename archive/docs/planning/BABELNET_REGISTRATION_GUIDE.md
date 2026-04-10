# 🔐 BABELNET - GUIA DE REGISTRO E SETUP

**Status:** ✅ Python 3.8 env criado + BabelNet client instalado  
**Próximo passo:** REGISTRO MANUAL necessário

---

## ✅ **O QUE JÁ FOI FEITO:**

1. ✅ Conda environment Python 3.8 criado (`babelnet`)
2. ✅ BabelNet Python client instalado (v1.2.0)
3. ✅ Dependências instaladas (requests, zerorpc, etc.)
4. ✅ Script de extração preparado (`extract_babelnet_network.py`)

---

## 🎯 **PRÓXIMA AÇÃO (REQUER AÇÃO MANUAL):**

### **PASSO 1: REGISTRAR NO BABELNET**

👉 **ABRA NO NAVEGADOR:** https://babelnet.org/register

**Preencher formulário:**
```
Name: Demetrios Agourakis
Email: [seu email institucional/pessoal]
Affiliation: [PhD Program/Institution]
Research Purpose: 
  "Academic research on geometric properties of semantic networks
   across multiple languages (Russian, Arabic, Portuguese) for 
   PhD thesis on hyperbolic geometry in cognition"
```

**IMPORTANTE:**
- Use email institucional se possível (maior chance de aprovação rápida)
- Descreva pesquisa acadêmica claramente
- API key é gratuita para academic use

### **PASSO 2: AGUARDAR EMAIL**

- **Tempo esperado:** Instantâneo até 24h
- **Email contém:** BabelNet API Key
- **Exemplo:** `a1b2c3d4-5e6f-7g8h-9i0j-k1l2m3n4o5p6`

### **PASSO 3: CONFIGURAR API KEY**

Após receber o email, **ME INFORME A API KEY** e eu configuro automaticamente:

```bash
# Eu vou rodar:
cat > babelnet_conf.yml << EOF
RESTFUL_KEY: 'SUA_API_KEY'
RESTFUL_URL: 'https://babelnet.io/v9/service'
EOF
```

---

## 📊 **O QUE ACONTECE DEPOIS:**

### **DIA 1-2: EXTRAÇÃO (Rate Limited)**

```bash
# Ativar environment
conda activate babelnet

# Extrair Russian (usa ~900 queries)
python code/analysis/extract_babelnet_network.py --language ru --max_queries 900

# Aguardar próximo dia (reset daily limit)

# Extrair Arabic (usa ~900 queries)
python code/analysis/extract_babelnet_network.py --language ar --max_queries 900
```

**Timeline:**
- Russian extraction: 3-4 horas (com rate limiting)
- Arabic extraction: 3-4 horas (próximo dia)

### **DIA 3: BUILD + CURVATURE**

```bash
# Build networks
# Compute Ollivier-Ricci curvature
# Tempo: ~4 horas
```

### **DIA 4: CONFIG NULLS + MANUSCRIPT**

```bash
# Configuration nulls M=1000 (parallel)
# Tempo: ~8 horas
# Meta-analysis 7 datasets
# Update manuscript v2.0
```

---

## ⚠️ **LIMITAÇÕES CONHECIDAS:**

### **Rate Limits:**
- **Free tier:** 1,000 Babelcoins/dia
- **1 Babelcoin = 1 query**
- **Para N=500 nodes:** ~800-1000 queries
- **Resultado:** Precisa dividir em 2 dias (RU day 1, AR day 2)

### **Data Quality:**
- BabelNet integra múltiplas sources (Wikipedia, WordNet, Wiktionary)
- Pode ter mais ruído que ConceptNet/SWOW
- Mas também mais coverage!

---

## 📈 **BENEFÍCIOS:**

### **SE SUCESSO:**
- **Datasets finais:** 7 (SWOW×3 + ConceptNet×2 + BabelNet×2)
- **Línguas:** 6 (ES, EN, ZH, PT, RU, AR)
- **Métodos:** 3 (association + knowledge graph×2)
- **Acceptance:** 80-85% ✅

### **Story:**
- Multi-dataset validation ACROSS sources
- West + East Asia + Romance + Slavic + Semitic
- Portuguese 🇧🇷 = pesquisador
- Russian/Arabic = expanding coverage

---

## 🚨 **AÇÃO NECESSÁRIA AGORA:**

**VOCÊ PRECISA:**
1. Abrir https://babelnet.org/register
2. Preencher formulário
3. Aguardar email com API key
4. **ME INFORMAR A API KEY**

**Então eu:**
1. Configuro babelnet_conf.yml
2. Testo conexão
3. Inicio extração Russian
4. (Day 2) Extração Arabic
5. (Day 3) Build + curvature
6. (Day 4) Nulls + manuscript

---

**TOTAL: 3-4 DIAS até manuscrito v2.0 com 7 datasets!**


