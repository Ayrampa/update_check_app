from fastapi import FastAPI, HTTPException
from passlib.context import CryptContext
import requests
from models import UserCreate, UpdateLibraries
from database import users_collection

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
PYPI_URL = "https://pypi.org/pypi/{}/json"

@app.post("/submit/")
async def register_user(input_data: UserCreate):
    ''' 
    Register user to DB.
    :param input_data: user name, email and password. list of libraries is optional
    :type input_data: class UserCreate
    :returns: notification for user
    :rtype: dict
    '''
    existing_user = await users_collection.find_one({"email": input_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = pwd_context.hash(input_data.password)
    user_data = {"name": input_data.name, "password": hashed_password, "email": input_data.email, "libraries": {}}
    await users_collection.insert_one(user_data)
    return {"message": "User added successfully"}

@app.put("/users/{email}/libraries/")
async def update_libraries(email: str, update_data: UpdateLibraries):
    ''' 
    Adds python libraries with the current versions for the registered user to DB.
    :param email: user email 
    :param update_data: list of python libraries from user
    :type email: str
    :type update_data: class UpdateLibraries
    :returns: notification for user
    :rtype: dict
    '''
    existing_user = await users_collection.find_one({"email": email})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    existing_libraries = existing_user.get("libraries", {})
    valid_libraries = {}
    invalid_libraries = []
    for lib in update_data.libraries:
        if lib not in existing_libraries:  
            response = requests.get(PYPI_URL.format(lib))
            if response.status_code == 200:
                latest_version = response.json()["info"]["version"]
                valid_libraries[lib] = latest_version 
            else:
                invalid_libraries.append(lib)  

    existing_libraries.update(valid_libraries)    
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
    user["_id"] = str(user["_id"])
    return user

