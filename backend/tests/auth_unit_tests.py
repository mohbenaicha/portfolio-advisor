
import httpx

BASE_URL = "http://localhost:8000"

VALID_TOKEN = "df77c9be-67fb-44b9-a15c-8146131e2d14"  # User1
INVALID_TOKEN = "deadbeef-dead-beef-dead-beefdeadbeef"
VALID_USER_ID = "1"
INVALID_USER_ID = "9999"

async def test_valid_token_auth():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        res = await client.post("/auth", json={"token": VALID_TOKEN})
        print("VALID TOKEN AUTH:", res.status_code, res.json())

async def test_invalid_token_auth():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        res = await client.post("/auth", json={"token": INVALID_TOKEN})
        print("INVALID TOKEN AUTH:", res.status_code, res.json())

async def test_missing_user_header_on_portfolios():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        res = await client.get("/portfolios")
        print("MISSING USER HEADER /portfolios:", res.status_code, res.json())

async def test_fake_user_id_on_portfolios():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        res = await client.get("/portfolios", headers={"x-user-id": INVALID_USER_ID})
        print("FAKE USER ID /portfolios:", res.status_code, res.json())

async def test_missing_user_header_on_archives():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        res = await client.get("/archives")
        print("MISSING USER HEADER /archives:", res.status_code, res.json())

async def test_fake_user_id_on_archives():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        res = await client.get("/archives", headers={"x-user-id": INVALID_USER_ID})
        print("FAKE USER ID /archives:", res.status_code, res.json())

async def run_all_auth_tests():
    await test_valid_token_auth()
    await test_invalid_token_auth()
    await test_missing_user_header_on_portfolios()
    await test_fake_user_id_on_portfolios()
    await test_missing_user_header_on_archives()
    await test_fake_user_id_on_archives()