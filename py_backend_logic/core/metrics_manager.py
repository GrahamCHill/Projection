import time
import threading
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
import statistics
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
from dotenv import load_dotenv

from core.logging_manager import get_logger

# Load environment variables
load_dotenv()

# Configure metrics settings
METRICS_ENABLED = os.getenv("METRICS_ENABLED", "true").lower() == "true"
METRICS_RETENTION_MINUTES = int(os.getenv("METRICS_RETENTION_MINUTES", "60"))
METRICS_SNAPSHOT_INTERVAL_SECONDS = int(os.getenv("METRICS_SNAPSHOT_INTERVAL_SECONDS", "60"))
METRICS_DIR = Path(os.getenv("METRICS_DIR", "metrics"))
METRICS_DIR.mkdir(exist_ok=True)

# Create logger
logger = get_logger("metrics")

class MetricsManager:
    """
    Manages application metrics collection and reporting.
    """
    
    def __init__(self):
        """Initialize the metrics manager."""
        self.enabled = METRICS_ENABLED
        self.retention_period = timedelta(minutes=METRICS_RETENTION_MINUTES)
        self.snapshot_interval = METRICS_SNAPSHOT_INTERVAL_SECONDS
        
        # Metrics storage
        self._request_metrics = deque(maxlen=10000)  # Store up to 10,000 requests
        self._endpoint_metrics = defaultdict(lambda: defaultdict(list))  # path -> method -> metrics list
        self._exception_metrics = defaultdict(lambda: defaultdict(int))  # path -> exception_type -> count
        self._custom_metrics = defaultdict(lambda: defaultdict(list))  # category -> name -> values list
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Start background tasks if enabled
        if self.enabled:
            self._start_background_tasks()
            logger.info("Metrics collection enabled")
        else:
            logger.info("Metrics collection disabled")
    
    def _start_background_tasks(self):
        """Start background tasks for metrics processing."""
        # Start metrics cleanup thread
        cleanup_thread = threading.Thread(target=self._cleanup_old_metrics, daemon=True)
        cleanup_thread.start()
        
        # Start metrics snapshot thread
        snapshot_thread = threading.Thread(target=self._periodic_snapshot, daemon=True)
        snapshot_thread.start()
    
    def _cleanup_old_metrics(self):
        """Periodically clean up old metrics data."""
        while True:
            try:
                cutoff_time = datetime.now() - self.retention_period
                
                with self._lock:
                    # Clean up request metrics
                    while self._request_metrics and self._request_metrics[0]["timestamp"] < cutoff_time:
                        self._request_metrics.popleft()
                    
                    # Clean up endpoint metrics
                    for path in list(self._endpoint_metrics.keys()):
                        for method in list(self._endpoint_metrics[path].keys()):
                            self._endpoint_metrics[path][method] = [
                                m for m in self._endpoint_metrics[path][method]
                                if m["timestamp"] >= cutoff_time
                            ]
                            if not self._endpoint_metrics[path][method]:
                                del self._endpoint_metrics[path][method]
                        if not self._endpoint_metrics[path]:
                            del self._endpoint_metrics[path]
                    
                    # Clean up custom metrics
                    for category in list(self._custom_metrics.keys()):
                        for name in list(self._custom_metrics[category].keys()):
                            self._custom_metrics[category][name] = [
                                m for m in self._custom_metrics[category][name]
                                if m["timestamp"] >= cutoff_time
                            ]
                            if not self._custom_metrics[category][name]:
                                del self._custom_metrics[category][name]
                        if not self._custom_metrics[category]:
                            del self._custom_metrics[category]
                
                # Sleep for 5 minutes
                time.sleep(300)
            except Exception as e:
                logger.exception(f"Error in metrics cleanup: {str(e)}")
                time.sleep(60)  # Sleep for 1 minute on error
    
    def _periodic_snapshot(self):
        """Periodically save a snapshot of current metrics."""
        while True:
            try:
                # Sleep first to allow metrics to accumulate
                time.sleep(self.snapshot_interval)
                
                # Generate snapshot
                snapshot = self.get_metrics_snapshot()
                
                # Save snapshot to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                snapshot_file = METRICS_DIR / f"metrics_snapshot_{timestamp}.json"
                
                with open(snapshot_file, "w") as f:
                    json.dump(snapshot, f, indent=2)
                
                # Keep only the last 24 snapshots (assuming 1 per hour)
                snapshot_files = sorted(METRICS_DIR.glob("metrics_snapshot_*.json"))
                if len(snapshot_files) > 24:
                    for old_file in snapshot_files[:-24]:
                        old_file.unlink()
                
            except Exception as e:
                logger.exception(f"Error in metrics snapshot: {str(e)}")
                time.sleep(60)  # Sleep for 1 minute on error
    
    def record_request(self, method: str, path: str, status_code: int, duration: float):
        """
        Record metrics for an HTTP request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            status_code: HTTP status code
            duration: Request duration in seconds
        """
        if not self.enabled:
            return
        
        timestamp = datetime.now()
        
        with self._lock:
            # Add to request metrics
            self._request_metrics.append({
                "timestamp": timestamp,
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration": duration
            })
            
            # Add to endpoint metrics
            self._endpoint_metrics[path][method].append({
                "timestamp": timestamp,
                "status_code": status_code,
                "duration": duration
            })
    
    def record_exception(self, method: str, path: str, exception_type: str):
        """
        Record metrics for an exception.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            exception_type: Type of exception
        """
        if not self.enabled:
            return
        
        with self._lock:
            # Increment exception counter
            self._exception_metrics[path][exception_type] += 1
    
    def record_custom_metric(self, category: str, name: str, value: Any, tags: Optional[Dict[str, str]] = None):
        """
        Record a custom metric.
        
        Args:
            category: Metric category (e.g., 'database', 'cache', 'external_api')
            name: Metric name (e.g., 'query_time', 'cache_hit', 'api_latency')
            value: Metric value
            tags: Optional tags for the metric
        """
        if not self.enabled:
            return
        
        timestamp = datetime.now()
        
        with self._lock:
            self._custom_metrics[category][name].append({
                "timestamp": timestamp,
                "value": value,
                "tags": tags or {}
            })
    
    def get_metrics_snapshot(self) -> Dict[str, Any]:
        """
        Get a snapshot of current metrics.
        
        Returns:
            Dictionary containing metrics data
        """
        if not self.enabled:
            return {"enabled": False}
        
        with self._lock:
            # Calculate request rate (requests per minute)
            now = datetime.now()
            one_minute_ago = now - timedelta(minutes=1)
            five_minutes_ago = now - timedelta(minutes=5)
            fifteen_minutes_ago = now - timedelta(minutes=15)
            
            requests_last_minute = sum(1 for r in self._request_metrics if r["timestamp"] >= one_minute_ago)
            requests_last_5min = sum(1 for r in self._request_metrics if r["timestamp"] >= five_minutes_ago)
            requests_last_15min = sum(1 for r in self._request_metrics if r["timestamp"] >= fifteen_minutes_ago)
            
            # Calculate error rate
            error_requests_last_minute = sum(
                1 for r in self._request_metrics 
                if r["timestamp"] >= one_minute_ago and r["status_code"] >= 400
            )
            error_requests_last_5min = sum(
                1 for r in self._request_metrics 
                if r["timestamp"] >= five_minutes_ago and r["status_code"] >= 400
            )
            
            # Calculate endpoint statistics
            endpoint_stats = {}
            for path, methods in self._endpoint_metrics.items():
                endpoint_stats[path] = {}
                for method, metrics in methods.items():
                    recent_metrics = [m for m in metrics if m["timestamp"] >= five_minutes_ago]
                    if not recent_metrics:
                        continue
                    
                    durations = [m["duration"] for m in recent_metrics]
                    status_codes = [m["status_code"] for m in recent_metrics]
                    
                    endpoint_stats[path][method] = {
                        "count": len(recent_metrics),
                        "avg_duration": statistics.mean(durations) if durations else 0,
                        "min_duration": min(durations) if durations else 0,
                        "max_duration": max(durations) if durations else 0,
                        "p95_duration": statistics.quantiles(durations, n=20)[18] if len(durations) >= 20 else max(durations) if durations else 0,
                        "status_codes": {
                            "2xx": sum(1 for s in status_codes if 200 <= s < 300),
                            "3xx": sum(1 for s in status_codes if 300 <= s < 400),
                            "4xx": sum(1 for s in status_codes if 400 <= s < 500),
                            "5xx": sum(1 for s in status_codes if 500 <= s < 600),
                        }
                    }
            
            # Prepare exception statistics
            exception_stats = {}
            for path, exceptions in self._exception_metrics.items():
                exception_stats[path] = {
                    exception_type: count for exception_type, count in exceptions.items()
                }
            
            # Prepare custom metrics statistics
            custom_metrics_stats = {}
            for category, metrics in self._custom_metrics.items():
                custom_metrics_stats[category] = {}
                for name, values in metrics.items():
                    recent_values = [m for m in values if m["timestamp"] >= five_minutes_ago]
                    if not recent_values:
                        continue
                    
                    # Extract numeric values for statistics
                    numeric_values = []
                    for m in recent_values:
                        try:
                            if isinstance(m["value"], (int, float)):
                                numeric_values.append(m["value"])
                        except (TypeError, ValueError):
                            pass
                    
                    stats = {
                        "count": len(recent_values),
                        "last_value": recent_values[-1]["value"] if recent_values else None,
                        "last_timestamp": recent_values[-1]["timestamp"].isoformat() if recent_values else None,
                    }
                    
                    # Add numeric statistics if available
                    if numeric_values:
                        stats.update({
                            "avg": statistics.mean(numeric_values),
                            "min": min(numeric_values),
                            "max": max(numeric_values),
                        })
                        if len(numeric_values) >= 2:
                            stats["stddev"] = statistics.stdev(numeric_values)
                    
                    custom_metrics_stats[category][name] = stats
            
            # Build the complete snapshot
            return {
                "timestamp": now.isoformat(),
                "enabled": self.enabled,
                "request_rate": {
                    "per_minute": requests_last_minute,
                    "per_5min": requests_last_5min / 5,
                    "per_15min": requests_last_15min / 15,
                },
                "error_rate": {
                    "per_minute": error_requests_last_minute / max(requests_last_minute, 1),
                    "per_5min": error_requests_last_5min / max(requests_last_5min, 1),
                },
                "endpoints": endpoint_stats,
                "exceptions": exception_stats,
                "custom_metrics": custom_metrics_stats,
            }
    
    def get_recent_requests(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get the most recent requests.
        
        Args:
            limit: Maximum number of requests to return
            
        Returns:
            List of recent request metrics
        """
        if not self.enabled:
            return []
        
        with self._lock:
            # Convert deque to list and get the most recent entries
            recent_requests = list(self._request_metrics)[-limit:]
            
            # Convert datetime objects to ISO format strings for JSON serialization
            for request in recent_requests:
                request["timestamp"] = request["timestamp"].isoformat()
            
            return recent_requests

# Create a singleton instance
metrics_manager = MetricsManager()