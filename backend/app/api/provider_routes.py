from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.openai_client import (
    retrieve_news,
    validate_prompt,
)
from app.models.schemas import *
from app.utils.profile_utils import profile_to_text
from typing import Union

router = APIRouter()


@router.post("/validate-prompt", response_model=ValidatePromptResponse)
async def api_validate_prompt(
    payload: ValidatePromptPayload,
    db: AsyncSession = Depends(get_db),
):

    result = await validate_prompt(
        question=payload.question,
        portfolio_id=payload.portfolio_id,
        user_id=payload.user_id,
        db=db,
    )

    # Create response with token counts
    if isinstance(result, dict):
        return ValidatePromptResponse(
            valid=result.get("valid", False),
        )

    return result



@router.post("/retrieve-news", response_model=RetrieveNewsResponse)
async def api_retrieve_news(
    payload: RetrieveNewsPayload,
    db: AsyncSession = Depends(get_db),
):

    result = await retrieve_news(
        question=payload.question,
        portfolio_id=payload.portfolio_id,
        db=db,
        user_id=payload.user_id,
    )

    # Handle the new return format with token counts
    if isinstance(result, dict) and "articles" in result:
        articles = result["articles"]
        return RetrieveNewsResponse(articles=articles)

    # Fallback for old format
    if isinstance(result, list):
        return RetrieveNewsResponse(articles=result)

    return result


@router.post("/get-user-portfolio")
async def api_get_user_portfolio(
    payload: GetUserPortfolioPayload,
    db: AsyncSession = Depends(get_db),
) -> Union[dict[str, str], str]:
    from app.utils.portfolio_utils import portfolio_to_text
    from app.db.portfolio_crud import get_portfolio_by_id

    portfolio = portfolio_to_text(
        jsonable_encoder(
            await get_portfolio_by_id(db, payload.portfolio_id, payload.user_id)
        )
    )

    if not portfolio:
        return {"error": "Portfolio not found"}

    return portfolio


@router.post("/get-user-profiles")
async def api_get_user_profiles(
    payload: GetUserProfilesPayload,
    db: AsyncSession = Depends(get_db),
) -> Union[dict[str, str], str]:
    from app.db.profile_crud import get_user_profile_for_portfolio, update_user_profile_fields
    from app.services.openai_client import extract_profile_details
    from app.models.schemas import UserProfileBase

    specific, general = await get_user_profile_for_portfolio(
        db, payload.user_id, payload.portfolio_id
    )

    # Extract and update profile details using LLM
    question = getattr(payload, "question", None)
    if question:
        # Dynamically get updatable fields from UserProfileBase
        exclude_fields = {"id", "user_id", "portfolio_id", "created_at", "updated_at"}
        updatable_fields = [f for f in UserProfileBase.model_fields.keys() if f not in exclude_fields]
        
        if specific:
            # Prepare current profile as dict (only updatable fields)
            current_profile = {}
            for field in updatable_fields:
                value = getattr(specific, field, None)
                if value not in (None, ""):
                    # If it's a string and should be a list, split it
                    if isinstance(value, str) and field.endswith("objectives") or field.endswith("preferences"):
                        current_profile[field] = value.split(",")
                    else:
                        current_profile[field] = value
                else:
                    current_profile[field] = [] if (field.endswith("objectives") or field.endswith("preferences")) else None
        else:
            # No specific profile exists, start with empty profile
            current_profile = {}
            for field in updatable_fields:
                current_profile[field] = [] if (field.endswith("objectives") or field.endswith("preferences")) else None
        
        update_fields = await extract_profile_details(question, current_profile)
        if update_fields:
            updated_profile = await update_user_profile_fields(db, payload.user_id, payload.portfolio_id, update_fields)
            if updated_profile:
                specific = updated_profile
        else:
            return {"error": "Investment profile details could not be determined from database or user query."}

    if not specific and not general:
        return {"error": "No investment profile found."}

    summary = ""
    if specific:
        summary += profile_to_text(specific, f"portfolio {getattr(specific, 'name', specific.portfolio_id)}") + "\n\n"
    if general:
        summary += profile_to_text(general, "all portfolios") + "\n\n"
    if specific and general:
        summary += "If general profile conflicts with the specific portfolio investment profile, try to reconcile between the two, otherwise prioritize the specific profile investment profile."
    print("DEBUG: get investment profile tool call: ", summary)
    return {"investment_profile": summary}
