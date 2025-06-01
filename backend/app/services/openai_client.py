import json, os, re, openai
from datetime import datetime, timezone
from typing import List, Dict, Tuple, Union
from fastapi.encoders import jsonable_encoder
from app.db.portfolio_crud import get_portfolio_by_id
from app.utils.portfolio_utils import get_exposure_summary, get_portfolio_summary
from app.db.session import AsyncSession
from app.db.user_session import UserSessionManager
from app.utils.memory_utils import parse_memories
from app.config import EXTRACTION_MODEL, ADVICE_MODEL
openai.api_key = os.getenv("OPENAI_API_KEY")


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
    memories = parse_memories(
        memories[-min(3, length):]
    )
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
             1. A key "valid" whose value is a boolean indicating whether the user's question is valid and relevant investment question (values: "yes", "no").
             2. A key "entities" whose value is a list of 3 specific, focused search themes suitable as Google News search queries.  
                Each theme must include:  
                - "theme": a concise, descriptive phrase reflecting a current news topic or trend tied to the user's question and portfolio (e.g., "US renewable energy policy", "emerging biotech startups in Europe")  
                - "keywords": a list of targeted keywords and phrases to support news search relevance  
                - "country_code": two-letter country code related to portfolio exposure or "NA" if none applies
             3. A key "short_term_objective"  : infer the investment objective indicated by the user's question and portfolio if it has changed from the last time, or leave blank if it has not changed
             4. A key "long_term_objective" : infer the investment objective indicated by the user's question and portfolio if it has changed from the last time, or leave blank if it has not changed
             5. a key "justification": a short justification for inferred invest objectives if they have changed, or leave blank if they have not changed

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

    # print("OPEN AI's response:\n\n")
    # print(cleaned)
    cleaned_json = json.loads(cleaned)

    return cleaned_json, portfolio, summary


async def generate_advice(question, summary, articles, user_id):
    system_prompt = """
    You are “Atlas”, a senior buy‑side investment strategist (CFA, 15 yrs experience).
    Duty: synthesize news + portfolio data and produce *actionable* portfolio guidance.
    Constraints:
    - Stay within classical asset‑allocation & risk‑management best practice.
    - No personal tax or legal advice.
    - Cite assumptions you rely on.
    - Write in clear, executive‑level English (no jargon unless defined).
    """

    memories = UserSessionManager.get_session(user_id).get("llm_memory")
    length = len(memories)
    memories = parse_memories(
        memories[-min(3, length):]
    )

    user_prompt = f"""
                ### User Question
                {question}

                ### Portfolio Snapshot
                {summary}

                ### Recent News & Data (already pre‑filtered for relevance)
                {articles}

                ### User's Investment Objective
                {memories if memories else "[No previous memory found, this is the first time]"}
                
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
