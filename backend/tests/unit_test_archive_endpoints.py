import asyncio
import httpx

BASE_URL = "http://localhost:8000"
USER_ID = "2"
HEADERS = {"x-user-id": USER_ID}
PORTFOLIO_ID = 2
ARCHIVE_ID = 1

def print_response(label, res):
    if res.headers.get("content-type") == "application/json":
        print(f"{label}:", res.status_code, res.json())
    else:
        print(f"{label}:", res.status_code, res.text)

async def test_create_archive():
    global ARCHIVE_ID
    payload = {
        "portfolio_id": PORTFOLIO_ID,
        "original_question": "What is up with tech stocks?",
        "openai_response": "Tech is flying.",
        "summary_tags": ["tech", "growth"]
    }
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        res = await client.post("/archives", json=payload, headers=HEADERS)
        print_response("CREATE ARCHIVE", res)
        if res.status_code == 200:
            ARCHIVE_ID = res.json().get("id")

async def test_get_all_archives():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        res = await client.get("/archives", headers=HEADERS)
        print_response("GET ALL ARCHIVES", res)

async def test_get_archive_by_id():
    if ARCHIVE_ID is None:
        print("GET ARCHIVE BY ID: skipped (no archive created)")
        return
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        res = await client.get(f"/responses/{ARCHIVE_ID}", headers=HEADERS)
        print_response("GET ARCHIVE BY ID", res)

async def test_delete_portfolio():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        res = await client.delete(f"/portfolios/{PORTFOLIO_ID}", headers=HEADERS)
        print_response("DELETE PORTFOLIO", res)

async def run_all_archive_endpoint_unit_tests():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        res = await client.post("/auth", json={"token": "df77c9be-67fb-44b9-a15c-8146131e2d14"})
        print_response("AUTH", res)

    await test_create_archive()
    await test_get_all_archives()
    await test_get_archive_by_id()
    await test_delete_portfolio()

