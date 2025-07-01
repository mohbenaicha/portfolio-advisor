import json, re
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Tuple, Union
from fastapi.encoders import jsonable_encoder
from app.db.portfolio_crud import get_portfolio_by_id
from app.utils.portfolio_utils import get_exposure_summary, get_portfolio_summary
from app.db.session import AsyncSession
from app.db.user_session import UserSessionManager
from app.utils.memory_utils import get_investment_objective
from app.config import ALT_LLM, LLM, OPEN_AI_API_KEY
from app.db.mongo import get_similar_articles, store_article_summaries
from app.services.google_news_scraper import fetch_articles
from app.services.article_processor import summarize_and_embed_articles
from app.utils.article_utils import extract_with_readability
from app.utils.advisor_utils import construct_prompt_for_embedding, count_tokens
from openai import OpenAI

client = OpenAI(api_key=OPEN_AI_API_KEY)


async def validate_prompt(
    question: str, portfolio_id: int, user_id: int, db: AsyncSession
) -> Dict[str, bool]:
    """
    Validates if the user's prompt is a valid investment question and the user's investment objective is clear.
    """
    portfolio_summary = get_portfolio_summary(
        jsonable_encoder(await get_portfolio_by_id(db, portfolio_id, user_id))
    )

    prompt = f"""
            You are a professional investment advisor. It is {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}

            User question:
            "{question}"

            User's portfolio:
            {portfolio_summary}

            Instructions:
            Determine if the user's question is related to finance, investing, and the user's portfolio.
            Return a JSON object with a 
              - key "valid" whose value is a boolean indicating whether the user's question is valid and relevant investment question
            Only return a json object...
            """


    # send the prompt to OpenAI API for processing
    response = client.chat.completions.create(
        model=ALT_LLM, messages=[{"role": "user", "content": prompt}]
    )
    raw_content = response.choices[0].message.content


    # process response
    if raw_content:
        cleaned = re.sub(
            r"^```json\s*|\s*```$", "", raw_content.strip(), flags=re.IGNORECASE
        )
        cleaned_json = json.loads(cleaned)
        return cleaned_json
    else:
        return {"valid": False}


async def validate_investment_goal(
    question: str,
    user_id: int | None = None,
    portfolio_id: int | None = None,
    db: AsyncSession | None = None,
) -> Dict[str, bool]:

    if not db or not portfolio_id or not user_id:
        return {"valid": False}

    portfolio_summary = get_portfolio_summary(
        jsonable_encoder(await get_portfolio_by_id(db, portfolio_id, user_id))
    )
    memory = await get_investment_objective(user_id, portfolio_id)
    prompt = f"""
            You are a professional investment advisor. It is {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}.
            Your job is to determine the user's investment object, based on the user's question, if it isn't provided below:
            
            User's query:
            {question}

            User's investment objectives from memory:
            {memory if memory else "None"}

            User's portfolio:
            {portfolio_summary}

            Instructions:
            Return a JSON object with a 
              - key "valid" whose value is a boolean indicating whether the user has a clear investment objective from the above
              - key "short_term_objective" whose value is the user's short-term investment objective if it has changed based on the question, or leave it as is if it has not changed
              - key "long_term_objective" whose value is the user's long-term investment objective if it has changed based on the question, or leave it as is if it has not changed
            Only return a json object...
            """


    max_retries = 3
    attempt = 0
    st_obj, lt_obj = "", ""

    while attempt < max_retries and not (st_obj or lt_obj):
        print("Attempt # ", attempt + 1, "to validate investment goal")
        attempt += 1
        response = client.chat.completions.create(
            model=ALT_LLM, messages=[{"role": "user", "content": prompt}]
        )
        raw_content = response.choices[0].message.content


        if raw_content:
            cleaned = re.sub(
                r"^```json\s*|\s*```$", "", raw_content.strip(), flags=re.IGNORECASE
            )
            cleaned_json = json.loads(cleaned)
            st_obj = cleaned_json.get("short_term_objective", "")
            lt_obj = cleaned_json.get("long_term_objective", "")

            if st_obj or lt_obj:
                break
    if st_obj or lt_obj:
        await UserSessionManager.update_session(
            user_id=user_id,
            db=db,
            updates={
                "llm_memory": {
                    "short_term": st_obj or "",
                    "long_term": lt_obj or "",
                    "portfolio_id": portfolio_id,
                }
            },
        )

    return cleaned_json if 'cleaned_json' in locals() else {"valid": False}


async def determine_if_augmentation_required(
    question: str, portfolio_id: int, db: AsyncSession | None = None, user_id: int | None = None
) -> bool:
    if not db or not portfolio_id or not user_id:
        return False
        
    exposure_summary = get_exposure_summary(
        jsonable_encoder(await get_portfolio_by_id(db, portfolio_id, user_id))
    )
    portfolio_summary = get_portfolio_summary(
        jsonable_encoder(await get_portfolio_by_id(db, portfolio_id, user_id))
    )
    memory = await get_investment_objective(user_id, portfolio_id)
    prompt = f"""
            You are a professional investment advisor. It is {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")}
            User question:
            "{question}"

            Summary of user's portfolio:
            {portfolio_summary}
            
            Summary of user's portfolio exposures:
            {exposure_summary}
            
            User's investment objectives: 
            {memory}
            
            Instructions:
            Determine if additional current news data is required to be able to answer the user's question confidently.

            Return a JSON object with a 
              - key "additional_data_required" whose value is a boolean indicating whether the user's question requires additional information or augmentation to provide a comprehensive answer.
            Only return a json object...
            """
    
    # send the prompt to client API for processing
    response = client.chat.completions.create(
        model=LLM, messages=[{"role": "user", "content": prompt}]
    )
    raw_content = response.choices[0].message.content
    
    # process response
    if raw_content:
        cleaned = re.sub(
            r"^```json\s*|\s*```$", "", raw_content.strip(), flags=re.IGNORECASE
        )
        cleaned_json = json.loads(cleaned)
        return cleaned_json.get("additional_data_required", False)
    else:
        return False


async def extract_entities(
    question: str, portfolio_id: int, db: AsyncSession | None = None, user_id: int | None = None
) -> List[Dict[str, str]]:

    if not db or not portfolio_id or not user_id:
        return []

    portfolio_assets = None
    portfolio_summary = ""

    portfolio_assets = jsonable_encoder(
        await get_portfolio_by_id(db, portfolio_id, user_id)
    )
    portfolio_summary = "\n".join(
        [
            get_portfolio_summary(portfolio_assets),
            get_exposure_summary(portfolio_assets),
        ]
    )

    memory = await get_investment_objective(user_id, portfolio_id)
    prompt = f"""
            You are a professional investment advisor. It is {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}

            User question:
            "{question}"

            Here's the user's portfolio summary and exposures:
            {portfolio_summary}
            
            {memory}

            Instructions:
            Extract and return a JSON object that strictly is a list of 2 specific, focused search themes related to the user's quesiton, portfolio and investment objectives, suitable as Google News search queries.           
            Only return a json object...
            """

    response = client.chat.completions.create(
        model=LLM, messages=[{"role": "user", "content": prompt}]
    )
    raw_content = response.choices[0].message.content

    # # stripping markers needed here
    if raw_content:
        themes = re.sub(
            r"^```json\s*|\s*```$", "", raw_content.strip(), flags=re.IGNORECASE
        )
        themes = json.loads(themes)
        return themes
    else:
        return []


async def retrieve_news(
    question: str,
    portfolio_id: int,
    db: AsyncSession | None = None,
    user_id: int | None = None,
    scrape: bool = False,
):
    if not db or not portfolio_id or not user_id:
        return []
        
    themes = await extract_entities(
        question=question,
        portfolio_id=portfolio_id,
        db=db,
        user_id=user_id,
    )

    start_date = datetime.now(timezone.utc) - timedelta(days=8)
    end_date = datetime.now(timezone.utc)

    print(" Looking for Cached Articles :", themes)
    # keys: link, posted (date published), query, query_tags, source (publisher), stored_at (d/t), summary, title
    # cached_articles = await get_cached_articles(
    #     themes, start_date=start_date, end_date=end_date
    # )

    composite_prompt = await construct_prompt_for_embedding(
        db=db, portfolio_id=portfolio_id, user_id=user_id, question=question
    )
    cached_articles = await get_similar_articles(
        composite_prompt, start_date=start_date, end_date=end_date
    )
    print("Found {} chached articles".format(len(cached_articles)))

    if len(cached_articles) > 0:
        for article in cached_articles:
            article["_id"] = str(article["_id"])
            article["stored_at"] = article["stored_at"].isoformat()

    def filter_article_fields(article):
        return {
            "title": article.get("title", ""),
            "summary": article.get("summary", ""),
            "source": article.get("source", ""),
            "link": article.get("link", "")
        }

    if scrape:
        # 3: Fetch articles from Alpha Vantage
        # list of dicts; keys: query, position, title, body, posted, source, link
        fresh_articles = await fetch_articles(themes)

        # 4: Scrape full article content using readability
        if fresh_articles:
            for article in fresh_articles:
                # key added added to each article dict: raw_article - full scraped article content
                try:
                    article["raw_article"] = await extract_with_readability(
                        article["link"]
                    )
                except Exception as e:
                    article["raw_article"] = "Readability extraction failed."

        # 5: Summarize articles using LangChain (Prompt 2 - multiple requests to open ai)
        # keys added:
        #   summary - summarized version of each article by GPT-4o mini
        #   embedding - embedding vector for the summary
        articles = await summarize_and_embed_articles(articles=fresh_articles)

        # 6: Cache summaries in MongoDB
        await store_article_summaries(articles)

        print("Retreived {} fresh articles".format(len(articles)))
        articles_to_return = articles + cached_articles if cached_articles else articles
        filtered_articles = [filter_article_fields(a) for a in articles_to_return]
        # Return articles with token counts
        return {
            "articles": filtered_articles,
        }
    else:
        articles_to_return = cached_articles if cached_articles else []
        filtered_articles = [filter_article_fields(a) for a in articles_to_return]
        return {
            "articles": filtered_articles,
            "token_counts": {
                "input_tokens": 0,
                "output_tokens": 0
            }
        }
