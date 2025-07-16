from fastapi import Request, HTTPException
from app.db.session import AsyncSession
from sqlalchemy.future import select
from app.models.sql_models import User
from fastapi import Depends
from app.db.session import get_db
from typing import cast
from app.config import SYSTEM_USER_TOKEN

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> int:
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")
    
    # Remove 'Bearer '
    token = auth_header[7:]  

    # Check if the token is for internal service calls
    if SYSTEM_USER_TOKEN and token == SYSTEM_USER_TOKEN:
        return 0  # ID 0 or some reserved value for internal service calls
    
    result = await db.execute(select(User).where(User.token == token))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return cast(int, user.id)
