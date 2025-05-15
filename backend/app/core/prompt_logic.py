from datetime import datetime, timedelta, timezone
from app.services.openai_client import extract_entities, generate_advice
from app.services.google_news_scraper import fetch_articles
from app.services.langchain_summary import summarize_articles
from app.utils.article_scraper import extract_with_readability
from app.db.mongo import get_cached_articles, store_article_summaries


async def handle_prompt(request):
    """
    Pipeline to handle user prompt through RAG including:
     1. extracting entities usin gpt-4o-mini,
     2. fetching news data using mongodb, or using alpha vantage if no keyword articles are stored in mongodb;
     3. summarizing news data, and caching summaries
     4. making final prompt to get investment advice with more detailed protfolio presentation and summary news (gpt-4o-mini)
    """
    # 1: Prompt 1 > extract asset_types, sectors, regions, themes, keywords
    entities = await extract_entities(request.question, request.portfolio_summary)

    print("Extracted entities:", entities)

    # 2: Check MongoDB for recent summaries
    # start_date = datetime.now(timezone.utc) - timedelta(days=1)
    # end_date = datetime.now(timezone.utc)
    # cached_articles = await get_cached_articles(
    #     entities, start_date=start_date, end_date=end_date
    # )

    # print("Cached articles:", cached_articles)


    # if not cached_articles:
    #     # 3: Fetch articles from Alpha Vantage
    #     fresh_articles = await fetch_articles(entities)

    #     # 4: Scrape full article content using readability
    #     for article in fresh_articles:
    #         article["raw_article"] = extract_with_readability(article["url"])

    #     # 5: Summarize articles using LangChain (Prompt 2 - multiple requests to open ai)
    #     summarized = await summarize_articles(fresh_articles)

    #     # 6: Cache summaries in MongoDB
    #     await store_article_summaries(summarized, entities.get("keywords"))
    # else:
    #     summarized = cached_articles

    # # 7: Prompt 3 > generate advice using gpt-4o-mini
    # advice = await generate_advice(request.question, request.portfolio_data, summarized)

    # return {"summary": advice, "articles": summarized}
