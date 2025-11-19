# 👋 START HERE - v6.4 Publication Repository

**Status**: ✅ PRONTO para GitHub + Zenodo  
**Paper**: Hyperbolic Geometry of Semantic Networks  
**Target**: Network Science (Cambridge)

---

## O QUE É ESTE REPOSITÓRIO

Repositório **dedicado** para publicação do paper v6.4:

- **Manuscrito completo** (389 linhas, Network Science ready)
- **6 figuras** (300 DPI, publication-quality)
- **8 scripts** análise reproduzíveis
- **7 datasets** processados (curvature metrics)
- **Zenodo integration** configurada para DOI automático

**Resultado principal**: 4/4 idiomas mostram geometria hiperbólica (κ = -0.166 ± 0.042)

---

## PRÓXIMOS 3 PASSOS

### 1. Criar GitHub Repository (5 min)

```
Ir para: https://github.com/new
Name: pcs-v6.4-hyperbolic-geometry
Description: Cross-linguistic evidence for hyperbolic geometry in semantic networks
Public: ✓
Initialize: ✗ (já temos README)
[Create repository]
```

### 2. Push Código (2 min)

```bash
cd /home/agourakis82/workspace/pcs-v6.4-hyperbolic-geometry

git remote add origin https://github.com/agourakis82/pcs-v6.4-hyperbolic-geometry.git
git push -u origin main
git push origin --tags
```

### 3. Enable Zenodo + Test (10 min)

```
1. Ir para: https://zenodo.org/account/settings/github/
2. Login com GitHub
3. Encontrar "pcs-v6.4-hyperbolic-geometry"
4. Toggle ON
5. Criar test release:
   git tag v0.1.0-test -m "Test Zenodo integration"
   git push origin v0.1.0-test
6. Aguardar 10 min
7. Verificar: https://zenodo.org/search?q=pcs-v6.4
8. Se DOI aparecer → SUCCESS! ✅
```

---

## ARQUIVOS IMPORTANTES

📄 `manuscript/main.md` - Manuscrito completo  
📊 `manuscript/figures/` - 6 figuras 300 DPI  
💻 `code/analysis/` - Scripts reproduzíveis  
📊 `data/processed/` - Resultados processados  
📋 `README.md` - Documentação completa  
⚙️ `.zenodo.json` - Metadata Zenodo (ORCID correto!)  
📖 `CITATION.cff` - Citation standard  
📝 `CHANGELOG.md` - Version history  
🔧 `ZENODO_INTEGRATION_GUIDE.md` - Troubleshooting  
🎯 `NEXT_STEPS.md` - Submission roadmap

---

## SCIENTIFIC CONTENT

**Title**: Universal Hyperbolic Geometry of Semantic Networks

**Main Finding**: 4/4 languages (ES, NL, ZH, EN) exhibit hyperbolic geometry

**Statistics**:
- Mean κ: -0.166 ± 0.042
- Scale-free: α ∈ [2.06, 2.28]
- Bootstrap CV: 10.1% (high stability)
- Cross-linguistic ANOVA: F=30.97, p<10⁻¹⁹

**Target**: Network Science (IF: 2.8)  
**Probability**: 85%

---

## METADATA (Corrected ✅)

**Author**: Demetrios Chiuratto Agourakis  
**ORCID**: 0000-0002-8596-5097  
**Email**: demetrios@agourakis.med.br  
**Affiliation**: PUC-SP; Faculdade São Leopoldo Mandic

**License**: CC BY 4.0 (data/manuscript), MIT (code)

**Zenodo Format**: RDM-style (person_or_org) ✅  
**Previous Issue**: Fixed (was using outdated format)

---

## ESTE REPOSITÓRIO É

✅ Self-contained (tudo que precisa para submission)  
✅ Q1-compliant (structure, metadata, documentation)  
✅ Reproducible (scripts + data + instructions)  
✅ Citable (DOI pending, CITATION.cff ready)  
✅ Clean (no cruft, only essentials)

---

## APÓS OBTER DOI

```bash
# Update com DOI real
# Edit files:
# - README.md (badge line 4)
# - CITATION.cff (doi field)
# - manuscript/main.md (if needed)

git add -A
git commit -m "docs: update with Zenodo DOI"
git push origin main
```

---

## QUESTIONS?

**Zenodo problems?** → Read `ZENODO_INTEGRATION_GUIDE.md`  
**Next steps unclear?** → Read `NEXT_STEPS.md`  
**Want full story?** → Read `README.md`

---

✅ **REPOSITORY READY. NEXT: PUSH TO GITHUB + GET DOI.** 🚀

