# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-11-07

### Added
- Taxonomy-based semantic graphs (EN WordNet, ES WordNet, PT BabelNet) aligned with SWOW vocabularies
- Phase-diagram analysis linking clustering ($C$) and degree heterogeneity ($\sigma_k$)
- Discrete Ricci flow experiments demonstrating curvature resistance
- Figure captions, tables, and cover letter compliant with *Nature Communications*

### Changed
- Abstract, Methods, Results, and Discussion reorganized around “hyperbolic sweet spot” framework
- Methods expanded with taxonomy preprocessing, Ricci flow pipeline, and reproducibility checklist
- Results section extended with seven subsections, including robustness and clinical projections
- Discussion updated with “Ricci Flow Resistance” subsection and clarified dataset counts

### Fixed
- Resolved inconsistencies in reported language/dataset numbers between abstract and methods
- Standardized curvature references and section cross-links (e.g., Section 3.5 for robustness)
- Updated manuscript metadata (version, figure/table counts) and changelog documentation

## [1.0.0] - 2025-10-30

### Added
- Initial publication submission to *Network Science*
- Complete manuscript with cross-linguistic analysis (4 languages)
- Publication-quality figures (300 DPI, 6 figures)
- Analysis scripts for reproducibility
- Processed curvature data for all languages
- Comprehensive documentation (README, CITATION, LICENSE)
- GitHub Actions workflow for automated DOI generation

### Analyses
- Ollivier-Ricci curvature computation (4 languages)
- Scale-free topology verification (power-law fitting)
- Baseline model comparisons (ER, BA)
- Bootstrap robustness analysis (50 iterations, CV=10.1%)
- Network size sensitivity (250-750 nodes)
- Statistical tests (Bonferroni correction, Cohen's d)

### Results
- All 4 languages exhibit hyperbolic geometry (κ < 0)
- Mean curvature: -0.166 ± 0.042
- Scale-free networks: α ∈ [2.06, 2.28]
- 100% cross-linguistic consistency

## [0.1.0] - 2025-10-27

### Added
- Methodological corrections from epistemological review (v6.4)
- Complete analysis pipeline
- Documentation of corrections

### Fixed
- Scale-free verification for ES, NL, ZH
- Baseline BA model (m parameter optimization)
- English analysis (R1 file usage)
- Robustness validations

---

## Version Numbering

- **1.0.0**: Publication submission
- **0.x.x**: Development versions
- **1.x.x**: Post-publication updates/corrections

---

[2.0.0]: https://github.com/agourakis82/hyperbolic-semantic-networks/releases/tag/v2.0.0
[1.0.0]: https://github.com/agourakis82/hyperbolic-semantic-networks/releases/tag/v1.0.0
[0.1.0]: https://github.com/agourakis82/hyperbolic-semantic-networks/releases/tag/v0.1.0

