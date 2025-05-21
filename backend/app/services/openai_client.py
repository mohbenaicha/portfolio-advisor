import json, os, re, openai
from typing import List, Dict, Tuple, Union
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from app.db.portfolio_crud import get_portfolio_by_id
from app.utils.portfolio_utils import get_exposure_summary, get_portfolio_summary
from app.db.session import get_db, AsyncSession
from app.db.user_session import UserSessionManager
from app.dependencies.user import get_current_user
from datetime import datetime, timezone


openai.api_key = os.getenv("OPENAI_API_KEY")


async def extract_entities(
    question: str, portfolio_id: str, db: AsyncSession = Depends(get_db)
) -> Tuple[
    List[Dict[str, str]],
    Dict[str, Union[int, str, List[Dict[str, Union[int, str, float, bool]]]]],
    str,
]:
    portfolio = None
    summary = ""

    portfolio = jsonable_encoder(await get_portfolio_by_id(db, portfolio_id))
    summary = "\n".join(
        [
            get_portfolio_summary(portfolio),
            get_exposure_summary(portfolio),
        ]
    )

    memories = "\n".join(
        [
            "\n".join(
                [
                    f"date: {memory.date}",
                    f"short_term: {memory.short_term_goal}",
                    f"long_term: {memory.long_term_goal}",
                ]
            )
            for memory in UserSessionManager.get_session(get_current_user()).get(
                "llm_memory"
            )[-3:]
        ]
    )
    prompt = f"""
            You are an AI assistant. It is {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}

            User question:
            "{question}"

            Here's the user's portfolio summary and exposures:
            {summary}
            
            Here's how the user's investment objectives have shifted over time:
            {
                memories
            }

            Instructions:
            Extract and return a JSON object with:
             1. A key "entities" whose value is a list of 5 specific themes based on the user's goal and portfolio exposure and positions.
                - "theme": short descriptive theme
                - "keywords": a list of very descriptive keywords for the theme used to store each theme in a database
                - "country_code": the two-letter country code (if applicable, if not applicable, return "NA") based on portfolio exposure
             2. A key "short_term_objective"  : value as the short-term investment objective indicated by the user's question and portfolio if it has changed from the last time
             3. A key "long_term_objective" : value as the long-term investment objective indicated by the user's question and portfolio if it has changed from the last time

            Only return a json object...
            """
    print("Prompt: \n", prompt)

    response = openai.chat.completions.create(
        model="gpt-4.1-mini", messages=[{"role": "user", "content": prompt}]
    )
    raw_content = response.choices[0].message.content

    # # stripping markers needed here
    cleaned = re.sub(
        r"^```json\s*|\s*```$", "", raw_content.strip(), flags=re.IGNORECASE
    )

    # print("OPEN AI's response:\n\n")
    # print(cleaned)
    cleaned_json = json.loads(cleaned)

    return cleaned_json, portfolio, summary


async def generate_advice(question, summary, articles):

    system_prompt = """
    You are “Atlas”, a senior buy‑side investment strategist (CFA, 15 yrs experience).
    Duty: synthesize news + portfolio data and produce *actionable* portfolio guidance.
    Constraints:
    - Stay within classical asset‑allocation & risk‑management best practice.
    - No personal tax or legal advice.
    - Cite assumptions you rely on.
    - Write in clear, executive‑level English (no jargon unless defined).
    """

    user_prompt = f"""
                ### User Question
                {question}

                ### Portfolio Snapshot
                {summary}

                ### Recent News & Data (already pre‑filtered for relevance)
                {articles}

                ### Deliverable
                Respond using **only** the following markdown section headings:

                1. **1‑Sentence Answer** – the punch line.  
                2. **Portfolio Impact Analysis** – how news items affect key positions/exposures (News summaries don't make sense, infer from their titles).  
                3. **Recommendations (Numbered)** – specific trades, hedges, or reallocations; include target weight/size, time frame, and thesis in ≤ 40 words each.  
                4. **Key Risks & Unknowns** – bullet list.  
                5. **Confidence (0‑100%)** – single number plus one‑line justification.  
                6. **References & Assumptions** – mention news snippets or metrics (brief).  
                7. **Citations** – list of news snippets (title, source) used to support your analysis.

                Keep total length under 450 words (excluding citations).
                """
    print(
        "------------------------- Generating Final Advice -------------------------------------------"
    )
    print("user prompt: \n")
    print(user_prompt)

    response = openai.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content
