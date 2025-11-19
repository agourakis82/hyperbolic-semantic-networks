# Hyperbolic Geometry of Semantic Networks

**Cross-Linguistic Evidence from Word Association Data**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17489685.svg)](https://doi.org/10.5281/zenodo.17489685)
[![GitHub](https://img.shields.io/github/stars/agourakis82/hyperbolic-semantic-networks?style=social)](https://github.com/agourakis82/hyperbolic-semantic-networks)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

---

## Overview

This repository contains the manuscript, data, code, and supplementary materials for:

**"Boundary Conditions for Hyperbolic Geometry in Semantic Networks"**

**Authors**: Demetrios Chiuratto Agourakis (ORCID: 0000-0002-8596-5097)  
**Institution**: PUC-SP; Faculdade São Leopoldo Mandic  
**Target Journal**: *Nature Communications*  
**Status**: Major Revisions Complete (v2.0)  
**Date**: 2025-11-08

---

## Key Findings

- **8 semantic networks** analyzed (3 SWOW, 2 ConceptNet, 3 taxonomies)
- **Hyperbolic geometry** confined to moderate clustering regime (C ≈ 0.02–0.15)
- **Broad-scale topology**: α = 1.90 ± 0.03 (not strictly scale-free)
- **Clustering moderates geometry**: Configuration nulls increase hyperbolicity (Δκ = +0.17 to +0.22)
- **Ricci flow resistance**: Semantic networks resist geometric flattening
- **Cross-linguistic consistency**: Robust across language families

---

## Repository Structure

```
hyperbolic-semantic-networks/
├── README.md                    # This file
├── CHANGELOG.md                 # Version history
├── LICENSE                      # CC BY 4.0
├── CITATION.cff                 # Citation metadata
├── .zenodo.json                 # Zenodo configuration
│
├── code/                        # Analysis code
│   ├── analysis/                # Python analysis scripts
│   └── figures/                 # Figure generation scripts
│
├── data/                        # Data
│   ├── raw/                     # Original SWOW data (download instructions)
│   └── processed/               # Computed curvature values
│
├── manuscript/                  # Main manuscript
│   ├── main.md                  # Complete manuscript
│   ├── figures/                 # Publication-quality figures (300 DPI)
│   └── references.bib           # Bibliographic references
│
├── results/                     # Computed results
│   ├── curvature/               # Curvature metrics
│   ├── null_models/             # Null model results
│   └── phase_diagram/           # Phase diagram data
│
├── submission/                  # Submission materials
│   ├── cover_letter.md          # Cover letter
│   └── *.pdf, *.zip            # Reviewer responses, submission packages
│
├── docs/                        # Organized documentation
│   ├── INDEX.md                 # Master documentation index
│   ├── session_reports/         # Session reports (24 files)
│   ├── planning/                 # Plans and strategies (38 files)
│   ├── research_reports/         # Research reports (34 files)
│   ├── integration/             # Integration plans (10 files)
│   ├── literature/              # Literature findings (6 files)
│   ├── manuscript_versions/     # Manuscript versions (16 files)
│   └── guides/                  # Usage guides (4 files)
│
├── config/                      # Configuration files
├── scripts/                      # Utility scripts
├── archive/                      # Archived files (31 files)
└── .github/workflows/            # CI/CD pipelines
```

**📚 Documentation**: 
- [`docs/INDEX.md`](docs/INDEX.md) - Complete documentation index
- [`docs/REPOSITORY_STRUCTURE.md`](docs/REPOSITORY_STRUCTURE.md) - Detailed repository structure
- [`docs/planning/CHECKLIST_Nature_Submission.md`](docs/planning/CHECKLIST_Nature_Submission.md) - Submission checklist
- [`docs/planning/NEXT_STEPS.md`](docs/planning/NEXT_STEPS.md) - Next steps

---

## Quick Start

### Requirements

- Python 3.9+
- See `code/analysis/requirements.txt` for dependencies

### Installation

```bash
git clone https://github.com/agourakis82/hyperbolic-semantic-networks.git
cd hyperbolic-semantic-networks
pip install -r code/analysis/requirements.txt
```

### Reproduce Analysis

```bash
# Run complete analysis pipeline
cd code/analysis
python run_analysis_pipeline.py

# Generate figures
cd ../figures
python generate_all_figures.py
```

---

## Data

**Source**: [Small World of Words (SWOW)](https://smallworldofwords.org)

**Languages**: Spanish, Dutch, Chinese, English

**Processed Data**: Available in `data/processed/`
- `curvature_metrics_4lang.csv` (curvature values)
- `network_statistics.json` (summary stats)

**Raw Data**: Not included due to size. Download from SWOW website:
- Instructions in `data/raw/DATA_DOWNLOAD.md`

---

## Citation

If you use this code or data, please cite:

```bibtex
@article{agourakis2025hyperbolic,
  title={Universal Hyperbolic Geometry of Semantic Networks: Cross-Linguistic Evidence},
  author={Agourakis, Demetrios},
  journal={Network Science},
  year={2025},
  publisher={Cambridge University Press},
  doi={10.XXXX/XXXXX}
}
```

Also cite the SWOW dataset:

```bibtex
@article{de2019small,
  title={The Small World of Words English word association norms for over 12,000 cue words},
  author={De Deyne, Simon and Navarro, Danielle J and Perfors, Amy and Brysbaert, Marc and Storms, Gert},
  journal={Behavior Research Methods},
  volume={51},
  pages={987--1006},
  year={2019}
}
```

---

## License

- **Code**: MIT License
- **Data**: CC BY 4.0
- **Manuscript**: CC BY 4.0

See `LICENSE` for details.

---

## Contact

**Demetrios Chiuratto Agourakis**  
Email: demetrios@agourakis.med.br  
ORCID: 0000-0002-8596-5097

---

## Acknowledgments

- Small World of Words project team
- [Funding sources if applicable]
- Contributors

---

## Version History

See `CHANGELOG.md` for detailed version history.

**Current Version**: v1.0.0 (Publication Submission)

