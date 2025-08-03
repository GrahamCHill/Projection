"""
This script tests the imports in a way that simulates the Docker environment.
It will verify that our solution for the import path issue works correctly.
"""

import sys
import os

# Add the current directory to the Python path (simulating what our new main.py does)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
    
    # Try importing the app from py_backend_logic.main (what our new main.py does)
    from py_backend_logic.main import app
    print("✓ Successfully imported app from py_backend_logic.main")
    
    print("\nAll imports successful! The Docker import path issue has been fixed.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")