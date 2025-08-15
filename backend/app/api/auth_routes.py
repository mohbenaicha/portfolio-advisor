from fastapi import APIRouter, HTTPException, Request
import uuid
from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import select
from fastapi import Depends
from app.db.session import get_db, AsyncSession
from app.models.sql_models import User
from app.models.schemas import TokenAuth
from app.core.session_state import session_store
from app.db.user_session import UserSessionManager
from app.db.memory import get_user_memory
from app.dependencies.user import get_current_user
from app.core.logging_config import logger

router = APIRouter()


@router.post("/auth")
async def authenticate_user(
    payload: TokenAuth, request: Request, db: AsyncSession = Depends(get_db)
):
    logger.debug("Authenticating user with provided token.")
    try:
        token = uuid.UUID(payload.token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token format")

    result = await db.execute(select(User).where(cast(User.token, UUID) == token))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    logger.info(f"User {user.id} authenticated successfully.")
    # Check if session already exists in session_store (i.e. for reaccessing the app within 24 hrs)
    if user_id := next(
        (uid for uid in session_store if session_store[uid]["timestamp"]), None
    ):
        logger.debug(f"Session already active for user {user_id}.")
        return {"message": "Session already active", "user_id": user_id}

    # returns object list(LLMMemory) for the user
    # access attribute of LLMMemory using llm_memory[assoc_portfolio_id].attribute
    # accessible members: id, user_id, date, short_term_goal, long_term_goal, created_at, assoc_portfolio_i
    llm_memories = await get_user_memory(user_id=user.id, db=db)
    
    # Load session from database if it exists (hypothetical: server crash)
    session = await UserSessionManager.load_session_from_db(
        user_id=user.id, llm_memory=llm_memories, db=db
    )
 
    # Check if session was actually loaded from database (has timestamp)
    if session and session.get("timestamp"):
        logger.debug(f"Session loaded from database for user {user.id}.")
        return {"message": "Session loaded from database", "user_id": user.id}

    # Otherwise, create a new session
    logger.debug(f"Creating new session for user {user.id}.")
    await UserSessionManager.create_session(
        user_id=user.id,
        llm_memory=llm_memories,
        db=db,
        timestamp=request.headers.get("x-client-time"),
    )
    logger.info(f"New session created for user {user.id}.")
    return {
        "message": f"User {user.id} authenticated; new session created",
        "user_id": user.id,
    }


@router.post("/logout")
async def logout_user(
    user_id: int = Depends(get_current_user),
):
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID missing")

    if user_id in session_store:
        del session_store[user_id]
        logger.info(f"User {user_id} logged out and session cleared.")

    return {"message": "Logout successful"}
