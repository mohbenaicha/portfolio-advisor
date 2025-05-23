import asyncio
import httpx
from datetime import datetime, timezone
from app.db.session import get_db
from app.db.user_session import UserSessionManager
from app.models.sql_models import UserSession
from sqlalchemy.future import select

# Constants
BASE_URL = "http://localhost:8000"
TOKEN = "df77c9be-67fb-44b9-a15c-8146131e2d14"  # User1
PORTFOLIO_ID = 3
SHORT_TERM = "Reduce exposure to volatile tech stocks"
LONG_TERM = "Build a stable dividend-focused portfolio"

async def test_auth_and_crash_recovery():
    print("\n=== Step 1: Authenticate and Create Session ===")
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{BASE_URL}/auth", json={"token": TOKEN})
        assert res.status_code == 200, f"X Auth failed: {res.text}"
        user_id = int(res.json()["user_id"])

    print("\n=== Step 2: Update Session with Prompt Count + Mock Memory ===")
    async with httpx.AsyncClient() as client:
        update_res = await client.post(
            f"{BASE_URL}/session/update",
            params={
                "user_id": user_id,
                "total_prompts_used": 7,
                "short_term": SHORT_TERM,
                "long_term": LONG_TERM,
                "portfolio_id": PORTFOLIO_ID,
            },
        )
        assert update_res.status_code == 200, f"X Update failed: {update_res.text}"

    print("\n=== Step 3: Simulate Crash (clear session_store via endpoint) ===")
    async with httpx.AsyncClient() as client:
        crash_res = await client.post(f"{BASE_URL}/session/simulate_crash")
        assert crash_res.status_code == 200, f"X Crash simulation failed: {crash_res.text}"

    print("\n=== Step 4: Re-authenticate (should restore session from DB) ===")
    async with httpx.AsyncClient() as client:
        res2 = await client.post(f"{BASE_URL}/auth", json={"token": TOKEN})
        assert res2.status_code == 200, f"X Re-auth failed: {res2.text}"
        restored_id = res2.json()["user_id"]
        assert restored_id == user_id, "X Restored user mismatch"

    print("\n=== Step 5: Verify Session Store State via Endpoint ===")
    async with httpx.AsyncClient() as client:
        session_res = await client.get(f"{BASE_URL}/session/state")
        assert session_res.status_code == 200, f"X Failed to fetch session state: {session_res.text}"
        session_state = session_res.json()
        assert str(user_id) in session_state, "X Restored session not found in session_store"
        restored_session = session_state[str(user_id)]
        assert restored_session["total_prompts_used"] == 7, "X Restored session prompt count mismatch"

    print("\n=== Step 6: DB Verification ===")
    async for db in get_db():
        result = await db.execute(select(UserSession).where(UserSession.user_id == user_id))
        session_row = result.scalar_one_or_none()
        assert session_row, f"X No session found in DB for user_id={user_id}"
        assert session_row.total_prompts_used == 7, "X DB prompt count mismatch"

    print("8-D Test passed: Session recovery verified!")