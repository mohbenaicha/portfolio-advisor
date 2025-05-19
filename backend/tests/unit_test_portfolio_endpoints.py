import httpx
import random

BASE_URL = "http://localhost:8000"
USER_ID = "2"
HEADERS = {"x-user-id": USER_ID}
PORTFOLIO_ID = None


async def test_create_portfolio():
    global PORTFOLIO_ID
    payload = {
        "name": f"Test Portfolio {random.randint(1000, 9999)}",
        "assets": [
            {
                "ticker": "NVDA",
                "name": "Nvidia Corp.",
                "asset_type": "stock",
                "sector": "Technology",
                "region": "US",
                "market_price": 1000.0,
                "units_held": 2,
                "is_hedge": False,
                "hedges_asset": None,
            }
        ],
    }
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        res = await client.post("/portfolios", json=payload, headers=HEADERS)
        print("CREATE PORTFOLIO:", res.status_code, res.text)
        try:
            data = res.json()
            PORTFOLIO_ID = data.get("id")
            print("Portfolio ID:", PORTFOLIO_ID)
        except Exception:
            print("Failed to parse JSON response")


async def test_get_all_portfolios():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        res = await client.get("/portfolios", headers=HEADERS)
        print("GET ALL PORTFOLIOS:", res.status_code, res.text)


async def test_get_portfolio_by_id():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        res = await client.get(f"/portfolios/{PORTFOLIO_ID}", headers=HEADERS)
        print("GET PORTFOLIO BY ID:", res.status_code, res.text)


async def test_update_portfolio():
    payload = {
        "name": f"Updated Test Portfolio SOMETHING Totall Else",
        "assets": [
            {
                "ticker": "TSLA",
                "name": "Tesla Inc.",
                "asset_type": "stock",
                "sector": "Technology",
                "region": "US",
                "market_price": 50.0,
                "units_held": 100,
                "is_hedge": False,
                "hedges_asset": None,
            },
            {
                "ticker": "SpaceX",
                "name": "SpaceX Rocket People",
                "asset_type": "bond",
                "sector": "Technology",
                "region": "US",
                "market_price": 980.0,
                "units_held": 15,
                "is_hedge": False,
                "hedges_asset": None,
            }
        ],
    }
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        res = await client.put(
            f"/portfolios/{20}", json=payload, headers=HEADERS
        )
        print("UPDATE PORTFOLIO:", res.status_code, res.text)


async def run_all_portfolio_endpoint_unit_tests():
    global PORTFOLIO_ID

    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        res = await client.post(
            "/auth", json={"token": "df77c9be-67fb-44b9-a15c-8146131e2d14"}
        )
        print("AUTH:", res.status_code, res.text)

    await test_create_portfolio()
    await test_get_all_portfolios()
    await test_get_portfolio_by_id()
    await test_update_portfolio()
