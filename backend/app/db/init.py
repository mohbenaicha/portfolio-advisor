# app/db/init.py

from app.models.sql_models import Base
from app.db.session import engine


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
