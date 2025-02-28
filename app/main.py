from fastapi import FastAPI, HTTPException, BackgroundTasks
from .models import UserCreate
from .database import users_collection
from .tasks import check_library_updates

# from fastapi import FastAPI, Form
# from fastapi.responses import HTMLResponse
# from pydantic import BaseModel
# from app import mongo, celery
# from starlette.requests import Request

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

@app.get("/users")
async def get_users():
    users = list(users_collection.find({}, {"_id": 0}))  # Exclude MongoDB's _id
    return {"users": users}



#app = FastAPI()

# class UserInput(BaseModel):
#     name: str
#     email: str
#     libraries: str  # A comma-separated list of libraries

# @app.post("/submit/")
# async def submit_user(input_data: UserInput):
#     name = input_data.name
#     email = input_data.email
#     libraries = input_data.libraries.split(',')

#     # Store in MongoDB
#     mongo.db.users.insert_one({"name": name, "email": email, "libraries": libraries})

#     # Schedule the task to check library updates
#     check_library_updates.apply_async(args=[email, libraries])

#     return {"message": "User data received and processing started."}

# @app.get("/", response_class=HTMLResponse)
# async def get_form():
#     with open('app/templates/index.html', 'r') as f:
#         return f.read()