from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
from typing import List
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from pymongo import MongoClient
import requests

""" 
Function that will get user name, email and register him - add to database.
    user name: str
    user email: EmailStr 
    user password: str
"""

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "fastapi_db")
client = AsyncIOMotorClient(MONGO_URI)
database = client[DATABASE_NAME]
users_collection = database["users"]

class UserCreate(BaseModel):
    name: str
    password: str
    email: EmailStr
    
# Pydantic Model for Updating User Libraries
class UpdateLibraries(BaseModel):
    libraries: list[str]

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
PYPI_URL = "https://pypi.org/pypi/{}/json"

@app.post("/submit/")
async def register_user(input_data: UserCreate):
    existing_user = await users_collection.find_one({"email": input_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    # Hash the password and add new user to dictionary in database
    hashed_password = pwd_context.hash(input_data.password)
    user_data = {"name": input_data.name, "password": hashed_password, "email": input_data.email, "libraries": {}}
    await users_collection.insert_one(user_data)
    return {"message": "User added successfully"}
# Add/Update Python Libraries for a User

@app.put("/users/{email}/libraries/")
async def update_libraries(email: str, update_data: UpdateLibraries):
    existing_user = await users_collection.find_one({"email": email})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    # Retrieve existing libraries
    existing_libraries = existing_user.get("libraries", {})
    valid_libraries = {}
    invalid_libraries = []
    for lib in update_data.libraries:
        if lib not in existing_libraries:  # Only fetch if it's a new library
            response = requests.get(PYPI_URL.format(lib))
            if response.status_code == 200:
                latest_version = response.json()["info"]["version"]
                valid_libraries[lib] = latest_version  # Add to valid list
            else:
                invalid_libraries.append(lib)  # Mark as invalid
    # Merge valid libraries with existing ones
    existing_libraries.update(valid_libraries)
    # Update only if there are new valid libraries
    if valid_libraries:
        await users_collection.update_one(
            {"email": email},
            {"$set": {"libraries": existing_libraries}}
        )
    return {
        "message": "Library update completed",
        "added_libraries": valid_libraries,
        "invalid_libraries": invalid_libraries
    }
    
    # Get User Information (Including Libraries)
@app.get("/users/{email}")
async def get_user(email: str):
    user = await users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Convert MongoDB ObjectId to string for JSON response
    user["_id"] = str(user["_id"])
    return user


############################################################################################
# # Celery part
# from celery import Celery

# REDIS_BROKER = os.getenv("REDIS_BROKER", "redis://redis:6379/0")

# celery = Celery("tasks", broker=REDIS_BROKER, backend=REDIS_BROKER)
# celery.conf.beat_schedule = {}
# celery.conf.timezone = "UTC"

# # Get list of unique libraries from all users
# @celery.task
# async def get_users_libraries():
#     users_cursor = users_collection.find({})  # Get all users
#     users = await users_cursor.to_list(length=None)  # Convert cursor to list
#     user_libs = {}  # Dictionary to store {email: {libraries}}
#     for user in users:
#         email = user.get("email")
#         libraries = user.get("libraries", {})  # Get libraries dict, default to empty
#         user_libs[email] = libraries  # Store user libraries
#     return user_libs
    
# @celery.task
# async def check_library_updates():
#     users = await users_collection.find().to_list(None)  # Fetch all users
#     updates_made = False  # Flag to check if updates happened
#     for user in users:
#         email = user.get("email")
#         libraries = user.get("libraries", {})  # Get stored libraries with versions
#         installed_versions = user.get("installed_versions", {})  # Get existing installed versions
#         updates = {}  # Dictionary to store new versions
#         for lib, version in libraries.items():
#             response = requests.get(PYPI_URL.format(lib))
#             if response.status_code == 200:
#                 latest_version = response.json()["info"]["version"]
#                 if latest_version != installed_versions.get(lib):  # Compare versions
#                     updates[lib] = latest_version
#         if updates:  # If any updates were found
#             updates_made = True
#             installed_versions.update(updates)  # Update installed_versions
#             # Save updated versions to the database
#             await users_collection.update_one(
#                 {"email": email},
#                 {"$set": {"installed_versions": installed_versions}}
#             )

#     return {"message": "Library updates checked", "updates_made": updates_made}




# @celery.task
# async def check_library_updates():
#     users = await users_collection.find().to_list(None)
#     for user in users:
#         updates = []
#         for lib in user["libraries"]:
#             response = requests.get(PYPI_URL.format(lib))
#             if response.status_code == 200:
#                 latest_version = response.json()["info"]["version"]
#                 if latest_version != user.get("installed_versions", {}).get(lib, None):
#                     updates.append(f"{lib}: {latest_version}")
#                     user["installed_versions"] = user.get("installed_versions", {})
#                     user["installed_versions"][lib] = latest_version    