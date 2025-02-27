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

# from celery import Celery
# import aiohttp
# from database import users_collection

# celery = Celery("tasks", broker="redis://redis:6379/0")

# async def fetch_latest_version(library: str):
#     """Fetch latest version from PyPI."""
#     url = f"https://pypi.org/pypi/{library}/json"
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url) as response:
#             if response.status == 200:
#                 data = await response.json()
#                 return data["info"]["version"]
#             return None

# @celery.task
# def check_library_updates(email: str):
#     """Check for updates and send email if needed."""
#     import asyncio
#     loop = asyncio.get_event_loop()

#     user = loop.run_until_complete(users_collection.find_one({"email": email}))
#     if not user:
#         return

#     libraries = user.get("libraries", [])
#     updates = {}

#     async def check():
#         tasks = [fetch_latest_version(lib) for lib in libraries]
#         results = await asyncio.gather(*tasks)
#         for lib, version in zip(libraries, results):
#             updates[lib] = version

#     loop.run_until_complete(check())

#     # Simulate sending email
#     if updates:
#         print(f"Sending email to {email} with updates: {updates}")

# celery.conf.beat_schedule = {
#     "check_for_updates_weekly": {
#         "task": "app.task.check_for_updates_task",
#         "schedule": 604800.0,  # Run once a week (in seconds)
#         }
#     }