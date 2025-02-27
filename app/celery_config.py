from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery = Celery(
    "task",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.task"]
)

celery.conf.beat_schedule = {
    "check_for_updates_weekly": {
        "task": "app.task.check_for_updates_task",
        "schedule": 604800.0,  # Run once a week (in seconds)
    }
}

celery.conf.timezone = "UTC"