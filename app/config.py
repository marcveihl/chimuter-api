import logging
import os

from dotenv import load_dotenv

load_dotenv()

CTA_BUS_API_KEY = os.getenv("CTA_BUS_API_KEY", "")
CTA_TRAIN_API_KEY = os.getenv("CTA_TRAIN_API_KEY", "")
METRA_API_TOKEN = os.getenv("METRA_API_TOKEN", "")
ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",")
    if o.strip()
]

logger = logging.getLogger("chimuter")


def check_env():
    missing = []
    if not CTA_BUS_API_KEY:
        missing.append("CTA_BUS_API_KEY")
    if not CTA_TRAIN_API_KEY:
        missing.append("CTA_TRAIN_API_KEY")
    if not METRA_API_TOKEN:
        missing.append("METRA_API_TOKEN")
    if missing:
        logger.warning("Missing environment variables: %s", ", ".join(missing))
