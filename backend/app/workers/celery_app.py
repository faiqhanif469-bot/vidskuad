"""
Celery Application Configuration
"""

from celery import Celery
from app.config import settings

# Create Celery app
celery_app = Celery(
    "ai_video_production",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        'app.workers.tasks.pipeline_task',
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.JOB_TIMEOUT_MINUTES * 60,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Task routes (assign tasks to specific queues)
celery_app.conf.task_routes = {
    'app.workers.tasks.pipeline_task.*': {'queue': 'default'},
}

if __name__ == '__main__':
    celery_app.start()
