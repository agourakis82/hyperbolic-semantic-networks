# Zenodo API Publishing Guide

**Date**: 2025-11-08

## Overview

This guide explains how to publish releases to Zenodo using the API automatically.

## Prerequisites

### 1. Get Zenodo Access Token

1. Go to: https://zenodo.org/account/settings/applications/tokens/new/
2. Log in with your Zenodo account
3. Create a new token with scopes:
   - `deposit:write` - Create and edit deposits
   - `deposit:actions` - Publish deposits
4. Copy the token (you'll only see it once!)

### 2. Install Python Dependencies

```bash
pip3 install requests --user
# or
pip install requests
```

## Usage

### Option 1: Using Environment Variable (Recommended)

```bash
# Set token
export ZENODO_ACCESS_TOKEN='your_token_here'

# Publish to production
python3 scripts/zenodo_publish.py

# Or use wrapper script
./scripts/zenodo_publish.sh
```

### Option 2: Pass Token as Argument

```bash
python3 scripts/zenodo_publish.py --token YOUR_TOKEN
```

### Option 3: Test with Sandbox

```bash
# Use sandbox for testing (doesn't create real DOI)
python3 scripts/zenodo_publish.py --token YOUR_TOKEN --sandbox
```

## Script Options

```bash
python3 scripts/zenodo_publish.py [OPTIONS]

Options:
  --token TOKEN       Zenodo access token
  --sandbox          Use Zenodo sandbox (for testing)
  --skip-upload      Skip file upload (metadata only)
  --version VERSION  Version number (default: 0.1.0)
```

## What the Script Does

1. **Loads Metadata**: Reads `.zenodo.json` for release information
2. **Creates Archive**: Builds zip file excluding large files
3. **Creates Deposition**: Creates new Zenodo deposit
4. **Uploads File**: Uploads release archive
5. **Publishes**: Publishes deposit and gets DOI
6. **Saves DOI**: Writes DOI to `ZENODO_DOI.txt`

## Example Workflow

```bash
# 1. Set token
export ZENODO_ACCESS_TOKEN='your_token_here'

# 2. Test with sandbox first (optional)
python3 scripts/zenodo_publish.py --sandbox

# 3. Publish to production
python3 scripts/zenodo_publish.py

# 4. Check results
cat ZENODO_DOI.txt

# 5. Update repository with DOI
# Edit .zenodo.json, README.md, docs/RELEASE_NOTES.md
git add .
git commit -m "docs: Add Zenodo DOI"
git push origin main
```

## Files Excluded from Archive

The script automatically excludes:
- `.git/` directories
- `target/` (Rust build artifacts)
- `__pycache__/` (Python cache)
- `.julia/` (Julia packages)
- Large data files:
  - `data/raw/conceptnet/*`
  - `data/raw/*.csv.gz`
  - `data/raw/SWOW-ZH24/*`
  - `data/raw/*.csv` (>100MB)
  - `*.xlsx` files

## Troubleshooting

### Token Issues

**Error**: "Zenodo access token required"
- **Solution**: Set `ZENODO_ACCESS_TOKEN` environment variable or use `--token`

**Error**: "401 Unauthorized"
- **Solution**: Check token is valid and has correct scopes

### Upload Issues

**Error**: "File too large"
- **Solution**: Large files are automatically excluded. If issue persists, use `--skip-upload` and upload manually

**Error**: "Connection timeout"
- **Solution**: Retry the command. Zenodo API may be slow during peak times

### Metadata Issues

**Error**: "Invalid metadata"
- **Solution**: Check `.zenodo.json` is valid JSON and has required fields

## After Publishing

1. **Save DOI**: DOI is saved to `ZENODO_DOI.txt`
2. **Update Repository**:
   ```bash
   # Update .zenodo.json
   # Update README.md
   # Update docs/RELEASE_NOTES.md
   git add .
   git commit -m "docs: Add Zenodo DOI"
   git push origin main
   ```
3. **Create GitHub Release**: Link to Zenodo DOI

## Sandbox vs Production

- **Sandbox**: https://sandbox.zenodo.org
  - For testing
  - Doesn't create permanent DOI
  - Use `--sandbox` flag

- **Production**: https://zenodo.org
  - Real releases
  - Permanent DOI
  - Default behavior

## Security Notes

- **Never commit tokens to git**
- Use environment variables or pass as arguments
- Tokens are sensitive - treat like passwords
- Revoke old tokens if compromised

---

**Status**: Ready for use  
**See also**: `scripts/create_zenodo_release.md` for manual instructions

