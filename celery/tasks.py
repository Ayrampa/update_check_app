import os
import requests
from celery import Celery
import smtplib
from email.message import EmailMessage
from celery.schedules import crontab
from motor.motor_asyncio import AsyncIOMotorClient
#from config import MONGO_URI, DATABASE_NAME

DATABASE_NAME = os.getenv("DATABASE_NAME", "fastapi_db")
PYPI_URL = "https://pypi.org/pypi/{}/json"
REDIS_BROKER = os.getenv("REDIS_BROKER", "redis://redis:6379/0")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
celery = Celery("tasks", broker=REDIS_BROKER, backend=REDIS_BROKER)
celery.conf.timezone = "UTC"
client = AsyncIOMotorClient(MONGO_URI)
database = client[DATABASE_NAME]
users_collection = database["users"]

# # Initialize Celery
# celery = Celery(
#     "worker",
#     broker="redis://redis:6379/0",
#     backend="redis://redis:6379/0"
# )

@celery.task
async def check_library_updates():
    users = await users_collection.find().to_list(None)  
    updates_made = False
    
    for user in users:
        email = user.get("email")
        libraries = user.get("libraries", {})  
        installed_versions = user.get("versions", {})
        updates = {}
        
        for lib, installed_versions in libraries.items():
            response = requests.get(PYPI_URL.format(lib))
            if response.status_code == 200:
                latest_version = response.json()["info"]["version"]
                if latest_version != installed_versions.get(lib):  
                    updates[lib] = latest_version
        
        if updates:  
            updates_made = True
            installed_versions.update(updates) 
            await users_collection.update_one(
                {"email": email},
                {"$set": {"installed_versions": installed_versions}}
            )
            send_email(email, updates)  
    return {"message": "Library updates checked", "updates_made": updates_made}

def send_email(email, updates):
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")  
    
    
    subject = "Library Updates Available"
    body = "The following libraries have updates available:\n\n"
    
    for lib, version in updates.items():
        body += f"- {lib}: {version}\n"
    
    body += "\nPlease update your libraries accordingly."
    
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = email
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user)
            server.send_message(msg)
        print(f"Email sent to {email}")
    except Exception as e:
        print(f"Failed to send email to {email}: {e}")

# Schedule task every 15 minutes
celery.conf.beat_schedule = {
    "check-library-updates": {
        "task": "tasks.check_library_updates",
        "schedule": crontab(minute="*/15")
    }
}

if __name__ == "__main__":
    celery.start()
