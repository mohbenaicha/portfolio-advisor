from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.mcp_client import run_mcp_client_pipeline
from app.db.session import get_db
from app.dependencies.user import get_current_user
from app.models.schemas import PromptRequest, PromptResponse
from app.db.user_session import UserSessionManager
from app.core.session_state import advisor_session_store
from app.core.logging_config import logger
import traceback

router = APIRouter()

@router.post("/analyze", response_model=PromptResponse)
async def analyze(request: PromptRequest, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user)):
    try:
        if not user_id in advisor_session_store:
            logger.debug(f"Loading session for user {user_id} from database.")
            with UserSessionManager.use_advisor_session():
                await UserSessionManager.load_session_from_db(user_id=user_id, db=db)
        logger.debug(f"Running MCP client pipeline for user {user_id}, portfolio {request.portfolio_id}.")
        result = await run_mcp_client_pipeline(request.conversation, user_id, request.portfolio_id, db)
        logger.info(f"Successfully completed MCP client pipeline for user {user_id}.")
        return result
    except Exception as e:
        logger.error(f"Error in analyze endpoint for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
