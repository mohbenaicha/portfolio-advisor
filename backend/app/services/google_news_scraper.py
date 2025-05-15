import requests
import feedparser
from app.utils.article_scraper import extract_with_readability
BASE_URL = "https://news.google.com/rss/search"

async def fetch_articles(entities):
    
    keywords = ",".join(entities.get("keywords", []))
    
    url = f"{BASE_URL}?q={keywords}"
    feed = feedparser.parse(url)
    
    return [
        {
            "title": a["title"],
            "source": a["title"].split(" - ")[-1] if " - " in a["title"] else "Unknown",
            "url": a["link"],
            "time_published": a["published"],
            "raw_article": extract_with_readability(a["link"]), 
            "query_tags": entities.get("keywords", []),
        } for a in feed.entries[:50]
    ]
