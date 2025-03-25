from motor.motor_asyncio import AsyncIOMotorClient
from app import MONGO_URI, DATABASE_NAME

def get_database():
    database = client[DATABASE_NAME]
    users_collection = database["users"]
    client = AsyncIOMotorClient(MONGO_URI)
    return client