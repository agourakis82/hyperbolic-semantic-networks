# Raw Data Download Instructions

Raw SWOW data is not included in this repository due to size and licensing considerations.

## Download

**Source**: [Small World of Words](https://smallworldofwords.org/en/project/explore)

### Required Files

1. **Spanish (ES)**: `strength.SWOW-ES.R100.csv`
2. **Dutch (NL)**: `strength.SWOW-NL.R100.csv`
3. **Chinese (ZH)**: `strength.SWOW-ZH.R100.csv`
4. **English (EN)**: `strength.SWOW-EN.R1.20180827.csv` (R1 only, not R123)

### Steps

1. Visit https://smallworldofwords.org/en/project/explore
2. Download the "Strength" files for each language
3. Place files in this directory (`data/raw/`)
4. Verify file integrity:
   ```bash
   # Expected file sizes (approximate):
   # ES: ~15 MB
   # NL: ~20 MB
   # ZH: ~12 MB
   # EN: ~8 MB (R1 only)
   ```

## Data Format

Files are CSV with columns:
- `cue`: Word cue
- `response`: Word response
- `R1` (or `R100`): First response strength (0-1)

Example:
```
cue,response,R1
dog,cat,0.35
dog,animal,0.28
...
```

## License

SWOW data is licensed under CC BY-NC-SA 4.0.  
See: https://smallworldofwords.org/en/project/home

## Citation

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

