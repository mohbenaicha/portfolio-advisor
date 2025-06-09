
from app.models.sql_models import Base
from app.db.session import engine



async def init_db():
    print("URL ➜", engine.url)
    async with engine.begin() as conn:
        result = await conn.run_sync(Base.metadata.create_all)
        print("Connected to:", result)

