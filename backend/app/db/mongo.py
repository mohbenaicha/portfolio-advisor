from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta, timezone
from os import getenv
from dotenv import load_dotenv

load_dotenv()
client = AsyncIOMotorClient(getenv("MONGO_URI"))
db = client["news_cache"]


async def get_cached_articles(entities, start_date=None, end_date=None):
    tags = [keyword for entity in entities for keyword in entity.get("keywords", [])]
    
    tags = ["renewable energy projects US","clean energy infrastructure investment","solar and wind farms US","renewable energy asset performance","US green energy initiatives",]
    
    
    print("Checking for cached articles with tags:", tags)
    query = {"query_tags": {"$in": tags}}

    if start_date or end_date:
        date_filter = {}
        if start_date:
            date_filter["$gte"] = start_date
        if end_date:
            date_filter["$lte"] = end_date
        query["stored_at"] = date_filter

    return await db.articles.find(query).to_list(length=20)


async def store_article_summaries(summaries):
    for article in summaries:
        if article:
            article["query_tags"] = article.get("keywords", [])
            article["stored_at"] = datetime.now(timezone.utc).replace(tzinfo=None)
            # Remove unnecessary fields
            article.pop("keywords", None)
            article.pop("raw_article", None)
            article.pop("position", None)
            article.pop("body", None)

            await db.articles.update_one(
                {"url": article["link"]}, {"$set": article}, upsert=True  # Match by URL
            )
