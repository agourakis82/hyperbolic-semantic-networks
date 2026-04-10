#!/bin/bash
# Wrapper script for Zenodo publishing

set -e

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$REPO_ROOT"

# Check for token
if [ -z "$ZENODO_ACCESS_TOKEN" ]; then
    echo "⚠️  ZENODO_ACCESS_TOKEN not set"
    echo ""
    echo "To get a token:"
    echo "  1. Go to https://zenodo.org/account/settings/applications/tokens/new/"
    echo "  2. Create a new token with 'deposit:write' and 'deposit:actions' scopes"
    echo "  3. Set environment variable:"
    echo "     export ZENODO_ACCESS_TOKEN='your_token_here'"
    echo ""
    read -p "Enter Zenodo access token (or press Ctrl+C to cancel): " token
    export ZENODO_ACCESS_TOKEN="$token"
fi

# Check if requests is installed
if ! python3 -c "import requests" 2>/dev/null; then
    echo "Installing requests..."
    pip3 install requests --user
fi

# Run publish script
echo "🚀 Publishing to Zenodo..."
python3 scripts/zenodo_publish.py --token "$ZENODO_ACCESS_TOKEN" "$@"

echo ""
echo "✅ Done! Check ZENODO_DOI.txt for the DOI"

