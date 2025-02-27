from fastapi import FastAPI
from app.routes import router

app = FastAPI()
app.include_router(router)

@app.get("/")
def home():
    return {"message": "Welcome to the PyPI Notifier API"}
# from fastapi import FastAPI, Depends, HTTPException
# from auth import router as auth_router
# from database import users_collection, init_db
# from utils import get_current_user
# from celery_config import check_library_updates

# app = FastAPI()

# @app.lifespan("startup")
# async def startup_db():
#     """Initialize the database indexes."""
#     await init_db()

# app.include_router(auth_router, prefix="/auth")

# @app.get("/user/me/")
# async def get_user_info(current_user: dict = Depends(get_current_user)):
#     """Get the authenticated user's info."""
#     return current_user

# @app.put("/user/{email}/add/")
# async def add_library(email: str, libraries: list, current_user: dict = Depends(get_current_user)):
#     """Add libraries to the user's tracking list."""
#     if current_user["email"] != email:
#         raise HTTPException(status_code=403, detail="Unauthorized")

#     await users_collection.update_one(
#         {"email": email},
#         {"$addToSet": {"libraries": {"$each": libraries}}}
#     )
#     return {"message": "Libraries added successfully"}

# @app.get("/user/{email}/check_updates/")
# async def check_updates(email: str, current_user: dict = Depends(get_current_user)):
#     """Manually trigger a check for library updates."""
#     if current_user["email"] != email:
#         raise HTTPException(status_code=403, detail="Unauthorized")

#     check_library_updates.delay(email)  # Run asynchronously
#     return {"message": "Update check started"}
