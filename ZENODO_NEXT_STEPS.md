# ✅ GitHub Push COMPLETO - Próximos Passos

**Repository**: https://github.com/agourakis82/hyperbolic-semantic-networks  
**Status**: ✅ Online com 10 commits, tag v1.0.0

---

## 🔗 PASSO 3: Enable Zenodo Integration (5 min)

### 1. Abrir Zenodo Settings

**URL**: https://zenodo.org/account/settings/github/

### 2. Login com GitHub (se necessário)

### 3. Encontrar Repositório

Na lista, procurar: `agourakis82/hyperbolic-semantic-networks`

### 4. Toggle ON

Click no switch para ativar (verde)

### 5. Verificar Webhook

- Deve aparecer "Webhook created"
- Ou verificar em: https://github.com/agourakis82/hyperbolic-semantic-networks/settings/hooks

---

## 🧪 PASSO 4: Test Release (10 min)

### Criar Test Tag

```bash
cd /home/agourakis82/workspace/hyperbolic-semantic-networks

git tag v0.1.0-test -m "Test Zenodo DOI integration"
git push origin v0.1.0-test
```

### Aguardar 10 Minutos

Zenodo processa webhook e cria DOI

### Verificar DOI

**URL**: https://zenodo.org/search?q=hyperbolic-semantic-networks

**Se aparecer record**:
- ✅ SUCCESS!
- Copiar DOI (exemplo: 10.5281/zenodo.1234567)
- Prosseguir para Passo 5

**Se NÃO aparecer após 15 min**:
- Check: https://zenodo.org/me/uploads
- Pode estar em draft (needs manual publish)
- Ver troubleshooting: `ZENODO_INTEGRATION_GUIDE.md`

---

## 🎉 PASSO 5: Official Release (2 min)

### Se Test OK, Limpar e Fazer Official

```bash
cd /home/agourakis82/workspace/hyperbolic-semantic-networks

# Delete test tag
git tag -d v0.1.0-test
git push origin :refs/tags/v0.1.0-test

# Delete test deposit no Zenodo (via web):
# https://zenodo.org/me/uploads → Delete v0.1.0-test

# Push official v1.0.0
git push origin v1.0.0
```

### Aguardar DOI Oficial (10 min)

Verificar: https://zenodo.org/search?q=hyperbolic-semantic-networks

---

## 📝 PASSO 6: Update com DOI (5 min)

### Quando DOI oficial aparecer:

```bash
cd /home/agourakis82/workspace/hyperbolic-semantic-networks

# Edit README.md (linha 5):
# Substituir: zenodo.XXXXXX
# Por: zenodo.1234567 (seu DOI real)

# Edit CITATION.cff (última linha preferred-citation):
# Substituir: doi: "10.XXXX/XXXXX"
# Por: doi: "10.5281/zenodo.1234567"

git add README.md CITATION.cff
git commit -m "docs: add Zenodo DOI (10.5281/zenodo.XXXXXX)"
git push origin main
```

---

## ✅ CHECKLIST

- [x] GitHub repo criado
- [x] Código pushed (main)
- [x] Tag v1.0.0 pushed
- [ ] Zenodo integration ON
- [ ] Test release created
- [ ] DOI test obtained
- [ ] Official v1.0.0 released
- [ ] DOI official obtained
- [ ] README/CITATION updated com DOI

---

## 🎯 APÓS ZENODO COMPLETO

**Você terá**:
- ✅ Repositório público GitHub
- ✅ DOI permanente Zenodo
- ✅ Citable, archived
- ✅ Badge no README
- ✅ **Paper v6.4 com DOI oficial**

**Então**: Começar implementação Major Revisions (4 semanas)

---

**Próximo agora**: Enable Zenodo integration!  
**URL**: https://zenodo.org/account/settings/github/

🚀

