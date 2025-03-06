import requests
from celery_worker import celery
from database import users_collection
# from email_utils import send_email

PYPI_URL = "https://pypi.org/pypi/{}/json"

@celery.task
async def check_library_updates():
    users = await users_collection.find().to_list(None)
    for user in users:
        updates = []
        for lib in user["libraries"]:
            response = requests.get(PYPI_URL.format(lib))
            if response.status_code == 200:
                latest_version = response.json()["info"]["version"]
                if latest_version != user.get("installed_versions", {}).get(lib, None):
                    updates.append(f"{lib}: {latest_version}")
                    user["installed_versions"] = user.get("installed_versions", {})
                    user["installed_versions"][lib] = latest_version
                    return True

        # if updates:
        #     update_message = "New updates available:\n" + "\n".join(updates)
        #     send_email(user["email"], "Library Updates", update_message)
        #     await users_collection.update_one(
        #         {"email": user["email"]}, {"$set": {"installed_versions": user["installed_versions"]}}
        #     )