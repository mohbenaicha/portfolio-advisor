import json, os, re, openai
from typing import List, Dict

openai.api_key = os.getenv("OPENAI_API_KEY")


async def extract_entities(question: str, summary: str) -> List[Dict[str, str]]:
    # print("Extracting entities from question and portfolio summary...")
    # print("Question:", question)
    # print("Portfolio summary:", summary)
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
    # print("Prompt: \n", prompt)
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
        cleaned_json = cleaned_json["themes"]  # Extract the list if open ai api returns a key: value pair
    return cleaned_json


async def generate_advice(question, portfolio, articles):

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
{portfolio}

### Recent News & Data (already pre‑filtered for relevance)
{articles}

### Deliverable
Respond using **only** the following markdown section headings:

1. **1‑Sentence Answer** – the punch line.  
2. **Portfolio Impact Analysis** – how news items affect key positions/exposures.  
3. **Recommendations (Numbered)** – specific trades, hedges, or reallocations; include target weight/size, time frame, and thesis in ≤ 40 words each.  
4. **Key Risks & Unknowns** – bullet list.  
5. **Confidence (0‑100%)** – single number plus one‑line justification.  
6. **References & Assumptions** – cite news snippets or metrics (brief, no URLs).  
7. **Compliance Note** – “This information is for educational purposes…”.

Keep total length under 450 words.
"""
    print("user prompt: \n")
    print(user_prompt)
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    print(response)
    return response.choices[0].message.content
