import json, os, re, openai

openai.api_key = os.getenv("OPENAI_API_KEY")


async def extract_entities(question, summary):
    prompt = f"""You are an AI assistant...

            User question:
            "{question}"

            Portfolio summary:
            {summary}

            Extract and return a JSON object with:
            - asset_types, sectors, regions, keywords (themes)
            - keywords (themes) from this list only:
            ["blockchain", "earnings", "ipo", "mergers_and_acquisitions", "financial_markets",
            "economy_fiscal", "economy_monetary", "economy_macro", "energy_transportation",
            "finance", "life_sciences", "manufacturing", "real_estate", "retail_wholesale", "technology"]
            Only return a json object...
            """
    response = openai.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
    )
    raw_content = response.choices[0].message.content

    # stripping markers needed here
    cleaned = re.sub(
        r"^```json\s*|\s*```$", "", raw_content.strip(), flags=re.IGNORECASE
    )

    print("OPEN AI's response:\n\n")
    print(cleaned)

    return json.loads(cleaned)


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
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message["content"]
