import os
import time
import requests
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GitHub API configuration
GITHUB_API_URL = "https://api.github.com"
GITHUB_ENTERPRISE_API_URL = os.getenv("GITHUB_ENTERPRISE_URL", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
POLLING_INTERVAL = int(os.getenv("GITHUB_POLLING_INTERVAL", "600"))  # 10 minutes in seconds

class GitHubClient:
    """
    Client for interacting with GitHub API
    """
    
    def __init__(self, token: Optional[str] = None, enterprise_url: Optional[str] = None):
        """
        Initialize the GitHub client
        
        Args:
            token: GitHub personal access token
            enterprise_url: GitHub Enterprise URL (if applicable)
        """
        self.token = token or GITHUB_TOKEN
        self.enterprise_url = enterprise_url or GITHUB_ENTERPRISE_API_URL
        self.base_url = self.enterprise_url if self.enterprise_url else GITHUB_API_URL
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
        
        # Rate limit tracking
        self.rate_limit_remaining = 5000
        self.rate_limit_reset = 0
        self.last_poll_time = datetime.min
    
    def _make_request(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None) -> Dict:
        """
        Make a request to the GitHub API with rate limit handling
        
        Args:
            endpoint: API endpoint (without base URL)
            method: HTTP method
            params: Query parameters
            data: Request body data
            
        Returns:
            Response data as dictionary
        """
        # Check if we need to wait for rate limit reset
        if self.rate_limit_remaining <= 1:
            reset_time = datetime.fromtimestamp(self.rate_limit_reset)
            now = datetime.now()
            
            if reset_time > now:
                wait_seconds = (reset_time - now).total_seconds() + 1
                logger.info(f"Rate limit reached. Waiting {wait_seconds} seconds until reset.")
                time.sleep(wait_seconds)
        
        # Make the request
        url = f"{self.base_url}{endpoint}"
        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            params=params,
            json=data
        )
        
        # Update rate limit information
        self.rate_limit_remaining = int(response.headers.get("X-RateLimit-Remaining", 5000))
        self.rate_limit_reset = int(response.headers.get("X-RateLimit-Reset", 0))
        
        # Handle response
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 204:
            return {}
        else:
            logger.error(f"GitHub API error: {response.status_code} - {response.text}")
            response.raise_for_status()
    
    def get_user_repositories(self, username: Optional[str] = None) -> List[Dict]:
        """
        Get repositories for a user
        
        Args:
            username: GitHub username (if None, gets authenticated user's repos)
            
        Returns:
            List of repository data
        """
        if username:
            endpoint = f"/users/{username}/repos"
        else:
            endpoint = "/user/repos"
        
        params = {
            "per_page": 100,
            "sort": "updated",
            "direction": "desc"
        }
        
        # Handle pagination
        all_repos = []
        page = 1
        
        while True:
            params["page"] = page
            repos = self._make_request(endpoint, params=params)
            
            if not repos:
                break
                
            all_repos.extend(repos)
            page += 1
            
            # If we got less than 100 repos, we've reached the end
            if len(repos) < 100:
                break
        
        return all_repos
    
    def get_organization_repositories(self, org_name: str) -> List[Dict]:
        """
        Get repositories for an organization
        
        Args:
            org_name: GitHub organization name
            
        Returns:
            List of repository data
        """
        endpoint = f"/orgs/{org_name}/repos"
        
        params = {
            "per_page": 100,
            "sort": "updated",
            "direction": "desc"
        }
        
        # Handle pagination
        all_repos = []
        page = 1
        
        while True:
            params["page"] = page
            repos = self._make_request(endpoint, params=params)
            
            if not repos:
                break
                
            all_repos.extend(repos)
            page += 1
            
            # If we got less than 100 repos, we've reached the end
            if len(repos) < 100:
                break
        
        return all_repos
    
    def get_repository(self, owner: str, repo: str) -> Dict:
        """
        Get a specific repository
        
        Args:
            owner: Repository owner (user or organization)
            repo: Repository name
            
        Returns:
            Repository data
        """
        endpoint = f"/repos/{owner}/{repo}"
        return self._make_request(endpoint)
    
    def can_poll(self) -> bool:
        """
        Check if enough time has passed since the last poll
        
        Returns:
            True if polling is allowed, False otherwise
        """
        now = datetime.now()
        time_since_last_poll = (now - self.last_poll_time).total_seconds()
        return time_since_last_poll >= POLLING_INTERVAL
    
    def update_poll_time(self):
        """
        Update the last poll time to now
        """
        self.last_poll_time = datetime.now()
    
    def get_rate_limit_info(self) -> Dict:
        """
        Get current rate limit information
        
        Returns:
            Rate limit data
        """
        endpoint = "/rate_limit"
        return self._make_request(endpoint)

# Create a singleton instance
github_client = GitHubClient()