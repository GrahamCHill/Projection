import logging
import json
import sys
import os
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from functools import wraps
from contextvars import ContextVar
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging directory
LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
LOG_DIR.mkdir(exist_ok=True)

# Configure log levels from environment
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
CONSOLE_LOG_LEVEL = os.getenv("CONSOLE_LOG_LEVEL", LOG_LEVEL).upper()
FILE_LOG_LEVEL = os.getenv("FILE_LOG_LEVEL", LOG_LEVEL).upper()

# Configure log file rotation
MAX_LOG_SIZE_MB = int(os.getenv("MAX_LOG_SIZE_MB", "10"))
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))

# Context variables for request tracking
request_id_var: ContextVar[str] = ContextVar('request_id', default='')
user_id_var: ContextVar[str] = ContextVar('user_id', default='')
component_var: ContextVar[str] = ContextVar('component', default='')

class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the log record.
    """
    def __init__(self, **kwargs):
        self.fmt_dict = kwargs

    def format(self, record):
        record_dict = self._prepare_log_dict(record)
        return json.dumps(record_dict)

    def _prepare_log_dict(self, record):
        record_dict = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add request context if available
        request_id = request_id_var.get()
        if request_id:
            record_dict["request_id"] = request_id
            
        user_id = user_id_var.get()
        if user_id:
            record_dict["user_id"] = user_id
            
        component = component_var.get()
        if component:
            record_dict["component"] = component
        
        # Add exception info if available
        if record.exc_info:
            record_dict["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
            
        # Add custom fields from the fmt_dict
        for key, value in self.fmt_dict.items():
            record_dict[key] = value
            
        # Add any custom fields from the record
        for key, value in record.__dict__.items():
            if key not in ["args", "exc_info", "exc_text", "msg", "message", "stack_info"] and not key.startswith("_"):
                if key == "extra" and isinstance(value, dict):
                    for extra_key, extra_value in value.items():
                        record_dict[extra_key] = extra_value
                else:
                    record_dict[key] = value
                    
        return record_dict

class LoggingManager:
    """
    Manages logging configuration and provides logging utilities.
    """
    def __init__(self):
        self.loggers = {}
        self.setup_root_logger()
        
    def setup_root_logger(self):
        """Configure the root logger with console and file handlers."""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)  # Capture all logs
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Add console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, CONSOLE_LOG_LEVEL))
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # Add JSON file handler
        json_file_handler = logging.FileHandler(LOG_DIR / "app.json.log")
        json_file_handler.setLevel(getattr(logging, FILE_LOG_LEVEL))
        json_formatter = JsonFormatter()
        json_file_handler.setFormatter(json_formatter)
        root_logger.addHandler(json_file_handler)
        
        # Add regular file handler
        file_handler = logging.FileHandler(LOG_DIR / "app.log")
        file_handler.setLevel(getattr(logging, FILE_LOG_LEVEL))
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger with the specified name.
        
        Args:
            name: The name of the logger
            
        Returns:
            A configured logger instance
        """
        if name not in self.loggers:
            logger = logging.getLogger(name)
            self.loggers[name] = logger
        return self.loggers[name]
    
    @staticmethod
    def set_request_context(request_id: Optional[str] = None, user_id: Optional[str] = None):
        """
        Set the request context for the current execution context.
        
        Args:
            request_id: The ID of the current request
            user_id: The ID of the current user
        """
        if request_id:
            request_id_var.set(request_id)
        else:
            request_id_var.set(str(uuid.uuid4()))
            
        if user_id:
            user_id_var.set(str(user_id))
    
    @staticmethod
    def set_component(component_name: str):
        """
        Set the component name for the current execution context.
        
        Args:
            component_name: The name of the current component
        """
        component_var.set(component_name)
    
    @staticmethod
    def clear_context():
        """Clear the current request context."""
        request_id_var.set('')
        user_id_var.set('')
        component_var.set('')
    
    @staticmethod
    def log_execution_time(logger: logging.Logger):
        """
        Decorator to log the execution time of a function.
        
        Args:
            logger: The logger to use
            
        Returns:
            Decorated function
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                execution_time = end_time - start_time
                logger.info(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
                return result
            return wrapper
        return decorator

# Create a singleton instance
logging_manager = LoggingManager()

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: The name of the logger
        
    Returns:
        A configured logger instance
    """
    return logging_manager.get_logger(name)