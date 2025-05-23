from fastapi import APIRouter, HTTPException, Request
import uuid
from sqlalchemy import select
from fastapi import Depends
from app.db.session import get_db, AsyncSession
from app.models.sql_models import User
from app.models.schemas import TokenAuth
from app.core.session_state import session_store
from app.db.user_session import UserSessionManager
from app.db.memory import get_user_memory

router = APIRouter()


@router.post("/auth")
async def authenticate_user(
    payload: TokenAuth, request: Request, db: AsyncSession = Depends(get_db)
):
    try:
        token = uuid.UUID(payload.token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token format")

    result = await db.execute(select(User).where(User.token == token))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Check if session already exists in session_store (i.e. for reaccessing the app within 24 hrs)
    if user_id := next(
        (uid for uid in session_store if session_store[uid]["timestamp"]), None
    ):
        print("DEBUG: Session already active for user:", user_id)
        return {"message": "Session already active", "user_id": user_id}

    # returns object list(LLMMemory) for the user
    # access attribute of LLMMemory using llm_memory[i].attribute
    # accessible members: id, user_id, date, short_term_goal, long_term_goal, created_at, assoc_portfolio_i
    llm_memories = await get_user_memory(user_id=user.id, db=db)
    print("DEBUG: LLM memories retrieved:", llm_memories)

    # Load session from database if it exists (hypothetical: server crash)
    session = await UserSessionManager.load_session_from_db(
        user_id=user.id, llm_memory=llm_memories, db=db
    )
    if session:
        print("DEBUG: Session loaded from database:", session)
        return {"message": "Session loaded from database", "user_id": user.id}

    # Otherwise, create a new session
    await UserSessionManager.create_session(
        user_id=user.id,
        llm_memory=llm_memories,
        db=db,
        timestamp=request.headers.get("x-client-time"),
    )
    print(
        f"DEBUG: New session created for user {session_store[user.id]}:",
        session_store[user.id],
    )
    print(f"Memory address of session_store in app: {id(session_store)}")
    return {
        "message": f"User {user.id} authenticated; new session created",
        "user_id": user.id,
    }
