# GROQ API Key Manager

## Overview

The `GroqApiKeyManager` class provides a mechanism to check if the GROQ API key is defined in the environment variables and maintains a status file that tracks this information. This allows the application to gracefully handle cases where the API key is not available.

## Features

- Checks if the GROQ API key is defined in environment variables
- Writes the status (True/False) to a text file
- Automatically updates the status file when the environment is reloaded
- Exposes the API key to the main application

## Usage

### Basic Usage

```python
from api_key_manager import GroqApiKeyManager

# Initialize the manager (creates/updates the status file)
api_key_manager = GroqApiKeyManager()

# Get the API key
api_key = api_key_manager.get_api_key()

# Check if the API key is defined
is_defined = api_key_manager.is_api_key_defined()
```

### Custom Status File Path

You can specify a custom path for the status file:

```python
api_key_manager = GroqApiKeyManager(status_file_path="custom_path/groq_status.txt")
```

### Reloading the API Key

If the environment variables are updated (e.g., the API key is added or changed), you can reload the key:

```python
# Reload the API key from environment variables
is_defined = api_key_manager.reload_api_key()
```

## API Endpoints

The application provides two endpoints to interact with the API key manager:

1. `GET /api/groq/status` - Check if the GROQ API key is defined
2. `POST /api/groq/reload` - Reload the GROQ API key from environment variables

## Status File

The status file is a simple text file that contains either `True` or `False`, indicating whether the GROQ API key is defined. By default, the file is named `groq_api_status.txt` and is created in the current working directory.

## Integration with main.py

The `main.py` file uses the `GroqApiKeyManager` to get the API key and initialize the GROQ client. If the API key is undefined, the application will still run, but GROQ-related functionality will not work correctly.