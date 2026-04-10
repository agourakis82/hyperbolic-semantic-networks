# Zenodo Quick Start

## Get Your Token

1. Visit: https://zenodo.org/account/settings/applications/tokens/new/
2. Create token with scopes: `deposit:write` and `deposit:actions`
3. Copy token

## Publish Release

```bash
# Set token
export ZENODO_ACCESS_TOKEN='your_token_here'

# Install dependencies (if needed)
pip3 install requests --user

# Publish
python3 scripts/zenodo_publish.py

# Or use wrapper
./scripts/zenodo_publish.sh
```

## Test First (Sandbox)

```bash
python3 scripts/zenodo_publish.py --sandbox
```

## After Publishing

1. Check `ZENODO_DOI.txt` for DOI
2. Update repository with DOI
3. Create GitHub release linking to Zenodo

---

**Full guide**: See `docs/ZENODO_API_GUIDE.md`
