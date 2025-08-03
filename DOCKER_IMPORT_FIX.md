# Docker Import Path Fix

## Issue Description

When running the application in Docker, the following error occurred:

```
ModuleNotFoundError: No module named 'py_backend_logic'
```

This error happened when trying to import from `py_backend_logic.core.logging_manager` in the main.py file. The issue was that the Docker container couldn't find the `py_backend_logic` package because it wasn't in the Python path.

## Root Cause Analysis

1. The Docker container was set up with `/app` as the working directory
2. The local `./py_backend_logic` directory was mounted to `/app` in the container
3. The `main.py` file was at `/app/main.py` in the container
4. The Docker container was running `uvicorn main:app` to start the application
5. Python couldn't find the `py_backend_logic` package because it wasn't in the Python path

## Solution

The solution was to create a new `main.py` file at the root level of the project that:

1. Adds the current directory to the Python path
2. Imports the app from the `py_backend_logic.main` module
3. Runs the application using uvicorn

This approach allows the Docker container to find the `py_backend_logic` package when running the application.

### Changes Made

1. Created a new `main.py` file at the root level with the following content:

```python
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the app from py_backend_logic.main
from py_backend_logic.main import app

# This allows the file to be run directly with python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

2. Updated the Dockerfile to use `python main.py` instead of `uvicorn main:app`:

```dockerfile
# Command to run the application
CMD ["python", "main.py"]
```

## Testing

The solution was tested using a script that simulates the Docker environment by adding the current directory to the Python path. All imports were successful, confirming that the issue has been fixed.

## Benefits of This Approach

1. **Minimal Changes**: Only required adding a new file and updating the Dockerfile command
2. **No Code Refactoring**: Didn't require changing any existing code or import statements
3. **Maintainability**: The solution is easy to understand and maintain
4. **Consistency**: The same code structure works both in development and in Docker

## Future Considerations

If the project structure changes in the future, the `main.py` file may need to be updated to reflect those changes. However, as long as the `py_backend_logic` package remains at the root level of the project, the current solution should continue to work.