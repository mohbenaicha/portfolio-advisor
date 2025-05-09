import requests
from os import getenv

API_KEY = getenv("ALPHA_VANTAGE_KEY")
BASE_URL = "https://www.alphavantage.co/query"

async def fetch_articles(entities):
    keywords = ",".join(entities.get("keywords", []))
    url = f"{BASE_URL}?function=NEWS_SENTIMENT&topics={keywords}&apikey={API_KEY}"
    response = requests.get(url)
    articles = response.json().get("feed", [])
    return [
        {
            "title": a["title"],
            "source": a["source"],
            "url": a["url"],
            "time_published": a["time_published"],
            "raw_article": "",  # filled later
            "query_tags": entities.get("keywords", []),
        } for a in articles
    ]
