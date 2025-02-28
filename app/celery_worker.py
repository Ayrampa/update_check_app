from celery import Celery
import requests

# Initialize Celery
celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

@celery_app.task
def check_library_updates(libraries):
    """Check PyPI for updates for a list of libraries."""
    updates = {}

    for lib in libraries:
        response = requests.get(f"https://pypi.org/pypi/{lib}/json")
        if response.status_code == 200:
            latest_version = response.json()["info"]["version"]
            updates[lib] = latest_version
        else:
            updates[lib] = "Not found"

    return updates