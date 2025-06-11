from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.openai_client import (
    determine_if_augmentation_required,
    retrieve_news,
    prepare_advice_template,
    validate_prompt,
    validate_investment_goal,
)
from pydantic import BaseModel

router = APIRouter()

class DetermineAugmentationPayload(BaseModel):
    question: str
    portfolio_id: int
    user_id: int

class RetrieveNewsPayload(BaseModel):
    question: str
    portfolio_id: int
    user_id: int

class GenerateAdviceTemplatePayload(BaseModel):
    question: str
    portfolio_id: int
    user_id: int
    article_summaries: list = []

class ValidatePromptPayload(BaseModel):
    question: str
    portfolio_id: int
    user_id: int

class ValidateInvestmentGoalPayload(BaseModel):
    question: str
    portfolio_id: int
    user_id: int

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

@router.post("/determine-augmentation")
async def api_determine_augmentation(
    payload: DetermineAugmentationPayload,
    db: AsyncSession = Depends(get_db),
):
    return await determine_if_augmentation_required(
        question=payload.question,
        portfolio_id=payload.portfolio_id,
        db=db,
        user_id=payload.user_id,
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

@router.post("/generate-advice-template")
async def api_generate_advice_template(
    payload: GenerateAdviceTemplatePayload,
    db: AsyncSession = Depends(get_db),
):
    return await prepare_advice_template(
        question=payload.question,
        portfolio_id=payload.portfolio_id,
        article_summaries=payload.article_summaries,
        db=db,
        user_id=payload.user_id,
    )
