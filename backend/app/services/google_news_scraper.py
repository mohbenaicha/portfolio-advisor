import time
from outscraper import ApiClient
from app.config import OUTSCRAPER_API_KEY

client = ApiClient(api_key=OUTSCRAPER_API_KEY)

def is_junk_news_link(link: str) -> bool:
    return "news.google.com/read" in link

def fetch_news(query: str = "options volatility", pages_per_query: int = 1, time_range: str = "w", retries: int = 10) -> list[dict]:
    if not query:
        return None

    for _ in range(retries + 1):
        response = client.google_search_news(
            query=query,
            pages_per_query=pages_per_query,
            tbs=time_range,
        )

        articles = response[0]
        if articles and not all(is_junk_news_link(article.get("link", "")) for article in articles):
            return response
        time.sleep(2)  # wait before retrying

    return response  # return even if junk after retries


async def fetch_articles(entities):
    if len(entities) == 0:
        return False
    news_response = []
    for entity in entities:
        response = fetch_news(entity.get("theme", ""), 1, time_range="w")

        if response[0] != []:
            for article in response[0]:
                article["keywords"] = entity.get("keywords", [])    
                news_response.append(article) 

    if not news_response:
        return False

    return news_response
