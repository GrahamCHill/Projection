# Git and GitHub Integration

This document describes the Git, GitHub, and Git LFS (Large File Storage) integration for the Projection application.

## Overview

The Projection now includes Git and GitHub support through a dedicated Golang backend service. This service handles Git operations such as cloning, pulling, and pushing repositories, as well as Git LFS operations such as initialization, tracking files, and managing LFS objects.

The architecture consists of:
1. A Golang backend service that interfaces directly with Git and Git LFS
2. A Python FastAPI module that communicates with the Golang service
3. Integration with the existing Projection application
4. Support for GitHub repositories with authentication

## Requirements

- Go 1.20 or later
- Git LFS installed on the system
- Python 3.9 or later
- All dependencies listed in `py_backend_logic/requirements.txt`

## Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│  React Frontend │──────│ Python Backend  │──────│  Golang Backend │──────┐
│                 │      │                 │      │                 │      │
└─────────────────┘      └─────────────────┘      └─────────────────┘      │
                                                                           │
                                                                           ▼
                                                                    ┌─────────────┐
                                                                    │             │
                                                                    │  Git LFS    │
                                                                    │             │
                                                                    └─────────────┘
```

## Golang Backend

The Golang backend provides a simple HTTP API for Git LFS operations:

- `GET /health`: Health check endpoint
- `POST /api/git-lfs`: Main endpoint for Git LFS operations

The following operations are supported:

1. `init`: Initialize Git LFS in a repository
2. `track`: Track files with Git LFS
3. `push`: Push LFS objects to the remote repository
4. `pull`: Pull LFS objects from the remote repository
5. `status`: Check the status of LFS files in the repository

## Python Integration

The Python backend includes a FastAPI router that communicates with the Golang service:

- `GET /api/git-lfs/status`: Check the status of the Git LFS service
- `POST /api/git-lfs/init`: Initialize Git LFS in a repository
- `POST /api/git-lfs/track`: Track files with Git LFS
- `POST /api/git-lfs/push`: Push LFS objects to the remote repository
- `POST /api/git-lfs/pull`: Pull LFS objects from the remote repository
- `POST /api/git-lfs/status`: Check the status of LFS files in the repository

## Configuration

The Golang backend runs on port 8001 by default. The Python backend connects to the Golang service using the `GO_BACKEND_URL` environment variable, which defaults to `http://localhost:8001`.

## Starting the Services

The services are automatically started by the run scripts:

- `run.bat` for Windows
- `run.sh` for Linux/Mac

The scripts check if Go is installed and start the Golang service if available. If Go is not installed, the Git LFS functionality will be disabled.

## Testing

A test script is provided to verify the integration between the Python backend and Golang service:

```bash
python py_backend_logic/test_git_lfs_integration.py <repo_path>
```

Replace `<repo_path>` with the path to a Git repository to test the Git LFS status endpoint.

## API Usage Examples

### Initialize Git LFS in a Repository

```python
import requests

response = requests.post(
    "http://localhost:8000/api/git-lfs/init",
    json={
        "operation": "init",
        "repo_path": "/path/to/repo"
    }
)
print(response.json())
```

### Track Files with Git LFS

```python
import requests

response = requests.post(
    "http://localhost:8000/api/git-lfs/track",
    json={
        "operation": "track",
        "repo_path": "/path/to/repo",
        "file_path": "*.pdf"
    }
)
print(response.json())
```

### Check Git LFS Status

```python
import requests

response = requests.post(
    "http://localhost:8000/api/git-lfs/status",
    json={
        "operation": "status",
        "repo_path": "/path/to/repo"
    }
)
print(response.json())
```

## Troubleshooting

1. **Go backend not starting**: Ensure Go is installed and in your PATH.
2. **Git LFS commands failing**: Ensure Git LFS is installed on your system.
3. **Connection errors**: Check that the Golang service is running and the `GO_BACKEND_URL` environment variable is set correctly.
4. **Permission errors**: Ensure the application has permission to access the Git repositories.

## GitHub Integration

The Projection now includes GitHub integration for working with repositories directly. This integration uses the same Golang backend service and provides the following features:

- Clone GitHub repositories
- Pull changes from GitHub repositories
- Push changes to GitHub repositories
- Check repository status

### GitHub API Endpoints

The Python backend includes a FastAPI router for GitHub operations:

- `GET /api/github/status`: Check the status of the GitHub integration
- `POST /api/github/clone`: Clone a GitHub repository
- `POST /api/github/pull`: Pull changes from a GitHub repository
- `POST /api/github/push`: Push changes to a GitHub repository
- `POST /api/github/status`: Check the status of a GitHub repository

### GitHub API Usage Examples

#### Clone a GitHub Repository

```python
import requests

response = requests.post(
    "http://localhost:8000/api/github/clone",
    json={
        "operation": "clone",
        "repo_path": "/path/to/local/repo",
        "github_owner": "username",
        "github_repo": "repository-name"
    }
)
print(response.json())
```

#### Pull Changes from a GitHub Repository

```python
import requests

response = requests.post(
    "http://localhost:8000/api/github/pull",
    json={
        "operation": "pull",
        "repo_path": "/path/to/local/repo"
    }
)
print(response.json())
```

#### Push Changes to a GitHub Repository

```python
import requests

response = requests.post(
    "http://localhost:8000/api/github/push",
    json={
        "operation": "push",
        "repo_path": "/path/to/local/repo"
    }
)
print(response.json())
```

## Docker Integration

The Projection now includes Docker support for both the Python backend and the Golang backend. The Docker setup includes:

- A Python backend container with Git and GitHub CLI
- A Golang backend container with Git and Git LFS
- Environment variables for GitHub authentication

To use the Docker setup, you need to:

1. Set the `GITHUB_TOKEN` environment variable for GitHub authentication
2. Run the application using `docker-compose up`

## Future Improvements

1. Add authentication between the Python and Golang services
2. Implement more Git and Git LFS operations
3. Add support for Git LFS hooks
4. Improve error handling and reporting
5. Add metrics and monitoring
6. Support for private GitHub repositories with SSH keys