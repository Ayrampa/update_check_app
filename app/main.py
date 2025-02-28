from fastapi import FastAPI, HTTPException, BackgroundTasks
from .models import UserCreate
from .database import users_collection
from .tasks import check_library_updates

app = FastAPI()

@app.post("/users/")
async def create_user(user: UserCreate):
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    user_data = user.model_dump()
    await users_collection.insert_one(user_data)
    return {"message": "User added successfully"}

@app.post("/check-updates/")
async def trigger_update_check():
    check_library_updates.apply_async()
    return {"message": "Update check triggered"}