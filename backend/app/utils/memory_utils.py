from typing import Dict
from app.db.user_session import UserSessionManager


async def get_investment_objective(user_id: int, portfolio_id: int) -> str:
    print("User session: \n", UserSessionManager.get_session(user_id))
    llm_memory: Dict[str, str] = await UserSessionManager.get_llm_memory(
        user_id, portfolio_id
    )
    st_obj = llm_memory.short_term_goal if llm_memory else ""
    lt_obj = llm_memory.long_term_goal if llm_memory else ""
    return f"""
            {
                f"User's last short-term investment objective: {st_obj}" if st_obj else ""
            }
            {
                f"User's last long-term investment objective: {lt_obj}" if lt_obj else ""
            }
            """
