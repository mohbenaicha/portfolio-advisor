from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from os import getenv
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = getenv("DATABASE_URI")

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session