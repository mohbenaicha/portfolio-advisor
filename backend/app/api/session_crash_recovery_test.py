# TODO: move to backend/tests
from fastapi import APIRouter, Depends
from app.core.session_state import session_store
from app.db.user_session import UserSessionManager
from app.db.session import get_db


router = APIRouter()

@router.get("/state")
async def get_session_state():
    """
    Returns the current state of the session store.
    """
    return session_store


@router.post("/update")
async def update_session(
    user_id: str,
    total_prompts_used: int,
    short_term: str,
    long_term: str,
    portfolio_id: int,
    db = Depends(get_db),
):
    """
    Updates the session store for a given user using the UserSessionManager.
    """
    user_id = int(user_id)
    await UserSessionManager.update_session(
        user_id=user_id,
        db=db,
        updates={
            "total_prompts_used": total_prompts_used,
            "llm_memory": {
                "short_term": short_term,
                "long_term": long_term,
                "portfolio_id": portfolio_id,
            },
        },
    )
    print("/update endpoint called, session_store updated via UserSessionManager: ", session_store)
    return {"message": "Session updated successfully"}


@router.post("/simulate_crash")
async def simulate_crash():
    """
    Simulates a server crash by clearing the session store.
    """
    session_store.clear()
    return {"message": "Session store cleared"}
