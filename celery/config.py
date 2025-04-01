import os
from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig
# from pathlib import Path
# dotenv_path = Path('/.env')
# load_dotenv(dotenv_path=dotenv_path)

load_dotenv()

# conf = ConnectionConfig(
#     MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
#     MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
#     MAIL_PORT=587,
#     MAIL_SERVER="smtp.gmail.com",
#     MAIL_FROM=os.getenv("MAIL_FROM", "noreply@example.com"),
#     MAIL_TLS=True,
#     MAIL_SSL=False
# )

REDIS_BROKER = os.getenv("REDIS_BROKER")
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")