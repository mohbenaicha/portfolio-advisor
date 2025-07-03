from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas import UserProfileCreate, UserProfileUpdate, UserProfileResponse, ProfileDeleteResponse
from app.services.profile_service import (
    create_profile, get_profiles, update_profile, delete_profile, str_to_list
)
from app.dependencies.user import get_current_user
from app.db.session import get_db
from typing import List

router = APIRouter(prefix="/profiles", tags=["profiles"])

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

@router.post("/", response_model=UserProfileResponse)
async def create_user_profile(
    profile_in: UserProfileCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    profile = await create_profile(db, user, profile_in)
    return profile_to_response(profile)

@router.get("/", response_model=List[UserProfileResponse])
async def list_user_profiles(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    profiles = await get_profiles(db, user)
    return [profile_to_response(p) for p in profiles]

@router.get("/{profile_id}", response_model=UserProfileResponse)
async def get_user_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    profiles = await get_profiles(db, user)
    profile = next((p for p in profiles if getattr(p, 'id') == profile_id), None)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile_to_response(profile)

@router.put("/{profile_id}", response_model=UserProfileResponse)
async def update_user_profile(
    profile_id: int,
    profile_in: UserProfileUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    profile = await update_profile(db, user, profile_id, profile_in)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile_to_response(profile)

@router.delete("/{profile_id}", response_model=ProfileDeleteResponse)
async def delete_user_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    success = await delete_profile(db, user, profile_id)
    if not success:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileDeleteResponse(deleted=True) 