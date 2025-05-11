"""
Celery configuration for scheduled tasks and async job processing.

This module sets up Celery with Redis as the broker and result backend,
configuring periodic tasks and worker settings.
"""

from celery import Celery
from celery.schedules import crontab
import yaml
import os

# Load configuration
with open("configs/settings.yaml") as f:
    config = yaml.safe_load(f)

# Initialize Celery
celery_app = Celery(
    'cybersage',
    broker=config['services']['redis']['url'],
    backend=config['services']['redis']['url']
)

# Celery Configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    worker_max_tasks_per_child=200,
    broker_connection_retry_on_startup=True
)

# Configure scheduled tasks
celery_app.conf.beat_schedule = {
    'daily-vulnerability-scan': {
        'task': 'tasks.security.run_vulnerability_scan',
        'schedule': crontab(hour=2, minute=0),  # Run at 2 AM
        'args': (['high', 'critical'],),
    },
    'hourly-threat-intel-update': {
        'task': 'tasks.security.update_threat_intel',
        'schedule': crontab(minute=0),  # Run every hour
    },
    'weekly-security-report': {
        'task': 'tasks.reporting.generate_security_report',
        'schedule': crontab(day_of_week='monday', hour=6, minute=0),
    },
}

# Include task modules
celery_app.autodiscover_tasks([
    'tasks.security',
    'tasks.reporting',
    'tasks.monitoring'
])
