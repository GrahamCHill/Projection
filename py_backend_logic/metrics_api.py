from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Any, Optional
import os
from pathlib import Path
import json
from datetime import datetime

from metrics_manager import metrics_manager
from logging_manager import get_logger, logging_manager

# Create logger
logger = get_logger("metrics_api")

# Create router
router = APIRouter(prefix="/api/metrics", tags=["metrics"])

@router.get("/status")
async def get_metrics_status():
    """Get the current status of metrics collection."""
    logging_manager.set_component("metrics_api")
    logger.info("Metrics status requested")
    
    return {
        "enabled": metrics_manager.enabled,
        "retention_minutes": metrics_manager.retention_period.total_seconds() / 60,
        "snapshot_interval_seconds": metrics_manager.snapshot_interval
    }

@router.get("/snapshot")
async def get_current_metrics_snapshot():
    """Get a snapshot of current metrics."""
    logging_manager.set_component("metrics_api")
    logger.info("Current metrics snapshot requested")
    
    if not metrics_manager.enabled:
        return {"enabled": False, "message": "Metrics collection is disabled"}
    
    return metrics_manager.get_metrics_snapshot()

@router.get("/snapshots")
async def list_metrics_snapshots():
    """List available metrics snapshots."""
    logging_manager.set_component("metrics_api")
    logger.info("Metrics snapshots list requested")
    
    metrics_dir = Path(os.getenv("METRICS_DIR", "metrics"))
    if not metrics_dir.exists():
        return {"snapshots": []}
    
    snapshot_files = sorted(metrics_dir.glob("metrics_snapshot_*.json"))
    snapshots = []
    
    for snapshot_file in snapshot_files:
        try:
            timestamp = snapshot_file.stem.replace("metrics_snapshot_", "")
            snapshots.append({
                "filename": snapshot_file.name,
                "timestamp": timestamp,
                "size_bytes": snapshot_file.stat().st_size
            })
        except Exception as e:
            logger.error(f"Error processing snapshot file {snapshot_file}: {str(e)}")
    
    return {"snapshots": snapshots}

@router.get("/snapshots/{filename}")
async def get_metrics_snapshot(filename: str):
    """Get a specific metrics snapshot by filename."""
    logging_manager.set_component("metrics_api")
    logger.info(f"Metrics snapshot requested: {filename}")
    
    metrics_dir = Path(os.getenv("METRICS_DIR", "metrics"))
    snapshot_file = metrics_dir / filename
    
    if not snapshot_file.exists():
        logger.warning(f"Snapshot file not found: {filename}")
        raise HTTPException(status_code=404, detail="Snapshot not found")
    
    try:
        with open(snapshot_file, "r") as f:
            snapshot_data = json.load(f)
        return snapshot_data
    except Exception as e:
        logger.error(f"Error reading snapshot file {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error reading snapshot: {str(e)}")

@router.get("/requests")
async def get_recent_requests(
    limit: int = Query(100, ge=1, le=1000),
    path: Optional[str] = None,
    method: Optional[str] = None,
    min_status: Optional[int] = None,
    max_status: Optional[int] = None
):
    """
    Get recent requests with optional filtering.
    
    Args:
        limit: Maximum number of requests to return (1-1000)
        path: Filter by request path (exact match)
        method: Filter by HTTP method (GET, POST, etc.)
        min_status: Minimum status code (inclusive)
        max_status: Maximum status code (inclusive)
    """
    logging_manager.set_component("metrics_api")
    logger.info(f"Recent requests requested (limit={limit}, filters applied: {bool(path or method or min_status or max_status)})")
    
    if not metrics_manager.enabled:
        return {"enabled": False, "message": "Metrics collection is disabled", "requests": []}
    
    # Get recent requests
    recent_requests = metrics_manager.get_recent_requests(limit=1000)  # Get more than needed for filtering
    
    # Apply filters
    if path:
        recent_requests = [r for r in recent_requests if r["path"] == path]
    
    if method:
        recent_requests = [r for r in recent_requests if r["method"].upper() == method.upper()]
    
    if min_status is not None:
        recent_requests = [r for r in recent_requests if r["status_code"] >= min_status]
    
    if max_status is not None:
        recent_requests = [r for r in recent_requests if r["status_code"] <= max_status]
    
    # Apply limit after filtering
    recent_requests = recent_requests[-limit:]
    
    return {"requests": recent_requests}

@router.get("/endpoints")
async def get_endpoint_metrics():
    """Get metrics for all endpoints."""
    logging_manager.set_component("metrics_api")
    logger.info("Endpoint metrics requested")
    
    if not metrics_manager.enabled:
        return {"enabled": False, "message": "Metrics collection is disabled"}
    
    snapshot = metrics_manager.get_metrics_snapshot()
    return {"endpoints": snapshot.get("endpoints", {})}

@router.get("/endpoints/{path}")
async def get_endpoint_metrics_by_path(path: str):
    """Get metrics for a specific endpoint path."""
    logging_manager.set_component("metrics_api")
    logger.info(f"Endpoint metrics requested for path: {path}")
    
    if not metrics_manager.enabled:
        return {"enabled": False, "message": "Metrics collection is disabled"}
    
    snapshot = metrics_manager.get_metrics_snapshot()
    endpoints = snapshot.get("endpoints", {})
    
    # Find the closest matching path
    matching_path = None
    for endpoint_path in endpoints:
        if endpoint_path == path:
            matching_path = endpoint_path
            break
        elif path in endpoint_path:
            matching_path = endpoint_path
    
    if not matching_path:
        logger.warning(f"No metrics found for path: {path}")
        raise HTTPException(status_code=404, detail="No metrics found for this path")
    
    return {"path": matching_path, "metrics": endpoints[matching_path]}

@router.get("/exceptions")
async def get_exception_metrics():
    """Get exception metrics."""
    logging_manager.set_component("metrics_api")
    logger.info("Exception metrics requested")
    
    if not metrics_manager.enabled:
        return {"enabled": False, "message": "Metrics collection is disabled"}
    
    snapshot = metrics_manager.get_metrics_snapshot()
    return {"exceptions": snapshot.get("exceptions", {})}

@router.get("/custom")
async def get_custom_metrics(category: Optional[str] = None):
    """
    Get custom metrics.
    
    Args:
        category: Optional category to filter by
    """
    logging_manager.set_component("metrics_api")
    logger.info(f"Custom metrics requested (category={category})")
    
    if not metrics_manager.enabled:
        return {"enabled": False, "message": "Metrics collection is disabled"}
    
    snapshot = metrics_manager.get_metrics_snapshot()
    custom_metrics = snapshot.get("custom_metrics", {})
    
    if category:
        return {"category": category, "metrics": custom_metrics.get(category, {})}
    else:
        return {"custom_metrics": custom_metrics}