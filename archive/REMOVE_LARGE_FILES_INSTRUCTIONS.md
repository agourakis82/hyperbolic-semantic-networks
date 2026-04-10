# Instructions: Removing Large Files from Git History

**Problem**: Large files (>100MB) exist in git history, blocking push to GitHub.

**Solution**: Remove large files from git history using git filter-branch.

## Option 1: Use git filter-branch (Manual)

```bash
# 1. Backup repository first!
cp -r /home/agourakis82/workspace/hyperbolic-semantic-networks /tmp/hyperbolic-semantic-networks-backup

# 2. Remove large files from history
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch \
    --force \
    --index-filter 'git rm --cached --ignore-unmatch data/raw/conceptnet/conceptnet-assertions-5.7.0.csv.gz data/raw/SWOW-EN.complete.20180827.csv data/raw/SWOW-EN.R100.20180827.csv data/raw/SWOWRP.raw.20220426.csv data/raw/SWOWRP.spellchecked.20220426.csv' \
    --prune-empty \
    --tag-name-filter cat \
    -- --all

# 3. Clean up
git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. Force push
git push origin --all --force
git push origin --tags --force
```

## Option 2: Use BFG Repo-Cleaner (Recommended)

BFG is faster and safer than filter-branch:

```bash
# 1. Install BFG (if not installed)
# Download from: https://rtyley.github.io/bfg-repo-cleaner/

# 2. Clone a fresh copy (mirror)
cd /tmp
git clone --mirror https://github.com/agourakis82/hyperbolic-semantic-networks.git

# 3. Remove large files
java -jar bfg.jar --strip-blobs-bigger-than 100M hyperbolic-semantic-networks.git

# 4. Clean up
cd hyperbolic-semantic-networks.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. Push
git push
```

## Option 3: Start Fresh Branch (Simplest)

If history rewriting is too complex:

```bash
# 1. Create orphan branch (no history)
git checkout --orphan release-v0.1.0

# 2. Add all current files
git add -A
git commit -m "Release v0.1.0: Initial Julia/Rust implementation (fresh branch, no large files)"

# 3. Delete old main branch
git branch -D main

# 4. Rename new branch to main
git branch -m main

# 5. Force push
git push origin main --force
```

## Recommended: Option 3 (Start Fresh)

For a new release with clean history:

```bash
cd /home/agourakis82/workspace/hyperbolic-semantic-networks

# Create fresh branch
git checkout --orphan clean-main
git add -A
git commit -m "Release v0.1.0: Initial Julia/Rust implementation

- Complete FFI integration (Julia ↔ Rust)
- Ollivater-Ricci curvature computation
- Null models, bootstrap, Ricci flow
- Comprehensive test suite (70%+ coverage)
- Validated against Q1 SOTA literature
- Performance: 10-100x speedup over Python
- Full documentation and examples

Large data files excluded (available via Zenodo)"

# Switch to clean branch
git branch -D main
git branch -m main

# Push
git push origin main --force
git push origin v0.1.0 --force
```

## After Push

1. Create Zenodo release with large data files
2. Create GitHub release linking to Zenodo DOI
3. Update documentation with data download instructions

---

**Current Status**: Ready for history cleanup and push
