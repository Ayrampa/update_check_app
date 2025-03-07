import os
import requests
from asgiref.sync import async_to_sync
from celery import Celery
import smtplib
from email.message import EmailMessage
from celery.schedules import crontab
from motor.motor_asyncio import AsyncIOMotorClient

DATABASE_NAME = os.getenv("DATABASE_NAME", "fastapi_db")
PYPI_URL = "https://pypi.org/pypi/{}/json"
REDIS_BROKER = os.getenv("REDIS_BROKER", "redis://redis:6379/0")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/fastapi_db")

celery = Celery("tasks", broker=REDIS_BROKER, backend=REDIS_BROKER)
celery.conf.timezone = "UTC"

@celery.task
def check_library_updates():
    '''
    Function that makes async function behaves as sync function that is necessary for celery
    '''    
    client = AsyncIOMotorClient("mongodb://mongo:27017")
    db = client["fastapi_db"]
    users_collection = db["users"]
    async def async_task():
        users = await users_collection.find().to_list(None)
        updates_made = False
        print(f"Total users found: {len(users)}")
        for user in users:
            email = user.get("email")
            libraries = user.get("libraries", {}) 
            print(f"DEBUG: libraries = {libraries} (Type: {type(libraries)})") 
            print(f"\nChecking updates for user: {email}")
            print(f"Stored libraries: {libraries}")        
            updates = {}
            for lib, installed_version in libraries.items():
                print(f"\nChecking {lib} (installed: {installed_version})")
                response = requests.get(f"https://pypi.org/pypi/{lib}/json")                
                if response.status_code == 200:
                    latest_version = response.json()["info"]["version"]
                    print(f"Latest version of {lib}: {latest_version}")
                    if latest_version != installed_version:
                        print(f"UPDATE FOUND: {lib} -> {latest_version}")
                        updates[lib] = latest_version
                else:
                    print(f"Failed to fetch {lib} from PyPI (status: {response.status_code})")
            if updates:
                updates_made = True               
                print(f"Updating database for user {email}: {updates}")
                await users_collection.update_one(
                    {"email": email},                   
                    {"$set": {"libraries": {**libraries, **updates}}}
                )
                send_email(email, updates)
        print(f"\nFinal result: Updates made? {updates_made}")
        return {"message": "Library updates checked", "updates_made": updates_made}
    return async_to_sync(async_task)()


def send_email(email, updates):
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")    
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
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        print(f"Email sent to {email}")
    except Exception as e:
        print(f"Failed to send email to {email}: {e}")

celery.conf.beat_schedule = {
    "check-library-updates": {
        "task": "tasks.check_library_updates",
        "schedule": crontab(minute="*/3")
    }
}

if __name__ == "__main__":
    celery.start()
