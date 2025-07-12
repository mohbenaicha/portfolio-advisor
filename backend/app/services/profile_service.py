from app.models.sql_models import UserProfile
from app.models.schemas import UserProfileCreate, UserProfileUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional, Sequence

# Helper functions for conversion

def list_to_str(lst: Optional[List[str]]) -> str:
    return ",".join(lst) if lst else ""

def str_to_list(s: Optional[str]) -> List[str]:
    return s.split(",") if s else []

# CRUD operations

async def create_profile(db: AsyncSession, user_id: int, profile_in: UserProfileCreate) -> UserProfile:
    profile = UserProfile(
        user_id=user_id,
        portfolio_id=profile_in.portfolio_id,
        short_term_objectives=list_to_str(profile_in.short_term_objectives),
        long_term_objectives=list_to_str(profile_in.long_term_objectives),
        sector_preferences=list_to_str(profile_in.sector_preferences),
        regional_preferences=list_to_str(profile_in.regional_preferences),
        asset_preferences=list_to_str(profile_in.asset_preferences),
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile

async def get_profiles(db: AsyncSession, user_id: int) -> Sequence[UserProfile]:
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    return result.scalars().all()

async def get_profile(db: AsyncSession, user_id: int, portfolio_id: Optional[int]) -> Optional[UserProfile]:
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id, UserProfile.portfolio_id == portfolio_id)
    )
    return result.scalars().first()

async def update_profile(db: AsyncSession, user_id: int, profile_id: int, profile_in: UserProfileUpdate) -> Optional[UserProfile]:
    # Delete the old profile
    result = await db.execute(
        select(UserProfile).where(UserProfile.id == profile_id, UserProfile.user_id == user_id)
    )
    old_profile = result.scalars().first()
    if old_profile:
        await db.delete(old_profile)
        await db.commit()
    # Create new profile
    new_profile = UserProfile(
        user_id=user_id,
        portfolio_id=profile_in.portfolio_id,
        short_term_objectives=list_to_str(profile_in.short_term_objectives),
        long_term_objectives=list_to_str(profile_in.long_term_objectives),
        sector_preferences=list_to_str(profile_in.sector_preferences),
        regional_preferences=list_to_str(profile_in.regional_preferences),
        asset_preferences=list_to_str(profile_in.asset_preferences),
    )
    db.add(new_profile)
    await db.commit()
    await db.refresh(new_profile)
    return new_profile

async def delete_profile(db: AsyncSession, user_id: int, profile_id: int) -> bool:
    print(f"DEBUG: delete_profile: user_id={user_id}, profile_id={profile_id}")
    result = await db.execute(
        select(UserProfile).where(UserProfile.id == profile_id, UserProfile.user_id == user_id)
    )
    profile = result.scalars().first()
    print(f"DEBUG: found profile: {profile}")
    if not profile:
        print("DEBUG: profile not found")
        return False
    await db.delete(profile)
    await db.commit()
    print("DEBUG: profile deleted")
    return True 