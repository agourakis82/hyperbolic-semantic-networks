# Submission Checklist — v4.0

Updated: 2026-03-08

## Manuscript

- [x] Title: "When Are Semantic Networks Hyperbolic? A Curvature Phase Transition Theory with Cross-Linguistic Validation"
- [x] Abstract updated (saturation β̄=0.28, CQG parallel, Euclidean tree theorem, geometric universality)
- [x] 20 pages, 10 figures, 7 tables, 30 references; §6.6 GNN, §6.7 CQG parallel, Appendix D hypergraph added
- [x] Terminology consistent (Ollivier-Ricci with en-dash, "sign change" not "phase transition" for finite N)
- [x] Cross-references verified (0 undefined refs)
- [x] Sounio cross-validation paragraph added (section 4.6)
- [x] PDF compiled clean: `pdflatex monograph.tex` x2, 0 errors
- [x] §6.4 Clinical: ADHD phase-level analysis, ASD falsifiable prediction, World of Words future test
- [x] Ricci flow section: caterpillar-tree theorem (arXiv:2601.02673) explains Euclidean classification
- [x] Introduction: curvature roadmap survey (arXiv:2510.22599) cited

## Cover Letter

- [x] Rewritten for v3.0 (March 2026)
- [x] Title matches manuscript
- [x] 4 novel contributions described
- [x] 5 reviewer suggestions with contact info
- [x] Competing interests declaration

## Figures

- [x] All 11 figures present in `figures/monograph/` (regenerated Mar 9 with 19-network dataset)
- [x] PDF and PNG versions available
- [ ] Verify 300 DPI resolution for print submission
- [x] Captions match manuscript text
- [x] Figure 2 (bridge): 19 dots (16 core + 3 depression variants)
- [x] Figure 3 (clustering): all 16 networks plotted, C*=0.05 line visible
- [x] Figure 11 (power-law): newly generated, β̄=0.283±0.034

## Tables

- [x] 6 tables formatted in LaTeX
- [x] Numerical data cross-checked against result JSON files

## References

- [x] 30 references, all with complete bibitem entries
- [x] All citations in text have corresponding bibitem
- [ ] Verify DOI/URLs are valid and current

## Code and Data

- [x] GitHub repo contains all scripts and results
- [x] Julia, Rust, Lean, Sounio code all present
- [x] RUNME.md written at repo root (full reproduction instructions)

## Formal Verification

- [x] `lake build` passes with 0 errors
- [x] 0 sorry in 7 core modules (documented in FORMALIZATION_STATUS.md)
- [x] SounioVerification.lean: Theorems 1-14 (Group 14 complete), 0 sorry
- [x] Phase 6-8 hypercomplex, epistemic flow, ADHD clinical — all proved in Lean

## arXiv Metadata

- [x] Abstract within 1,920 character limit (~1,580 chars)
- [x] Categories: cs.SI (primary), math.CO, physics.soc-ph
- [x] Keywords updated

## Remaining Items

- [ ] External spell-check (Grammarly/LanguageTool)
- [ ] Figure DPI verification for print
- [ ] DOI/URL link check
- [x] RUNME.md verified (all commands tested)
- [ ] arXiv upload
- [ ] Journal portal submission

## Statistics

- **Version**: 5.0
- **Date**: 2026-03-08
- **Pages**: 21
- **Figures**: 10
- **Tables**: 7
- **References**: 35
- **Networks analyzed**: 16 (11 training + 5 held-out test)
- **Languages**: 7 (ES, EN, ZH, NL, PT, RU, AR) + Arg. Spanish, British English, German
- **Lean modules**: 25
- **Lean sorry (core)**: 0
- **Test set accuracy**: 4/5 correct (FrameNet borderline at C=0.045)
