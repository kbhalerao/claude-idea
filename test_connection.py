#!/usr/bin/env python3
"""Simple script to test CouchDB connection and configuration."""

import sys
from idea_capture.config import config
import requests


def test_connection():
    """Test connection to CouchDB server."""
    print("Testing Idea Capture Configuration...\n")

    # Test 1: Configuration
    print("1. Checking configuration...")
    try:
        config.validate()
        print(f"   ✓ Configuration loaded")
        print(f"   - URL: {config.url}")
        print(f"   - Database: {config.database}")
        print(f"   - Username: {config.username}")
    except ValueError as e:
        print(f"   ✗ Configuration error: {e}")
        return False

    # Test 2: Server connection
    print("\n2. Testing CouchDB server connection...")
    try:
        response = requests.get(config.url, auth=config.auth)
        response.raise_for_status()
        info = response.json()
        print(f"   ✓ Connected to CouchDB")
        print(f"   - Version: {info.get('version')}")
        print(f"   - Vendor: {info.get('vendor', {}).get('name')}")
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Connection failed: {e}")
        print(f"\n   Troubleshooting:")
        print(f"   - Is CouchDB running? Try: curl {config.url}/")
        print(f"   - Check COUCHDB_URL in .env file")
        return False

    # Test 3: Authentication
    print("\n3. Testing authentication...")
    try:
        response = requests.get(f"{config.url}/_session", auth=config.auth)
        response.raise_for_status()
        session = response.json()
        user = session.get('userCtx', {}).get('name')
        if user:
            print(f"   ✓ Authenticated as: {user}")
        else:
            print(f"   ✗ Not authenticated (anonymous access)")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Authentication failed: {e}")
        print(f"\n   Troubleshooting:")
        print(f"   - Check COUCHDB_USERNAME and COUCHDB_PASSWORD in .env")
        return False

    # Test 4: Database access
    print("\n4. Checking database...")
    try:
        response = requests.get(f"{config.url}/{config.database}", auth=config.auth)
        if response.status_code == 404:
            print(f"   ⚠ Database '{config.database}' does not exist")
            print(f"   - Run: idea setup")
            return False
        response.raise_for_status()
        db_info = response.json()
        print(f"   ✓ Database '{config.database}' exists")
        print(f"   - Documents: {db_info.get('doc_count')}")
        print(f"   - Update sequence: {db_info.get('update_seq')}")
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Database check failed: {e}")
        return False

    # Test 5: Design documents
    print("\n5. Checking design documents...")
    try:
        response = requests.get(
            f"{config.url}/{config.database}/_design/queries",
            auth=config.auth
        )
        if response.status_code == 404:
            print(f"   ⚠ Design documents not installed")
            print(f"   - Run: idea setup")
            return False
        response.raise_for_status()
        print(f"   ✓ Design documents installed")
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Design document check failed: {e}")
        return False

    print("\n" + "="*50)
    print("✓ All tests passed!")
    print("="*50)
    print("\nYou're ready to use Idea Capture!")
    print("\nTry:")
    print('  idea add "My first idea"')
    print("  idea list")
    print("  idea next")
    return True


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
