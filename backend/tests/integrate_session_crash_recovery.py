import asyncio
import httpx
from datetime import datetime, timezone
from app.db.session import get_db
from app.core.session_state import session_store
from app.db.user_session import UserSessionManager
from app.models.sql_models import UserSession
from sqlalchemy.future import select

# Constants
BASE_URL = "http://localhost:8000"
TOKEN = "df77c9be-67fb-44b9-a15c-8146131e2d14"  # User1
PORTFOLIO_ID = 9
SHORT_TERM = "Reduce exposure to volatile tech stocks"
LONG_TERM = "Build a stable dividend-focused portfolio"

async def test_auth_and_crash_recovery():
    print("\n=== Step 1: Authenticate and Create Session ===")
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{BASE_URL}/auth", json={"token": TOKEN})
        assert res.status_code == 200, f"X Auth failed: {res.text}"
        user_id = res.json()["user_id"]

    async for db in get_db():
        print("Session created:", session_store[user_id])

        print("\n=== Step 2: Update Session with Prompt Count + Mock Memory ===")
        await UserSessionManager.update_session(
            user_id=user_id,
            db=db,
            updates={
                "total_prompts_used": 7,
                "llm_memory": {
                    "short_term": SHORT_TERM,
                    "long_term": LONG_TERM,
                    "portfolio_id": PORTFOLIO_ID,
                },
            },
        )
        print("Session after update:", session_store[user_id])

        print("\n=== Step 3: Simulate Crash (clear session_store) ===")
        session_store.clear()
        assert user_id not in session_store, "X Session store not cleared"

        print("\n=== Step 4: Re-authenticate (should restore session from DB) ===")
        async with httpx.AsyncClient() as client:
            res2 = await client.post(f"{BASE_URL}/auth", json={"token": TOKEN})
            assert res2.status_code == 200, f"X Re-auth failed: {res2.text}"
            restored_id = res2.json()["user_id"]
            assert restored_id == user_id, "X Restored user mismatch"

        print("8-D Session restored:", session_store[user_id])

        print("\n=== Step 5: DB Verification ===")
        result = await db.execute(select(UserSession).where(UserSession.user_id == user_id))
        session_row = result.scalar_one_or_none()
        if not session_row:
            print(f"X No session found in DB for user_id={user_id}")
        assert session_row.total_prompts_used == 7, "X DB prompt count mismatch"

        print(f"8-D DB session record: prompts={session_row.total_prompts_used}, timestamp={session_row.timestamp}")