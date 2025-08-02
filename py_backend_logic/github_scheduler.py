import logging
import os
from typing import List, Optional
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.base import JobLookupError
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from database import get_session
from github_service import GitHubRepositoryService
from github_client import github_client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GitHub polling configuration
POLLING_INTERVAL = int(os.getenv("GITHUB_POLLING_INTERVAL", "600"))  # 10 minutes in seconds
GITHUB_USERS = os.getenv("GITHUB_USERS", "").split(",")
GITHUB_ORGANIZATIONS = os.getenv("GITHUB_ORGANIZATIONS", "").split(",")

class GitHubPollingScheduler:
    """
    Scheduler for polling GitHub repositories at regular intervals
    """
    
    def __init__(self):
        """
        Initialize the scheduler
        """
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.polling_job = None
        logger.info("GitHub polling scheduler initialized")
    
    def start_polling(self):
        """
        Start the polling job
        """
        if self.polling_job:
            logger.info("Polling job already running")
            return
            
        # Create a polling job that runs every POLLING_INTERVAL seconds
        self.polling_job = self.scheduler.add_job(
            self._poll_repositories,
            trigger=IntervalTrigger(seconds=POLLING_INTERVAL),
            id='github_polling',
            name='Poll GitHub Repositories',
            replace_existing=True
        )
        
        logger.info(f"Started GitHub polling job (interval: {POLLING_INTERVAL} seconds)")
        
        # Run the job immediately
        self._poll_repositories()
    
    def stop_polling(self):
        """
        Stop the polling job
        """
        if not self.polling_job:
            logger.info("No polling job running")
            return
            
        try:
            self.scheduler.remove_job('github_polling')
            self.polling_job = None
            logger.info("Stopped GitHub polling job")
        except JobLookupError:
            logger.error("Failed to stop polling job: Job not found")
    
    def _poll_repositories(self):
        """
        Poll repositories from configured users and organizations
        """
        logger.info("Polling GitHub repositories...")
        
        # Check if we can poll (rate limiting)
        if not github_client.can_poll():
            logger.info("Skipping poll due to rate limiting")
            return
        
        try:
            # Create a new session for this job
            db = get_session()
            service = GitHubRepositoryService(db)
            
            # Poll authenticated user's repositories
            try:
                service.poll_user_repositories()
            except Exception as e:
                logger.error(f"Error polling authenticated user's repositories: {str(e)}")
            
            # Poll specific users' repositories
            for username in GITHUB_USERS:
                if username.strip():
                    try:
                        service.poll_user_repositories(username.strip())
                    except Exception as e:
                        logger.error(f"Error polling repositories for user {username}: {str(e)}")
            
            # Poll organizations' repositories
            for org_name in GITHUB_ORGANIZATIONS:
                if org_name.strip():
                    try:
                        service.poll_organization_repositories(org_name.strip())
                    except Exception as e:
                        logger.error(f"Error polling repositories for organization {org_name}: {str(e)}")
            
            logger.info("GitHub repository polling completed")
            
        except Exception as e:
            logger.error(f"Error during repository polling: {str(e)}")
        finally:
            # Close the session
            if 'db' in locals():
                db.close()
    
    def get_status(self):
        """
        Get the status of the polling scheduler
        
        Returns:
            dict: Status information
        """
        next_run_time = None
        if self.polling_job:
            next_run_time = self.polling_job.next_run_time.isoformat() if self.polling_job.next_run_time else None
            
        return {
            "is_running": self.polling_job is not None,
            "polling_interval": POLLING_INTERVAL,
            "next_run_time": next_run_time,
            "configured_users": GITHUB_USERS,
            "configured_organizations": GITHUB_ORGANIZATIONS,
            "rate_limit_remaining": github_client.rate_limit_remaining,
            "rate_limit_reset": datetime.fromtimestamp(github_client.rate_limit_reset).isoformat() if github_client.rate_limit_reset else None
        }
    
    def shutdown(self):
        """
        Shutdown the scheduler
        """
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("GitHub polling scheduler shutdown")

# Create a singleton instance
github_scheduler = GitHubPollingScheduler()