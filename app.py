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
    libraries: list[str] = []

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
    # user_data = {
    #     "name" = input_data.name,
    #     "password" = hashed_password,
    #     "email" = input_data.email,
    #     "libraries" = input_data.libraries,
    # }
    user_data = {"name": input_data.name, "password": hashed_password, "email": input_data.email, "libraries": input_data.libraries}
    #user_data = input_data.model_dump()
    # user_data["password"] = hashed_password
    await users_collection.insert_one(user_data)
    return {"message": "User added successfully"}

# Add/Update Python Libraries for a User
@app.put("/users/{email}/libraries/")
async def update_libraries(email: str, update_data: UpdateLibraries):
    existing_user = await users_collection.find_one({"email": email})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    # Merge existing and new libraries (avoid duplicates)
    new_libraries = list(set(existing_user.get("libraries", []) + update_data.libraries))
    lib_versions = {}
    for lib in new_libraries:
        response = requests.get(PYPI_URL.format(lib))
        if response.status_code == 200:
            latest_version = response.json()["info"]["version"]
            lib_versions[lib] = latest_version
    # Update user document in MongoDB
    await users_collection.update_one(
        {"email": email},
        {"$set": {"libraries": lib_versions}}
    )
    return {"message": "Libraries updated successfully", "libraries": lib_versions}


# @app.put("/users/{email}/libraries/")
# async def update_libraries(email: str, update_data: UpdateLibraries):
#     existing_user = await users_collection.find_one({"email": email})
#     if not existing_user:
#         raise HTTPException(status_code=404, detail="User not found")
#     # Merge existing and new libraries (avoid duplicates)
#     new_libraries = list(set(existing_user.get("libraries", []) + update_data.libraries))
#     lib_versions = []
#     for lib in new_libraries:
#         response = requests.get(PYPI_URL.format(lib))
#         if response.status_code == 200:
#             latest_version = response.json()["info"]["version"]
#             #if latest_version != user.get("installed_versions", {}).get(lib, None):
#             lib_versions.append(latest_version)
                #f"{lib}: {latest_version}")
            
    # # Update user document in MongoDB
    # await users_collection.update_one(
    #     {"email": email},
    #     {"$set": {"libraries": lib_versions}}
    # )
    # return {"message": "Libraries have been updated successfully", "libraries": new_libraries}
    
    
    # Get the version of python libraries before uploading to database
    for library in new_libraries:
        library = new_libraries.split(',')

# Get User Information (Including Libraries)
@app.get("/users/{email}")
async def get_user(email: str):
    user = await users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Convert MongoDB ObjectId to string for JSON response
    user["_id"] = str(user["_id"])
    return user

# if __name__ == '__main__':
#     app.run(debug=True)


# def register_user(user: UserCreate):
#     users = {}
#     if user.email not in users:
#         users[UserCreate.email].append(user)
#         #users[UserCreate.email] = [user]
#     else:
#         print(f"User {users.email} already exists.")

# @app.post("/subscribe/")
# async def raw_libraries(email, libraries: List[str]):
#     for email in user_data.email:

#     libraries = input_data.libraries.split(',')

# # MongoDB connection (Example)
# client = MongoClient("mongodb://localhost:27017")
# db = client.mydatabase
# users_collection = db.users