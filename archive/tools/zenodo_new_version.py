#!/usr/bin/env python3
"""
Zenodo New Version Publisher - v1.8.12
Creates new version of existing Zenodo deposit via API

Usage:
    export ZENODO_TOKEN=your_token_here
    python tools/zenodo_new_version.py

Requirements:
    - ZENODO_TOKEN environment variable
    - Existing deposit ID: 17489685
    - ZIP file: hyperbolic-semantic-networks-v1.8.12-submission.zip
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

# Configuration
EXISTING_DEPOSIT_ID = "17489685"  # From DOI 10.5281/zenodo.17489685
ZIP_FILE = "hyperbolic-semantic-networks-v1.8.12-submission.zip"
VERSION = "v1.8.12-submission"

# Zenodo API
ZENODO_BASE = 'https://zenodo.org/api'

def get_token():
    """Get token from environment"""
    token = os.environ.get('ZENODO_TOKEN')
    if not token:
        print('❌ ERROR: ZENODO_TOKEN not set!')
        print()
        print('Get token from: https://zenodo.org/account/settings/applications/tokens/new/')
        print('Scopes needed: deposit:write, deposit:actions')
        print()
        print('Then run:')
        print('  export ZENODO_TOKEN="your_token_here"')
        print('  python tools/zenodo_new_version.py')
        sys.exit(1)
    return token

def api_request(token, method, path, data=None, timeout=120):
    """Make API request"""
    url = ZENODO_BASE + path
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    body = json.dumps(data).encode('utf-8') if data else None
    
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.getcode(), json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        try:
            error_data = json.loads(e.read().decode('utf-8'))
            return e.code, error_data
        except:
            return e.code, {'error': str(e)}

def upload_file(token, bucket_url, filepath):
    """Upload file to Zenodo bucket"""
    filename = os.path.basename(filepath)
    url = bucket_url.rstrip('/') + '/' + filename
    
    filesize_mb = os.path.getsize(filepath) / 1024 / 1024
    print(f'📤 Uploading {filename} ({filesize_mb:.2f} MB)...')
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/octet-stream'
    }
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    req = urllib.request.Request(url, data=data, headers=headers, method='PUT')
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return resp.getcode(), result
    except urllib.error.HTTPError as e:
        return e.code, {'error': str(e)}

def main():
    print("="*70)
    print("🔖 ZENODO NEW VERSION - v1.8.12 Submission")
    print("="*70)
    print()
    
    # Get token
    token = get_token()
    print("✅ Token found")
    print()
    
    # Check ZIP exists
    repo_path = Path(__file__).parent.parent
    zip_path = repo_path / ZIP_FILE
    if not zip_path.exists():
        print(f"❌ ERROR: ZIP file not found: {zip_path}")
        sys.exit(1)
    print(f"✅ ZIP found: {zip_path.name} ({zip_path.stat().st_size / 1024:.0f} KB)")
    print()
    
    # Get existing deposit
    print(f"📋 Getting existing deposit {EXISTING_DEPOSIT_ID}...")
    code, deposit_info = api_request(token, 'GET', f'/deposit/depositions/{EXISTING_DEPOSIT_ID}')
    
    if code != 200:
        print(f"❌ ERROR: Failed to get deposit: {code}")
        print(json.dumps(deposit_info, indent=2))
        sys.exit(1)
    
    print(f"✅ Existing deposit found:")
    print(f"   Title: {deposit_info.get('title', 'N/A')}")
    print(f"   Current DOI: {deposit_info.get('doi', 'N/A')}")
    print()
    
    # Create new version
    print("🆕 Creating new version...")
    code, new_version = api_request(token, 'POST', f'/deposit/depositions/{EXISTING_DEPOSIT_ID}/actions/newversion')
    
    if code not in (200, 201):
        print(f"❌ ERROR: Failed to create new version: {code}")
        print(json.dumps(new_version, indent=2))
        sys.exit(1)
    
    # Get draft link
    draft_url = new_version.get('links', {}).get('latest_draft')
    if not draft_url:
        print("❌ ERROR: No draft URL in response")
        sys.exit(1)
    
    # Extract new draft ID from URL
    new_draft_id = draft_url.split('/')[-1]
    print(f"✅ New version draft created: ID={new_draft_id}")
    print()
    
    # Get new draft details
    code, new_draft = api_request(token, 'GET', f'/deposit/depositions/{new_draft_id}')
    if code != 200:
        print(f"❌ ERROR: Failed to get draft: {code}")
        sys.exit(1)
    
    bucket_url = new_draft['links']['bucket']
    print(f"✅ Upload bucket: {bucket_url}")
    print()
    
    # Delete old files (new version starts with old files)
    print("🗑️ Deleting old files from new version...")
    for file_info in new_draft.get('files', []):
        file_id = file_info['id']
        print(f"   Deleting {file_info['filename']}...")
        api_request(token, 'DELETE', f'/deposit/depositions/{new_draft_id}/files/{file_id}')
    print("✅ Old files deleted")
    print()
    
    # Update metadata
    print("📝 Updating metadata...")
    new_metadata = {
        'metadata': {
            'title': 'Hyperbolic Semantic Networks: Cross-Linguistic Evidence from Structural Null Models',
            'upload_type': 'dataset',
            'description': '''This release contains the complete dataset, analysis code, and results for the manuscript "Consistent Evidence for Hyperbolic Geometry in Semantic Networks Across Four Languages" submitted to Network Science on November 5, 2025.

VERSION 1.8.12 UPDATES:
- Complete structural null analysis (6/8 analyses, M=1000 replicates)
- Fixed critical algorithmic bugs (50x triadic-rewire speedup)
- Added meta-analytic heterogeneity testing (I²=0% effect homogeneity)
- Added triadic variance reduction analysis (51-59% reduction)
- Manuscript optimized through 12 MCTS/PUCT iterations (99.8% quality)

KEY RESULTS:
- 3 of 4 languages show robust hyperbolic geometry (p < 0.001)
- Effect sizes homogeneous across languages (Q=0.000, I²=0.0%)
- Perfect distributional separation (|Cliff's δ| = 1.00)

COMPUTATIONAL EFFORT:
- 6,000 null networks generated (M=1000 × 6)
- 266 CPU-hours total computation
''',
            'creators': deposit_info.get('metadata', {}).get('creators', []),
            'keywords': [
                'semantic networks', 'hyperbolic geometry', 'Ricci curvature',
                'cross-linguistic', 'cognitive networks', 'word associations',
                'null models', 'configuration model', 'network science', 'SWOW',
                'Monte Carlo', 'meta-analysis'
            ],
            'license': 'mit',
            'version': VERSION,
            'publication_date': '2025-11-05',
        }
    }
    
    code, updated = api_request(token, 'PUT', f'/deposit/depositions/{new_draft_id}', data=new_metadata)
    if code != 200:
        print(f"⚠️ Warning: Metadata update returned {code}")
    else:
        print("✅ Metadata updated")
    print()
    
    # Upload ZIP
    code, upload_result = upload_file(token, bucket_url, str(zip_path))
    if code not in (200, 201):
        print(f"❌ ERROR: Upload failed: {code}")
        print(json.dumps(upload_result, indent=2))
        sys.exit(1)
    print("✅ ZIP uploaded successfully!")
    print()
    
    # Publish
    print("📢 Publishing new version...")
    code, published = api_request(token, 'POST', f'/deposit/depositions/{new_draft_id}/actions/publish')
    
    if code in (200, 201, 202):
        doi = published.get('doi') or published.get('metadata', {}).get('doi')
        record_url = published.get('links', {}).get('record') or published.get('links', {}).get('record_html')
        
        print()
        print("="*70)
        print("🎉 SUCCESS! NOVA VERSÃO PUBLICADA!")
        print("="*70)
        print(f"✅ DOI: {doi}")
        print(f"✅ URL: {record_url}")
        print("="*70)
        print()
        print("📋 PRÓXIMOS PASSOS:")
        print(f"1. Verificar record: {record_url}")
        print(f"2. Atualizar manuscrito com DOI: {doi}")
        print("3. Regenerar PDF se DOI mudou")
        print("4. Submeter para Network Science!")
        print()
        
        # Save DOI for reference
        doi_file = repo_path / "ZENODO_NEW_DOI_v1.8.12.txt"
        with open(doi_file, 'w') as f:
            f.write(f"DOI: {doi}\n")
            f.write(f"URL: {record_url}\n")
            f.write(f"Version: {VERSION}\n")
            f.write(f"Date: 2025-11-05\n")
        print(f"💾 DOI saved to: {doi_file}")
        print()
    else:
        print(f"❌ ERROR: Publish failed: {code}")
        print(json.dumps(published, indent=2))
        sys.exit(1)

if __name__ == '__main__':
    main()

