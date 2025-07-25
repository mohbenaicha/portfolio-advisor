import httpx
import asyncio
import markdown
import tiktoken
from typing import Tuple, Union, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.portfolio_utils import (
    fetch_portfolio_from_service,
    get_exposure_summary,
    get_portfolio_summary,
)
from utils.profile_utils import fetch_profile_from_service
from fastapi.encoders import jsonable_encoder
from app.config import PROVIDER_BASE_URL
from app.db.user_session import UserSessionManager


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens in text using tiktoken."""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except:
        # Fallback for unknown models
        return int(len(text.split()) * 1.3)


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

async def build_system_prompt(user_id: int, portfolio_id: int) -> str:

    return f"""
        You are Titan, a senior buy-side investment strategist (CFA, 15+ years of experience).

        Your role is to review the user's portfolio, investment profile, and the latest news then deliver clear, actionable portfolio guidance based on the user's query.
        - Use the `get_user_portfolio` tool to access the user's portfolio holdings, exposures, and asset weights. This is not indicative of the user's investment profile.
        - Use the `get_user_profiles` tool to access access the user's investment profile (objectives and sector, regional, and asset preferences). If this tool returns unavaialble, you must ask user for clarification.
            **Very important notes on this tool:**
            1. The user may provided updated information regarding their profile, so you must always use the latest information available.
            2. If you are unable to determine the user's portoflio AND investment profile, you must ask user for clarification.
        
        - Use the `retrieve_news` tool to fetch relevant news for context and recommendation alignment. Only call this if the user asks for news or if you need to provide a recommendation.

       

        Otherwise, proceed with the following instructions with ###Deliverable to follow:
        Follow classical asset allocation and risk management principles. 
        You **must retrieve news data** to provide relevant advice. 
        Do **not** provide personal tax or legal advice.
        Write in concise, executive-level English — avoid jargon unless explained.

        ### Deliverable

        Respond using **only** the following markdown section headings:

        ## 1-Sentence Answer  
        The punchline summary.

        ## Portfolio Impact Analysis  
        Explain how news items affect key positions or exposures. *Do not summarize news — infer implications from titles.*

        ## Recommendations (Numbered)  
        Specific trades, hedges, or reallocations. Include:
        - Target weight or size  
        - Time frame  
        - Thesis in ≤ 40 words  
        Align suggestions to both short- and long-term user objectives.

        ## Key Risks & Unknowns  
        Bullet list of uncertainties or downside risks.

        ## Confidence (0-100%)  
        A single number with a one-line justification. 

        ## References & Assumptions  
        Briefly mention any key news snippets or metrics relied on.

        ## Citations  
        For each referenced news article, list the full title, source, and the direct URL.
        Format each citation as: [Title](URL) — Source

        **Constraints:**  
        Keep total length under 500 words (excluding citations). Use clean markdown formatting (headings, bullet points, short paragraphs).
        """


async def call_provider_endpoint(endpoint: str, payload: dict) -> Dict[str, Union[bool, str]]: 
    url = f"{PROVIDER_BASE_URL}{endpoint}"
    timeout = httpx.Timeout(600)  # 10 minutes timeout
    retries = 1
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
            print(f"INFO: [Retry] Attempt {attempt} failed: {e}. Retrying in {backoff}s...")
            await asyncio.sleep(backoff)
            backoff *= 2
    return {"archived": False, "summary": "Error calling provider endpoint"}


async def construct_prompt_for_embedding(
    db: AsyncSession, portfolio_id: int, user_id: int, question: str
) -> str:
    portfolio_assets = jsonable_encoder(
        await fetch_portfolio_from_service(portfolio_id, user_id)
        # await get_portfolio_by_id(db, portfolio_id, user_id)
    )


    portfolio_summary = "\n".join(
        [
            get_portfolio_summary(portfolio_assets),
            get_exposure_summary(portfolio_assets),
        ]
    )
    
    investment_profile = await fetch_profile_from_service(portfolio_id)
    return f"""
                {question}

                My portfolio:
                {portfolio_summary}

                My investment profile:
                {investment_profile}
            """


async def increment_prompt_usage(user_id: int, db: AsyncSession) -> None:
    with UserSessionManager.use_advisor_session():
        await UserSessionManager.update_session(
            user_id=user_id,
            db=db,
            updates={
                "total_prompts_used": await UserSessionManager.get_total_prompts_used(
                    user_id
                )
                + 1
            },
        )

LIMIT_MESSAGE = "<p>You have reached the maximum number of prompts allowed for today.</p>"

async def check_prompt_limit(user_id: int) -> Tuple[bool, Union[dict[str, Union[bool, str]], None]]:
    with UserSessionManager.use_advisor_session():
        prompt_count = await UserSessionManager.get_total_prompts_used(user_id)
        failed_count = await UserSessionManager.get_failed_prompts(user_id)
        if prompt_count >= 6 or failed_count >= 15:
            return True, {"archived": False, "summary": LIMIT_MESSAGE, "final_message": True}
        else:
            return False, None