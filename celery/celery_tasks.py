from celery import Celery, shared_task, chain
from database import users_collection
import requests
from celery.schedules import crontab

REDIS_BROKER = os.getenv("REDIS_BROKER", "redis://redis:6379/0")
celery = Celery("tasks", broker=REDIS_BROKER, backend=REDIS_BROKER)
celery.conf.timezone = "UTC"

@shared_task
async def get_libraries_set():
    users = users_collection.find().to_list(None)
    current_libraries = set()
    for user in users:
        libraries = user.get("libraries", []) 
        current_libraries.update(libraries)
    return list(current_libraries)

@shared_task
def get_libraries_versions(current_libraries):
    libraries_versions = {}
    for lib in current_libraries:
        response = requests.get(f"https://pypi.org/pypi/{lib}/json")                
        if response.status_code == 200:
            current_version = response.json()["info"]["version"]
            libraries_versions[lib] = current_version
    return libraries_versions

@shared_task
def check_library_updates(libraries_versions):
    users = users_collection.find().to_list(None)
   #? updates_by_user = {}
    for user in users:
        email = user.get("email")
        libraries = user.get("libraries", {}) 
    updates = {}
    for lib, installed_version in libraries.items():
        latest_version = libraries_versions.get(lib)
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
            users_collection.update_one(
                {"email": email},                   
                {"$set": {"libraries": {**libraries, **updates}}}
            )
        #     send_email(email, updates)
        # print(f"\nFinal result: Updates made? {updates_made}")
        # return {"message": "Library updates checked", "updates_made": updates_made}


@shared_task
def send_email_task(subject, message, recipient_list):
    send_mail(subject, message, "user@example.com", recipient_list)

    return "Email sent successfully!"

# Example: Using Celery Signatures
@shared_task
def celery_workflow():
    """
    Execute multiply tasks to get the versions of python libraries, check for updates and send emails to the user vith relevant information.
    """
    celery_workflow = chain(
        get_libraries_set.s(),  
        get_libraries_versions.s(),
        check_library_updates.s(),  
        send_email_task.s("Library updates checked", ["user@example.com"])
    )
    result = celery_workflow()
    return result

celery.conf.beat_schedule = {
    "check-library-updates": {
        "task": "tasks.celery_workflow",
        "schedule": crontab(minute="*/3")
    }
}

if __name__ == "__main__":
    celery.start()