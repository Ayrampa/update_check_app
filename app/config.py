import os
from dotenv import load_dotenv
# from pathlib import Path
# dotenv_path = Path('/.env')
# load_dotenv(dotenv_path=dotenv_path)
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

