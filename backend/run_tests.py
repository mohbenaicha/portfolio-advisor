import asyncio
from tests.test_analyze import run_test
from tests.test_scraper import test_article_scraping_and_saving
from tests.test_external_services import test_openai_extract_entities, test_generate_advice


if __name__ == "__main__":
    # Run the tests
    # run_test()
    # test_article_scraping_and_saving()
    # asyncio.run(test_openai_extract_entities())
    asyncio.run(test_generate_advice())