from app.services.google_news_scraper import fetch_articles
from app.utils.article_scraper import extract_with_readability



async def test_article_scraping_and_saving():
    articles = await fetch_articles(
        {
            "keywords": ["options volatility", "stock market"],
        }
    )
    for article in articles[0]:
        article["content"] = extract_with_readability(article["link"])
        print(article)
        print()
        print()

    
