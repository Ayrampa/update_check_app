from celery import Celery
from app.pypi_checker import get_latest_version
from app.database import users_collection
from app.email_sender import send_email
import asyncio

celery = Celery("tasks", broker="redis://redis:6379", backend="redis://redis:6379")

@celery.task
def check_for_updates_task():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check_for_updates())

async def check_for_updates():
    users = await users_collection.find().to_list(100)
    for user in users:
        for library in user["libraries"]:
            latest_version = await get_latest_version(library)
            if latest_version:
                send_email(
                    user["email"],
                    f"Update Available for {library}",
                    f"A new version ({latest_version}) of {library} is available on PyPI."
                )