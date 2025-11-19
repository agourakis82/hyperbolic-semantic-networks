# Zenodo Troubleshooting - Não Apareceu DOI

**Situação**: Tag v0.1.0-test pushed, mas DOI não apareceu em 10-15 min

---

## POSSÍVEIS CAUSAS

### 1. Integration Não Habilitada ⚠️

**Verificar**: https://zenodo.org/account/settings/github/

**Deve mostrar**:
- Lista de repositórios GitHub
- `agourakis82/hyperbolic-semantic-networks` com toggle **ON** (verde)

**Se estiver OFF (cinza)**:
- Click no toggle para ON
- Aguardar "Webhook created"
- **Depois criar novo test release** (v0.1.1-test)

---

### 2. Webhook Não Criado

**Verificar**: https://github.com/agourakis82/hyperbolic-semantic-networks/settings/hooks

**Deve mostrar**:
- Webhook para `zenodo.org`
- Status: Recent deliveries (verde)

**Se não houver webhook**:
- Zenodo integration não foi ativada
- Toggle ON no Zenodo
- Delete v0.1.0-test e recrie

---

### 3. Zenodo Precisa de Release (não Tag)

Zenodo às vezes só processa **GitHub Releases**, não tags simples.

**Criar Release via GitHub UI**:

1. Ir: https://github.com/agourakis82/hyperbolic-semantic-networks/releases/new

2. Preencher:
   - **Tag**: v0.1.1-test (ou usar v0.1.0-test existente)
   - **Title**: "v0.1.1-test - Zenodo Integration Test"
   - **Description**: "Test release for Zenodo DOI generation"
   - **Pre-release**: ✓ (marcar)

3. Click: **Publish release**

4. Aguardar 10 min

5. Verificar: https://zenodo.org/me/uploads

---

### 4. Zenodo em Sandbox Mode

Se você usou Zenodo Sandbox (sandbox.zenodo.org), não vai aparecer no Zenodo production.

**Verificar**: Qual Zenodo você habilitou?
- Production: https://zenodo.org
- Sandbox: https://sandbox.zenodo.org

**Se foi Sandbox**:
- Toggle OFF no sandbox
- Toggle ON no production
- Recrie release

---

### 5. Processing Delay (mais comum)

Às vezes Zenodo demora **15-30 minutos**.

**Action**: Aguardar mais 15 min e verificar periodicamente:
- https://zenodo.org/me/uploads
- https://zenodo.org/search?q=hyperbolic-semantic-networks

---

## SOLUÇÃO ALTERNATIVA: Upload Manual

Se webhook não funcionar, você pode fazer upload manual:

### 1. Create Archive

```bash
cd /home/agourakis82/workspace/hyperbolic-semantic-networks
tar -czf hyperbolic-semantic-networks-v1.0.0.tar.gz \
  --exclude='.git' \
  .
```

### 2. Upload no Zenodo

1. Ir: https://zenodo.org/deposit/new
2. Upload: `hyperbolic-semantic-networks-v1.0.0.tar.gz`
3. Fill metadata (use info from .zenodo.json)
4. Click: **Publish**
5. Get DOI

**Vantagem**: Garantido funcionar  
**Desvantagem**: Manual (não automático)

---

## CHECKLIST DEBUG

Verificar cada item:

- [ ] Zenodo integration toggle está **ON** (verde)?
- [ ] Webhook aparece em GitHub settings/hooks?
- [ ] É Zenodo production (não sandbox)?
- [ ] Passou >15 minutos desde push?
- [ ] Tentou criar GitHub Release (não só tag)?
- [ ] Email GitHub = Email Zenodo?

---

## PRÓXIMO PASSO RECOMENDADO

### Opção 1: Aguardar Mais (15-30 min)

Às vezes demora. Verificar de novo em:
- https://zenodo.org/me/uploads

### Opção 2: Criar GitHub Release (não só tag)

Via UI: https://github.com/agourakis82/hyperbolic-semantic-networks/releases/new

### Opção 3: Upload Manual

Se webhook não funcionar, fazer upload manual (garantido)

---

**O que você quer tentar primeiro?**

**a)** Aguardar mais 15 min  
**b)** Criar GitHub Release (via UI)  
**c)** Verificar se Zenodo toggle está ON  
**d)** Upload manual (plano B)

---

**Não se preocupe**, isso é comum na primeira vez. Vamos resolver! 💪
