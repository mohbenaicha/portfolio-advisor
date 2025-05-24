import os
from outscraper import ApiClient
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
client = ApiClient(api_key=os.getenv("OUTSCRAPER_API_KEY"))


def fetch_news(
    query: str = "options volatility", pages_per_query: int = 1, time_range: str = "w"
) -> list[dict]:
    """
    Fetches Google News articles based on the provided query.
    Args:
        qery: Search query.
        pages_per_query : Number of pages to fetch (10 articles per page).
        time_range: Time range for the articles. Options are "all_time", "h" (last hour), "d" (last day), "w" (last week), "m" (last month).
    Returns:
        A list of articles.
    """
    if len(query) == 0:
        return None

    response = client.google_search_news(
        query=query,
        pages_per_query=pages_per_query,
        tbs=time_range,
    )

    return response


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
        break

    if not news_response:
        return False

    return news_response
