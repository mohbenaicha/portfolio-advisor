import asyncio
import httpx

BASE_URL = "http://localhost:8000"
TOKEN = "d5a80990-4c1b-442e-af01-6a868e074e93"  # User2
PORTFOLIO_ID = 38  # Belongs to User2
OTHER_USER_ARCHIVE_ID = 1  # Assume this exists but belongs to User1

async def test_archive_endpoints():
    async with httpx.AsyncClient() as client:
        print("\n=== Step 1: Authenticate as User2 ===")
        res = await client.post(f"{BASE_URL}/auth", json={"token": TOKEN})
        assert res.status_code == 200, f"X Auth failed: {res.text}"
        user_id = res.json()["user_id"]
        headers = {"x-user-id": str(user_id)}
        print(" Authenticated. User ID:", user_id)

        print("\n=== Step 2: Ensure No Archives Exist Initially ===")
        res = await client.get(f"{BASE_URL}/archives", headers=headers)
        assert res.status_code == 200
        assert res.json() == [], "X Expected no archives"
        print("No existing archives for User2")

        print("\n=== Step 3: Create an Archive ===")
        payload = {
            "portfolio_id": PORTFOLIO_ID,
            "original_question": "What's the long-term outlook for tech ETFs?",
            "openai_response": "Tech ETFs may benefit from secular growth themes..."
        }
        res = await client.post(f"{BASE_URL}/archives", json=payload, headers=headers)
        assert res.status_code in [200, 201], f"X Failed to create archive: {res.text}"
        archive = res.json()
        archive_id = archive["id"]
        print(f"Archive created with ID: {archive_id}")

        print("\n=== Step 3b: Attempt Invalid Archive Creation (Wrong Portfolio ID) ===")
        bad_payload = {
            "portfolio_id": 9,  # belongs to User1
            "original_question": "Is oil a good hedge right now?",
            "openai_response": "Oil may act as a partial inflation hedge..."
        }
        res = await client.post(f"{BASE_URL}/archives", json=bad_payload, headers=headers)
        assert res.status_code in [400, 403, 404, 422, 500], "X Invalid archive creation not blocked"
        print("Invalid archive creation blocked as expected")


        print("\n=== Step 4: List Archives Again ===")
        res = await client.get(f"{BASE_URL}/archives", headers=headers)
        assert any(a["id"] == archive_id for a in res.json()), "X Created archive not found"
        print("Archive appears in list")

        print("\n=== Step 5: Retrieve Archive by ID ===")
        res = await client.get(f"{BASE_URL}/responses/{archive_id}", headers=headers)
        assert res.status_code == 200, "X Failed to retrieve archive"
        print("Successfully retrieved archive")

        print("\n=== Step 6: Attempt to Access Another User’s Archive ===")
        res = await client.get(f"{BASE_URL}/responses/{OTHER_USER_ARCHIVE_ID}", headers=headers)
        assert res.status_code in [403, 404], "X Unauthorized archive access not blocked"
        print("Unauthorized access correctly blocked")
