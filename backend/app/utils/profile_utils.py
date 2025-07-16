import httpx
from app.config import SYSTEM_USER_TOKEN, BACKEND_SERVICE_MAP
def profile_to_text(profile, label):
    if not profile:
        return ""
    exclude = {"id", "user_id", "portfolio_id", "name", "created_at", "updated_at"}
    def fmt(val):
        if isinstance(val, list):
            return ', '.join(str(v) for v in val) if val else 'N/A'
        if isinstance(val, str):
            return val if val else 'N/A'
        return str(val) if val else 'N/A'
    lines = [f"Profile for {label}:"]
    for field in vars(profile):
        if field in exclude:
            continue
        value = getattr(profile, field, None)
        lines.append(f"{field}: {fmt(value)}")
    return "\n".join(lines) 


async def fetch_profile(portfolio_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_SERVICE_MAP.get('profile')}/profiles/portfolio/{portfolio_id}",
            headers={"Authorization": f"Bearer {SYSTEM_USER_TOKEN}"}
        )
        response.raise_for_status()
        return response.json()