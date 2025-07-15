from os import getenv

ENV = getenv("ENV", "DEV")  # Default to "DEV" if ENV is not set

if ENV == "DEV":
    from dotenv import load_dotenv
    print("Loading environment variables from .env file")

    load_dotenv()
    TEST_DB_URL = getenv("TEST_DB_URI", "").strip()

DATABASE_URL = getenv("DATABASE_URI").strip()
MONGO_URI = getenv("MONGO_URI").strip()
OUTSCRAPER_API_KEY = getenv("OUTSCRAPER_API_KEY").strip()
OPEN_AI_API_KEY = getenv("OPENAI_API_KEY").strip()  # Remove any surrounding quotes due to GCP cloud secter create
BACKEND_BASE_URL = getenv("BACKEND_BASE_URL", "https://briefly-backend-459260001744.us-central1.run.app")
ALLOWED_ORIGINS = [
    getenv("ALLOWED_ORIGIN", "https://project-briefly-2a809.web.app"),
]

if ENV == "TEST":
    ALLOWED_ORIGINS.append("http://localhost:8089")

if ENV == "DEV":
    ALLOWED_ORIGINS.extend([
        "http://localhost:5173", 
        "http://localhost:3000",
    ])
    
PROVIDER_BASE_URL = "/".join([BACKEND_BASE_URL, "tool"])
GMAIL_PWD = getenv("GMAIL_PWD", "").strip()
RECAPTCHA_SECRET_KEY = getenv("RECAPTCHA_SECRET_KEY", "").strip()

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
SUMMARY_LLM = "gpt-4o-mini"
LLM = "gpt-4o-mini"
ALT_LLM = "gpt-4.1-mini"
EMBEDDING_MODEL = "text-embedding-3-small"
EMAIL_ADDRESS = "mohamedbenaicha1992@gmail.com"

def print_env_variables():
    env_vars = {
        "ENV": ENV,
        "DATABASE_URL": DATABASE_URL,
        "MONGO_URI": MONGO_URI,
        "OUTSCRAPER_API_KEY": OUTSCRAPER_API_KEY,
        "OPEN_AI_API_KEY": OPEN_AI_API_KEY,
        "BACKEND_BASE_URL": BACKEND_BASE_URL,
        "ALLOWED_ORIGIN": ALLOWED_ORIGINS,
        "PROVIDER_BASE_URL": PROVIDER_BASE_URL,
        "GMAIL_PWD": GMAIL_PWD,
        "RECAPTCHA_SECRET_KEY": RECAPTCHA_SECRET_KEY,
        "SESSION_EXPIRY_HOURS": SESSION_EXPIRY_HOURS,
        "SCRAPER_HEADERS": SCRAPER_HEADERS,
        "SUMMARY_MODEL": SUMMARY_LLM,
        "LLM": LLM,
        "EMAIL_ADDRESS": EMAIL_ADDRESS,
    }

    for key, value in env_vars.items():
        print(f"{key}: {value}")

print_env_variables()