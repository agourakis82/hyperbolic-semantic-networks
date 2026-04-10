#!/usr/bin/env python3
"""
Publish release to Zenodo using API.

Requires:
- ZENODO_ACCESS_TOKEN environment variable
- Or pass token via --token argument

Usage:
    python scripts/zenodo_publish.py --token YOUR_TOKEN
    python scripts/zenodo_publish.py  # Uses ZENODO_ACCESS_TOKEN env var
"""

import argparse
import json
import os
import sys
import time
import zipfile
from pathlib import Path
from typing import Dict, Optional

import requests

# Zenodo API endpoints
ZENODO_SANDBOX_URL = "https://sandbox.zenodo.org/api"
ZENODO_PRODUCTION_URL = "https://zenodo.org/api"


def get_token_from_file() -> Optional[str]:
    """Try to load token from common locations."""
    token_locations = [
        Path.home() / ".zenodo_token",
        Path("/home/agourakis82/.zenodo_token"),
        Path(".zenodo_token"),
    ]
    
    for token_file in token_locations:
        if token_file.exists():
            try:
                token = token_file.read_text().strip()
                if len(token) > 20:
                    return token
            except Exception:
                pass
    
    return None


def load_zenodo_metadata(repo_root: Path) -> Dict:
    """Load metadata from .zenodo.json."""
    zenodo_file = repo_root / ".zenodo.json"
    if not zenodo_file.exists():
        raise FileNotFoundError(f".zenodo.json not found at {zenodo_file}")
    
    with open(zenodo_file, 'r') as f:
        return json.load(f)


def should_exclude_file(file_path: Path, repo_root: Path) -> bool:
    """Check if file should be excluded from archive."""
    rel_path = str(file_path.relative_to(repo_root))
    
    # Exclude patterns
    exclude_patterns = [
        '.git',
        'target/',
        '__pycache__',
        '.julia/',
        'data/raw/conceptnet/',
        'data/raw/SWOW-ZH24/',
        'release_archives/',
        'ZENODO_DOI.txt',
    ]
    
    # Check patterns
    for pattern in exclude_patterns:
        if pattern in rel_path:
            return True
    
    # Exclude large files
    if file_path.stat().st_size > 100 * 1024 * 1024:  # 100MB
        return True
    
    # Exclude specific extensions
    exclude_extensions = ['.csv.gz', '.xlsx', '.zip']
    if any(rel_path.endswith(ext) for ext in exclude_extensions):
        return True
    
    return False


def create_release_archive(repo_root: Path, output_path: Path) -> Path:
    """Create release archive excluding large files."""
    print(f"Creating release archive: {output_path}")
    
    if output_path.exists():
        output_path.unlink()
    
    total_files = 0
    excluded_files = 0
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(repo_root):
            # Skip .git and other excluded directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'target', '__pycache__', '.julia', 'release_archives']]
            
            for file in files:
                file_path = Path(root) / file
                
                if should_exclude_file(file_path, repo_root):
                    excluded_files += 1
                    continue
                
                rel_path = file_path.relative_to(repo_root)
                zipf.write(file_path, rel_path)
                total_files += 1
    
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"✅ Archive created: {size_mb:.1f} MB")
    print(f"   Files included: {total_files}")
    print(f"   Files excluded: {excluded_files}")
    return output_path


def create_deposition(
    api_url: str,
    token: str,
    metadata: Dict
) -> Dict:
    """Create a new deposition on Zenodo."""
    print(f"Creating deposition on Zenodo ({api_url})...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Create empty deposition
    response = requests.post(
        f"{api_url}/deposit/depositions",
        headers=headers,
        json={},
        params={"access_token": token}
    )
    
    if response.status_code != 201:
        raise Exception(f"Failed to create deposition: {response.status_code} - {response.text}")
    
    deposition = response.json()
    deposition_id = deposition['id']
    print(f"✅ Deposition created: {deposition_id}")
    
    # Update with metadata
    print("Updating metadata...")
    response = requests.put(
        f"{api_url}/deposit/depositions/{deposition_id}",
        headers=headers,
        json={"metadata": metadata},
        params={"access_token": token}
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to update metadata: {response.status_code} - {response.text}")
    
    print("✅ Metadata updated")
    return deposition


def upload_file(
    api_url: str,
    token: str,
    deposition_id: int,
    file_path: Path
) -> None:
    """Upload file to Zenodo deposition."""
    file_size_mb = file_path.stat().st_size / (1024*1024)
    print(f"Uploading file: {file_path.name} ({file_size_mb:.1f} MB)...")
    
    # Get upload URL
    headers = {
        "Authorization": f"Bearer {token}",
    }
    
    response = requests.get(
        f"{api_url}/deposit/depositions/{deposition_id}",
        headers=headers,
        params={"access_token": token}
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to get deposition: {response.status_code} - {response.text}")
    
    deposition = response.json()
    bucket_url = deposition['links']['bucket']
    
    # Upload file to bucket
    print(f"  Uploading to: {bucket_url}/{file_path.name}")
    with open(file_path, 'rb') as f:
        response = requests.put(
            f"{bucket_url}/{file_path.name}",
            headers={"Authorization": f"Bearer {token}"},
            data=f
        )
    
    if response.status_code not in (200, 201):
        raise Exception(f"Failed to upload file: {response.status_code} - {response.text}")
    
    print("✅ File uploaded successfully")


def publish_deposition(
    api_url: str,
    token: str,
    deposition_id: int
) -> Dict:
    """Publish the deposition."""
    print("Publishing deposition...")
    
    headers = {
        "Authorization": f"Bearer {token}",
    }
    
    response = requests.post(
        f"{api_url}/deposit/depositions/{deposition_id}/actions/publish",
        headers=headers,
        params={"access_token": token}
    )
    
    if response.status_code != 202:
        raise Exception(f"Failed to publish: {response.status_code} - {response.text}")
    
    published = response.json()
    doi = published.get('doi', published.get('metadata', {}).get('doi', 'N/A'))
    record_url = published.get('links', {}).get('html', published.get('record_url', 'N/A'))
    
    print(f"✅ Published successfully!")
    print(f"   DOI: {doi}")
    print(f"   URL: {record_url}")
    
    return published


def main():
    parser = argparse.ArgumentParser(description="Publish release to Zenodo")
    parser.add_argument(
        "--token",
        help="Zenodo access token (or set ZENODO_ACCESS_TOKEN env var)",
        default=os.getenv("ZENODO_ACCESS_TOKEN")
    )
    parser.add_argument(
        "--sandbox",
        action="store_true",
        help="Use Zenodo sandbox (for testing)"
    )
    parser.add_argument(
        "--skip-upload",
        action="store_true",
        help="Skip file upload (metadata only)"
    )
    parser.add_argument(
        "--version",
        default="0.1.0",
        help="Version number (default: 0.1.0)"
    )
    
    args = parser.parse_args()
    
    # Try to get token from various sources
    if not args.token:
        # Try environment variable
        args.token = os.getenv("ZENODO_ACCESS_TOKEN")
        
        # Try file
        if not args.token:
            args.token = get_token_from_file()
            if args.token:
                print(f"✅ Token loaded from file: ~/.zenodo_token")
    
    if not args.token:
        print("❌ Error: Zenodo access token required")
        print("   Set ZENODO_ACCESS_TOKEN environment variable or use --token")
        print("   Or save token to: ~/.zenodo_token")
        sys.exit(1)
    
    # Determine API URL
    api_url = ZENODO_SANDBOX_URL if args.sandbox else ZENODO_PRODUCTION_URL
    if args.sandbox:
        print("⚠️  Using Zenodo SANDBOX (for testing)")
    else:
        print("🌐 Using Zenodo PRODUCTION")
    
    # Get repository root
    repo_root = Path(__file__).parent.parent
    os.chdir(repo_root)
    
    # Load metadata
    print("\n📋 Loading metadata...")
    metadata = load_zenodo_metadata(repo_root)
    metadata['version'] = args.version
    
    print(f"   Title: {metadata['title']}")
    print(f"   Version: {metadata['version']}")
    
    # Create archive
    if not args.skip_upload:
        archive_dir = repo_root / "release_archives"
        archive_dir.mkdir(exist_ok=True)
        archive_path = archive_dir / f"hyperbolic-semantic-networks-v{args.version}.zip"
        
        print(f"\n📦 Creating release archive...")
        create_release_archive(repo_root, archive_path)
    else:
        archive_path = None
    
    # Create deposition
    print(f"\n🔷 Creating Zenodo deposition...")
    deposition = create_deposition(api_url, args.token, metadata)
    deposition_id = deposition['id']
    
    # Upload file
    if archive_path and not args.skip_upload:
        print(f"\n📤 Uploading archive...")
        upload_file(api_url, args.token, deposition_id, archive_path)
    
    # Publish
    print(f"\n🚀 Publishing...")
    published = publish_deposition(api_url, args.token, deposition_id)
    
    # Extract DOI and URL
    doi = published.get('doi', published.get('metadata', {}).get('doi', ''))
    record_url = published.get('links', {}).get('html', published.get('record_url', ''))
    
    # Print results
    print("\n" + "=" * 80)
    print("✅ RELEASE PUBLISHED SUCCESSFULLY!")
    print("=" * 80)
    print(f"\nDOI: {doi}")
    print(f"URL: {record_url}")
    print(f"Deposition ID: {deposition_id}")
    
    if archive_path:
        print(f"\nArchive: {archive_path}")
        print(f"Archive size: {archive_path.stat().st_size / (1024*1024):.1f} MB")
    
    # Save DOI to file
    doi_file = repo_root / "ZENODO_DOI.txt"
    with open(doi_file, 'w') as f:
        f.write(f"DOI: {doi}\n")
        f.write(f"URL: {record_url}\n")
        f.write(f"Deposition ID: {deposition_id}\n")
        f.write(f"Version: {args.version}\n")
        f.write(f"Published: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"\n✅ DOI saved to: {doi_file}")
    print("\n📋 Next steps:")
    print("  1. Update .zenodo.json with DOI")
    print("  2. Update README.md with DOI")
    print("  3. Create GitHub release with Zenodo DOI")
    print("  4. Commit and push updates")


if __name__ == "__main__":
    main()

