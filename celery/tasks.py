import os
import requests
from celery import Celery
from app import users_collection
from app import database


PYPI_URL = "https://pypi.org/pypi/{}/json"
REDIS_BROKER = os.getenv("REDIS_BROKER", "redis://redis:6379/0")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
celery = Celery("tasks", broker=REDIS_BROKER, backend=REDIS_BROKER)
celery.conf.timezone = "UTC"

@celery.task
async def check_library_updates():
    users = await users_collection.find().to_list(None)  # Fetch all users
    updates_made = False
    
    for user in users:
        email = user.get("email")
        libraries = user.get("libraries", {})  # Get stored libraries
        installed_versions = user.get("versions", {})
        updates = {}
        
        for lib, installed_versions in libraries.items():
            response = requests.get(PYPI_URL.format(lib))
            if response.status_code == 200:
                latest_version = response.json()["info"]["version"]
                if latest_version != installed_versions.get(lib):  # Compare versions
                    updates[lib] = latest_version
        
        if updates:  # If updates exist
            updates_made = True
            installed_versions.update(updates)  # Update installed versions
            await users_collection.update_one(
                {"email": email},
                {"$set": {"installed_versions": installed_versions}}
            )
            send_email(email, updates)  # Send email notification
    return {"message": "Library updates checked", "updates_made": updates_made}