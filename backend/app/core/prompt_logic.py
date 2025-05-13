from app.services.openai_client import extract_entities, generate_advice
from app.services.alpha_vantage import fetch_articles
from app.services.langchain_summary import summarize_articles
from app.services.article_scraper import extract_with_readability
from app.db.mongo import get_cached_articles, store_article_summaries

async def handle_prompt(request):
    # Step 1: Prompt 1 → extract asset_types, sectors, regions, themes, keywords
    entities = await extract_entities(request.question, request.portfolio_summary)

    # Step 2: Check MongoDB for recent summaries
    cached_articles = await get_cached_articles(entities)

    if not cached_articles:
        # Step 3: Fetch articles from Alpha Vantage
        fresh_articles = await fetch_articles(entities)

        # Step 4: Scrape full article content using readability
        for article in fresh_articles:
            article["raw_article"] = extract_with_readability(article["url"])

        # Step 5: Summarize articles using LangChain
        summarized = await summarize_articles(fresh_articles)

        # Step 6: Cache summaries in MongoDB
        await store_article_summaries(summarized)
    else:
        summarized = cached_articles

    # Step 7: Prompt 2 → generate advice using OpenAI
    advice = await generate_advice(request.question, request.portfolio_data, summarized)

    return {
        "summary": advice,
        "articles": summarized
    }
