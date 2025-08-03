from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
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
router = APIRouter(prefix="/api/github", tags=["github"])

# Configuration
GO_BACKEND_URL = os.getenv("GO_BACKEND_URL", "http://localhost:8001")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# Models
class GitHubRequest(BaseModel):
    operation: str
    repo_path: str
    github_owner: Optional[str] = None
    github_repo: Optional[str] = None
    branch: Optional[str] = None
    file_path: Optional[str] = None

class GitHubResponse(BaseModel):
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
            f"{GO_BACKEND_URL}/api/github",
            json=request_data,
            timeout=30  # 30 seconds timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error calling Go backend: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Failed to communicate with GitHub service: {str(e)}"
        )

@router.get("/status")
async def get_status():
    """
    Check the status of the GitHub integration.
    """
    try:
        response = requests.get(f"{GO_BACKEND_URL}/health", timeout=5)
        response.raise_for_status()
        
        # Check if GitHub token is configured
        token_configured = GITHUB_TOKEN != ""
        
        return {
            "status": "available",
            "go_backend_url": GO_BACKEND_URL,
            "github_token_configured": token_configured,
            "message": "GitHub integration is available"
        }
    except requests.RequestException as e:
        logger.error(f"Error checking GitHub service status: {str(e)}")
        return {
            "status": "unavailable",
            "go_backend_url": GO_BACKEND_URL,
            "github_token_configured": GITHUB_TOKEN != "",
            "error": str(e)
        }

@router.post("/clone")
async def clone_repository(request: GitHubRequest):
    """
    Clone a GitHub repository.
    """
    if not request.github_owner or not request.github_repo or not request.repo_path:
        raise HTTPException(status_code=400, detail="GitHub owner, repository name, and local path are required")
    
    request_data = {
        "operation": "clone",
        "repo_path": request.repo_path,
        "github_owner": request.github_owner,
        "github_repo": request.github_repo,
        "branch": request.branch
    }
    return call_go_backend(request_data)

@router.post("/pull")
async def pull_repository(request: GitHubRequest):
    """
    Pull changes from a GitHub repository.
    """
    if not request.repo_path:
        raise HTTPException(status_code=400, detail="Repository path is required")
    
    request_data = {
        "operation": "pull",
        "repo_path": request.repo_path,
        "branch": request.branch
    }
    return call_go_backend(request_data)

@router.post("/push")
async def push_repository(request: GitHubRequest):
    """
    Push changes to a GitHub repository.
    """
    if not request.repo_path:
        raise HTTPException(status_code=400, detail="Repository path is required")
    
    request_data = {
        "operation": "push",
        "repo_path": request.repo_path,
        "branch": request.branch
    }
    return call_go_backend(request_data)

@router.post("/status")
async def get_repository_status(request: GitHubRequest):
    """
    Get the status of a GitHub repository.
    """
    if not request.repo_path:
        raise HTTPException(status_code=400, detail="Repository path is required")
    
    request_data = {
        "operation": "status",
        "repo_path": request.repo_path
    }
    return call_go_backend(request_data)