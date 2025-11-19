#!/bin/bash
# Remove large files from git history using git filter-branch

set -e

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$REPO_ROOT"

echo "⚠️  WARNING: This will rewrite git history!"
echo "Make sure you have a backup first."
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

# Files to remove from history
LARGE_FILES=(
    "data/raw/conceptnet/conceptnet-assertions-5.7.0.csv.gz"
    "data/raw/SWOW-EN.complete.20180827.csv"
    "data/raw/SWOW-EN.R100.20180827.csv"
    "data/raw/SWOWRP.raw.20220426.csv"
    "data/raw/SWOWRP.spellchecked.20220426.csv"
    "data/external/geco/*.xlsx"
)

# Build filter command
FILTER_CMD="git rm --cached --ignore-unmatch"

for file in "${LARGE_FILES[@]}"; do
    FILTER_CMD="$FILTER_CMD '$file'"
done

echo "Removing large files from history..."
echo "This may take a while..."

# Use filter-branch
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch \
    --force \
    --index-filter "$FILTER_CMD" \
    --prune-empty \
    --tag-name-filter cat \
    -- --all

echo ""
echo "✅ Large files removed from history"
echo ""
echo "Next steps:"
echo "  1. Force push: git push origin --all --force"
echo "  2. Force push tags: git push origin --tags --force"
echo ""
echo "⚠️  WARNING: This rewrites history. Make sure all collaborators"
echo "   are aware before force pushing!"

