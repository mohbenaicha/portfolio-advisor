import httpx
import asyncio
import markdown
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.portfolio_crud import get_portfolio_by_id
from app.utils.portfolio_utils import (
    get_asset_representation,
    get_exposure_summary,
    get_portfolio_summary,
)
from fastapi.encoders import jsonable_encoder
from app.config import PROVIDER_BASE_URL
from app.db.user_session import UserSessionManager


def preprocess_markdown(markdown_text):
    # Example: Normalize spacing and fix common issues
    markdown_text = markdown_text.strip()
    markdown_text = markdown_text.replace("**;", "**")  # Fix malformed bold syntax
    markdown_text = markdown_text.replace("\n\n", "\n")  # Remove excessive newlines
    return markdown_text


def convert_markdown_to_html(markdown_text):
    markdown_text = preprocess_markdown(markdown_text)

    html_content = markdown.markdown(markdown_text, extensions=["extra", "smarty"])
    styled_html = f"""
    <html>
        <style>
            ul, ol {{
                margin-left: 30px; 
            }}
            li {{
                margin-bottom: 10px; 
            }}
            p {{
                margin-left: 10px;
            }}
        </style>
    <body>
        {html_content}
    </body>
    </html>
    """
    return styled_html


async def preprocess_final_prompt(db, portfolio_id, user_id, article_summaries=None):

    portfolio = jsonable_encoder(await get_portfolio_by_id(db, portfolio_id, user_id))
    portfolio_summary = "\n".join(
        [
            get_asset_representation(portfolio),
            get_portfolio_summary(portfolio),
            get_exposure_summary(portfolio),
        ]
    )

    if article_summaries:
        article_summaries = [
            article
            for article in article_summaries
            if all(key in article for key in ["title", "summary", "link"])
        ]
        article_summaries = "\n\n".join(
            [
                "\n".join([article["title"], article["summary"], article["link"]])
                for article in article_summaries
                if article["summary"] != "Readability extraction failed"
            ]
        )

    return portfolio_summary, article_summaries


async def build_system_prompt(user_id: int, portfolio_id: int, db: AsyncSession) -> str:

    portfolio = jsonable_encoder(await get_portfolio_by_id(db, portfolio_id, user_id))
    portfolio_summary = "\n".join(
        [
            get_asset_representation(portfolio),
            get_portfolio_summary(portfolio),
            get_exposure_summary(portfolio),
        ]
    )

    memory  = await UserSessionManager.get_llm_memory(
        user_id=user_id, portfolio_id=portfolio_id
    )
    return f"""You are “Titan”, a senior buy‑side investment strategist (CFA, 15 yrs experience).
    Duty: synthesize news + portfolio data and produce *actionable* portfolio guidance.
    Constraints:
    - Stay within classical asset‑allocation & risk‑management best practice.
    - No personal tax or legal advice.
    - Cite assumptions you rely on.
    - Write in clear, executive‑level English (no jargon unless defined).
    - Use markdown for formatting (headings, lists, links).
    
    User's portfolio summary:
    {portfolio_summary}

    User's investment objectives:
    {memory}
    """


def build_advice_prompt(
    question: str, portfolio_summary: str, objectives: str, article_summaries: list
) -> str:

    return f"""
            You are a professional investment advisor with expertise in financial markets, portfolio management, and risk assessment. You have 
            received a question from a user regarding their investment portfolio, and you need to provide a comprehensive analysis and actionable 
            recommendations based on the user's portfolio, recent news data if any, and their investment objectives.
            
            ### User Question
            {question}

            ### Portfolio Snapshot
            {portfolio_summary}

            {
            "### Recent News & Data (already pre‑filtered for relevance)\n"
            f"{article_summaries}" if article_summaries else ""
            }

            
            "### User's Investment Objective\n"
            {objectives}
                
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

async def call_provider_endpoint(endpoint: str, payload: dict) -> dict:
    url = f"{PROVIDER_BASE_URL}{endpoint}"
    timeout = httpx.Timeout(600) # 10 minutes timeout
    retries = 3
    backoff = 2  # seconds

    for attempt in range(1, retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            if attempt == retries:
                raise  # re raise on last atempt
            print(f"[Retry] Attempt {attempt} failed: {e}. Retrying in {backoff}s...")
            await asyncio.sleep(backoff)
            backoff *= 2 