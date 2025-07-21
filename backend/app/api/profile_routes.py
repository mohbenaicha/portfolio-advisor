from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas import UserProfileCreate, UserProfileUpdate, UserProfileResponse, ProfileDeleteResponse, UserProfilePairResponse, AdminProfileRequest
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


@router.get("/portfolio/{portfolio_id}", response_model=UserProfilePairResponse)
async def get_portfolio_profile(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    specific, general = None, None
    profiles = await get_profiles(db, user)
    specific = next((p for p in profiles if getattr(p, 'portfolio_id') == portfolio_id), None)
    general = next((p for p in profiles if getattr(p, 'portfolio_id') is None), None)
    specific = profile_to_response(specific) if specific else None
    general = profile_to_response(general) if general else None
    return UserProfilePairResponse(
        specific=specific,
        general=general
    ) 


@router.post("/admin/portfolio/{portfolio_id}", response_model=UserProfilePairResponse)
async def get_portfolio_profile_as_admin(
    request: Request,
    body: AdminProfileRequest,    
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
):
    user_id = await get_current_user(request, db)
    if user_id != 0:  # Ensure the user is admin
        raise HTTPException(status_code=403, detail="Access denied")
    specific, general = None, None
    profiles = await get_profiles(db, body.user_id)
    print("Retrieved Profiles:", profiles)
    specific = next((p for p in profiles if getattr(p, 'portfolio_id') == portfolio_id), None)
    general = next((p for p in profiles if getattr(p, 'portfolio_id') is None), None)
    specific = profile_to_response(specific) if specific else None
    general = profile_to_response(general) if general else None
    # validate specific and general types and content
    print("Specific Profile:", specific)
    print("General Profile:", general)
    return UserProfilePairResponse(
        specific=specific,
        general=general
    ) 