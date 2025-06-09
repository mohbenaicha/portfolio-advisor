from os import getenv

ENV = getenv("ENV", "DEV")  # Default to "DEV" if ENV is not set

if ENV == "DEV":
    from dotenv import load_dotenv
    print("Loading environment variables from .env file")

    load_dotenv()

DATABASE_URL = getenv("DATABASE_URI")
MONGO_URI = getenv("MONGO_URI")
OUTSCRAPER_API_KEY = getenv("OUTSCRAPER_API_KEY")
OPEN_AI_API_KEY = getenv("OPENAI_API_KEY")
BACKEND_BASE_URL = getenv("BACKEND_BASE_URL", "https://briefly-backend-459260001744.us-central1.run.app")
ALLOWED_ORIGIN = getenv("ALLOWED_ORIGIN", "https://project-briefly-2a809.web.app/")
PROVIDER_BASE_URL = "/".join([BACKEND_BASE_URL, "tool"])
GMAIL_PWD = getenv("GMAIL_PWD", "")
RECAPTCHA_SECRET_KEY = getenv("RECAPTCHA_SECRET_KEY", "")

if not DATABASE_URL:
    raise ValueError("DATABASE_URI environment variable not set")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable isn't set")
if not OUTSCRAPER_API_KEY:
    raise ValueError("OUTSCRAPER_API_KEY environment variable isn't set")
if not OPEN_AI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable isn't set")
if not BACKEND_BASE_URL:
    raise ValueError("BACKEND_BASE_URL environment variable isn't set")
if not GMAIL_PWD:
    raise ValueError("GMAIL_PWD environment variable isn't set")
if not RECAPTCHA_SECRET_KEY:
    raise ValueError("RECAPTCHA_SECRET_KEY environment variable isn't set")

SESSION_EXPIRY_HOURS = 24
SCRAPER_HEADERS = {"User-Agent": "Mozilla/5.0"}
EXTRACTION_MODEL = "gpt-4.1-mini"
SUMMARY_MODEL = "gpt-4.1-mini"
ADVICE_MODEL = "gpt-4.1-mini"
EMAIL_ADDRESS = "mohamedbenaicha1992@gmail.com"