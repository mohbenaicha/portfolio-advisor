from app.models.sql_models import Base
from sqlalchemy.ext.asyncio import create_async_engine


async def init_db(url: str):
    engine = create_async_engine(url)
    print("DEBUG: URL ->", engine.url)
    async with engine.begin() as conn:
        print("DEBUG: Connected to:", conn)
        await conn.run_sync(Base.metadata.create_all)
