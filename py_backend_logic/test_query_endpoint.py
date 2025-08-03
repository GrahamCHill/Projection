import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_query_endpoint():
    """Test the new database query endpoint"""
    print("Testing database query endpoint...")
    
    # Test 1: Get database info
    print("\nTest 1: Get database info")
    response = requests.get(f"{BASE_URL}/api/db/info")
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test 2: Query users table
    print("\nTest 2: Query users table")
    response = requests.get(f"{BASE_URL}/api/db/query/users")
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total records: {data['metadata']['total_count']}")
        print(f"Available filters: {data['metadata']['available_filters']}")
        print(f"First few records: {json.dumps(data['data'][:2], indent=2)}")
    else:
        print(f"Error: {response.text}")
    
    # Test 3: Query with invalid table name
    print("\nTest 3: Query with invalid table name")
    response = requests.get(f"{BASE_URL}/api/db/query/invalid_table")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test 4: Query with filters
    print("\nTest 4: Query with filters")
    response = requests.get(f"{BASE_URL}/api/db/query/cv_documents?limit=5")
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total records: {data['metadata']['total_count']}")
        print(f"Limited to: {data['metadata']['limit']}")
        print(f"Number of records returned: {len(data['data'])}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_query_endpoint()