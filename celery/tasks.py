from celery import Celery, shared_task, chain, signature
import requests
from celery.schedules import crontab
import os
#from config import conf
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pymongo import MongoClient
import smtplib
from email.message import EmailMessage

DATABASE_NAME = os.getenv("DATABASE_NAME", "fastapi_db")
PYPI_URL = "https://pypi.org/pypi/{}/json"
REDIS_BROKER = os.getenv("REDIS_BROKER", "redis://redis:6379/0")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
#MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/fastapi_db")

client = MongoClient("mongodb://localhost:27017")
database = client[DATABASE_NAME]
users_collection = database["users"]

celery = Celery("tasks", broker=REDIS_BROKER, backend=REDIS_BROKER)
celery.conf.timezone = "UTC"

@shared_task
def get_libraries_set():
    users = list(users_collection.find({})) 
    print(users)
    current_libraries = set()
    for user in users:
        libraries = user.get("libraries", []) 
        current_libraries.update(libraries)
        #print(current_libraries)
    return list(current_libraries)

@shared_task
def get_libraries_versions(current_libraries):
    libraries_versions = {}
    for lib in current_libraries.items:
        response = requests.get(f"https://pypi.org/pypi/{lib}/json")                
        if response.status_code == 200:
            current_version = response.json()["info"]["version"]
            libraries_versions[lib] = current_version
            print(libraries_versions)
    return libraries_versions

@shared_task
def check_library_updates(libraries_versions):
    users = list(users_collection.find({})) 
    updates_made = False
    updates_by_user = {}
    for user in users:
        email = user.get("email")
    updates = {}
    for lib, installed_version in libraries_versions.items():
        response = requests.get(f"https://pypi.org/pypi/{lib}/json")                
        if response.status_code == 200:
            latest_version = response.json()["info"]["version"]
            #print(f"Latest version of {lib}: {latest_version}")
            if latest_version != installed_version:
                print(f"UPDATE FOUND: {lib} -> {latest_version}")
                updates[lib] = latest_version
        else:
            print(f"Failed to fetch {lib} from PyPI (status: {response.status_code})")
        if updates:
            updates_made = True               
            print(f"Updating database for user {email}: {updates}")
            users_collection.update_one(
                {"email": email},                   
                {"$set": {"libraries": {**libraries_versions, **updates}}}
            )
        updates_by_user[email] = updates
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
        get_libraries_versions.s(),
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
    get_libraries_set()

# Configure FastAPI-Mail connection
# conf = ConnectionConfig(
#     MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
#     MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
#     MAIL_PORT=587,
#     MAIL_SERVER="smtp.gmail.com",
#     MAIL_FROM=os.getenv("MAIL_FROM", "noreply@example.com"),
#     MAIL_TLS=True,
#     MAIL_SSL=False
# )

# @shared_task
# def send_email_task(updates_by_user):
#     """
#     Send an email to users if updates were found.
#     """
#     conf = ConnectionConfig(
#         MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
#         MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
#         MAIL_PORT=587,
#         MAIL_SERVER="smtp.gmail.com",
#         MAIL_FROM=os.getenv("MAIL_FROM", "noreply@example.com"),
#         MAIL_TLS=True,
#         MAIL_SSL=False
# )

#     fastmail = FastMail(conf)  # Create FastMail instance

#     for email, updates in updates_by_user.items():
#         subject = "Library Updates Available"
#         message_body = "The following libraries have updates:\n\n"
#         message_body += "\n".join([f"{lib}: {version}" for lib, version in updates.items()])

#         message = MessageSchema(
#             subject=subject,
#             recipients=[email],
#             body=message_body,
#             subtype="plain"
#         )
#         fastmail.send_message(message)  # Await sending the email

#     return "Emails sent successfully!"