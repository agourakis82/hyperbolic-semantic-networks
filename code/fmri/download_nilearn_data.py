#!/usr/bin/env python3
"""
Nilearn Dataset Download Script
Hyperbolic Semantic Networks - fMRI Integration

Downloads resting-state fMRI data using Nilearn's built-in datasets.
MUCH EASIER than OpenNeuro or HCP - no AWS, no credentials, just works!

Usage:
    python code/fmri/download_nilearn_data.py --dataset adhd --subjects 10
    python code/fmri/download_nilearn_data.py --dataset development --subjects 20
"""

import argparse
import sys
from pathlib import Path

try:
    from nilearn import datasets
    import numpy as np
except ImportError:
    print("ERROR: nilearn not installed. Run: pip install nilearn")
    sys.exit(1)

# Available Nilearn datasets with resting-state fMRI
DATASETS = {
    "adhd": {
        "name": "ADHD-200 Resting-state",
        "function": datasets.fetch_adhd,
        "subjects": 40,
        "description": "ADHD-200 dataset: 40 subjects with resting-state fMRI"
    },
    "development": {
        "name": "Development fMRI",
        "function": datasets.fetch_development_fmri,
        "subjects": 155,
        "description": "Movie-watching brain development dataset"
    }
}

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "nilearn"


def download_adhd(n_subjects: int = 10):
    """Download ADHD-200 resting-state fMRI dataset."""
    print(f"\n{'='*70}")
    print(f"Downloading ADHD-200 Dataset")
    print(f"Subjects: {n_subjects} (of 40 available)")
    print(f"{'='*70}\n")
    
    # Nilearn automatically downloads to ~/nilearn_data
    # We'll fetch the data and create symlinks to our data directory
    
    adhd_data = datasets.fetch_adhd(n_subjects=n_subjects)
    
    print(f"\n✓ Downloaded {len(adhd_data.func)} subjects")
    print(f"✓ Data location: {adhd_data.description}")
    
    # Create our data directory structure
    dataset_dir = DATA_DIR / "adhd"
    dataset_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file paths for later use
    import json
    metadata = {
        "dataset": "adhd",
        "n_subjects": len(adhd_data.func),
        "func_files": [str(f) for f in adhd_data.func],
        "confounds": [str(f) if f else None for f in adhd_data.confounds],
        "phenotypic": adhd_data.phenotypic if hasattr(adhd_data, 'phenotypic') else None
    }
    
    metadata_file = dataset_dir / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✓ Metadata saved to: {metadata_file}")
    
    # Print summary
    print(f"\n{'='*70}")
    print("Download Summary:")
    print(f"  Functional images: {len(adhd_data.func)}")
    print(f"  First file: {adhd_data.func[0]}")
    print(f"  Metadata: {metadata_file}")
    print(f"{'='*70}\n")
    
    return adhd_data


def download_development(n_subjects: int = 20):
    """Download Development fMRI dataset."""
    print(f"\n{'='*70}")
    print(f"Downloading Development fMRI Dataset")
    print(f"Subjects: {n_subjects} (of 155 available)")
    print(f"{'='*70}\n")
    
    dev_data = datasets.fetch_development_fmri(n_subjects=n_subjects)
    
    print(f"\n✓ Downloaded {len(dev_data.func)} subjects")
    
    # Create our data directory structure
    dataset_dir = DATA_DIR / "development"
    dataset_dir.mkdir(parents=True, exist_ok=True)
    
    # Save metadata
    import json
    metadata = {
        "dataset": "development",
        "n_subjects": len(dev_data.func),
        "func_files": [str(f) for f in dev_data.func],
        "confounds": [str(f) if f else None for f in dev_data.confounds] if hasattr(dev_data, 'confounds') else None
    }
    
    metadata_file = dataset_dir / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✓ Metadata saved to: {metadata_file}")
    
    print(f"\n{'='*70}")
    print("Download Summary:")
    print(f"  Functional images: {len(dev_data.func)}")
    print(f"  First file: {dev_data.func[0]}")
    print(f"  Metadata: {metadata_file}")
    print(f"{'='*70}\n")
    
    return dev_data


def verify_downloads(dataset_name: str):
    """Verify downloaded data."""
    metadata_file = DATA_DIR / dataset_name / "metadata.json"
    
    if not metadata_file.exists():
        print(f"✗ No data found for {dataset_name}")
        print(f"  Expected: {metadata_file}")
        return False
    
    import json
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    print(f"\n{'='*70}")
    print(f"Dataset: {metadata['dataset']}")
    print(f"Subjects: {metadata['n_subjects']}")
    print(f"{'='*70}\n")
    
    # Check if files exist
    missing = 0
    for func_file in metadata['func_files']:
        if not Path(func_file).exists():
            print(f"  ✗ Missing: {func_file}")
            missing += 1
    
    if missing == 0:
        print(f"  ✓ All {len(metadata['func_files'])} files present")
    else:
        print(f"  ✗ {missing}/{len(metadata['func_files'])} files missing")
    
    return missing == 0


def main():
    parser = argparse.ArgumentParser(
        description="Download resting-state fMRI data using Nilearn"
    )
    parser.add_argument(
        "--dataset",
        choices=list(DATASETS.keys()),
        default="adhd",
        help="Dataset to download"
    )
    parser.add_argument(
        "--subjects",
        type=int,
        default=10,
        help="Number of subjects to download"
    )
    parser.add_argument(
        "--method",
        choices=["download", "verify", "list"],
        default="download",
        help="Action to perform"
    )
    
    args = parser.parse_args()
    
    if args.method == "list":
        print("\nAvailable Nilearn Datasets:\n")
        for ds_id, ds_info in DATASETS.items():
            print(f"  {ds_id}:")
            print(f"    Name: {ds_info['name']}")
            print(f"    Subjects: {ds_info['subjects']}")
            print(f"    Description: {ds_info['description']}")
            print()
        return
    
    if args.method == "verify":
        verify_downloads(args.dataset)
        return
    
    # Download
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    if args.dataset == "adhd":
        download_adhd(args.subjects)
    elif args.dataset == "development":
        download_development(args.subjects)


if __name__ == "__main__":
    main()

