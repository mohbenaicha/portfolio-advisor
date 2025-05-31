import requests
from bs4 import BeautifulSoup
from readability import Document
from app.config import SCRAPER_HEADERS as HEADERS

async def extract_with_readability(url: str) -> str:
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        doc = Document(response.text)
        article_html = doc.summary()
        soup = BeautifulSoup(article_html, "html.parser")
        paragraphs = [p.get_text() for p in soup.find_all("p") if len(p.get_text()) > 40]
        return "\n\n".join(paragraphs)
    except Exception as e:
        return f"Readability extraction failed: {e}"
