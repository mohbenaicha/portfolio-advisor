import requests
from bs4 import BeautifulSoup
from readability import Document
from app.config import SCRAPER_HEADERS as HEADERS

async def extract_with_readability(url: str) -> str:
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if not response.text.strip():
            return "Readability extraction failed: Empty response from URL."

        doc = Document(response.text)
        article_html = doc.summary()
        if not article_html.strip():
            return "Readability extraction failed: Empty summary from Document."

        soup = BeautifulSoup(article_html, "html.parser")
        paragraphs = [p.get_text() for p in soup.find_all("p") if len(p.get_text()) > 40]
        if not paragraphs:
            return "Readability extraction failed: No readable paragraphs found."

        return "\n\n".join(paragraphs)

    except Exception as e:
        return f"Readability extraction failed: {type(e).__name__}: {e}"

