import asyncio
from datetime import datetime, timezone
from app.services.openai_client import extract_entities
from app.db.session import get_db
from app.db.portfolio_crud import get_user_portfolios
from app.db.archive import get_archived_responses
from app.db.memory import get_user_memory, add_user_memory
from app.db.user_session import UserSessionManager
from app.models.sql_models import UserSession
from app.core.session_state import session_store
from sqlalchemy.future import select

USER_ID = 1
PORTFOLIO_ID = 9
QUESTION = "Should I rotate capital into AI hardware manufacturers this quarter?"

OTHER_USER_ID = 2
OTHER_PORTFOLIO_ID = 3

async def test_user1_memory_flow():
    async for db in get_db():
        print("\n===  User1: OWNED DATA ===")

        print("\n Portfolios:")
        portfolios = await get_user_portfolios(db, user_id=USER_ID)
        for p in portfolios:
            print(f"- {p.name} (id={p.id})")

        print("\n Memories:")
        memories = await get_user_memory(user_id=USER_ID, portfolio_id=PORTFOLIO_ID, db=db)
        for m in memories:
            print(f"- {m.date}: {m.short_term_goal} | {m.long_term_goal}")

        print("\n Archives:")
        archives = await get_archived_responses(user_id=USER_ID, db=db)
        for a in archives:
            print(f"- {a.timestamp}: {a.original_question[:60]}")

        print("\n===  Attempt to Access User2 Data ===")
        try:
            other_mem = await get_user_memory(user_id=OTHER_USER_ID, portfolio_id=OTHER_PORTFOLIO_ID, db=db)
            print(f"X Should not access memories: {other_mem}")
        except Exception as e:
            print(f" Access to other user’s memory blocked: {e}")

        try:
            other_arch = await get_archived_responses(user_id=OTHER_USER_ID, db=db)
            print(f"X Should not access archives: {other_arch}")
        except Exception as e:
            print(f" Access to other user’s archives blocked: {e}")

        print("\n===  Extracting New Memory with LLM ===")
        json_result, _, _ = await extract_entities(QUESTION, PORTFOLIO_ID, db)
        print("Extracted entities:", json_result["entities"])

        print("\n===  Adding Memory to Session Store ===")
        UserSessionManager.create_session(user_id=USER_ID, db=db, llm_memory=[], timestamp=datetime.now(timezone.utc).replace(tzinfo=None))
        await UserSessionManager.update_session(
            user_id=USER_ID,
            db=db,
            updates={
                "llm_memory": {
                    "short_term": json_result["short_term_objective"],
                    "long_term": json_result["long_term_objective"],
                    "portfolio_id": PORTFOLIO_ID,
                },
                "total_prompts_used": 99
            }
        )

        print(" Session Store In-Memory:")
        print(session_store[USER_ID])

        print("\n===  Verifying DB Backup of Session ===")
        result = await db.execute(select(UserSession).where(UserSession.user_id == USER_ID))
        record = result.scalar_one_or_none()
        print(f"UserSession DB record: ts={record.timestamp}, total_prompts={record.total_prompts_used}")

