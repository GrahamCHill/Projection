import os
import sys
from pathlib import Path

# Add parent directory to path to import from parent directory
sys.path.append(str(Path(__file__).parent.parent))
from api_key_manager import GroqApiKeyManager

def test_api_key_manager():
    """
    Test the GroqApiKeyManager class functionality.
    """
    # Create a test status file path
    test_status_file = "test_groq_api_status.txt"
    
    # Initialize the manager
    manager = GroqApiKeyManager(status_file_path=test_status_file)
    
    # Check if the API key is defined
    is_defined = manager.is_api_key_defined()
    print(f"API key is defined: {is_defined}")
    
    # Check if the status file was created
    status_file = Path(test_status_file)
    if status_file.exists():
        with open(status_file) as f:
            status_content = f.read().strip()
        print(f"Status file content: {status_content}")
        print(f"Status file matches is_defined: {status_content == str(is_defined)}")
    else:
        print("Status file was not created!")
    
    # Test what happens when the API key is undefined
    # Save the original key
    original_key = os.environ.get("GROQ_API_KEY")
    
    try:
        # Temporarily unset the API key
        if "GROQ_API_KEY" in os.environ:
            del os.environ["GROQ_API_KEY"]
        
        # Reload the API key
        manager.reload_api_key()
        
        # Check if the API key is defined now
        is_defined = manager.is_api_key_defined()
        print(f"API key is defined after unsetting: {is_defined}")
        
        # Check the status file again
        if status_file.exists():
            with open(status_file) as f:
                status_content = f.read().strip()
            print(f"Status file content after unsetting: {status_content}")
            print(f"Status file matches is_defined: {status_content == str(is_defined)}")
        else:
            print("Status file was not created after reload!")
    finally:
        # Restore the original key
        if original_key is not None:
            os.environ["GROQ_API_KEY"] = original_key
    
    # Clean up the test file
    if status_file.exists():
        status_file.unlink()
        print(f"Removed test status file: {test_status_file}")

if __name__ == "__main__":
    test_api_key_manager()