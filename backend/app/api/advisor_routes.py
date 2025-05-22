from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.prompt_logic import handle_prompt
from app.db.session import get_db
from app.models.schemas import PromptRequest, PromptResponse
router = APIRouter()

@router.post("/analyze", response_model=PromptResponse)
async def analyze(request: PromptRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await handle_prompt(request = request, db = db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
