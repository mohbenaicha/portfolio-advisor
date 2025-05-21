import asyncio
import os

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# from tests.mock_populate_dbs import create_demo_users
# from tests.unit_test_analyze import run_test
# from tests.unit_test_scraper import test_article_scraping_and_saving
# from tests.unit_test_external_services import (
    # test_openai_extract_entities,
#     test_generate_advice,
#     test_langchain_summary,
# )
# from tests.unit_test_mongo_storage import run_tests
# from tests.integration_test_analyze_endpoint import test_handle_prompt_with_real_data
from tests.auth_unit_tests import run_all_auth_tests
from app.db.populate_demo_users import populate_users
from tests.unit_test_portfolio_endpoints import run_all_portfolio_endpoint_unit_tests
from tests.unit_test_archive_endpoints import run_all_archive_endpoint_unit_tests
from tests.unit_test_llm_memory import test_llm_memory_evolution, test_multi_user_memory_isolation, get_last_user_memory

if __name__ == "__main__":
    # Run the tests
    # run_test()
    # asyncio.run(test_article_scraping_and_saving())
    # asyncio.run(test_openai_extract_entities())
    # asyncio.run(test_generate_advice())
    # asyncio.run(test_langchain_summary())
    # asyncio.run(run_tests()) # mongo storage
    # asyncio.run(test_handle_prompt_with_real_data())
    # asyncio.run(create_demo_users())
    # asyncio.run(run_all_auth_tests())
    # asyncio.run(populate_users())
    # asyncio.run(run_all_portfolio_endpoint_unit_tests())
    # asyncio.run(run_all_archive_endpoint_unit_tests())
    # asyncio.run(test_llm_memory_evolution())
    # asyncio.run(test_multi_user_memory_isolation())
    asyncio.run(get_last_user_memory(2))


