from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta, timezone
from os import getenv
from dotenv import load_dotenv

load_dotenv()
client = AsyncIOMotorClient(getenv("MONGO_URI"))
db = client["news_cache"]

async def get_cached_articles(entities, start_date=None, end_date=None):
    tags = entities.get("keywords", [])
    query = {"query_tags": {"$in": tags}}

    if start_date or end_date:
        date_filter = {}
        if start_date:
            date_filter["$gte"] = start_date
        if end_date:
            date_filter["$lte"] = end_date
        query["stored_at"] = date_filter

    return await db.articles.find(query).to_list(length=20)

async def store_article_summaries(summaries, query_tags):
    for article in summaries:
        article["query_tags"] = query_tags
        article["stored_at"] = datetime.now(timezone.utc)

        await db.articles.update_one(
            {"url": article["url"]},  # Match by URL
            {"$set": article},
            upsert=True
        )