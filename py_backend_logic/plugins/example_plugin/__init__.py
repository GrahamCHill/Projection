"""
Example Plugin

This is an example plugin that demonstrates the plugin architecture.
It provides a simple API endpoint and hooks into the application.
"""

from fastapi import APIRouter, Request, Response
from typing import Dict, Any, List, Callable
import time

# Import from the plugin API
import sys
import os
from pathlib import Path

# Add parent directory to path to import the plugin API
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from plugin_api import PluginInterface, get_plugin_logger, record_plugin_metric, get_metrics_snapshot

# Create logger
logger = get_plugin_logger("example_plugin")

class ExamplePlugin(PluginInterface):
    """
    Example plugin implementation.
    """
    
    def get_name(self) -> str:
        """Get the name of the plugin."""
        return "example_plugin"
    
    def get_version(self) -> str:
        """Get the version of the plugin."""
        return "1.0.0"
    
    def get_description(self) -> str:
        """Get the description of the plugin."""
        return "An example plugin that demonstrates the plugin architecture"
    
    def initialize(self, app: Any, config: Dict[str, Any]) -> bool:
        """
        Initialize the plugin.
        
        Args:
            app: The FastAPI application instance
            config: Plugin configuration
            
        Returns:
            True if initialization was successful, False otherwise
        """
        logger.info(f"Initializing {self.get_name()} plugin")
        
        # Store configuration
        self.config = config
        self.greeting = config.get("greeting", "Hello from the example plugin!")
        
        # Create router
        self.router = APIRouter(prefix="/api/plugins/example", tags=["plugins"])
        
        # Add routes
        self.router.add_api_route("/", self.get_info, methods=["GET"])
        self.router.add_api_route("/greeting", self.get_greeting, methods=["GET"])
        self.router.add_api_route("/metrics", self.get_metrics, methods=["GET"])
        
        # Include router in app
        app.include_router(self.router)
        
        # Register middleware
        @app.middleware("http")
        async def example_plugin_middleware(request: Request, call_next: Callable):
            # Only process requests to this plugin's endpoints
            if request.url.path.startswith("/api/plugins/example"):
                # Record start time
                start_time = time.time()
                
                # Process request
                response = await call_next(request)
                
                # Record processing time
                process_time = time.time() - start_time
                
                # Add custom header
                response.headers["X-Example-Plugin"] = f"v{self.get_version()}"
                
                # Record custom metric
                record_plugin_metric(
                    category="plugins",
                    name="example_plugin_request",
                    value=process_time,
                    tags={"path": request.url.path}
                )
                
                return response
            else:
                # Pass through for other requests
                return await call_next(request)
        
        logger.info(f"{self.get_name()} plugin initialized successfully")
        return True
    
    def shutdown(self) -> None:
        """Perform cleanup when the plugin is being shut down."""
        logger.info(f"Shutting down {self.get_name()} plugin")
    
    def get_hooks(self) -> Dict[str, Callable]:
        """
        Get the hooks provided by this plugin.
        
        Returns:
            Dictionary mapping hook names to handler functions
        """
        return {
            "before_request": self.before_request_hook,
            "after_request": self.after_request_hook,
            "process_document": self.process_document_hook
        }
    
    # API endpoints
    
    async def get_info(self):
        """Get information about the plugin."""
        logger.info("Plugin info requested")
        return {
            "name": self.get_name(),
            "version": self.get_version(),
            "description": self.get_description()
        }
    
    async def get_greeting(self):
        """Get the configured greeting."""
        logger.info("Plugin greeting requested")
        return {"greeting": self.greeting}
    
    async def get_metrics(self):
        """Get plugin-specific metrics."""
        logger.info("Plugin metrics requested")
        return {
            "requests_processed": get_metrics_snapshot().get("custom_metrics", {}).get("plugins", {}).get("example_plugin_request", {}).get("count", 0)
        }
    
    # Hook implementations
    
    def before_request_hook(self, request: Request):
        """
        Hook that runs before processing a request.
        
        Args:
            request: The incoming request
        """
        logger.debug(f"Before request hook called for {request.url.path}")
        return True
    
    def after_request_hook(self, request: Request, response: Response):
        """
        Hook that runs after processing a request.
        
        Args:
            request: The incoming request
            response: The outgoing response
        """
        logger.debug(f"After request hook called for {request.url.path}")
        return True
    
    def process_document_hook(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hook that processes a document.
        
        Args:
            document: The document to process
            
        Returns:
            The processed document
        """
        logger.debug(f"Processing document: {document.get('filename', 'unknown')}")
        
        # Add a tag from the plugin
        if "tags" not in document:
            document["tags"] = []
        
        document["tags"].append("processed_by_example_plugin")
        
        return document