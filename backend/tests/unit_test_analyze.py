# tests/test_analyze.py

from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)


def mock_extract_entities(question, summary):
    return {
        "themes": ["AI"],
        "regions": ["Asia"],
        "asset_types": ["stocks"],
        "sectors": ["technology"],
        "keywords": ["emerging markets"],
    }


def mock_fetch_articles(entities):
    return [
        {
            "title": "AI Growth in Asia",
            "url": "https://example.com/ai",
            "source": "MockTimes",
        },
        {
            "title": "Emerging Tech Trends",
            "url": "https://example.com/tech",
            "source": "MockFinance",
        },
    ]


def mock_extract_with_readability(url):
    return f"Full content for {url}"


def mock_summarize_articles(articles):
    return [
        {
            "title": article["title"],
            "url": article["url"],
            "source": article["source"],
            "summary": f"Summary for {article['title']}",
            "time_published": "2025-05-12T10:00:00Z",  # Added time_published field
        }
        for article in articles
    ]


def mock_generate_advice(question, portfolio_data, summaries):
    return f"Mocked investment advice for: {question} with {len(summaries)} summaries."


@patch("app.core.prompt_logic.extract_entities", side_effect=mock_extract_entities)
@patch("app.core.prompt_logic.fetch_articles", side_effect=mock_fetch_articles)
@patch(
    "app.core.prompt_logic.extract_with_readability",
    side_effect=mock_extract_with_readability,
)
@patch("app.core.prompt_logic.summarize_articles", side_effect=mock_summarize_articles)
@patch("app.core.prompt_logic.generate_advice", side_effect=mock_generate_advice)
def run_test(mock1, mock2, mock3, mock4, mock5):
    payload = payload = {
        "question": "What are good assets to add to this portfolio?",
        "portfolio_data": [
            {
                "ticker": "BND",
                "name": "Vanguard Total Bond",
                "asset_type": "bond",
                "sector": "GovernmentBonds",
                "region": "Global",
                "market_price": 80,
                "units_held": 100,
                "is_hedge": False,
                "hedges_asset": None,
            },
            {
                "ticker": "VTI",
                "name": "Total US Market",
                "asset_type": "stock",
                "sector": "Finance",
                "region": "US",
                "market_price": 230,
                "units_held": 20,
                "is_hedge": False,
                "hedges_asset": None,
            },
        ],
        "portfolio_summary": {
            "asset_types": ["bond", "stock"],
            "sectors": ["GovernmentBonds", "Finance"],
            "regions": ["Global", "US"],
        },
    }

    try:
        response = client.post("/analyze", json=payload)
        if response.status_code != 200:
            print(f"❌ POST /analyze: status {response.status_code}")
            print(response.text)
            return

        data = response.json()
        if (
            "summary" in data
            and "Mocked investment advice" in data["summary"]
            and "articles" in data
            and len(data["articles"]) == 2
            and all("summary" in a for a in data["articles"])
        ):
            print(
                "✅ POST /analyze: full internal logic passed with external services mocked"
            )
        else:
            print("❌ POST /analyze: unexpected response structure")
            print(data)

    except Exception as e:
        print("❌ POST /analyze: exception occurred")
        print(e)

        