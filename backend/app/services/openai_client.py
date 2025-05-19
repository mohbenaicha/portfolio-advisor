import json, os, re, openai
from typing import List, Dict, Tuple, Union
from fastapi.encoders import jsonable_encoder
from app.models.schemas import Portfolio
from app.db.portfolio_crud import get_portfolio_by_id
from app.utils.portfolio_utils import get_exposure_summary, get_portfolio_summary
from app.db.session import AsyncSessionLocal


openai.api_key = os.getenv("OPENAI_API_KEY")


async def extract_entities(question: str, portfolio_id: str) -> Tuple[
    List[Dict[str, str]],
    Dict[str, Union[int, str, List[Dict[str, Union[int, str, float, bool]]]]],
    str,
]:
    # print("Extracting entities from question and portfolio summary...")
    # print("Question:", question)
    # print("Portfolio summary:", summary)
    portfolio = None
    summary = ""
    async with AsyncSessionLocal() as db:

        portfolio = jsonable_encoder(await get_portfolio_by_id(db, portfolio_id))
        print("Portfolio: ", portfolio)
        summary = "\n".join(
            [
                get_portfolio_summary(portfolio),
                get_exposure_summary(portfolio),
            ]
        )

    prompt = f"""
            You are an AI assistant...

            User question:
            "{question}"

            Here's the user's portfolio summary and exposures:
            {summary}

            Instructions:
            Extract and return a JSON list object that is a list of 5 specific themes based on the user's goal and portfolio exposure and positions.
            - "theme": short descriptive theme
            - "keywords": a list of very descriptive keywords for the theme used to store each theme in a database
            - "country_code": the two-letter country code (if applicable, if not applicable, return "NA") based on portfolio exposure

            Only return a json object...
            """
    print("Prompt: \n", prompt)

    response = openai.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
    )
    raw_content = response.choices[0].message.content

    # # stripping markers needed here
    cleaned = re.sub(
        r"^```json\s*|\s*```$", "", raw_content.strip(), flags=re.IGNORECASE
    )

    # print("OPEN AI's response:\n\n")
    # print(cleaned)
    cleaned_json = json.loads(cleaned)
    if isinstance(cleaned_json, dict) and "themes" in cleaned_json:
        cleaned_json = cleaned_json[
            "themes"
        ]  # Extract the list if open ai api returns a key: value pair
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
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content
