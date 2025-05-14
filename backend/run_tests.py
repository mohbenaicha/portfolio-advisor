import asyncio
import os

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# from tests.test_analyze import run_test
# from tests.test_scraper import test_article_scraping_and_saving
from tests.test_external_services import (
    test_openai_extract_entities,
    test_generate_advice,
    test_langchain_summary,
)


# from tests.test_mongo_storage import run_tests


if __name__ == "__main__":
    # Run the tests
    # run_test()
    # test_article_scraping_and_saving()
    # asyncio.run(test_openai_extract_entities())
    asyncio.run(test_generate_advice())
    # asyncio.run(test_langchain_summary())
    # asyncio.run(run_tests()) # mongo storage
