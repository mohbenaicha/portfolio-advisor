from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.prompt_logic import handle_prompt
from app.db.session import get_db
from app.dependencies.user import get_current_user
from app.models.schemas import PromptRequest, PromptResponse

router = APIRouter()

@router.post("/analyze", response_model=PromptResponse)
async def analyze(request: PromptRequest, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user)):
    try:
        return await handle_prompt(request = request, db = db, user_id= user_id)
    except Exception as e:
        print(f"Error in analyze endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
