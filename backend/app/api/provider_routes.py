from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.openai_client import (
    retrieve_news,
    validate_prompt,
    validate_investment_goal,
)
from app. models.schemas import *

router = APIRouter()



@router.post("/validate-prompt")
async def api_validate_prompt(
    payload: ValidatePromptPayload,
    db: AsyncSession = Depends(get_db),
):
    
    return await validate_prompt(
        question=payload.question,
        portfolio_id=payload.portfolio_id,
        user_id=payload.user_id,
        db=db,
    )

@router.post("/validate-investment-goal")
async def api_validate_investment_goal(
    payload: ValidateInvestmentGoalPayload,
    db: AsyncSession = Depends(get_db),
):
    return await validate_investment_goal(
        question=payload.question,
        portfolio_id=payload.portfolio_id,
        user_id=payload.user_id,
        db=db,
    )

@router.post("/retrieve-news")
async def api_retrieve_news(
    payload: RetrieveNewsPayload,
    db: AsyncSession = Depends(get_db),
):
    return await retrieve_news(
        question=payload.question,
        portfolio_id=payload.portfolio_id,
        db=db,
        user_id=payload.user_id,
    )

@router.post("/get-user-portfolio")
async def api_get_user_portfolio(
    payload: GetUserPortfolioPayload,
    db: AsyncSession = Depends(get_db),
):
    from app.utils.portfolio_utils import get_portfolio
    from app.db.portfolio_crud import get_portfolio_by_id
    portfolio = get_portfolio(
       jsonable_encoder(await get_portfolio_by_id(db, payload.portfolio_id, payload.user_id))
    )
    
    if not portfolio:
        return {"error": "Portfolio not found"}
    
    return portfolio
