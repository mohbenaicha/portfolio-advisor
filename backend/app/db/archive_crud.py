from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from datetime import datetime, timezone
from app.models.sql_models import ArchivedResponse, Portfolio
from html import escape


async def delete_archive_by_id(db: AsyncSession, archive_id: int, user_id: int) -> bool:

    query = delete(ArchivedResponse).where(
        ArchivedResponse.id == archive_id, ArchivedResponse.user_id == user_id
    )
    result = await db.execute(query)
    await db.commit()

    return result.rowcount > 0


async def delete_all_archives_by_user_id(db: AsyncSession, user_id: int) -> bool:
    query = delete(ArchivedResponse).where(ArchivedResponse.user_id == user_id)
    _ = await db.execute(query)
    await db.commit()
    
    return True  # Always return True as we're deleting all archives for the user


# TODO: order arguments consitently
async def save_archive(db: AsyncSession = None, archive_data=None, user_id: int = None):
    if archive_data:
        portfolio_exists = await db.execute(
            select(Portfolio).where(
                Portfolio.id == archive_data.portfolio_id, Portfolio.user_id == user_id
            )
        )
        portfolio = portfolio_exists.scalar()
        if not portfolio:
            raise ValueError(
                f"Portfolio with id {archive_data.portfolio_id} does not exist."
            )

        record = ArchivedResponse(
            portfolio_id=archive_data.portfolio_id,
            user_id=user_id,
            original_question=archive_data.original_question,
            openai_response=escape(archive_data.openai_response),
            title=archive_data.title,
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
        )

        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record
    else:
        raise ValueError("No archive data provided.")


async def get_archived_responses(user_id: int = None, db: AsyncSession = None):
    result = await db.execute(
        select(ArchivedResponse).where(ArchivedResponse.user_id == user_id)
    )
    return result.scalars().all()


async def get_archive_by_id(
    db: AsyncSession = None,
    archive_id: int = None,
    user_id: int = None,
):
    result = await db.execute(
        select(ArchivedResponse).filter(
            ArchivedResponse.id == archive_id, ArchivedResponse.user_id == user_id
        )
    )
    return result.scalar_one_or_none()
