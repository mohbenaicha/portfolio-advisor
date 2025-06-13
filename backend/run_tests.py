import asyncio
import os

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


from tests.integration_llm_memory_session_flow import test_user1_memory_flow
from tests.integrate_session_crash_recovery import test_auth_and_crash_recovery
from tests.integration_portfolio_crud_flow import test_portfolio_crud_flow
from tests.integration_archive_access_flow import test_archive_endpoints
from tests.integration_advice_generation_flow import test_analyze_endpoint
from app.test_fetch_articles import run_retrieve_relevant_articles


if __name__ == "__main__":
    # asyncio.run(test_portfolio_crud_flow())
    # asyncio.run(test_auth_and_crash_recovery())
    # asyncio.run(test_archive_endpoints())
    # asyncio.run(test_analyze_endpoint())
    run_retrieve_relevant_articles()


