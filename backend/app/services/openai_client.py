import json, re
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Tuple, Union
from fastapi.encoders import jsonable_encoder
from app.db.portfolio_crud import get_portfolio_by_id
from app.utils.portfolio_utils import get_exposure_summary, get_portfolio_summary
from app.db.session import AsyncSession
from app.db.user_session import UserSessionManager
from app.utils.memory_utils import get_investment_objective
from app.config import EXTRACTION_MODEL, ADVICE_MODEL, EMAIL_ADDRESS, OPEN_AI_API_KEY
from app.db.mongo import get_cached_articles, store_article_summaries
from app.services.google_news_scraper import fetch_articles
from app.services.langchain_summary import summarize_articles
from app.utils.article_scraper import extract_with_readability
from app.utils.advisor_utils import preprocess_final_prompt
from app.utils.advisor_utils import build_advice_prompt
from openai import OpenAI
import socket

client = OpenAI(api_key=OPEN_AI_API_KEY)


async def validate_prompt(
    question: str, portfolio_id: int, user_id: int, db: AsyncSession
) -> Dict[str, bool]:
    """
    Validates if the user's prompt is a valid investment question and the user's investment objective is clear.
    """
    print("Validating prompt for user_id:", user_id, "portfolio_id:", portfolio_id)
    print("🧪 DNS:", socket.gethostbyname("api.openai.com"))
    try:
        result = await client.models.list()
        print("✅ OpenAI reachable:", result[:3])
    except Exception as e:
        import traceback
        print("🔥 OpenAI error:")
        traceback.print_exc()
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
            Determine if the user's question is a valid and relevant investment question.
            Return a JSON object with a 
              - key "valid" whose value is a boolean indicating whether the user's question is valid and relevant investment question
            Only return a json object...
            """

    # send the prompt to OpenAI API for processing
    response = client.chat.completions.create(
        model=EXTRACTION_MODEL, messages=[{"role": "user", "content": prompt}]
    )
    raw_content = response.choices[0].message.content

    # process response
    cleaned = re.sub(
        r"^```json\s*|\s*```$", "", raw_content.strip(), flags=re.IGNORECASE
    )
    cleaned_json = json.loads(cleaned)
    return cleaned_json


async def validate_investment_goal(
    question: str,
    user_id: int = None,
    portfolio_id: int = None,
    db: AsyncSession = None,
) -> Dict[str, bool]:
    print(
        "Validating investment goal for user_id:",
        user_id,
        "portfolio_id:",
        portfolio_id,
    )

    portfolio_summary = get_portfolio_summary(
        jsonable_encoder(await get_portfolio_by_id(db, portfolio_id, user_id))
    )
    memory = await get_investment_objective(user_id, portfolio_id)

    prompt = f"""
            You are a professional investment advisor. It is {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}.
            Your job is to determine the user's investment object, based on the user's question, if it isn't provided below.

            User question:
            "{question}"
            
            User's portfolio:
            {portfolio_summary}

            User's investment objectives from memory:
            {memory if memory else "None"}

            Instructions:
            Return a JSON object with a 
              - key "valid" whose value is a boolean indicating whether the user has a clear investment objective from the above
              - key "short_term_objective" whose value is the user's short-term investment objective if it has changed based on the question, or blank if it has not changed
              - key "long_term_objective" whose value is the user's long-term investment objective if it has changed based on the question, or blank if it has not changed
            Only return a json object...
            """

    max_retries = 3
    attempt = 0
    st_obj, lt_obj = "", ""

    while attempt < max_retries and not (st_obj or lt_obj):
        print("Attempt # ", attempt + 1, "to validate investment goal")
        attempt += 1
        response = client.chat.completions.create(
            model=EXTRACTION_MODEL, messages=[{"role": "user", "content": prompt}]
        )
        raw_content = response.choices[0].message.content

        cleaned = re.sub(
            r"^```json\s*|\s*```$", "", raw_content.strip(), flags=re.IGNORECASE
        )
        cleaned_json = json.loads(cleaned)
        st_obj = cleaned_json.get("short_term_objective", "")
        lt_obj = cleaned_json.get("long_term_objective", "")

        if st_obj or lt_obj:
            break

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
    print(
        "--------------->updated user objective based on llm response",
        await UserSessionManager.get_llm_memory(
            user_id=user_id, portfolio_id=portfolio_id
        ),
    )
    return cleaned_json


async def determine_if_augmentation_required(
    question: str, portfolio_id: str, db: AsyncSession = None, user_id: int = None
) -> bool:
    # print("Determining if augmentation is required for question:", question)
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
    # print("determine_if_augmentation_required prompt: \n", prompt)
    # send the prompt to client API for processing
    response = client.chat.completions.create(
        model=EXTRACTION_MODEL, messages=[{"role": "user", "content": prompt}]
    )
    raw_content = response.choices[0].message.content
    # process response
    cleaned = re.sub(
        r"^```json\s*|\s*```$", "", raw_content.strip(), flags=re.IGNORECASE
    )
    cleaned_json = json.loads(cleaned)
    # print("determine_if_augmentation_required response: \n", cleaned_json)
    return cleaned_json.get("additional_data_required", False)


async def extract_entities(
    question: str, portfolio_id: str, db: AsyncSession = None, user_id: int = None
) -> Tuple[
    List[Dict[str, str]],
    Dict[str, Union[int, str, List[Dict[str, Union[int, str, float, bool]]]]],
    str,
]:
    # print("Extracting entities for question:", question)

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
            Extract and return a JSON object that is a list of 3 specific, focused search themes suitable as Google News search queries.
                Each theme must include:  
                - a key "theme" whose value is a concise, descriptive phrase reflecting a current news topic or trend tied to the user's question and portfolio (e.g., "US renewable energy policy", "emerging biotech startups in Europe")  
                - a key "keywords" whose value is a list of targeted keywords and phrases to support news search relevance  
                - a key "country_code" whose value is a two-letter country code related to portfolio exposure or "NA" if none applies
           

            Only return a json object...
            """
    # print("Prompt: \n", prompt)

    response = client.chat.completions.create(
        model=EXTRACTION_MODEL, messages=[{"role": "user", "content": prompt}]
    )
    raw_content = response.choices[0].message.content

    # # stripping markers needed here
    themes = re.sub(
        r"^```json\s*|\s*```$", "", raw_content.strip(), flags=re.IGNORECASE
    )

    themes = json.loads(themes)

    return themes


async def retrieve_news(
    question: str, portfolio_id: str, db: AsyncSession = None, user_id: int = None
):
    # print("Retrieving news for question:", question)
    themes = await extract_entities(
        question=question,
        portfolio_id=portfolio_id,
        db=db,
        user_id=user_id,
    )

    start_date = datetime.now(timezone.utc) - timedelta(days=8)
    end_date = datetime.now(timezone.utc)

    # print(" Looking for Cached Articles ")
    # keys: link, posted (date published), query, query_tags, source (publisher), stored_at (d/t), summary, title
    cached_articles = await get_cached_articles(
        themes, start_date=start_date, end_date=end_date
    )
    # print("Found {} chached articles".format(len(cached_articles)))

    if len(cached_articles) < 10:
        # print(" Fetching Articles from Google Search News ")

        # 3: Fetch articles from Alpha Vantage
        # list of dicts; keys: query, position, title, body, posted, source, link
        fresh_articles = await fetch_articles(themes)

        # 4: Scrape full article content using readability
        # print(" Extracting Article Content ")
        for article in fresh_articles:
            # key added added to each article dict: raw_article - full scraped article content
            try:
                article["raw_article"] = await extract_with_readability(article["link"])
            except Exception as e:
                # print(f"Error extracting article content: {e}")
                article["raw_article"] = "Readability extraction failed."

        # print("Starting to summarize articles...")
        # 5: Summarize articles using LangChain (Prompt 2 - multiple requests to open ai)
        # key added: summary - summarized version of each article by GPT-4o mini
        # print(" Summarizing Articles ")
        summarized = await summarize_articles(fresh_articles)

        # print(" Storing Articles ")
        # 6: Cache summaries in MongoDB
        await store_article_summaries(summarized)
    else:
        for article in cached_articles:
            article["_id"] = str(article["_id"])
            article["stored_at"] = article["stored_at"].isoformat()
        summarized = cached_articles

    return summarized


async def generate_advice(question, db, portfolio_id, user_id, article_summaries):
    system_prompt = """
    You are “Titan”, a senior buy‑side investment strategist (CFA, 15 yrs experience).
    Duty: synthesize news + portfolio data and produce *actionable* portfolio guidance.
    Constraints:
    - Stay within classical asset‑allocation & risk‑management best practice.
    - No personal tax or legal advice.
    - Cite assumptions you rely on.
    - Write in clear, executive‑level English (no jargon unless defined).
    """
    # print("Generating advice for question:", question)

    portfolio_summary, article_summaries = await preprocess_final_prompt(
        db, portfolio_id, user_id, article_summaries
    )
    memory = await get_investment_objective(user_id, portfolio_id)
    news_section = (
        f"### Recent News & Data (already pre‑filtered for relevance)\n{article_summaries}"
        if article_summaries
        else ""
    )
    user_prompt = f"""
                You are a professional investment advisor with expertise in financial markets, portfolio management, and risk assessment. You have 
                received a question from a user regarding their investment portfolio, and you need to provide a comprehensive analysis and actionable 
                recommendations based on the user's portfolio, recent news data if any, and their investment objectives.
                
                ### User Question
                {question}

                ### Portfolio Snapshot
                {portfolio_summary}

                {news_section}

                "### User's Investment Objective\n"
                {memory}
                    
                ### Deliverable
                Respond using **only** the following markdown section headings:

                ##1‑Sentence Answer – the punch line.  
                ##Portfolio Impact Analysis – how news items affect key positions/exposures (News summaries don't make sense, infer from their titles).  
                ##Recommendations (Numbered) – specific trades, hedges, or reallocations; include target weight/size, time frame, and thesis in ≤ 40 words each, taking into consideration the user's short-term and long-term objectives.
                ##Key Risks & Unknowns – bullet list.  
                ##Confidence (0‑100%) – single number plus one‑line justification.  
                ##References & Assumptions – mention news snippets or metrics (brief).  
                ##Citations – list of news snippets (title, source) used to support your analysis.

                Keep total length under 500 words (not counting citations) and format the response in an appropriate markdown of headings, paragraphs and lists.
                """
    # print("generate_advice prompt: \n", user_prompt)
    response = client.chat.completions.create(
        model=ADVICE_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    # print("generate_advice response: \n", response.choices[0].message.content)
    return response.choices[0].message.content


async def prepare_advice_template(
    question: str,
    portfolio_id: int,
    db: AsyncSession,
    article_summaries: List[Dict[str, str]],
    **kwargs,
):
    portfolio_summary, article_summaries = await preprocess_final_prompt(
        db,
        portfolio_id,
        user_id=kwargs.get("user_id"),
        article_summaries=article_summaries,
    )
    memory = await UserSessionManager.get_llm_memory(
        user_id=kwargs.get("user_id"), portfolio_id=portfolio_id
    )

    prompt = build_advice_prompt(
        question=question,
        portfolio_summary=portfolio_summary,
        objectives=memory,
        article_summaries=article_summaries,
    )
    print("prepare_advice_template prompt: \n", prompt)
    return {"advice_prompt": prompt}
