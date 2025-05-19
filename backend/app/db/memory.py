from sqlalchemy import select
from app.models.sql_models import LLMMemory
from app.db.session import get_db

# Add a new memory entry
async def add_user_memory(user_id: int, date, short_term: str, long_term: str):
    async for db in get_db():
        memory = LLMMemory(
            user_id=user_id,
            date=date,
            short_term_goal=short_term,
            long_term_goal=long_term,
        )
        db.add(memory)
        await db.commit()

# Get all memory entries for a user
async def get_user_memory(user_id: int):
    async for db in get_db():
        result = await db.execute(
            select(LLMMemory).where(LLMMemory.user_id == user_id)
        )
        return result.scalars().all()

# Get the latest memory entry for a user
async def get_latest_user_memory(user_id: int):
    async for db in get_db():
        result = await db.execute(
            select(LLMMemory)
            .where(LLMMemory.user_id == user_id)
            .order_by(LLMMemory.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
