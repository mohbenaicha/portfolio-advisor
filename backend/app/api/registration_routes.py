import smtplib
from email.message import EmailMessage
from fastapi import APIRouter
from fastapi import HTTPException
from app.config import GMAIL_PWD, EMAIL_ADDRESS
from app.models.schemas import AccessRequest

def email_access_request(user_email):
    msg = EmailMessage()
    msg["Subject"] = "New Access Token Request"
    msg["From"] = user_email
    msg["To"] = EMAIL_ADDRESS
    msg.set_content(f"{user_email} is requesting access to the app.")
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, GMAIL_PWD)
            smtp.send_message(msg)
    except Exception as e:
        raise Exception(f"Failed to send email: {e}")

router = APIRouter()

@router.post("/request-key")
def request_auth_token(request: AccessRequest):
    user_email = request.email
    try:
        email_access_request(user_email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"message": "Access request submitted successfully."}
