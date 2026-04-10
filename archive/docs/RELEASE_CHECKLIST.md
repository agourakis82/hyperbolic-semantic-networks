# Release Checklist - v0.1.0

**Date**: 2025-11-08  
**Status**: ✅ Ready for Release

## Pre-Release Validation

### Build & Compilation
- [x] Rust libraries build successfully
- [x] Julia dependencies install correctly
- [x] Module loads without errors
- [x] No compilation warnings (critical)

### Testing
- [x] Rust tests pass
- [x] Julia basic tests pass
- [x] Test suite structure complete
- [x] No critical test failures

### Validation
- [x] Literature validation complete
- [x] Q1 SOTA properties verified
- [x] Numerical correctness confirmed
- [x] File structure validated

### Documentation
- [x] README.md complete
- [x] Quick start guide
- [x] Build guide
- [x] Release notes
- [x] API documentation
- [x] Examples provided

### Code Quality
- [x] Code structure organized
- [x] Comments and docstrings present
- [x] No obvious bugs
- [x] Error handling implemented

## Release Artifacts

### Version Information
- [x] Version: 0.1.0
- [x] Tag: v0.1.0
- [x] Changelog: docs/RELEASE_NOTES.md

### Metadata
- [x] .zenodo.json configured
- [x] LICENSE file present
- [x] CITATION file (optional)
- [x] Authors and affiliations

### Files
- [x] All source code included
- [x] Documentation complete
- [x] Scripts and examples
- [x] Test files included

## Release Process

### Git Operations
- [x] All changes committed
- [x] Tag created: v0.1.0
- [ ] Push to remote (manual step)
  ```bash
  git push origin main
  git push origin v0.1.0
  ```

### Zenodo Release
- [ ] Create Zenodo deposit
- [ ] Upload release archive
- [ ] Fill metadata from .zenodo.json
- [ ] Publish on Zenodo
- [ ] Copy DOI

### GitHub Release
- [ ] Create GitHub release
- [ ] Tag: v0.1.0
- [ ] Add release notes
- [ ] Add Zenodo DOI
- [ ] Publish

### Post-Release
- [ ] Update README with DOI
- [ ] Update .zenodo.json with DOI
- [ ] Announce release (if applicable)

## Known Limitations

Documented in RELEASE_NOTES.md:
- Triadic-rewire placeholder
- Parallel optimization in progress
- Test coverage ~70% (targeting 90%+)

## Success Criteria

- [x] All validation checks pass
- [x] Documentation complete
- [x] Code ready for use
- [x] Release artifacts prepared
- [ ] DOI obtained from Zenodo
- [ ] GitHub release published

---

**Status**: ✅ Ready for final release steps (push, Zenodo, GitHub)

**Next Action**: Execute manual release steps (see scripts/create_zenodo_release.md)

