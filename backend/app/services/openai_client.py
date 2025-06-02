import json, os, re, openai
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Tuple, Union
from fastapi.encoders import jsonable_encoder
from app.db.portfolio_crud import get_portfolio_by_id
from app.utils.portfolio_utils import get_exposure_summary, get_portfolio_summary
from app.db.session import AsyncSession
from app.db.user_session import UserSessionManager
from app.utils.memory_utils import parse_memories
from app.config import EXTRACTION_MODEL, ADVICE_MODEL
from app.db.mongo import get_cached_articles, store_article_summaries
from app.services.google_news_scraper import fetch_articles
from app.services.langchain_summary import summarize_articles
from app.utils.article_scraper import extract_with_readability
from app.utils.advisor_utils import preprocess_final_prompt


openai.api_key = os.getenv("OPENAI_API_KEY")


async def validate_prompt(question: str) -> Dict[str, bool]:
    """
    Validates if the user's prompt is a valid investment question and the user's investment objective is clear.
    """
    
    prompt = f"""
            You are an AI assistant. It is {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}

            User question:
            "{question}"

            Instructions:
            Determine if the user's question is a valid and relevant investment question.
            Return a JSON object with a 
              - key "valid" whose value is a boolean indicating whether the user's question is valid and relevant investment question
              - key "clear_objective" whose value is a boolean indicating whether the user's investment objective is ascertainable or not
            Only return a json object...
            """
    print("Prompt: \n", prompt)
    response = openai.chat.completions.create(
        model=EXTRACTION_MODEL, messages=[{"role": "user", "content": prompt}]
    )
    raw_content = response.choices[0].message.content
    # # stripping markers needed here
    cleaned = re.sub(
        r"^```json\s*|\s*```$", "", raw_content.strip(), flags=re.IGNORECASE
    )

    cleaned_json = json.loads(cleaned)
    return cleaned_json


async def retrieve_news(
    question: str, portfolio_id: str, db: AsyncSession = None, user_id: int = None
):
    entities, portfolio, portfolio_summary = extract_entities(
        question=question,
        portfolio_id=portfolio_id,
        db=db,
        user_id=user_id,
    )

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
        summarized = await summarize_articles(fresh_articles)

        print("Summarized articles:", summarized)
        print(
            "------------------------ Storing Articles -------------------------------------------"
        )
        # 6: Cache summaries in MongoDB
        await store_article_summaries(summarized)
    else:
        summarized = cached_articles
    
    return summarized


async def extract_entities(
    question: str, portfolio_id: str, db: AsyncSession = None, user_id: int = None
) -> Tuple[
    List[Dict[str, str]],
    Dict[str, Union[int, str, List[Dict[str, Union[int, str, float, bool]]]]],
    str,
]:

    portfolio = None
    summary = ""

    portfolio = jsonable_encoder(await get_portfolio_by_id(db, portfolio_id, user_id))
    summary = "\n".join(
        [
            get_portfolio_summary(portfolio),
            get_exposure_summary(portfolio),
        ]
    )

    memories = UserSessionManager.get_session(user_id).get("llm_memory")
    length = len(memories)
    memories = parse_memories(memories[-min(3, length) :])
    prompt = f"""
            You are an AI assistant. It is {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}

            User question:
            "{question}"

            Here's the user's portfolio summary and exposures:
            {summary}
            
            Here's how the user's investment objectives have shifted over time:
            {
                memories if memories else "[No previous memory found, this is the first time]"
            }

            Instructions:
            Extract and return a JSON object with:
             1. A key "entities" whose value is a list of 3 specific, focused search themes suitable as Google News search queries.  
                Each theme must include:  
                - "theme": a concise, descriptive phrase reflecting a current news topic or trend tied to the user's question and portfolio (e.g., "US renewable energy policy", "emerging biotech startups in Europe")  
                - "keywords": a list of targeted keywords and phrases to support news search relevance  
                - "country_code": two-letter country code related to portfolio exposure or "NA" if none applies
             2. A key "short_term_objective"  : infer the investment objective indicated by the user's question and portfolio if it has changed from the last time, or leave blank if it has not changed
             3. A key "long_term_objective" : infer the investment objective indicated by the user's question and portfolio if it has changed from the last time, or leave blank if it has not changed

            Only return a json object...
            """
    print("Prompt: \n", prompt)

    response = openai.chat.completions.create(
        model=EXTRACTION_MODEL, messages=[{"role": "user", "content": prompt}]
    )
    raw_content = response.choices[0].message.content

    # # stripping markers needed here
    cleaned = re.sub(
        r"^```json\s*|\s*```$", "", raw_content.strip(), flags=re.IGNORECASE
    )

    cleaned_json = json.loads(cleaned)

    return cleaned_json, portfolio, summary


async def generate_advice(question, db, portfolio_id, user_id, article_summaries):
    system_prompt = """
    You are “Atlas”, a senior buy‑side investment strategist (CFA, 15 yrs experience).
    Duty: synthesize news + portfolio data and produce *actionable* portfolio guidance.
    Constraints:
    - Stay within classical asset‑allocation & risk‑management best practice.
    - No personal tax or legal advice.
    - Cite assumptions you rely on.
    - Write in clear, executive‑level English (no jargon unless defined).
    """

    portfolio_summary, article_summaries = preprocess_final_prompt(db, portfolio_id, user_id, article_summaries)
    memory = UserSessionManager.get_session(user_id).get("llm_memory")

    user_prompt = f"""
                ### User Question
                {question}

                ### Portfolio Snapshot
                {portfolio_summary}

                ### Recent News & Data (already pre‑filtered for relevance)
                {article_summaries if article_summaries else "[No articles were needed regarding this question]"}

                ### User's Investment Objective
                {memory if memory else "[No previous memory found, this is the first time]"}
                
                ### Deliverable
                Respond using **only** the following markdown section headings:

                ##1‑Sentence Answer – the punch line.  
                ##Portfolio Impact Analysis – how news items affect key positions/exposures (News summaries don't make sense, infer from their titles).  
                ##Recommendations (Numbered) – specific trades, hedges, or reallocations; include target weight/size, time frame, and thesis in ≤ 40 words each, taking into consideration the user's short-term and long-term objectives.
                ##Key Risks & Unknowns – bullet list.  
                ##Confidence (0‑100%) – single number plus one‑line justification.  
                ##References & Assumptions – mention news snippets or metrics (brief).  
                ##Citations – list of news snippets (title, source) used to support your analysis.

                Keep total length under 450 words (excluding citations) and format the response in an appropriate markdown of headings, paragraphs and lists.
                """
    print(
        "------------------------- Generating Final Advice -------------------------------------------"
    )
    print("user prompt: \n")
    print(user_prompt)

    response = openai.chat.completions.create(
        model=ADVICE_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content
