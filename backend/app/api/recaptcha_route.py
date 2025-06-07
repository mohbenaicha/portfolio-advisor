import httpx
from fastapi import HTTPException
from fastapi import APIRouter
from app.models.schemas import RecaptchaRequest
from app.config import RECAPTCHA_SECRET_KEY
router = APIRouter()


@router.post("/verify-recaptcha")
async def verify_recaptcha(request: RecaptchaRequest):
    secret_key = RECAPTCHA_SECRET_KEY  # Replace with your reCAPTCHA secret key
    url = "https://www.google.com/recaptcha/api/siteverify"
    payload = {"secret": secret_key, "response": request.token}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=payload)
        result = response.json()

    score = result.get("score", 0)
    print("reCAPTCHA verification result:", result)
    if score < 0.5:  # Set your threshold score here
        raise HTTPException(status_code=400, detail="Suspicious activity detected")

    return {"message": "success", "score": score}
