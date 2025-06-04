from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.openai_client import (
    determine_if_augmentation_required,
    retrieve_news,
    prepare_advice_prompt,
)

router = APIRouter()

@router.post("/determine-augmentation")
async def api_determine_augmentation(payload: dict, db: AsyncSession = Depends(get_db)):
    return await determine_if_augmentation_required(
        question=payload["question"],
        portfolio_id=payload["portfolio_id"],
        db=db,
        user_id=payload["user_id"]
    )


@router.post("/retrieve-news")
async def api_retrieve_news(payload: dict, db: AsyncSession = Depends(get_db)):
    return await retrieve_news(
        question=payload["question"],
        portfolio_id=payload["portfolio_id"],
        db=db,
        user_id=payload["user_id"]
    )

@router.post("/generate-advice")
async def api_generate_advice(payload: dict, db: AsyncSession = Depends(get_db)):
    return await prepare_advice_prompt(
        question=payload["question"],
        db=db,
        portfolio_id=payload["portfolio_id"],
        article_summaries=payload.get("article_summaries", []),
        user_id=payload["user_id"],
    )
