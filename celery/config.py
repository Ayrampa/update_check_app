import os
from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM=os.getenv("MAIL_FROM", "noreply@example.com"),
    MAIL_TLS=True,
    MAIL_SSL=False
)
