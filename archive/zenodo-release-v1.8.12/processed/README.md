# Processed Data

This directory contains computed curvature values and network statistics for all four languages.

## Files

- `scale_free_analysis_v6.4.json` - Power-law fitting results (α exponents)
- `baseline_correction_v6.4.json` - Baseline model curvatures (ER, BA)
- `english_analysis_v6.4.json` - English network curvature
- `robustness_analysis_v6.4.json` - Bootstrap stability analysis
- `statistical_tests_v6.4.json` - Statistical test results
- `er_sensitivity_v6.4.json` - ER parameter sensitivity analysis
- `network_science_summary_v6.4.json` - Complete summary statistics

## Data Format

Each JSON file contains:
```json
{
  "language": "ES/NL/ZH/EN",
  "mean_curvature": -0.XXX,
  "std_curvature": 0.XXX,
  "curvature_range": [-1.0, 1.0],
  "network_stats": {
    "nodes": 500,
    "edges": 800,
    ...
  }
}
```

## Citation

If you use this data, please cite the original SWOW dataset:

```
De Deyne, S., Navarro, D. J., Perfors, A., Brysbaert, M., & Storms, G. (2019).
The Small World of Words English word association norms for over 12,000 cue words.
Behavior Research Methods, 51, 987–1006.
```

## License

CC BY 4.0

