from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.sql_models import UserProfile
from datetime import datetime, timezone

# TODO: remove for existing functionality
async def get_user_profiles(db: AsyncSession, user_id: int):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    return result.scalars().all()

# TODO: remove for existing functionality
async def get_user_profile_for_portfolio(db: AsyncSession, user_id: int, portfolio_id: int):
    # Get specific profile for portfolio
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id, UserProfile.portfolio_id == portfolio_id)
    )
    specific = result.scalars().first()
    # INSERT_YOUR_CODE
    # If a specific profile exists, fetch the portfolio name and set it as an attribute on the profile object
    if specific and specific.portfolio_id is not None:
        from app.models.sql_models import Portfolio
        portfolio_result = await db.execute(
            select(Portfolio.name).where(Portfolio.id == specific.portfolio_id)
        )
        portfolio_name = portfolio_result.scalar_one_or_none()
        # Set the name attribute on the specific profile object, even if it doesn't exist in the model
        setattr(specific, "name", portfolio_name)
    # Get general profile (All Portfolios)
    result_all = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id, UserProfile.portfolio_id == None)
    )
    general = result_all.scalars().first()
    return specific, general

async def create_user_profile(db: AsyncSession, user_id: int, portfolio_id: int, profile_data: dict | None = None):
    from app.models.sql_models import UserProfile
    
    # Convert lists to comma-separated strings if profile_data is provided
    short_term = ""
    long_term = ""
    sector_prefs = ""
    regional_prefs = ""
    asset_prefs = ""
    
    if profile_data:
        short_term = ",".join(profile_data.get("short_term_objectives", [])) if isinstance(profile_data.get("short_term_objectives"), list) else profile_data.get("short_term_objectives", "")
        long_term = ",".join(profile_data.get("long_term_objectives", [])) if isinstance(profile_data.get("long_term_objectives"), list) else profile_data.get("long_term_objectives", "")
        sector_prefs = ",".join(profile_data.get("sector_preferences", [])) if isinstance(profile_data.get("sector_preferences"), list) else profile_data.get("sector_preferences", "")
        regional_prefs = ",".join(profile_data.get("regional_preferences", [])) if isinstance(profile_data.get("regional_preferences"), list) else profile_data.get("regional_preferences", "")
        asset_prefs = ",".join(profile_data.get("asset_preferences", [])) if isinstance(profile_data.get("asset_preferences"), list) else profile_data.get("asset_preferences", "")
    
    profile = UserProfile(
        user_id=user_id,
        portfolio_id=portfolio_id,
        short_term_objectives=short_term,
        long_term_objectives=long_term,
        sector_preferences=sector_prefs,
        regional_preferences=regional_prefs,
        asset_preferences=asset_prefs,
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile

async def update_user_profile_fields(db: AsyncSession, user_id: int, portfolio_id: int, update_fields: dict):
    from app.models.sql_models import UserProfile
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id, UserProfile.portfolio_id == portfolio_id)
    )
    profile = result.scalars().first()
    if not profile:
        # Create a new profile if it doesn't exist
        return await create_user_profile(db, user_id, portfolio_id, update_fields)
    # Dynamically get updatable fields from the SQLAlchemy model
    exclude_fields = {"id", "user_id", "portfolio_id", "created_at", "updated_at"}
    updatable_fields = [c.name for c in UserProfile.__table__.columns if c.name not in exclude_fields]
    for field, value in update_fields.items():
        if field in updatable_fields:
            # If it's a list, store as comma-separated string
            if isinstance(value, list):
                setattr(profile, field, ",".join(value))
            else:
                setattr(profile, field, value)
    await db.commit()
    await db.refresh(profile)
    return profile 