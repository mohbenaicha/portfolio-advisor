import asyncio
import httpx

BASE_URL = "http://localhost:8000"
TOKEN = "d5a80990-4c1b-442e-af01-6a868e074e93"  # User2
OTHER_PORTFOLIO_ID = 9  # Belongs to User1

async def test_portfolio_crud_flow():
    async with httpx.AsyncClient() as client:
        print("\n=== Step 1: Authenticate as User2 ===")
        res = await client.post(f"{BASE_URL}/auth", json={"token": TOKEN})
        assert res.status_code == 200, f"X Auth failed: {res.text}"
        user_id = res.json()["user_id"]
        headers = {"x-user-id": str(user_id)}
        print(" Authenticated. User ID:", user_id)

        print("\n=== Step 2: List Own Portfolios ===")
        res = await client.get(f"{BASE_URL}/portfolios", headers=headers)
        assert res.status_code == 200
        print(f" Found {len(res.json())} portfolios")

        print("\n=== Step 3: Attempt to Access Another User's Portfolio ===")
        res = await client.get(f"{BASE_URL}/portfolios/{OTHER_PORTFOLIO_ID}", headers=headers)
        assert res.status_code in [403, 404], "X Unauthorized access not blocked"
        print(" Unauthorized access correctly blocked")

        print("\n=== Step 4: Create a New Portfolio ===")
        create_payload = {
            "name": "Integration_Portfolio_X",
            "assets": [{
                "ticker": "AAPL",
                "name": "Apple Inc.",
                "asset_type": "stock",
                "sector": "Technology",
                "region": "US",
                "market_price": 200.0,
                "units_held": 3,
                "is_hedge": False
            }]
        }
        res = await client.post(f"{BASE_URL}/portfolios", json=create_payload, headers=headers)
        assert res.status_code in [200, 201], f"X Portfolio creation failed: {res.text}"
        portfolio = res.json()
        portfolio_id = portfolio["id"]
        print(f" Portfolio created: {portfolio_id}")

        print("\n=== Step 5: Access Created Portfolio ===")
        res = await client.get(f"{BASE_URL}/portfolios/{portfolio_id}", headers=headers)
        assert res.status_code == 200
        print(" Accessed own created portfolio")

        print("\n=== Step 6: Update Portfolio ===")
        update_payload = {
            "name": "Updated_Portfolio_X",
            "assets": [{
                "ticker": "AAPL",
                "name": "Apple Inc.",
                "asset_type": "option",
                "sector": "Technology",
                "region": "US",
                "market_price": 300.0,
                "units_held": 100,
                "is_hedge": False
            }]
        }
        res = await client.put(f"{BASE_URL}/portfolios/{portfolio_id}", json=update_payload, headers=headers)
        assert res.status_code == 200
        updated = res.json()
        assert updated["name"] == "Updated_Portfolio_X"
        print('updated["assets"][0]["ticker"]', updated["assets"][0]["ticker"])
        assert updated["assets"][0]["ticker"] == "AAPL"
        print(" Portfolio updated successfully")

        print("\n=== Step 7: Delete Portfolio ===")
        res = await client.delete(f"{BASE_URL}/portfolios/{portfolio_id}", headers=headers)
        assert res.status_code == 200
        print(" Portfolio deleted")

        print("\n=== Step 8: Confirm Portfolio Deletion ===")
        res = await client.get(f"{BASE_URL}/portfolios/{portfolio_id}", headers=headers)
        assert res.status_code == 404, "X Deleted portfolio still accessible"
        print(" Deletion confirmed")

