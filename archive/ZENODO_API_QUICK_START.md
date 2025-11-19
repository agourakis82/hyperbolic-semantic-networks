# 🚀 ZENODO API - Quick Start (2 Passos)
**Tempo Total:** 5 minutos  
**Result:** Nova versão v1.8.12 publicada com DOI

---

## 🔑 PASSO 1: Obter Token (2 min)

### **1.1 Login Zenodo**
```
https://zenodo.org/login
```
(Use GitHub ou ORCID)

### **1.2 Criar Token**
```
https://zenodo.org/account/settings/applications/tokens/new/
```

**Preencher:**
- Name: `hyperbolic-semantic-networks-v1.8.12`
- Scopes: ✓ `deposit:write` + ✓ `deposit:actions`

**Clicar:** Create

**Copiar token** (aparece UMA VEZ só! Ex: `aBcDeFg123...`)

### **1.3 Configurar Token**
```bash
export ZENODO_TOKEN="cole_seu_token_aqui"
```

---

## 📤 PASSO 2: Publicar (3 min)

### **Executar Script:**
```bash
cd /home/agourakis82/workspace/hyperbolic-semantic-networks
python tools/zenodo_new_version.py
```

**O script vai:**
1. ✅ Acessar depósito existente (17489685)
2. ✅ Criar nova versão (draft)
3. ✅ Deletar arquivos antigos
4. ✅ Upload ZIP (503KB) via API
5. ✅ Atualizar metadata (v1.8.12)
6. ✅ **PUBLISH** com novo DOI
7. ✅ **Mostrar novo DOI** → Copiar!

---

## 📋 O QUE O SCRIPT FAZ

```
🔖 ZENODO NEW VERSION - v1.8.12 Submission
══════════════════════════════════════════

✅ Token found
✅ ZIP found: hyperbolic-semantic-networks-v1.8.12-submission.zip (503 KB)

📋 Getting existing deposit 17489685...
✅ Existing deposit found:
   Title: Hyperbolic Geometry of Semantic Networks...
   Current DOI: 10.5281/zenodo.17489685

🆕 Creating new version...
✅ New version draft created: ID=XXXXXX

🗑️ Deleting old files from new version...
✅ Old files deleted

📝 Updating metadata...
✅ Metadata updated

📤 Uploading hyperbolic-semantic-networks-v1.8.12-submission.zip (0.49 MB)...
✅ ZIP uploaded successfully!

📢 Publishing new version...

══════════════════════════════════════════════════════════════
🎉 SUCCESS! NOVA VERSÃO PUBLICADA!
══════════════════════════════════════════════════════════════
✅ DOI: 10.5281/zenodo.XXXXXX  ← COPIAR ESTE!
✅ URL: https://zenodo.org/records/XXXXXX
══════════════════════════════════════════════════════════════

📋 PRÓXIMOS PASSOS:
1. Verificar record: [URL]
2. Atualizar manuscrito com DOI: [DOI]
3. Regenerar PDF se DOI mudou
4. Submeter para Network Science!

💾 DOI saved to: ZENODO_NEW_DOI_v1.8.12.txt
```

---

## 🔄 APÓS SCRIPT COMPLETAR

### **Se novo DOI é diferente** (ex: ...17489686):

**1. Atualizar Manuscrito:**
```bash
# Substituir DOI em 3 locais:
cd /home/agourakis82/workspace/hyperbolic-semantic-networks

# Opção A: Usar sed (automático)
NEW_DOI="10.5281/zenodo.17489686"  # Seu novo DOI
OLD_DOI="10.5281/zenodo.17489685"

sed -i "s|$OLD_DOI|$NEW_DOI|g" manuscript/main.md
sed -i "s|$OLD_DOI|$NEW_DOI|g" submission/cover_letter.md
```

**2. Regenerar PDF:**
```bash
cd manuscript
pandoc main.md -o manuscript_v1.8.12_FINAL_ZENODO.pdf \
  --pdf-engine=xelatex \
  --variable mainfont="DejaVu Sans" \
  --variable geometry:margin=1in

# Copiar para Downloads
cp manuscript_v1.8.12_FINAL_ZENODO.pdf /mnt/c/Users/demet/Downloads/
```

**3. Submeter Journal:**
- Use novo PDF com DOI correto

---

### **Se novo DOI é o mesmo** (raro):
✅ Manuscrito já correto, submeter imediatamente!

---

## ⏱️ TIMELINE

```
Min 0:   Obter token Zenodo
Min 2:   export ZENODO_TOKEN="..."
Min 3:   python tools/zenodo_new_version.py
Min 6:   ✅ Script completa, DOI gerado
Min 7:   (Atualizar manuscrito se DOI mudou)
Min 12:  (Regenerar PDF se necessário)
Min 15:  ✅ PRONTO PARA SUBMISSÃO!
```

---

## ✅ **COMANDOS COMPLETOS (Copy-Paste)**

```bash
# 1. Obter token em: https://zenodo.org/account/settings/applications/tokens/new/
# 2. Configurar (substituir SEU_TOKEN):
export ZENODO_TOKEN="SEU_TOKEN_AQUI"

# 3. Executar script:
cd /home/agourakis82/workspace/hyperbolic-semantic-networks
python tools/zenodo_new_version.py

# 4. Script mostra novo DOI → Copiar!
# 5. Se DOI mudou, me avisar para atualizar manuscrito
# 6. Submeter para Network Science!
```

---

## 🎯 **STATUS**

**Script:** ✅ Pronto (`tools/zenodo_new_version.py`)  
**ZIP:** ✅ Pronto (503KB, Downloads)  
**Metadata:** ✅ Hardcoded no script  
**Ação:** 🟡 **Aguardando seu token Zenodo**

**Obtenha token e execute em 5 minutos!** 🔑🚀


