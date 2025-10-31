# Zenodo Integration Guide

**Updated**: 2025-10-30  
**Status**: ✅ Problema identificado e resolvido

---

## Problema Anterior (Diagnosticado)

### Sintoma
Integração Zenodo falhava com erro de autoria/ORCID

### Causa Raiz Identificada

**1. Formato de Creators Desatualizado**

Zenodo migrou para formato RDM (Research Data Management):

❌ **Formato Antigo** (não funciona mais):
```json
{
  "creators": [
    {
      "name": "Agourakis, Demetrios",
      "orcid": "0000-0002-8596-5097"
    }
  ]
}
```

✅ **Formato Novo** (RDM-style, requerido):
```json
{
  "creators": [
    {
      "person_or_org": {
        "type": "personal",
        "given_name": "Demetrios",
        "family_name": "Chiuratto Agourakis",
        "identifiers": [
          {
            "scheme": "orcid",
            "identifier": "0000-0002-8596-5097"
          }
        ]
      },
      "affiliations": [
        {
          "name": "PUC-SP; Faculdade São Leopoldo Mandic"
        }
      ]
    }
  ]
}
```

**2. Resource Type também mudou**:

❌ Antigo:
```json
{
  "upload_type": "publication",
  "publication_type": "article"
}
```

✅ Novo:
```json
{
  "resource_type": {
    "type": "publication",
    "subtype": "article"
  }
}
```

**3. ORCID Correto Identificado**

Estava usando placeholder `0000-0000-0000-0000`  
ORCID real: **0000-0002-8596-5097**

---

## Solução Implementada

### 1. Arquivo `.zenodo.json` Atualizado

Localizado em: `/home/agourakis82/workspace/pcs-v6.4-hyperbolic-geometry/.zenodo.json`

✅ Formato RDM completo  
✅ ORCID correto  
✅ Afiliação incluída  
✅ resource_type atualizado

### 2. Arquivo `CITATION.cff` Atualizado

✅ ORCID correto  
✅ Nome completo  
✅ Email incluído  
✅ Afiliação adicionada

### 3. Configuração Git

```bash
# Local (pcs-meta-repo):
user.name = Demetrios Chiuratto Agourakis
user.email = demetrios@agourakis.med.br

# Global:
user.name = Demetrios Chiuratto Agourakis
user.email = agourakis82@gmail.com
```

**Nota**: Email diverge (local vs global). Para Zenodo, usar email registrado na conta Zenodo.

---

## Checklist para Sucesso

### Antes de Criar Release:

- [x] `.zenodo.json` usa formato RDM
- [x] ORCID correto (0000-0002-8596-5097)
- [x] `resource_type` atualizado
- [x] `CITATION.cff` atualizado
- [ ] Conta Zenodo login com GitHub
- [ ] Email Git = Email Zenodo account
- [ ] GitHub repository criado e público
- [ ] Zenodo integration toggle ON

### Durante Release:

- [ ] Criar release no GitHub (v1.0.0 ou v0.1.0-test)
- [ ] Aguardar webhook Zenodo (5-10 min)
- [ ] Verificar em https://zenodo.org/search?q=pcs-v6.4
- [ ] DOI aparecerá automaticamente

### Após Release Bem-Sucedido:

- [ ] Copiar DOI gerado
- [ ] Atualizar README.md (badge)
- [ ] Atualizar CITATION.cff (doi field)
- [ ] Criar novo commit com DOI

---

## Passos para GitHub + Zenodo

### 1. Criar Repositório GitHub

```bash
# Via web: github.com → New repository
# Name: pcs-v6.4-hyperbolic-geometry
# Description: Cross-linguistic evidence for hyperbolic geometry in semantic networks
# Public
# No initialize (we have files)
```

### 2. Push para GitHub

```bash
cd /home/agourakis82/workspace/hyperbolic-semantic-networks

# Add remote
git remote add origin https://github.com/agourakis82/hyperbolic-semantic-networks.git

# Push
git push -u origin main
git push origin --tags
```

### 3. Enable Zenodo Integration

1. Go to https://zenodo.org/account/settings/github/
2. Login if needed (use GitHub OAuth)
3. Find "pcs-v6.4-hyperbolic-geometry" in list
4. Toggle **ON**
5. Verify webhook in GitHub repo settings

### 4. Test Release (Recomendado)

```bash
# Create test tag
git tag v0.1.0-test -m "Test release for Zenodo integration"
git push origin v0.1.0-test

# Wait 5-10 minutes
# Check: https://zenodo.org/search?q=hyperbolic-semantic-networks

# If DOI appears → SUCCESS!
# If not → Check errors in Zenodo account
```

### 5. Official Release

```bash
# Only after test successful
git tag v1.0.0 -m "v1.0.0 - Publication submission to Network Science"
git push origin v1.0.0

# Or create release via GitHub UI:
# - Tag: v1.0.0
# - Title: "v1.0.0 - Publication Submission"
# - Description: Copy from CHANGELOG.md
```

---

## Troubleshooting

### Error: "Invalid creators format"

**Solução**: Verificar `.zenodo.json` usa `person_or_org`, não `name`

### Error: "ORCID not found"

**Solução**: 
1. Verificar ORCID em https://orcid.org/0000-0002-8596-5097
2. Verificar ORCID linked na conta Zenodo
3. Verificar identifiers format correto

### Webhook não trigger

**Solução**:
1. Verify integration toggle ON em Zenodo settings
2. Check webhook exists em GitHub repo settings
3. Re-toggle integration OFF then ON
4. Try manual: Create release no Zenodo UI

### DOI não aparece

**Solução**:
1. Wait 10-15 minutes (pode demorar)
2. Check Zenodo account "Uploads" section
3. Look for draft deposit
4. Publish manually se necessário

---

## Reference

- Zenodo API docs: https://developers.zenodo.org/
- CITATION.cff spec: https://citation-file-format.github.io/
- GitHub-Zenodo guide: https://guides.github.com/activities/citable-code/

---

**Status**: Configuração correta implementada ✅  
**Next**: Push to GitHub + Enable Zenodo integration

