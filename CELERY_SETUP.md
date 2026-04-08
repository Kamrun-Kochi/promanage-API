# Celery + Redis Setup for ProManage

This document explains how to run the Celery workers and Redis for the ProManage project.

## Prerequisites

1. **Redis Server** must be installed and running
   - Download from: https://redis.io/download
   - Or use Docker: `docker run -d -p 6379:6379 redis`

## Running the Application

### Step 1: Start Redis
```bash
# On Windows (if installed locally)
redis-server

# On macOS with Homebrew
brew services start redis

# Or use Docker
docker run -d -p 6379:6379 redis
```

### Step 2: Start Celery Worker
```bash
# Basic worker (single process)
celery -A core worker -l INFO

# Worker with multiple processes (for production)
celery -A core worker -l INFO --concurrency=4

# Worker with specific queue
celery -A core worker -l INFO -Q default
```

### Step 3: Start Celery Beat (for scheduled tasks)
```bash
celery -A core beat -l INFO
```

### Step 4: Run Django Development Server
```bash
python manage.py runserver
```

## Available Celery Tasks

### Projects App
- `apps.projects.tasks.send_task_assignment_email` - Send email when task is assigned
- `apps.projects.tasks.send_task_status_update_email` - Send email when task status changes
- `apps.projects.tasks.send_daily_task_summary` - Daily task summary (runs at 8 AM)
- `apps.projects.tasks.check_overdue_tasks` - Check for overdue tasks (runs hourly)
- `apps.projects.tasks.generate_project_report` - Generate project report in background

### Users App
- `apps.users.tasks.send_welcome_email` - Send welcome email to new users
- `apps.users.tasks.send_password_reset_email` - Send password reset email
- `apps.users.tasks.cleanup_inactive_users` - Clean up inactive users

### Common App
- `apps.common.tasks.cleanup_old_logs` - Clean up old log entries (runs at midnight)
- `apps.common.tasks.clear_cache` - Clear Redis cache
- `apps.common.tasks.health_check` - Health check task
- `apps.common.tasks.send_bulk_notification` - Send notification to multiple users

## Testing Celery

### Test from Django Shell
```bash
python manage.py shell
```

Then run:
```python
from apps.projects.tasks import send_task_assignment_email

# Test task
result = send_task_assignment_email.delay(
    task_id=1,
    user_email='test@example.com',
    task_title='Test Task',
    project_title='Test Project'
)

# Check result
print(result.id)  # Task ID
print(result.status)  # Task status: PENDING, SUCCESS, FAILURE
```

### Test using curl
```bash
# Health check
curl -X POST http://localhost:8000/api/celery/health/
```

## Scheduled Tasks (Celery Beat)

The following tasks are scheduled automatically:

| Task | Schedule |
|------|----------|
| Daily Task Summary | Every day at 8:00 AM |
| Check Overdue Tasks | Every hour |
| Cleanup Old Logs | Every day at midnight |

## Troubleshooting

### Redis Connection Error
```
Error: Cannot connect to 'redis://localhost:6379/0'
```
**Solution**: Make sure Redis is running: `redis-cli ping` should return `PONG`

### Worker Not Processing Tasks
**Solution**: Restart the worker:
```bash
# Kill existing workers
celery -A core control shutdown

# Start fresh
celery -A core worker -l INFO
```

### View Celery Results
```bash
celery -A core events  # Monitor events in real-time
celery -A core inspect active  # View active tasks
celery -A core inspect scheduled  # View scheduled tasks
```

## Environment Variables

Add these to your `.env` file:
```
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

## Production Deployment

For production, consider:
1. Use a process manager (Supervisor, systemd)
2. Run multiple workers for load balancing
3. Use Redis Sentinel for high availability
4. Monitor with Flower: `celery -A core flower`
