import httpx

BASE_URL = "http://localhost:8000"
USER_TOKEN = "df77c9be-67fb-44b9-a15c-8146131e2d14"  # Replace with actual token for user 1
USER_ID = "1"

HEADERS = {
    "Authorization": f"Bearer {USER_TOKEN}",
    "x-user-id": USER_ID,
    "Content-Type": "application/json"
}

async def test_analyze_endpoint():
    async with httpx.AsyncClient() as client:
        # Step 1: Authenticate
        auth_payload = {"token": USER_TOKEN}
        auth_resp = await client.post(f"{BASE_URL}/auth", json=auth_payload)
        assert auth_resp.status_code == 200
        user_id = auth_resp.json().get("user_id")
        assert user_id is not None

        # Step 2: Call analyze with x-user-id header
        analyze_payload = {
            "question": "I want to fully shift my portfolio to renewable energy. Can you recommend some well performing assets?",
            "portfolio_id": 9
        }
        headers = {"x-user-id": str(user_id)}
        analyze_resp = await client.post(f"{BASE_URL}/analyze", json=analyze_payload, headers=headers)
        assert analyze_resp.status_code == 200
        analyze_data = analyze_resp.json()
        assert "summary" in analyze_data
        assert isinstance(analyze_data["summary"], str) and analyze_data["summary"]