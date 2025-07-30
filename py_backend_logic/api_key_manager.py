import os
from pathlib import Path
from dotenv import load_dotenv

class GroqApiKeyManager:
    """
    A class to manage the GROQ API key, check its validity,
    and maintain a status file that tracks whether the key is defined.
    """
    
    def __init__(self, status_file_path="groq_api_status.txt"):
        """
        Initialize the API key manager.
        
        Args:
            status_file_path: Path to the status file that will store the API key status
        """
        # Load environment variables
        load_dotenv()
        
        # Set the status file path
        self.status_file_path = Path(status_file_path)
        
        # Get the API key
        self.api_key = os.getenv("GROQ_API_KEY")
        
        # Update the status file
        self.update_status_file()
    
    def is_api_key_defined(self):
        """
        Check if the GROQ API key is defined.
        
        Returns:
            bool: True if the API key is defined, False otherwise
        """
        return self.api_key is not None and self.api_key.strip() != ""
    
    def update_status_file(self):
        """
        Update the status file with the current API key status.
        """
        status = self.is_api_key_defined()
        with open(self.status_file_path, "w") as f:
            f.write(str(status))
    
    def reload_api_key(self):
        """
        Reload the API key from environment variables and update the status file.
        This can be called when the environment is updated.
        
        Returns:
            bool: True if the API key is defined after reloading, False otherwise
        """
        # Reload environment variables
        load_dotenv()
        
        # Update the API key
        self.api_key = os.getenv("GROQ_API_KEY")
        
        # Update the status file
        self.update_status_file()
        
        return self.is_api_key_defined()
    
    def get_api_key(self):
        """
        Get the GROQ API key.
        
        Returns:
            str or None: The API key if defined, None otherwise
        """
        return self.api_key