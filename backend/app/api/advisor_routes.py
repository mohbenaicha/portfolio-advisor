from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.mcp_client import run_mcp_client_pipeline
from app.db.session import get_db
from app.dependencies.user import get_current_user
from app.models.schemas import PromptRequest, PromptResponse

router = APIRouter()

@router.post("/analyze", response_model=PromptResponse)
async def analyze(request: PromptRequest, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user)):
    try:
        result = await run_mcp_client_pipeline(request.question, user_id, request.portfolio_id, db)
        return result
    except Exception as e:
        print(f"Error in analyze endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
