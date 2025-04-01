import os
from dotenv import load_dotenv

load_dotenv()

REDIS_BROKER = os.getenv("REDIS_BROKER")
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")