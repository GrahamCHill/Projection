from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging

from database import get_session
from github_models import GitHubRepository, RepositoryTag, RepositoryProject
from github_service import GitHubRepositoryService
from github_client import github_client
from github_scheduler import github_scheduler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/github", tags=["github"])

# Pydantic models for request/response
class TagCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: str = "#CCCCCC"

class TagResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    color: str
    
    class Config:
        orm_mode = True

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    
    class Config:
        orm_mode = True

class RepositoryResponse(BaseModel):
    id: int
    name: str
    full_name: str
    url: str
    html_url: str
    description: Optional[str] = None
    is_private: bool
    owner_name: str
    owner_type: str
    tags: List[TagResponse] = []
    projects: List[ProjectResponse] = []
    
    class Config:
        orm_mode = True

class PollingStatusResponse(BaseModel):
    is_running: bool
    polling_interval: int
    next_run_time: Optional[str] = None
    configured_users: List[str]
    configured_organizations: List[str]
    rate_limit_remaining: int
    rate_limit_reset: Optional[str] = None

# Helper function to get repository service
def get_repo_service(db: Session = Depends(get_session)) -> GitHubRepositoryService:
    return GitHubRepositoryService(db)

# Repository endpoints
@router.get("/repositories", response_model=List[RepositoryResponse])
def list_repositories(
    skip: int = 0, 
    limit: int = 100,
    service: GitHubRepositoryService = Depends(get_repo_service)
):
    """
    List all repositories
    """
    return service.list_repositories(skip=skip, limit=limit)

@router.get("/repositories/{repo_id}", response_model=RepositoryResponse)
def get_repository(
    repo_id: int,
    service: GitHubRepositoryService = Depends(get_repo_service)
):
    """
    Get a repository by ID
    """
    repo = service.get_repository(repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    return repo

@router.delete("/repositories/{repo_id}")
def delete_repository(
    repo_id: int,
    service: GitHubRepositoryService = Depends(get_repo_service)
):
    """
    Delete a repository by ID
    """
    result = service.delete_repository(repo_id)
    if not result:
        raise HTTPException(status_code=404, detail="Repository not found")
    return {"message": "Repository deleted successfully"}

# Tag endpoints
@router.get("/tags", response_model=List[TagResponse])
def list_tags(
    service: GitHubRepositoryService = Depends(get_repo_service)
):
    """
    List all tags
    """
    return service.list_tags()

@router.post("/tags", response_model=TagResponse)
def create_tag(
    tag: TagCreate,
    service: GitHubRepositoryService = Depends(get_repo_service)
):
    """
    Create a new tag
    """
    return service.create_tag(name=tag.name, description=tag.description, color=tag.color)

@router.get("/tags/{tag_id}", response_model=TagResponse)
def get_tag(
    tag_id: int,
    service: GitHubRepositoryService = Depends(get_repo_service)
):
    """
    Get a tag by ID
    """
    tag = service.get_tag(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag

@router.delete("/tags/{tag_id}")
def delete_tag(
    tag_id: int,
    service: GitHubRepositoryService = Depends(get_repo_service)
):
    """
    Delete a tag by ID
    """
    result = service.delete_tag(tag_id)
    if not result:
        raise HTTPException(status_code=404, detail="Tag not found")
    return {"message": "Tag deleted successfully"}

# Project endpoints
@router.get("/projects", response_model=List[ProjectResponse])
def list_projects(
    service: GitHubRepositoryService = Depends(get_repo_service)
):
    """
    List all projects
    """
    return service.list_projects()

@router.post("/projects", response_model=ProjectResponse)
def create_project(
    project: ProjectCreate,
    service: GitHubRepositoryService = Depends(get_repo_service)
):
    """
    Create a new project
    """
    return service.create_project(name=project.name, description=project.description)

@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    service: GitHubRepositoryService = Depends(get_repo_service)
):
    """
    Get a project by ID
    """
    project = service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    service: GitHubRepositoryService = Depends(get_repo_service)
):
    """
    Delete a project by ID
    """
    result = service.delete_project(project_id)
    if not result:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}

# Tag-Repository relationship endpoints
@router.post("/repositories/{repo_id}/tags/{tag_id}")
def add_tag_to_repository(
    repo_id: int,
    tag_id: int,
    service: GitHubRepositoryService = Depends(get_repo_service)
):
    """
    Add a tag to a repository
    """
    result = service.add_tag_to_repository(repo_id, tag_id)
    if not result:
        raise HTTPException(status_code=404, detail="Repository or tag not found")
    return {"message": "Tag added to repository successfully"}

@router.delete("/repositories/{repo_id}/tags/{tag_id}")
def remove_tag_from_repository(
    repo_id: int,
    tag_id: int,
    service: GitHubRepositoryService = Depends(get_repo_service)
):
    """
    Remove a tag from a repository
    """
    result = service.remove_tag_from_repository(repo_id, tag_id)
    if not result:
        raise HTTPException(status_code=404, detail="Repository or tag not found")
    return {"message": "Tag removed from repository successfully"}

# Project-Repository relationship endpoints
@router.post("/repositories/{repo_id}/projects/{project_id}")
def add_repository_to_project(
    repo_id: int,
    project_id: int,
    service: GitHubRepositoryService = Depends(get_repo_service)
):
    """
    Add a repository to a project
    """
    result = service.add_repository_to_project(repo_id, project_id)
    if not result:
        raise HTTPException(status_code=404, detail="Repository or project not found")
    return {"message": "Repository added to project successfully"}

@router.delete("/repositories/{repo_id}/projects/{project_id}")
def remove_repository_from_project(
    repo_id: int,
    project_id: int,
    service: GitHubRepositoryService = Depends(get_repo_service)
):
    """
    Remove a repository from a project
    """
    result = service.remove_repository_from_project(repo_id, project_id)
    if not result:
        raise HTTPException(status_code=404, detail="Repository or project not found")
    return {"message": "Repository removed from project successfully"}

# Polling endpoints
@router.get("/polling/status", response_model=PollingStatusResponse)
def get_polling_status():
    """
    Get the status of the GitHub polling scheduler
    """
    return github_scheduler.get_status()

@router.post("/polling/start")
def start_polling():
    """
    Start the GitHub polling scheduler
    """
    github_scheduler.start_polling()
    return {"message": "GitHub polling started"}

@router.post("/polling/stop")
def stop_polling():
    """
    Stop the GitHub polling scheduler
    """
    github_scheduler.stop_polling()
    return {"message": "GitHub polling stopped"}

@router.post("/polling/poll-now")
def poll_now(
    service: GitHubRepositoryService = Depends(get_repo_service)
):
    """
    Trigger an immediate poll of GitHub repositories
    """
    # Poll authenticated user's repositories
    try:
        repos = service.poll_user_repositories()
        return {
            "message": "GitHub repositories polled successfully",
            "repositories_updated": len(repos)
        }
    except Exception as e:
        logger.error(f"Error polling repositories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error polling repositories: {str(e)}")

@router.post("/polling/poll-user/{username}")
def poll_user(
    username: str,
    service: GitHubRepositoryService = Depends(get_repo_service)
):
    """
    Poll repositories for a specific user
    """
    try:
        repos = service.poll_user_repositories(username)
        return {
            "message": f"Repositories for user {username} polled successfully",
            "repositories_updated": len(repos)
        }
    except Exception as e:
        logger.error(f"Error polling repositories for user {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error polling repositories: {str(e)}")

@router.post("/polling/poll-organization/{org_name}")
def poll_organization(
    org_name: str,
    service: GitHubRepositoryService = Depends(get_repo_service)
):
    """
    Poll repositories for a specific organization
    """
    try:
        repos = service.poll_organization_repositories(org_name)
        return {
            "message": f"Repositories for organization {org_name} polled successfully",
            "repositories_updated": len(repos)
        }
    except Exception as e:
        logger.error(f"Error polling repositories for organization {org_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error polling repositories: {str(e)}")

# GitHub API rate limit endpoint
@router.get("/rate-limit")
def get_rate_limit():
    """
    Get GitHub API rate limit information
    """
    try:
        rate_limit_info = github_client.get_rate_limit_info()
        return rate_limit_info
    except Exception as e:
        logger.error(f"Error getting rate limit information: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting rate limit information: {str(e)}")