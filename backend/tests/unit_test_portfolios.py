
import requests

BASE = "http://localhost:8000"

def test_get_all_portfolios():
    res = requests.get(f"{BASE}/portfolios")
    res.raise_for_status()
    portfolios = res.json()
    print("✅ GET /portfolios:", len(portfolios), "portfolios found")

def test_create_portfolio():
    payload = {
        "name": "Test Portfolio",
        "assets": [
            {
                "ticker": "TSLA",
                "name": "Tesla",
                "asset_type": "stock",
                "sector": "Technology",
                "region": "US",
                "market_price": 250.0,
                "units_held": 15,
                "is_hedge": False,
                "hedges_asset": ""
            }
        ]
    }
    res = requests.post(f"{BASE}/portfolios", json=payload)
    res.raise_for_status()
    print("✅ POST /portfolios: created Test Portfolio")

def test_delete_portfolio(id):
    res = requests.delete(f"{BASE}/portfolios/{id}")
    if res.status_code == 404:
        print(f"⚠️  DELETE /portfolios/{id}: not found")
    else:
        res.raise_for_status()
        print(f"✅ DELETE /portfolios/{id}: deleted")

if __name__ == "__main__":
    test_get_all_portfolios()
    test_create_portfolio()
    test_get_all_portfolios()
    test_delete_portfolio(3)
