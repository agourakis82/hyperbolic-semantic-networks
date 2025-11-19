#!/bin/bash
# Push release to remote repository

set -e

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$REPO_ROOT"

VERSION="0.1.0"
TAG="v${VERSION}"

echo "=" | head -c 80
echo ""
echo "PUSHING RELEASE v${VERSION}"
echo "=" | head -c 80
echo ""

# Check if tag exists
if ! git rev-parse "$TAG" >/dev/null 2>&1; then
    echo "Creating tag $TAG..."
    git tag -a "$TAG" -m "Release v${VERSION}: Initial Julia/Rust implementation"
fi

# Push main branch
echo "Pushing main branch..."
git push origin main || {
    echo "⚠️  Push failed. Checking for large files..."
    exit 1
}

# Push tag
echo "Pushing tag $TAG..."
git push origin "$TAG" || {
    echo "⚠️  Tag push failed"
    exit 1
}

echo ""
echo "✅ Release pushed successfully!"
echo "   - Branch: main"
echo "   - Tag: $TAG"
echo ""
echo "Next steps:"
echo "  1. Create Zenodo release (see scripts/create_zenodo_release.md)"
echo "  2. Create GitHub release with Zenodo DOI"
echo ""
