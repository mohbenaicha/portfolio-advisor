import asyncio
import argparse
import sys
from app.db.init import init_db

if __name__ == "__main__":
    from app.config import DATABASE_URL, TEST_DB_URL

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env",
        choices=["dev", "prod"],
        default="dev",
        help="Environment: dev or prod (default: dev)",
    )
    args = parser.parse_args()

    # Check if args were provided
    if not args:
        print("No arguments provided")
        sys.exit(1)

    # Update engine URL based on environment
    print("DEBUG: args.env =", args.env)
    print("DEBUG: TEST_DB_URL =", TEST_DB_URL)
    print("DEBUG: DATABASE_URL =", DATABASE_URL)

    if args.env == "dev":
        url = TEST_DB_URL
        print("Using test database:", TEST_DB_URL)
    else:
        url = DATABASE_URL
        print("Using production database:", DATABASE_URL)

    asyncio.run(init_db(url))
    print(f"Using {args.env} environment with database: {url}")
