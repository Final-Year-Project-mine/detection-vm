import logging

from app.core.config import settings


logging.basicConfig(
    filename=settings.log_file,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("detection")
