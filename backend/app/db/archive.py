from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone
from app.models.sql_models import ArchivedResponse, Portfolio
from app.db.session import get_db
from app.dependencies.user import get_current_user

# TODO: order arguments consitently
async def save_archive(db: AsyncSession = Depends(get_db), archive_data = None, user_id: int = Depends(get_current_user)):
    if archive_data:
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
    else:
        raise ValueError("No archive data provided.")


async def get_archived_responses(user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ArchivedResponse).where(ArchivedResponse.user_id == user_id)
    )
    return result.scalars().all()


async def list_archives(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ArchivedResponse).order_by(ArchivedResponse.timestamp.desc())
    )
    return result.scalars().all()


async def get_archive_by_id(db: AsyncSession = Depends(get_db), archive_id: int = None, user_id: int = Depends(get_current_user)):
    result = await db.execute(
        select(ArchivedResponse).filter(
            ArchivedResponse.id == archive_id, ArchivedResponse.user_id == user_id
        )
    )
    return result.scalar_one_or_none()
