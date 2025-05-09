# app/db/init.py

from app.models.sql_models import Base
from app.db.session import engine
from app.models.archive_models import ArchivedResponse  # force model registration

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
