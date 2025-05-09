from fastapi import APIRouter, HTTPException
from app.core.prompt_logic import handle_prompt
from app.models.schemas import PromptRequest, PromptResponse
router = APIRouter()

@router.post("/analyze", response_model=PromptResponse)
async def analyze(request: PromptRequest):
    try:
        return await handle_prompt(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
