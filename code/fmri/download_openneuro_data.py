#!/usr/bin/env python3
"""
OpenNeuro Data Download Script
Hyperbolic Semantic Networks - fMRI Integration

Downloads resting-state fMRI data from OpenNeuro datasets.
Much easier than HCP - no registration required!

Usage:
    python code/fmri/download_openneuro_data.py --dataset ds000228 --subjects 10
    python code/fmri/download_openneuro_data.py --dataset ds000030 --subjects 20
"""

import argparse
import subprocess
import sys
from pathlib import Path
import urllib.request
import json

# OpenNeuro datasets with resting-state fMRI
DATASETS = {
    "ds000228": {
        "name": "UCLA Resting-state fMRI",
        "url": "https://openneuro.org/datasets/ds000228",
        "s3": "s3://openneuro.org/ds000228",
        "subjects": 122,
        "subject_prefix": "pixar",
        "description": "122 healthy adults, well-validated dataset"
    },
    "ds000030": {
        "name": "UCLA CNP",
        "url": "https://openneuro.org/datasets/ds000030",
        "s3": "s3://openneuro.org/ds000030",
        "subjects": 265,
        "subject_prefix": "sub",
        "description": "Large consortium dataset with multiple tasks"
    },
    "ds005747": {
        "name": "7T Resting-state",
        "url": "https://openneuro.org/datasets/ds005747",
        "s3": "s3://openneuro.org/ds005747",
        "subjects": 30,
        "subject_prefix": "sub",
        "description": "High-resolution 7T fMRI data"
    }
}

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "openneuro"


def check_aws_cli() -> bool:
    """Check if AWS CLI is installed."""
    try:
        result = subprocess.run(
            ["aws", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ AWS CLI found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ AWS CLI not found. Install with: pip install awscli")
        return False


def download_dataset_aws(dataset_id: str, num_subjects: int) -> bool:
    """Download dataset from OpenNeuro S3 bucket."""
    if dataset_id not in DATASETS:
        print(f"Error: Unknown dataset '{dataset_id}'")
        print(f"Available: {', '.join(DATASETS.keys())}")
        return False
    
    dataset = DATASETS[dataset_id]
    dataset_dir = DATA_DIR / dataset_id
    dataset_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*70}")
    print(f"Downloading: {dataset['name']}")
    print(f"Dataset: {dataset_id}")
    print(f"Subjects: {num_subjects} (of {dataset['subjects']} available)")
    print(f"Target: {dataset_dir}")
    print(f"{'='*70}\n")
    
    # Download first N subjects
    success_count = 0
    for i in range(1, num_subjects + 1):
        subject_id = f"sub-{dataset['subject_prefix']}{i:03d}"
        
        print(f"\n[{i}/{num_subjects}] Downloading {subject_id}...")
        
        # Try downloading all functional data first
        cmd = [
            "aws", "s3", "sync",
            f"{dataset['s3']}/{subject_id}/",
            str(dataset_dir / subject_id),
            "--no-sign-request",
            "--exclude", "*",
            "--include", "func/*bold.nii.gz",
            "--include", "func/*bold.json",
            "--include", "func/*rest*.nii.gz",
            "--include", "func/*rest*.json"
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"  ✓ {subject_id} downloaded")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"  ✗ {subject_id} failed: {e}")
    
    print(f"\n{'='*70}")
    print(f"Download complete: {success_count}/{num_subjects} subjects")
    print(f"{'='*70}")
    
    return success_count > 0


def download_direct_http(dataset_id: str, num_subjects: int) -> bool:
    """Download via direct HTTP (fallback if AWS fails)."""
    print("\nDirect HTTP download not yet implemented.")
    print("Please use AWS CLI method or manual download from:")
    print(f"  {DATASETS[dataset_id]['url']}")
    return False


def verify_downloads(dataset_id: str) -> dict:
    """Verify which subjects have been downloaded."""
    dataset_dir = DATA_DIR / dataset_id
    if not dataset_dir.exists():
        return {}
    
    status = {}
    for subject_dir in sorted(dataset_dir.glob("sub-*")):
        subject_id = subject_dir.name
        func_dir = subject_dir / "func"
        
        if not func_dir.exists():
            status[subject_id] = "missing"
            continue
        
        nii_files = list(func_dir.glob("*rest*.nii.gz"))
        json_files = list(func_dir.glob("*rest*.json"))
        
        if len(nii_files) > 0:
            status[subject_id] = "complete" if len(json_files) > 0 else "partial"
        else:
            status[subject_id] = "empty"
    
    return status


def main():
    parser = argparse.ArgumentParser(
        description="Download resting-state fMRI data from OpenNeuro"
    )
    parser.add_argument(
        "--dataset",
        choices=list(DATASETS.keys()),
        default="ds000228",
        help="OpenNeuro dataset ID"
    )
    parser.add_argument(
        "--subjects",
        type=int,
        default=10,
        help="Number of subjects to download (default: 10)"
    )
    parser.add_argument(
        "--method",
        choices=["aws", "http", "verify", "list"],
        default="aws",
        help="Download method"
    )
    
    args = parser.parse_args()
    
    if args.method == "list":
        print("\nAvailable OpenNeuro Datasets:\n")
        for ds_id, ds_info in DATASETS.items():
            print(f"  {ds_id}:")
            print(f"    Name: {ds_info['name']}")
            print(f"    Subjects: {ds_info['subjects']}")
            print(f"    URL: {ds_info['url']}")
            print(f"    Description: {ds_info['description']}")
            print()
        return
    
    if args.method == "verify":
        print(f"\nVerifying downloads for {args.dataset}...\n")
        status = verify_downloads(args.dataset)
        
        if not status:
            print(f"No data found for {args.dataset}")
            return
        
        print("Download Status:")
        print("-" * 40)
        for subj, stat in status.items():
            symbol = "✓" if stat == "complete" else "○" if stat == "partial" else "✗"
            print(f"  {symbol} {subj}: {stat}")
        
        complete = sum(1 for s in status.values() if s == "complete")
        print(f"\nComplete: {complete}/{len(status)}")
        return
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    if args.method == "aws":
        if not check_aws_cli():
            sys.exit(1)
        download_dataset_aws(args.dataset, args.subjects)
    
    elif args.method == "http":
        download_direct_http(args.dataset, args.subjects)


if __name__ == "__main__":
    main()

