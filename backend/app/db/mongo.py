from motor.motor_asyncio import AsyncIOMotorClient
from os import getenv
from dotenv import load_dotenv

load_dotenv()
client = AsyncIOMotorClient(getenv("MONGO_URI"))
db = client["news_cache"]

async def get_cached_articles(entities):
    tags = entities.get("keywords", [])
    return await db.articles.find({"query_tags": {"$in": tags}}).to_list(length=20)

async def store_article_summaries(summaries):
    for article in summaries:
        await db.articles.update_one(
            {"url": article["url"]},
            {"$set": article},
            upsert=True
        )
