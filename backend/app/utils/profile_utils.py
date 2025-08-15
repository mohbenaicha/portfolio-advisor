import httpx
from sqlalchemy.inspection import inspect
from app.config import SYSTEM_USER_TOKEN, BACKEND_SERVICE_MAP
from app.models.schemas import UserProfileResponse
from app.services.profile_service import str_to_list


def profile_to_response(profile):
    return UserProfileResponse(
        id=getattr(profile, 'id'),
        user_id=getattr(profile, 'user_id'),
        portfolio_id=getattr(profile, 'portfolio_id'),
        short_term_objectives=str_to_list(getattr(profile, 'short_term_objectives')),
        long_term_objectives=str_to_list(getattr(profile, 'long_term_objectives')),
        sector_preferences=str_to_list(getattr(profile, 'sector_preferences')),
        regional_preferences=str_to_list(getattr(profile, 'regional_preferences')),
        asset_preferences=str_to_list(getattr(profile, 'asset_preferences')),
        created_at=getattr(profile, 'created_at'),
        updated_at=getattr(profile, 'updated_at'),
    )


def profile_to_text(profile, label=None) -> str:
    if not isinstance(profile, dict):
        profile = sqlalchemy_object_to_dict(profile)
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
    for field, value in profile.items():  # Iterate directly over the dictionary
        if field in exclude:
            continue
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
    
    
def sqlalchemy_object_to_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}