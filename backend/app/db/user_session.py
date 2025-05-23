from datetime import datetime, timedelta, timezone
from fastapi import Depends
from typing import List, Dict, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, insert, delete
from app.core.session_state import session_store
from app.models.sql_models import (
    UserSession,
    LLMMemory,
)
from app.db.memory import add_user_memory
from app.dependencies.user import get_current_user


class UserSessionManager:

    SESSION_EXPIRY_HOURS = 24

    @staticmethod
    def get_session(user_id: int):
        return session_store[user_id]

    @staticmethod
    async def load_session_from_db(
        user_id: int = Depends(get_current_user),
        db: AsyncSession = None,
        llm_memory: List[LLMMemory] = [],
    ) -> Dict[str, Union[int, str, List[LLMMemory]]]:
        if db is None:
            raise ValueError("error in user_session.py/UserSessionManager::load_session_from_db: Database session is required")
        
        result = await db.execute(
            select(UserSession).where(UserSession.user_id == user_id)
        )
        session = result.scalar_one_or_none()

        if session:
            session_store[user_id] = {
                "llm_memory": llm_memory,
                "timestamp": session.timestamp,
                "total_prompts_used": session.total_prompts_used,
            }
            return session_store[user_id]

    @staticmethod
    async def update_session(
        user_id: int = None,
        db: AsyncSession = None,
        updates: Dict[str, Union[int, str]] = {},
    ):
        if not user_id:
            try:
                user_id = get_current_user()
            except Exception as e:
                raise ValueError("error in user_session.py/UserSessionManager::update_session: User ID is required") from e
            
        
        for k, v in updates.items():
            if k == "llm_memory": 
                # writes memory to db and updates session store
                user_memory = await add_user_memory(
                    user_id=user_id,
                    date=datetime.now(timezone.utc).replace(tzinfo=None),
                    short_term=v.get("short_term"),
                    long_term=v.get("long_term"),
                    portfolio_id=v.get("portfolio_id"),
                    db=db,
                )
                session_store[user_id]["llm_memory"].append(user_memory)
            else:
                print(f"Updating session_store[{user_id}][{k}] to {v}")
                session_store[user_id][k] = v

        await db.execute(
            update(UserSession)
            .where(UserSession.user_id == user_id)
            .values(
                timestamp=session_store[user_id]["timestamp"],
                total_prompts_used=session_store[user_id]["total_prompts_used"],
            )
        )
        await db.commit()

    @staticmethod
    async def create_session(
        user_id: int = Depends(get_current_user),
        db: AsyncSession = None,
        llm_memory: List[LLMMemory] = [],
        timestamp: str = None,
    ):
        session_store[user_id] = {
            "llm_memory": llm_memory,
            "timestamp": timestamp or datetime.now(timezone.utc).replace(tzinfo=None),
            "total_prompts_used": 0,
        }

        await db.execute(
            insert(UserSession).values(
                user_id=user_id,
                timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                total_prompts_used=0,
            )
        )
        await db.commit()

    @staticmethod
    async def cleanup_sessions(db: AsyncSession = None):
        current_time = datetime.now(timezone.utc).replace(tzinfo=None)

        expired_users = [
            user_id
            for user_id, session in session_store.items()
            if session["timestamp"]
            and datetime.fromisoformat(session["timestamp"])
            + timedelta(hours=UserSessionManager.SESSION_EXPIRY_HOURS)
            < current_time
        ]
        for user_id in expired_users:
            del session_store[user_id]

        await db.execute(
            delete(UserSession).where(
                UserSession.timestamp
                + timedelta(hours=UserSessionManager.SESSION_EXPIRY_HOURS)
                < current_time
            )
        )
        await db.commit()
