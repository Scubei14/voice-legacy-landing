import sys, logging
from config import settings

def setup_logging():
    logger = logging.getLogger("voicelegacy")
    if logger.handlers: return logger
    level = logging.DEBUG if settings.APP_DEBUG else logging.INFO
    logger.setLevel(level)
    sh = logging.StreamHandler(sys.stdout); sh.setLevel(level)
    sh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s", "%Y-%m-%d %H:%M:%S"))
    logger.addHandler(sh)
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    return logger

logger = setup_logging()
