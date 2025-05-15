import asyncio
import os

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# from tests.unit_test_analyze import run_test
# from tests.unit_test_scraper import test_article_scraping_and_saving
# from tests.unit_test_external_services import (
#     unit_test_openai_extract_entities,
#     unit_test_generate_advice,
#     unit_test_langchain_summary,
# )
# from tests.unit_test_mongo_storage import run_tests
from tests.integration_test_analyze_endpoint import test_handle_prompt_with_real_data

if __name__ == "__main__":
    # Run the tests
    # run_test()
    # test_article_scraping_and_saving()
    # asyncio.run(test_openai_extract_entities())
    # asyncio.run(test_generate_advice())
    # asyncio.run(test_langchain_summary())
    # asyncio.run(run_tests()) # mongo storage
    asyncio.run(test_handle_prompt_with_real_data())
