import os
import requests

from celery.schedules import crontab
from motor.motor_asyncio import AsyncIOMotorClient
from celery import Celery
from app import users_collection
from app import database

# export EMAIL_HOST="smtp.example.com"
# export EMAIL_PORT=587
# export EMAIL_USER="your-email@example.com"
# export EMAIL_PASSWORD="your-email-password"

########################################################################################################
''' Celery tasks '''

# Environment variables and configurations
REDIS_BROKER = os.getenv("REDIS_BROKER", "redis://redis:6379/0")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
#MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
PYPI_URL = "https://pypi.org/pypi/{}/json"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.example.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER", "your-email@example.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your-email-password")



def send_email(recipient, updates):
    """Send an email notification about library updates."""
    subject = "Library Updates Available"
    body = "The following libraries have updates:\n\n"
    body += "\n".join([f"{lib}: {version}" for lib, version in updates.items()])
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = recipient
    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, recipient, msg.as_string())
    except Exception as e:
        print(f"Failed to send email to {recipient}: {e}")



# Schedule task every 15 minutes
celery.conf.beat_schedule = {
    "check-library-updates": {
        "task": "tasks.check_library_updates",
        "schedule": crontab(minute="*/15")
    }
}

if __name__ == "__main__":
    celery.start()


import os
import requests
import smtplib
from email.mime.text import MIMEText
from celery import Celery
from celery.schedules import crontab
from motor.motor_asyncio import AsyncIOMotorClient

# Environment variables and configurations
REDIS_BROKER = os.getenv("REDIS_BROKER", "redis://redis:6379/0")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
PYPI_URL = "https://pypi.org/pypi/{}/json"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.example.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER", "your-email@example.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your-email-password")

# Initialize Celery
celery = Celery("tasks", broker=REDIS_BROKER, backend=REDIS_BROKER)
celery.conf.timezone = "UTC"

# Connect to MongoDB
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client.get_database("your_database_name")
users_collection = db.get_collection("users")



@celery.task
async def check_library_updates():
    users = await users_collection.find().to_list(None)  # Fetch all users
    updates_made = False
    
    for user in users:
        email = user.get("email")
        libraries = user.get("libraries", {})  # Get stored libraries
        installed_versions = user.get("installed_versions", {})
        updates = {}
        
        for lib, installed_version in libraries.items():
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

# Schedule task every 15 minutes
celery.conf.beat_schedule = {
    "check-library-updates": {
        "task": "tasks.check_library_updates",
        "schedule": crontab(minute="*/15")
    }
}

if __name__ == "__main__":
    celery.start()















REDIS_BROKER = os.getenv("REDIS_BROKER", "redis://redis:6379/0")
PYPI_URL = "https://pypi.org/pypi/{}/json"

celery = Celery("tasks", broker=REDIS_BROKER, backend=REDIS_BROKER)
celery.conf.beat_schedule = {}
celery.conf.timezone = "UTC"

# Get list of unique libraries from all users
@celery.task
async def get_users_libraries():
    users_cursor = users_collection.find({})  # Get all users
    users = await users_cursor.to_list(length=None)  # Convert cursor to list
    user_libs = {}  # Dictionary to store {email: {libraries}}
    for user in users:
        email = user.get("email")
        libraries = user.get("libraries", {})  # Get libraries dict, default to empty
        user_libs[email] = libraries  # Store user libraries
    return user_libs
    
@celery.task
async def check_library_updates():
    users = await users_collection.find().to_list(None)  # Fetch all users
    updates_made = False  # Flag to check if updates happened
    for user in users:
        email = user.get("email")
        libraries = user.get("libraries", {})  # Get stored libraries with versions
        installed_versions = user.get("installed_versions", {})  # Get existing installed versions
        updates = {}  # Dictionary to store new versions
        for lib, installed_versions in libraries.items():
            response = requests.get(PYPI_URL.format(lib))
            if response.status_code == 200:
                latest_version = response.json()["info"]["version"]
                if latest_version != installed_versions.get(lib):  # Compare versions
                    updates[lib] = latest_version
        if updates:  # If any updates were found
            updates_made = True
            installed_versions.update(updates)  # Update installed_versions
            # Save updated versions to the database
            await users_collection.update_one(
                {"email": email},
                {"$set": {"installed_versions": installed_versions}}
            )

    return {"message": "Library updates checked", "updates_made": updates_made}


# @celery.task
# async def check_library_updates():
#     users = await users_collection.find().to_list(None)
#     for user in users:
#         updates = []
#         for lib in user["libraries"]:
#             response = requests.get(PYPI_URL.format(lib))
#             if response.status_code == 200:
#                 latest_version = response.json()["info"]["version"]
#                 if latest_version != user.get("installed_versions", {}).get(lib, None):
#                     updates.append(f"{lib}: {latest_version}")
#                     user["installed_versions"] = user.get("installed_versions", {})
#                     user["installed_versions"][lib] = latest_version    


