from datetime import datetime, timedelta, timezone
import json

from app.db.mongo import db, get_cached_articles, store_article_summaries

async def clear_test_db():
    """Clear the test database before each test."""
    await db.articles.delete_many({})

def load_articles_from_file(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


# Mock database setup
articles = load_articles_from_file("./tests/article_summary.json")
entities = json.load(open("./tests/entities.json", "r"))


async def test_get_cached_articles():
    start_date = datetime.now(timezone.utc) - timedelta(days=1)
    end_date = datetime.now(timezone.utc)

    # Call the function
    result = await get_cached_articles(entities, start_date, end_date)
    print("Cached articles in DB:\n", result)
    # Assertions
    assert len(result) == 2
    # Assertions
    assert len(result) == len(articles)
    for i, article in enumerate(result):
        assert article["title"] == articles[i]["title"]

    print("Test Passed: Cached articles retrieved successfully from MongoDB.")

async def test_store_article_summaries():
    await clear_test_db()
    # Call the function
    await store_article_summaries(articles, entities.get("keywords"))

    # Verify data in the database
    stored_articles = await db.articles.find().to_list(length=10)
    print("Stored articles in DB:\n", stored_articles)
    assert len(stored_articles) == len(articles)
    for i, article in enumerate(stored_articles):
        assert article["query_tags"] == entities.get("keywords")
        assert "stored_at" in article
    print("Test Passed: Articles stored successfully in MongoDB.")

async def run_tests():
    await test_store_article_summaries()
    await test_get_cached_articles()


