# Next Steps for v6.4 Submission

**Repository Created**: 2025-10-30  
**Status**: ✅ Ready for GitHub + Zenodo integration

---

## Phase 3: Zenodo Integration (TODO)

### 1. Diagnose Previous Zenodo/ORCID Issue

**Problem reported**: Integration failed due to author/ORCID mismatch

**To investigate**:
```bash
# Check current Git config
git config --get user.name
git config --get user.email

# Verify ORCID in files
grep -r "0000-0000-0000-0000" .
```

**Common causes**:
- Git email ≠ Zenodo account email
- ORCID not properly linked in Zenodo account
- Missing or incorrect `.zenodo.json` format
- GitHub-Zenodo webhook not configured

**To fix**:
1. Update `.zenodo.json` with correct ORCID and email
2. Update `CITATION.cff` with correct ORCID
3. Verify Zenodo account settings
4. Test with v0.1.0-test release first

### 2. GitHub Repository Setup

```bash
# Create GitHub repo (do this on github.com):
# - Name: pcs-v6.4-hyperbolic-geometry
# - Description: Cross-linguistic evidence for hyperbolic geometry in semantic networks
# - Public repository
# - No README (we have one)

# Add remote and push
git remote add origin https://github.com/YOUR_USERNAME/pcs-v6.4-hyperbolic-geometry.git
git push -u origin main
git push --tags
```

### 3. Enable Zenodo Integration

1. Go to https://zenodo.org/account/settings/github/
2. Login with GitHub
3. Find "pcs-v6.4-hyperbolic-geometry" in list
4. Toggle ON to enable integration
5. Verify webhook created in GitHub settings

### 4. Test Release

```bash
# Create test release
git tag v0.1.0-test -m "Test release for Zenodo integration"
git push origin v0.1.0-test
```

**Expected outcome**:
- GitHub Actions workflow runs
- Zenodo receives webhook
- DOI created within 5-10 minutes
- Check: https://zenodo.org/search?q=pcs-v6.4

**If successful**:
- Update README.md with DOI badge
- Update CITATION.cff with DOI
- Delete test release
- Create official v1.0.0 release

### 5. Official Release

```bash
# Create release on GitHub:
# - Tag: v1.0.0
# - Title: "v1.0.0 - Publication Submission"
# - Description: Copy from CHANGELOG.md
# - Attach: release-archive.tar.gz (optional)
```

---

## Phase 4: Clean pcs-meta-repo (TODO)

See main plan for cleanup strategy.

**Key actions**:
1. Create cleanup branch
2. Remove ~200 temporary files (*_REPORT.md, *_STATUS.md)
3. Update .gitignore
4. Commit with: "chore: establish clean Q1 structure"
5. Create v0.8.0 tag

---

## Phase 5: Final Submission

### Update v6.4 Repository
- [ ] Add DOI to README.md
- [ ] Add DOI to CITATION.cff
- [ ] Update manuscript with DOI
- [ ] Create GitHub release notes

### Prepare Manuscript
- [ ] Convert main.md → LaTeX (Network Science template)
- [ ] Finalize figure legends
- [ ] Write supplementary materials
- [ ] Prepare cover letter
- [ ] Submit to Network Science

---

## Checklist Before Submission

Repository:
- [x] Q1 structure implemented
- [x] All files present (manuscript, figures, code, data)
- [x] README comprehensive
- [x] LICENSE clear (CC BY 4.0)
- [x] CITATION.cff complete
- [x] .zenodo.json configured
- [ ] GitHub repository created
- [ ] Zenodo integration active
- [ ] DOI obtained
- [ ] Test release successful

Manuscript:
- [x] Content complete (389 lines)
- [x] Figures ready (6 × 300 DPI)
- [ ] Convert to LaTeX
- [ ] Supplementary materials
- [ ] Cover letter

Scientific:
- [x] Cross-linguistic evidence (4 languages)
- [x] Statistical tests (Bonferroni, Cohen's d)
- [x] Robustness analysis (bootstrap CV=10.1%)
- [x] Baseline comparisons (ER, BA)
- [x] Scale-free verification
- [x] Methods documentation

---

## Timeline

**Today** (2025-10-30):
- [x] Create repository structure
- [x] Initial commit
- [ ] Push to GitHub
- [ ] Configure Zenodo

**Tomorrow** (2025-10-31):
- [ ] Test Zenodo integration
- [ ] Get DOI
- [ ] Update with DOI

**This Week**:
- [ ] Clean pcs-meta-repo
- [ ] Convert manuscript to LaTeX
- [ ] Finalize supplementary materials

**Next Week**:
- [ ] Submit to Network Science
- [ ] Celebrate! 🎉

---

## Support

If Zenodo integration fails:
1. Check Zenodo community forum
2. Email Zenodo support: info@zenodo.org
3. Alternative: Manual deposit (upload .tar.gz directly)

---

**Status**: Fase 2 completa (repository created) ✅  
**Next**: Fase 3 (Zenodo integration) ⏭️

