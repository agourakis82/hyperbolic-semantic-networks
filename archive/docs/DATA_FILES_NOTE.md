# Note on Large Data Files

**Date**: 2025-11-08

## Overview

Large data files (>100MB) are excluded from git tracking to comply with GitHub's file size limits.

## Excluded Files

The following file patterns are excluded via `.gitignore`:
- `*.csv` - Large CSV data files
- `*.csv.gz` - Compressed CSV files  
- `*.xlsx` - Excel data files
- `*.zip` - Archive files

## Specific Files Excluded

- `data/raw/SWOWRP.raw.20220426.csv` (~500MB)
- `data/raw/conceptnet/conceptnet-assertions-5.7.0.csv.gz` (~200MB)
- `data/raw/SWOW-EN.complete.20180827.csv` (~150MB)
- Other large data files

## Data Availability

Large data files will be:
1. **Released via Zenodo** - As a separate data release with DOI
2. **Available on request** - Contact repository maintainer
3. **Download scripts** - Automated download scripts provided in `scripts/`

## For Reproducibility

To reproduce results:
1. Use data download scripts in `scripts/`
2. Follow instructions in `docs/REPRODUCIBILITY.md`
3. Or use Zenodo data release DOI (when available)

---

**Note**: This approach is standard for scientific repositories with large datasets.

