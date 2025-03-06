from fastapi import FastAPI, HTTPException
from passlib.context import CryptContext
import requests
from models import UserCreate, UpdateLibraries
from database import users_collection

# load_dotenv()

# MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
# DATABASE_NAME = os.getenv("DATABASE_NAME", "fastapi_db")
# client = AsyncIOMotorClient(MONGO_URI)
# database = client[DATABASE_NAME]
# users_collection = database["users"]

# class UserCreate(BaseModel):
#     name: str
#     password: str
#     email: EmailStr
    
# # Pydantic Model for Updating User Libraries
# class UpdateLibraries(BaseModel):
#     libraries: list[str]

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
    user["_id"] = str(user["_id"])
    return user