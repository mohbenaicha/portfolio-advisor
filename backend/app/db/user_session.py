from datetime import datetime, timedelta, timezone
from fastapi import Depends
from typing import Dict, Any
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
from app.config import SESSION_EXPIRY_HOURS
from collections import defaultdict


class UserSessionManager:

    session_expiry_hours = SESSION_EXPIRY_HOURS

    @staticmethod
    def get_session(user_id: int):
        return session_store[user_id]

    @staticmethod
    async def load_session_from_db(
        user_id: int = Depends(get_current_user),
        db: AsyncSession = None,
        llm_memory: Dict[str, Any] = {},
    ) -> Dict[str, Any]:
        if db is None or user_id is None:
            raise ValueError(
                "error in user_session.py/UserSessionManager::load_session_from_db: Database session and user_id are required"
            )

        result = await db.execute(
            select(UserSession).where(UserSession.user_id == user_id)
        )

        session = result.scalar_one_or_none()
        if session:
            session_store[user_id] = {  # type: ignore
                "llm_memory": dict(llm_memory),
                "timestamp": session.timestamp,
                "total_prompts_used": session.total_prompts_used,
                "failed_prompts": session.failed_prompts,
            }
            return session_store[user_id]
        else:
            print(f"No session found for user {user_id} in database")
            session_store[user_id] = {  # type: ignore
                "llm_memory": {},
                "timestamp": None,
                "total_prompts_used": 0,
                "failed_prompts": 0,
            }
            return session_store[user_id]

    @staticmethod
    async def update_session(
        user_id: int = None,
        db: AsyncSession = None,
        updates: dict = {},
    ):
        if user_id is None or db is None:
            raise ValueError("user_id and db are required for update_session")
        if user_id not in session_store:
            session_store[user_id] = {  # type: ignore
                "llm_memory": {},
                "timestamp": None,
                "total_prompts_used": 0,
                "failed_prompts": 0,
            }
        for k, v in updates.items():
            if k == "llm_memory":
                user_memory = await add_user_memory(
                    user_id=user_id,
                    date=datetime.now(timezone.utc).replace(tzinfo=None),
                    short_term=v.get("short_term"),
                    long_term=v.get("long_term"),
                    portfolio_id=v.get("portfolio_id"),
                    db=db,
                )
                if not isinstance(session_store[user_id]["llm_memory"], dict):
                    session_store[user_id]["llm_memory"] = {}  # type: ignore
                portfolio_key = v.get("portfolio_id")
                if portfolio_key is not None and isinstance(session_store[user_id]["llm_memory"], dict):
                    session_store[user_id]["llm_memory"][portfolio_key] = user_memory
            else:
                session_store[user_id][k] = v
        await db.execute(
            update(UserSession)
            .where(UserSession.user_id == user_id)
            .values(
                total_prompts_used=session_store[user_id]["total_prompts_used"],
                failed_prompts=session_store[user_id]["failed_prompts"],
            )
        )
        await db.commit()

    @staticmethod
    async def create_session(
        user_id: int = Depends(get_current_user),
        db: AsyncSession = None,
        llm_memory: Dict[str, Any] = {},
        timestamp: str = None,
    ):
        if user_id is None or db is None:
            raise ValueError("user_id and db are required for create_session")
        session_store[user_id] = {  # type: ignore
            "llm_memory": dict(llm_memory),
            "timestamp": timestamp or datetime.now(timezone.utc).replace(tzinfo=None),
            "total_prompts_used": 0,
            "failed_prompts": 0,
        }

        await db.execute(
            insert(UserSession).values(
                user_id=user_id,
                timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                total_prompts_used=0,
                failed_prompts=0,
            )
        )
        await db.commit()

    @staticmethod
    async def delete_session(user_id: int, db: AsyncSession):
        if user_id is None or db is None:
            raise ValueError("user_id and db are required for delete_session")
        if user_id in session_store:
            del session_store[user_id]
        await db.execute(delete(UserSession).where(UserSession.user_id == user_id))
        await db.commit()

    @staticmethod
    async def fix_null_sessions(db: AsyncSession):
        if db is None:
            raise ValueError("db is required for fix_null_sessions")
        current_time = datetime.now(timezone.utc).replace(tzinfo=None)
        result = await db.execute(
            select(UserSession).where(UserSession.timestamp == None)
        )
        null_sessions = result.scalars().all()
        for session in null_sessions:
            if not hasattr(session, 'user_id') or not isinstance(session.user_id, int):
                continue
            await UserSessionManager.update_session(
                user_id=session.user_id,
                db=db,
                updates={
                    "timestamp": current_time,
                    "total_prompts_used": session.total_prompts_used or 0,
                },
            )
            await db.execute(
                update(UserSession)
                .where(UserSession.user_id == session.user_id)
                .values(
                    timestamp=current_time,
                    total_prompts_used=session.total_prompts_used or 0,
                )
            )
        await db.commit()

    @staticmethod
    async def cleanup_sessions(db: AsyncSession = None):
        if db is None:
            raise ValueError("db is required for cleanup_sessions")
        current_time = datetime.now(timezone.utc).replace(tzinfo=None)
        expired_users = [
            user_id
            for user_id, session in session_store.items()
            if isinstance(session, dict)
            and session.get("timestamp")
            and isinstance(session["timestamp"], datetime)
            and not isinstance(session["timestamp"], (int, defaultdict))
            and session["timestamp"] + timedelta(hours=UserSessionManager.session_expiry_hours) < current_time
        ]
        for user_id in expired_users:
            del session_store[user_id]
        await db.execute(
            delete(UserSession).where(
                UserSession.timestamp != None,
                UserSession.timestamp + timedelta(hours=UserSessionManager.session_expiry_hours) < current_time
            )
        )
        await db.commit()

    @staticmethod
    async def get_llm_memory(
        user_id: int, portfolio_id: int
    ) -> LLMMemory:
        memory = session_store[user_id].get("llm_memory").get(portfolio_id, {}) if user_id in session_store else False
        return memory
    
    @staticmethod
    async def get_total_prompts_used(
        user_id: int
    ) -> int:
        """
        Retrieves the total number of prompts used by a user.
        """
        return session_store[user_id].get("total_prompts_used", 0) if user_id in session_store else 0

    @staticmethod
    async def get_failed_prompts(
        user_id: int
    ) -> int:
        """
        Retrieves the total number of failed prompts used by a user.
        """
        return session_store[user_id].get("failed_prompts", 0) if user_id in session_store else 0

    @staticmethod
    async def increment_failed_prompts(
        user_id: int,
        db: AsyncSession
    ) -> None:
        session_store[user_id]["failed_prompts"] = session_store[user_id].get("failed_prompts", 0) + 1
        await db.execute(
            update(UserSession)
            .where(UserSession.user_id == user_id)
            .values(failed_prompts=session_store[user_id]["failed_prompts"])
        )
        await db.commit()