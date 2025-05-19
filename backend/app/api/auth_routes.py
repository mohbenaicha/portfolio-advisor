from fastapi import APIRouter, HTTPException, Request
import uuid
from sqlalchemy import select
from fastapi import Depends
from app.db.session import get_db
from app.models.sql_models import User
from app.models.schemas import TokenAuth
from app.core.session_state import session_store

router = APIRouter()



@router.post("/auth")
async def authenticate_user(payload: TokenAuth, request: Request, db=Depends(get_db)):
    try:
        token = uuid.UUID(payload.token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    result = await db.execute(select(User).where(User.token == token))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    session_store[user.id] = {
        "llm_memory": [],
        "timestamp": request.headers.get("x-client-time") 
    }

    return {"message": "Authenticated", "user_id": user.id}
