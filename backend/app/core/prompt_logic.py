from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.openai_client import (
    validate_prompt,
    extract_entities,
    generate_advice,
)
from app.services.google_news_scraper import fetch_articles
from app.services.langchain_summary import summarize_articles
from app.db.mongo import get_cached_articles, store_article_summaries
from app.db.user_session import UserSessionManager
from app.utils.article_scraper import extract_with_readability
from app.utils.advisor_utils import convert_markdown_to_html


async def handle_prompt(request, db: AsyncSession, user_id: int):
    """
    Pipeline to handle user prompt through RAG including:
     1. extracting entities usin gpt-4o-mini,
     2. fetching news data using mongodb, or using alpha vantage if no keyword articles are stored in mongodb;
     3. summarizing news data, and caching summaries
     4. making final prompt to get investment advice with more detailed protfolio presentation and summary news (gpt-4o-mini)
    """
    # Check the number of prompts used by the user
    session = UserSessionManager.get_session(user_id)
    if session["total_prompts_used"] >= 3:
        return {
            "archived": False,
            "summary": "<p>You have reached the maximum number of prompts you can use today, please check back tomorrow. "
            "If you need additional quota for today, you can request additional quota by emailing mohamed.benaicha@hotmail.com</p>",
        }

    # 1: Prompt 1 > extract asset_types, sectors, regions, themes, keywords
    print(
        "------------------------ Extracting Entities using GPT-4o -------------------------------------------"
    )

    is_question_valid, is_objective_clea = validate_prompt(question=request.question)
    if is_question_valid:
        await UserSessionManager.update_session(
            user_id=user_id,
            db=db,
            updates={"total_prompts_used": session["total_prompts_used"] + 1},
        )
        return {
            "archived": False,
            "summary": "<p>Invalid question. Please ask a relevant investment question.</p>",
        }

    if not is_objective_clea:
        await UserSessionManager.update_session(
            user_id=user_id,
            db=db,
            updates={"total_prompts_used": session["total_prompts_used"] + 1},
        )
        return {
            "archived": False,
            "summary": "<p>Unable to determine your investment objective. Please clarify your investment goals.</p>",
        }

    entities, portfolio, portfolio_summary = await extract_entities(
        question=request.question,
        portfolio_id=request.portfolio_id,
        db=db,
        user_id=user_id,
    )  # portfolio summary does not have detailed asset breakdown

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
    start_date = datetime.now(timezone.utc) - timedelta(days=8)
    end_date = datetime.now(timezone.utc)

    print(
        "------------------------ Looking for Cached Articles -------------------------------------------"
    )
    # keys: link, posted (date published), query, query_tags, source (publisher), stored_at (d/t), summary, title
    cached_articles = await get_cached_articles(
        entities["entities"], start_date=start_date, end_date=end_date
    )
    print("Found {} chached articles".format(len(cached_articles)))

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
        summarized_articles = await summarize_articles(fresh_articles)

        print("Summarized articles:", summarized_articles)
        print(
            "------------------------ Storing Articles -------------------------------------------"
        )
        # 6: Cache summaries in MongoDB
        await store_article_summaries(summarized_articles)
    else:
        summarized_articles = cached_articles

    print(
        "------------------------ Generating Final Advice -------------------------------------------"
    )
    advice = await generate_advice(
        request.question, db, request.portfolio_id, user_id, summarized_articles
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
        },
    )

    return {"archived": True, "summary": convert_markdown_to_html(advice)}
