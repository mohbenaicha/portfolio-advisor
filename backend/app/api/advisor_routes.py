from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.mcp_client import run_mcp_client_pipeline
from app.db.session import get_db
from app.dependencies.user import get_current_user
from app.models.schemas import PromptRequest, PromptResponse
from app.db.user_session import UserSessionManager
from app.core.session_state import advisor_session_store
import traceback

router = APIRouter()

@router.post("/analyze", response_model=PromptResponse)
async def analyze(request: PromptRequest, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user)):
    try:
        if not user_id in advisor_session_store:
            with UserSessionManager.use_advisor_session():
                await UserSessionManager.load_session_from_db(user_id=user_id, db=db)
        result = await run_mcp_client_pipeline(request.question, user_id, request.portfolio_id, db)
        return result
    except Exception as e:
        print(f"ERROR: Error in analyze endpoint: {e}")
        # traceback.print_exc() # DEBUG
        raise HTTPException(status_code=500, detail=str(e))
