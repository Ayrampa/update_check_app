# from motor.motor_asyncio import AsyncIOMotorClient
# import os

# MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
# client = AsyncIOMotorClient(MONGO_URI)
# db = client.pypi_notifier
# users_collection = db.users
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

client = AsyncIOMotorClient(MONGO_URI)
db = client["pypi_checker"]
users_collection = db["users"]

async def init_db():
    """Ensure indexes are created for faster lookups."""
    await users_collection.create_index([("email", ASCENDING)], unique=True)