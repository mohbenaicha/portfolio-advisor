
import requests

BASE = "http://localhost:8000"

def test_get_archives():
    res = requests.get(f"{BASE}/archives")
    res.raise_for_status()
    data = res.json()
    print("✅ GET /archives:", len(data), "archives found")

def test_get_response_by_id(id):
    res = requests.get(f"{BASE}/responses/{id}")
    if res.status_code == 404:
        print(f"⚠️  GET /responses/{id}: not found")
    else:
        res.raise_for_status()
        print(f"✅ GET /responses/{id}: archive retrieved")

def test_create_archive():
    payload = {
        "portfolio_id": 1,
        "original_question": "Should I worry about inflation?",
        "openai_response": "Mock AI: Inflation is cooling off, but maintain defensive positions.",
        "article_ids": ["https://mock.com/inflation"],
        "summary_tags": ["Finance", "US"]
    }
    res = requests.post(f"{BASE}/archives", json=payload)
    res.raise_for_status()
    print("✅ POST /archives: archive created")

if __name__ == "__main__":
    test_get_archives()
    test_create_archive()
    test_get_archives()
    test_get_response_by_id(1)
