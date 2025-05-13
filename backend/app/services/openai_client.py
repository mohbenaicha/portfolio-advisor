import json, os, re
import openai

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
    cleaned = re.sub(r"^```json\s*|\s*```$", "", raw_content.strip(), flags=re.IGNORECASE)

    print("OPEN AI's response:\n\n")
    print(cleaned)

    return json.loads(cleaned)


async def generate_advice(question, portfolio, articles):
    article_text = "\n".join([f"{a['title']} - {a['summary']}" for a in articles])
    prompt = f"""User question: {question}

            Portfolio:
            {portfolio}

            Recent news:
            {article_text}

            Respond with a financial analysis and recommendation.
            """
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"]
