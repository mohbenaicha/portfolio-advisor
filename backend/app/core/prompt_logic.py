from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.openai_client import extract_entities, generate_advice
from app.services.google_news_scraper import fetch_articles
from app.services.langchain_summary import summarize_articles
from app.db.mongo import get_cached_articles, store_article_summaries
from app.db.user_session import UserSessionManager
from app.utils.portfolio_utils import get_asset_representation
from app.utils.article_scraper import extract_with_readability


async def handle_prompt(request, db: AsyncSession, user_id: int):
    """
    Pipeline to handle user prompt through RAG including:
     1. extracting entities usin gpt-4o-mini,
     2. fetching news data using mongodb, or using alpha vantage if no keyword articles are stored in mongodb;
     3. summarizing news data, and caching summaries
     4. making final prompt to get investment advice with more detailed protfolio presentation and summary news (gpt-4o-mini)
    """
    # 1: Prompt 1 > extract asset_types, sectors, regions, themes, keywords
    print(
        "------------------------ Extracting Entities using GPT-4o -------------------------------------------"
    )
    entities, portfolio, portfolio_summary = await extract_entities(
        question=request.question, portfolio_id=request.portfolio_id, db=db, user_id=user_id
    )  # portfolio summary does not have detailed asset breakdown

    if db is None or user_id is None:
        raise ValueError(
            "error in prompt_logic.py/handle_prompt: Database session or user id is missing"
        )
    # add latest llm memory to db and update session
    if entities["short_term_objective"] != "" or entities["long_term_objective"] != "":
        await UserSessionManager.update_session(
            user_id=user_id,
            db=db,
            updates={
                "llm_memory": {
                    "short_term": entities["short_term_objective"],
                    "long_term": entities["long_term_objective"],
                    "portfolio_id": request.portfolio_id,
                }
            },
        )
    print(
        "------------------------ Entities Extracted -------------------------------------------"
    )
    print("Entities: \n", entities)
    print("short_term_objective: \n", entities["short_term_objective"])
    print("long_term_objective: \n", entities["long_term_objective"])
    print("Sessions: \n", UserSessionManager.get_session(user_id))
    # 2: Check MongoDB for recent summaries
    start_date = datetime.now(timezone.utc) - timedelta(days=1)
    end_date = datetime.now(timezone.utc)

    print(
        "------------------------ Looking for Cached Articles -------------------------------------------"
    )
    # keys: link, posted (date published), query, query_tags, source (publisher), stored_at (d/t), summary, title
    cached_articles = await get_cached_articles(
        entities["entities"], start_date=start_date, end_date=end_date
    )

    if len(cached_articles) < 10:
        print(
            "------------------------ Fetching Articles from Google Search News -------------------------------------------"
        )

        # 3: Fetch articles from Alpha Vantage
        # list of dicts; keys: query, position, title, body, posted, source, link
        fresh_articles = await fetch_articles(entities["entities"])

        # 4: Scrape full article content using readability
        print(
            "------------------------ Extracting Article Content -------------------------------------------"
        )
        for article in fresh_articles:
            # key added added to each article dict: raw_article - full scraped article content
            try:
                article["raw_article"] = await extract_with_readability(article["link"])
            except Exception as e:
                print(f"Error extracting article content: {e}")
                article["raw_article"] = "Readability extraction failed."

        print("Starting to summarize articles...")
        # 5: Summarize articles using LangChain (Prompt 2 - multiple requests to open ai)
        # key added: summary - summarized version of each article by GPT-4o
        print(
            "------------------------ Summarizing Articles -------------------------------------------"
        )
        summarized = await summarize_articles(fresh_articles)

        print("Summarized articles:", summarized)
        print(
            "------------------------ Storing Articles -------------------------------------------"
        )
        # 6: Cache summaries in MongoDB
        await store_article_summaries(summarized)
    else:
        summarized = cached_articles
    

    print(
        "------------------------ Generating Final Advice -------------------------------------------"
    )
    # # 7: Prompt 3 > generate advice using gpt-4o-mini

    portfolio_summary = "\n".join(
        [get_asset_representation(portfolio), portfolio_summary]
    )
    article_summaries = "\n\n".join(
        [
            "\n".join([article["title"], article["summary"], article["link"]])
            for article in summarized
            if article["summary"] != "Readability extraction failed"
        ][:3]
    )

    print("Summaries:::::\n\n\n", article_summaries)    

    print(
        "------------------------ Generating Final Advice -------------------------------------------"
    )
    advice = await generate_advice(
        request.question, portfolio_summary, article_summaries, user_id
    )
    print("Advice:::::\n\n\n", advice)
    await UserSessionManager.update_session(
        user_id=user_id,
        db=db,
        updates={
            "total_prompts_used": UserSessionManager.get_session(user_id)[
                "total_prompts_used"
            ]
            + 1
        }
    )
    return {"summary": advice}
