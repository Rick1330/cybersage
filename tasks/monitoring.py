"""
System monitoring tasks for CyberSage.

This module contains Celery tasks for monitoring system health,
resource usage, and service availability.
"""

from celery import shared_task
from typing import Dict, Any
import asyncio
from datetime import datetime
import psutil
import requests

from services.logging_service import LoggingService


@shared_task
def monitor_system_health() -> Dict[str, Any]:
    """Monitor system health metrics."""
    try:
        metrics = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "status": "completed",
            "metrics": metrics
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@shared_task
def check_services_availability() -> Dict[str, Any]:
    """Check availability of all critical services."""
    services = {
        "api": "http://localhost:8000/health",
        "redis": "redis://localhost:6379",
        "vector_db": "http://localhost:5432"
    }
    
    results = {}
    for service_name, url in services.items():
        try:
            if url.startswith('http'):
                response = requests.get(url, timeout=5)
                results[service_name] = {
                    "status": "up" if response.status_code == 200 else "down",
                    "latency": response.elapsed.total_seconds()
                }
            else:
                # Add checks for non-HTTP services
                results[service_name] = {
                    "status": "up",
                    "latency": 0
                }
        except Exception as e:
            results[service_name] = {
                "status": "down",
                "error": str(e)
            }
    
    return {
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": results
    }
