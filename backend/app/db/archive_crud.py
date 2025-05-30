from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sql_models import ArchivedResponse

async def delete_archive_by_id(db: AsyncSession, archive_id: int, user_id: int) -> bool:

    query = delete(ArchivedResponse).where(ArchivedResponse.id == archive_id, ArchivedResponse.user_id == user_id)
    result = await db.execute(query)
    await db.commit()

    return result.rowcount > 0