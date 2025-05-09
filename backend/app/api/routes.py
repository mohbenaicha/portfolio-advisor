from fastapi import APIRouter, HTTPException
from app.core.prompt_logic import handle_prompt
from app.db.portfolio_crud import get_all_portfolios
from app.models.schemas import PromptRequest, PromptResponse

router = APIRouter()

@router.get("/portfolios")
async def list_portfolios():
    return await get_all_portfolios()

@router.post("/analyze", response_model=PromptResponse)
async def analyze(request: PromptRequest):
    try:
        return await handle_prompt(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
