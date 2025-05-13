import requests

BASE = "http://localhost:8000"

dummy_portfolios = [
    {
        "name": "Macro Hedged Fund",
        "assets": [
            {
                "ticker": "TLT",
                "name": "20Y Treasury ETF",
                "asset_type": "bond",
                "sector": "GovernmentBonds",
                "region": "US",
                "market_price": 90,
                "units_held": 150,
                "is_hedge": False,
                "hedges_asset": "",
            },
            {
                "ticker": "TLT-SWAP",
                "name": "TLT Swap Hedge",
                "asset_type": "swap",
                "sector": "GovernmentBonds",
                "region": "US",
                "market_price": 10,
                "units_held": 100,
                "is_hedge": True,
                "hedges_asset": "TLT",
            },
            {
                "ticker": "GLD",
                "name": "Gold ETF",
                "asset_type": "stock",
                "sector": "Energy",
                "region": "Global",
                "market_price": 170,
                "units_held": 30,
                "is_hedge": False,
                "hedges_asset": "",
            },
        ],
    },
    {
        "name": "Emerging Markets Play",
        "assets": [
            {
                "ticker": "EEM",
                "name": "MSCI EM Index ETF",
                "asset_type": "stock",
                "sector": "Finance",
                "region": "EmergingMarkets",
                "market_price": 45,
                "units_held": 500,
                "is_hedge": False,
                "hedges_asset": "",
            },
            {
                "ticker": "PBR",
                "name": "Petrobras",
                "asset_type": "stock",
                "sector": "Energy",
                "region": "EmergingMarkets",
                "market_price": 12,
                "units_held": 200,
                "is_hedge": False,
                "hedges_asset": "",
            },
            {
                "ticker": "PBR-PUT",
                "name": "Petrobras Put Option",
                "asset_type": "option",
                "sector": "Energy",
                "region": "EmergingMarkets",
                "market_price": 1.5,
                "units_held": 100,
                "is_hedge": True,
                "hedges_asset": "PBR",
            },
        ],
    },
    {
        "name": "European Defensive",
        "assets": [
            {
                "ticker": "SIEGY",
                "name": "Siemens AG",
                "asset_type": "stock",
                "sector": "Manufacturing",
                "region": "Europe",
                "market_price": 75,
                "units_held": 80,
                "is_hedge": False,
                "hedges_asset": "",
            },
            {
                "ticker": "VOD",
                "name": "Vodafone Group",
                "asset_type": "stock",
                "sector": "Technology",
                "region": "Europe",
                "market_price": 9,
                "units_held": 600,
                "is_hedge": False,
                "hedges_asset": "",
            },
        ],
    },
]

dummy_responses = [
    {
        "portfolio_id": 3,
        "original_question": "Is this tech-heavy portfolio risky?",
        "openai_response": "Mock AI: Tech exposure is significant but well diversified.",
        "article_ids": ["https://mock.com/aapl", "https://mock.com/googl"],
        "summary_tags": ["Technology", "US", "stock"],
    }
]

for p in dummy_portfolios:
    res = requests.post(f"{BASE}/portfolios", json=p)
    res.raise_for_status()
    print(res.text)
    print(f"Created portfolio: {p['name']}")

for r in dummy_responses:
    res = requests.post(f"{BASE}/archives", json=r)
    res.raise_for_status()
    print(res.text)
    print(f"Created archive for portfolio ID: {r['portfolio_id']}")
