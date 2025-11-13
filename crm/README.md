# CRM Application - Celery Setup Guide

This guide provides instructions for setting up and running Celery with Celery Beat for automated task scheduling in the CRM application.

## Overview

The CRM application uses Celery for asynchronous task execution and Celery Beat for periodic task scheduling. The system includes:

- **Celery Worker**: Executes background tasks
- **Celery Beat**: Schedules periodic tasks (e.g., weekly reports)
- **Redis**: Message broker and result backend

## Prerequisites

- Python 3.8+
- Redis server
- Django project configured and running

## Installation Steps

### 1. Install Redis

#### macOS (using Homebrew)
```bash
brew install redis
brew services start redis
```

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

#### Windows
Download and install Redis from: https://github.com/microsoftarchive/redis/releases

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `celery==5.4.0`
- `redis==5.2.1`
- `django-celery-beat==2.7.0`

### 3. Run Database Migrations

The `django-celery-beat` app requires database tables for storing periodic task schedules:

```bash
python manage.py migrate
```

## Running Celery

### Start the Celery Worker

Open a terminal and run:

```bash
celery -A crm worker -l info
```

Options:
- `-A crm`: Specifies the Celery app location
- `worker`: Runs the worker process
- `-l info`: Sets logging level to INFO

### Start Celery Beat

Open another terminal and run:

```bash
celery -A crm beat -l info
```

Options:
- `-A crm`: Specifies the Celery app location
- `beat`: Runs the beat scheduler
- `-l info`: Sets logging level to INFO

### Run Both Worker and Beat Together (Development Only)

For development, you can run both in a single process:

```bash
celery -A crm worker --beat -l info
```

**Note**: This is not recommended for production use.

## Scheduled Tasks

### Weekly CRM Report

**Task**: `generate_crm_report`
**Schedule**: Every Monday at 6:00 AM
**Description**: Generates a report summarizing:
- Total number of customers
- Total number of orders
- Total revenue

**Log File**: `/tmp/crm_report_log.txt`

**Example Log Entry**:
```
2025-01-13 06:00:00 - Report: 45 customers, 120 orders, $15234.50 revenue
```

## Verifying Setup

### 1. Check Redis Connection

```bash
redis-cli ping
```

Expected output: `PONG`

### 2. Check Celery Worker Status

After starting the worker, you should see:
```
[tasks]
  . crm.tasks.generate_crm_report
```

### 3. Check Celery Beat Status

After starting beat, you should see:
```
Scheduler: Starting...
DatabaseScheduler: Schedule changed.
```

### 4. Verify Log Files

Check that the report is being generated:

```bash
tail -f /tmp/crm_report_log.txt
```

## Testing the Report Task Manually

You can manually trigger the report task without waiting for the schedule:

```python
# In Django shell
python manage.py shell

from crm.tasks import generate_crm_report
result = generate_crm_report.delay()
print(result.id)
```

Or using Celery command:

```bash
celery -A crm call crm.tasks.generate_crm_report
```

## Configuration

### Celery Settings (in settings.py)

```python
# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    'generate-crm-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(day_of_week='mon', hour=6, minute=0),
    },
}
```

## Production Deployment

For production, use a process manager like **Supervisor** or **systemd** to manage Celery processes.

### Example Supervisor Configuration

Create `/etc/supervisor/conf.d/celery.conf`:

```ini
[program:celery_worker]
command=/path/to/venv/bin/celery -A crm worker -l info
directory=/path/to/project
user=www-data
numprocs=1
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker.log
autostart=true
autorestart=true
startsecs=10

[program:celery_beat]
command=/path/to/venv/bin/celery -A crm beat -l info
directory=/path/to/project
user=www-data
numprocs=1
stdout_logfile=/var/log/celery/beat.log
stderr_logfile=/var/log/celery/beat.log
autostart=true
autorestart=true
startsecs=10
```

Then:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start celery_worker
sudo supervisorctl start celery_beat
```

## Troubleshooting

### Redis Connection Error

**Error**: `Error while connecting to Redis`

**Solution**:
1. Verify Redis is running: `redis-cli ping`
2. Check Redis URL in settings.py
3. Ensure Redis is accessible on port 6379

### Task Not Executing

**Possible Causes**:
1. Celery worker not running
2. Task not registered (check worker startup logs)
3. Beat scheduler not running

**Debug Steps**:
```bash
# Check Celery worker logs
celery -A crm worker -l debug

# Check Beat scheduler logs
celery -A crm beat -l debug
```

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'crm.celery'`

**Solution**: Ensure `crm/__init__.py` imports the Celery app:
```python
from .celery import app as celery_app
__all__ = ('celery_app',)
```

## Additional Resources

- [Celery Documentation](https://docs.celeryproject.org/)
- [Django-Celery-Beat Documentation](https://django-celery-beat.readthedocs.io/)
- [Redis Documentation](https://redis.io/documentation)

## Support

For issues or questions, refer to the project documentation or contact the development team.
