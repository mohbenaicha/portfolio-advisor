import time
from outscraper import ApiClient
from app.config import OUTSCRAPER_API_KEY

client = ApiClient(api_key=OUTSCRAPER_API_KEY)


def is_junk_news_link(link: str) -> bool:
    return "news.google.com/read" in link


def fetch_news(
    query: str = "options volatility",
    pages_per_query: int = 1,
    time_range: str = "w",
    retries: int = 10,
) -> list[dict]:
    if not query:
        return None

    for _ in range(retries + 1):
        response = client.google_search_news(
            query=query,
            pages_per_query=pages_per_query,
            tbs=time_range,
        )

        articles = response[0]
        if articles and not all(
            is_junk_news_link(article.get("link", "")) for article in articles
        ):
            return response
        time.sleep(3)  # wait before retrying

    return []


async def fetch_articles(themes):
    if len(themes) == 0:
        return False
    news_response = []
    for theme in themes:
        print(f"Fetching news for theme: {theme.get('theme', '')}")
        response = fetch_news(theme.get("theme", ""), 1, time_range="w")
        if response and response[0] != []:
            for article in response[0]:
                news_response.append(article)
        break
    if not news_response:
        return False

    return news_response
