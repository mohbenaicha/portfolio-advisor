from app.models.sql_models import ArchivedResponse, Portfolio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone


async def save_archive(db: AsyncSession, archive_data, user_id: int):
    # Check if the portfolio_id exists
    portfolio_exists = await db.execute(
        select(Portfolio).where(
            Portfolio.id == archive_data.portfolio_id, Portfolio.user_id == user_id
        )
    )
    portfolio = portfolio_exists.scalar()
    print(f"DEBUG: Portfolio Query Result: {portfolio}")  # Debugging line
    if not portfolio:
        raise ValueError(
            f"Portfolio with id {archive_data.portfolio_id} does not exist."
        )

    record = ArchivedResponse(
        portfolio_id=archive_data.portfolio_id,
        user_id=user_id,
        original_question=archive_data.original_question,
        openai_response=archive_data.openai_response,
        timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
    )

    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_archived_responses(user_id: int, db: AsyncSession):
    result = await db.execute(
        select(ArchivedResponse).where(ArchivedResponse.user_id == user_id)
    )
    return result.scalars().all()


async def list_archives(db: AsyncSession):
    result = await db.execute(
        select(ArchivedResponse).order_by(ArchivedResponse.timestamp.desc())
    )
    return result.scalars().all()


async def get_archive_by_id(db: AsyncSession, archive_id: int, user_id: int):
    result = await db.execute(
        select(ArchivedResponse).filter(
            ArchivedResponse.id == archive_id, ArchivedResponse.user_id == user_id
        )
    )
    return result.scalar_one_or_none()
