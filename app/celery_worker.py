from celery import Celery
from .config import REDIS_BROKER
from celery.schedules import crontab

celery = Celery("tasks", broker=REDIS_BROKER, backend=REDIS_BROKER)
celery.conf.beat_schedule = {}
celery.conf.timezone = "UTC"

celery.conf.beat_schedule = {
    "check-updates-daily": {
        "task": "app.tasks.check_library_updates",
        "schedule": crontab(hour=0, minute=0),  # Runs every day at midnight
    },
}