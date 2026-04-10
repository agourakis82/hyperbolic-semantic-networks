#!/usr/bin/env python3
"""
Publish hyperbolic-semantic-networks to Zenodo via API
Creates deposition, uploads tarball, publishes with DOI.

Usage:
    export ZENODO_TOKEN=your_token_here
    python tools/zenodo_publish.py [--sandbox]
"""

import os
import sys
import json
import urllib.request
import urllib.error
import tarfile
import tempfile
from pathlib import Path

# Zenodo API base URLs
PRODUCTION_BASE = 'https://zenodo.org/api'
SANDBOX_BASE = 'https://sandbox.zenodo.org/api'

def get_base_url(sandbox=False):
    return SANDBOX_BASE if sandbox else PRODUCTION_BASE

def get_token():
    token = os.environ.get('ZENODO_TOKEN')
    if not token:
        print('❌ ERROR: ZENODO_TOKEN not set in environment', file=sys.stderr)
        print('Get token from: https://zenodo.org/account/settings/applications/tokens/new/', file=sys.stderr)
        sys.exit(1)
    return token

def req(base, token, method, path, data=None, timeout=120):
    """Make API request to Zenodo"""
    url = base + path
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    body = None
    if data is not None:
        body = json.dumps(data).encode('utf-8')
    
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            payload = resp.read()
            return resp.getcode(), json.loads(payload.decode('utf-8'))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode('utf-8'))
        except:
            return e.code, {'error': str(e)}

def upload_file(base, token, bucket_url, filepath):
    """Upload file to Zenodo bucket"""
    filename = os.path.basename(filepath)
    url = bucket_url.rstrip('/') + '/' + filename
    
    print(f'📤 Uploading {filename} ({os.path.getsize(filepath) / 1024 / 1024:.2f} MB)...')
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/octet-stream'
    }
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    r = urllib.request.Request(url, data=data, headers=headers, method='PUT')
    with urllib.request.urlopen(r, timeout=600) as resp:
        payload = resp.read()
        return resp.getcode(), json.loads(payload.decode('utf-8'))

def create_tarball(repo_path):
    """Create tarball of repository (excluding .git)"""
    print('📦 Creating tarball...')
    
    # Create temp tarball
    temp_dir = tempfile.mkdtemp()
    tarball_path = os.path.join(temp_dir, 'hyperbolic-semantic-networks-v1.0.0.tar.gz')
    
    with tarfile.open(tarball_path, 'w:gz') as tar:
        # Add all files except .git
        for root, dirs, files in os.walk(repo_path):
            # Skip .git directory
            if '.git' in root:
                continue
            
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, repo_path)
                tar.add(filepath, arcname=arcname)
                
    print(f'✅ Tarball created: {tarball_path} ({os.path.getsize(tarball_path) / 1024 / 1024:.2f} MB)')
    return tarball_path

def load_metadata(repo_path):
    """Load .zenodo.json metadata"""
    zenodo_json = os.path.join(repo_path, '.zenodo.json')
    if not os.path.exists(zenodo_json):
        print(f'❌ ERROR: .zenodo.json not found at {zenodo_json}', file=sys.stderr)
        sys.exit(1)
    
    with open(zenodo_json, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    sandbox = '--sandbox' in sys.argv
    base = get_base_url(sandbox)
    token = get_token()
    
    print('='*60)
    print('🚀 ZENODO PUBLISH - Hyperbolic Semantic Networks')
    print('='*60)
    print(f'Environment: {"SANDBOX" if sandbox else "PRODUCTION"}')
    print(f'API Base: {base}')
    print('='*60)
    print()
    
    # Get repo path
    script_dir = Path(__file__).parent.parent
    repo_path = str(script_dir.resolve())
    print(f'📂 Repository: {repo_path}')
    print()
    
    # Load metadata
    print('📋 Loading metadata from .zenodo.json...')
    metadata = load_metadata(repo_path)
    print(f'✅ Title: {metadata.get("title")}')
    print(f'✅ Version: {metadata.get("version")}')
    print()
    
    # Create tarball
    tarball_path = create_tarball(repo_path)
    print()
    
    # Create deposition
    print('🆕 Creating new deposition...')
    code, deposition = req(base, token, 'POST', '/deposit/depositions', data={'metadata': metadata})
    
    if code not in (200, 201):
        print(f'❌ ERROR: Failed to create deposition: {code}')
        print(json.dumps(deposition, indent=2))
        sys.exit(1)
    
    dep_id = deposition['id']
    bucket_url = deposition['links']['bucket']
    print(f'✅ Deposition created: ID={dep_id}')
    print(f'✅ Bucket URL: {bucket_url}')
    print()
    
    # Upload tarball
    try:
        code, upload_result = upload_file(base, token, bucket_url, tarball_path)
        if code in (200, 201):
            print(f'✅ File uploaded successfully!')
        else:
            print(f'❌ ERROR: Upload failed: {code}')
            print(json.dumps(upload_result, indent=2))
            sys.exit(1)
    except Exception as e:
        print(f'❌ ERROR: Upload exception: {e}')
        sys.exit(1)
    finally:
        # Clean up tarball
        os.remove(tarball_path)
        os.rmdir(os.path.dirname(tarball_path))
    
    print()
    
    # Publish
    print('📢 Publishing deposition...')
    code, published = req(base, token, 'POST', f'/deposit/depositions/{dep_id}/actions/publish')
    
    if code in (200, 201, 202):
        doi = published.get('doi') or published.get('metadata', {}).get('doi')
        record_url = published.get('links', {}).get('html') or published.get('links', {}).get('latest_html')
        
        print()
        print('='*60)
        print('🎉 SUCCESS!')
        print('='*60)
        print(f'✅ DOI: {doi}')
        print(f'✅ Record: {record_url}')
        print('='*60)
        print()
        print('Next steps:')
        print(f'1. Verify record: {record_url}')
        print('2. Update README.md with DOI badge')
        print('3. Update CITATION.cff with DOI')
        print()
    else:
        print(f'❌ ERROR: Publish failed: {code}')
        print(json.dumps(published, indent=2))
        sys.exit(1)

if __name__ == '__main__':
    main()

