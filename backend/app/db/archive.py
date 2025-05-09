from app.models.archive_models import ArchivedResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

async def save_archive(db: AsyncSession, archive_data):
    record = ArchivedResponse(
        portfolio_id=archive_data.portfolio_id,
        original_question=archive_data.original_question,
        openai_response=archive_data.openai_response,
        associated_article_ids=archive_data.article_ids,
        summary_tags=archive_data.summary_tags,
        timestamp=datetime.utcnow()
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record

async def list_archives(db: AsyncSession):
    result = await db.execute(
        select(ArchivedResponse).order_by(ArchivedResponse.timestamp.desc())
    )
    return result.scalars().all()

async def get_archive_by_id(db: AsyncSession, archive_id: int):
    result = await db.execute(
        select(ArchivedResponse).filter(ArchivedResponse.id == archive_id)
    )
    return result.scalar_one_or_none()
