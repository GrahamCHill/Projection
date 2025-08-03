import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable, Optional

from core.logging_manager import logging_manager, get_logger

# Create a logger for the middleware
logger = get_logger("middleware")

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    """
    
    def __init__(
        self, 
        app: ASGIApp,
        exclude_paths: Optional[list] = None
    ):
        """
        Initialize the middleware.
        
        Args:
            app: The ASGI application
            exclude_paths: List of paths to exclude from logging (e.g., ["/metrics", "/health"])
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or []
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and log information about it.
        
        Args:
            request: The incoming request
            call_next: The next middleware or route handler
            
        Returns:
            The response from the next middleware or route handler
        """
        # Skip logging for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Generate request ID if not present
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Set request context
        logging_manager.set_request_context(request_id=request_id)
        
        # Extract user ID from request if available
        user_id = None
        if hasattr(request.state, "user") and hasattr(request.state.user, "id"):
            user_id = request.state.user.id
            logging_manager.set_request_context(user_id=user_id)
        
        # Log request
        start_time = time.time()
        
        # Prepare request info for logging
        request_info = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client": request.client.host if request.client else None,
            "headers": dict(request.headers),
        }
        
        # Remove sensitive information from headers
        if "authorization" in request_info["headers"]:
            request_info["headers"]["authorization"] = "[REDACTED]"
            
        logger.info(f"Request started: {request.method} {request.url.path}", extra={"request": request_info})
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add custom header with request processing time
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id
            
            # Log response
            status_code = response.status_code
            response_info = {
                "request_id": request_id,
                "status_code": status_code,
                "process_time": process_time,
                "headers": dict(response.headers),
            }
            
            log_message = f"Request completed: {request.method} {request.url.path} - {status_code} in {process_time:.4f}s"
            
            # Log at appropriate level based on status code
            if status_code >= 500:
                logger.error(log_message, extra={"response": response_info})
            elif status_code >= 400:
                logger.warning(log_message, extra={"response": response_info})
            else:
                logger.info(log_message, extra={"response": response_info})
                
            return response
            
        except Exception as e:
            # Log exceptions
            process_time = time.time() - start_time
            logger.exception(
                f"Request failed: {request.method} {request.url.path} after {process_time:.4f}s",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "process_time": process_time,
                    "error": str(e),
                }
            )
            raise
        finally:
            # Clear request context
            logging_manager.clear_context()


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware for collecting metrics about HTTP requests.
    """
    
    def __init__(
        self, 
        app: ASGIApp,
        metrics_manager,
        exclude_paths: Optional[list] = None
    ):
        """
        Initialize the middleware.
        
        Args:
            app: The ASGI application
            metrics_manager: The metrics manager instance
            exclude_paths: List of paths to exclude from metrics (e.g., ["/metrics", "/health"])
        """
        super().__init__(app)
        self.metrics_manager = metrics_manager
        self.exclude_paths = exclude_paths or []
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and collect metrics about it.
        
        Args:
            request: The incoming request
            call_next: The next middleware or route handler
            
        Returns:
            The response from the next middleware or route handler
        """
        # Skip metrics for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Start timer
        start_time = time.time()
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Record metrics
            self.metrics_manager.record_request(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=time.time() - start_time
            )
            
            return response
            
        except Exception as e:
            # Record exception metrics
            self.metrics_manager.record_exception(
                method=request.method,
                path=request.url.path,
                exception_type=type(e).__name__
            )
            raise