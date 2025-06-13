from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import numpy as np
from app.services.article_processor import batch_embed  # reuse embedding logic
from app.utils.article_utils import cosine_sim
from app.config import MONGO_URI

client = AsyncIOMotorClient(MONGO_URI)
db = client["news_cache"]

print("Connected to MongoDB at:", MONGO_URI)


async def get_similar_articles(prompt_text: str, start_date=None, end_date=None, top_k=10):
    # TODO: $vectorSearch in Atlas v7+
    prompt_embedding = np.array((await batch_embed([prompt_text]))[0])
    
    query = {}
    if start_date or end_date:
        date_filter = {}
        if start_date:
            date_filter["$gte"] = start_date
        if end_date:
            date_filter["$lte"] = end_date
        query["stored_at"] = date_filter

    articles = await db.articles.find(query).to_list(length=100)

    scored = []
    for article in articles:
        emb = article.get("summary_embedding")
        if emb:
            score = cosine_sim(prompt_embedding, emb)
            article["similarity"] = score
            scored.append(article)

    
    top_articles = sorted(scored, key=lambda x: x["similarity"], reverse=True)[:top_k] # descending order
    return top_articles


async def store_article_summaries(summaries):
    for article in summaries:
        if article:
            article["query_tags"] = article.get("keywords", [])
            article["stored_at"] = datetime.now(timezone.utc).replace(tzinfo=None)
            article["summary_embedding"] = article.get("summary_embedding", [])
            # Remove unnecessary fields
            article.pop("keywords", None)
            article.pop("raw_article", None)
            article.pop("position", None)
            article.pop("body", None)

            await db.articles.update_one(
                {"url": article["link"]}, {"$set": article}, upsert=True  # Match by URL
            )
