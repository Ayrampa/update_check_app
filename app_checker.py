""" 
Function that will get user name, email and register him - add to database.
    user name: str
    user email: EmailStr 
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
from typing import List
import os
from dotenv import load_dotenv

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
    #libraries: List[str]

app = FastAPI()

@app.post("/submit/")
async def register_user(input_data: UserCreate):
    name = input_data.name
    password = input_data.password
    email = input_data.email
    

    existing_user = await users_collection.find_one({"email": input_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    user_data = input_data.model_dump_json()
    await users_collection.insert_one(user_data)
    return {"message": "User added successfully"}

def register_user(user: UserCreate):
    users = {}
    if user.email not in users:
        users[UserCreate.email].append(user)
        #users[UserCreate.email] = [user]
    else:
        print(f"User {users.email} already exists.")


def raw_libraries(users.email, libraries: List[str]):
    for email in users.email:

    libraries = input_data.libraries.split(',')




if __name__ == '__main__':
    app_checker.run(debug=True)