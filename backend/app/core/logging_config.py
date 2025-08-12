import logging
from app.config import LOG_LEVEL

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)

logger = logging.getLogger("app")
