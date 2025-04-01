from celery import Celery, shared_task, chain
import requests
from celery.schedules import crontab
import os
from pymongo import MongoClient
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os
from pathlib import Path

dotenv_path = Path('/.env')
load_dotenv(dotenv_path=dotenv_path)
PYPI_URL = "https://pypi.org/pypi/{}/json"
REDIS_BROKER = os.getenv("REDIS_BROKER")
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

client = MongoClient(MONGO_URI)
database = client[DATABASE_NAME]
users_collection = database["users"]

celery = Celery("tasks", broker=REDIS_BROKER, backend=REDIS_BROKER)
celery.conf.timezone = "UTC"

@shared_task
def get_libraries_set():
    users = list(users_collection.find({})) 
    print(users)
    current_user_libraries = {}
    for user in users:
        email = user.get("email")
        libraries = user.get("libraries", {}) 
        current_user_libraries[email] = libraries
        print(current_user_libraries)
    return current_user_libraries

@shared_task
def check_library_updates(current_user_libraries):
    updates_made = False
    updates_by_user = {}
    for email, libraries in current_user_libraries.items():
        updates_by_user[email] = {}
        for lib, installed_version in libraries.items():
            response = requests.get(f"https://pypi.org/pypi/{lib}/json")
            if response.status_code == 200:
                latest_version = response.json()["info"]["version"]
                if latest_version != installed_version:
                    updates_by_user[email][lib] = latest_version
                    print(f"UPDATE FOUND: {lib} -> {latest_version}")
                    updates_made = True

        # Update database only if there are changes
        if updates_by_user[email]:
            users_collection.update_one(
                {"email": email},
                {"$set": {"libraries": {**libraries, **updates_by_user[email]}}}
            )
    return updates_by_user

@shared_task
def send_email_task(updates_by_user):
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")    
    subject = "Library Updates Available"
    body = "The following libraries have updates available:\n\n"
    
    for email, updates in updates_by_user.items():
        body = "The following libraries have updates:\n\n"
    body += "\n".join([f"{lib}: {version}" for lib, version in updates.items()])    
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = email    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        print(f"Email sent to {email}")
    except Exception as e:
        print(f"Failed to send email to {email}: {e}")

@shared_task
def celery_workflow():
    """
    Execute multiply tasks to get the versions of python libraries, check for updates and send emails to the user vith relevant information.
    """
    workflow = chain(
        get_libraries_set.s(),  
        check_library_updates.s(),  
        send_email_task.s()
    )
    return workflow()

celery.conf.beat_schedule = {
    "check-library-updates": {
        "task": "tasks.celery_workflow",
        "schedule": crontab(minute="*/1")
    }
}

if __name__ == "__main__":
    celery.start()