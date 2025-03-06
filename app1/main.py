from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from celery_worker import check_library_updates

# Connect to MongoDB
client = MongoClient("mongodb://mongo:27017/")
db = client["user_db"]
users_collection = db["users"]

app = FastAPI()

@app.post("/register/")
async def register_user(username: str, password: str, email: str, libraries: list[str]):
    """Register a new user with their Python libraries."""
    if users_collection.find_one({"username": username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user_data = {
        "username": username,
        "password": password,  # In production, hash passwords!
        "email": email,
        "libraries": libraries,
    }
    
    users_collection.insert_one(user_data)
    return {"message": "User registered successfully!"}

@app.get("/check-updates/{username}")
async def check_updates(username: str):
    """Trigger a background task to check for updates for a user's libraries."""
    user = users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    task = check_library_updates.apply_async(args=[user["libraries"]])
    return {"task_id": task.id, "message": "Checking for updates..."}

@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """Get Celery task status."""
    from celery.result import AsyncResult
    task_result = AsyncResult(task_id)
    return {"task_id": task_id, "status": task_result.status, "result": task_result.result}