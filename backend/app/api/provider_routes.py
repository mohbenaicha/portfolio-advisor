from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.openai_client import (
    retrieve_news,
    validate_prompt,
    validate_investment_goal,
)
from app.models.schemas import *

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


@router.post("/validate-investment-goal", response_model=ValidateInvestmentGoalResponse)
async def api_validate_investment_goal(
    payload: ValidateInvestmentGoalPayload,
    db: AsyncSession = Depends(get_db),
):

    result = await validate_investment_goal(
        question=payload.question,
        portfolio_id=payload.portfolio_id,
        user_id=payload.user_id,
        db=db,
    )

    # Create response with token counts
    if isinstance(result, dict):
        short_term = result.get("short_term_objective")
        long_term = result.get("long_term_objective")

        # Ensure they are strings or None
        short_term_str = str(short_term) if short_term is not None else None
        long_term_str = str(long_term) if long_term is not None else None

        return ValidateInvestmentGoalResponse(
            valid=result.get("valid", False),
            short_term_objective=short_term_str,
            long_term_objective=long_term_str,
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
):
    from app.utils.portfolio_utils import get_portfolio
    from app.db.portfolio_crud import get_portfolio_by_id

    portfolio = get_portfolio(
        jsonable_encoder(
            await get_portfolio_by_id(db, payload.portfolio_id, payload.user_id)
        )
    )

    if not portfolio:
        return {"error": "Portfolio not found"}

    return portfolio
