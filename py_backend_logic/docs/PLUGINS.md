# Plugin System

This document provides information about the plugin system implemented in the Projection application.

## Overview

The plugin system allows extending the application with custom functionality without modifying the core codebase. Plugins can add new API endpoints, middleware, and hook into various parts of the application.

## Features

- **Dynamic Discovery**: Plugins are automatically discovered at startup
- **Lifecycle Management**: Plugins have well-defined initialization and shutdown phases
- **Configuration**: Plugins can be configured through a central configuration file
- **API Integration**: Plugins can add new API endpoints
- **Hook System**: Plugins can hook into various parts of the application
- **Middleware Support**: Plugins can add custom middleware

## Plugin Structure

A plugin is a Python package with the following structure:

```
plugins/
  example_plugin/
    __init__.py
    other_files.py
```

The `__init__.py` file must contain a class that implements the `PluginInterface`.

## Creating a Plugin

### Basic Plugin Template

```python
from plugin_api import PluginInterface, get_plugin_logger

# Create logger
logger = get_plugin_logger("my_plugin")

class MyPlugin(PluginInterface):
    """
    My custom plugin implementation.
    """
    
    def get_name(self) -> str:
        """Get the name of the plugin."""
        return "my_plugin"
    
    def get_version(self) -> str:
        """Get the version of the plugin."""
        return "1.0.0"
    
    def get_description(self) -> str:
        """Get the description of the plugin."""
        return "My custom plugin"
    
    def initialize(self, app, config):
        """Initialize the plugin."""
        logger.info(f"Initializing {self.get_name()} plugin")
        # Plugin initialization code here
        return True
    
    def shutdown(self):
        """Perform cleanup when the plugin is being shut down."""
        logger.info(f"Shutting down {self.get_name()} plugin")
        # Plugin cleanup code here
```

### Adding API Endpoints

Plugins can add new API endpoints using FastAPI's router:

```python
def initialize(self, app, config):
    # Create router
    self.router = APIRouter(prefix=f"/api/plugins/{self.get_name()}", tags=["plugins"])
    
    # Add routes
    self.router.add_api_route("/", self.get_info, methods=["GET"])
    self.router.add_api_route("/custom", self.custom_endpoint, methods=["POST"])
    
    # Include router in app
    app.include_router(self.router)
    
    return True

async def get_info(self):
    """Get information about the plugin."""
    return {
        "name": self.get_name(),
        "version": self.get_version(),
        "description": self.get_description()
    }

async def custom_endpoint(self, data: dict):
    """Custom endpoint implementation."""
    logger.info(f"Custom endpoint called with data: {data}")
    return {"result": "success", "data": data}
```

### Adding Hooks

Plugins can provide hooks that are called at specific points in the application:

```python
def get_hooks(self):
    """Get the hooks provided by this plugin."""
    return {
        "before_request": self.before_request_hook,
        "after_request": self.after_request_hook,
        "process_document": self.process_document_hook
    }

def before_request_hook(self, request):
    """Hook that runs before processing a request."""
    logger.debug(f"Before request hook called for {request.url.path}")
    return True

def after_request_hook(self, request, response):
    """Hook that runs after processing a request."""
    logger.debug(f"After request hook called for {request.url.path}")
    return True

def process_document_hook(self, document):
    """Hook that processes a document."""
    logger.debug(f"Processing document: {document.get('filename', 'unknown')}")
    # Modify document here
    return document
```

### Adding Middleware

Plugins can add custom middleware:

```python
def initialize(self, app, config):
    # Register middleware
    @app.middleware("http")
    async def plugin_middleware(request, call_next):
        # Only process requests to this plugin's endpoints
        if request.url.path.startswith(f"/api/plugins/{self.get_name()}"):
            # Process request
            response = await call_next(request)
            # Modify response
            response.headers["X-Plugin"] = f"{self.get_name()} v{self.get_version()}"
            return response
        else:
            # Pass through for other requests
            return await call_next(request)
    
    return True
```

## Plugin API

The plugin API provides a clean interface for plugins to access core functionality:

### Logging

```python
from plugin_api import get_plugin_logger

# Create a logger for your plugin
logger = get_plugin_logger("my_plugin")

# Log at different levels
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### Metrics

```python
from plugin_api import record_plugin_metric

# Record a custom metric
record_plugin_metric(
    category="plugins",
    name="my_plugin_event",
    value=42,
    tags={"type": "example"}
)
```

### Accessing Metrics

```python
from plugin_api import get_metrics_snapshot

# Get metrics snapshot
snapshot = get_metrics_snapshot()

# Access plugin-specific metrics
plugin_metrics = snapshot.get("custom_metrics", {}).get("plugins", {})
```

## Plugin Configuration

Plugins can be configured through a central configuration file (`plugin_config.json`):

```json
{
  "example_plugin": {
    "greeting": "Hello from the example plugin!",
    "enabled": true
  },
  "my_plugin": {
    "custom_setting": "value",
    "max_items": 100
  }
}
```

Access configuration in the plugin:

```python
def initialize(self, app, config):
    # Store configuration
    self.config = config
    self.custom_setting = config.get("custom_setting", "default")
    self.max_items = config.get("max_items", 50)
    
    logger.info(f"Plugin configured with: {self.custom_setting}, {self.max_items}")
    return True
```

## Enabling and Disabling Plugins

The plugin system can be enabled or disabled through environment variables:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `PLUGINS_ENABLED` | Enable/disable the plugin system | `true` |
| `PLUGINS_DIR` | Directory for plugins | `plugins` |
| `PLUGIN_CONFIG_FILE` | Plugin configuration file | `plugin_config.json` |

## Example Plugin

An example plugin is provided in `plugin_example.py`. To use it:

1. Create a directory in the `plugins` folder (e.g., `example_plugin`)
2. Copy the file to that directory as `__init__.py`
3. Restart the application

## Best Practices

1. **Use the Plugin API**: Always use the plugin API rather than importing directly from core modules
2. **Handle Errors Gracefully**: Catch and log exceptions to prevent plugin failures from affecting the core application
3. **Clean Up Resources**: Implement the `shutdown` method to clean up resources when the plugin is being shut down
4. **Document Your Plugin**: Provide clear documentation for your plugin
5. **Version Your Plugin**: Use semantic versioning for your plugin
6. **Test Your Plugin**: Write tests for your plugin to ensure it works correctly
7. **Respect Performance**: Be mindful of performance implications, especially in hooks that are called frequently