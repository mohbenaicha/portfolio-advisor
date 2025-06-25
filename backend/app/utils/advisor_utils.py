import httpx
import asyncio
import markdown
from typing import Tuple, Union, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.portfolio_crud import get_portfolio_by_id
from app.utils.portfolio_utils import (
    get_exposure_summary,
    get_portfolio_summary,
)
from fastapi.encoders import jsonable_encoder
from app.config import PROVIDER_BASE_URL
from app.db.user_session import UserSessionManager
from app.utils.memory_utils import get_investment_objective


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

    memory = await UserSessionManager.get_llm_memory(
        user_id=user_id, portfolio_id=portfolio_id
    )
    return f"""
You are Titan, a senior buy-side investment strategist (CFA, 15+ years of experience).

Your role is to review the user's portfolio and investment objectives, then deliver clear, actionable portfolio guidance.

Follow classical asset allocation and risk management principles. 
You **must retrieve news data** to provide relevant advice. 
Do **not** provide personal tax or legal advice.  
Cite any key assumptions you rely on.  
Write in concise, executive-level English — avoid jargon unless explained.

User’s investment objectives:
{memory}

### Deliverable

Respond using **only** the following markdown section headings:

## 1‑Sentence Answer  
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

## Confidence (0‑100%)  
A single number with a one-line justification.

## References & Assumptions  
Briefly mention any key news snippets or metrics relied on.

## Citations  
For each referenced news article, list the full title, source, and the direct URL.
Format each citation as: [Title](URL) — Source

**Constraints:**  
Keep total length under 500 words (excluding citations). Use clean markdown formatting (headings, bullet points, short paragraphs).

Assume no follow-up questions. Your response must be as decisive and complete as possible, or clearly explain what’s missing to provide valid recommendations.
    """


async def call_provider_endpoint(endpoint: str, payload: dict) -> Dict[str, Union[bool, str]]: 
    url = f"{PROVIDER_BASE_URL}{endpoint}"
    timeout = httpx.Timeout(600)  # 10 minutes timeout
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
    return {"archived": False, "summary": "Error calling provider endpoint"}


async def construct_prompt_for_embedding(
    db: AsyncSession, portfolio_id: int, user_id: int, question: str
) -> str:
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
    return f"""
{question}

My portfolio:
{portfolio_summary}

My investment objectives:
{memory}
            """


async def increment_prompt_usage(user_id: int, db: AsyncSession) -> None:
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

async def check_prompt_limit(user_id: int) -> Tuple[bool, Union[dict[str, Union[bool, str]], None]]:
    prompt_count = await UserSessionManager.get_total_prompts_used(user_id)
    if prompt_count >= 3:
        return True, {
            "archived": False,
            "summary": "<p>You have reached the maximum number of prompts allowed for today.</p>",
        }
    else:
        return False, None