#!/usr/bin/env python3
"""
Test Zenodo API connection.

Tests if token is valid and API is accessible.
"""

import os
import sys
import requests

ZENODO_SANDBOX_URL = "https://sandbox.zenodo.org/api"
ZENODO_PRODUCTION_URL = "https://zenodo.org/api"


def test_connection(api_url: str, token: str) -> bool:
    """Test connection to Zenodo API."""
    print(f"Testing connection to: {api_url}")
    
    headers = {
        "Authorization": f"Bearer {token}",
    }
    
    # Test by getting user info
    response = requests.get(
        f"{api_url}/deposit/depositions",
        headers=headers,
        params={"access_token": token, "size": 1}
    )
    
    if response.status_code == 200:
        print("✅ Connection successful!")
        print(f"   Status: {response.status_code}")
        return True
    else:
        print(f"❌ Connection failed: {response.status_code}")
        print(f"   Error: {response.text[:200]}")
        return False


def main():
    token = os.getenv("ZENODO_ACCESS_TOKEN")
    
    if not token:
        print("❌ ZENODO_ACCESS_TOKEN not set")
        print("   Set: export ZENODO_ACCESS_TOKEN='your_token'")
        sys.exit(1)
    
    print("Testing Zenodo API connection...")
    print("=" * 60)
    
    # Test sandbox
    print("\n1. Testing SANDBOX:")
    sandbox_ok = test_connection(ZENODO_SANDBOX_URL, token)
    
    # Test production
    print("\n2. Testing PRODUCTION:")
    production_ok = test_connection(ZENODO_PRODUCTION_URL, token)
    
    print("\n" + "=" * 60)
    if sandbox_ok and production_ok:
        print("✅ All connections successful!")
        print("\nYou can now publish using:")
        print("  python3 scripts/zenodo_publish.py --sandbox  # Test")
        print("  python3 scripts/zenodo_publish.py            # Production")
    else:
        print("⚠️  Some connections failed")
        print("   Check your token and permissions")


if __name__ == "__main__":
    main()

