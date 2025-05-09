import openai
from os import getenv

openai.api_key = getenv("OPENAI_API_KEY")

async def extract_entities(question, summary):
    prompt = f"""You are an AI assistant...

            User question:
            {question}

            Portfolio summary:
            {summary}

            Extract and return a JSON object with:
            ... [full prompt 1 as defined earlier] ...
            """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return eval(response.choices[0].message["content"])

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
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"]
