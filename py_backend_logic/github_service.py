import logging
from typing import List, Dict, Optional, Union, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from github_models import GitHubRepository, RepositoryTag, RepositoryProject
from github_client import github_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubRepositoryService:
    """
    Service for managing GitHub repositories in the database
    """
    
    def __init__(self, db: Session):
        """
        Initialize the service with a database session
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def create_repository(self, repo_data: Dict[str, Any]) -> GitHubRepository:
        """
        Create a new repository record from GitHub API data
        
        Args:
            repo_data: Repository data from GitHub API
            
        Returns:
            Created repository object
        """
        try:
            # Check if repository already exists
            existing_repo = self.db.query(GitHubRepository).filter_by(
                full_name=repo_data.get("full_name")
            ).first()
            
            if existing_repo:
                # Update existing repository
                existing_repo.name = repo_data.get("name")
                existing_repo.url = repo_data.get("url")
                existing_repo.html_url = repo_data.get("html_url")
                existing_repo.description = repo_data.get("description")
                existing_repo.is_private = repo_data.get("private", False)
                existing_repo.owner_name = repo_data.get("owner", {}).get("login")
                existing_repo.owner_type = repo_data.get("owner", {}).get("type")
                existing_repo.last_polled = datetime.utcnow()
                existing_repo.updated_at = datetime.utcnow()
                
                self.db.commit()
                logger.info(f"Updated repository: {existing_repo.full_name}")
                return existing_repo
            
            # Create new repository
            new_repo = GitHubRepository(
                name=repo_data.get("name"),
                full_name=repo_data.get("full_name"),
                url=repo_data.get("url"),
                html_url=repo_data.get("html_url"),
                description=repo_data.get("description"),
                is_private=repo_data.get("private", False),
                owner_name=repo_data.get("owner", {}).get("login"),
                owner_type=repo_data.get("owner", {}).get("type"),
                last_polled=datetime.utcnow()
            )
            
            self.db.add(new_repo)
            self.db.commit()
            self.db.refresh(new_repo)
            
            logger.info(f"Created repository: {new_repo.full_name}")
            return new_repo
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating repository: {str(e)}")
            raise
    
    def get_repository(self, repo_id: int) -> Optional[GitHubRepository]:
        """
        Get a repository by ID
        
        Args:
            repo_id: Repository ID
            
        Returns:
            Repository object or None if not found
        """
        return self.db.query(GitHubRepository).filter_by(id=repo_id).first()
    
    def get_repository_by_full_name(self, full_name: str) -> Optional[GitHubRepository]:
        """
        Get a repository by full name (owner/repo)
        
        Args:
            full_name: Repository full name
            
        Returns:
            Repository object or None if not found
        """
        return self.db.query(GitHubRepository).filter_by(full_name=full_name).first()
    
    def list_repositories(self, skip: int = 0, limit: int = 100) -> List[GitHubRepository]:
        """
        List repositories with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of repository objects
        """
        return self.db.query(GitHubRepository).order_by(
            GitHubRepository.updated_at.desc()
        ).offset(skip).limit(limit).all()
    
    def delete_repository(self, repo_id: int) -> bool:
        """
        Delete a repository by ID
        
        Args:
            repo_id: Repository ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            repo = self.get_repository(repo_id)
            if not repo:
                return False
                
            self.db.delete(repo)
            self.db.commit()
            logger.info(f"Deleted repository: {repo.full_name}")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error deleting repository: {str(e)}")
            raise
    
    def create_tag(self, name: str, description: Optional[str] = None, color: str = "#CCCCCC") -> RepositoryTag:
        """
        Create a new tag
        
        Args:
            name: Tag name
            description: Tag description
            color: Tag color (hex code)
            
        Returns:
            Created tag object
        """
        try:
            # Check if tag already exists
            existing_tag = self.db.query(RepositoryTag).filter_by(name=name).first()
            
            if existing_tag:
                # Update existing tag
                existing_tag.description = description
                existing_tag.color = color
                existing_tag.updated_at = datetime.utcnow()
                
                self.db.commit()
                logger.info(f"Updated tag: {existing_tag.name}")
                return existing_tag
            
            # Create new tag
            new_tag = RepositoryTag(
                name=name,
                description=description,
                color=color
            )
            
            self.db.add(new_tag)
            self.db.commit()
            self.db.refresh(new_tag)
            
            logger.info(f"Created tag: {new_tag.name}")
            return new_tag
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating tag: {str(e)}")
            raise
    
    def get_tag(self, tag_id: int) -> Optional[RepositoryTag]:
        """
        Get a tag by ID
        
        Args:
            tag_id: Tag ID
            
        Returns:
            Tag object or None if not found
        """
        return self.db.query(RepositoryTag).filter_by(id=tag_id).first()
    
    def get_tag_by_name(self, name: str) -> Optional[RepositoryTag]:
        """
        Get a tag by name
        
        Args:
            name: Tag name
            
        Returns:
            Tag object or None if not found
        """
        return self.db.query(RepositoryTag).filter_by(name=name).first()
    
    def list_tags(self) -> List[RepositoryTag]:
        """
        List all tags
        
        Returns:
            List of tag objects
        """
        return self.db.query(RepositoryTag).order_by(RepositoryTag.name).all()
    
    def delete_tag(self, tag_id: int) -> bool:
        """
        Delete a tag by ID
        
        Args:
            tag_id: Tag ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            tag = self.get_tag(tag_id)
            if not tag:
                return False
                
            self.db.delete(tag)
            self.db.commit()
            logger.info(f"Deleted tag: {tag.name}")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error deleting tag: {str(e)}")
            raise
    
    def create_project(self, name: str, description: Optional[str] = None) -> RepositoryProject:
        """
        Create a new project
        
        Args:
            name: Project name
            description: Project description
            
        Returns:
            Created project object
        """
        try:
            # Check if project already exists
            existing_project = self.db.query(RepositoryProject).filter_by(name=name).first()
            
            if existing_project:
                # Update existing project
                existing_project.description = description
                existing_project.updated_at = datetime.utcnow()
                
                self.db.commit()
                logger.info(f"Updated project: {existing_project.name}")
                return existing_project
            
            # Create new project
            new_project = RepositoryProject(
                name=name,
                description=description
            )
            
            self.db.add(new_project)
            self.db.commit()
            self.db.refresh(new_project)
            
            logger.info(f"Created project: {new_project.name}")
            return new_project
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating project: {str(e)}")
            raise
    
    def get_project(self, project_id: int) -> Optional[RepositoryProject]:
        """
        Get a project by ID
        
        Args:
            project_id: Project ID
            
        Returns:
            Project object or None if not found
        """
        return self.db.query(RepositoryProject).filter_by(id=project_id).first()
    
    def list_projects(self) -> List[RepositoryProject]:
        """
        List all projects
        
        Returns:
            List of project objects
        """
        return self.db.query(RepositoryProject).order_by(RepositoryProject.name).all()
    
    def delete_project(self, project_id: int) -> bool:
        """
        Delete a project by ID
        
        Args:
            project_id: Project ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            project = self.get_project(project_id)
            if not project:
                return False
                
            self.db.delete(project)
            self.db.commit()
            logger.info(f"Deleted project: {project.name}")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error deleting project: {str(e)}")
            raise
    
    def add_tag_to_repository(self, repo_id: int, tag_id: int) -> bool:
        """
        Add a tag to a repository
        
        Args:
            repo_id: Repository ID
            tag_id: Tag ID
            
        Returns:
            True if added, False if repository or tag not found
        """
        try:
            repo = self.get_repository(repo_id)
            tag = self.get_tag(tag_id)
            
            if not repo or not tag:
                return False
                
            if tag not in repo.tags:
                repo.tags.append(tag)
                self.db.commit()
                logger.info(f"Added tag {tag.name} to repository {repo.full_name}")
                
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error adding tag to repository: {str(e)}")
            raise
    
    def remove_tag_from_repository(self, repo_id: int, tag_id: int) -> bool:
        """
        Remove a tag from a repository
        
        Args:
            repo_id: Repository ID
            tag_id: Tag ID
            
        Returns:
            True if removed, False if repository or tag not found
        """
        try:
            repo = self.get_repository(repo_id)
            tag = self.get_tag(tag_id)
            
            if not repo or not tag:
                return False
                
            if tag in repo.tags:
                repo.tags.remove(tag)
                self.db.commit()
                logger.info(f"Removed tag {tag.name} from repository {repo.full_name}")
                
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error removing tag from repository: {str(e)}")
            raise
    
    def add_repository_to_project(self, repo_id: int, project_id: int) -> bool:
        """
        Add a repository to a project
        
        Args:
            repo_id: Repository ID
            project_id: Project ID
            
        Returns:
            True if added, False if repository or project not found
        """
        try:
            repo = self.get_repository(repo_id)
            project = self.get_project(project_id)
            
            if not repo or not project:
                return False
                
            if project not in repo.projects:
                repo.projects.append(project)
                self.db.commit()
                logger.info(f"Added repository {repo.full_name} to project {project.name}")
                
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error adding repository to project: {str(e)}")
            raise
    
    def remove_repository_from_project(self, repo_id: int, project_id: int) -> bool:
        """
        Remove a repository from a project
        
        Args:
            repo_id: Repository ID
            project_id: Project ID
            
        Returns:
            True if removed, False if repository or project not found
        """
        try:
            repo = self.get_repository(repo_id)
            project = self.get_project(project_id)
            
            if not repo or not project:
                return False
                
            if project in repo.projects:
                repo.projects.remove(project)
                self.db.commit()
                logger.info(f"Removed repository {repo.full_name} from project {project.name}")
                
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error removing repository from project: {str(e)}")
            raise
    
    def poll_user_repositories(self, username: Optional[str] = None) -> List[GitHubRepository]:
        """
        Poll repositories for a user and update the database
        
        Args:
            username: GitHub username (if None, gets authenticated user's repos)
            
        Returns:
            List of updated repository objects
        """
        if not github_client.can_poll():
            logger.info("Skipping poll due to rate limiting")
            return []
            
        try:
            # Get repositories from GitHub API
            repos_data = github_client.get_user_repositories(username)
            
            # Update poll time
            github_client.update_poll_time()
            
            # Update repositories in database
            updated_repos = []
            for repo_data in repos_data:
                repo = self.create_repository(repo_data)
                updated_repos.append(repo)
                
            logger.info(f"Polled {len(updated_repos)} repositories for user {username or 'authenticated user'}")
            return updated_repos
            
        except Exception as e:
            logger.error(f"Error polling user repositories: {str(e)}")
            raise
    
    def poll_organization_repositories(self, org_name: str) -> List[GitHubRepository]:
        """
        Poll repositories for an organization and update the database
        
        Args:
            org_name: GitHub organization name
            
        Returns:
            List of updated repository objects
        """
        if not github_client.can_poll():
            logger.info("Skipping poll due to rate limiting")
            return []
            
        try:
            # Get repositories from GitHub API
            repos_data = github_client.get_organization_repositories(org_name)
            
            # Update poll time
            github_client.update_poll_time()
            
            # Update repositories in database
            updated_repos = []
            for repo_data in repos_data:
                repo = self.create_repository(repo_data)
                updated_repos.append(repo)
                
            logger.info(f"Polled {len(updated_repos)} repositories for organization {org_name}")
            return updated_repos
            
        except Exception as e:
            logger.error(f"Error polling organization repositories: {str(e)}")
            raise