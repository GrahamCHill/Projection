from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import requests
import logging
import os
from sqlalchemy.orm import Session

# Import our modules
from database import get_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/git-lfs", tags=["git-lfs"])

# Configuration
GO_BACKEND_URL = os.getenv("GO_BACKEND_URL", "http://localhost:8001")

# Models
class GitLFSRequest(BaseModel):
    operation: str
    repo_path: str
    file_path: Optional[str] = None
    url: Optional[str] = None

class GitLFSResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None

# Helper function to call the Go backend
def call_go_backend(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call the Go backend service with the provided request data.
    """
    try:
        response = requests.post(
            f"{GO_BACKEND_URL}/api/git-lfs",
            json=request_data,
            timeout=30  # 30 seconds timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error calling Go backend: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Failed to communicate with Git LFS service: {str(e)}"
        )

@router.get("/status")
async def get_status():
    """
    Check the status of the Git LFS Go backend service.
    """
    try:
        response = requests.get(f"{GO_BACKEND_URL}/health", timeout=5)
        response.raise_for_status()
        return {
            "status": "available",
            "go_backend_url": GO_BACKEND_URL,
            "message": response.json().get("message", "Git LFS backend is running")
        }
    except requests.RequestException as e:
        logger.error(f"Error checking Git LFS service status: {str(e)}")
        return {
            "status": "unavailable",
            "go_backend_url": GO_BACKEND_URL,
            "error": str(e)
        }

@router.post("/init")
async def init_git_lfs(request: GitLFSRequest):
    """
    Initialize Git LFS in a repository.
    """
    request_data = {
        "operation": "init",
        "repo_path": request.repo_path
    }
    return call_go_backend(request_data)

@router.post("/track")
async def track_files(request: GitLFSRequest):
    """
    Track files with Git LFS.
    """
    if not request.file_path:
        raise HTTPException(status_code=400, detail="file_path is required")
    
    request_data = {
        "operation": "track",
        "repo_path": request.repo_path,
        "file_path": request.file_path
    }
    return call_go_backend(request_data)

@router.post("/push")
async def push_lfs_objects(request: GitLFSRequest):
    """
    Push Git LFS objects to the remote repository.
    """
    request_data = {
        "operation": "push",
        "repo_path": request.repo_path
    }
    return call_go_backend(request_data)

@router.post("/pull")
async def pull_lfs_objects(request: GitLFSRequest):
    """
    Pull Git LFS objects from the remote repository.
    """
    request_data = {
        "operation": "pull",
        "repo_path": request.repo_path
    }
    return call_go_backend(request_data)

@router.post("/status")
async def get_lfs_status(request: GitLFSRequest):
    """
    Get the status of Git LFS files in the repository.
    """
    request_data = {
        "operation": "status",
        "repo_path": request.repo_path
    }
    return call_go_backend(request_data)