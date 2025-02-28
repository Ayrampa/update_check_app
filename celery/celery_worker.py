from celery import Celery
import os
from celery.schedules import crontab

REDIS_BROKER = os.getenv("REDIS_BROKER", "redis://redis:6379/0")

celery = Celery("tasks", broker=REDIS_BROKER, backend=REDIS_BROKER)
celery.conf.beat_schedule = {}
celery.conf.timezone = "UTC"

celery.conf.beat_schedule = {
    "check-updates-daily": {
        "task": "app.tasks.check_library_updates",
        "schedule": crontab(hour=0, minute=0),  # Runs every day at midnight
    },
}





import beetschedule
from celery_worker import add

scheduler = beetschedule.Scheduler()

@scheduler.schedule(beetschedule.every(10).seconds)
def scheduled_task():
    print("Running scheduled task...")
    add.apply_async(args=[5, 10])  # Schedule Celery task

if __name__ == "__main__":
    scheduler.run()
