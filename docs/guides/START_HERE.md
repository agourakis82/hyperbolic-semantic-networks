# 🚀 START HERE - Push para GitHub

**Repositório**: `hyperbolic-semantic-networks`  
**Tempo**: 15 minutos  
**Status**: ✅ Pronto para push

---

## O QUE VOCÊ TEM

- ✅ Manuscrito completo (Network Science paper)
- ✅ 6 figuras 300 DPI
- ✅ 8 scripts reproduzíveis
- ✅ Metadata Zenodo correto (ORCID: 0000-0002-8596-5097)
- ✅ 8 commits, tag v1.0.0
- ✅ Nome profissional (`hyperbolic-semantic-networks`)

---

## EXECUTE AGORA (3 comandos)

### 1. Criar Repo GitHub (3 min - via web)

**Abrir**: https://github.com/new

**Preencher**:
- Repository name: `hyperbolic-semantic-networks`
- Description: `Cross-linguistic evidence for hyperbolic geometry in semantic networks`
- ✓ Public
- ✗ NÃO initialize

**Click**: Create repository

---

### 2. Push Código (1 comando)

```bash
cd /home/agourakis82/workspace/hyperbolic-semantic-networks && \
git remote add origin https://github.com/agourakis82/hyperbolic-semantic-networks.git && \
git push -u origin main && \
git push origin --tags && \
echo "✅ PUSH COMPLETO! Ver em: https://github.com/agourakis82/hyperbolic-semantic-networks"
```

---

### 3. Enable Zenodo (2 min - via web)

**Abrir**: https://zenodo.org/account/settings/github/

**Fazer**:
1. Login com GitHub
2. Encontrar `hyperbolic-semantic-networks`
3. Toggle **ON**
4. ✅ Done!

---

### 4. Test DOI (1 comando + esperar)

```bash
cd /home/agourakis82/workspace/hyperbolic-semantic-networks && \
git tag v0.1.0-test -m "Test Zenodo" && \
git push origin v0.1.0-test && \
echo "⏳ Aguarde 10 min e verificar: https://zenodo.org/search?q=hyperbolic-semantic-networks"
```

**Após 10 minutos**: Se DOI aparecer → SUCCESS!

---

### 5. Official Release (se test OK)

```bash
cd /home/agourakis82/workspace/hyperbolic-semantic-networks && \
git tag -d v0.1.0-test && \
git push origin :refs/tags/v0.1.0-test && \
git push origin v1.0.0 && \
echo "🎉 v1.0.0 RELEASED! DOI em ~10 min"
```

---

## OU USE SCRIPT AUTOMATIZADO

```bash
cd /home/agourakis82/workspace/hyperbolic-semantic-networks
./COMANDOS_RAPIDOS.sh
```

(Script interativo que guia você por todos os passos)

---

## ARQUIVOS ÚTEIS

- `README_FIRST.md` - Quick start
- `PUSH_INSTRUCTIONS.md` - Passo a passo detalhado
- `ZENODO_INTEGRATION_GUIDE.md` - Troubleshooting
- `COMANDOS_RAPIDOS.sh` - Script automatizado

---

## APÓS OBTER DOI

Atualizar 2 arquivos com DOI real:

```bash
# Editar README.md linha 5 (substituir XXXXXX)
# Editar CITATION.cff linha final (substituir doi)

git add README.md CITATION.cff
git commit -m "docs: add Zenodo DOI"
git push origin main
```

---

✅ **TUDO PRONTO. PRÓXIMO PASSO: CRIAR REPO NO GITHUB!**

🎯 **https://github.com/new**

