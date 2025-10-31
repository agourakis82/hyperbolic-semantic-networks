# Hyperbolic Geometry of Semantic Networks

**Cross-Linguistic Evidence from Word Association Data**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXX)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

---

## Overview

This repository contains the manuscript, data, code, and supplementary materials for:

**"Universal Hyperbolic Geometry of Semantic Networks: Cross-Linguistic Evidence"**

**Authors**: Demetrios Agourakis (ORCID: 0000-0000-0000-0000)  
**Institution**: [To be added]  
**Submitted to**: *Network Science* (Cambridge University Press)  
**Date**: 2025-10-30

---

## Key Findings

- **4/4 languages** exhibit hyperbolic geometry (ES, NL, ZH, EN)
- **Mean curvature**: κ = -0.166 ± 0.042 (all negative)
- **Scale-free topology**: α ∈ [2.06, 2.28]
- **Robust across network sizes**: 250-750 nodes
- **High stability**: Bootstrap CV = 10.1%

---

## Repository Structure

```
├── .github/workflows/      # GitHub Actions for CI/CD
├── manuscript/             # Main manuscript files
│   ├── figures/           # Publication-quality figures (300 DPI)
│   └── main.md            # Manuscript (Markdown/LaTeX)
├── data/
│   ├── raw/               # Original SWOW data (see DATA.md)
│   └── processed/         # Computed curvature values
├── code/
│   ├── analysis/          # Analysis scripts (Python)
│   └── figures/           # Figure generation scripts
├── supplementary/         # Supplementary materials
├── README.md              # This file
├── LICENSE                # CC BY 4.0
├── CITATION.cff           # Citation metadata
├── CHANGELOG.md           # Version history
└── .gitignore             # Git ignore rules
```

---

## Quick Start

### Requirements

- Python 3.9+
- See `code/analysis/requirements.txt` for dependencies

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/pcs-v6.4-hyperbolic-geometry.git
cd pcs-v6.4-hyperbolic-geometry
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

**Demetrios Agourakis**  
Email: [to be added]  
ORCID: [0000-0000-0000-0000]

---

## Acknowledgments

- Small World of Words project team
- [Funding sources if applicable]
- Contributors

---

## Version History

See `CHANGELOG.md` for detailed version history.

**Current Version**: v1.0.0 (Publication Submission)

