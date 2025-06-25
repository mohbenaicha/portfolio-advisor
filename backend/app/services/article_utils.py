from typing import Optional
import requests
from bs4 import BeautifulSoup, Tag
from urllib.parse import urlparse


def extract_thumbnail_image(url: str):
    try:
        resp = requests.get(url, timeout=5)
        soup = BeautifulSoup(resp.text, "html.parser")
        og_image = soup.find("meta", property="og:image")
        image = None
        if isinstance(og_image, Tag):
            content = og_image.get("content", None)
            if isinstance(content, str) and content:
                image = content
        twitter_image = soup.find("meta", attrs={"name": "twitter:image"})
        if not image and isinstance(twitter_image, Tag):
            content = twitter_image.get("content", None)
            if isinstance(content, str) and content:
                image = content
        # Title
        title_tag = soup.find("meta", property="og:title")
        title = None
        if isinstance(title_tag, Tag):
            t = title_tag.get("content", None)
            if isinstance(t, str) and t:
                title = t
        if not title:
            t = soup.title.string if soup.title else None
            if isinstance(t, str) and t:
                title = t
        # Source (domain)
        parsed = urlparse(url)
        source = parsed.hostname.replace('www.', '') if parsed.hostname else None
        return {"image": image, "title": title, "source": source}
    except Exception:
        return {"image": None, "title": None, "source": None} 