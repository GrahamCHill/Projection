"""
This script tests only the imports without trying to connect to the database.
It will verify that our import path fixes are working correctly.
"""

# Try importing the modules that were previously causing errors
try:
    from py_backend_logic.core.logging_manager import get_logger, logging_manager
    print("✓ Successfully imported logging_manager")
    
    from py_backend_logic.core.metrics_manager import metrics_manager
    print("✓ Successfully imported metrics_manager")
    
    from py_backend_logic.core.middleware import LoggingMiddleware, MetricsMiddleware
    print("✓ Successfully imported middleware")
    
    from py_backend_logic.plugins.plugin_system import plugin_manager
    print("✓ Successfully imported plugin_system")
    
    print("\nAll imports successful! The import path issues have been fixed.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")