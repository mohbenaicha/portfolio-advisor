from fastapi import Depends
from sqlalchemy import select
from app.models.sql_models import LLMMemory
from app.db.session import get_db, AsyncSession
from app.dependencies.user import get_current_user

# Add a new memory entry
async def add_user_memory(
    user_id: int = Depends(get_current_user),
    date = None,
    short_term: str = None,
    long_term: str = None,
    portfolio_id: int = None,
    db: AsyncSession = Depends(get_db),
):
    if short_term is None and long_term is None:
        raise ValueError("At least one of short_term or long_term must be provided")
    if portfolio_id is None:
        raise ValueError("Memory must be associated with a portfolio_id")
    memory = LLMMemory(
        user_id=user_id,
        date=date,
        assoc_portfolio_id=portfolio_id,
        short_term_goal=short_term,
        long_term_goal=long_term,
    )

    if db:
        db.add(memory)
        await db.commit()
    else:
        return memory

# Get all memory entries for a user and associated portfolio
async def get_user_memory(
    user_id: int = Depends(get_current_user), portfolio_id: int = None, db: AsyncSession = None
):
    if db is None:
        raise ValueError("Database session is required")
    result = await db.execute(
        select(LLMMemory).where(
            LLMMemory.user_id == user_id
            and (LLMMemory.assoc_portfolio_id == portfolio_id if portfolio_id else True)
        )
    )
    return result.scalars().all()


# Get the latest memory entry for a user and associated portfolio
async def get_latest_user_memory(
    user_id: int = Depends(get_current_user), portfolio_id: int = None, db: AsyncSession = Depends(get_db)
):
    if portfolio_id is None:
        raise ValueError("Memory must be associated with a portfolio_id")
    result = await db.execute(
        select(LLMMemory)
        .where(
            LLMMemory.user_id == user_id
            and (LLMMemory.assoc_portfolio_id == portfolio_id if portfolio_id else True)
        )
        .order_by(LLMMemory.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()
