from fastapi import APIRouter, HTTPException
from app.database import users_collection
from app.models import User
from app.tasks import check_for_updates_task

router = APIRouter()

@router.post("/subscribe/")
async def subscribe(user: User):
    """Subscribe a user to track updates for given libraries"""
    existing_user = await users_collection.find_one({"email": user.email})
    
    if existing_user:
        await users_collection.update_one(
            {"email": user.email}, 
            {"$addToSet": {"libraries": {"$each": user.libraries}}}
        )
    else:
        await users_collection.insert_one(user.dict())
    
    return {"message": "Subscription updated successfully"}

@router.get("/users/")
async def list_users():
    """List all users with their tracked libraries"""
    users = await users_collection.find().to_list(100)
    return [{"email": user["email"], "libraries": user["libraries"]} for user in users]

@router.get("/user/{email}")
async def get_user(email: str):
    """Get a specific user's tracked libraries"""
    user = await users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"email": user["email"], "libraries": user["libraries"]}

@router.put("/user/{email}/add/")
async def add_libraries(email: str, libraries: list):
    """Add new libraries to a user's tracking list"""
    result = await users_collection.update_one(
        {"email": email}, 
        {"$addToSet": {"libraries": {"$each": libraries}}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Libraries added successfully"}

@router.put("/user/{email}/remove/")
async def remove_libraries(email: str, libraries: list):
    """Remove libraries from a user's tracking list"""
    result = await users_collection.update_one(
        {"email": email}, 
        {"$pull": {"libraries": {"$in": libraries}}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Libraries removed successfully"}

@router.post("/trigger_check/")
async def trigger_manual_check():
    """Manually trigger a check for library updates"""
    check_for_updates_task.delay()
    return {"message": "Update check triggered"}