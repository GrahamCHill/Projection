# Logging and Metrics System

This document provides information about the logging and metrics system implemented in the Projection application.

## Logging System

The application includes a comprehensive logging system that provides structured logging with different log levels, context tracking, and multiple output formats.

### Features

- **Structured Logging**: Logs are structured with consistent fields for easier parsing and analysis
- **JSON Format**: Logs can be output in JSON format for machine readability
- **Context Tracking**: Request IDs, user IDs, and component names are tracked across the application
- **Multiple Output Destinations**: Logs can be sent to console and files
- **Configurable Log Levels**: Different log levels can be set for different outputs

### Configuration

Logging is configured through environment variables:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `LOG_LEVEL` | Overall log level | `INFO` |
| `CONSOLE_LOG_LEVEL` | Console log level | Same as `LOG_LEVEL` |
| `FILE_LOG_LEVEL` | File log level | Same as `LOG_LEVEL` |
| `LOG_DIR` | Directory for log files | `logs` |
| `MAX_LOG_SIZE_MB` | Maximum log file size | `10` |
| `LOG_BACKUP_COUNT` | Number of backup log files | `5` |

### Usage

#### Basic Logging

```python
from logging_manager import get_logger

# Create a logger for your module
logger = get_logger("my_module")

# Log at different levels
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")

# Log with exception information
try:
    # Some code that might raise an exception
    result = 1 / 0
except Exception as e:
    logger.exception("An error occurred")
```

#### Context Tracking

```python
from logging_manager import logging_manager

# Set the component name
logging_manager.set_component("my_component")

# Set request context
logging_manager.set_request_context(request_id="123", user_id="456")

# Log with context
logger.info("This log will include component and request information")

# Clear context when done
logging_manager.clear_context()
```

#### Performance Logging

```python
from logging_manager import logging_manager, get_logger

logger = get_logger("performance")

# Use the decorator to log execution time
@logging_manager.log_execution_time(logger)
def my_function():
    # Function code here
    pass
```

## Metrics System

The application includes a metrics collection and reporting system that tracks request/response metrics, performance metrics, and custom metrics.

### Features

- **Request Metrics**: Track HTTP request counts, durations, and status codes
- **Endpoint Metrics**: Collect statistics for each endpoint
- **Exception Tracking**: Monitor exceptions by type and endpoint
- **Custom Metrics**: Record application-specific metrics
- **Automatic Cleanup**: Old metrics are automatically removed
- **Periodic Snapshots**: Metrics snapshots are saved periodically
- **API Access**: Metrics can be accessed through API endpoints

### Configuration

Metrics are configured through environment variables:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `METRICS_ENABLED` | Enable/disable metrics collection | `true` |
| `METRICS_RETENTION_MINUTES` | How long to keep metrics | `60` |
| `METRICS_SNAPSHOT_INTERVAL_SECONDS` | How often to save snapshots | `60` |
| `METRICS_DIR` | Directory for metrics snapshots | `metrics` |

### Usage

#### Recording Custom Metrics

```python
from metrics_manager import metrics_manager

# Record a simple metric
metrics_manager.record_custom_metric(
    category="database",
    name="query_time",
    value=0.123,
    tags={"table": "users", "operation": "select"}
)

# Record a non-numeric metric
metrics_manager.record_custom_metric(
    category="cache",
    name="status",
    value="hit",
    tags={"key": "user_profile"}
)
```

#### Accessing Metrics

```python
from metrics_manager import metrics_manager

# Get a snapshot of all metrics
snapshot = metrics_manager.get_metrics_snapshot()

# Get recent requests
recent_requests = metrics_manager.get_recent_requests(limit=10)
```

### API Endpoints

The following API endpoints are available for accessing metrics:

- `GET /api/metrics/status`: Get the current status of metrics collection
- `GET /api/metrics/snapshot`: Get a snapshot of current metrics
- `GET /api/metrics/snapshots`: List available metrics snapshots
- `GET /api/metrics/snapshots/{filename}`: Get a specific metrics snapshot
- `GET /api/metrics/requests`: Get recent requests with optional filtering
- `GET /api/metrics/endpoints`: Get metrics for all endpoints
- `GET /api/metrics/endpoints/{path}`: Get metrics for a specific endpoint
- `GET /api/metrics/exceptions`: Get exception metrics
- `GET /api/metrics/custom`: Get custom metrics

## Integration with FastAPI

The logging and metrics systems are integrated with FastAPI through middleware:

```python
from fastapi import FastAPI
from middleware import LoggingMiddleware, MetricsMiddleware
from metrics_manager import metrics_manager

app = FastAPI()

# Add logging middleware
app.add_middleware(
    LoggingMiddleware,
    exclude_paths=["/api/health", "/api/metrics"]
)

# Add metrics middleware
app.add_middleware(
    MetricsMiddleware,
    metrics_manager=metrics_manager,
    exclude_paths=["/api/health", "/api/metrics"]
)
```

## Best Practices

1. **Create Module-Specific Loggers**: Use `get_logger("module_name")` to create loggers for each module
2. **Use Appropriate Log Levels**: Use the right log level for each message
3. **Include Context**: Set component and request context for better traceability
4. **Add Structured Information**: Use the `extra` parameter to add structured information to logs
5. **Monitor Metrics**: Regularly check metrics to identify performance issues
6. **Record Custom Metrics**: Add custom metrics for application-specific events
7. **Clean Up**: The systems automatically clean up old data, but be mindful of disk usage