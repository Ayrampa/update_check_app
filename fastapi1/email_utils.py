import smtplib
from email.mime.text import MIMEText
from config import SMTP_SERVER, SMTP_PORT, EMAIL_SENDER, EMAIL_PASSWORD
from database import users_collection
from email_utils import send_email

def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = to_email
    if updates:
        update_message = "New updates available:\n" + "\n".join(updates)
        send_email(user["email"], "Library Updates", update_message)
        users_collection.update_one(
            {"email": user["email"]}, {"$set": {"installed_versions": user["installed_versions"]}}
        )


    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
    except Exception as e:
        print("Error sending email:", e)