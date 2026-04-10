# Instruções para Push GitHub + Zenodo

**Execute AGORA** (15 minutos)

---

## PASSO 1: Criar Repositório GitHub (3 min)

### Via Interface Web:

1. Ir para: https://github.com/new

2. Configurar:
   - **Repository name**: `hyperbolic-semantic-networks`
   - **Description**: `Cross-linguistic evidence for hyperbolic geometry in semantic networks`
   - **Public**: ✓ (marcar)
   - **Initialize**: ✗ NÃO marcar README, gitignore, license (já temos!)

3. Click: **Create repository**

4. **NÃO siga as instruções** que GitHub mostra (já temos repo local)

---

## PASSO 2: Push para GitHub (2 min)

```bash
cd /home/agourakis82/workspace/hyperbolic-semantic-networks

# Adicionar remote
git remote add origin https://github.com/agourakis82/hyperbolic-semantic-networks.git

# Push branch main
git push -u origin main

# Push todas as tags
git push origin --tags

# Verificar
git remote -v
```

**Expected output**:
```
Enumerating objects: 112, done.
Counting objects: 100% (112/112), done.
...
To https://github.com/agourakis82/pcs-v6.4-hyperbolic-geometry.git
 * [new branch]      main -> main
 * [new tag]         v1.0.0 -> v1.0.0
```

---

## PASSO 3: Enable Zenodo Integration (3 min)

### 3.1 Configurar Zenodo

1. Ir para: https://zenodo.org/account/settings/github/

2. Login com GitHub (se não logado)

3. **Importante**: Verificar email Zenodo = email GitHub
   - Se diferente: Update em Settings

4. Na lista de repositórios, encontrar:
   `agourakis82/hyperbolic-semantic-networks`

5. Toggle **ON** (switch para verde)

6. Verificar:
   - Deve aparecer mensagem "Webhook created"
   - GitHub repo Settings → Webhooks deve mostrar Zenodo

---

## PASSO 4: Test Release (5 min)

### 4.1 Criar Test Release

```bash
cd /home/agourakis82/workspace/pcs-v6.4-hyperbolic-geometry

# Criar tag de teste
git tag v0.1.0-test -m "Test release for Zenodo DOI integration"

# Push tag
git push origin v0.1.0-test
```

### 4.2 Aguardar Zenodo (5-10 min)

1. Aguardar 5 minutos

2. Ir para: https://zenodo.org/search?q=hyperbolic-semantic-networks

3. **Se aparecer record**:
   - ✅ SUCCESS!
   - Copiar DOI (formato: 10.5281/zenodo.XXXXXXX)
   - Prosseguir para Passo 5

4. **Se NÃO aparecer após 10 min**:
   - Check Zenodo account → Uploads
   - Check GitHub repo → Settings → Webhooks (erros?)
   - Ver troubleshooting em `ZENODO_INTEGRATION_GUIDE.md`

---

## PASSO 5: Cleanup Test + Official Release (2 min)

### Se test foi bem-sucedido:

```bash
cd /home/agourakis82/workspace/hyperbolic-semantic-networks

# Deletar test tag (local e remote)
git tag -d v0.1.0-test
git push origin :refs/tags/v0.1.0-test

# Deletar test deposit no Zenodo:
# Ir para: https://zenodo.org/me/uploads
# Encontrar v0.1.0-test
# Click "Delete" (se ainda draft)

# Push official release
git push origin v1.0.0

# Aguardar 5-10 min
# Verificar DOI em: https://zenodo.org/search?q=pcs-v6.4
```

---

## PASSO 6: Update com DOI (2 min)

### Após obter DOI oficial:

```bash
# Edit files (substituir XXXXXX pelo DOI real):

# 1. README.md (linha 4)
# Substituir: zenodo.XXXXXX
# Por: zenodo.1234567 (seu DOI)

# 2. CITATION.cff (linha final)
# Substituir: doi: "10.XXXX/XXXXX"
# Por: doi: "10.5281/zenodo.1234567"

# Commit
git add README.md CITATION.cff
git commit -m "docs: add Zenodo DOI badge and citation"
git push origin main
```

---

## VERIFICAÇÃO FINAL

### Checklist:

- [ ] GitHub repo criado
- [ ] Código pushed (main + tags)
- [ ] Zenodo integration ON
- [ ] Test release successful
- [ ] DOI obtido
- [ ] README updated com DOI
- [ ] CITATION.cff updated com DOI

---

## SE ALGO DER ERRADO

**Zenodo não cria DOI**:
- Read: `ZENODO_INTEGRATION_GUIDE.md`
- Email: info@zenodo.org
- Alternative: Upload manual (tar.gz)

**GitHub push fail**:
- Check credentials (token ou SSH key)
- Check remote URL correto
- Try: `git push -v` (verbose)

---

## APÓS TUDO PRONTO

**Você terá**:
- ✅ Repositório público no GitHub
- ✅ DOI permanente no Zenodo
- ✅ Citável e archivado
- ✅ Código reproduzível
- ✅ **Pronto para submission!**

---

**NEXT**: Convert manuscript MD → LaTeX (esta semana)

---

**Tempo estimado total**: 15-20 minutos  
**Resultado**: Paper v6.4 com DOI, pronto para submeter

🚀 **VAMOS LÁ!**

