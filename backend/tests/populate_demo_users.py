
import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal
import uuid

async def populate_users():
    async with AsyncSessionLocal() as session:
        for i in range(3, 53):
            name = f"user{i}"
            token = str(uuid.uuid4())
            await session.execute(
                text("INSERT INTO users (name, token) VALUES (:name, :token)"),
                {"name": name, "token": token}
            )
            print(f"Created {name} with token: {token}")
        await session.commit()

if __name__ == "__main__":
    import uuid
    asyncio.run(populate_users())
