"""
Plugin API

This module provides a clean interface for plugins to access core functionality.
Plugins should import from this module rather than directly importing from other modules.
"""

from typing import Dict, Any, List, Optional, Callable
import abc

# Re-export components needed by plugins
from plugin_system import PluginInterface
from logging_manager import get_logger, logging_manager
from metrics_manager import metrics_manager

# Define plugin API version
__version__ = "1.0.0"

class PluginAPI:
    """
    API for plugins to access core functionality.
    """
    
    @staticmethod
    def get_logger(name: str):
        """
        Get a logger with the specified name.
        
        Args:
            name: The name of the logger
            
        Returns:
            A configured logger instance
        """
        return get_logger(name)
    
    @staticmethod
    def record_metric(category: str, name: str, value: Any, tags: Optional[Dict[str, str]] = None):
        """
        Record a custom metric.
        
        Args:
            category: Metric category (e.g., 'plugins', 'database')
            name: Metric name
            value: Metric value
            tags: Optional tags for the metric
        """
        metrics_manager.record_custom_metric(category, name, value, tags)
    
    @staticmethod
    def set_logging_context(component: str, request_id: Optional[str] = None, user_id: Optional[str] = None):
        """
        Set the logging context.
        
        Args:
            component: The component name
            request_id: Optional request ID
            user_id: Optional user ID
        """
        logging_manager.set_component(component)
        if request_id or user_id:
            logging_manager.set_request_context(request_id, user_id)
    
    @staticmethod
    def clear_logging_context():
        """Clear the current logging context."""
        logging_manager.clear_context()

# Create a singleton instance
plugin_api = PluginAPI()

# Add metrics snapshot access
@staticmethod
def get_metrics_snapshot():
    """
    Get a snapshot of current metrics.
    
    Returns:
        Dictionary containing metrics data
    """
    return metrics_manager.get_metrics_snapshot()

# Add this method to the PluginAPI class
PluginAPI.get_metrics_snapshot = get_metrics_snapshot

# For backwards compatibility
get_plugin_logger = plugin_api.get_logger
record_plugin_metric = plugin_api.record_metric
get_metrics_snapshot = plugin_api.get_metrics_snapshot