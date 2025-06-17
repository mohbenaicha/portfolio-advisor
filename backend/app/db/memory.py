from fastapi import Depends
from sqlalchemy import select, update
from app.models.sql_models import LLMMemory
from app.db.session import get_db, AsyncSession
from app.dependencies.user import get_current_user


async def add_user_memory(
    user_id: int = Depends(get_current_user),
    date=None,
    short_term: str = None,
    long_term: str = None,
    portfolio_id: int = None,
    db: AsyncSession = Depends(get_db),
) -> LLMMemory:
    result = await db.execute(
        update(LLMMemory)
        .where(
            LLMMemory.user_id == user_id, LLMMemory.assoc_portfolio_id == portfolio_id
        )
        .values(date=date, short_term_goal=short_term, long_term_goal=long_term)
    )

    if result.rowcount == 0:
        memory = LLMMemory(
            user_id=user_id,
            date=date,
            assoc_portfolio_id=portfolio_id,
            short_term_goal=short_term,
            long_term_goal=long_term,
        )
        db.add(memory)
        await db.commit()
        return memory

    await db.commit()

    updated_memory = await db.execute(
        select(LLMMemory).where(
            LLMMemory.user_id == user_id, LLMMemory.assoc_portfolio_id == portfolio_id
        )
    )
    return updated_memory.scalar_one_or_none()


async def get_user_memory(
    user_id: int = Depends(get_current_user),
    portfolio_id: int = None,
    db: AsyncSession = None,
):
    result = await db.execute(
        select(LLMMemory).where(
            LLMMemory.user_id == user_id
            and (LLMMemory.assoc_portfolio_id == portfolio_id if portfolio_id else True)
        )
    )
    result = result.scalars().all()
    memory_dict = {row.assoc_portfolio_id: row for row in result}
    return memory_dict


# Get the latest memory entry for a user and associated portfolio
async def get_latest_user_memory(
    user_id: int = Depends(get_current_user),
    portfolio_id: int = None,
    db: AsyncSession = Depends(get_db),
):
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
