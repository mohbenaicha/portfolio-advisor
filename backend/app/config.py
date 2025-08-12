from os import getenv
import json
import os
import logging


ENV = getenv("ENV", "DEV")  # Default to "DEV" if ENV is not set
DATABASE_URL = getenv("DATABASE_URI").strip()
MONGO_URI = getenv("MONGO_URI").strip()
OUTSCRAPER_API_KEY = getenv("OUTSCRAPER_API_KEY").strip()
OPEN_AI_API_KEY = getenv(
    "OPENAI_API_KEY"
).strip()  # Remove any surrounding quotes due to GCP cloud secter create
SYSTEM_USER_TOKEN = getenv("SYSTEM_USER_TOKEN", "").strip()

ALLOWED_ORIGINS = [
    getenv("ALLOWED_ORIGIN", "https://project-briefly-2a809.web.app"),
]

raw_endpoint_str = getenv("BACKEND_URLS")
if raw_endpoint_str:
    BACKEND_SERVICE_MAP = json.loads(
        raw_endpoint_str.strip()
    )  # ("core" "advisor" "archive" "portfolio" "profile")
else:
    BACKEND_SERVICE_MAP = {}

if ENV == "TEST":
    ALLOWED_ORIGINS.append("http://localhost:8089")


PROVIDER_BASE_URL = "/".join([getenv("ADVISOR_INTERNAL_BASE_URI"), "tool"])
GMAIL_PWD = getenv("GMAIL_PWD", "").strip()
RECAPTCHA_SECRET_KEY = getenv("RECAPTCHA_SECRET_KEY", "").strip()
LOG_LEVEL = logging.INFO


if ENV == "DEV":
    TEST_DB_URL = getenv("TEST_DB_URI", "").strip()
    LOG_LEVEL = logging.DEBUG


if not DATABASE_URL:
    raise ValueError("DATABASE_URI environment variable not set")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable isn't set")
if not OUTSCRAPER_API_KEY:
    raise ValueError("OUTSCRAPER_API_KEY environment variable isn't set")
if not OPEN_AI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable isn't set")
if not GMAIL_PWD:
    raise ValueError("GMAIL_PWD environment variable isn't set")
if not RECAPTCHA_SECRET_KEY:
    raise ValueError("RECAPTCHA_SECRET_KEY environment variable isn't set")
if not SYSTEM_USER_TOKEN:
    raise ValueError("SYSTEM_USER_TOKEN environment variable isn't set")
if not BACKEND_SERVICE_MAP:
    raise ValueError("BACKEND_SERVICE_MAP environment variable isn't set or is empty")
if not ALLOWED_ORIGINS:
    raise ValueError("ALLOWED_ORIGINS environment variable isn't set or is empty")
if not PROVIDER_BASE_URL:
    raise ValueError("PROVIDER_BASE_URL environment variable isn't set or is empty")

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
