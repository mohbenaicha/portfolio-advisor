import json
from os import getenv
import requests
from random import choice
import urllib.request
from unittest.mock import patch, AsyncMock

from app.services.langchain_summary import summarize_articles
from app.services.openai_client import extract_entities
from app.services.openai_client import generate_advice
from app.utils.portfolio_utils import get_asset_representation, get_exposure_summary
from app.utils.news_utils import news_summary_string_representation


def test_alpha_vantage_news_sentiment_api(keywords="technology,US"):
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


from langchain.llms.base import LLM


class MockLLM(LLM):
    def _call(self, prompt, stop=None):
        return "Mock summary of: " + prompt[:100]

    @property
    def _llm_type(self):
        return "mock"


async def test_langchain_summary():
    # Load articles from the JSON file
    with open("./tests/article_content.json", "r", encoding="utf-8") as file:
        articles_data = json.load(
            file,
        )

    articles = [
        {
            "raw_article": article["Content"],
            "url": article["Link"],
            "title": title,
        }
        for title, article in list(articles_data.items())[
            :10
        ]  # {title: {content:  content, link: url}, ...}
    ]
    print("Loaded article samples:\n\n", articles[0])

    test_llm = MockLLM()

    summarized_articles = await summarize_articles(articles)
    for article in summarized_articles:
        print("Article URL:", article["url"])
        print("Summary:", article["summary"])
        print("Title:", article["title"])
        print("\n")

    # Write the summaries to a JSON file
    with open("./tests/article_summary.json", "w") as file:
        json.dump(
            [
                {
                    "title": article["title"],
                    "summary": article["summary"],
                    "url": article["url"],
                }
                for article in summarized_articles
            ],
            file,
            indent=4,
        )
    print("Summaries written to article_summary.json")


async def test_generate_advice():
    # Define the question and portfolio
    question = "What is the best investment strategy for my portfolio given the current market conditions?"

    response = requests.get("http://localhost:8000/portfolios")
    if response.status_code == 200:
        portfolios = response.json()
        if portfolios:
            selected_portfolio = choice(portfolios)  # Pick a random portfolio
            print("Selected Portfolio:", selected_portfolio)
            portfolio_string_rep = "\n".join(
                [
                    get_asset_representation(selected_portfolio),
                    get_exposure_summary(selected_portfolio),
                ]
            )
            # Organize assets into a string representation

        else:
            print("No portfolios available to select.")
            return
    else:
        print(f"Failed to fetch portfolios: {response.status_code}")
        return

    with open("./tests/article_summary.json", "r") as file:
        articles_summaries = json.load(file)
    articles_string_rep = news_summary_string_representation(articles_summaries)

    result = await generate_advice(question, portfolio_string_rep, articles_string_rep)

    # Assertions
    print("Generated Advice:\n", result)


# test_openai_extract_entities()
# test_alpha_vantage_news_sentiment_api()
# test_generate_advice()
