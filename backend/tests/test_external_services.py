import json
from os import getenv
import requests
from random import choice
import urllib.request

from app.services.openai_client import extract_entities
import asyncio
import json
from unittest.mock import patch, AsyncMock
from app.services.openai_client import generate_advice


def test_alpha_vantage_news_sentiment_api(keywords="technology,finance"):
    # Replace 'YOUR_API_KEY' with your actual Alpha Vantage API key
    api_key = getenv("ALPHA_VANTAGE_KEY")
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topics={keywords}&apikey={api_key}"

    try:
        # Make the API request
        response = urllib.request.urlopen(url)
        data = response.read()
        json_data = json.loads(data)

        if "feed" in json_data:
            print("Test Passed: Alpha Vantage News Sentiment API returned valid data.")
            for article in json_data["feed"]:
                print("\n")
                title = article.get("title", "No Title")
                link = article.get("url", "No URL")
                print(f"Title: {title}\nLink: {link}\n")
        else:
            print("Test Failed: Expected key 'feed' not found in response.")
    except Exception as e:
        print(f"Test Failed: An error occurred - {e}")


async def test_openai_extract_entities():

    question = "How does the market news and sentiment affect my portofolio?"
    # Fetch portfolios from the API
    response = requests.get("http://localhost:8000/portfolios")
    if response.status_code == 200:
        portfolios = response.json()
        if portfolios:
            selected_portfolio = choice(portfolios)  # Pick a random portfolio
            print("Selected Portfolio:", selected_portfolio)
            summary = {
                "asset_types": list(
                    {
                        asset["asset_type"]
                        for asset in selected_portfolio.get("assets", [])
                    }
                ),
                "sectors": list(
                    {asset["sector"] for asset in selected_portfolio.get("assets", [])}
                ),
                "regions": list(
                    {asset["region"] for asset in selected_portfolio.get("assets", [])}
                ),
            }
            print("Portfolio Summary:", summary)
        else:
            print("No portfolios available to select.")
            summary = {}
            return
    else:
        print(f"Failed to fetch portfolios: {response.status_code}")
        summary = {}
        return

    try:
        result = await extract_entities(question, summary)

        # Print the result
        print("Test Passed: OpenAI extract_entities returned valid data.")
        print("Extracted Entities:\n", result)
    except Exception as e:
        print(f"Test Failed: An error occurred - {e}")


async def test_generate_advice():
    # Define the question and portfolio
    question = "What is the best investment strategy for my portfolio given the current market conditions?"
    portfolio = {
        "id": 2,
        "name": "Emerging Markets Play",
        "assets": [
            {
                "ticker": "EEM",
                "name": "MSCI EM Index ETF",
                "asset_type": "stock",
                "sector": "Finance",
                "region": "Emerging Markets",
                "market_price": 45.0,
                "units_held": 500.0,
                "is_hedge": False,
                "hedges_asset": "",
                "id": 15,
            },
            {
                "ticker": "PBR",
                "name": "Petrobras",
                "asset_type": "stock",
                "sector": "Energy",
                "region": "Emerging Markets",
                "market_price": 12.0,
                "units_held": 200.0,
                "is_hedge": False,
                "hedges_asset": "",
                "id": 16,
            },
            {
                "ticker": "PBR-PUT",
                "name": "Petrobras Put Option",
                "asset_type": "option",
                "sector": "Energy",
                "region": "Emerging Markets",
                "market_price": 1.5,
                "units_held": 100.0,
                "is_hedge": True,
                "hedges_asset": "PBR",
                "id": 17,
            },
        ],
    }

    # Load articles from the JSON file
    with open("./article_content.json", "r") as file:
        articles_data = json.load(file)
    articles = [
        {"title": f"Article {i+1}", "summary": article["summary"]}
        for i, article in enumerate(articles_data[:2])
    ]

    # Mock the OpenAI API response
    mock_response = AsyncMock()
    mock_response.choices = [
        {
            "message": {
                "content": "This is a mock financial analysis and recommendation."
            }
        }
    ]

    with patch("openai.ChatCompletion.create", return_value=mock_response):
        result = await generate_advice(question, portfolio, articles)

        # Assertions
        assert result == "This is a mock financial analysis and recommendation."
        print("Test Passed: generate_advice returned valid data.")
        print("Generated Advice:\n", result)


# test_openai_extract_entities()
# test_alpha_vantage_news_sentiment_api()
# test_generate_advice()
