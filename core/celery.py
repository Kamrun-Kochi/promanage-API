"""
Celery configuration for ProManage project.

This file configures Celery to use Redis as the message broker
and result backend for async task processing.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Create the Celery app
app = Celery('promanage_api')

# Load config from Django settings with CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()


# ====================
# CELERY BEAT SCHEDULE
# ====================
# Configure periodic tasks using Celery Beat
app.conf.beat_schedule = {
    # Send daily task summary at 8 AM every day
    'daily-task-summary': {
        'task': 'apps.projects.tasks.send_daily_task_summary',
        'schedule': crontab(hour=8, minute=0),
    },
    
    # Check for overdue tasks every hour
    'check-overdue-tasks': {
        'task': 'apps.projects.tasks.check_overdue_tasks',
        'schedule': crontab(minute=0),  # Every hour
    },
    
    # Clean up old task logs every day at midnight
    'cleanup-old-logs': {
        'task': 'apps.common.tasks.cleanup_old_logs',
        'schedule': crontab(hour=0, minute=0),  # Midnight
    },
}


# ====================
# CELERY CONFIGURATION
# ====================
# Timezone
app.conf.timezone = 'UTC'

# Fix deprecation warning for Celery 6.0+
app.conf.broker_connection_retry_on_startup = True

# Result backend (where task results are stored)
app.conf.result_backend = 'redis://localhost:6379/1'

# Task serialization
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']

# Task execution settings
app.conf.task_acks_late = True  # Acknowledge after task completes
app.conf.task_reject_on_worker_lost = True  # Requeue if worker dies
app.conf.worker_prefetch_multiplier = 4  # Prefetch tasks for efficiency

# Task routes for different queues
app.conf.task_routes = {
    'apps.projects.tasks.*': {'queue': 'projects'},
    'apps.users.tasks.*': {'queue': 'users'},
    'apps.common.tasks.*': {'queue': 'default'},
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to test Celery is working."""
    print(f'Request: {self.request!r}')
