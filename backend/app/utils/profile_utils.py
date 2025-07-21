import httpx
from app.config import SYSTEM_USER_TOKEN, BACKEND_SERVICE_MAP


def profile_to_text(profile, label = None) -> str:
    if not profile:
        return ""
    exclude = {"id", "user_id", "portfolio_id", "name", "created_at", "updated_at"}
    def fmt(val):
        if isinstance(val, list):
            return ', '.join(str(v) for v in val) if val else 'N/A'
        if isinstance(val, str):
            return val if val else 'N/A'
        return str(val) if val else 'N/A'
    lines = [f"Profile for {label}:"] if label else []
    for field in vars(profile):
        if field in exclude:
            continue
        value = getattr(profile, field, None)
        lines.append(f"{field}: {fmt(value)}")
    return "\n".join(lines) 


async def fetch_profile_from_service(portfolio_id: str, user_id: int) -> dict:
    profile_service_url = BACKEND_SERVICE_MAP.get("profile")
    # admin user can access any profile
    request_url = f"{profile_service_url}/profiles/admin/portfolio/{portfolio_id}"
    print("fetch_profile_from_service URL:", profile_service_url)
    print("request: URL:", request_url)
    async with httpx.AsyncClient() as client:
        response = await client.post( 
            request_url,
            headers={"Authorization": f"Bearer {SYSTEM_USER_TOKEN}"},
            json={
                "user_id": user_id
            },  # Explicitly pass the target user_id since system user is able to access any portfolio
        ) # response =  {specific: UserProfileResponse, general: UserProfileResponse}
        response.raise_for_status()
        return response.json()