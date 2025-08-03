#!/usr/bin/env python3
"""
Test script for Git LFS integration between Python backend and Golang service.
This script tests the connection to the Golang Git LFS service.
"""

import requests
import sys
import os
import json

# Configuration
GO_BACKEND_URL = os.getenv("GO_BACKEND_URL", "http://localhost:8001")

def test_go_backend_health():
    """Test the health endpoint of the Go backend."""
    try:
        response = requests.get(f"{GO_BACKEND_URL}/health", timeout=5)
        response.raise_for_status()
        print(f"✅ Go backend health check successful: {response.json()}")
        return True
    except requests.RequestException as e:
        print(f"❌ Go backend health check failed: {str(e)}")
        return False

def test_git_lfs_status(repo_path):
    """Test the Git LFS status endpoint."""
    try:
        payload = {
            "operation": "status",
            "repo_path": repo_path
        }
        response = requests.post(
            f"{GO_BACKEND_URL}/api/git-lfs",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        print(f"✅ Git LFS status check successful:")
        print(json.dumps(result, indent=2))
        return True
    except requests.RequestException as e:
        print(f"❌ Git LFS status check failed: {str(e)}")
        return False

def main():
    """Main function to run the tests."""
    print("Testing Git LFS integration between Python backend and Golang service...")
    
    # Test Go backend health
    if not test_go_backend_health():
        print("❌ Go backend is not running. Please start the Go backend first.")
        sys.exit(1)
    
    # Test Git LFS status
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
        print(f"Testing Git LFS status for repository: {repo_path}")
        test_git_lfs_status(repo_path)
    else:
        print("⚠️ No repository path provided. Skipping Git LFS status test.")
        print("Usage: python test_git_lfs_integration.py <repo_path>")
    
    print("Tests completed.")

if __name__ == "__main__":
    main()