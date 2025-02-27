from app.celery_config import celery
from app.pypi_updates_checker import get_latest_version
from app.database import users_collection
from app.email_sender import send_email
import asyncio

@celery.task
def check_for_updates_task():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check_for_updates())

async def check_for_updates():
    """Check PyPI for updates for each user's tracked libraries"""
    users = await users_collection.find().to_list(100)

    for user in users:
        email = user["email"]
        libraries = user["libraries"]
        
        updates = []
        for library in libraries:
            latest_version = await get_latest_version(library)
            if latest_version:
                updates.append(f"{library}: {latest_version}")

        if updates:
            body = "The following libraries have new updates available:\n\n" + "\n".join(updates)
            send_email(email, "Library Updates Available", body)