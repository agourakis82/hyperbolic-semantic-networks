# Zenodo Release Instructions

## Version 0.1.0 Release

### Step 1: Verify Release Files

```bash
# Check all files are present
cd /home/agourakis82/workspace/hyperbolic-semantic-networks
find . -type f -not -path './.git/*' | wc -l
# Should show ~250 files
```

### Step 2: Create Release Archive

```bash
# Create zip archive
cd ..
zip -r hyperbolic-semantic-networks-v0.1.0.zip hyperbolic-semantic-networks/ \
    -x "*.git*" -x "*/target/*" -x "*/__pycache__/*" -x "*/.julia/*"
```

### Step 3: Upload to Zenodo

1. Go to https://zenodo.org/deposit/new
2. Upload the zip file
3. Fill in metadata from `.zenodo.json`:
   - Title: "Hyperbolic Semantic Networks: Julia/Rust Implementation"
   - Description: (from .zenodo.json)
   - Authors: Demetrios C. Agourakis
   - ORCID: 0000-0002-8596-5097
   - Version: 0.1.0
   - License: MIT
   - Keywords: (from .zenodo.json)
4. Publish

### Step 4: Update Repository with DOI

After Zenodo assigns DOI:
1. Add DOI to README.md
2. Add DOI to .zenodo.json
3. Add DOI to docs/RELEASE_NOTES.md
4. Commit and push

### Step 5: GitHub Release

1. Go to repository on GitHub
2. Create new release
3. Tag: v0.1.0
4. Title: "Release v0.1.0"
5. Description: (from docs/RELEASE_NOTES.md)
6. Attach Zenodo DOI
7. Publish

## Metadata Summary

**Title**: Hyperbolic Semantic Networks: Julia/Rust Implementation  
**Version**: 0.1.0  
**Authors**: Demetrios C. Agourakis (ORCID: 0000-0002-8596-5097)  
**License**: MIT  
**Upload Type**: Software  
**Access Right**: Open

**Description**: High-performance implementation of Ollivier-Ricci curvature analysis for semantic networks, enabling identification of hyperbolic geometry boundary conditions. This implementation provides 10-100x performance improvements over Python through Julia/Rust FFI integration.

**Keywords**: semantic networks, hyperbolic geometry, Ollivier-Ricci curvature, network science, Julia, Rust, computational geometry, natural language processing, complex networks

