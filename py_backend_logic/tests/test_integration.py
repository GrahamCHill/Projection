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
    from storage import s3_storage
    from vector_db import vector_db
    DEPENDENCIES_INSTALLED = True
except ImportError:
    DEPENDENCIES_INSTALLED = False
    print("Warning: S3 storage and vector database dependencies not installed.")
    print("This test will only check if the services are running, not their functionality.")

def test_services_running():
    """Test if the services are running in Docker"""
    print("\n=== Testing if services are running ===")
    
    # Test MinIO
    try:
        minio_response = requests.get("http://localhost:9000/minio/health/live", timeout=5)
        print(f"MinIO status: {'OK' if minio_response.status_code == 200 else 'Failed'}")
    except requests.exceptions.RequestException as e:
        print(f"MinIO status: Failed - {str(e)}")
    
    # Test Qdrant
    try:
        qdrant_response = requests.get("http://localhost:6333/health", timeout=5)
        print(f"Qdrant status: {'OK' if qdrant_response.status_code == 200 else 'Failed'}")
    except requests.exceptions.RequestException as e:
        print(f"Qdrant status: Failed - {str(e)}")
    
    # Test Backend API
    try:
        backend_response = requests.get("http://localhost:8000/", timeout=5)
        print(f"Backend API status: {'OK' if backend_response.status_code == 200 else 'Failed'}")
    except requests.exceptions.RequestException as e:
        print(f"Backend API status: Failed - {str(e)}")
    
    # Test Integration API
    try:
        integration_response = requests.get("http://localhost:8000/api/integration/status", timeout=5)
        if integration_response.status_code == 200:
            print("Integration API status: OK")
            print(f"Integration API response: {json.dumps(integration_response.json(), indent=2)}")
        else:
            print(f"Integration API status: Failed - Status code {integration_response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Integration API status: Failed - {str(e)}")

def test_s3_functionality():
    """Test S3 storage functionality"""
    if not DEPENDENCIES_INSTALLED:
        print("\n=== Skipping S3 functionality test (dependencies not installed) ===")
        return
    
    print("\n=== Testing S3 storage functionality ===")
    
    # Create a test file
    test_file_path = Path("./tests/test_file.txt")
    test_file_path.parent.mkdir(exist_ok=True)
    with open(test_file_path, "w") as f:
        f.write("This is a test file for S3 storage.")
    
    # Upload the file
    object_name = "test_file.txt"
    upload_result = s3_storage.upload_file(str(test_file_path), object_name)
    print(f"Upload result: {'Success' if upload_result else 'Failed'}")
    
    # List objects
    objects = s3_storage.list_objects()
    print(f"Objects in bucket: {len(objects)}")
    for obj in objects:
        print(f"  - {obj.get('Key')}")
    
    # Generate presigned URL
    presigned_url = s3_storage.generate_presigned_url(object_name)
    print(f"Presigned URL generated: {'Yes' if presigned_url else 'No'}")
    
    # Delete the file
    delete_result = s3_storage.delete_object(object_name)
    print(f"Delete result: {'Success' if delete_result else 'Failed'}")
    
    # Clean up
    test_file_path.unlink(missing_ok=True)

def test_vector_db_functionality():
    """Test vector database functionality"""
    if not DEPENDENCIES_INSTALLED:
        print("\n=== Skipping vector database functionality test (dependencies not installed) ===")
        return
    
    print("\n=== Testing vector database functionality ===")
    
    # Create a test embedding
    import numpy as np
    test_embedding = np.random.randn(1536)
    test_embedding = test_embedding / np.linalg.norm(test_embedding)
    
    # Store the embedding
    document_id = "test_document"
    metadata = {"title": "Test Document", "description": "This is a test document"}
    store_result = vector_db.store_embedding(document_id, test_embedding, metadata)
    print(f"Store result: {'Success' if store_result else 'Failed'}")
    
    # Count embeddings
    count = vector_db.count_embeddings()
    print(f"Embeddings count: {count}")
    
    # List embeddings
    embeddings = vector_db.list_embeddings()
    print(f"Embeddings in database: {len(embeddings)}")
    for emb in embeddings:
        print(f"  - {emb.get('id')}: {emb.get('metadata', {}).get('title')}")
    
    # Search similar
    search_results = vector_db.search_similar(test_embedding)
    print(f"Search results: {len(search_results)}")
    
    # Delete the embedding
    delete_result = vector_db.delete_embedding(document_id)
    print(f"Delete result: {'Success' if delete_result else 'Failed'}")

def test_integration_api():
    """Test integration API endpoints"""
    print("\n=== Testing integration API endpoints ===")
    
    # Test status endpoint
    try:
        status_response = requests.get("http://localhost:8000/api/integration/status", timeout=5)
        if status_response.status_code == 200:
            print("Status endpoint: OK")
        else:
            print(f"Status endpoint: Failed - Status code {status_response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Status endpoint: Failed - {str(e)}")
    
    # Test list-cvs endpoint
    try:
        list_response = requests.get("http://localhost:8000/api/integration/list-cvs", timeout=5)
        if list_response.status_code == 200:
            print("List CVs endpoint: OK")
            print(f"CVs in database: {len(list_response.json())}")
        else:
            print(f"List CVs endpoint: Failed - Status code {list_response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"List CVs endpoint: Failed - {str(e)}")
    
    # Test search-similar endpoint
    try:
        search_data = {"query": "test query"}
        search_response = requests.post(
            "http://localhost:8000/api/integration/search-similar",
            json=search_data,
            timeout=5
        )
        if search_response.status_code == 200:
            print("Search similar endpoint: OK")
        else:
            print(f"Search similar endpoint: Failed - Status code {search_response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Search similar endpoint: Failed - {str(e)}")

if __name__ == "__main__":
    print("=== Integration Test Script ===")
    print("This script tests the integration of S3 storage and vector database with the Projection.")
    print("Make sure the Docker containers are running before executing this script.")
    
    # Wait a moment to ensure services are fully started
    print("\nWaiting 5 seconds for services to start...")
    time.sleep(5)
    
    # Run tests
    test_services_running()
    test_s3_functionality()
    test_vector_db_functionality()
    test_integration_api()
    
    print("\n=== Test completed ===")