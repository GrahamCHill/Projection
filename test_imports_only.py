"""
This script tests only the imports without trying to connect to the database.
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
    
    # Import specific components from main without initializing the database
    import importlib.util
    spec = importlib.util.spec_from_file_location("main_module", 
                                                 os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                                             "py_backend_logic/main.py"))
    main_module = importlib.util.module_from_spec(spec)
    
    # Patch the init_db function to return None instead of connecting to the database
    import py_backend_logic.core.database
    original_init_db = py_backend_logic.core.database.init_db
    py_backend_logic.core.database.init_db = lambda: None
    
    # Now we can safely execute the module
    try:
        spec.loader.exec_module(main_module)
        print("✓ Successfully imported main module without database initialization")
    finally:
        # Restore the original init_db function
        py_backend_logic.core.database.init_db = original_init_db
    
    print("\nAll imports successful! The Docker import path issue has been fixed.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")