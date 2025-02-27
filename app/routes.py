from fastapi import APIRouter, HTTPException
from app.database import users_collection
from app.models import User
from app.tasks import check_for_updates_task

router = APIRouter()

@router.post("/subscribe/")
async def subscribe(user: User):
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        await users_collection.update_one(
            {"email": user.email}, 
            {"$addToSet": {"libraries": {"$each": user.libraries}}}
        )
    else:
        await users_collection.insert_one(user.dict())
    return {"message": "Subscription successful"}

@router.get("/users/")
async def list_users():
    users = await users_collection.find().to_list(100)
    return [{"email": user["email"], "libraries": user["libraries"]} for user in users]

@router.post("/trigger_check/")
async def trigger_manual_check():
    check_for_updates_task.delay()
    return {"message": "Update check triggered"}