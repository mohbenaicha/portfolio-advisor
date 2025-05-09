import requests

BASE = "http://localhost:8000"

dummy_portfolios = [
    {
        "name": "Tech Growth",
        "assets": [
            {
                "ticker": "AAPL",
                "name": "Apple Inc.",
                "asset_type": "stock",
                "sector": "Technology",
                "region": "US",
                "market_price": 180,
                "units_held": 50,
                "is_hedge": False,
                "hedges_asset": "",
            },
            {
                "ticker": "GOOGL",
                "name": "Alphabet",
                "asset_type": "stock",
                "sector": "Technology",
                "region": "US",
                "market_price": 2800,
                "units_held": 10,
                "is_hedge": False,
                "hedges_asset": "",
            },
        ],
    },
    {
        "name": "Diversified Global",
        "assets": [
            {
                "ticker": "BND",
                "name": "Vanguard Total Bond",
                "asset_type": "bond",
                "sector": "GovernmentBonds",  # ✅ matches DB enum
                "region": "Global",
                "market_price": 80,
                "units_held": 100,
                "is_hedge": False,
                "hedges_asset": "",
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
                "hedges_asset": "",
            },
        ],
    },
]

dummy_responses = [{
    "portfolio_id": 1,
    "original_question": "Is this tech-heavy portfolio risky?",
    "openai_response": "Mock AI: Tech exposure is significant but well diversified.",
    "article_ids": ["https://mock.com/aapl", "https://mock.com/googl"],
    "summary_tags": ["Technology", "US", "stock"],
}]

for p in dummy_portfolios:
    res = requests.post(f"{BASE}/portfolios", json=p)
    res.raise_for_status()
    print(f"Created portfolio: {p['name']}")

for r in dummy_responses:
    res = requests.post(f"{BASE}/archives", json=r)
    res.raise_for_status()
    print(f"Created archive for portfolio ID: {r['portfolio_id']}")