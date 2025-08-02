import os
import sys
import requests
import json
import time
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import our modules (will fail if dependencies aren't installed)
try:
    from github_client import github_client
    from github_service import GitHubRepositoryService
    from github_scheduler import github_scheduler
    from database import get_session
    DEPENDENCIES_INSTALLED = True
except ImportError:
    DEPENDENCIES_INSTALLED = False
    print("Warning: GitHub API dependencies not installed.")
    print("This test will only check if the API endpoints are accessible, not their functionality.")

def test_api_endpoints():
    """Test if the GitHub API endpoints are accessible"""
    print("\n=== Testing GitHub API endpoints ===")
    
    # Test status endpoint
    try:
        status_response = requests.get("http://localhost:8000/api/github/polling/status", timeout=5)
        if status_response.status_code == 200:
            print("Polling status endpoint: OK")
            print(f"Status response: {json.dumps(status_response.json(), indent=2)}")
        else:
            print(f"Polling status endpoint: Failed - Status code {status_response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Polling status endpoint: Failed - {str(e)}")
    
    # Test repositories endpoint
    try:
        repos_response = requests.get("http://localhost:8000/api/github/repositories", timeout=5)
        if repos_response.status_code == 200:
            print("Repositories endpoint: OK")
            repos = repos_response.json()
            print(f"Found {len(repos)} repositories")
        else:
            print(f"Repositories endpoint: Failed - Status code {repos_response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Repositories endpoint: Failed - {str(e)}")
    
    # Test tags endpoint
    try:
        tags_response = requests.get("http://localhost:8000/api/github/tags", timeout=5)
        if tags_response.status_code == 200:
            print("Tags endpoint: OK")
            tags = tags_response.json()
            print(f"Found {len(tags)} tags")
        else:
            print(f"Tags endpoint: Failed - Status code {tags_response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Tags endpoint: Failed - {str(e)}")
    
    # Test projects endpoint
    try:
        projects_response = requests.get("http://localhost:8000/api/github/projects", timeout=5)
        if projects_response.status_code == 200:
            print("Projects endpoint: OK")
            projects = projects_response.json()
            print(f"Found {len(projects)} projects")
        else:
            print(f"Projects endpoint: Failed - Status code {projects_response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Projects endpoint: Failed - {str(e)}")
    
    # Test rate limit endpoint
    try:
        rate_limit_response = requests.get("http://localhost:8000/api/github/rate-limit", timeout=5)
        if rate_limit_response.status_code == 200:
            print("Rate limit endpoint: OK")
        else:
            print(f"Rate limit endpoint: Failed - Status code {rate_limit_response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Rate limit endpoint: Failed - {str(e)}")

def test_create_tag():
    """Test creating a tag"""
    print("\n=== Testing tag creation ===")
    
    tag_data = {
        "name": f"Test Tag {int(time.time())}",
        "description": "Tag created by test script",
        "color": "#00FF00"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/github/tags",
            json=tag_data,
            timeout=5
        )
        
        if response.status_code == 200:
            print("Tag creation: OK")
            tag = response.json()
            print(f"Created tag: {tag['name']} (ID: {tag['id']})")
            return tag
        else:
            print(f"Tag creation: Failed - Status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Tag creation: Failed - {str(e)}")
        return None

def test_create_project():
    """Test creating a project"""
    print("\n=== Testing project creation ===")
    
    project_data = {
        "name": f"Test Project {int(time.time())}",
        "description": "Project created by test script"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/github/projects",
            json=project_data,
            timeout=5
        )
        
        if response.status_code == 200:
            print("Project creation: OK")
            project = response.json()
            print(f"Created project: {project['name']} (ID: {project['id']})")
            return project
        else:
            print(f"Project creation: Failed - Status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Project creation: Failed - {str(e)}")
        return None

def test_poll_repositories():
    """Test polling repositories"""
    print("\n=== Testing repository polling ===")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/github/polling/poll-now",
            timeout=10  # Longer timeout for polling
        )
        
        if response.status_code == 200:
            print("Repository polling: OK")
            result = response.json()
            print(f"Polling result: {json.dumps(result, indent=2)}")
        else:
            print(f"Repository polling: Failed - Status code {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Repository polling: Failed - {str(e)}")

def test_direct_service():
    """Test the GitHub service directly (if dependencies are installed)"""
    if not DEPENDENCIES_INSTALLED:
        print("\n=== Skipping direct service test (dependencies not installed) ===")
        return
    
    print("\n=== Testing GitHub service directly ===")
    
    try:
        # Create a session and service
        db = get_session()
        service = GitHubRepositoryService(db)
        
        # Create a tag
        tag = service.create_tag(
            name=f"Direct Tag {int(time.time())}",
            description="Tag created directly by test script",
            color="#0000FF"
        )
        print(f"Created tag directly: {tag.name} (ID: {tag.id})")
        
        # Create a project
        project = service.create_project(
            name=f"Direct Project {int(time.time())}",
            description="Project created directly by test script"
        )
        print(f"Created project directly: {project.name} (ID: {project.id})")
        
        # List repositories
        repos = service.list_repositories()
        print(f"Found {len(repos)} repositories directly")
        
        # Close the session
        db.close()
    except Exception as e:
        print(f"Direct service test failed: {str(e)}")

if __name__ == "__main__":
    print("=== GitHub API Test Script ===")
    print("This script tests the GitHub repository management API.")
    print("Make sure the backend server is running before executing this script.")
    
    # Wait a moment to ensure services are fully started
    print("\nWaiting 2 seconds for services to start...")
    time.sleep(2)
    
    # Run tests
    test_api_endpoints()
    tag = test_create_tag()
    project = test_create_project()
    test_poll_repositories()
    test_direct_service()
    
    print("\n=== Test completed ===")