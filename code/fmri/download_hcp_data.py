#!/usr/bin/env python3
"""
HCP Data Download Script
Hyperbolic Semantic Networks - fMRI Integration

Downloads parcellated fMRI time series for 10 HCP subjects.
Requires: AWS CLI configured, or manual download from ConnectomeDB.

Usage:
    python code/fmri/download_hcp_data.py --method aws
    python code/fmri/download_hcp_data.py --method manual
"""

import argparse
import subprocess
import sys
from pathlib import Path

# 10 subjects for proof-of-concept (first batch, well-validated)
SUBJECTS = [
    "100307", "100408", "101107", "101309", "101915",
    "103111", "103414", "103818", "105014", "105115"
]

HCP_S3_BUCKET = "s3://hcp-openaccess/HCP_1200"
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "hcp"


def download_subject_aws(subject_id: str) -> bool:
    """Download subject data from AWS S3 bucket."""
    subject_dir = DATA_DIR / subject_id
    subject_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n[{subject_id}] Downloading from AWS S3...")
    
    # Download resting-state fMRI (both LR and RL)
    cmd_rest = [
        "aws", "s3", "sync",
        f"{HCP_S3_BUCKET}/{subject_id}/MNINonLinear/Results/",
        str(subject_dir),
        "--no-sign-request",
        "--exclude", "*",
        "--include", "*rfMRI_REST*Atlas_MSMAll.dtseries.nii"
    ]
    
    # Download language task fMRI (both LR and RL)
    cmd_lang = [
        "aws", "s3", "sync",
        f"{HCP_S3_BUCKET}/{subject_id}/MNINonLinear/Results/",
        str(subject_dir),
        "--no-sign-request",
        "--exclude", "*",
        "--include", "*tfMRI_LANGUAGE*Atlas_MSMAll.dtseries.nii"
    ]
    
    try:
        subprocess.run(cmd_rest, check=True)
        subprocess.run(cmd_lang, check=True)
        print(f"[{subject_id}] ✓ Download complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[{subject_id}] ✗ Download failed: {e}")
        return False


def check_aws_cli() -> bool:
    """Check if AWS CLI is installed and configured."""
    try:
        result = subprocess.run(
            ["aws", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"AWS CLI found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: AWS CLI not found. Install with: pip install awscli")
        return False


def print_manual_instructions():
    """Print manual download instructions."""
    print("\n" + "="*70)
    print("MANUAL DOWNLOAD INSTRUCTIONS")
    print("="*70)
    print("\n1. Go to: https://db.humanconnectome.org")
    print("2. Login with your institutional credentials")
    print("3. Navigate to: WU-Minn HCP Data - 1200 Subjects")
    print("4. For each subject, download:")
    print("   - rfMRI_REST1_LR_Atlas_MSMAll.dtseries.nii")
    print("   - rfMRI_REST1_RL_Atlas_MSMAll.dtseries.nii")
    print("   - tfMRI_LANGUAGE_LR_Atlas_MSMAll.dtseries.nii")
    print("   - tfMRI_LANGUAGE_RL_Atlas_MSMAll.dtseries.nii")
    print("\n5. Save to: data/hcp/<subject_id>/")
    print("\nSubjects to download:")
    for i, subj in enumerate(SUBJECTS, 1):
        print(f"   {i:2d}. {subj}")
    print("\n" + "="*70)


def verify_downloads() -> dict:
    """Verify which subjects have been downloaded."""
    status = {}
    for subject_id in SUBJECTS:
        subject_dir = DATA_DIR / subject_id
        if not subject_dir.exists():
            status[subject_id] = "missing"
            continue
        
        # Check for expected files
        rest_files = list(subject_dir.glob("*rfMRI_REST*.dtseries.nii"))
        lang_files = list(subject_dir.glob("*tfMRI_LANGUAGE*.dtseries.nii"))
        
        if len(rest_files) >= 2 and len(lang_files) >= 2:
            status[subject_id] = "complete"
        elif len(rest_files) > 0 or len(lang_files) > 0:
            status[subject_id] = "partial"
        else:
            status[subject_id] = "empty"
    
    return status


def main():
    parser = argparse.ArgumentParser(description="Download HCP fMRI data")
    parser.add_argument(
        "--method",
        choices=["aws", "manual", "verify"],
        default="verify",
        help="Download method: aws (S3), manual (instructions), verify (check status)"
    )
    parser.add_argument(
        "--subjects",
        nargs="+",
        default=SUBJECTS,
        help="Subject IDs to download (default: first 10)"
    )
    
    args = parser.parse_args()
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    if args.method == "verify":
        print("\nVerifying downloads...")
        status = verify_downloads()
        print("\nDownload Status:")
        print("-" * 40)
        for subj, stat in status.items():
            symbol = "✓" if stat == "complete" else "○" if stat == "partial" else "✗"
            print(f"  {symbol} {subj}: {stat}")
        
        complete = sum(1 for s in status.values() if s == "complete")
        print(f"\nComplete: {complete}/{len(SUBJECTS)}")
        
    elif args.method == "aws":
        if not check_aws_cli():
            sys.exit(1)
        
        print(f"\nDownloading {len(args.subjects)} subjects from AWS S3...")
        print(f"Target directory: {DATA_DIR}")
        
        success_count = 0
        for subject_id in args.subjects:
            if download_subject_aws(subject_id):
                success_count += 1
        
        print(f"\n{'='*70}")
        print(f"Download complete: {success_count}/{len(args.subjects)} subjects")
        print(f"{'='*70}")
        
    elif args.method == "manual":
        print_manual_instructions()


if __name__ == "__main__":
    main()

